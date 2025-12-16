#######################################################################################
#
# used to decode and validate the data posted up from the web forms
#
#######################################################################################

from marshmallow import Schema, fields, validate
# from collections import namedtuple
from dataclasses import make_dataclass

# from marshmallow_validators.wtforms import from_wtforms

MIN_BARCODE_LENGTH = 8
MIN_AMOUNT = 1
MAX_AMOUNT = 750
MIN_CONCENTRATION = 0.1
MAX_CONCENTRATION = 100.0

# the base schema with minimal functionality
class Base_schema(Schema):
    def __init__(self, *args, **kwargs):
        Schema.__init__(self, *args, **kwargs)
        # create the "model class" for the schema.  this is a simple namedtuple which will allow us to
        # access the values as through an object, not a dict.  we create one field in the namedtuple for each
        # field in the schema
        self.model_name = self.__class__.__name__.replace("_schema",'') + "_model"
        fields = list(self.fields.keys())
        # we are creating a dataclass, not namedtuple because the former will be mutable.  there are cases where we
        # want to change a value in the model instance created by the schema.  ex: when updating a vial, we pull the
        # vial's container id from the request and apply it to the model data.  very restful.
        self.model_class = make_dataclass(self.model_name, fields)
        # get all the field names for use in creating model objects
        self.field_names = self.fields.keys()

    # make a model instance from the passed data.  the data may NOT contain all fields of the model as marshmallow
    # does NOT serialize None values unless you add a post dump handler
    def _mk_model_object(self, data: dict):
        # do not monkey with the original data!!!
        d = data.copy()
        if len(d.keys()) < len(self.field_names):
            # there are fewer fields in the data than the model requires.  add None values to the dict for the balance
            # of fields
            d.update(dict([(fld,None) for fld in self.field_names-d.keys()]))
        # now just create the model instance from the data
        return self.model_class(**d)

    # need support for "many"
    def to_model(self, data:dict|list|tuple) -> object:
        # this will yield all values, including defaults, as a dict
        # it will fail if validation fails
        # the assumption is than any single instance is represented by the data being a dict.  if the data is a list
        # or tuple, we assume it represents many objects, so we derive the "many" value from that.
        is_many = isinstance(data,list) or isinstance(data,tuple)
        model_values = self.dump(self.load(data, many=is_many, unknown='exclude'), many=is_many)
        if is_many:
            ret_val = model_list = []
            for val in model_values:
                model_list.append(self._mk_model_object(val))
        else:
            ret_val = self._mk_model_object(model_values)
        return ret_val

# schema for same
class SampleContainer_schema(Base_schema):
    def __init__(self, *args, **kwargs):
        Base_schema.__init__(self, *args, **kwargs)

    # id not required for when we add a new vial.
    id = fields.Int(load_default=None)
    barcode = fields.String(required=True, validate=validate.Length(min=MIN_BARCODE_LENGTH))
    reagent = fields.String()
    lot_id = fields.Integer()
    lot = fields.String(validate=validate.Length(min=1))
    amount = fields.Integer(required=True, validate=validate.Range(min=MIN_AMOUNT, max=MAX_AMOUNT))
    unit = fields.String(default='uL')
    concentration = fields.Float(required=True, validate=validate.Range(min=MIN_CONCENTRATION, max=MAX_CONCENTRATION))
    concentration_unit = fields.String(default="uM")
    container_type = fields.String(required=False, validate=validate.Length(min=2),default='vial')

class LocateContainer_schema(Base_schema):
    def __init__(self, *args, **kwargs):
        Base_schema.__init__(self, *args, **kwargs)

    barcode = fields.String(required=True, validate=validate.Length(min=MIN_BARCODE_LENGTH))
    parent_barcode = fields.String(required=True, validate=validate.Length(min=MIN_BARCODE_LENGTH))
    position = fields.String(required=True, validate=validate.Length(min=1))

class PickList_schema(Base_schema):
    def __init__(self, *args, **kwargs):
        Base_schema.__init__(self, *args, **kwargs)

    lineNum = fields.Int(required=True, validate=validate.Range(min=1))
    reagent = fields.String(required=True, validate=validate.Length(min=1))
    amount = fields.Integer(required=True, validate=validate.Range(min=1))
    concentration = fields.Float(required=True, validate=validate.Range(min=0.1))
