from . import models 
from django.db.models import Q
from inventory.models import Products
import traceback
from django.utils import timezone
from datetime import timedelta, date
def GenerateCronLog(type,failed_msg):
    import datetime
    import logging
    logger = logging.getLogger('django')
    if failed_msg:
        logger.error(f'----------{type} Report Generation Failed at {datetime.datetime.today()} ------------------')
        logger.error(f'-----------{failed_msg} Report Generation Failed at {datetime.datetime.today()} ------------------\n')
    else:
        logger.error(f'-----------{type} Report Generated at {datetime.datetime.today()} ------------------\n')




def createDailyReport(is_custom=False,is_requisition_order=False,is_purchase_order=False,is_outlet=False,outlet=None):
    today = date.today()
    # today = date.today() - timedelta(days=1)

    todays_invoices_productss = models.Invoice_Products.objects.filter(Q(invoice_date__contains=today) and Q(invoice__is_custom=is_custom,invoice__is_requisition_order=is_requisition_order,invoice__is_purchase_order=is_purchase_order,invoice__is_outlet=is_outlet,invoice__outlet=outlet))
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
                models.DailyReport.objects.create(is_custom=False,products=value['product'],product_name=value['name'], quantity=value['quantity'], total_amount=value['total'],created_at=timezone.now(),is_purchase_order=is_purchase_order,is_requisition_order=is_requisition_order,is_custom=is_custom,is_outlet=is_outlet,outlet=outlet)

        GenerateCronLog('Daily Sales ',None)
    except Exception as e:
        GenerateCronLog('Daily Sales ',str(e))
        traceback.print_exc()



 

def createDailyReport_custom():
    from datetime import date
    today = date.today()
    # today = date.today() - timedelta(days=1)
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
createDailyReportManual(year=2023, month=9, day=29)
def createDailyReportManual(year=2023, month=1, day=1):
    from datetime import date,datetime
    created_at = datetime(year,month,day)
    today =date(year,month,day)
    todays_invoices_productss = models.Invoice_Products.objects.filter(Q(invoice_date__contains=today) & Q(invoice__is_custom=False))
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


