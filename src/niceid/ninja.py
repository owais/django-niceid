from ninja.orm import register_field

from .fields import NiceID


def register_ninja_field() -> None:
    register_field("NiceID", NiceID)
