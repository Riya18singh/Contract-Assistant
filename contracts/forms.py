from django import forms
from .models import Contract


class ContractUploadForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ['title', 'file']
        