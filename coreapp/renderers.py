from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response


class CustomRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        status_code = renderer_context['response'].status_code
        if status_code == 204:
            status_code = 200
        response = {
            "status": "success",
            "code": status_code,
            "data": data,
            "message": None
        }
        if data is not None and "detail" in data:
            response["message"] = data["detail"]
            del data['detail']
        if not str(status_code).startswith('2'):
            response["status"] = "error"
            response["data"] = None
            try:
                response["message"] = data["detail"]
            except :
                response["errors"] = data
        return super(CustomRenderer, self).render(response, accepted_media_type, renderer_context)

    
class ProductRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        from inventory.models import Products
        from django.db.models import Max, Min
        status_code = renderer_context['response'].status_code
        if status_code == 204:
            status_code = 200
        response = {
            "status": "success",
            "code": status_code,
            'max_price': Products.objects.all().aggregate(Max('price'))['price__max'],
            'min_price': Products.objects.all().aggregate(Min('price'))['price__min'],
            "data": data,
            "message": None,
       
        }
        if data is not None and "detail" in data:

            response["message"] = data["detail"]
            del data['detail']
        if not str(status_code).startswith('2'):
            response["status"] = "error"
            response["data"] = None
            try:
                response["message"] = data["detail"]
            except :
                response["errors"] = data
        return super(ProductRenderer, self).render(response, accepted_media_type, renderer_context)
