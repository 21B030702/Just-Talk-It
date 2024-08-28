from rest_framework.test import APITestCase
from django.urls import reverse

class CourseAPITest(APITestCase):
    def test_get_courses(self):
        url = reverse('course-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
