from django.shortcuts import render
from mainapp.forms import PatientForm, FileStorageForm
from mainapp.models import Patient, Disease, AnalysisResultItem, AnalysisItem
from django.http import JsonResponse


from mainapp.parsers.main import get_file_data


def show_required_analyzes(request, pk):
    """Upload data with the required analyses depending on the disease."""

    if request.is_ajax() and pk:
        required_analyzes = Disease.objects.get(pk=pk).analyzes.all()
        an = [req.parameter for req in required_analyzes]
        return JsonResponse({'required_analyzes': an})


def load_data(request):
    """View of a page with forms."""

    is_success = False
    title = 'load data'
    all_patients = Patient.objects.all()

    if request.method == 'POST':

        # new patient, load data through the file
        if request.POST.get('new-patient', False) and request.POST.get('load-file', False):
            patient_form = PatientForm(request.POST)
            file_form = FileStorageForm(request.POST, request.FILES)
            if patient_form.is_valid() and file_form.is_valid():
                new_patient, patient_diseases = create_new_patient(patient_form, request)

                if request.FILES.get('file'):
                    save_analyzes_result(file_form, new_patient, request)
                    is_success = True

        # patient is exists, load data through the file
        elif not request.POST.get('new-patient', False) and request.POST.get('load-file', False):
            patient_form = PatientForm(request.POST)
            file_form = FileStorageForm(request.POST, request.FILES)
            patient = Patient.objects.get(pk=request.POST['patients'])
            if patient_form.is_valid() and file_form.is_valid():
                patient_diseases = Disease.objects.get(pk=request.POST['diseases'])
                patient.save()
                patient.diseases.set((patient_diseases,))

                if request.FILES.get('file'):
                    save_analyzes_result(file_form, patient, request)
                    is_success = True

        # new patient, load data through form's fields
        elif request.POST.get('new-patient', False) and not request.POST.get('load-file', False):
            patient_form = PatientForm(request.POST)
            if patient_form.is_valid():
                new_patient, patient_diseases = create_new_patient(patient_form, request)

                required_analyzes = patient_diseases.analyzes.all()
                for analysis_obj in required_analyzes:
                    parameter = analysis_obj.parameter.replace(' ', '-')
                    value = request.POST.get(parameter)
                    AnalysisResultItem.objects.create(
                        patient=new_patient,
                        parameter=analysis_obj,
                        value=value
                    )
                is_success = True
            file_form = None

        # patient is exists, load data through form's fields
        else:
            patient_form = PatientForm(request.POST)
            patient = Patient.objects.get(pk=request.POST['patients'])
            if patient_form.is_valid():
                patient_diseases = Disease.objects.get(pk=request.POST['diseases'])
                patient.diseases.set((patient_diseases,))

                required_analyzes = patient_diseases.analyzes.all()

                for analysis_obj in required_analyzes:
                    parameter = analysis_obj.parameter.replace(' ', '-')
                    value = request.POST.get(parameter)
                    AnalysisResultItem.objects.create(
                        patient=patient,
                        parameter=analysis_obj,
                        value=value
                    )
                is_success = True
            file_form = None

    else:
        file_form = FileStorageForm()
        patient_form = PatientForm()
    content = {
        'title': title,
        'file_form': file_form,
        'patient_form': patient_form,
        'all_patients': all_patients,
        'is_success': is_success,
    }
    return render(request, 'mainapp/load_data.html', content)


def save_analyzes_result(file_form, patient_obj, request):
    """Save the data of the analysis results read from files."""

    new_file_obj = file_form.save(commit=False)
    new_file_obj.patient = patient_obj
    new_file_obj.save()

    file_data = get_file_data(request.FILES['file'].name)
    patient_obj.language = file_data['language']
    patient_obj.save()
    for data in file_data['analyzes']:
        analysis_obj, created = AnalysisItem.objects.get_or_create(
            parameter__iexact=data['parameter'],
            defaults={
                'parameter': data['parameter'],
                'reference_value_min': data['reference_values'][0],
                'reference_value_max': data['reference_values'][1],
                'unit_of_measure': data['units']
            })
        AnalysisResultItem.objects.create(
            patient=patient_obj,
            file=new_file_obj,
            parameter=analysis_obj,
            value=data['value'],
            comment=data['comment']
        )


def create_new_patient(patient_form, request):
    """Get the objects of a new patient and his illness."""

    patient_diseases = Disease.objects.get(pk=request.POST['diseases'])
    new_patient = patient_form.save(commit=False)
    new_patient.save()
    new_patient.diseases.set((patient_diseases,))
    return new_patient, patient_diseases
