from django import forms
from .models import Contract



class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ['recipient_email', 'pdf_file']