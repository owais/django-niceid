import logging

from django.apps import AppConfig
from django.urls import register_converter

from .converter import NiceIDConverter

logger = logging.getLogger(__name__)


class NiceIDConfig(AppConfig):
    default_auto_field = "niceid.fields.NiceIDPrimaryKeyField"
    name = "niceid"

    def ready(self):
        register_converter(NiceIDConverter, "niceid")
        self._register_ninja()
        self._patch_tortoise()

    def _register_ninja(self) -> None:
        try:
            from .ninja import register_ninja_field
        except ImportError:
            logger.debug(
                "django-ninja not installed, skipping Ninja field registration"
            )
            return
        register_ninja_field()

    def _patch_tortoise(self) -> None:
        try:
            from django_tortoise import fields
        except ImportError:
            logger.debug("django-tortoise not installed, skipping Tortoise ORM patch")
            return

        fields.FIELD_MAP["NiceID"] = fields.FIELD_MAP["UUIDField"]
