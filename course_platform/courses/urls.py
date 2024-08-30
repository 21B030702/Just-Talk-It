from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, CourseViewSet, TeacherViewSet, EnrollmentViewSet, ReviewViewSet, EventViewSet, ServiceViewSet, KnowledgeBaseArticleViewSet, create_payment, stripe_webhook, home
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'teachers', TeacherViewSet)
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'events', EventViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'knowledge-base', KnowledgeBaseArticleViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('create-payment/', create_payment, name='create-payment'),
    path('stripe-webhook/', stripe_webhook, name='stripe-webhook'),
    path('', home, name='home'),
]
