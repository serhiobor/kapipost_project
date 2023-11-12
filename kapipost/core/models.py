from django.db import models


class CreatedModel(models.Model):
    """Abstract model that add creation date."""
    created = models.DateTimeField(
        'Creation date',
        auto_now_add=True
    )

    class Meta:
        abstract = True
