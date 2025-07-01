from django.db import models

class AnalysisResult(models.Model):
    filename = models.CharField(max_length=255)
    score = models.FloatField()
    suggestions = models.TextField()