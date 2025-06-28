from django import forms

class UploadFileForm(forms.Form):
    code_files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    sql_files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)
