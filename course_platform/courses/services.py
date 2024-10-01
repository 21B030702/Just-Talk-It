from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from .models import Course
import logging

# Инициализация логгера для отслеживания кэширования и запросов
logger = logging.getLogger(__name__)

def get_course_details(course_id):
    """
    Получение детализированной информации о курсе с использованием кэширования.
    Если данные не найдены в кэше, извлекает их из базы данных и добавляет в кэш.
    """
    # Получаем данные из кэша
    course_data = cache.get(f'course_details_{course_id}')
    
    if not course_data:
        try:
            # Извлечение курса и связанных данных
            course = Course.objects.select_related('category', 'instructor').get(id=course_id)
            
            # Формирование структуры данных
            course_data = {
                'title': course.title,
                'category': course.category.name,
                'instructor': course.instructor.username,
                'description': course.description,
                'price': str(course.price),
                'duration': course.duration,
                'start_date': course.start_date,
                'end_date': course.end_date,
            }
            
            # Добавление данных в кэш на 10 минут
            cache.set(f'course_details_{course_id}', course_data, 60 * 10)
            logger.info(f"Course details for ID {course_id} cached successfully.")
        except ObjectDoesNotExist:
            logger.error(f"Course with ID {course_id} not found.")
            return None

    return course_data


def get_instructor_courses(instructor_id):
    """
    Получение списка курсов для конкретного преподавателя.
    Если данные не найдены в кэше, извлекает их из базы данных и добавляет в кэш.
    """
    # Пытаемся получить данные из кэша
    courses_data = cache.get(f'instructor_courses_{instructor_id}')
    
    if not courses_data:
        # Оптимизация запроса с использованием select_related и values
        courses = Course.objects.select_related('instructor', 'category') \
                                .filter(instructor_id=instructor_id) \
                                .values('title', 'category__name', 'price', 'duration', 'start_date', 'end_date')

        courses_data = list(courses)

        # Кэшируем результат на 20 минут
        cache.set(f'instructor_courses_{instructor_id}', courses_data, 60 * 20)
        logger.info(f"Instructor courses for ID {instructor_id} cached successfully.")

    return courses_data


def get_all_courses():
    """
    Извлекает и кэширует список всех курсов на 30 минут.
    """
    courses_data = cache.get('all_courses')
    
    if not courses_data:
        # Применяем prefetch_related для более оптимизированного запроса
        courses = Course.objects.select_related('category', 'instructor') \
                                .prefetch_related('students') \
                                .values('id', 'title', 'category__name', 'instructor__username', 'price', 'duration')

        # Формируем данные и кэшируем
        courses_data = list(courses)
        cache.set('all_courses', courses_data, 60 * 30)
        logger.info("All courses data cached successfully.")
    
    return courses_data


def update_course(course_id, updated_data):
    """
    Обновление данных курса и сброс кэша.
    """
    try:
        # Обновление курса на основе переданных данных
        Course.objects.filter(id=course_id).update(**updated_data)

        # Удаление кэша для конкретного курса
        cache.delete(f'course_details_{course_id}')
        logger.info(f"Course with ID {course_id} updated and cache cleared.")
    except Exception as e:
        logger.error(f"Error updating course with ID {course_id}: {str(e)}")
