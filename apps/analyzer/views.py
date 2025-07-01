import os
import pymongo
import requests
from groq import Groq
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from urllib3 import request

from .forms import UploadFileForm
from .models import AnalysisResult

# mongo_client = pymongo.MongoClient(settings.MONGO_URI)
# mongo_db = mongo_client[settings.MONGO_DB]

client = Groq(
    api_key=settings.GROQ_API_KEY,
)

def call_groq_llm(content, file_type):
    prompt = build_prompt(content, file_type)
    print(settings.GROQ_API_KEY)
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="deepseek-r1-distill-llama-70b",
            temperature=0.6,
        )
        completion = chat_completion.choices[0].message.content
        score_line = [line for line in completion.splitlines() if "score" in line.lower()]
        score = 80.0
        if score_line:
            import re
            match = re.search(r'(\d{1,3}(\.\d+)?)', score_line[0])
            if match:
                score = float(match.group(1))
        return {
            'score': score,
            'suggestions': completion
        }
    except Exception as e:
        return {
            'score': 0.0,
            'suggestions': f"Error calling Groq API: {e}"
        }

def build_prompt(content, file_type):
    if file_type == 'sql':
        return f"""
请使用中文评估以下 SQL 脚本的质量，重点关注性能优化、可读性、风险点（如 SQL 注入）以及可维护性。请给出一个 0 到 100 的评分，并提供详细改进建议。

内容如下：
{content}
"""
    else:
        return f"""
请使用中文评估以下代码文件的质量，重点关注可读性、可维护性、性能、安全性、编码风格一致性。请给出一个 0 到 100 的评分，并提供详细改进建议。

内容如下：
{content}
"""

def upload_files(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        save_dir = settings.MEDIA_ROOT
        os.makedirs(save_dir, exist_ok=True)

        if form.is_valid():
            files = request.FILES.getlist('code_files') + request.FILES.getlist('sql_files')
            for f in files:
                save_path = os.path.join(settings.MEDIA_ROOT, f.name)
                with open(save_path, 'wb+') as destination:
                    for chunk in f.chunks():
                        destination.write(chunk)
                with open(save_path, 'r', encoding='utf-8', errors='ignore') as fp:
                    content = fp.read()
                file_type = 'sql' if f.name.endswith('.sql') else 'code'
                # mongo_db.files.insert_one({
                #     'filename': f.name,
                #     'content': content,
                #     'file_type': file_type
                # })
                analysis = call_groq_llm(content, file_type)
                AnalysisResult.objects.create(
                    filename=f.name,
                    score=analysis['score'],
                    suggestions=analysis['suggestions']
                )
            return redirect('analysis_results')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})

def analysis_results(request):
    results = AnalysisResult.objects.all()
    avg_score = sum(r.score for r in results) / results.count() if results.exists() else 0
    return render(request, 'results.html', {'results': results, 'avg_score': avg_score})

def file_detail(request, file_id):
    result = get_object_or_404(AnalysisResult, pk=file_id)
    # file_doc = mongo_db.files.find_one({"filename": result.filename})
    # file_content = file_doc.get("content", "文件内容未找到") if file_doc else "文件内容未找到"
    # return render(request, 'file_detail.html', {'result': result, 'file_content': file_content})

def initialize_system(request):
    try:
        # mongo_db.create_collection("files")
        print('init mongodb')
    except:
        pass
    return HttpResponse("MongoDB collection initialized.")

def sql_analyzer(request):
    return render(request, 'analyzer/sql_analyzer.html', {'active_page': 'sql'})


def code_analyzer(request):
    return render(request, 'analyzer/code_analyzer.html', {'active_page': 'code'})