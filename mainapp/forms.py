from django import forms
from mainapp.models import Patient, Disease, FileStorage


class PatientForm(forms.ModelForm):

    class Meta:
        model = Patient
        exclude = ('is_active',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = "form-control-patient"

    diseases = forms.ModelChoiceField(
        queryset=Disease.objects.all(),
        widget=forms.RadioSelect,
        required=False
    )

    def clean_diseases(self):
        data = self.cleaned_data['diseases']
        if not data:
            raise forms.ValidationError('Please select disease!')
        return data


class FileStorageForm(forms.ModelForm):

    class Meta:
        model = FileStorage
        fields = ('file',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = "form-control-file"

    def clean_file(self):
        data = self.cleaned_data['file']
        format = str(data).split('.')[-1]
        if format not in ['xlsx', 'xltx', 'xls', 'xlt', 'csv', 'pdf', 'odt', 'docx']:
            raise forms.ValidationError('This file format is not supported!')
        return data
