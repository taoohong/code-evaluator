import json
import os

import pymongo
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import UploadCodeForm, UploadProjectForm, UploadSQLForm
from .llm_utils import call_groq_llm
from .models import AnalysisResult

# Initialize Groq client
# mongo_client = pymongo.MongoClient(settings.MONGO_URI)
# mongo_db = mongo_client[settings.MONGO_DB]


def analysis_results(request):
    results = AnalysisResult.objects.all()
    avg_score = (
        sum(r.score for r in results) / results.count() if results.exists() else 0
    )
    return render(request, "results.html", {"results": results, "avg_score": avg_score})


def initialize_system(request):
    try:
        # mongo_db.create_collection("files")
        print("init mongodb")
    except:
        pass
    return HttpResponse("MongoDB collection initialized.")


def upload_project(request):
    if request.method == "POST":
        form = UploadProjectForm(request.POST, request.FILES)

        if form.is_valid():
            files = request.FILES.getlist("code_file")
            for f in files:
                save_path = os.path.join(settings.MEDIA_ROOT, f.name)
                with open(save_path, "wb+") as destination:
                    for chunk in f.chunks():
                        destination.write(chunk)
            return render(request, "analyzer/results.html", {"files": files})
    else:
        form = UploadProjectForm()
    return render(request, "code_evaluator/code_evaluator.html", {"form": form})


def upload_code(request):
    if request.method == "POST":
        form = UploadCodeForm(request.POST, request.FILES)

        if form.is_valid():
            file = request.FILES["code_file"]
            content = file.read().decode("utf-8")
            filename = file.name
            file_type = os.path.splitext(filename)[-1].replace(".", "")
            # save_file_to_mongo(filename, content)
            evaluation = call_groq_llm(content, file_type)
            print(f"LLM evaluation result: {evaluation}")
            try:
                risks = json.loads(evaluation)
                final_score = calculate_sql_score(risks)
            except Exception as e:
                risks = []
                final_score = 0.0
                print(f"Error parsing LLM output: {evaluation}{e}")
            AnalysisResult.objects.create(
                filename=filename,
                file_type=file_type,
                description=form.cleaned_data.get("description", ""),
                task_name=form.cleaned_data.get("task_name", ""),
                evaluation=risks,
                score=final_score,
            )
        return render(
            request,
            "analyzer/results.html",
            {
                "filename": filename,
                "file_content": content,
                "evaluation": risks,
                "score": final_score,
                "task_name": form.cleaned_data.get("task_name", ""),
                "description": form.cleaned_data.get("description", ""),
            },
        )
    else:
        form = UploadCodeForm()
    return render(request, "code_evaluator/code_evaluator.html", {"form": form})


def upload_sql(request):
    if request.method == "POST":
        form = UploadSQLForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["sql_file"]
            content = file.read().decode("utf-8")
            filename = file.name
            file_type = os.path.splitext(filename)[-1].replace(".", "")
            # save_file_to_mongo(filename, content)
            evaluation = call_groq_llm(content, file_type)
            print(f"LLM evaluation result: {evaluation}")
            try:
                risks = json.loads(evaluation)
                final_score = calculate_sql_score(risks)
            except Exception as e:
                risks = []
                final_score = 0.0
                print(f"Error parsing LLM output: {evaluation}{e}")
            AnalysisResult.objects.create(
                filename=filename,
                file_type=file_type,
                description=form.cleaned_data.get("description", ""),
                task_name=form.cleaned_data.get("task_name", ""),
                evaluation=risks,
                score=final_score,
            )
        return render(
            request,
            "analyzer/results.html",
            {
                "filename": filename,
                "file_content": content,
                "evaluation": risks,
                "score": final_score,
                "task_name": form.cleaned_data.get("task_name", ""),
                "description": form.cleaned_data.get("description", ""),
            },
        )
    else:
        form = UploadSQLForm()
    return render(request, "code_evaluator/code_evaluator.html", {"form": form})


def save_file_to_mongo(filename, content):
    mongo_client = pymongo.MongoClient(settings.MONGO_URI)
    mongo_db = mongo_client[settings.MONGO_DB]
    mongo_db.files.insert_one({"filename": filename, "content": content})


def calculate_sql_score(risks: json) -> float:
    try:
        if not isinstance(risks, list):
            print("Invalid risks format, expected a list.")
            return 0.0
        if not all(isinstance(item, dict) for item in risks):
            print("Invalid risks format, expected a list of dictionaries.")
            return 0.0
        if not all("风险分" in item for item in risks):
            print("Invalid risks format, missing '风险分' key in some items.")
            return 0.0
        total_deduction = 0
        for item in risks:
            score = item.get("风险分", 0)
            factor = 1 if score <= 8 else 2
            total_deduction += score * factor
        final_score = max(0, 100 - total_deduction)
        return final_score
    except Exception as e:
        print(f"Error parsing LLM output: {e}")
        return 0.0
