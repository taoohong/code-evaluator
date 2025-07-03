from django.db import models


class AnalysisResult(models.Model):
    filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    task_name = models.CharField(max_length=255, blank=True, null=True)
    evaluation = models.JSONField(default=dict)  # call_groq_llm返回内容
    score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    # 文件内容不存sqlite，存mongodb
