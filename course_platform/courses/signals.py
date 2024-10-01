from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Enrollment, Payment
import logging
from django.contrib.auth.models import User
from .models import Profile, CourseProgress, Certificate
import os
from django.template.loader import render_to_string
from .certificate_generator import generate_certificate

# Инициализация логгера
logger = logging.getLogger(__name__)

# Сообщение о загрузке модуля сигналов
logger.info("Signals module loaded!")


@receiver(post_save, sender=Enrollment)
def send_enrollment_confirmation(sender, instance, created, **kwargs):
    """
    Отправляет письмо-подтверждение после успешного создания записи о регистрации на курс.
    """
    if created and instance.status == 'confirmed':
        logger.info(f"Enrollment Signal triggered for: {instance}")
        logger.info(f"Sending enrollment confirmation email to: {instance.student.email}")

        send_mail(
            subject='Enrollment Confirmed',
            message=f'Your enrollment for the course "{instance.course.title}" has been confirmed.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.student.email],
        )

        logger.info(f"Email sent successfully to {instance.student.email}")


@receiver(post_save, sender=Payment)
def send_payment_confirmation(sender, instance, created, **kwargs):
    """
    Отправляет письмо-подтверждение после успешного платежа.
    """
    if created and instance.status == 'succeeded':
        logger.info(f"Payment Signal triggered for: {instance}")
        logger.info(f"Sending payment confirmation email to: {instance.user.email}")

        send_mail(
            subject='Payment Successful',
            message=f'Your payment for the course "{instance.course.title}" has been successfully processed.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.user.email],
        )

        logger.info(f"Email sent successfully to {instance.user.email}")

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

@receiver(post_save, sender=CourseProgress)
def create_certificate(sender, instance, created, **kwargs):
    # Если курс завершен и это новое событие, создаем сертификат
    if instance.is_completed and not Certificate.objects.filter(student=instance.student, course=instance.course).exists():
        Certificate.objects.create(student=instance.student, course=instance.course)

@receiver(post_save, sender=CourseProgress)
def create_certificate(sender, instance, created, **kwargs):
    """
    Создание сертификата после завершения курса и отправка email с PDF-сертификатом.
    """
    if instance.is_completed and not Certificate.objects.filter(student=instance.student, course=instance.course).exists():
        # Генерация сертификата в формате PDF
        student_name = instance.student.username
        course_title = instance.course.title
        certificate_filename = f"{student_name}_{course_title}_certificate.pdf"
        certificate_path = os.path.join(settings.MEDIA_ROOT, 'certificates', certificate_filename)

        # Создаем директорию, если она не существует
        os.makedirs(os.path.dirname(certificate_path), exist_ok=True)

        # Генерация PDF-файла
        generate_certificate(student_name, course_title, certificate_path)

        # Создание записи о сертификате в базе данных
        certificate = Certificate.objects.create(
            student=instance.student,
            course=instance.course,
            certificate_url=f"/media/certificates/{certificate_filename}"
        )

        # Отправка email-уведомления
        subject = "Поздравляем с завершением курса!"
        context = {
            'student_name': student_name,
            'course_title': course_title,
            'certificate_url': f"{settings.SITE_URL}/media/certificates/{certificate_filename}"
        }
        message = render_to_string('emails/course_completion.html', context)

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.student.email],
            fail_silently=False,
        )

# Создание профиля пользователя после создания пользователя
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    # Используйте get_or_create вместо create для избежания дублирования профилей
    Profile.objects.get_or_create(user=instance)
    
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()