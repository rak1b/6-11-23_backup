import django_filters
from ..models import *
# https://www.youtube.com/watch?v=FTUxl5ZCMb8&ab_channel=BugBytes



class InvoiceSearchFilter_forInventory(django_filters.FilterSet):
    address_filter = django_filters.CharFilter(method='get_filter_address', label="address_filter")
    export_data = django_filters.BooleanFilter(method='get_export_data', label="export_data") 
    query = django_filters.CharFilter(method='get_query_filter', label="search")
    class Meta:
        model = Invoice
        fields = ['number','is_purchase_order','is_custom','is_requisition_order','is_outlet','is_regular','outlet','is_draft',"payment_status","delivery_status"]
    def get_filter_address(self, queryset, name, address):
        invoice_list = queryset.filter(
            Q(to_address__icontains=address) |
            Q(to_address__icontains=address) |
            Q(to_city__icontains=address) |
            Q(to_division__icontains=address)
        )
        return invoice_list
    
    def get_export_data(self, queryset, name, export_data):
        return queryset
    
    def get_query_filter(self, queryset, name, filter_by):
        delivery_status_queue = {
            "Returned": 0,
            "Recieved": 1,
            "Delivered": 2,
            "Pending": 3,
            "Hold": 4,
            "Dispatched": 5,
        }

        source_status_queue = {"Ecommerce Website": 0, "Inventory": 1, "Admin Panel": 2}

        delivery_type_queue = {"Regular": 0, "Urgent": 1}

        payment_status_queue = {"Paid": 0, "Unpaid": 1, "Due": 2}

        q = self.request.query_params.get("query")
        if q:

            queryset = queryset.filter(
                Q(number__icontains=q)
                | Q(created_by__first_name__icontains=q)
                | Q(created_by__last_name__icontains=q)
                | Q(total_amount__icontains=q)
                | Q(invoice_date__icontains=q)
                | Q(
                    delivery_status__in=[
                        delivery_status_queue[label]
                        for label in delivery_status_queue
                        if label.lower().startswith(q.lower())
                    ]
                )
                | Q(
                    source__in=[
                        source_status_queue[label]
                        for label in source_status_queue
                        if q.lower() in label.lower()
                    ]
                )
                | Q(
                    delivery_type__in=[
                        delivery_type_queue[label]
                        for label in delivery_type_queue
                        if label.lower().startswith(q.lower())
                    ]
                )
                | Q(
                    payment_status__in=[
                        payment_status_queue[label]
                        for label in payment_status_queue
                        if label.lower().startswith(q.lower())
                    ]
                )|Q(bill_to__icontains=q) | Q(to_mobile__icontains=q )
            )
        return queryset
class InvoiceFilter(django_filters.FilterSet):
    class Meta:
        model = Invoice
        fields = {
            'number': ['icontains'],
            'created_by__first_name': ['icontains'],
            'total_amount': ['icontains'],
            'created_at': ['lt', 'gt'],
            'updated_at': ['lt', 'gt'],
        }
        

class InvoiceSearchFilter(django_filters.FilterSet):
    query = django_filters.CharFilter(method='my_custom_filter', label="search")
    to_mobile = django_filters.CharFilter(method='to_mobile_filter', label="to_mobile")

    class Meta:
        model = Invoice
        fields = ['query','created_for']

    def my_custom_filter(self, queryset, name, filter_by):
        return queryset.filter(is_custom=False).filter( Q(created_by__first_name__icontains=filter_by) | Q(created_by__last_name__icontains=filter_by) | Q(total_amount__icontains=filter_by) | Q(number__icontains=filter_by))

    def to_mobile_filter(self, queryset, name, filter_by):
        return queryset.filter(to_mobile__icontains=filter_by)


class CustomInvoiceSearchFilter(django_filters.FilterSet):
    query = django_filters.CharFilter(method='my_custom_filter', label="search")

    class Meta:
        model = Invoice
        fields = ['query']

    def my_custom_filter(self, queryset, name, filter_by):
        return queryset.filter(is_custom=True).filter( Q(created_by__first_name__icontains=filter_by) | Q(created_by__last_name__icontains=filter_by) | Q(total_amount__icontains=filter_by) | Q(number__icontains=filter_by))
