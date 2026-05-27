from niceid.models import NiceIDModel


class Item(NiceIDModel):
    namespace = "item"

    class Meta:
        app_label = "testapp"
