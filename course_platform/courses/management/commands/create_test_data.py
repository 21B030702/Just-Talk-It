from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from courses.models import Category, Course, Teacher, Enrollment
from datetime import datetime

class Command(BaseCommand):
    help = "Создает тестовые данные для курсов, категорий, преподавателей и студентов."

    def handle(self, *args, **kwargs):
        # 1. Создание тестовых категорий
        categories = [
            "General English",
            "Business English",
            "Grammar",
            "Exam Preparation",
            "Conversation"
        ]
        for category in categories:
            Category.objects.get_or_create(name=category, description=f"Category for {category} courses.")

        # 2. Создание тестовых преподавателей
        teacher1, _ = User.objects.get_or_create(username="teacher1", email="teacher1@example.com", password="teacherpassword")
        teacher2, _ = User.objects.get_or_create(username="teacher2", email="teacher2@example.com", password="teacherpassword")

        # Присваиваем их к модели Teacher
        Teacher.objects.get_or_create(name="John Doe", email=teacher1.email, bio="Experienced English Teacher", image=None, user=teacher1)
        Teacher.objects.get_or_create(name="Jane Smith", email=teacher2.email, bio="Business English Instructor", image=None, user=teacher2)

        # 3. Создание тестовых курсов
        course_titles = ["English for Beginners", "Advanced Business English", "IELTS Preparation", "Fluency in English", "Mastering Grammar"]
        course_data = [
            {"title": "English for Beginners", "description": "Basic English Course", "price": 50, "duration": 20, "level": "beginner"},
            {"title": "Advanced Business English", "description": "Business English for Professionals", "price": 100, "duration": 30, "level": "advanced"},
            {"title": "IELTS Preparation", "description": "Get ready for the IELTS exam", "price": 120, "duration": 40, "level": "advanced"},
            {"title": "Fluency in English", "description": "Become fluent in everyday conversations", "price": 70, "duration": 25, "level": "intermediate"},
            {"title": "Mastering Grammar", "description": "Comprehensive grammar course", "price": 80, "duration": 30, "level": "intermediate"},
        ]

        # Привязка преподавателей к курсам
        for idx, course_info in enumerate(course_data):
            category = Category.objects.get(name=categories[idx % len(categories)])
            instructor = User.objects.get(username=f"teacher{idx % 2 + 1}")
            Course.objects.get_or_create(
                title=course_info['title'],
                description=course_info['description'],
                price=course_info['price'],
                duration=course_info['duration'],
                instructor=instructor,
                category=category,
                syllabus="Basic syllabus content",
                requirements="General knowledge of English",
                level=course_info['level'],
                start_date=datetime.now(),
                end_date=datetime.now()
            )

        # 4. Создание тестовых учеников
        student1, _ = User.objects.get_or_create(username="student1", email="student1@example.com", password="studentpassword")
        student2, _ = User.objects.get_or_create(username="student2", email="student2@example.com", password="studentpassword")

        # 5. Запись студентов на тестовые курсы
        courses = Course.objects.all()
        for idx, course in enumerate(courses):
            student = student1 if idx % 2 == 0 else student2
            Enrollment.objects.get_or_create(student=student, course=course, status="confirmed")

        self.stdout.write(self.style.SUCCESS("Тестовые данные успешно созданы!"))
