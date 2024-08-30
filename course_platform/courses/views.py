from django.shortcuts import render
from rest_framework import viewsets, status, filters
from .models import Category, Course, Enrollment, Teacher, Review, Event, Service, KnowledgeBaseArticle, FAQ, ContactMessage, Payment
from .serializers import CategorySerializer, CourseSerializer, EnrollmentSerializer, TeacherSerializer, ReviewSerializer, EventSerializer, ServiceSerializer, KnowledgeBaseArticleSerializer, FAQSerializer
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.decorators import permission_classes
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from .services import get_course_details, get_instructor_courses, get_all_courses, update_course

stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment(request):
    user = request.user
    course_id = request.data.get('course_id')

    try:
        # Используем select_related для предотвращения дополнительных запросов
        course = Course.objects.select_related('category').get(id=course_id)
    except Course.DoesNotExist:
        return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

    # Создаем платежное намерение (PaymentIntent) в Stripe
    intent = stripe.PaymentIntent.create(
        amount=int(course.price * 100),  # Stripe работает с центами
        currency='usd',
        metadata={'course_id': course.id, 'user_id': user.id},
    )

    # Создаем запись о платеже в базе данных
    Payment.objects.create(
        user=user,
        course=course,
        amount=course.price,
        stripe_payment_intent=intent['id'],
    )

    return Response({
        'client_secret': intent['client_secret']
    })


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    if not sig_header:
        return JsonResponse({'error': 'Missing Stripe signature header'}, status=400)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        return JsonResponse({'error': str(e)}, status=400)

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        stripe_payment_id = payment_intent['id']
        Payment.objects.filter(stripe_payment_intent=stripe_payment_id).update(status='succeeded')

    return JsonResponse({'status': 'success'})


@api_view(['POST'])
def register_user(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not all([username, password]):
        return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

    User.objects.create_user(username=username, password=password)
    return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)


def courses_list(request):
    courses = Course.objects.select_related('category', 'instructor').all()
    return render(request, 'courses/courses_list.html', {'courses': courses})


def home(request):
    courses = Course.objects.select_related('category', 'instructor').all()
    teachers = Teacher.objects.all()
    return render(request, 'main/home.html', {'courses': courses, 'teachers': teachers})


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.prefetch_related('course_set')
    serializer_class = CategorySerializer


def course_details_view(request, course_id):
    course_data = get_course_details(course_id)
    return JsonResponse(course_data)


@method_decorator(cache_page(60 * 15), name='dispatch')  # Кэширование на 15 минут
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related('category', 'instructor').prefetch_related('students')
    serializer_class = CourseSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'duration']

    def get_queryset(self):
        queryset = super().get_queryset()
        if 'popular' in self.request.query_params:
            queryset = queryset.filter(is_popular=True)
        if 'min_price' in self.request.query_params:
            queryset = queryset.filter(price__gte=self.request.query_params.get('min_price'))
        return queryset
    
    def update(self, request, *args, **kwargs):
        # Извлекаем course_id из аргументов
        course_id = kwargs.get('pk')
        updated_data = request.data

        # Вызываем сервис для обновления курса и удаления кэша
        update_course(course_id, updated_data)

        return super().update(request, *args, **kwargs)

def all_courses_view(request):
    courses = get_all_courses()
    return JsonResponse(courses, safe=False)


@method_decorator(cache_page(60 * 30), name='dispatch')
class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.prefetch_related('courses')
    serializer_class = TeacherSerializer


def instructor_courses_view(request, instructor_id):
    courses = get_instructor_courses(instructor_id)
    return JsonResponse(courses, safe=False)


@method_decorator(cache_page(60 * 10), name='dispatch')
class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.select_related('student', 'course')
    serializer_class = EnrollmentSerializer


@method_decorator(cache_page(60 * 10), name='dispatch')
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('course')
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def create(self, request, *args, **kwargs):
        course_id = request.data.get('course_id')
        enrollment = Enrollment.objects.filter(student=request.user, course_id=course_id, status='confirmed').first()
        if not enrollment:
            return Response({"error": "Вы не завершили этот курс"}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)


@method_decorator(cache_page(60 * 20), name='dispatch')
class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


@method_decorator(cache_page(60 * 30), name='dispatch')
class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer


@method_decorator(cache_page(60 * 15), name='dispatch')
class KnowledgeBaseArticleViewSet(viewsets.ModelViewSet):
    queryset = KnowledgeBaseArticle.objects.all()
    serializer_class = KnowledgeBaseArticleSerializer

    def get_queryset(self):
        level = self.request.query_params.get('level')
        return self.queryset.filter(level=level) if level else self.queryset


@method_decorator(cache_page(60 * 30), name='dispatch')
class FAQViewSet(viewsets.ModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer


@cache_page(60 * 10)
@api_view(['GET'])
def get_faqs(request):
    faqs = FAQ.objects.all()
    serializer = FAQSerializer(faqs, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def submit_contact_message(request):
    name = request.data.get('name')
    email = request.data.get('email')
    message = request.data.get('message')

    if not all([name, email, message]):
        return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

    ContactMessage.objects.create(name=name, email=email, message=message)
    return Response({'success': 'Message submitted successfully'}, status=status.HTTP_201_CREATED)
