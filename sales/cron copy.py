
import datetime
from . import models 
from django.db.models import Q
from inventory.models import Products
import traceback
from django.utils import timezone
def GenerateCronLog(type,failed_msg):
    import datetime
    import logging
    logger = logging.getLogger('django')
    if failed_msg:
        logger.error(f'----------{type} Report Generation Failed at {datetime.datetime.today()} ------------------')
        logger.error(f'-----------{failed_msg} Report Generation Failed at {datetime.datetime.today()} ------------------\n')
    else:
        logger.error(f'-----------{type} Report Generated at {datetime.datetime.today()} ------------------\n')


def createDailyReport(is_custom=False,is_requisition_order=False,is_purchase_order=False):
    from datetime import date
    today = date.today()
    todays_invoices_productss = models.Invoice_Products.objects.filter(Q(invoice_date__contains=today) & Q(invoice__is_custom=is_custom,invoice__is_requisition_order=is_requisition_order,invoice__is_purchase_order=is_purchase_order))
    print(todays_invoices_productss)
    try:
        todaysProductList = {}
        for inv_prod in todays_invoices_productss:
            todaysProductList[inv_prod.product_name] = {
                'name': inv_prod.product_name,
                'quantity':0,
                'total':0,
                'product':inv_prod.product,
                }
        for inv_prod in todays_invoices_productss:
            todaysProductList[inv_prod.product_name]['quantity'] += inv_prod.quantity
            todaysProductList[inv_prod.product_name]['total'] += inv_prod.total

        for key, value in todaysProductList.items():
            today_report_exist = models.DailyReport.objects.filter(Q(created_at__contains=today) & Q(products=value['product']),is_custom=is_custom,is_requisition_order=is_requisition_order,is_purchase_order=is_purchase_order).first()
            if not today_report_exist:
                models.DailyReport.objects.create(is_custom=False,products=value['product'],product_name=value['name'], quantity=value['quantity'], total_amount=value['total'],created_at=timezone.now())

        GenerateCronLog('Daily Sales ',None)
    except Exception as e:
        GenerateCronLog('Daily Sales ',str(e))
        traceback.print_exc()



 

def createDailyReport_custom():
    from datetime import date
    today = date.today()
    # inv = Invoice.objects.filter(invoice_date__contains=datetime.today().date())
    todays_invoices_productss = models.Invoice_Products.objects.filter(Q(invoice_date__contains=today) & Q(invoice__is_custom=True))
    
    # todays_invoices_productss = models.Invoice_Products.objects.filter(is_custom=True)
    try:
        todaysProductList = {}
        for inv_prod in todays_invoices_productss:
            todaysProductList[inv_prod.product_name] = {
                'name':inv_prod.product_name,
                'quantity':0,
                'total':0
                }
        for inv_prod in todays_invoices_productss:
            todaysProductList[inv_prod.product_name]['quantity'] += inv_prod.quantity
            todaysProductList[inv_prod.product_name]['total'] += inv_prod.total

        for key, value in todaysProductList.items():
            models.DailyReport.objects.create(is_custom=True,product_name=value['name'], quantity=value['quantity'], total_amount=value['total'],created_at=timezone.now())


        GenerateCronLog('Custom Sales ',None)
    except Exception as e:
        GenerateCronLog('Custom Sales ',str(e))
        traceback.print_exc()

def createAllDailyReport():
    createDailyReport(is_custom=False)
    createDailyReport(is_requisition_order=True)
    createDailyReport(is_purchase_order=True)
    createDailyReport_custom()

def createDailyReportManual(year=2023, month=1, day=1):
    from datetime import date,datetime
    created_at = datetime(year,month,day)
    today =date(year,month,day)
    todays_invoices_productss = models.Invoice_Products.objects.filter(Q(invoice_date__contains=today) & Q(invoice__is_custom=False))
    print(todays_invoices_productss)
    try:
        todaysProductList = {}
        for inv_prod in todays_invoices_productss:
            todaysProductList[inv_prod.product_name] = {
                'name':inv_prod.product_name,
                'quantity':0,
                'total':0,
                'product':inv_prod.product,
                }
        for inv_prod in todays_invoices_productss:
            todaysProductList[inv_prod.product_name]['quantity'] += inv_prod.quantity
            todaysProductList[inv_prod.product_name]['total'] += inv_prod.total

        for key, value in todaysProductList.items():
            models.DailyReport.objects.create(is_custom=False,products=value['product'],product_name=value['name'], quantity=value['quantity'], total_amount=value['total'],created_at=created_at)

       
    except Exception as e:
        traceback.print_exc()



