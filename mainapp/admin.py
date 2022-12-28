from django.contrib import admin
from mainapp.models import Disease, AnalysisItem, Patient, FileStorage, AnalysisResultItem

admin.site.register(Disease)
admin.site.register(AnalysisItem)
admin.site.register(Patient)
admin.site.register(FileStorage)
admin.site.register(AnalysisResultItem)
