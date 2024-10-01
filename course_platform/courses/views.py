from django.shortcuts import render
from rest_framework import viewsets, status, filters
from .models import (
    Category, Course, Enrollment, Teacher, Review, Event, Service,
    KnowledgeBaseArticle, FAQ, ContactMessage, Payment, Testimonial, BlogPost, Profile, CourseProgress, Certificate
)
from .serializers import (
    CategorySerializer, CourseSerializer, EnrollmentSerializer, TeacherSerializer,
    ReviewSerializer, EventSerializer, ServiceSerializer, KnowledgeBaseArticleSerializer,
    FAQSerializer, TestimonialSerializer, BlogPostSerializer, ProfileSerializer, CourseProgressSerializer, CertificateSerializer
)
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
from django.shortcuts import render, get_object_or_404
from rest_framework import generics, permissions

stripe.api_key = settings.STRIPE_SECRET_KEY

# Регистрация пользователя
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


# Создание платежа
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment(request):
    user = request.user
    course_id = request.data.get('course_id')

    try:
        course = Course.objects.select_related('category').get(id=course_id)
    except Course.DoesNotExist:
        return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

    intent = stripe.PaymentIntent.create(
        amount=int(course.price * 100),
        currency='usd',
        metadata={'course_id': course.id, 'user_id': user.id},
    )

    Payment.objects.create(
        user=user,
        course=course,
        amount=course.price,
        stripe_payment_intent=intent['id'],
    )

    return Response({'client_secret': intent['client_secret']})


# Вебхук Stripe
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    if not sig_header:
        return JsonResponse({'error': 'Missing Stripe signature header'}, status=400)

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        return JsonResponse({'error': str(e)}, status=400)

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        stripe_payment_id = payment_intent['id']
        Payment.objects.filter(stripe_payment_intent=stripe_payment_id).update(status='succeeded')

    return JsonResponse({'status': 'success'})

class ProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile
    
# Отправка контактного сообщения
@api_view(['POST'])
def submit_contact_message(request):
    name = request.data.get('name')
    email = request.data.get('email')
    message = request.data.get('message')

    if not all([name, email, message]):
        return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

    ContactMessage.objects.create(name=name, email=email, message=message)
    return Response({'success': 'Message submitted successfully'}, status=status.HTTP_201_CREATED)


# Виды представлений для каждой модели
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.prefetch_related('course_set')
    serializer_class = CategorySerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related('category', 'instructor').prefetch_related('reviews')
    serializer_class = CourseSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'duration']


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.select_related('student', 'course')
    serializer_class = EnrollmentSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('course')
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer


class KnowledgeBaseArticleViewSet(viewsets.ModelViewSet):
    queryset = KnowledgeBaseArticle.objects.all()
    serializer_class = KnowledgeBaseArticleSerializer


class FAQViewSet(viewsets.ModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer


class TestimonialViewSet(viewsets.ModelViewSet):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer


# Дополнительные представления для статей и блога
class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer

class CourseProgressListCreateView(generics.ListCreateAPIView):
    queryset = CourseProgress.objects.all()
    serializer_class = CourseProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(student=self.request.user)

    def perform_create(self, serializer):
        # Устанавливаем текущего пользователя как студента
        serializer.save(student=self.request.user)


class CourseProgressDetailView(generics.RetrieveUpdateAPIView):
    queryset = CourseProgress.objects.all()
    serializer_class = CourseProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(student=self.request.user)

    def perform_update(self, serializer):
        # Пересчитываем процент завершения курса при обновлении
        completed_lessons = serializer.validated_data.get('completed_lessons')
        total_lessons = serializer.validated_data.get('total_lessons')
        progress = (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0
        serializer.save(progress=progress)

class CertificateListView(generics.ListAPIView):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(student=self.request.user)
    
def home(request):
    courses = Course.objects.select_related('category', 'instructor').all()
    teachers = Teacher.objects.all()
    return render(request, 'main/home.html', {'courses': courses, 'teachers': teachers})

def courses_list(request):
    courses = Course.objects.all()  # Получаем все курсы из базы данных
    return render(request, 'courses/courses_list.html', {'courses': courses})

# Представление для отображения подробной информации о курсе
def course_details_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    course_data = {
        'title': course.title,
        'description': course.description,
        'instructor': course.instructor.username,
        'price': course.price,
        'duration': course.duration,
        'level': course.get_level_display(),
        'start_date': course.start_date,
        'end_date': course.end_date,
    }
    return JsonResponse(course_data)

def blog_view(request):
    return render(request, 'main/blog.html')

def all_courses_view(request):
    courses = Course.objects.all().values('id', 'title', 'description', 'price', 'duration')
    return JsonResponse(list(courses), safe=False)

@api_view(['GET'])
def get_faqs(request):
    faqs = FAQ.objects.all()
    serializer = FAQSerializer(faqs, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def instructor_courses_view(request, instructor_id):
    """
    Возвращает список курсов, преподаваемых конкретным преподавателем.
    """
    courses = Course.objects.filter(instructor_id=instructor_id).values('title', 'category__name', 'price', 'duration', 'start_date', 'end_date')
    return Response(list(courses))