from io import BytesIO
from tempfile import tempdir
import traceback
from urllib import response
import uu
from django.http import HttpResponse
from django.template.loader import get_template
import xhtml2pdf.pisa as pisa
import uuid
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from coreapp.helper import print_log

def sendPdfEmail(subject, message_text, from_mail, to_mail, filepath,params):
    try:
        msg = EmailMultiAlternatives(subject, message_text, from_mail, to_mail)
        msg.attach('invoice.pdf', open(filepath, 'rb').read(), 'application/pdf')
        message_html = render_to_string('invoice/invoice_notify.html', params)
        msg.attach_alternative(message_html, "text/html")
        msg.send()
        print_log(f"Email sent successfully to {to_mail} from {from_mail}")
    except Exception as e:
        print_log('-----------Invoice Create Issue in send email------------------')
        print_log(str(e))


def get_invoice_params(instance):
    params = {}
    params['qr_code'] = instance.qr_code
    params['number'] = instance.number
    params['invoice_date'] = instance.invoice_date
    params['bill_from'] = instance.bill_from
    params['bill_to'] = instance.bill_to
    params['from_email'] = instance.from_email
    params['to_email'] = instance.to_email
    params['from_mobile'] = instance.from_mobile
    params['to_mobile'] = instance.to_mobile
    params['from_address'] = instance.from_address
    params['to_address'] = instance.to_address
    if instance.delivery_type == 0:
        params['delivery_type'] = "Regular"
    else:
        params['delivery_type'] = "Urgent"

    params['delivery_charge'] = instance.delivery_charge
    params['delivery_charge_type'] = instance.delivery_charge_type
    params['payment_type'] = ["COD", "Card", "Bank", "Bkash","Sscommerz"][instance.payment_type]
    params['delivery_status'] = instance.delivery_status
    params['total_due'] = instance.total_due
    params['total_paid'] = instance.total_paid
    params['total_amount'] = instance.total_amount
    params['total_discount'] = instance.total_discount
    if instance.payment_status == 0:
        params['payment_status'] = "Paid"
    if instance.payment_status == 1:
        params['payment_status'] = "UnPaid"
    if instance.payment_status == 2:
        params['payment_status'] = "Due"
    params['notes'] = instance.notes
    params['total_due'] = instance.total_due
    params['total_paid'] = instance.total_paid
    params['total_amount'] = instance.total_amount
    params['total_discount'] = instance.total_discount
    params['invoice_view_json'] = instance.invoice_view_json
    params['header_image_url'] = "https://inventory.clients.devsstream.com/media/default/KAARUJ_PDF_Header.png"
    params['sub_total'] = instance.sub_total
    params['invoice_products'] = []
    for item in instance.get_invoice_products():
        params['invoice_products'].append({
            'product_name': item.product.name,
            'variant_name': item.variant.name,
            'quantity': item.quantity,
            'price': item.product.get_offer_price,
            'quantity': item.quantity,
            'total': item.total,
            'thumb': item.variant.get_thumb_url,
        })
    print_log(f"565656565{params['invoice_products']}")
    return params

# def sendPdfEmail(subject, message,  from_mail, to_mail, filepath):
#     try:
#         msg = EmailMultiAlternatives(subject, message, from_mail, to_mail)
#         msg.attach('invoice.pdf', open(filepath, 'rb').read(), 'application/pdf')
#         msg.send()
#         print(f"Email sent successfully to {to_mail} from {from_mail}")
#     except Exception as e:
#         traceback.print_exc()
#         import logging
#         logger = logging.getLogger('django')
#         logger.error(f'-----------Invoice Create Issue in send email------------------')
#         logger.error(f'{str(e)}')


def save_pdf(params):
    try:
        template = get_template("invoice/index.html")

        # print("params",params)
        html = template.render(params)
        response = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), response)
        # file_name = "changeItlater"
        file_name = uuid.uuid4()
        from pathlib import Path

        directory = f"{settings.BASE_DIR}/media/invoice_pdf/"
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True)  

        try:
            with open(str(settings.BASE_DIR)+f'/media/invoice_pdf/{file_name}.pdf', 'wb+') as output:
                pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), output)
        except Exception as e:
            traceback.print_exc()
        if pdf.err:
            return "", False
        return f"{settings.BASE_DIR}/media/invoice_pdf/{file_name}.pdf", True
    except Exception as e:
        traceback.print_exc()
        import logging
        logger = logging.getLogger('django')
        logger.error(f'-----------Save pdf issue in create invoicel------------------')
        logger.error(f'{str(e)}')
        return "", False
