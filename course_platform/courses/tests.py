from rest_framework.test import APITestCase
from django.urls import reverse
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Course, Enrollment, Payment
from unittest.mock import patch
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.core.mail import send_mail

class CourseAPITest(APITestCase):
    def test_get_courses(self):
        url = reverse('course-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

# Тесты для платёжной системы
class PaymentTests(TestCase):
    def setUp(self):
        # Создаем тестового пользователя и аутентифицируем его
        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Создаем тестовый курс
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            price=100.00,
            instructor=self.user
        )

    @patch('stripe.PaymentIntent.create')
    def test_create_payment(self, mock_create_payment):
        # Мокаем создание платежа в Stripe
        mock_create_payment.return_value = {'id': 'pi_test_123', 'client_secret': 'test_secret'}

        # Выполняем запрос создания платежа
        response = self.client.post(reverse('create-payment'), {'course_id': self.course.id})
        self.assertEqual(response.status_code, 200)
        self.assertIn('client_secret', response.json())

        # Проверяем, что платеж был создан в базе данных
        payment = Payment.objects.get(course=self.course, user=self.user)
        self.assertEqual(payment.stripe_payment_intent, 'pi_test_123')


# Тесты сигналов и email-уведомлений
class SignalTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student', password='testpassword', email='student@example.com')
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            price=100.00,
            instructor=self.user
        )

    @patch('courses.signals.send_mail')
    def test_enrollment_confirmation_email(self, mock_send_mail):
        # Создание записи на курс
        enrollment = Enrollment.objects.create(student=self.user, course=self.course, status='confirmed')
        
        self.assertTrue(mock_send_mail.called, "send_mail was not called")
        mock_send_mail.assert_called_once_with(
            subject='Enrollment Confirmed',
            message=f'Your enrollment for the course "{self.course.title}" has been confirmed.',
            from_email='test@example.com',
            recipient_list=[self.user.email]
        )

    @patch('courses.signals.send_mail')
    def test_payment_confirmation_email(self, mock_send_mail):
        # Создание записи платежа
        payment = Payment.objects.create(user=self.user, course=self.course, amount=100.00, stripe_payment_intent='pi_test_123', status='succeeded')
        
        self.assertTrue(mock_send_mail.called, "send_mail was not called")
        mock_send_mail.assert_called_once_with(
            subject='Payment Successful',
            message=f'Your payment for the course "{self.course.title}" has been successfully processed.',
            from_email='test@example.com',
            recipient_list=[self.user.email]
        )

# Тесты для middleware логирования
import logging

class MiddlewareTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')

    @patch('courses.middleware.logger')
    def test_request_log_middleware(self, mock_logger):
        # Переход на любую страницу
        self.client.get('/')
        # Проверяем, что логгирование вызвано
        mock_logger.info.assert_called_with(f"User {self.user.username} accessed /")