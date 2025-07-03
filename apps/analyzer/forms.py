from django import forms


class UploadCodeForm(forms.Form):
    code_file = forms.FileField(required=True)
    task_name = forms.CharField(max_length=255, required=True)
    description = forms.CharField(widget=forms.Textarea, required=False)


class UploadProjectForm(forms.Form):
    code_files = forms.FileField(required=True)
    task_name = forms.CharField(max_length=255, required=True)
    description = forms.CharField(widget=forms.Textarea, required=False)


class UploadSQLForm(forms.Form):
    sql_file = forms.FileField(required=True)
    task_name = forms.CharField(max_length=255, required=True)
    description = forms.CharField(widget=forms.Textarea, required=False)
