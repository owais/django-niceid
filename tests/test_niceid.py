import pickle
import uuid
from copy import deepcopy

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

    def test_deepcopy_instance(self):
        original = NiceID.from_string("support_message_1KT25CN7TFQDV7STJ2NQJVS7S")
        copied = deepcopy(original)
        assert copied == original
        assert copied is not original
        assert copied.namespace == original.namespace
        assert copied.uuid == original.uuid

    def test_deepcopy_in_dict(self):
        original = NiceID.from_string("support_message_1KT25CN7TFQDV7STJ2NQJVS7S")
        copied = deepcopy({"message_id": original})
        assert isinstance(copied["message_id"], NiceID)
        assert copied["message_id"] == original
        assert copied["message_id"].namespace == "support_message"

    def test_deepcopy_namespace_with_underscores(self):
        for value in (
            "support_message_1KT25CN7TFQDV7STJ2NQJVS7S",
            "ai_session_event_1KGGWGM8FEABRJA533GJKYW0B",
        ):
            original = NiceID.from_string(value)
            copied = deepcopy(original)
            assert copied == original
            assert copied.namespace == original.namespace

    def test_pickle_round_trip(self):
        original = NiceID.from_string("support_message_1KT25CN7TFQDV7STJ2NQJVS7S")
        restored = pickle.loads(pickle.dumps(original))
        assert restored == original
        assert restored.namespace == original.namespace
        assert restored.uuid == original.uuid
