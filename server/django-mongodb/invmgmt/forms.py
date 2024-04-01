from django.forms import Form, CharField, IntegerField, FloatField
from django.core.exceptions import ValidationError

MIN_BARCODE_LENGTH = 8
MIN_AMOUNT = 1
MAX_AMOUNT = 750
MIN_CONCENTRATION = 0.1
MAX_CONCENTRATION = 100.0

class FormMixin:
    def get_errors(self) -> [str]:
        if self.is_valid():
            return None
        errors = []
        for fld_name,fld in self.fields.items():
            try:
                fld.clean(self.data.get(fld_name))
            except ValidationError as ve:
                # wierd - sometimes only get the error in messages, not message
                # init-capping the field name to make it look better.  we don't want to set the label
                # value for the field for this since that implies the label value should match what is
                # on the form, which we don't want to assume.
                errors.append(f"{fld_name.title()} : {' '.join(ve.messages)}")
        return errors


class SampleContainerForm(Form, FormMixin):
    # same as the barcode, but we don't want to change the UI
    id = CharField(required=False)
    barcode = CharField(required=True, min_length=MIN_BARCODE_LENGTH)
    lot = CharField(required=True)
    container_type = CharField(required=False, empty_value="vial")
    amount = IntegerField(required=True, min_value=MIN_AMOUNT, max_value=MAX_AMOUNT)
    unit = CharField(required=False, empty_value="uL")
    concentration = FloatField(required=True, min_value=MIN_CONCENTRATION, max_value=MAX_CONCENTRATION)
    concentration_unit = CharField(required=False, empty_value="uM")

class LocateContainerForm(Form, FormMixin):
    barcode = CharField(required=True, min_length=MIN_BARCODE_LENGTH)
    parent_barcode = CharField(required=True, min_length=MIN_BARCODE_LENGTH)
    position = CharField(required=True, min_length=1)

class PickListForm(Form, FormMixin):
    lineNum = IntegerField(required=True, min_value=1)
    reagent = CharField(required=True, min_length=1)
    amount = IntegerField(required=True, min_value=1)
    concentration = IntegerField(required=True, min_value=1)
