from itertools import zip_longest

from django.core.exceptions import ValidationError
from django.forms import MultiValueField, TextInput


class MultiTextInput(TextInput):
    template_name = "django/forms/widgets/multiwidget.html"

    def value_from_datadict(self, data, files, name):
        try:
            getter = data.getlist
        except AttributeError:
            getter = data.get
        return getter(name)

    def format_value(self, value):
        return [] if value is None else value


class MultiTextField(MultiValueField):
    def compress(self, data_list):
        return data_list

    def has_changed(self, initial, data):
        if self.disabled:
            return False
        if initial is None:
            initial = ["" for x in range(0, len(data))]
        else:
            if not isinstance(initial, list):
                initial = self.widget.decompress(initial)
        for field, initial, data in zip_longest(
            self.fields, initial, data, fillvalue=None
        ):
            if initial is None or data is None:
                return True

            try:
                initial_val = field.to_python(initial)
            except ValidationError:
                return True
            if field.has_changed(initial_val, data):
                return True
        return False