def createDailyReport_custom_manual(year=2023, month=1, day=1):
    from datetime import date,datetime
    created_at = datetime(year,month,day)
    today =date(year,month,day)
    # inv = Invoice.objects.filter(invoice_date__contains=datetime.today().date())
    todays_invoices_productss = models.Invoice_Products.objects.filter(Q(invoice_date__contains=today) & Q(invoice__is_custom=True))
    print(todays_invoices_productss)
    # todays_invoices_productss = models.Invoice_Products.objects.filter(is_custom=True)
    try:
        todaysProductList = {}
        for inv_prod in todays_invoices_productss:
            todaysProductList[inv_prod.product_name] = {
                'name':inv_prod.product_name,
                'quantity':0,
                'total':0
                }
        for inv_prod in todays_invoices_productss:
            todaysProductList[inv_prod.product_name]['quantity'] += inv_prod.quantity
            todaysProductList[inv_prod.product_name]['total'] += inv_prod.total

        for key, value in todaysProductList.items():
            models.DailyReport.objects.create(is_custom=True,product_name=value['name'], quantity=value['quantity'], total_amount=value['total'],created_at=created_at)

       
    except Exception as e:
        traceback.print_exc()

def createReportManul(year=2023, month=2, day=1):
    createDailyReportManual(year,month,day)
    createDailyReport_custom_manual(year,month,day)




# Mymodel.objects.filter(date_time_field__contains=datetime.date(1986, 7, 28))










# def createDailyReport():
#     today = datetime.datetime.today()
#     start_date = datetime.datetime(year=today.year, month=today.month, day=today.day,
#                                    hour=0, minute=0, second=0)  # represents 00:00:00
#     end_date = datetime.datetime(year=today.year, month=today.month, day=today.day,
#                                  hour=23, minute=59, second=59)  # represents 23:59:59

#     todays_invoices_productss = models.Invoice_Products.objects.filter(
#         Q(invoice_date__range=(start_date, end_date)) & ~Q(product=None))
        

#     try:
#         todaysProductList = []
#         for inv_prod in todays_invoices_productss:
#             # todaysProductList[]
#             if inv_prod.product.id not in todaysProductList:
#                 mainProudct = inv_prod.product.id
#                 todaysProductList.append(mainProudct)
#         for current_prod in todaysProductList:
#             getCurrentProduct = Products.objects.filter(id=current_prod).first()
#             alreadyReportCheck = models.DailyReport.objects.filter(
#                 Q(created_at__range=(start_date, end_date)) & Q(products_id=current_prod)).first()
#             if getCurrentProduct is not None and alreadyReportCheck is None:
#                 models.DailyReport.objects.create(
#                     products_id=getCurrentProduct.id, total_amount=getCurrentProduct.today_total_amount(getCurrentProduct.id), quantity=getCurrentProduct.today_total_sales(getCurrentProduct.id))
#             else:
#                 alreadyReportCheck.total_amount = getCurrentProduct.today_total_amount(getCurrentProduct.id)
#                 alreadyReportCheck.quantity = getCurrentProduct.today_total_sales(getCurrentProduct.id)
#                 alreadyReportCheck.save()
#     except Exception as e:
#         traceback.print_exc()


# def createDailyReport_custom():
#     today = datetime.datetime.today()
#     start_date = datetime.datetime(year=today.year, month=today.month, day=today.day,
#                                    hour=0, minute=0, second=0)  # represents 00:00:00
#     end_date = datetime.datetime(year=today.year, month=today.month, day=today.day,
#                                  hour=23, minute=59, second=59)  # represents 23:59:59

#     todays_invoices_productss = models.Invoice_Products.objects.filter(
#         Q(invoice_date__range=(start_date, end_date)) & Q(is_custom=True))

#     # todays_invoices_productss = models.Invoice_Products.objects.filter(is_custom=True)
        

#     try:
#         todaysProductList = {}
#         for inv_prod in todays_invoices_productss:
#             todaysProductList[inv_prod.product_name] = {
#                 'name':inv_prod.product_name,
#                 'quantity':0,
#                 'total':0
#                 }
#         for inv_prod in todays_invoices_productss:
#             todaysProductList[inv_prod.product_name]['quantity'] += inv_prod.quantity
#             todaysProductList[inv_prod.product_name]['total'] += inv_prod.total

#         for key, value in todaysProductList.items():
#             models.DailyReport.objects.create(is_custom=True,product_name=value['name'], quantity=value['quantity'], total_amount=value['total'])

       
#     except Exception as e:
#         traceback.print_exc()