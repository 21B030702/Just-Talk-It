from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True, help_text="Биография пользователя")
    avatar = models.ImageField(upload_to='profiles/', blank=True, null=True, help_text="Фото профиля")
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# Модель категории курсов
class Category(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.name


# Модель курсов
class Course(models.Model):
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ]
    
    TYPE_CHOICES = [
        ('grammar', 'Grammar'),
        ('conversation', 'Conversation'),
        ('exam_preparation', 'Exam Preparation'),
        ('business', 'Business English'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    duration = models.IntegerField(help_text="Продолжительность в часах", default=1)  
    image = models.ImageField(upload_to='courses/', blank=True, null=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    syllabus = models.TextField(blank=True, null=True, help_text="Программа курса")  
    requirements = models.TextField(blank=True, null=True, help_text="Требования к слушателям")
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner', help_text="Уровень курса")
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='conversation', help_text="Тип курса")
    language = models.CharField(max_length=50, default='English', help_text="Язык курса")
    start_date = models.DateField(blank=True, null=True, help_text="Дата начала курса")
    end_date = models.DateField(blank=True, null=True, help_text="Дата окончания курса")
    is_popular = models.BooleanField(default=False, help_text="Популярный курс")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['id']


# Модель преподавателей
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile', null=True, blank=True)
    name = models.CharField(max_length=100)
    bio = models.TextField()
    image = models.ImageField(upload_to='teachers/', blank=True, null=True)  
    email = models.EmailField(blank=True, null=True)  
    linkedin_url = models.URLField(blank=True, null=True)  
    phone_number = models.CharField(max_length=20, blank=True, null=True)  
    expertise = models.CharField(max_length=200, help_text="Область знаний", blank=True, null=True)

    def __str__(self):
        return self.name


# Модель для платежей
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_payment_intent = models.CharField(max_length=200)  # ID платежа Stripe
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')

    def __str__(self):
        return f"Payment {self.id} - {self.course.title} - {self.amount}"


# Модель отзывов    
class Review(models.Model):
    author = models.CharField(max_length=100)
    text = models.TextField()
    video_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')  
    rating = models.IntegerField(default=5, help_text="Рейтинг от 1 до 5")

    def __str__(self):
        return f"{self.author} - {self.course.title}"


# Модель событий    
class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    location = models.CharField(max_length=200, help_text="Место проведения", blank=True, null=True)

    def __str__(self):
        return self.title


# Модель записей на курсы
class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
     
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    enrolled_on = models.DateTimeField(auto_now_add=True)  
    completion_date = models.DateField(blank=True, null=True, help_text="Дата завершения курса")

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"


# Модель услуг    
class Service(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    def __str__(self):
        return self.title


# Модель статей базы знаний    
class KnowledgeBaseArticle(models.Model):
    title = models.CharField(max_length=200)  
    content = models.TextField()  
    level = models.CharField(max_length=50, default="Beginner")
    created_at = models.DateTimeField(auto_now_add=True)  
    is_featured = models.BooleanField(default=False, help_text="Выделенная статья")

    def __str__(self):
        return self.title


# Модель часто задаваемых вопросов (FAQ)    
class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    category = models.CharField(max_length=100, blank=True, null=True, help_text="Категория FAQ")

    def __str__(self):
        return self.question


# Модель контактных сообщений    
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    message = models.TextField()
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# Модель отзывов студентов    
class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=5, help_text="Рейтинг от 1 до 5")

    def __str__(self):
        return f"{self.name} - {self.course.title}"


# Модель для блогов
class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='blog_images/')
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.CharField(max_length=100, blank=True, null=True, help_text="Теги, разделенные запятыми")

    def __str__(self):
        return self.title
    
class CourseProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='progress')
    completed_lessons = models.IntegerField(default=0, help_text="Количество завершенных уроков")
    total_lessons = models.IntegerField(default=0, help_text="Общее количество уроков")
    progress = models.FloatField(default=0.0, help_text="Процент завершения курса")
    is_completed = models.BooleanField(default=False, help_text="Курс завершен")

    def __str__(self):
        return f"{self.student.username}'s Progress in {self.course.title}"

    class Meta:
        unique_together = ('student', 'course')

class Certificate(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates')
    issued_on = models.DateTimeField(auto_now_add=True)
    certificate_url = models.URLField(blank=True, null=True, help_text="URL сертификата")
    verified = models.BooleanField(default=False, help_text="Сертификат проверен и действителен")

    def __str__(self):
        return f"Certificate for {self.student.username} - {self.course.title}"

    class Meta:
        unique_together = ('student', 'course')
