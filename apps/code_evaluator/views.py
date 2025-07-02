from django.shortcuts import render


def index(request):
    return render(request, "code_evaluator/index.html", {"active_page": "index"})


def sql_analyzer(request):
    return render(request, "code_evaluator/sql_evaluator.html", {"active_page": "sql"})


def code_analyzer(request):
    return render(
        request, "code_evaluator/code_evaluator.html", {"active_page": "code"}
    )
