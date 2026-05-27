from rest_framework import fields, serializers
from rest_framework.relations import PrimaryKeyRelatedField

from .fields import NiceID


class NiceIDSerializerFieldMixin:
    def to_internal_value(self, data):
        try:
            return NiceID.from_string(data)
        except (AttributeError, ValueError) as exc:
            raise serializers.ValidationError(f"{data} is not a valid NiceID.") from exc

    def to_representation(self, value):
        return str(value)


class NiceIDSerializerField(NiceIDSerializerFieldMixin, fields.Field):
    pass


class NiceIDRelatedField(PrimaryKeyRelatedField):
    def to_internal_value(self, data):
        try:
            niceid = NiceID.from_string(data)
        except (AttributeError, ValueError) as exc:
            raise serializers.ValidationError(f"{data} is not a valid NiceID.") from exc
        return super().to_internal_value(niceid.uuid)

    def to_representation(self, value):
        if hasattr(value, "id") and value.id is not None:
            return str(value.id)
        return str(value)
