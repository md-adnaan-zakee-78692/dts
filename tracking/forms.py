from django import forms
from .models import Document

class DocumentCreateForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'content']

class DocumentActionForm(forms.Form):
    action = forms.ChoiceField(choices=[('APPROVE', 'Approve'), ('REJECT', 'Reject')])
    comment = forms.CharField(widget=forms.Textarea, required=False)
