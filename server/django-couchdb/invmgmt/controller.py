from typing import Any
from datetime import datetime

from .forms import *

from .cb_util import CoucbaseUtil

cb = CoucbaseUtil()

class ApplicationException(Exception):
    def __init__(self, message: Any):
        self.message = message

def _location_str(cntr: dict):
    if cntr:
        l = []
        temp_cntr = cntr
        while True:
            # print(f"temp cont {temp_cont.barcode} {temp_cont.type.name}")
            parent_bc,parent_pos = temp_cntr.get("parent_barcode"),temp_cntr.get("parent_position")
            if parent_bc:
                parent_bc = parent_bc.strip()
            if parent_pos:
                parent_pos = parent_pos.strip()
            if not (parent_bc and parent_pos):
                # no parent, add the current container's barcode
                l.insert(0, temp_cntr['barcode'])
                break
            parent_cntr = cb.get_by_id("container", parent_bc)
            if not parent_cntr:
                break
            l.insert(0, parent_pos)
            temp_cntr = parent_cntr
        if l:
            return " / ".join(l)
    return None

def _get_lot_reagent(lot_name: str):
    reagent = None
    try:
        lot = cb.get_by_id("lot", lot_name)
        if lot:
            reagent = lot['reagent']
            if reagent:
                reagent = reagent.strip()
    except Exception as ex:
        print(f"_get_lot_reagent FAILED - {ex}")
    return reagent if reagent else "<UNKNOWN>"

def _mk_container_data(cntr: dict) -> dict:
    d = { "id": cntr['id'], "barcode": cntr['barcode'], "container_type": cntr['type'],
           "position": _location_str(cntr) }
    lot = cntr.get('lot')
    if lot:
        lot = lot.strip()
    if lot:
        d['lot'] = lot
        d['reagent'] = _get_lot_reagent(lot)
        for k in ("amount","unit","concentration","concentration_unit"):
            d[k] = cntr[k]
    else:
        container_list = []
        # query example with hard coded value
        # sql_clause = f"where parent_barcode='{cntr['barcode']}'"
        # child_cntrs = cb.run_query("container", None, sql_clause)
        # query example with query params
        sql_clause = f"where parent_barcode=$parent_barcode"
        child_cntrs = cb.run_query("container", None, sql_clause,
                                {'parent_barcode': cntr['barcode']})
        for child in child_cntrs:
            d2 = { "id": child['id'], "barcode": child['barcode'], "lot": child.get("lot"),
                "container_type": child['type'], "position": child['parent_position'] }
            lot = child.get('lot')
            if lot:
                lot = lot.strip()
            if lot:
                d2['reagent'] = _get_lot_reagent(lot)
            container_list.append(d2)
        # must add empty slots for empty positions.  the id should NOT matter as the client should be
        # looking at the barcode to see if the position is occupied
        cntr_type = cb.get_by_id("container_type", d['container_type'])
        if (cntr_type is None):
            # just complain
            print(f"No container type record found for {d['container_type']}")
        else:
            # use sets to determine the container type's positions which are not occupied
            positions = set(cntr_type.get("positions", []))
            child_positions = set([ child.get("position") for child in container_list ])
            # positions now holds the empty slots
            for i,pos in enumerate(positions-child_positions):
                container_list.append({ "id": f"empty_{i}", "barcode": None, "position": pos })
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

def get_reagents(limit: int = 100) -> list:
    l = cb.run_query(collection="reagent", extra_clause=f"limit {limit}")
    return l

def get_lots(limit: int = 100) -> list:
    l = cb.run_query(collection="lot", extra_clause=f"limit {limit}")
    return l

def get_container_types() -> list:
    # return _list_to_json(ContainerType.objects.all())
    return cb.run_query(collection="container_type")

def get_container_by_barcode(barcode: str) -> dict:
    return get_container_by_id(barcode)

def get_container_by_id(id: str) -> dict:
    t1 = datetime.now()
    cntr = cb.get_by_id("container", id)
    if cntr is not None:
        cntr = _mk_container_data(cntr)
    t2 = datetime.now()
    print(f"*** get container {t2-t1} ms")
    return cntr

def add_new_container(frm: SampleContainerForm) -> dict:
    # paranoid
    if not frm.is_valid():
        raise ApplicationException("Form data is not valid!!!!")
    cntr_data = frm.clean()
    print(cntr_data)
    lot_name = cntr_data.pop("lot").strip()
    if not lot_name:
        raise ApplicationException("Lot must be supplied")
    container_type = cntr_data.pop("container_type").strip()
    if not container_type:
        raise ApplicationException("Container type must be supplied")
    if container_type != 'vial':
        raise ApplicationException("Container must be a vial")

    lot = cb.get_by_id("lot", lot_name)
    if lot is None:
        raise ApplicationException("Lot is invalid")
    barcode = cntr_data.pop("barcode")
    if barcode:
        barcode = barcode.strip()
    if not barcode:
        raise ApplicationException("Container barcode must be supplied")
    cntr = cb.get_by_id("container", barcode)
    if cntr:
        raise ApplicationException("Container barcode is already in use")
    d = { 'barcode': barcode, 'lot': lot_name, 'type': container_type }
    for k in ('amount','unit','concentration','concentration_unit'):
        d[k] = cntr_data[k]
    cntr = cb.insert("container", d)
    return cntr

