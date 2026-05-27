import uuid

import pytest
from django.core.exceptions import ValidationError

from niceid.fields import NiceID, NiceIDField, NiceIDPrimaryKeyField
from testproj.testapp.models import Item


class TestNiceIDField:
    def test_to_python_from_uuid(self):
        field = NiceIDField(namespace="user")
        u = uuid.uuid7()
        nid = field.to_python(u)
        assert isinstance(nid, NiceID)
        assert nid.namespace == "user"
        assert nid.uuid == u

    def test_to_python_from_string(self):
        field = NiceIDField(namespace="user")
        original = NiceID("user")
        nid = field.to_python(str(original))
        assert nid == original

    def test_namespace_mismatch_on_pk_field(self):
        field = NiceIDPrimaryKeyField(namespace="user")
        other = NiceID("org")
        with pytest.raises(ValidationError, match="namespace does not match"):
            field.to_python(str(other))


class TestNiceIDModel:
    def test_item_requires_namespace(self):
        assert Item.namespace == "item"

    def test_pk_field_namespace(self):
        field = Item._meta.get_field("id")
        assert field.namespace == "item"
