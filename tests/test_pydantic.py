import pytest

pydantic = pytest.importorskip("pydantic")

from niceid.fields import NiceID


@pytest.mark.pydantic
class TestPydantic:
    def test_validate_from_string(self):
        class Model(pydantic.BaseModel):
            id: NiceID

        nid = NiceID("user")
        model = Model(id=str(nid))
        assert model.id == nid

    def test_json_schema_type_is_string(self):
        schema = NiceID.__get_pydantic_json_schema__({}, lambda x: x)
        assert schema["type"] == "string"
