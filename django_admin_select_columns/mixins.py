from typing import Any

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

    def get_list_display(self, request: HttpRequest):
        objs = SelectedColumn.objects.filter(
            user=request.user, model=self.model.__name__
        ).order_by("id")
        selected = list(objs.values_list("name", flat=True))
        if not selected:
            return super().get_list_display(request)
        return selected

    def get_urls(self):
        return [
            path(
                "select_columns/",
                self.admin_site.admin_view(self.select_columns_view),
                name="select_columns",
            ),
        ] + super().get_urls()

    def select_columns_view(self, request: HttpRequest):

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
                        user=request.user, model=self.model.__name__, name=name
                    )
                    for name, is_selected in form.cleaned_data.items()
                    if is_selected
                ]
                SelectedColumn.objects.filter(
                    user=request.user, model=self.model.__name__
                ).delete()
                SelectedColumn.objects.bulk_create(cols)
                changelist_url = reverse(
                    f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_changelist"
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
                        "title": f"Select columns for {self.model.__name__}",
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
                "title": f"Select columns for {self.model.__name__}",
                "form": form,
            },
        )

    def changelist_view(
        self, request: HttpRequest, extra_context: dict[str, Any] | None = None
    ):
        extra_context = extra_context or {}
        url = reverse("admin:select_columns")
        extra_context["url"] = url
        return super().changelist_view(request, extra_context=extra_context)
