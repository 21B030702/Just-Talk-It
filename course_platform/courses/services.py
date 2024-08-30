from django.core.cache import cache
from .models import Course

def get_course_details(course_id):
    # Логика кэширования данных о курсе
    course_data = cache.get(f'course_details_{course_id}')
    
    if not course_data:
        course = Course.objects.select_related('category', 'instructor').get(id=course_id)
        course_data = {
            'title': course.title,
            'category': course.category.name,
            'instructor': course.instructor.username,
        }
        cache.set(f'course_details_{course_id}', course_data, 60 * 10)
    
    return course_data

def get_instructor_courses(instructor_id):
    # Кэшируем список курсов для конкретного преподавателя
    courses_data = cache.get(f'instructor_courses_{instructor_id}')
    
    if not courses_data:
        # Оптимизация запроса с использованием select_related
        courses = Course.objects.select_related('instructor', 'category') \
                                .filter(instructor_id=instructor_id) \
                                .values('title', 'category__name')

        courses_data = list(courses)
        # Кэшируем на 20 минут
        cache.set(f'instructor_courses_{instructor_id}', courses_data, 60 * 20)

    return courses_data

def get_all_courses():
    # Применение prefetch_related для связи ManyToMany и select_related для ForeignKey
    courses = Course.objects.select_related('category', 'instructor') \
                            .prefetch_related('students')

    # Кэширование всех курсов на 30 минут
    cache.set('all_courses', list(courses), 60 * 30)

    return courses

def update_course(course_id, updated_data):
    # Обновляем курс
    Course.objects.filter(id=course_id).update(**updated_data)

    # Удаляем старый кэш
    cache.delete(f'course_details_{course_id}')