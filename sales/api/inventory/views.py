from sales.api.filters import CustomInvoiceSearchFilter, InvoiceSearchFilter
from . import serializers
from ...models import *
from coreapp.models import User
from coreapp.helper import *
from utility.utils.bulk_utils import *
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from coreapp.models import User
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import PermissionRequiredMixin
from rest_framework.decorators import action
from .serializers import *
from utility.utils.model_utils import *
import calendar
from datetime import date, timedelta
from inventory.models import *
from django.db.models import Q
from ..filters import InvoiceSearchFilter_forInventory
import os
from io import BytesIO
from django.http import HttpResponse
from weasyprint import HTML
from pdf2image import convert_from_bytes
from sales.helpers import get_invoice_params
from django.template.loader import render_to_string
from coreapp.admin import DailyReportResource
from utility.utils.resize_utils import get_data_bounding_box
class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [
        AllowAny,
    ]
    lookup_field = "slug"
    filter_backends = (DjangoFilterBackend, )
    filterset_class = InvoiceSearchFilter_forInventory

    def get_serializer_context(self):
        request = self.request
        context = super().get_serializer_context()
        context.update({"request": request})
        return context

    def get_serializer_class(self):
        if self.action == "list":
            address = self.request.query_params.get("address_filter")
            if address is not None:
                return InvoiceSerializer_AddressFilter
            if self.request.query_params.get("is_draft", None):
                return InvoiceSerializer
            return InvoiceListSerializer
        elif self.action == "update":
            return InvoiceSerializer_Update
        elif self.action == "partial_update":
            return InvoiceSerializer_Update
        elif self.action == "filter":
            return  InvoiceListSerializer
        else:
            return InvoiceSerializer

    def generate_data_format(self):
        from datetime import datetime
        address = self.request.query_params.get("address_filter", "")
        start_date = self.request.query_params.get("start", "")
        end_date = self.request.query_params.get("end", "")
        outlet = self.request.query_params.get("outlet", None)

        if start_date == "" or end_date == "":
            start_date = None
            end_date = None
        else:
            start_date = datetime.strptime(start_date, "%m/%d/%Y")
            end_date = datetime.strptime(end_date, "%m/%d/%Y")
        
        invoice_list = self.queryset.filter(
            Q(to_address__icontains=address)
            | Q(to_address__icontains=address)
            | Q(to_city__icontains=address)
            | Q(to_division__icontains=address)
          
        )
        if outlet:
            invoice_list = invoice_list.filter(outlet__id=outlet)
        if address == "default":
            invoice_list = self.queryset.all()
        if start_date and end_date:
            invoice_list = invoice_list.filter(
                invoice_date__range=[start_date, end_date]
            )
        
        data = []
        for instance in invoice_list:
            for product in instance.get_invoice_products():
                data.append(
                    {
                        "invoice_id": instance.id,
                        "invoice_number": instance.number,
                        "product_name": product.product.name if product.product else product.product_name,
                        "sku": product.product.sku if product.product else "",
                        "quantity": product.quantity,
                        "total": product.total,
                        "address": instance.to_address,
                        "address2": instance.to_address2,
                        "city": instance.to_city,
                        "division": instance.to_division,
                        "country": instance.to_country,
                        "zip_code": instance.to_zip_code,
                        "phone": instance.to_mobile,
                        "email": instance.to_email,
                        "name": instance.bill_to,
                        "invoice_date": instance.invoice_date,
                    }
                )
        return data

    @paginate
    def get_paginated_data(self):
        data = self.generate_data_format()
        return data

    def list(self, request, *args, **kwargs):
        from utility.utils import notification_utils
        notification_utils.update_dashboard_notification("invoice", 0)
        export = self.request.query_params.get("export_data", None)
        address = self.request.query_params.get("address_filter", None)

        data = self.generate_data_format()
        if export and address:
            from utility.utils.excel_export_utils import generate_excel

            return generate_excel(list(data[0].keys()), data)
        if not export and address:
            return self.get_paginated_data()
        return super().list(request, *args, **kwargs)

    @paginate
    @action(detail=False, methods=["get"])
    def filter(self, request, *args, **kwargs):
        start = request.GET.get("start")
        end = request.GET.get("end")
        is_requisition_order = request.GET.get("is_requisition_order", False)
        is_purchase_order = request.GET.get("is_purchase_order", False)
        is_custom = request.GET.get("is_custom", False)
        is_regular = request.GET.get("is_regular", False)
        outlet = request.GET.get("outlet", None)
        if is_regular=="true":is_regular=True
        is_outlet = request.GET.get("is_outlet", False)
        if is_outlet=="true":is_outlet=True
        is_requisition_order = True if is_requisition_order == "true" else False
        is_purchase_order = True if is_purchase_order == "true" else False
        is_custom = True if is_custom == "true" else False

        try:
            start_month, start_day, start_year = start.split("/")
        except:
            return Response(
                {
                    "data": [],
                    "error": "Start date is empty or Please use correct format,month/date/year",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            end_month, end_day, end_year = end.split("/")
        except:
            return Response(
                {
                    "data": [],
                    "error": "End date is empty or Please use correct format,month/date/year",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        start_date = datetime.datetime(
            year=int(start_year),
            month=int(start_month),
            day=int(start_day),
            hour=0,
            minute=0,
            second=0,
        )  # represents 00:00:00
        end_date = datetime.datetime(
            year=int(end_year),
            month=int(end_month),
            day=int(end_day),
            hour=23,
            minute=59,
            second=59,
        )
        return self.get_queryset().model.objects.filter(
            invoice_date__range=[start_date, end_date], is_custom=is_custom, is_requisition_order=is_requisition_order, is_purchase_order=is_purchase_order, is_regular=is_regular, is_outlet=is_outlet,outlet__id=outlet
        )

    @action(detail=True, methods=["get"])
    def outlet_invoice_print(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        instance = self.get_object()
        params = get_invoice_params(instance)
        html_string = render_to_string('invoice/outlet_invoice.html', params)

        try:
            pdf_buffer = BytesIO()
            HTML(string=html_string).write_pdf(pdf_buffer)
            pdf_images = convert_from_bytes(pdf_buffer.getvalue())
            if pdf_images:
                image = pdf_images[0]
                left, top, right, bottom = get_data_bounding_box(image)
                cropped_image = image.crop((left, top, right, bottom))
                            # Convert the image to a PNG byte buffer
                # Convert the image to a PNG byte buffer
                image_buffer = BytesIO()
                cropped_image.save(image_buffer, format='PNG')
                
                # Encode the image in base64
                image_base64 = base64.b64encode(image_buffer.getvalue()).decode('utf-8')

                # return HttpResponse(image_base64, content_type='text/plain')
                # return Response({"data": image_base64})
                return HttpResponse(image_buffer.getvalue(), content_type='image/png')
            # img response
            
        except Exception as e:
            return HttpResponse("Error converting HTML to image: {}".format(str(e)))

        return HttpResponse("Error converting HTML to image")


class ExportDailyReportAPIView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        start = request.GET.get("start")
        end = request.GET.get("end")
        try:
            start_month, start_day, start_year = start.split("/")
            end_month, end_day, end_year = end.split("/")
            start_date = datetime.datetime(year=int(start_year), month=int(start_month), day=int(start_day),
                                            hour=0, minute=0, second=0)  # represents 00:00:00
            end_date = datetime.datetime(year=int(end_year), month=int(end_month), day=int(end_day),
                                            hour=23, minute=59, second=59) 
        except Exception as e:
            start_date = None
            end_date = None
            print_log(f"Error in convert date in daily report {e}")
        is_custom = request.GET.get("is_custom")
        query = request.GET.get("query")
        outlet = request.GET.get("outlet", None)
        dataset = DailyReportResource(start_date, end_date, is_custom, query,outlet).export()
        today = datetime.date.today().strftime(
            "%Y-%m-%d"
        )  # get current date in YYYY-MM-DD format
        filename = f"DailyReport_{today}.xlsx"  # create filename with current date
        response = HttpResponse(
            dataset.xlsx,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


class AllInvoiceView(FilterGivenDateInvoice, viewsets.ModelViewSet):
    permission_classes = (CustomDjangoModelPermissions, IsAuthenticated)
    queryset = Invoice.objects.all()
    serializer_class = All_InvoiceSerializer
    pagination_class = LimitOffsetPagination
    filterset_class = InvoiceSearchFilter

    def get_serializer_class(self):
        if self.action == "list":
            return InvoiceListSerializer
        else:
            return InvoiceSerializer


class InvoiceView(FilterGivenDateInvoice, viewsets.ModelViewSet):
    permission_classes = (CustomDjangoModelPermissions, IsAuthenticated)
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    lookup_field = "slug"
    filterset_class = InvoiceSearchFilter

    def get_serializer_class(self):
        if self.action == "list":
            return InvoiceListSerializer
        else:
            return InvoiceSerializer

    def get_queryset(self):
        return self.queryset.filter(is_custom=False)

    @paginate
    @action(detail=False, methods=["get"])
    def filter(self, request, *args, **kwargs):
        start = request.GET.get("start")
        end = request.GET.get("end")
        try:
            start_month, start_day, start_year = start.split("/")
        except:
            return Response(
                {
                    "data": [],
                    "error": "Start date is empty or Please use correct format,month/date/year",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            end_month, end_day, end_year = end.split("/")
        except:
            return Response(
                {
                    "data": [],
                    "error": "End date is empty or Please use correct format,month/date/year",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        start_date = datetime.datetime(
            year=int(start_year),
            month=int(start_month),
            day=int(start_day),
            hour=0,
            minute=0,
            second=0,
        )  # represents 00:00:00
        end_date = datetime.datetime(
            year=int(end_year),
            month=int(end_month),
            day=int(end_day),
            hour=23,
            minute=59,
            second=59,
        )
        return self.get_queryset().model.objects.filter(
            invoice_date__range=[start_date, end_date], is_custom=False
        )


class CustomInvoiceView(FilterGivenDateInvoice, viewsets.ModelViewSet):
    permission_classes = (CustomDjangoModelPermissions, IsAuthenticated)
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    lookup_field = "slug"
    filterset_class = CustomInvoiceSearchFilter

    def get_serializer_class(self):
        if self.action == "list":
            return InvoiceListSerializer
        else:
            return InvoiceSerializer

    def get_queryset(self):
        return self.queryset.filter(is_custom=True)

    @paginate
    @action(detail=False, methods=["get"])
    def filter(self, request, *args, **kwargs):
        start = request.GET.get("start")
        end = request.GET.get("end")
        try:
            start_month, start_day, start_year = start.split("/")
        except:
            return Response(
                {
                    "data": [],
                    "error": "Start date is empty or Please use correct format,month/date/year",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            end_month, end_day, end_year = end.split("/")
        except:
            return Response(
                {
                    "data": [],
                    "error": "End date is empty or Please use correct format,month/date/year",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        start_date = datetime.datetime(
            year=int(start_year),
            month=int(start_month),
            day=int(start_day),
            hour=0,
            minute=0,
            second=0,
        )  # represents 00:00:00
        end_date = datetime.datetime(
            year=int(end_year),
            month=int(end_month),
            day=int(end_day),
            hour=23,
            minute=59,
            second=59,
        )
        return self.get_queryset().model.objects.filter(
            invoice_date__range=[start_date, end_date], is_custom=True
        )


def createDailyReport():
    today = datetime.datetime.today()
    start_date = datetime.datetime(
        year=today.year, month=today.month, day=today.day, hour=0, minute=0, second=0
    )  # represents 00:00:00
    end_date = datetime.datetime(
        year=today.year, month=today.month, day=today.day, hour=23, minute=59, second=59
    )  # represents 23:59:59

    todays_invoices_productss = Invoice_Products.objects.filter(
        Q(invoice_date__range=(start_date, end_date)) and ~Q(product=None)
    )

    from coreapp.helper import print_log

    print_log("todays_invoices_productss")
    print_log(todays_invoices_productss)

    try:
        todaysProductList = []
        for inv_prod in todays_invoices_productss:
            # todaysProductList[]
            if inv_prod.product.id not in todaysProductList:
                mainProudct = inv_prod.product.id
                todaysProductList.append(mainProudct)
        for current_prod in todaysProductList:
            getCurrentProduct = Products.objects.filter(id=current_prod).first()
            alreadyReportCheck = DailyReport.objects.filter(
                Q(created_at__range=(start_date, end_date))
                and Q(products_id=current_prod)
            ).first()
            if getCurrentProduct is not None and alreadyReportCheck is None:
                DailyReport.objects.create(
                    products_id=getCurrentProduct.id
                    if getCurrentProduct is not None
                    else None,
                    product_name=getCurrentProduct.name
                    if getCurrentProduct is not None
                    else None,
                    total_amount=getCurrentProduct.today_total_amount(),
                    quantity=getCurrentProduct.today_total_sales(),
                    created_at=datetime.datetime.now(),
                    is_custom=inv_prod.is_custom,
                    is_purchase_order=inv_prod.is_purchase_order,
                    is_requisition_order=inv_prod.is_requisition_order,
                )
            else:
                alreadyReportCheck.total_amount = getCurrentProduct.today_total_amount()
                alreadyReportCheck.quantity = getCurrentProduct.today_total_sales()
                alreadyReportCheck.save()
    except Exception as e:
        traceback.print_exc()


class createDailyReportFromAPi(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        try:
            createDailyReport()
            return Response({"data": "Generated"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"data": "Generated", "error": str(e)}, status=status.HTTP_200_OK
            )


class GetDailyReport(APIView):
    permission_classes = (AllowAny,)
    # permission_classes = (CustomDjangoModelPermissions, IsAuthenticated)
    queryset = DailyReport.objects.all()

    def get_object(self, pk):
        try:
            return DailyReport.objects.get(pk=pk)
        except DailyReport.DoesNotExist:
            raise Http404

    def get(self, request):
        try:
            today = datetime.datetime.today()
            start = request.GET.get("start")
            end = request.GET.get("end")
            is_custom = request.GET.get("is_custom", "false")
            is_purchase_order = request.GET.get("is_purchase_order", "false")
            is_requisition_order = request.GET.get("is_requisition_order", "false")
            outlet = request.GET.get("outlet", None)  

            from coreapp.helper import print_log
            # print_log("is_requisition_order--------------")
            # print_log(is_requisition_order)
            print("is_purchase_order:", is_purchase_order)
            ReportList = []
            if start == None and end == None:
                if is_custom == "true":
                    ReportList = DailyReport.objects.filter(is_custom=True)
                elif is_purchase_order.lower() == 'true': 
                    ReportList = DailyReport.objects.filter(is_purchase_order=True)
                elif is_requisition_order == "true":
                    ReportList = DailyReport.objects.filter(is_requisition_order=True)
                else:
                    ReportList = DailyReport.objects.filter(is_custom=False)
                if outlet:
                    ReportList = ReportList.filter(outlet__id=outlet)

            else:
                # month / date / year
                try:
                    start_month, start_day, start_year = start.split("/")
                except:
                    return Response(
                        {
                            "data": [],
                            "error": "Start date is empty or Please use correct format,month/date/year",
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )
                try:
                    end_month, end_day, end_year = end.split("/")
                except:
                    return Response(
                        {
                            "data": [],
                            "error": "End date is empty or Please use correct format,month/date/year",
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )
                start_date = datetime.datetime(year=int(start_year), month=int(start_month), day=int(start_day),
                                               hour=0, minute=0, second=0)  # represents 00:00:00
                end_date = datetime.datetime(year=int(end_year), month=int(end_month), day=int(end_day),
                                             hour=23, minute=59, second=59)    
                # start_date = datetime.datetime.strptime(start, "%m/%d/%Y").date()
                # end_date = datetime.datetime.strptime(end, "%m/%d/%Y").date()
                if is_custom == "true":
                    ReportList = DailyReport.objects.filter(
                        created_at__range=[start_date, end_date], is_custom=True
                    )
                else:
                    ReportList = DailyReport.objects.filter(
                        created_at__range=[start_date, end_date], is_custom=False
                    )
                if outlet:
                    ReportList = ReportList.filter(outlet__id=outlet)


            if len(list(ReportList)) > 0:
                # ReportList =  DailyReport.objects.filter(created_at__range=(start_date, end_date))
                data = []
                for report in ReportList:
                    if report.products is not None or report.product_name is not None:
                        data.append(
                            {
                                "id": report.id,
                                "created_at": report.created_at,
                                "product": report.products.name
                                if report.products != None
                                else report.product_name,
                                # "image": report.products.thumb.url if report.products.thumb else None,
                                "total_sales": report.quantity,
                                "total_amount": report.total_amount,
                                "is_custom": report.is_custom,
                            }
                        )

                return Response({"data": data}, status=status.HTTP_200_OK)
            return Response({"data": []}, status=status.HTTP_200_OK)

        except Exception as e:
            traceback.print_exc()
            data = {"data": [], "error": str(e)}
            return Response(data, status=status.HTTP_404_NOT_FOUND)


class GetDailyReportOutlet(APIView):
    permission_classes = (AllowAny,)
    # permission_classes = (CustomDjangoModelPermissions, IsAuthenticated)
    queryset = DailyReport.objects.all()

    def get(self, request):
        try:
            today = datetime.datetime.today()
            start = request.GET.get("start")
            end = request.GET.get("end")
            outlet = request.GET.get("outlet", None)  

            from coreapp.helper import print_log
            ReportList = []
            invoices = Invoice.objects.filter(outlet__id=outlet)
            if start is not None and end is not None:
                start_month, start_day, start_year = start.split("/")
                end_month, end_day, end_year = end.split("/")
                start_date = datetime.datetime(year=int(start_year), month=int(start_month), day=int(start_day),
                                               hour=0, minute=0, second=0)  # represents 00:00:00
                end_date = datetime.datetime(year=int(end_year), month=int(end_month), day=int(end_day),
                                             hour=23, minute=59, second=59)
                invoices = invoices.filter(invoice_date__range=[start_date, end_date])
            filtered_invoice_ids = invoices.values_list('id', flat=True)
            invoice_products = Invoice_Products.objects.filter(invoice__in=filtered_invoice_ids)
       
            
            products_dict = {}
            
            for inv_prod in invoice_products:
                if inv_prod.product_name not in products_dict:
                    products_dict[inv_prod.product_name] = {
                        'product': inv_prod.product_name,
                        'quantity': 0,
                        'total_sales': 0,
                        'created_at': inv_prod.invoice_date,
                    }
                products_dict[inv_prod.product_name]['quantity'] += inv_prod.quantity
                products_dict[inv_prod.product_name]['total_sales'] += inv_prod.total

            final_data = {
                "product_data":products_dict.values(),
                "combined_total_cash_recieved":invoices.aggregate(Sum('total_cash_recieved'))['total_cash_recieved__sum'],
                "combined_change_amount":invoices.aggregate(Sum('change_amount'))['change_amount__sum'],
                "combined_total_sales":invoice_products.aggregate(Sum('total'))['total__sum'],

            }


            return Response(final_data, status=status.HTTP_200_OK)

        except Exception as e:
            traceback.print_exc()
            data = {"data": [], "error": str(e)}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
class DeleteDailyReport(APIView):
    permission_classes = (CustomDjangoModelPermissions, IsAuthenticated)
    queryset = DailyReport.objects.all()

    def get_object(self, pk):
        try:
            return DailyReport.objects.get(pk=pk)
        except DailyReport.DoesNotExist:
            raise Http404

    def delete(self, request, pk, format=None):
        DailyReport.objects.get(pk=pk).delete()
        return Response({"data": "Deleted"}, status=status.HTTP_204_NO_CONTENT)


class InvoiceNewProductsView(APIView):
    def post(self, request):
        try:
            data = request.data.get("data")
            run = 0
            for item in data:
                product = item["product"]
                product_name = item.get("product_name", None)
                variant = item["variant"]
                invoice = item["invoice"]
                quantity = item["quantity"]
                price = item["price"]
                total = item["total"]

                try:
                    newObj = Invoice_Products.objects.create(
                        product_id=product,
                        product_name=product_name,
                        variant_id=variant,
                        invoice_id=invoice,
                        quantity=quantity,
                        total=total,
                    )
                except (
                    Exception
                ) as e:  # in except that means this product or its variant doesn't exist anymore
                    traceback.print_exc()
                data = {"data": "created"}
            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            msg = str(e)
            return Response({"msg": msg}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        try:
            data = request.data.get("data")
            for item in data:
                product = item["product"]
                product_name = item.get("product_name", None)
                variant = item["variant"]
                invoice = item["invoice"]
                quantity = item["quantity"]
                price = item["price"]
                total = item["total"]
                inv_product_id = item["inv_product_id"]

                try:
                    pass

                except (
                    Exception
                ) as e:  # in except that means this product or its variant doesn't exist anymore
                    traceback.print_exc()

            return Response({"data": "Updated"}, status=status.HTTP_200_OK)

        except Exception as e:
            msg = str(e)
            return Response({"msg": msg}, status=status.HTTP_400_BAD_REQUEST)


def getNumberofDays():
    count = 6
    today = date.today()
    while 1:
        my_date = today - timedelta(days=count)
        dayname = calendar.day_name[my_date.weekday()]
        print(dayname)
        if dayname == "Saturday":
            break
        count -= 1

    return count


def getTodayDay(today):
    dayname = calendar.day_name[today.weekday()]
    return dayname


dateFormat = "%d-%m-%Y"


class ReportChartData(APIView):
    permission_classes = [
        AllowAny,
    ]

    def get(self, request):
        try:
            filter_by = request.GET.get("filter", "week")
            is_custom = request.GET.get("is_custom", None)
            is_purchase_order = request.GET.get("is_purchase_order", None)
            is_requisition_order = request.GET.get("is_requisition_order", None)
            outlet = request.GET.get("outlet", None)

            if filter_by == "week":
                """
                # /api/v1/sales/date/?filter=week
                if /api/v1/sales/date/ default will be current week

                """
                today = date.today()
                start_number = getNumberofDays()
                weeek_started = today - timedelta(days=start_number)
                todays_data = today + timedelta(
                    days=1
                )  # so that it includes in the result

                if is_custom == "true":
                    filtered_data = Invoice.objects.filter(
                        invoice_date__range=[weeek_started, todays_data], is_custom=True
                    )
                    print("filtered_data", filtered_data)
                elif is_custom == "false":
                    filtered_data = Invoice.objects.filter(
                        invoice_date__range=[weeek_started, todays_data],
                        is_custom=False,
                    )
                elif is_purchase_order == "true" and is_custom == None:
                    filtered_data = Invoice.objects.filter(
                        invoice_date__range=[weeek_started, todays_data],
                        is_purchase_order=True,
                    )
                elif is_requisition_order == "true" and is_custom == None:
                    filtered_data = Invoice.objects.filter(
                        invoice_date__range=[weeek_started, todays_data],
                        is_requisition_order=True,
                    )
                else:
                    filtered_data = Invoice.objects.filter(
                        invoice_date__range=[weeek_started, todays_data]
                    )
                if outlet:
                    filtered_data = filtered_data.filter(outlet__id=outlet)
                delta = datetime.timedelta(days=1)
                data = {
                    "Saturday": 0,
                    "Sunday": 0,
                    "Monday": 0,
                    "Tuesday": 0,
                    "Wednesday": 0,
                    "Thursday": 0,
                    "Friday": 0,
                }

                if len(list(filtered_data)) > 0:
                    for items in filtered_data:
                        data[
                            items.invoice_date.strftime("%A")
                        ] += items.total_amount  # adding all sold data
                        # data[items.created_at.strftime('%d/%m/%Y')] += items.product.total_amount  # adding all sold data

                    return Response({"data": data}, status=status.HTTP_200_OK)
                else:
                    return Response({"data": []}, status=status.HTTP_200_OK)

            if filter_by == "month":
                """
                # /api/v1/sales/date/?filter=month?month=9
                if /api/v1/sales/date/?filter=month default will be current month
                """
                today = datetime.datetime.today()
                year = today.year
                month = today.month
                filter_month = request.GET.get("month", month)
                if is_custom == "true":
                    filtered_data = Invoice.objects.filter(
                        invoice_date__year__gte=year,
                        invoice_date__month__gte=filter_month,
                        invoice_date__year__lte=year,
                        invoice_date__month__lte=filter_month,
                        is_custom=True,
                    )
                elif is_custom == "false":
                    filtered_data = Invoice.objects.filter(
                        invoice_date__year__gte=year,
                        invoice_date__month__gte=filter_month,
                        invoice_date__year__lte=year,
                        invoice_date__month__lte=filter_month,
                        is_custom=False,
                    )
                elif is_purchase_order == "true" and is_custom == None:
                    filtered_data = Invoice.objects.filter(
                        invoice_date__year__gte=year,
                        invoice_date__month__gte=filter_month,
                        invoice_date__year__lte=year,
                        invoice_date__month__lte=filter_month,
                        is_purchase_order=True,
                    )
                elif is_requisition_order == "true" and is_custom == None:
                    filtered_data = Invoice.objects.filter(
                        invoice_date__year__gte=year,
                        invoice_date__month__gte=filter_month,
                        invoice_date__year__lte=year,
                        invoice_date__month__lte=filter_month,
                        is_requisition_order=True,
                    )
                else:
                    filtered_data = Invoice.objects.filter(
                        invoice_date__year__gte=year,
                        invoice_date__month__gte=filter_month,
                        invoice_date__year__lte=year,
                        invoice_date__month__lte=filter_month,
                    )
                if outlet:
                    filtered_data = filtered_data.filter(outlet__id=outlet)
                data = {}
                if len(list(filtered_data)) > 0:
                    for items in filtered_data:
                        data[
                            items.invoice_date.strftime(dateFormat)
                        ] = 0  # intialized 0 to all date
                    now = datetime.datetime.now()
                    year = now.year
                    month = now.month
                    num_days = calendar.monthrange(year, month)[1]
                    days = [
                        datetime.date(year, month, day).strftime(dateFormat)
                        for day in range(1, num_days + 1)
                    ]
                    for dates in days:
                        data[dates] = 0

                    if len(list(filtered_data)) > 0:
                        for items in filtered_data:
                            # print("report -- ", items)
                            # adding all sold data
                            data[
                                items.invoice_date.strftime(dateFormat)
                            ] += items.total_amount

                    sorted_data = {}
                    for key in sorted(data):
                        # print (key, data[key])
                        sorted_data[key] = data[key]
                    return Response({"data": sorted_data}, status=status.HTTP_200_OK)
                else:
                    return Response({"data": []}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ChartDataInvoiceByCreated(APIView):
    permission_classes = [
        AllowAny,
    ]
    def get(self, request):
        try:
            filter_by = request.GET.get("filter", "week")
            is_custom = request.GET.get("is_custom", "false")
            outlet = request.GET.get("outlet", None)

            if filter_by == "week":
                """
                # /api/v1/sales/date/?filter=week
                if /api/v1/sales/date/ default will be current week

                """
                today = date.today()
                start_number = getNumberofDays()
                weeek_started = today - timedelta(days=start_number)
                todays_data = today + timedelta(
                    days=1
                )  # so that it includes in the result
                print("============")
                print("weeek_started", weeek_started)
                print("todays_data", todays_data)
                print("============")
                # filtered_data =  Invoice_Products.objects.all()

                if is_custom == "true":
                    filtered_data = Invoice.objects.filter(
                        invoice_date__range=[weeek_started, todays_data], is_custom=True
                    )
                else:
                    filtered_data = Invoice.objects.filter(
                        invoice_date__range=[weeek_started, todays_data],
                        is_custom=False,
                    )

                delta = datetime.timedelta(days=1)

                data = {
                    "Saturday": 0,
                    "Sunday": 0,
                    "Monday": 0,
                    "Tuesday": 0,
                    "Wednesday": 0,
                    "Thursday": 0,
                    "Friday": 0,
                }
                if outlet:
                    filtered_data = filtered_data.filter(outlet__id=outlet)

                if len(list(filtered_data)) > 0:
                    for items in filtered_data:
                        data[
                            items.invoice_date.strftime("%A")
                        ] += 1  # adding all sold data
                        # data[items.created_at.strftime('%d/%m/%Y')] += items.product.total_amount  # adding all sold data

                    return Response({"data": data}, status=status.HTTP_200_OK)
                else:
                    return Response({"data": []}, status=status.HTTP_200_OK)

            if filter_by == "month":
                """
                # /api/v1/sales/date/?filter=month?month=9
                if /api/v1/sales/date/?filter=month default will be current month
                """
                today = datetime.datetime.today()
                year = today.year
                month = today.month
                filter_month = request.GET.get("month", month)
                if is_custom == "true":
                    filtered_data = Invoice.objects.filter(
                        invoice_date__year__gte=year,
                        invoice_date__month__gte=filter_month,
                        invoice_date__year__lte=year,
                        invoice_date__month__lte=filter_month,
                        is_custom=True,
                    )
                else:
                    filtered_data = Invoice.objects.filter(
                        invoice_date__year__gte=year,
                        invoice_date__month__gte=filter_month,
                        invoice_date__year__lte=year,
                        invoice_date__month__lte=filter_month,
                        is_custom=False,
                    )
                data = {}
                if outlet:
                    filtered_data = filtered_data.filter(outlet__id=outlet)

                if len(list(filtered_data)) > 0:
                    for items in filtered_data:
                        data[
                            items.invoice_date.strftime(dateFormat)
                        ] = 0  # intialized 0 to all date
                    now = datetime.datetime.now()
                    year = now.year
                    month = now.month
                    num_days = calendar.monthrange(year, month)[1]
                    days = [
                        datetime.date(year, month, day).strftime(dateFormat)
                        for day in range(1, num_days + 1)
                    ]
                    for dates in days:
                        data[dates] = 0

                    if len(list(filtered_data)) > 0:
                        for items in filtered_data:
                            # print("report -- ", items)
                            # adding all sold data
                            data[items.invoice_date.strftime(dateFormat)] += 1

                    sorted_data = {}
                    for key in sorted(data):
                        # print (key, data[key])
                        sorted_data[key] = data[key]
                    return Response({"data": sorted_data}, status=status.HTTP_200_OK)
                else:
                    return Response({"data": []}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ChartDataCustomer(APIView):
    def get(self, request):
        try:
            filter_by = request.GET.get("filter", "week")
            if filter_by == "week":
                """
                # /api/v1/sales/date/?filter=week
                if /api/v1/sales/date/ default will be current week

                """
                today = date.today()
                start_number = getNumberofDays()
                weeek_started = today - timedelta(days=start_number)
                todays_data = today + timedelta(
                    days=1
                )  # so that it includes in the result
                print("============")
                print("weeek_started", weeek_started)
                print("todays_data", todays_data)
                print("============")
                # filtered_data =  Invoice_Products.objects.all()
                filtered_data = Customer.objects.filter(
                    created_at__range=[weeek_started, todays_data]
                )
                print("weekly filtered data", filtered_data)
                delta = datetime.timedelta(days=1)

                data = {
                    "Saturday": 0,
                    "Sunday": 0,
                    "Monday": 0,
                    "Tuesday": 0,
                    "Wednesday": 0,
                    "Thursday": 0,
                    "Friday": 0,
                }

                if len(list(filtered_data)) > 0:
                    for items in filtered_data:
                        data[
                            items.created_at.strftime("%A")
                        ] += 1  # adding all sold data
                        # data[items.created_at.strftime('%d/%m/%Y')] += items.product.total_amount  # adding all sold data

                    return Response({"data": data}, status=status.HTTP_200_OK)
                else:
                    return Response({"data": []}, status=status.HTTP_200_OK)

            if filter_by == "month":
                """
                # /api/v1/sales/date/?filter=month?month=9
                if /api/v1/sales/date/?filter=month default will be current month
                """
                today = datetime.datetime.today()
                year = today.year
                month = today.month
                filter_month = request.GET.get("month", month)
                filtered_data = Customer.objects.filter(
                    created_at__year__gte=year,
                    created_at__month__gte=filter_month,
                    created_at__year__lte=year,
                    created_at__month__lte=filter_month,
                )
                data = {}
                if len(list(filtered_data)) > 0:
                    for items in filtered_data:
                        data[
                            items.created_at.strftime(dateFormat)
                        ] = 0  # intialized 0 to all date
                    now = datetime.datetime.now()
                    year = now.year
                    month = now.month
                    num_days = calendar.monthrange(year, month)[1]
                    days = [
                        datetime.date(year, month, day).strftime(dateFormat)
                        for day in range(1, num_days + 1)
                    ]
                    for dates in days:
                        data[dates] = 0

                    if len(list(filtered_data)) > 0:
                        for items in filtered_data:
                            # print("report -- ", items)
                            # adding all sold data
                            data[items.created_at.strftime(dateFormat)] += 1

                    sorted_data = {}
                    for key in sorted(data):
                        # print (key, data[key])
                        sorted_data[key] = data[key]
                    return Response({"data": sorted_data}, status=status.HTTP_200_OK)
                else:
                    return Response({"data": []}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SaveAndSendPdf(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        # invoice =  Invoice.objects.get
        instance = Invoice.objects.filter().first()

        params = {}
        params["is_custom"] = instance.is_custom
        params["number"] = instance.number
        params["barcode"] = instance.barcode
        params["barcode_text"] = instance.barcode_text
        params["invoice_date"] = instance.invoice_date
        params["bill_from"] = instance.bill_from
        params["bill_to"] = instance.bill_to
        params["from_email"] = instance.from_email
        params["to_email"] = instance.to_email
        params["from_mobile"] = instance.from_mobile
        params["to_mobile"] = instance.to_mobile
        params["from_address"] = instance.from_address
        params["to_address"] = instance.to_address
        params["delivery_type"] = instance.delivery_type
        params["delivery_charge"] = instance.delivery_charge
        params["delivery_charge_type"] = instance.delivery_charge_type
        params["payment_type"] = instance.payment_type
        params["delivery_statu s"] = instance.delivery_status
        params["total_due"] = instance.total_due
        params["total_paid"] = instance.total_paid
        params["total_amount"] = instance.total_amount
        params["total_discount"] = instance.total_discount
        params["payment_status"] = instance.payment_status
        params["notes"] = instance.notes
        params["payment_status"] = instance.payment_status
        params["total_due"] = instance.total_due
        params["total_paid"] = instance.total_paid
        params["total_amount"] = instance.total_amount
        params["total_discount"] = instance.total_discount
        params["delivery_type"] = instance.delivery_type
        params["invoice_view_json"] = instance.invoice_view_json
        params[
            "header_image_url"
        ] = "http://ims-backend.kaaruj.cloud/media/default/KAARUJ_PDF_Header.png"
        params[
            "default_image"
        ] = "http://ims-backend.kaaruj.cloud/media/default/product-default.png"
        data = request.data
        import logging

        logger = logging.getLogger("django")
        logger.error(f"-----------test------------------")
        logger.error(f"params : {params}")
        logger.error(f"delivery charge {instance.delivery_charge}")
        logger.error(f"-----------test------------------")
        subtotal = 0
        for i in instance.invoice_view_json:
            subtotal += i["total"]

        params["subtotal"] = subtotal

        file_name, status = save_pdf(params)
        if not status:
            return Response({"error": "error"})
        return HttpResponse(file_name)
