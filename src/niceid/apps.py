from django.apps import AppConfig
from django.urls import register_converter
from ninja.orm import register_field

from project.logging import get_logger

from .converter import NiceIDConverter
from .fields import NiceID

logger = get_logger()


class NiceIDConfig(AppConfig):
    default_auto_field = "niceid.fields.NiceIDPrimaryKeyField"
    name = "niceid"

    def ready(self):
        register_converter(NiceIDConverter, "niceid")
        register_field("NiceID", NiceID)
        try:
            self._patch_tortoise()
        except ImportError:
            logger.warning("django_tortoise not installed, skipping patch")

    def _patch_tortoise(self):
        from django_tortoise import fields

        fields.FIELD_MAP["NiceID"] = fields.FIELD_MAP["UUIDField"]
