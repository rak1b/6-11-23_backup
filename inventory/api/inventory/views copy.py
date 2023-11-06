
from . import serializers
from ...models import *
from coreapp.models import User
from coreapp.helper import *

from coreapp.admin import ProductResource,CustomerResource
from .serializers import *
from .filters import *
from utility.utils.model_utils import *
from utility.utils.bulk_utils import ProductBulkImport,CustomerBulkImport
import base64
from utility.utils.printer_utils import print_barcode,convert_zpl
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from weasyprint import HTML
from pdf2image import convert_from_bytes
import os
from utility.utils.resize_utils import get_data_bounding_box

def download(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404


def image_as_base64(image_file, format='png'):
    """
    :param `image_file` for the complete path of image.
    :param `format` is format for image, eg: `png` or `jpg`.
    """
    if not os.path.isfile(image_file):
        return None

    encoded_string = ''
    with open(image_file, 'rb') as img_f:
        encoded_string = base64.b64encode(img_f.read())
    return 'data:image/%s;base64,%s' % (format, encoded_string)

class ExportProductAPIView(APIView):
   permission_classes = (AllowAny,)
   def get(self, request):
        start_date= request.GET.get('start')
        end_date = request.GET.get('end')
        filter = request.GET.get('filter')
        query = request.GET.get('query',"")
        dataset = ProductResource(start_date,end_date,filter,query).export()
        today = datetime.date.today().strftime('%Y-%m-%d %H:%M:%S') # get current date in YYYY-MM-DD format
        filename = f'Products_{today}.xlsx'  # create filename with current date
        response = HttpResponse(dataset.xlsx, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] =f'attachment; filename="{filename}"'
        return response

class ExportCustomerAPIView(APIView):
   permission_classes = (AllowAny,)
   def get(self, request):
        filter = request.GET.get('filter')
        query = request.GET.get('query',"")
        dataset = CustomerResource(filter,query).export()
        today = datetime.date.today().strftime('%Y-%m-%d')  # get current date in YYYY-MM-DD format
        filename = f'Customer_{today}.xlsx'  # create filename with current date
        response = HttpResponse(dataset.xlsx, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] =f'attachment; filename="{filename}"'
        return response

# class ProductImageBase64(APIView):
#     def get(self, request):
#         slug = request.GET.get("slug")
#         print("slug",slug)
#         img = Products.objects.get(slug=slug)
#         print(img.barcode.path)
#         # print_barcode(img.barcode.path)
#         baseStr = ""
#         with open(img.barcode.path, "rb") as img:
#             baseStr = base64.b64encode(img.read())

#         return Response({"data": baseStr})
class ProductImageBase64(APIView):
    permission_classes = (AllowAny,)
    def get(self, request, *args, **kwargs):
        slug = request.GET.get("slug")
        product = get_object_or_404(Products, slug=slug)
        barcode_image = product.barcode.read()  
        barcode_base64 = base64.b64encode(barcode_image).decode("utf-8")
        context = {
            "product": product,
            "barcode_base64": barcode_base64,  
        }
        html_string = render_to_string('invoice/barcode.html', context)
        try:
            pdf_buffer = BytesIO()
            HTML(string=html_string).write_pdf(pdf_buffer)

            pdf_images = convert_from_bytes(pdf_buffer.getvalue())

            if pdf_images:
                image = pdf_images[0]

                left, top, right, bottom = get_data_bounding_box(image)

                cropped_image = image.crop((left, top, right, bottom))

                image_buffer = BytesIO()
                cropped_image.save(image_buffer, format='PNG')

                response = HttpResponse(image_buffer.getvalue(), content_type='image/png')
                response['Content-Disposition'] = 'inline; filename="barcode.png"'
                return response

        except Exception as e:
            return HttpResponse("Error converting HTML to image: {}".format(str(e)))
        
class ProductImageBase64(APIView):
    permission_classes = (AllowAny,)
    def get(self, request, *args, **kwargs):
        slug = request.GET.get("slug")
        product = get_object_or_404(Products, slug=slug)
        barcode_image = product.barcode.read()  
        barcode_base64 = base64.b64encode(barcode_image).decode("utf-8")
        context = {
            "product": product,
            "barcode_base64": barcode_base64,  
        }
        html_string = render_to_string('invoice/barcode.html', context)
        try:
            pdf_buffer = BytesIO()
            HTML(string=html_string).write_pdf(pdf_buffer)

            pdf_images = convert_from_bytes(pdf_buffer.getvalue())

            if pdf_images:
                image = pdf_images[0]

                left, top, right, bottom = get_data_bounding_box(image)

                cropped_image = image.crop((left, top, right, bottom))

                image_buffer = BytesIO()
                cropped_image.save(image_buffer, format='PNG')

                response = HttpResponse(image_buffer.getvalue(), content_type='image/png')
                response['Content-Disposition'] = 'inline; filename="barcode.png"'
                return response

        except Exception as e:
            return HttpResponse("Error converting HTML to image: {}".format(str(e)))
        # return Response({"data": baseStr})
class ProductBarcodePrint(APIView):
    def get(self,request):
        try:
            slug = request.GET.get("slug")
            img = Products.objects.get(slug=slug)
            # print_barcode(img.barcode.path)
            return Response({"data": "success","zpl":convert_zpl(img.barcode.path)})
        except Exception as e:
            print(e)
            return Response({"data": str(e)})

class CategoryView(FilterGivenDate,ModelViewSet):
    permission_classes = (CustomDjangoModelPermissions, IsAuthenticated)
    # permission_classes = (AllowAny,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    search_fields = ['name']
    filterset_fields = ['level','main_category','sub_main_category','category_type']
    # def destroy(self, request, *args, **kwargs):
    #     category = self.get_object()
    #     connectedProducts = Products.objects.filter(category_id=category.id)
    #     for product in connectedProducts:
    #         product.category = None
    #         product.save()
    #     category.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)


    
class ProductViewForInvoice(ModelViewSet):
    permission_classes = (AllowAny,)
    filterset_class = ProductSearchFilter
    queryset = Products.objects.all()
    serializer_class = ProductSerializerForInvoice
    http_method_names = ['get']
    pagination_class = None
    
    @action(detail=True, methods=['get'])
    def outlet(self, request,pk, *args, **kwargs):
        from sales.models import Outlet
        from inventory.api.admin.serializers import OutletProductSerializerForInvoice
        query = request.GET.get('query',"")
        try:
            print(f"pk {pk} args {args} kwargs {kwargs}")
            outlet_info = Outlet.objects.get(id=pk)
            products = outlet_info.get_products(query)
            context={
                "outlet":outlet_info,
                "request":request
            }
            serializer = OutletProductSerializerForInvoice(products,many=True,context=context)
            return Response(serializer.data,status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CustomerViewForInvoice(APIView):
    permission_classes = (AllowAny,)
    # @extend_schema(responses={200, CustomerSerializerForInvoice})
    def get(self, request):
        product = Customer.objects.all()
        serializer =  CustomerSerializerForInvoice(product, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
class ProductView(ModelViewSet):
    # permission_classes = (CustomDjangoModelPermissions, IsAuthenticated)

    permission_classes = (AllowAny,)
    queryset = Products.objects.all().order_by('-updated_at')
    serializer_class = ProductSerializer
    lookup_field = 'slug'
    filterset_class = ProductSearchFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('-updated_at')

    def get_serializer_class(self):
        print("self.action",self.action)
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'ranking':
            return ProductListSerializer
        elif self.action == 'filter':
            return ProductListSerializer
        elif self.action == 'update':
            return ProductSerializer_Update
        elif self.action == 'partial_update':
            return ProductSerializer_Update
        else:
            return ProductSerializer
    @paginate
    @action(detail=False, methods=['get'])
    def filter(self, request, *args, **kwargs):
        start = request.GET.get("start")
        end = request.GET.get("end")
        try:
            start_month, start_day,  start_year = start.split("/")
        except:
            return Response({"data": [], "error": "Start date is empty or Please use correct format,month/date/year"}, status=status.HTTP_404_NOT_FOUND)
        try:
            end_month, end_day,  end_year = end.split("/")
        except:
            return Response({"data": [], "error": "End date is empty or Please use correct format,month/date/year"}, status=status.HTTP_404_NOT_FOUND)
        start_date = datetime.datetime.strptime(start, '%m/%d/%Y').date()
        end_date = datetime.datetime.strptime(end, '%m/%d/%Y').date()
        data =  self.queryset.model.objects.filter(updated_at__range=[start_date, end_date])
        return data

    @paginate
    @action(detail=False, methods=['get'])
    def ranking(self, request):
        try:
            filter_by = request.GET.get("filter", "today")  # default today
            if (filter_by == "today"):
                return filter_utils.todays_queryset(Products)
                 
            if (filter_by == "week"):
                return filter_utils.weekly_queryset(Products)

            if (filter_by == "month"):
                return filter_utils.monthly_queryset(Products)

            if (filter_by == "year"):
                return filter_utils.yearly_queryset(Products)
            if (filter_by == "all"):
                return  Products.objects.all().order_by("-created_at")
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(request=ProductSerializerForStatusUpdate, )
    @action(detail=False, methods=['post'])
    def update_status(self, request, *args, **kwargs):
        try:
            products_ids = request.data.get("products", None)
            is_new_arrival = request.data.get("is_new_arrival", False)
            is_trending = request.data.get("is_trending", False)
            print("request.POST",request.POST)
            print(f"products_ids {products_ids} is_new_arrival {is_new_arrival} is_trending {is_trending}")
            if products_ids is None:
                return Response({"error": "Please provide products ids"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                products_update = Products.objects.filter(id__in=products_ids)
                if is_new_arrival is not None:
                    products_update.update(is_new_arrival=is_new_arrival,updated_at=timezone.now())
                if is_trending is not None:
                    products_update.update(is_trending=is_trending,updated_at=timezone.now())
                
            return Response({"data": "success"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProductVariantView(ModelViewSet):
    permission_classes = (CustomDjangoModelPermissions, IsAuthenticated)
    queryset = Variant.objects.all()
    serializer_class = VariantSerializer


def getNumberofDays():
    count = 6
    today = date.today()
    while 1:
        my_date = today - timedelta(days=count)
        dayname = calendar.day_name[my_date.weekday()]
        if (dayname == 'Saturday'):
            break
        count -= 1

    return count


def getTodayDay(today):
    dayname = calendar.day_name[today.weekday()]
    return dayname


class productUpdateView(APIView):
    pass
    def post(self, request):
        variant_data = request.data.get("data")
        print("variant_data", variant_data)
        created_and_added = []
        try:
            for data in variant_data:

                variant = data['variant']
                price = data['price']
                stock = data['stock']
                product = data['product']
                is_active = data['is_active']

                created_and_added.append(variant)  # storing to delete other which are remaining

                # ---Check variant exists----
                variantFound = ProductVariants.objects.filter(Q(variant=variant) & Q(product_id=product)).first()
                # variantFound = ProductVariants.objects.filter(Q(variant='39-Floral') & Q(product_id=970)).first()

                if variantFound is not None:
                    variantFound.price = price
                    variantFound.stock = stock
                    variantFound.is_active = is_active
                    variantFound.save()

                # ---Else create variants----
                else:
                    ProductVariants.objects.create(variant=variant, price=price, stock=stock,
                                                   product_id=product, is_active=is_active)
                print("created_and_added----", created_and_added)
                # need_delete = ProductVariants.objects.filter(
                #     ~Q(variant__in=created_and_added) & Q(product_id=product)).delete()  # deleteed old data
                need_delete = ProductVariants.objects.filter(
                    ~Q(variant__in=created_and_added) & Q(product_id=product))
                print("need_delete", need_delete)

            return Response({"data": "Deleted and created"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            traceback.print_exc()
            return Response({"data": str(e)}, status=status.HTTP_404_NOT_FOUND)



class AttributeViewSet(ModelViewSet):
    """
    A ViewSet for create,view and delete attributes.
    """
    permission_classes = (CustomDjangoModelPermissions, IsAuthenticated)
    # permission_required = ('inventory.view_attributes', 'inventory.change_attributes')
    queryset = Attributes.objects.all()
    serializer_class = AttributeSerializer

    http_method_names = ['get', 'post', 'delete']


class CustomerViewSet(FilterGivenDate,ModelViewSet):
    """
    A ViewSet for create,view and delete Customer.
    """
    permission_classes = (CustomDjangoModelPermissions, IsAuthenticated)
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    lookup_field = 'slug'
    filterset_class = CustomerFilter
    filter_backends = [filters.SearchFilter]
    search_fields = ["email",  "mobile", "name", "to_address", "to_address2", "to_city", "to_country", "to_district", "to_division", "to_zip_code"]

    def list(self, request, *args, **kwargs):
        filter = request.query_params.get('filter', None)
        @paginate
        def get_ascending_descending(self):
            if filter == 'ascending':
                return  sorted(Customer.objects.all(), key= lambda current:current.total_purchase_method,reverse=False)
            if filter == 'descending':
                return  sorted(Customer.objects.all(), key= lambda current:current.total_purchase_method,reverse=True)
        if filter is not None and (filter == 'ascending' or filter == 'descending'):
            return get_ascending_descending(self)
        else:
            return super().list(request, *args, **kwargs)


class BulkExportView(APIView):
    permission_classes = (CustomDjangoModelPermissions, IsAuthenticated)

    def get_queryset(self):
        return Products.objects.all()

    @ extend_schema(request=ProductSerializer, responses={201: ProductSerializer})
    def get(self, request, format=None):
        try:

            queryset = Products.objects.all()
            serializer = ProductSerializer(queryset, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            data = {
                "msg": "Data Doesn't Exists"
            }
            return Response(data, status=status.HTTP_404_NOT_FOUND)


fs = FileSystemStorage(location='media/csv')


# class BulkImportView(APIView):
#     permission_classes = (CustomDjangoModelPermissions, IsAuthenticated)

#     def get_queryset(self):
#         return Products.objects.all()

#     @ extend_schema(request= ProductSerializer, responses={201:  ProductSerializer})
#     def post(self, request, format=None):
#         """Upload data from CSV"""
#         file = request.FILES["file"]
#         print("file--", file)
#         content = file.read()  # these are bytes
#         file_content = ContentFile(content)
#         file_name = fs.save(
#             "_tmp.xlsx", file_content
#         )
#         uploaded_file_path = fs.path(file_name)
#         try:
#             result = BulkImportFunction(uploaded_file_path)
#             if result == 1:
#                 data = {'data': "success"}
#                 return Response(data, status=status.HTTP_201_CREATED)

#             else:
#                 data = result
#                 return Response(data, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             errors = {
#                 'msg': "Please Upload Excel Files Only..",
#                 'error': str(e)
#             }
#             return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class ProductBulkImportAPI(APIView,ProductBulkImport):
#     permission_classes = (CustomDjangoModelPermissions, IsAuthenticated)
    permission_classes = (AllowAny,)

    @ extend_schema(request=BulkProductSerializer, responses={201: BulkProductSerializer})
    def post(self, request, format=None):
        '''
        Product Demo excel file:\n
        https://docs.google.com/spreadsheets/d/1K6kReiwXrSj1sbaKkOagA-_ObQpV2ihsOHK2T3z5Oz0/edit?usp=sharing
        '''
        file = request.FILES["file"]
        file_location = '/bulk/product/'
        # try:
        result = self.bulk_import(file,file_location,request)
        if result == 1:
            data = {'data': "success"}
            return Response(data, status=status.HTTP_201_CREATED)

        else:
            data = result
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

class CustomerBulkImportView(APIView,CustomerBulkImport):
    permission_classes = (AllowAny, )
    # permission_classes = (CustomDjangoModelPermissions, IsAuthenticated)

    def get_queryset(self):
        return Customer.objects.all()

    @ extend_schema(request= BulkProductSerializer, responses={201:  CustomerSerializer})
    def post(self, request, format=None):
        '''
        Product Demo excel file:\n
        https://docs.google.com/spreadsheets/d/1yfk3wRgMBe2wMy_9N0B4Fh__i1Gc1sZOPfmjBjq-dDg/edit?usp=sharing        '''
        file = request.FILES["file"]
        file_location = '/bulk/customer/'
        # try:
        result = self.bulk_import(file,file_location,request)
        if result == 1:
            data = {'data': "success"}
            return Response(data, status=status.HTTP_201_CREATED)

        else:
            data = result
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
    