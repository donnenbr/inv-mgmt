from django.db import transaction, models
from typing import Any

from .models import *
from .forms import *

class ApplicationException(Exception):
    def __init__(self, message: Any):
        self.message = message

# sqlalchemy-like one_or_none implemented as a local method
"""
def _get_one_or_none(model_class: models.Model, **kwargs) -> models.Model|None :
    try:
        obj = model_class.objects.get(**kwargs)
    except model_class.DoesNotExist:
        obj = None
    return obj
"""

def _location_str(cntr:Container):
    if cntr:
        l = []
        temp_cntr = cntr
        while True:
            # print(f"temp cont {temp_cont.barcode} {temp_cont.type.name}")
            cc = ContainerContainer.objects.filter(container=temp_cntr).all()
            if len(cc) != 1:
                if len(l) > 0:
                    # input container is not the top level container (ie, freezer), so add the barcode since there is NO position
                    l.insert(0, temp_cntr.barcode)
                break
            l.insert(0, cc[0].position)
            temp_cntr = cc[0].parent_container
        if l:
            return " / ".join(l)
    return None
def _mk_container_data(cntr: Container) -> dict:
    d = {  "id": cntr.id, "barcode": cntr.barcode, "container_type": cntr.type.name,
           "position": _location_str(cntr) }
    if cntr.lot:
        d['lot'] = cntr.lot.name
        d['reagent'] = cntr.lot.reagent.name
        d['amount'] = cntr.amount
        d['unit'] = cntr.unit
        d['concentration'] = cntr.concentration
        d['concentration_unit'] = cntr.concentration_unit
    else:
        container_list = []
        for child in ContainerContainer.objects.filter(parent_container=cntr).all():
            child_cntr = child.container
            if child_cntr:
                d2 = { "id": child_cntr.id, "barcode": child_cntr.barcode,
                    "container_type": child_cntr.type.name, "position": child.position }
                if child_cntr.lot:
                    d2['reagent'] = child_cntr.lot.reagent.name
            else:
                d2 = { "position": child.position }
            container_list.append(d2)
        sorted_container_list = sorted(container_list, key=lambda val: _sortable_position(val['position']))
        d['containers'] = sorted_container_list

    return d

def _sortable_position(pos:str):
    if pos is None:
        return None
    try:
        return tuple([int(v.strip()) for v in pos.split(",")])
    except:
        # assuming bad int value
        return tuple([v.strip() for v in pos.split(",")])

def _list_to_json(models: [models.Model]) -> dict:
    data = []
    for obj in models:
        data.append(obj.to_json())
    return data
def get_reagents(limit: int = 100) -> dict:
    return _list_to_json(Reagent.objects.all()[:limit])

def get_lots(limit: int = 100) -> dict:
    return _list_to_json(Lot.objects.all()[:limit])

def get_container_types() -> dict :
    return _list_to_json(ContainerType.objects.all())

def get_container_by_barcode(barcode: str) -> dict:
    l = Container.objects.filter(barcode=barcode).all()
    if len(l) != 1:
        if len(l) < 1:
            return None
        raise ApplicationException("More than one row returned")
    return _mk_container_data(l[0])

def get_container_by_id(id: int) -> dict:
    # pk is a pseudonym for id.  since we are querying by the pk, we assume one row, or none, only.
    cntr = Container.objects.filter(pk=id).first()
    if cntr is None:
        return None
    return _mk_container_data(cntr)

def add_new_container(frm: SampleContainerForm) -> dict:
    # paranoid
    if not frm.is_valid():
        raise ApplicationException("Form data is not valid!!!!")
    cntr_data = frm.clean()
    lot_name = cntr_data.pop("lot").strip()
    if not lot_name:
        raise ApplicationException("Lot must be supplied")
    container_type = cntr_data.pop("container_type").strip()
    if not container_type:
        raise ApplicationException("Container type must be supplied")
    if container_type != 'vial':
        raise ApplicationException("Container must be a vial")

    cntr = Container(**cntr_data)
    lot = Lot.objects.get_or_none(name=lot_name)
    if lot is None:
        raise ApplicationException("Lot is invalid")
    cntr.lot = lot

    cntr_type = ContainerType.objects.get_or_none(name=container_type)
    if cntr_type is None:
        raise ApplicationException("Container type is invalid")
    cntr.type = cntr_type
    # check the barcode for dups
    cntr.barcode = cntr.barcode.strip()
    if Container.objects.filter(barcode=cntr.barcode).count() > 0:
        raise ApplicationException("Barcode is already in use")
    with transaction.atomic():
        cntr.save()
        return _mk_container_data(cntr)

