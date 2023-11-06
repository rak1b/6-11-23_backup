
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from utility.models import Contact
from utility import constants
from decouple import config
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def sendPdfEmail(subject, message_text, from_mail, to_mail,template,params):
    try:
        msg = EmailMultiAlternatives(subject, message_text, from_mail, to_mail)
        message_html = render_to_string(template, params)
        msg.attach_alternative(message_html, "text/html")
        msg.send()
        print(f"Email sent successfully to {to_mail} from {from_mail}")
    except Exception as e:
        import logging
        logger = logging.getLogger('django')
        logger.error('-----------Invoice Create Issue in send email------------------')
        logger.error(str(e))






def sendContactUsEmail(sender, instance, created, **kwargs):
  if created:
    params = {
      "name": instance.name,
      "email": instance.email,
      "mobile": instance.mobile,
      "message": instance.message,
      "contact_type": ["Contact Us","Work With Us"][instance.inquiry_type],
      "inquiry_type": ["Urgent","Normal"][instance.inquiry_type],
      "document": instance.document.get_url if instance.document else None,

    }
    sendPdfEmail(
      subject=f"{instance.name} has contacted you",
      message_text="data",
      from_mail=config("EMAIL_SENDER"),
      to_mail=[config("EMAIL_RECIEVER")],
      template="email/auth/contact_us.html",
      params=params
    )
post_save.connect(sendContactUsEmail, sender=Contact)