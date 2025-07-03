from typing import Any
from typing import Sequence

from django import forms
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.db.models import Model
from django.http import HttpRequest
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path
from django.urls import reverse

from django_admin_select_columns.models import SelectedColumn


class SelectColumnsMixin(ModelAdmin):  # type: ignore
    model: type[Model]  # for fixing pyright type

    def get_list_display(self, request: HttpRequest) -> Sequence[str]:
        model_name = self.model._meta.model_name
        objs = SelectedColumn.objects.filter(
            user=request.user, model=model_name
        ).order_by("id")
        selected = list(objs.values_list("name", flat=True))
        if not selected:
            return super().get_list_display(request)
        return selected

    def get_urls(self):
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        return [
            path(
                "select_columns/",
                self.admin_site.admin_view(self.select_columns_view),
                name=f"{app_label}_{model_name}_select_columns",
            ),
        ] + super().get_urls()

    def select_columns_view(self, request: HttpRequest):
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        selectable_fields = super().get_list_display(request)
        selected_fileds = self.get_list_display(request)

        class ColumnSelectForm(forms.Form):
            def __init__(self, *args: Any, **kwargs: Any):
                super().__init__(*args, **kwargs)
                for field in selectable_fields:
                    self.fields[field] = forms.BooleanField(
                        label=field,
                        required=False,
                        initial=field in selected_fileds,
                    )

            def clean(self):
                cleaned_data = super().clean()
                if not any(cleaned_data.values()):
                    raise forms.ValidationError(
                        "Please select at least one field."
                    )
                return cleaned_data

        if request.method == "POST":
            form = ColumnSelectForm(request.POST)
            if form.is_valid():

                cols = [
                    SelectedColumn(
                        user=request.user, model=model_name, name=name
                    )
                    for name, is_selected in form.cleaned_data.items()
                    if is_selected
                ]
                SelectedColumn.objects.filter(
                    user=request.user, model=model_name
                ).delete()
                SelectedColumn.objects.bulk_create(cols)
                changelist_url = reverse(
                    f"admin:{app_label}_{model_name}_changelist"
                )
                return HttpResponseRedirect(changelist_url)
            else:
                return render(
                    request,
                    "select_columns/select_columns.html",
                    {
                        "site_header": admin.site.site_header,
                        "site_title": admin.site.site_title,
                        "site_title": admin.site.site_title,
                        "title": f"Select columns for {model_name}",
                        "form": form,
                    },
                )
        else:
            form = ColumnSelectForm()

        return render(
            request,
            "select_columns/select_columns.html",
            {
                "site_header": admin.site.site_header,
                "site_title": admin.site.site_title,
                "site_title": admin.site.site_title,
                "title": f"Select columns for {model_name}",
                "form": form,
            },
        )

    def changelist_view(
        self, request: HttpRequest, extra_context: dict[str, Any] | None = None
    ):
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        extra_context = extra_context or {}
        url = reverse(f"admin:{app_label}_{model_name}_select_columns")
        extra_context["url"] = url
        return super().changelist_view(request, extra_context=extra_context)
