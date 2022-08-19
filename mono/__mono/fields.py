from django import forms
from django.core import exceptions, validators
from django.db import models
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _


def get_max_length(choices, max_length, default=200):
    if max_length is None:
        if choices:
            return len(",".join([str(key) for key, label in choices]))
        return default
    return max_length


class MultiSelectFormField(forms.MultipleChoiceField):
    widget = forms.CheckboxSelectMultiple

    def __init__(self, *args, **kwargs):
        self.min_choices = kwargs.pop("min_choices", None)
        self.max_choices = kwargs.pop("max_choices", None)
        self.max_length = kwargs.pop("max_length", None)
        super().__init__(*args, **kwargs)
        self.max_length = get_max_length(self.choices, self.max_length)
        self.validators.append(MaxValueMultiFieldValidator(self.max_length))
        if self.max_choices is not None:
            self.validators.append(MaxChoicesValidator(self.max_choices))
        if self.min_choices is not None:
            self.validators.append(MinChoicesValidator(self.min_choices))


class MaxValueMultiFieldValidator(validators.MaxLengthValidator):
    code = "max_multifield_value"

    def clean(self, x):
        return len(",".join(x))


class MinChoicesValidator(validators.MinLengthValidator):
    message = _("You must select a minimum of  %(limit_value)d choices.")
    code = "min_choices"


class MaxChoicesValidator(validators.MaxLengthValidator):
    message = _("You must select a maximum of  %(limit_value)d choices.")
    code = "max_choices"


class MSFList(list):
    def __init__(self, choices, *args, **kwargs):
        self.choices = choices
        super().__init__(*args, **kwargs)

    def __str__(self):
        msg_list = [
            self.choices.get(int(i)) if i.isdigit() else self.choices.get(i)
            for i in self
        ]
        return ", ".join([str(s) for s in msg_list])


class MultiSelectField(models.CharField):
    """Choice values can not contain commas."""

    def __init__(self, *args, **kwargs):
        self.min_choices = kwargs.pop("min_choices", None)
        self.max_choices = kwargs.pop("max_choices", None)
        super(MultiSelectField, self).__init__(*args, **kwargs)
        self.max_length = get_max_length(self.choices, self.max_length)
        self.validators.insert(0, MaxValueMultiFieldValidator(self.max_length))
        if self.min_choices is not None:
            self.validators.append(MinChoicesValidator(self.min_choices))
        if self.max_choices is not None:
            self.validators.append(MaxChoicesValidator(self.max_choices))

    def _get_flatchoices(self):
        flat_choices = super(MultiSelectField, self)._get_flatchoices()

        class MSFFlatchoices(list):
            # Used to trick django.contrib.admin.utils.display_for_field into
            # not treating the list of values as a dictionary key (which errors
            # out)
            def __bool__(self):
                return False

            __nonzero__ = __bool__

        return MSFFlatchoices(flat_choices)

    flatchoices = property(_get_flatchoices)

    def get_choices_default(self):
        return self.get_choices(include_blank=False)

    def get_choices_selected(self, arr_choices):
        named_groups = arr_choices and isinstance(
            arr_choices[0][1], (list, tuple)
        )
        choices_selected = []
        if named_groups:
            for choice_group_selected in arr_choices:
                for choice_selected in choice_group_selected[1]:
                    choices_selected.append(str(choice_selected[0]))
        else:
            for choice_selected in arr_choices:
                choices_selected.append(str(choice_selected[0]))
        return choices_selected

    def value_to_string(self, obj):
        try:
            value = self._get_val_from_obj(obj)
        except AttributeError:
            value = super().value_from_object(obj)
        return self.get_prep_value(value)

    def validate(self, value, model_instance):
        arr_choices = self.get_choices_selected(self.get_choices_default())
        for opt_select in value:
            if opt_select not in arr_choices:
                raise exceptions.ValidationError(
                    self.error_messages["invalid_choice"] % {"value": value}
                )

    def get_default(self):
        default = super().get_default()
        if isinstance(default, int):
            default = str(default)
        return default

    def formfield(self, **kwargs):
        defaults = {
            "required": not self.blank,
            "label": capfirst(self.verbose_name),
            "help_text": self.help_text,
            "choices": self.choices,
            "max_length": self.max_length,
            "max_choices": self.max_choices,
        }
        if self.has_default():
            defaults["initial"] = self.get_default()
        defaults.update(kwargs)
        return MultiSelectFormField(**defaults)

    def get_prep_value(self, value):
        return "" if value is None else ",".join(map(str, value))

    def get_db_prep_value(self, value, connection, prepared=False):
        if not prepared and not isinstance(value, str):
            value = self.get_prep_value(value)
        return value

    def to_python(self, value):
        choices = dict(self.flatchoices)

        if value:
            if isinstance(value, list):
                return value
            if isinstance(value, str):
                value_list = map(
                    lambda x: x.strip(), value.replace("，", ",").split(",")
                )
                return MSFList(choices, value_list)
            if isinstance(value, (set, dict)):
                return MSFList(choices, list(value))
        return MSFList(choices, [])

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return self.to_python(value)

    def contribute_to_class(self, cls, name, private_only=False):
        super().contribute_to_class(cls, name, private_only)
        if self.choices:

            def get_list(obj):
                fieldname = name
                choicedict = dict(self.choices)
                display = []
                if getattr(obj, fieldname):
                    for value in getattr(obj, fieldname):
                        item_display = choicedict.get(value, None)
                        if item_display is None:
                            try:
                                item_display = choicedict.get(int(value), value)
                            except (ValueError, TypeError):
                                item_display = value
                        display.append(str(item_display))
                return display

            def get_display(obj):
                return ", ".join(get_list(obj))

            get_display.short_description = self.verbose_name

            setattr(cls, f"get_{self.name}_list", get_list)
            setattr(cls, f"get_{self.name}_display", get_display)
