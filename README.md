# django-admin-select-columns

Dynamically select columns in django admin changelist view with persistence

## Demo

![Demo](https://raw.githubusercontent.com/sandbox-pokhara/django-admin-select-columns/master/demo.gif)

## Installation

You can install the package via pip:

```
pip install django-admin-select-columns
```

Add `django_admin_select_columns` to `INSTALLED_APPS`.

```py
INSTALLED_APPS = [
    ...
    "django_admin_select_columns",
    "django.contrib.admin",
    ...
]
```

The column configuration is stored in the database. Use the migrate command to create the necessary tables.

```
python manage.py migrate
```

## Usage

Simply add `SelectColumnsMixin` to your `ModelAdmin`.

```python
from django.contrib import admin

from django_admin_select_columns.mixins import SelectColumnsMixin
from my_app.models import Person


@admin.register(Person)
class PersonAdmin(SelectColumnsMixin, admin.ModelAdmin):
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

```

## License

This project is licensed under the terms of the MIT license.
