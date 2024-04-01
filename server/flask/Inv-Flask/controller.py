from typing import Any
from sqlalchemy import func

from ma_models import *

class ApplicationException(Exception):
    def __init__(self, message: Any):
        self.message = message

# will be assigned on app startup
db = None

def get_container_types() -> dict:
    ct_list = db.session.query(ContainerType).all()
    ct_schema = ContainerType_schema()
    dump_data = ct_schema.dump(ct_list, many=True)
    return dump_data

def get_lots() -> dict:
    lot_list = db.session.query(Lot).limit(20).all()
    lot_schema = Lot_schema()
    dump_data = lot_schema.dump(lot_list, many=True)
    return dump_data

def get_containers_by_type(cntr_type:str, limit:int = 100) -> [dict]:
    cntr_list = db.session.query(Container).join(Container.type).filter_by(name=cntr_type).limit(limit).all()
    for i,cntr in enumerate(cntr_list):
        cntr.position = str(i)
    cntr_schema = Container_schema()
    data = cntr_schema.dump(cntr_list, many=True)
    return data

########################## real stuff ###############################

def _sortable_position(pos:str):
    if pos is None:
        return None
    try:
        return tuple([int(v.strip()) for v in pos.split(",")])
    except:
        # assuming bad int value
        return tuple([v.strip() for v in pos.split(",")])

def _location_str(cont:Container) -> str|None:
    if cont is not None:
        l = []
        temp_cont = cont
        while True:
            # print(f"temp cont {temp_cont.barcode} {temp_cont.type.name}")
            cc = db.session.query(ContainerContainer).filter(ContainerContainer.container==temp_cont).first()
            if cc is None:
                if len(l) > 0:
                    # input container is not the top level container (ie, freezer), so add the barcode since there is NO position
                    l.insert(0, temp_cont.barcode)
                break
            l.insert(0, cc.position)
            temp_cont = cc.parent_container
        if l:
            return " / ".join(l)
    return None

def _get_child_containers(cont: Container) -> [Container]:
    if cont.lot_id:
        return None
    child_list = []
    child_containers = db.session.query(ContainerContainer).filter(ContainerContainer.parent_container == cont).all()
    for child in child_containers:
        child_cont = child.container
        if child_cont is None:
            # position is EMPTY.  we need a dummy container to serialize
            child_cont = Container()
        child_cont.position = child.position
        child_list.append(child_cont)
    # sort by position - sb sort by attribute
    # sorted_child_list = sorted(child_list, key=lambda val: _sortable_position(val.position))
    return child_list

def _mk_container_info(cntr: Container) -> dict:
    cntr_schema = Container_schema()
    cntr.position = _location_str(cntr)
    cntr.containers = _get_child_containers(cntr)
    data = cntr_schema.dump(cntr, many=False)
    return data

def get_container_by_barcode(barcode:str) -> dict|None:
    cntr_list = db.session.query(Container).filter(Container.barcode == barcode).all()
    if len(cntr_list) > 1:
        raise ApplicationException("More than one row returned");
    if len(cntr_list) < 1:
        return None
    cntr = cntr_list[0]
    return _mk_container_info(cntr)

def get_container(cntr_id) -> dict|None:
    cntr = db.session.query(Container).get(cntr_id)
    if (cntr is not None):
        return _mk_container_info(cntr)
    return None

def add_container(model: Any):
    # can only be a vial
    if model.container_type != 'vial':
        raise ApplicationException("Container type must be a vial")
    # we assume the other values were validated by pydantic
    # barcode cannot exist
    x = db.session.query(Container).filter(Container.barcode==model.barcode).count()
    if x > 0:
        raise ApplicationException("Barcode is already in use")
    # check the lot
    lot = db.session.query(Lot).filter(Lot.name == model.lot).one_or_none()
    if lot is None:
        raise ApplicationException("Lot is invalid")
    cont_type = db.session.query(ContainerType).filter(ContainerType.name == model.container_type).one()
    cont = Container()
    cont.type = cont_type
    cont.barcode = model.barcode
    cont.lot = lot
    cont.amount = model.amount
    cont.unit = model.unit
    cont.concentration = model.concentration
    cont.concentration_unit = model.concentration_unit
    db.session.add(cont)
    db.session.flush()
    db.session.commit()
    db.session.refresh(cont)
    # the cont object should now have it's db id.  just put it back
    return _mk_container_info(cont)

