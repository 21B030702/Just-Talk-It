from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Enrollment, Payment

print("Signals module loaded!")

@receiver(post_save, sender=Enrollment)
def send_enrollment_confirmation(sender, instance, created, **kwargs):
    if created and instance.status == 'confirmed':
        print(f"Enrollment Signal triggered for: {instance}")
        print(f"Sending mail to: {instance.student.email}")
        send_mail(
            subject='Enrollment Confirmed',
            message=f'Your enrollment for the course "{instance.course.title}" has been confirmed.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.student.email],
        )

@receiver(post_save, sender=Payment)
def send_payment_confirmation(sender, instance, created, **kwargs):
    if created and instance.status == 'succeeded':
        print(f"Payment Signal triggered for: {instance}")
        print(f"Sending mail to: {instance.user.email}")
        send_mail(
            subject='Payment Successful',
            message=f'Your payment for the course "{instance.course.title}" has been successfully processed.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.user.email],
        )
