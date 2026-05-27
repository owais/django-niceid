import os

import pytest

pytestmark = pytest.mark.postgres

pytest.importorskip("psycopg")

requires_postgres = pytest.mark.skipif(
    not os.environ.get("POSTGRES_HOST"),
    reason="POSTGRES_HOST not set",
)


@requires_postgres
@pytest.mark.django_db
class TestPostgresIntegration:
    def test_create_item(self):
        from testproj.testapp.models import Item

        item = Item.objects.create()
        assert item.id.namespace == "item"
        item.refresh_from_db()
        assert item.id.namespace == "item"
