import re

import base32_crockford

NAMESPACE_PATTERN = re.compile(r"^[a-z_]{2,16}$")
ENCODED_PART_CHARSET = re.compile(r"^[0-9A-HJKMNP-TV-Z]+$")

NAMESPACE_MIN_LENGTH = 2
NAMESPACE_MAX_LENGTH = 16
ENCODED_LENGTH = 25


def validate_namespace(namespace: str) -> None:
    if not NAMESPACE_PATTERN.fullmatch(namespace):
        raise ValueError(
            f"Invalid namespace {namespace!r}: must be {NAMESPACE_MIN_LENGTH}-"
            f"{NAMESPACE_MAX_LENGTH} lowercase letters or underscores"
        )


def validate_encoded_part(encoded: str) -> None:
    if not ENCODED_PART_CHARSET.fullmatch(encoded):
        raise ValueError(
            f"Invalid NiceID encoded part {encoded!r}: invalid Crockford base32"
        )
    try:
        base32_crockford.decode(encoded)
    except Exception as exc:
        raise ValueError(
            f"Invalid NiceID encoded part {encoded!r}: not decodable"
        ) from exc
