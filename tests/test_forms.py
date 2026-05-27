from niceid.fields import NiceID, NiceIDFormField


class TestNiceIDFormField:
    def test_prepare_value_returns_string(self):
        field = NiceIDFormField()
        nid = NiceID("user")
        assert field.prepare_value(nid) == str(nid)

    def test_to_python_parses_string(self):
        field = NiceIDFormField()
        nid = NiceID("user")
        parsed = field.to_python(str(nid))
        assert parsed == nid
