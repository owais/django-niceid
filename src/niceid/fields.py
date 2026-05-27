import uuid
from functools import total_ordering
from typing import Any

import base32_crockford
from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


@total_ordering
class NiceID:
    uuid: uuid.UUID

    def __init__(self, namespace: str, int: int | None = None):
        self.namespace = namespace
        if not int:
            self.uuid = uuid.uuid7()
        else:
            self.uuid = uuid.UUID(int=int)
        self._encoded = base32_crockford.encode(self.uuid.int)

    @property
    def string(self) -> str:
        return f"{self.namespace}_{self._encoded}"

    @classmethod
    def from_string(cls, value: str) -> "NiceID":
        if "_" not in value:
            raise ValueError("Invalid NiceID format")

        namespace, num = value.rsplit("_", 1)
        int = base32_crockford.decode(num)
        return cls(namespace=namespace, int=int)

    @classmethod
    def from_uuid(cls, namespace: str, value: uuid.UUID) -> "NiceID":
        return cls(namespace=namespace, int=value.int)

    def __str__(self):
        return self.string

    def __repr__(self):
        return f"NiceID('{self.namespace}_{self._encoded}')"

    def __int__(self) -> int:
        return self.uuid.int

    def __bytes__(self) -> bytes:
        return self.uuid.bytes

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, NiceID):
            return self.uuid < other.uuid
        if isinstance(other, uuid.UUID):
            return self.uuid < other
        return NotImplemented

    def __eq__(self, other: object) -> bool:
        if isinstance(other, NiceID):
            return self.uuid == other.uuid
        if isinstance(other, uuid.UUID):
            return self.uuid == other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.uuid.bytes)

    def get_schema_type(self):
        return NiceID

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        return {
            "type": "NiceID",
            "examples": ["user_1KGGWGM8FEABRJA533GJKYW0B"],
            "description": "NiceID string representation",
        }

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        def validate_from_string(value: str) -> "NiceID":
            return cls.from_string(value)

        # 1. Logic for when the input is already a NiceID instance
        instance_schema = core_schema.is_instance_schema(cls)

        # 2. Logic for when the input is a string (e.g. from JSON)
        # We chain a string schema with our custom from_string parser
        from_string_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(validate_from_string),
            ]
        )

        return core_schema.json_or_python_schema(
            # How to handle raw Python objects (NiceID or str)
            python_schema=core_schema.union_schema(
                [
                    instance_schema,
                    from_string_schema,
                ]
            ),
            # How to handle JSON input (always starts as str)
            json_schema=from_string_schema,
            # How to serialize back to a string
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: instance.string, when_used="json-unless-none"
            ),
        )


class NiceIDField(models.Field):
    namespace: str

    def __init__(self, verbose_name=None, **kwargs):
        kwargs.setdefault("max_length", 26)
        super().__init__(verbose_name, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        return name, path, args, kwargs

    def db_type(self, connection):
        return "UUID"

    def get_internal_type(self):
        return "NiceID"

    def get_db_prep_value(self, value, connection, prepared=False):
        if not connection.features.has_native_uuid_field:
            raise ValueError(
                "NiceIDField needs native UUID field support in the database"
            )

        value = self.to_python(value)
        if not value:
            return None
        return value.uuid

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def to_python(self, value) -> NiceID | None:
        if not value:
            return None
        if isinstance(value, int):
            return NiceID(namespace=self.namespace, int=value)
        if isinstance(value, NiceID):
            return value
        if isinstance(value, uuid.UUID):
            return NiceID.from_uuid(self.namespace, value)
        if isinstance(value, str):
            ns = self.namespace
            if "_" in value:
                ns, value = value.rsplit("_", 1)
            return NiceID.from_string(ns + "_" + value)
        raise ValidationError(
            _("'%(value)s' is not a valid NiceID."),
            code="invalid",
            params={"value": value},
        )


class UUID7(models.Func):
    function = "uuidv7"
    output_field = NiceIDField()


class NiceIDPrimaryKeyField(NiceIDField):
    def __init__(self, *args, namespace: str = "", **kwargs):
        self.namespace = namespace
        # kwargs["default"] = NoneNiceID
        kwargs.pop("default", None)
        kwargs["editable"] = False
        kwargs["primary_key"] = True
        kwargs.setdefault("db_default", UUID7())
        super().__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name, private_only=False):
        super().contribute_to_class(cls, name, private_only)

        # skip during migrations
        if cls.__module__ == "__fake__":
            return

        if cls._meta.abstract:
            return

        self.namespace = getattr(cls, "namespace", "")

        if not self.namespace:
            raise ValueError(
                f"model {cls.__module__}.{cls.__name__} does not specify a namespace attribute on the class"
            )
        if not (2 <= len(self.namespace) <= 16):
            raise ValueError(
                f"NiceIDField namespace must be 2-16 characters long, got {self.namespace} (length: {len(self.namespace)})"
            )

    def to_python(self, value):
        if (niceid := super().to_python(value)) is None:
            return None

        if niceid.namespace != self.namespace:
            raise ValidationError(
                f"'{value}' namespace does not match the field namespace ({self.namespace}).",
            )
        return niceid


class NiceIDFormField(forms.CharField):
    def prepare_value(self, value):
        return NiceID.from_string(value) if value is not None else None

    def to_python(self, value):
        value = super().to_python(value)

        if value in self.empty_values:
            return None
        try:
            return NiceID.from_string(value)
        except (AttributeError, ValueError):
            raise ValidationError(_("Enter a valid ULID."), code="invalid")
