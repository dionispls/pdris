from django.test import TestCase


class BasicTestCase(TestCase):
    def test_basic(self):
        """Простой тест для проверки работы тестовой среды"""
        self.assertEqual(1 + 1, 2)
