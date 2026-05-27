from niceid.converter import NiceIDConverter
from niceid.fields import NiceID


class TestNiceIDConverter:
    def setup_method(self):
        self.converter = NiceIDConverter()

    def test_round_trip(self):
        nid = NiceID("user")
        url_value = self.converter.to_url(nid)
        assert self.converter.to_python(url_value) == nid
