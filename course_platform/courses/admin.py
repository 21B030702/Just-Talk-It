from django.contrib import admin
from .models import (
    Category,
    Course,
    Enrollment,
    Teacher,
    Review,
    Event,
    Service,
    KnowledgeBaseArticle,
    FAQ,
    ContactMessage,
    Payment,
    Testimonial,
    BlogPost
)

# Регистрация каждой модели в админ-панели
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'instructor', 'category', 'price', 'start_date', 'end_date')
    search_fields = ('title', 'description')
    list_filter = ('category', 'level', 'instructor')
    list_editable = ('price', 'start_date', 'end_date')  # Позволяет редактировать поля прямо из списка
    date_hierarchy = 'start_date'


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone_number')
    search_fields = ('name', 'email')
    list_filter = ('name',)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'course', 'status', 'enrolled_on')
    search_fields = ('student__username', 'course__title')
    list_filter = ('status', 'course')
    date_hierarchy = 'enrolled_on'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'course', 'created_at')
    search_fields = ('author', 'course__title')
    list_filter = ('course',)
    date_hierarchy = 'created_at'


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'date')
    search_fields = ('title', 'description')
    list_filter = ('date',)
    date_hierarchy = 'date'


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'price')
    search_fields = ('title',)
    list_filter = ('price',)


@admin.register(KnowledgeBaseArticle)
class KnowledgeBaseArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'level', 'created_at')
    search_fields = ('title', 'content')
    list_filter = ('level',)
    date_hierarchy = 'created_at'


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('id', 'question')
    search_fields = ('question',)
    list_filter = ('id',)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone_number', 'message')
    search_fields = ('name', 'email')
    list_filter = ('email',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'course', 'amount', 'stripe_payment_intent', 'status', 'timestamp')
    search_fields = ('user__username', 'course__title')
    list_filter = ('status',)
    date_hierarchy = 'timestamp'


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'course', 'content', 'created_at')
    search_fields = ('name', 'course__title')
    list_filter = ('course',)
    date_hierarchy = 'created_at'


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'created_at')
    search_fields = ('title', 'content')
    list_filter = ('author',)
    date_hierarchy = 'created_at'
