from django.shortcuts import render
from rest_framework import viewsets, filters
from .models import Category, Course, Enrollment, Teacher, Review, Event, Service, KnowledgeBaseArticle, FAQ, ContactMessage, Payment
from .serializers import CategorySerializer, CourseSerializer, EnrollmentSerializer, TeacherSerializer, ReviewSerializer, EventSerializer, ServiceSerializer, KnowledgeBaseArticleSerializer, FAQSerializer
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import filters
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.decorators import permission_classes
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment(request):
    user = request.user
    if not user.is_authenticated:
        return Response({"error": "User must be authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

    course_id = request.data.get('course_id')
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

    # Найдем выбранный курс
    course = Course.objects.get(id=course_id)

    # Создаем платежное намерение (PaymentIntent) в Stripe
    intent = stripe.PaymentIntent.create(
        amount=int(course.price * 100),  # Stripe работает с центами
        currency='usd',
        metadata={'course_id': course.id, 'user_id': user.id},
    )

    # Создаем запись о платеже в базе данных
    payment = Payment.objects.create(
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
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = 'your-webhook-secret'

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({'error': str(e)}, status=400)

    # Обработка события подтверждения оплаты
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        stripe_payment_id = payment_intent['id']
        # Обновляем статус платежа в базе данных
        payment = Payment.objects.get(stripe_payment_intent=stripe_payment_id)
        payment.status = 'succeeded'
        payment.save()

    return JsonResponse({'status': 'success'})

@api_view(['POST'])
def register_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    if not username or not password:
        return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.create_user(username=username, password=password)
    return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
def courses_list(request):
    courses = Course.objects.all()
    return render(request, 'courses/courses_list.html', {'courses': courses})

def home(request):
    courses = Course.objects.all()
    teachers = Teacher.objects.all()
    return render(request, 'main/home.html', {'courses': courses, 'teachers': teachers})

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.Category.objects.prefetch_related('course_set')
    serializer_class = CategorySerializer

@method_decorator(cache_page(60 * 15), name='dispatch')  # Кэширование на 15 минут
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related('category', 'instructor') \
                             .prefetch_related('students')
    serializer_class = CourseSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'duration']

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def create(self, request, *args, **kwargs):
        course_id = request.data.get('course_id')
        enrollment = Enrollment.objects.filter(student=request.user, course_id=course_id, status='confirmed').first()
        if not enrollment:
            return Response({"error": "Вы не завершили этот курс"}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class KnowledgeBaseArticleViewSet(viewsets.ModelViewSet):
    queryset = KnowledgeBaseArticle.objects.all()
    serializer_class = KnowledgeBaseArticleSerializer

    def get_queryset(self):
        level = self.request.query_params.get('level')
        if level:
            return self.queryset.filter(level=level)
        return self.queryset

class FAQViewSet(viewsets.ModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer

@api_view(['POST'])
def submit_contact_message(request):
    name = request.data.get('name')
    email = request.data.get('email')
    message = request.data.get('message')

    if not name or not email or not message:
        return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

    contact_message = ContactMessage.objects.create(name=name, email=email, message=message)
    contact_message.save()
    return Response({'success': 'Message submitted successfully'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def get_faqs(request):
    faqs = FAQ.objects.all()
    serializer = FAQSerializer(faqs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)