def update_container(id: int, frm: SampleContainerForm) -> dict:
    # paranoid
    if not frm.is_valid():
        raise ApplicationException("Form data is not valid!!!!")
    cntr = Container.objects.filter(pk=id).first()
    if cntr is None:
        return None
    if cntr.type.name != 'vial':
        raise ApplicationException("Container must be a vial")
    data = frm.clean()
    new_amount,new_concentration = data['amount'],data['concentration']
    # amount can be either lower (if the concentration is the same) or greater if the concentration is less
    # because the sample was diluted
    if cntr.concentration == new_concentration:
        if cntr.amount < new_amount:
            raise ApplicationException("Amount cannot be increased")
    elif cntr.concentration < new_concentration:
        raise ApplicationException("Concentration cannot be increased")
    # we only update the amount and concentration
    cntr.amount = new_amount
    cntr.concentration = new_concentration
    with transaction.atomic():
        cntr.save()
    return _mk_container_data(cntr)

def delete_container(id: int) -> dict:
    cntr = Container.objects.filter(pk=id).first()
    if cntr is None:
        return None
    if cntr.type.name != 'vial':
        raise ApplicationException("Container must be a vial")
    # is this container located under a parent???  there should only be ONE
    cntr_cntr = ContainerContainer.objects.filter(container=cntr).first()
    # must get this before the container is deleted (natch!!!)
    cntr_data = _mk_container_data(cntr)
    with transaction.atomic():
        if cntr_cntr:
            cntr_cntr.container = None
            cntr_cntr.save()
            cntr.delete()
    return cntr_data

def locate_container(frm: SampleContainerForm) -> dict:
    # paranoid
    if not frm.is_valid():
        raise ApplicationException("Form data is not valid!!!!")
    data = frm.clean()

    cntr = Container.objects.get_or_none(barcode=data['barcode'])
    if cntr is None:
        raise ApplicationException("Container barcode is invalid")
    if cntr.type.name != 'vial':
        raise ApplicationException("Container must be a vial")
    parent_cntr = Container.objects.get_or_none(barcode=data['parent_barcode'])
    if parent_cntr is None:
        raise ApplicationException("Parent container barcode is invalid")
    if parent_cntr.type.name != 'rack':
        raise ApplicationException("Parent container must be a rack")
    # parent container + position should be unique
    new_location = ContainerContainer.objects. \
        get_or_none(parent_container=parent_cntr,position=data['position'])
    if new_location is None:
        raise ApplicationException("Position is invalid")
    if new_location.container:
        raise ApplicationException("Position is already occupied.")
    # container (as a child) should also be unique in container_container
    curr_location = ContainerContainer.objects.get_or_none(container=cntr)
    with transaction.atomic():
        if curr_location:
            curr_location.container = None
            curr_location.save()
        new_location.container = cntr
        new_location.save()
    return _mk_container_data(cntr)

