from django.db import models
import pytz
import django.conf


class ParameterField(models.CharField):
    def __init__(self, *args, **kwargs):
        super(ParameterField, self).__init__(*args, **kwargs)

    def get_prep_value(self, value):
        return str(value).lower().strip()


class AnalysisItem(models.Model):
    parameter = ParameterField(max_length=128, unique=True)
    reference_value_min = models.CharField(max_length=8, verbose_name='reference value min', default=0, blank=True, null=True)
    reference_value_max = models.CharField(max_length=8, verbose_name='reference value max', blank=True)
    unit_of_measure = models.CharField(max_length=32, verbose_name='unit of measure', blank=True)

    class Meta:
        verbose_name = 'analysis'
        verbose_name_plural = 'analyzes'
        ordering = ['parameter']

    def __str__(self):
        return self.parameter


class Disease(models.Model):
    analyzes = models.ManyToManyField(AnalysisItem, related_name='analyzes_disease')
    disease = models.TextField(max_length=256, unique=True)

    class Meta:
        verbose_name = 'disease'
        verbose_name_plural = 'diseases'

    def __str__(self):
        return self.disease


class Patient(models.Model):
    COUNTRIES = list(pytz.country_names.items())
    COUNTRIES.insert(0, (None, 'Select a country'))

    LANGUAGES = list(django.conf.settings.LANGUAGES)
    LANGUAGES.insert(0, (None, 'Select a language'))

    diseases = models.ManyToManyField(Disease, related_name='disease_patient')
    first_name = models.CharField(max_length=64, verbose_name='first name', blank=True)
    last_name = models.CharField(max_length=64, verbose_name='last name', blank=True)
    country = models.CharField(max_length=32, choices=COUNTRIES, default='US')
    language = models.CharField(max_length=32, choices=LANGUAGES, default='en')
    age = models.PositiveSmallIntegerField(default=18)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'patient'
        verbose_name_plural = 'patients'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class FileStorage(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, blank=True, null=True)
    file = models.FileField(upload_to='patient_files', blank=True)


class AnalysisResultItem(models.Model):
    file = models.ForeignKey(FileStorage, on_delete=models.CASCADE, blank=True, null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    parameter = models.ForeignKey(AnalysisItem, on_delete=models.CASCADE)
    value = models.CharField(max_length=8)
    comment = models.TextField(max_length=512, blank=True, null=True)
