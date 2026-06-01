import uuid
from typing import Any

import base32_crockford
from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from .validators import validate_encoded_part, validate_namespace


class NiceID(str):
    """A human-readable, URL-safe identifier backed by a UUIDv7.

    Subclasses str so it serializes, compares, and hashes as a plain string
    everywhere — JSON encoding, dict keys, template rendering — with no
    special-casing required by callers.
    """

    namespace: str
    uuid: uuid.UUID

    def __new__(cls, namespace: str, int: int | None = None) -> NiceID:
        validate_namespace(namespace)
        _uuid = uuid.UUID(int=int) if int is not None else uuid.uuid7()
        _encoded = base32_crockford.encode(_uuid.int)
        validate_encoded_part(_encoded)
        instance = super().__new__(cls, f"{namespace}_{_encoded}")
        instance.namespace = namespace
        instance.uuid = _uuid
        instance._encoded = _encoded
        return instance

    @property
    def string(self) -> str:
        return str(self)

    @classmethod
    def from_string(cls, value: str) -> NiceID:
        if "_" not in value:
            raise ValueError("Invalid NiceID format")
        namespace, encoded = value.rsplit("_", 1)
        validate_namespace(namespace)
        validate_encoded_part(encoded)
        return cls(namespace=namespace, int=base32_crockford.decode(encoded))

    @classmethod
    def from_uuid(cls, namespace: str, value: uuid.UUID) -> NiceID:
        return cls(namespace=namespace, int=value.int)

    def __repr__(self) -> str:
        return f"NiceID('{self}')"

    def __deepcopy__(self, memo: dict[int, Any]) -> NiceID:
        return self.__class__.from_string(str(self))

    def __reduce_ex__(self, protocol: int) -> tuple[Any, tuple[str]]:
        return (self.__class__.from_string, (str(self),))

    def __int__(self) -> int:
        return self.uuid.int

    def __bytes__(self) -> bytes:
        return self.uuid.bytes

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        return {
            "type": "string",
            "pattern": r"^[a-z_]{2,16}_[0-9A-HJKMNP-TV-Z]+$",
            "examples": ["user_1KGGWGM8FEABRJA533GJKYW0B"],
            "description": "NiceID string representation",
        }

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any) -> Any:
        from pydantic_core import core_schema

        def validate_from_string(value: str) -> NiceID:
            return cls.from_string(value)

        instance_schema = core_schema.is_instance_schema(cls)

        from_string_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(validate_from_string),
            ]
        )

        return core_schema.json_or_python_schema(
            python_schema=core_schema.union_schema(
                [
                    instance_schema,
                    from_string_schema,
                ]
            ),
            json_schema=from_string_schema,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: instance.string, when_used="json-unless-none"
            ),
        )


class NiceIDField(models.Field):
    namespace: str = ""

    def __init__(self, *args, namespace: str = "", **kwargs):
        self.namespace = namespace
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.namespace:
            kwargs["namespace"] = self.namespace
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
            if not self.namespace:
                raise ValidationError(
                    _("NiceIDField requires a namespace for integer values."),
                    code="invalid",
                )
            return NiceID(namespace=self.namespace, int=value)
        if isinstance(value, NiceID):
            return value
        if isinstance(value, uuid.UUID):
            if not self.namespace:
                raise ValidationError(
                    _("NiceIDField requires a namespace for UUID values."),
                    code="invalid",
                )
            return NiceID.from_uuid(self.namespace, value)
        if isinstance(value, str):
            ns = self.namespace
            if "_" in value:
                ns, value = value.rsplit("_", 1)
            if not ns:
                raise ValidationError(
                    _("'%(value)s' is not a valid NiceID."),
                    code="invalid",
                    params={"value": value},
                )
            return NiceID.from_string(f"{ns}_{value}")
        raise ValidationError(
            _("'%(value)s' is not a valid NiceID."),
            code="invalid",
            params={"value": value},
        )


class UUID7(models.Func):
    function = "uuidv7"
    output_field = models.UUIDField()


class NiceIDPrimaryKeyField(NiceIDField):
    def __init__(self, *args, namespace: str = "", **kwargs):
        self.namespace = namespace
        kwargs.pop("default", None)
        kwargs["editable"] = False
        kwargs["primary_key"] = True
        kwargs.setdefault("db_default", UUID7())
        super().__init__(*args, namespace=namespace, **kwargs)

    def contribute_to_class(self, cls, name, private_only=False):
        super().contribute_to_class(cls, name, private_only)

        if cls.__module__ == "__fake__":
            return

        if cls._meta.abstract:
            return

        self.namespace = getattr(cls, "namespace", "")

        if not self.namespace:
            raise ValueError(
                f"model {cls.__module__}.{cls.__name__} does not specify a "
                "namespace attribute on the class"
            )
        validate_namespace(self.namespace)

    def to_python(self, value):
        if (niceid := super().to_python(value)) is None:
            return None

        if niceid.namespace != self.namespace:
            raise ValidationError(
                f"'{value}' namespace does not match the field namespace "
                f"({self.namespace}).",
            )
        return niceid


class NiceIDFormField(forms.CharField):
    def prepare_value(self, value):
        if value is None:
            return None
        if isinstance(value, NiceID):
            return str(value)
        return value

    def to_python(self, value):
        value = super().to_python(value)

        if value in self.empty_values:
            return None
        try:
            return NiceID.from_string(value)
        except (AttributeError, ValueError) as exc:
            raise ValidationError(_("Enter a valid NiceID."), code="invalid") from exc
