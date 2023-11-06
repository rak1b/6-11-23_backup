from django.core.mail import EmailMessage

def send_email_with_attachment(subject, message, from_email, recipient_list, attachment_file_path):
    try:
        # Create an EmailMessage instance
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=from_email,
            to=recipient_list,
        )
        email.attach_file(attachment_file_path)
        email.send()
        return True  # Email sent successfully
    except Exception as e:
        print(f"An error occurred while sending the email: {str(e)}")
        return False  # Email sending failed

# Example usage:
def send_email():
    subject = "Sample Email with Attachment"
    message = "Please find the attached file."
    from_email = "kaaruj.bd.official@gmail.com"
    from_email = "kaaruj.bd.official@gmail.com"
    recipient_list = ["rak13.dev@gmail.com", ]
    attachment_file_path = r"H:/Devsstream_NEW/kaaruj-backend-v2/media/invoice_pdf/0ef09231-73b3-49f2-a561-a3df792cd42d.pdf"

    if send_email_with_attachment(subject, message, from_email, recipient_list, attachment_file_path):
        print("Email sent successfully")
    else:
        print("Email sending failed")

