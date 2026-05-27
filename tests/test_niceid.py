import uuid

import pytest

from niceid.fields import NiceID


class TestNiceID:
    def test_generate_has_namespace_and_encoded_part(self):
        nid = NiceID("user")
        assert nid.namespace == "user"
        assert nid.string.startswith("user_")
        assert len(nid.string.split("_", 1)[1]) == 25

    def test_round_trip(self):
        original = NiceID("user")
        restored = NiceID.from_string(str(original))
        assert restored == original
        assert restored.uuid == original.uuid

    def test_from_uuid(self):
        u = uuid.uuid7()
        nid = NiceID.from_uuid("org", u)
        assert nid.uuid == u
        assert nid.namespace == "org"

    def test_int_zero(self):
        nid = NiceID("user", int=0)
        assert int(nid) == 0
        assert nid.uuid == uuid.UUID(int=0)
        assert NiceID.from_string(str(nid)) == nid

    def test_ordering(self):
        a = NiceID("user", int=1)
        b = NiceID("user", int=2)
        assert a < b

    def test_hashable_in_set(self):
        a = NiceID("user")
        b = NiceID.from_string(str(a))
        assert {a, b} == {a}

    def test_invalid_format(self):
        with pytest.raises(ValueError, match="Invalid NiceID format"):
            NiceID.from_string("nounderscore")

    def test_invalid_namespace(self):
        with pytest.raises(ValueError, match="Invalid namespace"):
            NiceID.from_string("X_1KGGWGM8FEABRJA533GJKYW0B")

    def test_namespace_too_short(self):
        with pytest.raises(ValueError, match="Invalid namespace"):
            NiceID("x")
