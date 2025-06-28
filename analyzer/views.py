import os
import pymongo
import requests
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .forms import UploadFileForm
from .models import AnalysisResult

mongo_client = pymongo.MongoClient(settings.MONGO_URI)
mongo_db = mongo_client[settings.MONGO_DB]

def call_groq_llm(content, file_type):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = build_prompt(content, file_type)
    payload = {
        "model": "deepseek-r1-distill-llama-70b",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        completion = response.json()["choices"][0]["message"]["content"]
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
        return f"Evaluate the following SQL script focusing on performance, readability, risk (like SQL injection), and maintainability. Provide a 0-100 score and suggestions.\n\n{content}"
    else:
        return f"Evaluate the following code file (Python) focusing on readability, maintainability, performance, security, and style consistency. Provide a 0-100 score and suggestions.\n\n{content}"

def upload_files(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
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
                mongo_db.files.insert_one({
                    'filename': f.name,
                    'content': content,
                    'file_type': file_type
                })
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
    file_doc = mongo_db.files.find_one({"filename": result.filename})
    file_content = file_doc.get("content", "文件内容未找到") if file_doc else "文件内容未找到"
    return render(request, 'file_detail.html', {'result': result, 'file_content': file_content})

def initialize_system(request):
    try:
        mongo_db.create_collection("files")
    except:
        pass
    return HttpResponse("MongoDB collection initialized.")