from django.db import models
from django.core.exceptions import ObjectDoesNotExist

# implements a sqlalchemy-like "one_or_none" method.  like that, it WILL blow up if more than one row is
# returned.  Thank you Stack Overflow.
# it must be specified in each model, as shown below.  django di NOT like having it done in a base model
# class (which we'd also use for to_json()) - it wanted to use a "basemodel" table.

"""
class BaseModel(models.Model):
    def __init__(self, *args, **kwargs):
        models.Model.__init__(self, *args, **kwargs)

    class Meta:
        db_table = None
"""

class CustomManager(models.Manager):

    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except ObjectDoesNotExist:
            return None

class ModelMixin:

    # exclude_none allows us to strip out null values so the consumer will get a smaller amount of data
    def to_json(self, exclude_none=False) -> dict:
        include_none = not exclude_none
        value_map = self._get_field_value_map(self._meta)
        d = {}
        for k in value_map:
            if k != 'pk':
                obj = getattr(self, k)
                if not (exclude_none and obj is None):
                    if isinstance(obj,models.Model):
                        obj = obj.to_json(exclude_none)
                    d[k] = obj
        return d

### SUPER IMPORTANT NOTE!!!
# if we include an id field, it will NOT be automatically populated when new models are saved, even if it
# is declared as a primary key.  in order for that to happen, we either add an AutoField or BigAutoField
# or just let django do it automatically.  it will create a BigAutoField named id.
# note that Container is the only model the app will create records for.
#
# also note that in all the ForeignKey relations, related_name="+" tells django to NOT create a backwards
# relation.  ex: in Lot,
class Reagent(models.Model, ModelMixin):
    objects = CustomManager()

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=64, null=False, unique=True)
    smiles = models.CharField(max_length=256)

    class Meta:
        db_table = "reagent"

class Lot(models.Model, ModelMixin):
    objects = CustomManager()

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=64, null=False, unique=True)
    reagent = models.ForeignKey(Reagent, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "lot"

class ContainerType(models.Model, ModelMixin):
    objects = CustomManager()

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=128)
    number_rows = models.IntegerField()
    number_columns = models.IntegerField()
    can_hold_sample = models.BooleanField()
    can_move = models.BooleanField()

    class Meta:
        db_table = "container_type"

class Container(models.Model, ModelMixin):
    objects = CustomManager()

    # we'll let django do it automatically
    # id = models.IntegerField(primary_key=True)
    barcode = models.CharField(unique=True, max_length=30)
    amount = models.FloatField(null=True)
    unit = models.CharField(max_length=8, null=True)
    concentration = models.FloatField(null=True)
    concentration_unit = models.CharField(max_length=8, null=True)

    type = models.ForeignKey(ContainerType, on_delete=models.DO_NOTHING)
    lot = models.ForeignKey(Lot, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "container"


class ContainerContainer(models.Model, ModelMixin):
    objects = CustomManager()

    # here too, but the app never creates records for this
    # id = models.IntegerField(primary_key=True)
    position = models.CharField(unique=True, max_length=30)

    parent_container = models.ForeignKey(Container, on_delete=models.DO_NOTHING, related_name="+")
    container = models.ForeignKey(Container, on_delete=models.DO_NOTHING, null=True, related_name="+")

    class Meta:
        db_table = "container_container"

################################################################################################

# just for testing the use of multiple databases.  as far as we can tell, we CANNOT join across
# them as the QuerySet has no concept of join(), just the relations.
# but you CAN do this:
# get reagents with specific characteristics:
# l_chars = ReagentCharacteristics.objects.filter(primary_amines__lt=2,secondary_amines__gt=2,
#               mol_wt__lt=100).values().all()
# this got the characteristics as a dict.  values() can be used to limit the fields coming back.
# for readability, create a list of those reagent names
# reag_list = [reag['reagent_name'] for reag in l_chars]
# then query the Reagent models
# l_reag = Reagent.objects.filter(name__in=reag_list).all()
# natch we'd probably want to put one result into a dict keyed by reagent name for easy lookup joining
# the data, like this
# d = dict((reag.name,reag) for reag in l_reag)
# or d2 = dict((reag.name,reag) for reag in Reagent.objects.filter(name__in=reag_list).all())



class ReagentCharacteristics(models.Model, ModelMixin):
    objects = CustomManager()

    reagent_name = models.CharField(max_length=64, null=False, unique=True)
    mol_wt = models.IntegerField(null=False)
    num_hydrogens = models.IntegerField(null=False)
    num_nitrogens = models.IntegerField(null=False)
    primary_amines = models.IntegerField(null=False)
    secondary_amines = models.IntegerField(null=False)

    class Meta:
        db_table = "reagent_characteristics"
        app_label = "characteristics"
