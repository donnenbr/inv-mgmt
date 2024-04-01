from sqlalchemy.orm import Session
from sqlalchemy import func
from models import *

class ApplicationException(Exception):
    def __init__(self, message: Any):
        self.message = message

def get_container_type(session:Session):
    data = session.query(ContainerType).all()
    return data

def get_containers_by_type(session:Session, container_type:str, limit:int):
    data = session.query(Container).join(Container.type,aliased=True).filter_by(name=container_type).limit(limit).all()
    return data

def _sortable_position(pos:str):
    if pos is None:
        return None
    try:
        return tuple([int(v.strip()) for v in pos.split(",")])
    except:
        # assuming bad int value
        return tuple([v.strip() for v in pos.split(",")])

def _location_str(session:Session, cont:Container):
    if cont is not None:
        l = []
        temp_cont = cont
        while True:
            # print(f"temp cont {temp_cont.barcode} {temp_cont.type.name}")
            cc = session.query(ContainerContainer).filter(ContainerContainer.container==temp_cont).first()
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

def _mk_container_data(session:Session, cont:Container):
    d = {"id": cont.id, "barcode": cont.barcode, "container_type": cont.type.name}
    d['position'] = _location_str(session, cont)
    if cont.type.can_hold_sample:
        d.update({"amount": cont.amount, "unit": cont.unit, "concentration":cont.concentration, "concentration_unit":cont.concentration_unit})
        if cont.lot_id is not None:
            d.update({"lot": cont.lot.name, "reagent": cont.lot.reagent.name})
    else:
        child_containers = session.query(ContainerContainer).filter(ContainerContainer.parent_container==cont).all()
        container_list = []
        for child in child_containers:
            child_cont = child.container
            d_child = { "position": child.position }
            if child_cont is not None:
                d_child.update({"id":child_cont.id, "barcode": child_cont.barcode,
                                "container_type": child_cont.type.name})
                if child_cont.lot_id is not None:
                    d_child['reagent'] = child_cont.lot.reagent.name
            container_list.append(d_child)
        # make sure it's sorted by position which is in row,col format.  we want row, col order and want to make sure
        # that 2,10 is sorted BEFORE 10,1 which would not happen if they were sorted lexically
        # dr. bobby is falling out of love with the position format
        sorted_container_list = sorted(container_list, key=lambda val : _sortable_position(val['position']))
        d['containers'] = sorted_container_list
    return d

def get_container_by_id(session:Session, id:int):
    if id is None:
        return None
    cntr = session.query(Container).get(id)
    if cntr is None:
        return None
    # let's go ape-shit!!!  if the container can contain a sample, we'll return the sample
    # if not, we'll return data on the containers it holds
    return _mk_container_data(session, cntr)

def get_container_by_barcode(session:Session, barcode:str):
    if barcode is None:
        return None
    data = session.query(Container).filter(Container.barcode==barcode).all()
    if len(data) > 1:
        raise ApplicationException("More than one row returned");
    if len(data) < 1:
        return None
    # let's go ape-shit!!!  if the container can contain a sample, we'll return the sample
    # if not, we'll return data on the containers it holds
    return _mk_container_data(session, data[0])

def add_container(session:Session, model: FormSampleContainer):
    # can only be a vial
    if model.container_type != 'vial':
        raise ApplicationException("Container type must be a vial")
    # we assume the other values were validated by pydantic
    # barcode cannot exist
    x = session.query(Container).filter(Container.barcode==model.barcode).count()
    if x > 0:
        raise ApplicationException("Barcode is already in use")
    # check the lot
    lot = session.query(Lot).filter(Lot.name == model.lot).one_or_none()
    if lot is None:
        raise ApplicationException("Lot is invalid")
    cont_type = session.query(ContainerType).filter(ContainerType.name == model.container_type).one()
    cont = Container()
    cont.type = cont_type
    cont.barcode = model.barcode
    cont.lot = lot
    cont.amount = model.amount
    cont.unit = model.unit
    cont.concentration = model.concentration
    cont.concentration_unit = model.concentration_unit
    session.add(cont)
    session.flush()
    session.commit()
    session.refresh(cont)
    # the cont object should now have it's db id.  just put it back
    return _mk_container_data(session,cont)

def update_container(session:Session, model: FormSampleContainer):
    # this is a rest style update so we assume we have the id
    cont = session.query(Container).get(model.id)
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
    session.merge(cont)
    session.commit()
    session.refresh(cont)
    return _mk_container_data(session, cont)

def locate_container(session:Session, model:FormLocateContainer):
    # we assume form passed validation and we have the 3 values we need
    cont = session.query(Container).filter(Container.barcode==model.barcode).one_or_none()
    if cont is None:
        raise ApplicationException(f"Container barcode {model.barcode} is invalid")
    if cont.type.name != 'vial':
        raise ApplicationException("Container is not a vial")
    parent_cont = session.query(Container).filter(Container.barcode == model.parent_barcode).one_or_none()
    if parent_cont is None:
        raise ApplicationException(f"Parent container barcode {model.parent_barcode} is invalid")
    if parent_cont.type.name != 'rack':
        raise ApplicationException("Parent container is not a rack")
    # must have an empty slot for the parent container and position
    loc = session.query(ContainerContainer).filter(ContainerContainer.parent_container==parent_cont) \
            .filter(ContainerContainer.position==model.position).one_or_none()
    if loc is None:
        raise ApplicationException(f"Position {model.position} is invalid")
    if loc.container_id is not None:
        raise ApplicationException("Position is already assigned")
    # note that a container can appear ONLY ONCE as a child in the container_container table
    cont_loc = session.query(ContainerContainer).filter(ContainerContainer.container==cont).one_or_none()
    if cont_loc is not None:
        cont_loc.container = None
        session.merge(cont_loc)
    loc.container = cont
    session.merge(loc)
    session.flush()
    session.commit()
    session.refresh(cont)
    return _mk_container_data(session, cont)

def delete_container(session:Session, container_id:int):
    cont = session.query(Container).get(container_id)
    if cont is None:
        return None
    # must be a vial
    if cont.type.name != 'vial':
        raise ApplicationException("Container is not a vial")
    # see if it has a location.  if so, mark it as empty
    cont_loc = session.query(ContainerContainer).filter(ContainerContainer.container == cont).one_or_none()
    if cont_loc is not None:
        cont_loc.container = None
        session.merge(cont_loc)
    # bye-bye container!!!
    session.delete(cont)
    session.flush()
    session.commit()
    return cont

def generate_pick_list(session:Session, models:List[FormPickListItem]):
    # validate the inputs
    errors = []
    # each reagent must exist
    reagentList = []
    reagentConcentrations = set()
    for rec in models:
        reagent = session.query(Reagent).filter(func.lower(Reagent.name) == func.lower(rec.reagent)).one_or_none()
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
        l = session.query(Container).join(Lot).filter(Lot.reagent_id==reagent_id). \
            filter(Container.amount >= rec.amount).filter(Container.concentration == rec.concentration).all()
        if l:
            d = _mk_container_data(session, l[0])
            # and add requested amount
            d['requested_amount'] = rec.amount
            available_inventory.append(d)
        else:
            unavailable_reagents.append(rec)

    return {"available": available_inventory, "unavailable": unavailable_reagents}

