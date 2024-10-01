from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from .views import (
    home, courses_list, course_details_view, register_user, submit_contact_message, 
    blog_view, TestimonialViewSet, create_payment, stripe_webhook, all_courses_view,
    get_faqs, instructor_courses_view, ProfileDetailView
)
from .views import CategoryViewSet, CourseViewSet, TeacherViewSet, EnrollmentViewSet, ReviewViewSet
from .views import EventViewSet, ServiceViewSet, KnowledgeBaseArticleViewSet, FAQViewSet, BlogPostViewSet, CourseProgressListCreateView, CourseProgressDetailView, CertificateListView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Определение маршрутов с помощью DefaultRouter
router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'teachers', TeacherViewSet)
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'events', EventViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'knowledge-base', KnowledgeBaseArticleViewSet)
router.register(r'faqs', FAQViewSet)
router.register(r'testimonials', TestimonialViewSet)
router.register(r'blog-posts', BlogPostViewSet)

schema_view = get_schema_view(
    openapi.Info(
        title="Course Platform API",
        default_version='v1',
        description="API документация для платформы курсов JTI",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Определение URL-шаблонов
urlpatterns = [
    path('', home, name='home'),
    path('courses/', courses_list, name='courses'),
    path('courses/<int:course_id>/', course_details_view, name='course-details'),
    path('courses/all/', all_courses_view, name='all-courses'),  # Маршрут для всех курсов
    path('courses/instructor/<int:instructor_id>/', instructor_courses_view, name='instructor-courses'),  # Курсы преподавателя
    path('register/', register_user, name='register_user'),
    path('blog/', blog_view, name='blog'),  # Страница блога
    path('contact/', submit_contact_message, name='contact'),
    path('api/', include(router.urls)),  # Интеграция маршрутов API из DefaultRouter
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/create-payment/', create_payment, name='create_payment'),
    path('api/stripe-webhook/', stripe_webhook, name='stripe_webhook'),  # Вебхук для Stripe
    path('api/faqs/', get_faqs, name='get_faqs'),  # ЧЗВ
    path('profile/', ProfileDetailView.as_view(), name='profile-detail'),
    path('api/progress/', CourseProgressListCreateView.as_view(), name='course-progress-list-create'),
    path('api/progress/<int:pk>/', CourseProgressDetailView.as_view(), name='course-progress-detail'),
    path('api/certificates/', CertificateListView.as_view(), name='certificate-list'),
    path('courses/all/', all_courses_view, name='all-courses'),
    path('api/faqs/', get_faqs, name='get_faqs'),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
