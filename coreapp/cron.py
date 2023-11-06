from sales.cron import *
from inventory.cron import *
from .helper import print_log


def ExecuteAllCrons():
    try:
        createDailyReport(is_regular=True)
        print_log("createDailyReport(is_regular=True) executed")
    except Exception as e:
        print_log(f"Error in createDailyReport(is_regular=False) : {e}")
    try:
        createDailyReport(is_outlet=True)
        print_log("createDailyReport(is_outlet=True) executed")
    except Exception as e:
        print_log(f"Error in createDailyReport(is_outlet=False) : {e}")
    try:
        createDailyReport(is_requisition_order=True)
        print_log("createDailyReport(is_requisition_order=True) executed")
    except Exception as e:
        print_log("Error in createDailyReport(is_requisition_order=True) : "+str(e))
    
    try:
        createDailyReport(is_purchase_order=True)
        print_log("createDailyReport(is_purchase_order=True) executed")
    except Exception as e:
        print_log("Error in createDailyReport(is_purchase_order=True) : "+str(e))
    
    try:
        createDailyReport_custom()
        print_log("createDailyReport_custom() executed")
    except Exception as e:
        print_log("Error in createDailyReport_custom() : "+str(e))
    try:
        UpdateProductOrder()
        print_log("UpdateProductOrder() executed")
    except Exception as e:
        print_log("Error in UpdateProductOrder() : "+str(e))

    try:
        test()
    except Exception as e:
        print_log("Error in test() : "+str(e))
    

        
