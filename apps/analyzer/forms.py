from django import forms

class UploadFileForm(forms.Form):
    code_files = forms.FileField(
        widget=forms.ClearableFileInput(),
        required=False
    )
    sql_files = forms.FileField(
        widget=forms.ClearableFileInput(),
        required=False
    )