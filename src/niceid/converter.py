from django.urls.converters import StringConverter

from .fields import NiceID
from .validators import ENCODED_LENGTH, NAMESPACE_MAX_LENGTH, NAMESPACE_MIN_LENGTH

NICEID_URL_REGEX = (
    rf"[a-z_]{{{NAMESPACE_MIN_LENGTH},{NAMESPACE_MAX_LENGTH}}}"
    rf"_[0-9A-HJKMNP-TV-Z]{{{ENCODED_LENGTH}}}"
)


class NiceIDConverter(StringConverter):
    regex = NICEID_URL_REGEX

    def to_python(self, value):
        return NiceID.from_string(value)

    def to_url(self, value):
        return str(value)