def update_container(id: str, frm: SampleContainerForm) -> dict:
    # paranoid
    if not frm.is_valid():
        raise ApplicationException("Form data is not valid!!!!")
    cntr = cb.get_by_id("container", id)
    if cntr is None:
        return None
    if cntr['type'] != 'vial':
        raise ApplicationException("Container must be a vial")
    data = frm.clean()
    new_amount,new_concentration = data['amount'],data['concentration']
    # amount can be either lower (if the concentration is the same) or greater if the concentration is less
    # because the sample was diluted
    cntr_conc,cntr_amount = cntr['concentration'],cntr['amount']
    if cntr_conc == new_concentration:
        if cntr_amount < new_amount:
            raise ApplicationException("Amount cannot be increased")
    elif cntr_conc < new_concentration:
        raise ApplicationException("Concentration cannot be increased")
    # we only update the amount and concentration
    cntr['amount'] = new_amount
    cntr['concentration'] = new_concentration
    cntr = cb.update("container", cntr)
    return _mk_container_data(cntr)

def delete_container(id: str) -> dict:
    cntr = cb.get_by_id("container", id)
    if cntr is None:
        return None
    if cntr['type'] != 'vial':
        raise ApplicationException("Container must be a vial")
    cntr_data = _mk_container_data(cntr)
    cb.delete("container", id)
    return cntr_data

def locate_container(frm: SampleContainerForm) -> dict:
    # paranoid
    if not frm.is_valid():
        raise ApplicationException("Form data is not valid!!!!")
    data = frm.clean()
    cntr = cb.get_by_id("container", data['barcode'])
    if cntr is None:
        raise ApplicationException("Container barcode is invalid")
    if cntr['type'] != 'vial':
        raise ApplicationException("Container must be a vial")
    parent_bc,parent_pos = data['parent_barcode'],data['position']
    parent_cntr = cb.get_by_id("container", parent_bc)
    if parent_cntr is None:
        raise ApplicationException("Parent container barcode is invalid")
    if parent_cntr['type'] != 'rack':
        raise ApplicationException("Parent container must be a rack")
    cntr_type = cb.get_by_id("container_type", "rack")
    if cntr_type is None:
        raise ApplicationException("rack container type not found!!!")
    if parent_pos not in cntr_type['positions']:
        raise ApplicationException("Position is invalid")
    # make sure it's not already assigned.  the fields just lets us bring back minimal info
    temp_cntr = cb.run_query("container", fields=["0 as zero"],
                             extra_clause="where parent_barcode=$parent_bc and parent_position=$parent_pos",
                             query_params={"parent_bc":parent_bc, "parent_pos":parent_pos})
    if temp_cntr:
        raise ApplicationException("Position is already occupied.")
    cntr['parent_barcode'] = parent_bc
    cntr['parent_position'] = parent_pos
    cb.update("container", cntr)
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

    t1 = datetime.now()
    data_list = [ frm.clean() for frm in form_list ]
    # validate the inputs
    errors = []
    # we need the reagent lots to do the container query as a join or inner select will KILL the system.
    # we want to use a real list of lots for the container query.  we'll just capture the reagents
    # below then validate them afterward.  we assume any valid reagent will have at least one lot
    # and that lots never disappear, even if a lot has no containerss.
    reagentLots = dict()
    reagentConcentrations = set()
    for rec in data_list:
        reagent_name,amount,concentration = rec['reagent'].strip(),rec['amount'],rec['concentration']
        upper_reagent = reagent_name.upper()
        key = (upper_reagent, concentration)
        if key in reagentConcentrations:
            errors.append(f"Reagent {reagent_name} with concentration {concentration} requested more than once")
        else:
            reagentConcentrations.add(key)
            if upper_reagent not in reagentLots:
                reagentLots[upper_reagent] = {"name": reagent_name, "lots":[]}
    if errors:
        raise ApplicationException(errors)
    # get the lots for each reagent
    reagent_list = list(reagentLots.keys())
    query_params = ",".join("?"*len(reagent_list))
    lots = cb.run_query("lot", extra_clause=f"where upper(reagent) in [ {query_params} ]",
                        query_params=reagent_list)
    for l in lots:
        x = reagentLots[l['reagent'].upper()]['lots']
        x.append(l['name'])

    # validate the reagents.  invalid ones will have no lots.
    for reagent in reagentLots.values():
        if not reagent['lots']:
            errors.append(f"Reagent {reagent['name']} is invalid.")
    if errors:
        raise ApplicationException(errors)

    available_inventory = []
    unavailable_reagents = []

    for rec in data_list:
        reagent_name,amount,concentration = rec['reagent'].strip(),rec['amount'],rec['concentration']
        lots = reagentLots[reagent_name.upper()]['lots']
        query_params = { 'amount': amount, 'concentration': concentration }
        lot_param_names = []
        for i,lot_name in enumerate(lots):
            param_name = f"lot{i}"
            lot_param_names.append(f"${param_name}")
            query_params[param_name] = lot_name
        sql_clause = f"where amount >= $amount and concentration = $concentration and lot in [ {','.join(lot_param_names)} ] order by amount"
        # we'll pick the container with the amount closest to the requested amount
        result = cb.run_query("container", extra_clause=sql_clause, query_params=query_params)
        if result:
            d = _mk_container_data(result[0])
            # and add requested amount
            d['requested_amount'] = rec['amount']
            available_inventory.append(d)
        else:
            d = {"requested_amount": amount}
            d.update(rec)
            unavailable_reagents.append(d)

    t2 = datetime.now()
    print(f"*** pick list {t2 - t1} ms")
    return {"available": available_inventory, "unavailable": unavailable_reagents}

