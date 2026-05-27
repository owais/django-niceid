from django.db import models

from .fields import NiceIDPrimaryKeyField


class NiceIDModel(models.Model):
    # namespace attribute must be set by the model that inherits from this class
    # namespace: str = ""

    id = NiceIDPrimaryKeyField()

    class Meta:
        abstract = True
