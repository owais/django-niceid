from rest_framework import serializers, fields
from rest_framework.relations import PrimaryKeyRelatedField

from .fields import NiceID


class NiceIDSerializerFieldMixin:
    def to_internal_value(self, data):
        try:
            return NiceID.from_string(data)
        except (AttributeError, ValueError):
            raise serializers.ValidationError(f"{data} is not a valid NiceID.")

    def to_representation(self, value):
        return str(value)


class NiceIDSerializerField(NiceIDSerializerFieldMixin, fields.Field):
    pass


class NiceIDRelatedField(NiceIDSerializerFieldMixin, PrimaryKeyRelatedField):
    pass
