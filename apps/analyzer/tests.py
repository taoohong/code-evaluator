from django.test import TestCase
from .models import AnalysisResult

class AnalysisResultModelTest(TestCase):
    def test_create_result(self):
        result = AnalysisResult.objects.create(
            filename="test.py",
            score=85.0,
            suggestions="Test suggestion"
        )
        self.assertEqual(result.filename, "test.py")
        self.assertEqual(result.score, 85.0)