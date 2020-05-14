from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import F
from django.shortcuts import render
from django.http import HttpResponseRedirect

from openfacstrack.apps.track.forms import ConfirmFileForm
from openfacstrack.apps.track.models import (
    Panel,
    ProcessedSample,
    NumericValue,
    Parameter,
    UploadedFile,
    DataProcessing,
    GatingStrategy,
)
import json

from openfacstrack.apps.track.utils import ClinicalSampleFile, PatientFile


def index(request):
    return HttpResponseRedirect("/track/home/")


def home(request):
    return render(request, "track/index.html")


@login_required(login_url="/track/login/")
def upload(request):
    if request.method == "POST":
        file_type = None
        if request.FILES.get("observationsFile"):
            file_type = "observationsFile"
        elif request.FILES.get("patientsFile"):
            file_type = "patientsFile"
        if file_type:
            gating_strategy = GatingStrategy.objects.get_or_create(strategy="manual")[0]
            gating_strategy.save()
            print(f"Gating strategy id = {gating_strategy.id}")
            file_name = request.FILES[file_type].name
            file_contents = request.FILES.get(file_type)
            if file_type == "observationsFile":
                uploaded_file = ClinicalSampleFile(
                    file_name,
                    file_contents,
                    user=request.user,
                    gating_strategy=gating_strategy,
                )
            else:
                uploaded_file = PatientFile(file_name, file_contents, user=request.user)
            validation_errors = uploaded_file.validate()
            if validation_errors:
                validation_report = {
                    "info": [
                        error
                        for error in validation_errors
                        if error.entry_type == "INFO"
                    ],
                    "warn": [
                        error
                        for error in validation_errors
                        if error.entry_type == "WARN"
                    ],
                    "error": [
                        error
                        for error in validation_errors
                        if error.entry_type == "ERROR"
                    ],
                }
            else:
                validation_report = {}
            upload_report = {}
            if not uploaded_file.upload_file.valid_syntax:
                print("Validation errors, aborting upload:")
                print(validation_errors)
            else:
                print("trying upload")
                try:
                    upload_report = uploaded_file.upload(dry_run=True)
                    upload_errors = {
                        "info": [
                            error
                            for error in upload_report["validation"]
                            if error.entry_type == "INFO"
                        ],
                        "warn": [
                            error
                            for error in upload_report["validation"]
                            if error.entry_type == "WARN"
                        ],
                        "error": [
                            error
                            for error in upload_report["validation"]
                            if error.entry_type == "ERROR"
                        ],
                    }
                    upload_report["validation"] = upload_errors
                except Exception as e:
                    print("upload failed")
                    upload_report["status"] = "failed"
            confirm_file_form = ConfirmFileForm(
                initial={"file_id": uploaded_file.upload_file.id}
            )
            return render(
                request,
                "track/upload.html",
                {
                    "uploaded": True,
                    "syntax_report": validation_report,
                    "model_report": upload_report,
                    "form": confirm_file_form,
                },
            )
        elif ConfirmFileForm(request.POST).data.get("file_id"):
            gating_strategy = GatingStrategy.objects.get_or_create(strategy="manual")[0]
            uploaded_file = UploadedFile.objects.get(
                pk=ConfirmFileForm(request.POST).data.get("file_id")
            )
            if uploaded_file.content_type == "PANEL_RESULTS":
                uploaded_file = ClinicalSampleFile(
                    user=request.user,
                    uploaded_file=uploaded_file,
                    gating_strategy=gating_strategy,
                )
            else:
                uploaded_file = PatientFile(
                    user=request.user, uploaded_file=uploaded_file
                )
            uploaded_file.validate()
            uploaded_file.upload()
            return render(request, "track/upload.html", {"upload_status": "success"})
    return render(request, "track/upload.html")


@login_required(login_url="/track/login/")
def panels_view(request):
    panels = Panel.objects.all().order_by("name")
    return render(request, "track/panels.html", {"panels": panels})


@login_required(login_url="/track/login/")
def samples_view(request):
    samples = (
        ProcessedSample.objects.all()
        .annotate(sample_id=F("clinical_sample__covid_patient_id"))
        .values()
    )
    for sample in samples:
        panels_by_sample = DataProcessing.objects.filter(
            processed_sample=sample["id"]
        ).values("panel__name", "created")
        for panel in panels_by_sample:
            sample[panel["panel__name"]] = panel["created"]
    panel_names = [
        panel["name"] for panel in Panel.objects.values("name").order_by("name")
    ]
    table_json = json.dumps(
        list(samples), sort_keys=True, indent=1, cls=DjangoJSONEncoder
    )
    return render(
        request,
        "track/clinical_samples.html",
        {"panels": panel_names, "table_json": table_json},
    )


@login_required(login_url="/track/login/")
def observations_view(request):
    parameters = Parameter.objects.all().order_by("panel__name")
    if request.GET.get("parameter") is None:
        return render(
            request,
            "track/observations.html",
            {"parameters": parameters, "selected": None, "numeric": []},
        )
    else:
        numeric = NumericValue.objects.filter(parameter=request.GET.get("parameter"))
        return render(
            request,
            "track/observations.html",
            {
                "parameters": parameters,
                "selected": Parameter.objects.get(id=request.GET.get("parameter")),
                "numeric": numeric,
            },
        )


def login(request):
    return render(request, "track/login.html")
