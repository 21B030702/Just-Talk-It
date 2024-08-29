from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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

    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    duration = models.IntegerField(help_text="Продолжительность в часах", default=1)  
    image = models.ImageField(upload_to='courses/', blank=True, null=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    syllabus = models.TextField(blank=True, null=True, help_text="Программа курса")  
    requirements = models.TextField(blank=True, null=True, help_text="Требования к слушателям")
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner', help_text="Уровень курса")
    start_date = models.DateField(blank=True, null=True, help_text="Дата начала курса")
    end_date = models.DateField(blank=True, null=True, help_text="Дата окончания курса")

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['id']

# Модель преподавателей
class Teacher(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField()
    image = models.ImageField(upload_to='teachers/', blank=True, null=True)  
    email = models.EmailField(blank=True, null=True)  
    linkedin_url = models.URLField(blank=True, null=True)  
    phone_number = models.CharField(max_length=20, blank=True, null=True)  

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

    def __str__(self):
        return self.author

# Модель событий    
class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    image = models.ImageField(upload_to='events/', blank=True, null=True)

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
    status = models.CharField(max_length=20, default='pending')
    enrolled_on = models.DateTimeField(auto_now_add=True)  

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

    def __str__(self):
        return self.title
    
# Модель часто задаваемых вопросов (FAQ)    
class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()

    def __str__(self):
        return self.question

# Модель контактных сообщений    
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    message = models.TextField()

    def __str__(self):
        return self.name
    
