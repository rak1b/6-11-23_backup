from django_filters import rest_framework as filters
from ..models import *
from rest_framework import serializers
import datetime
from coreapp.models import User
class UserFilterInventory(filters.FilterSet):
    start = filters.CharFilter(
        field_name="start",
        method="filter_start_end",
        label="start",
    )
    end = filters.CharFilter(
        field_name="end",
        method="filter_start_end",
        label="end",
    )

    class Meta:
        model = User
        fields = ["start", "end","is_customer","is_outlet_user","outlet"]

    def filter_start_end(self, queryset, name, value):
        start = self.request.GET.get("start", None)
        end =  self.request.GET.get("end", None)
        if start is None or end is None:
            return queryset
        else:
            start_month, start_day, start_year = start.split("/")
            end_month, end_day, end_year = end.split("/")
            start_date = datetime.datetime(year=int(start_year), month=int(start_month), day=int(start_day),
                                            hour=0, minute=0, second=0)  # represents 00:00:00
            end_date = datetime.datetime(year=int(end_year), month=int(end_month), day=int(end_day),
                                            hour=23, minute=59, second=59)
            queryset = queryset.filter(created_at__range=[start_date, end_date])
            
        return queryset



        # if start is None and end is None:
        #     serializer = self.get_serializer(queryset, many=True)
        #     return Response(serializer.data, status=status.HTTP_200_OK)
        # else:
        #     try:
        #         start_month, start_day, start_year = start.split("/")
        #         end_month, end_day, end_year = end.split("/")
        #         start_date = datetime.datetime(year=int(start_year), month=int(start_month), day=int(start_day),
        #                                        hour=0, minute=0, second=0)  # represents 00:00:00
        #         end_date = datetime.datetime(year=int(end_year), month=int(end_month), day=int(end_day),
        #                                      hour=23, minute=59, second=59)
        #         queryset = queryset.filter(created_at__range=[start_date, end_date])
        #         serializer = self.get_serializer(queryset, many=True)