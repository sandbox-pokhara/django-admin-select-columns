from django.contrib import admin

from django_admin_select_columns.mixins import SelectColumnsMixin
from my_app.models import Person


@admin.register(Person)
class PersonAdmin(SelectColumnsMixin, admin.ModelAdmin):  # type: ignore
    list_display = (
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "gender",
        "birthdate",
        "is_active",
    )
    list_filter = ("gender", "is_active")
    search_fields = ("first_name", "last_name", "email", "phone_number")
