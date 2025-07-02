from django.contrib.auth import get_user_model
from django.db import models


class SelectedColumn(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="selected_columns",
    )
    model = models.CharField(max_length=128)
    name = models.CharField(max_length=128)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "model", "name"],
                name="unique_selected_column",
            )
        ]
