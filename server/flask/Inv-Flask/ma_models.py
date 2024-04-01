# from marshmallow import fields, ValidationError
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field, fields
from marshmallow import post_dump, pre_dump

from models import *

class ContainerType_schema(SQLAlchemySchema):
    class Meta:
        model = ContainerType

    id = auto_field()
    name = auto_field()
    number_rows = auto_field()
    number_columns = auto_field()
    can_hold_sample = auto_field()
    can_move = auto_field()

class Reagent_schema(SQLAlchemySchema):
    class Meta:
        model = Reagent

    id = auto_field()
    name = auto_field()
    smiles = auto_field()

class Lot_schema(SQLAlchemySchema):
    class Meta:
        model = Lot

    id = auto_field()
    name = auto_field()
    # will prevent it from showing in a dump
    # reagent_id = auto_field(load_only=True)
    reagent_id = auto_field()
    reagent = fields.Nested(Reagent_schema, many=False, dump_only=True)

    # only dump the reagent name, not all reagent data
    @post_dump(pass_many=False, pass_original=False)
    def post_dump(self, data, **kwargs):
        reag = data.get('reagent')
        if reag:
            data['reagent_name'] = reag.get('name')
            data.pop('reagent')
        return data;

# information on a child container (one listed in the "containers" property of a container
# it just contains the container info (id, barcode, type, position) and only the reagent name of any
# sample the container holds.  we do allow the lot_id through
class ChildContainer_schema(SQLAlchemySchema):
    class Meta:
        model = Container

    id = auto_field()
    barcode = auto_field()
    type_id = auto_field()
    lot_id = auto_field()
    lot = fields.Nested(Lot_schema, many=False, dump_only=True)
    type = fields.Nested(ContainerType_schema, many=False, dump_only=True)
    position = fields.fields.String(dump_only=True)

    @post_dump(pass_many=False, pass_original=False)
    def post_dump(self, data, **kwargs):
        lot = data.pop('lot', None)
        if lot:
            data['reagent'] = lot.get('reagent_name')
            data['lot'] = lot.get('name')
        cntr_type = data.pop('type', None)
        if cntr_type:
            data['container_type'] = cntr_type['name']
        data.pop('type_id')
        return data

# real marshmallow schema for a container.  sample info is stripped out if the container does not hold a sample
# (even if it can but is empty).  this is to minimize the data going down the wire.  we do allow the lot_id through
# child containers are included if they exist and are serialized in a minimalist fashion (no amount or conc), using the
# above schema.  the data for the main container will have the reagent name and lot name if appropriate, but the
# lot object and its nested reagent object are not included
class Container_schema(SQLAlchemySchema):
    class Meta:
        model = Container

    id = auto_field()
    barcode = auto_field()
    type_id = auto_field()
    lot_id = auto_field()
    lot = fields.Nested(Lot_schema, many=False, dump_only=True)
    amount = auto_field()
    unit = auto_field()
    concentration = auto_field()
    concentration_unit = auto_field()
    type = fields.Nested(ContainerType_schema, many=False, dump_only=True)
    position = fields.fields.String(dump_only=True)
    containers = fields.Nested(ChildContainer_schema, many=True, dump_only=True)


    # just an example
    """
    @pre_dump(pass_many=False)
    def pre_dump(self, obj, **kwargs):
        # print(f"*** pre dump {obj}, type {obj.type}")
        # obj.position = "toilet"
        return obj
    """

    sample_fields = ("amount", "unit", "concentration", "concentration_unit")

    @post_dump(pass_many=False, pass_original=False)
    def post_dump(self, data, **kwargs):
        lot = data.pop('lot', None)
        if lot:
            data['reagent'] = lot.get('reagent_name')
            data['lot'] = lot.get('name')
            # no child containers
            data.pop("containers", None)
        else:
            for fld in self.sample_fields:
                data.pop(fld, None)
        cntr_type = data.pop('type', None)
        if cntr_type:
            data['container_type'] = cntr_type['name']
        data.pop('type_id')
        return data


class ParentContainer_schema(Container_schema):
    containers = fields.Nested(Container_schema, many=True, dump_only=True)

    @pre_dump(pass_many=False)
    def pre_dump(self, obj, **kwargs):
        print(f"*** pre dump {obj}, containers {obj.containers}")
        return obj