def generate_pick_list(form_list: [PickListForm]) -> dict:
    # some reagents to use
    """
    X8277128-4
    X11546287-2
    X10008319-6
    Child_X10008319-6
    X6091314-6
    X2428538-7
    X8163306-7
    X7811932-7
    X10902884-2
    X6041174-7
    X4151109-3
    Child_X4151109-3
    X6814737-3
    X8538334-0
    X5441102-8
    X9301900-4
    X6028126-3
    X10567858-8
    X1701017-4
    Child_X1701017-4
    X11538903-4
    X12043500-6
    X3358639-7
    X3854325-2
    X8675023-4
    X9184492-9
    X9146084-3
    Child_X9146084-3
    X10183509-1
    X8319691-4
    """
    # verify all forms are valid
    if not form_list:
        raise ApplicationException("Form list cannot be empty")
    for frm in form_list:
        if not frm.is_valid():
            raise ApplicationException("Form data is not valid!!!!")
    data_list = [ frm.clean() for frm in form_list ]
    # validate the inputs
    errors = []
    # each reagent must exist
    reagentList = []
    reagentConcentrations = set()
    for rec in data_list:
        reagent_name,amount,concentration = rec['reagent'].strip(),rec['amount'],rec['concentration']
        # iexact is case insensitive matching
        reagent = Reagent.objects.get_or_none(name__iexact=reagent_name)
        if reagent is None:
            errors.append(f"Reagent {reagent_name} does not exist")
        else:
            key = (reagent.id, concentration)
            if key in reagentConcentrations:
                errors.append(f"Reagent {reagent_name} with concentration {concentration} requested more than once")
            else:
                reagentList.append({"reagent_id": reagent.id, "record": rec})
                reagentConcentrations.add(key)
    if errors:
        raise ApplicationException(errors)

    available_inventory = []
    unavailable_reagents = []
    for reagent in reagentList:
        reagent_id = reagent['reagent_id']
        rec = reagent['record']
        # print(f"reagent id {reagent_id}, amount {rec['amount']}, conc {rec['concentration']}")
        # we'll pick the container with the amount closest to the requested amount
        # note - using a dict to make the query more readable.  could have put all of that in the filter as
        # comma separated values with "=" separating the key from the value like so
        # cntr = Container.objects.filter(lot__reagent_id=reagent_id, concentration=rec['concentration'], ...
        # note how we used lot__reagent_id to match the container lots by reagent id.  we COULD have also used
        # lot__reagent__name to access by reagent name.  also, amount__gte=value means amount >= value
        # django querying has many such operations, like type__name__in=['vial','tube'] to query a container
        # whose type is vial or tube.  could also do "type__name='vial' | type__name='tube'"
        # last note - NOT (as in amount != 100) requires the use of django's Q class (for Query???):
        # from django.db.models import Q
        # Container.objects.filter(Q(type__name='vial'), ~Q(amount=100)).all()
        # the ~ negates the query represented by Q instance.  if using Q()s, they must come first BECAUSE
        # the Qs are positional args and the others are keyword args.
        qry = {"lot__reagent_id": reagent_id, "concentration": rec['concentration'], "amount__gte": rec['amount']}
        cntr = Container.objects.filter(**qry).order_by("amount").first()
        if cntr:
            d = _mk_container_data(cntr)
            # and add requested amount
            d['requested_amount'] = rec['amount']
            available_inventory.append(d)
        else:
            unavailable_reagents.append(rec)

    return {"available": available_inventory, "unavailable": unavailable_reagents}

def reagent_search(min_mw:int, max_mw:int) -> [dict] :
    # data comes back as a QuerySet.  kind of acts like a list of dicts but it is NOT!!!
    reagent_chars = ReagentCharacteristics.objects.filter(mol_wt__gte=min_mw,mol_wt__lte=max_mw) \
            .order_by("mol_wt").values()
    reagent_names = [reag['reagent_name'] for reag in reagent_chars]
    # the number of records can be quite large, so do this in batches
    BATCH_SIZE = 1000  # sqlite seems to be able to handle 100K, but this is more "cross-db" friendly.  faster too.
    reagent_data = []
    for idx in range(0, len(reagent_names), BATCH_SIZE):
        temp = reagent_names[idx:idx + BATCH_SIZE]
        reagent_data.extend(Reagent.objects.filter(name__in=temp).values())
    # put the data in a dict for quick lookup
    reagent_dict = dict((reag['name'], reag) for reag in reagent_data)
    # just reuse reagent_data for the return
    reagent_data = []
    for rec in reagent_chars:
        smiles = reagent_dict[rec['reagent_name']]['smiles']
        d = dict(rec.items())
        d['smiles'] = smiles
        reagent_data.append(d)
    print(f"*** returning {len(reagent_data)} rows")
    return reagent_data