def update_container(model: Any):
    # this is a rest style update so we assume we have the id
    cont = db.session.query(Container).get(model.id)
    if cont is None:
        return None
    # must be a vial
    if cont.type.name != 'vial':
        raise ApplicationException("Container type must be a vial")
    # amount can be either lower (if the concentration is the same) or greater if the concentration is less
    # because the sample was diluted
    if cont.concentration == model.concentration:
        if cont.amount < model.amount:
            raise ApplicationException("Amount cannot be increased")
    elif cont.concentration < model.concentration:
        raise ApplicationException("Concentration cannot be increased")
    # should be good to go.  note that the model prevents setting the amount to zer, so make it 1 if empty or just
    # delete it
    # we do NOT change the units of either since we assume they are constant across the inventory like merck.
    cont.amount = model.amount
    cont.concentration = model.concentration
    db.session.merge(cont)
    db.session.commit()
    db.session.refresh(cont)
    return _mk_container_info(cont)

def delete_container(container_id:int):
    cont = db.session.query(Container).get(container_id)
    if cont is None:
        return None
    # must be a vial
    if cont.type.name != 'vial':
        raise ApplicationException("Container is not a vial")
    # get the container data NOW because there will be problems doing so after it is deleted
    cntr_info = _mk_container_info(cont)
    # see if it has a location.  if so, mark it as empty
    cont_loc = db.session.query(ContainerContainer).filter(ContainerContainer.container == cont).one_or_none()
    if cont_loc is not None:
        cont_loc.container = None
        db.session.merge(cont_loc)
    # bye-bye container!!!
    db.session.delete(cont)
    db.session.flush()
    db.session.commit()
    return cntr_info

def locate_container(model: Any):
    # we assume form passed validation and we have the 3 values we need
    cont = db.session.query(Container).filter(Container.barcode==model.barcode).one_or_none()
    if cont is None:
        raise ApplicationException(f"Container barcode {model.barcode} is invalid")
    if cont.type.name != 'vial':
        raise ApplicationException("Container is not a vial")
    parent_cont = db.session.query(Container).filter(Container.barcode == model.parent_barcode).one_or_none()
    if parent_cont is None:
        raise ApplicationException(f"Parent container barcode {model.parent_barcode} is invalid")
    if parent_cont.type.name != 'rack':
        raise ApplicationException("Parent container is not a rack")
    # must have an empty slot for the parent container and position
    loc = db.session.query(ContainerContainer).filter(ContainerContainer.parent_container==parent_cont) \
            .filter(ContainerContainer.position==model.position).one_or_none()
    if loc is None:
        raise ApplicationException(f"Position {model.position} is invalid")
    if loc.container_id is not None:
        raise ApplicationException("Position is already assigned")
    # note that a container can appear ONLY ONCE as a child in the container_container table
    cont_loc = db.session.query(ContainerContainer).filter(ContainerContainer.container==cont).one_or_none()
    if cont_loc is not None:
        cont_loc.container = None
        db.session.merge(cont_loc)
    loc.container = cont
    db.session.merge(loc)
    db.session.flush()
    db.session.commit()
    db.session.refresh(cont)
    return _mk_container_info(cont)

def generate_pick_list(models:[Any]):
    # validate the inputs
    errors = []
    # each reagent must exist
    reagentList = []
    reagentConcentrations = set()
    for rec in models:
        reagent = db.session.query(Reagent).filter(func.lower(Reagent.name) == func.lower(rec.reagent)).one_or_none()
        if reagent is None:
            errors.append(f"Reagent {rec.reagent} does not exist")
        else:
            key = (rec.reagent,rec.concentration)
            if key in reagentConcentrations:
                errors.append(f"Reagent {rec.reagent} with concentration {rec.concentration} requested more than once")
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
        print(f"reagent id {reagent_id}, amount {rec.amount}, conc {rec.concentration}")
        l = db.session.query(Container).join(Lot).filter(Lot.reagent_id==reagent_id). \
            filter(Container.amount >= rec.amount).filter(Container.concentration == rec.concentration).all()
        if l:
            d = _mk_container_info(l[0])
            # and add requested amount
            d['requested_amount'] = rec.amount
            available_inventory.append(d)
        else:
            unavailable_reagents.append(rec)

    return {"available": available_inventory, "unavailable": unavailable_reagents}

