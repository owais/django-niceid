from .apps import NiceIDConfig
from .fields import (
    NiceID,
    NiceIDField,
    NiceIDFormField,
    NiceIDPrimaryKeyField,
)

__all__ = [
    "NiceID",
    "NiceIDConfig",
    "NiceIDField",
    "NiceIDFormField",
    "NiceIDModel",
    "NiceIDPrimaryKeyField",
]


def __getattr__(name: str):
    if name == "NiceIDModel":
        from .models import NiceIDModel

        return NiceIDModel
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
