from django.urls.converters import StringConverter

from .fields import NiceID


class NiceIDConverter(StringConverter):
    regex = r"[a-z_]{2,12}_[A-Za-z0-9]{25}"

    def to_python(self, value):
        return NiceID.from_string(value)

    def to_url(self, value):
        return str(value)
