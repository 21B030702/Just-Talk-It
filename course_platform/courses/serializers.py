from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Category, Course, Enrollment, Teacher, Review, Event,
    Service, KnowledgeBaseArticle, FAQ, Payment, Testimonial, BlogPost, ContactMessage, Profile, CourseProgress, Certificate
)

class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Profile
        fields = ['user', 'bio', 'avatar', 'phone_number', 'location']


# Сериализатор для модели категории
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'description']


# Сериализатор для модели преподавателей
class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'


# Сериализатор для курсов с вложенными полями
class CourseSerializer(serializers.ModelSerializer):
    # Вложенные сериализаторы для создания курса
    category = CategorySerializer()
    instructor = TeacherSerializer()
    
    reviews = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'price', 'duration',
            'syllabus', 'requirements', 'level', 'type', 'language',
            'start_date', 'end_date', 'is_popular', 'category', 'instructor', 'reviews'
        ]

    def validate_price(self, value):
        """
        Приведение поля 'price' к правильному формату.
        """
        try:
            # Пробуем привести строку к типу Decimal
            return float(value) if isinstance(value, str) else value
        except (ValueError, TypeError):
            raise serializers.ValidationError("Price must be a valid number.")


# Сериализатор для отзывов студентов (Testimonial)
class TestimonialSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Testimonial
        fields = '__all__'


# Сериализатор для управления записями на курсы
class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = '__all__'
        extra_kwargs = {
            'status': {'read_only': True},  # По умолчанию статус будет "pending"
        }


# Сериализатор для отзывов к курсам
class ReviewSerializer(serializers.ModelSerializer):
    course = serializers.SlugRelatedField(slug_field='title', queryset=Course.objects.all())
    author = serializers.CharField()

    class Meta:
        model = Review
        fields = '__all__'


# Сериализатор для модели событий
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


# Сериализатор для управления платежами
class PaymentSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    course = serializers.SlugRelatedField(slug_field='title', read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'


# Сериализатор для управления услугами
class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'


# Сериализатор для статей базы знаний
class KnowledgeBaseArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeBaseArticle
        fields = '__all__'


# Сериализатор для часто задаваемых вопросов (FAQ)
class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'


# Сериализатор для контактных сообщений
class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = '__all__'


# Сериализатор для управления блогами
class BlogPostSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())

    class Meta:
        model = BlogPost
        fields = '__all__'


class CourseProgressSerializer(serializers.ModelSerializer):
    student = serializers.SlugRelatedField(slug_field='username', read_only=True)
    course = serializers.SlugRelatedField(slug_field='title', read_only=True)

    class Meta:
        model = CourseProgress
        fields = '__all__'


class CertificateSerializer(serializers.ModelSerializer):
    student = serializers.SlugRelatedField(slug_field='username', read_only=True)
    course = serializers.SlugRelatedField(slug_field='title', read_only=True)

    class Meta:
        model = Certificate
        fields = '__all__'
