from unittest.mock import Mock

import pytest

pytest.importorskip("rest_framework")

from niceid.drf import NiceIDRelatedField, NiceIDSerializerField
from niceid.fields import NiceID
from testproj.testapp.models import Item


@pytest.mark.drf
class TestDRF:
    def test_serializer_field_round_trip(self):
        field = NiceIDSerializerField()
        nid = NiceID("item")
        internal = field.to_internal_value(str(nid))
        assert internal == nid
        assert field.to_representation(nid) == str(nid)

    def test_related_field_uses_queryset(self):
        item = Item(id=NiceID("item"))
        qs = Mock()
        qs.get.return_value = item
        field = NiceIDRelatedField(queryset=qs)
        result = field.to_internal_value(str(item.id))
        assert result == item
        qs.get.assert_called_once_with(pk=item.id.uuid)
