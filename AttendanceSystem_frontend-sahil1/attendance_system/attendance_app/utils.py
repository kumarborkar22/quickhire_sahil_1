from django.core.mail import send_mail

def send_shift_end_email(user):
    """Send an email notifying the user that their shift has ended."""
    subject = "Shift Over Notification"
    message = f"""\
Hello {user.first_name},

Your shift is over. If you wish to apply for overtime, please visit the dashboard and submit your request.

Best Regards,  
Company Name
    """
    send_mail(
        subject,
        message,
        'no-reply@company.com',
        [user.email],
        fail_silently=False
    )
