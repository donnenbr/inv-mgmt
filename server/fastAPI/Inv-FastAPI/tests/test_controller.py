import os
import sys
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import random

os.environ['SERVER_RELEASE_LEVEL'] = 'UnitTest'

sys.path.append("..")

import config
import controller
from models import *
from form_models import *

FREEZER_NAME = 'freezer-A'
SHELF_BARCODE = 10000000
RACK_BARCODE = 20000000
VIAL_BARCODE = 30000000
# barcodes to be assigned to vials we create during the tests (not db setup)
NEW_VIAL_BARCODE = 99990000

# values returned in various dict values from the controller
# top level container with children
PARENT_CONTAINER_KEYS = set(('id','barcode','container_type', 'position', 'containers'))
# the child containers it holds which do NOT hold a sample
CHILD_CONTAINER_KEYS = set(('id', 'barcode', 'container_type', 'position'))
# child containers whicg DO hold a sample
CHILD_SAMPLE_CONTAINER_KEYS = set(('id', 'barcode', 'container_type', 'position', 'reagent'))
# containers which DO hold a sample
SAMPLE_CONTAINER_KEYS = set(('id','barcode','container_type', 'position', 'amount', 'unit', 'concentration', 
                             'concentration_unit', 'lot', 'reagent'))

def setup_db():
    from sqlalchemy.orm import declarative_base

    metadata_obj.create_all(engine)

    _create_container_types()
    _create_lots()
    _create_locations()

def _create_container_types():
    containerTypes = (
        ContainerType(name="freezer", number_rows=1, number_columns=3),
        ContainerType(name='shelf', number_rows=1, number_columns=2),
        ContainerType(name='rack', number_rows=10, number_columns=10),
        ContainerType(name='vial', number_rows=1, number_columns=1, can_hold_sample=True)
    )
    for ct in containerTypes:
        session.add(ct)
    session.commit()

def _create_lots():
    reagents = []
    for i in range(200):
        r = Reagent(name=f'reagent-{i}')
        reagents.append(r)
    session.add_all(reagents)
    session.commit()
    lots = []
    for r in session.query(Reagent).all():
        for i in range(3):
            lots.append(Lot(name=f'{r.name}-{i+1}', reagent_id=r.id))
    session.add_all(lots)
    session.commit()

def _create_locations():
    container_types = {}
    for ct in session.query(ContainerType).all():
        container_types[ct.name] = ct
    # use the capacities of the container types to drive the containers created
    # leave the final rack empty
    freezer = Container(barcode=FREEZER_NAME, type_id=container_types['freezer'].id)
    session.add(freezer)
    session.flush()
    session.refresh(freezer)
    # create shelves
    shelves = []
    barcode = SHELF_BARCODE
    for i in range(container_types['freezer'].number_columns):
        barcode += 1
        cntr = Container(barcode=f'{barcode}', type_id=container_types['shelf'].id)
        shelves.append(cntr)
    session.add_all(shelves)
    # locate them
    session.flush()
    for pos,cntr in enumerate(shelves):
        session.refresh(cntr)
        cntr_cntr = ContainerContainer(container=cntr, parent_container=freezer, position=f'{pos+1}')
        session.add(cntr_cntr)
    session.flush()
    # create racks
    racks = []
    barcode = RACK_BARCODE
    racks_per_shelf = container_types['shelf'].number_columns * container_types['shelf'].number_rows
    for i in range(racks_per_shelf*len(shelves)):
        barcode += 1
        cntr = Container(barcode=f'{barcode}', type_id=container_types['rack'].id)
        racks.append(cntr)
    session.add_all(racks)
    for i,shelf in enumerate(shelves):
        start_idx = i * racks_per_shelf
        end_idx = start_idx + racks_per_shelf
        subset = racks[start_idx:end_idx]
        for pos in range(racks_per_shelf):
            cntr_cntr = ContainerContainer(container=subset[pos], parent_container=shelf, position=f'{pos+1}')
            session.add(cntr_cntr)
    session.flush()
    # create vials - 1 vial per lot.  we create empty positions in the rack to test handling of same as child 
    # containers of a rack.  we do this for ALL racks so we don't need to find specific racks for it.
    lots = session.query(Lot).all()
    concentrations = (1, 2, 10)
    amounts = (500, 250, 100)
    barcode = VIAL_BARCODE
    # leave 5 positions per rack empty
    empty_positions = 5
    vials_per_rack = (container_types['rack'].number_columns * container_types['rack'].number_rows) - empty_positions
    rack_d = {}
    for rack in racks:
        vial_l = []
        rack_d[rack.id] = vial_l
        while len(vial_l) < vials_per_rack:
            lot = lots.pop()
            for amt,conc in zip(amounts,concentrations):
                if len(vial_l) < vials_per_rack:
                    barcode += 1
                    cntr = Container(barcode=f'{barcode}', type_id=container_types['vial'].id, lot=lot,
                                 amount=amt, unit='uL', concentration=conc, concentration_unit='uM')
                    vial_l.append(cntr)
    for l in rack_d.values():
        session.add_all(l)
    positions = [ i for i in range(vials_per_rack+empty_positions)]
    for rack_id,vials in rack_d.items():
        random.shuffle(positions)
        temp_positions = positions.copy()
        for i,vial in enumerate(vials):
            pos = temp_positions.pop()
            cntr_cntr = ContainerContainer(container=vial, parent_container_id=rack_id, position=f'{pos+1}')
            session.add(cntr_cntr)
        # empty positions
        for pos in temp_positions:
            cntr_cntr = ContainerContainer(container=None, parent_container_id=rack_id, position=f'{pos+1}')
            session.add(cntr_cntr)
    session.flush()
    session.commit()

class Test_sortable_position(unittest.TestCase):
    def test_none(self):
        x = controller._sortable_position(None)
        self.assertIsNone(x)

    def test_comma_int(self):
        x = controller._sortable_position("1,2")
        self.assertEqual(x, (1,2))
        x = controller._sortable_position("   3   ,   4  ")
        self.assertEqual(x, (3,4))

    def test_nocomma_int(self):
        x = controller._sortable_position("105")
        self.assertEqual(x, (105,))
        x = controller._sortable_position("  231   ")
        self.assertEqual(x, (231,))

    def test_comma_nonint(self):
        x = controller._sortable_position("a,b")
        self.assertEqual(x, ("a","b"))
        x = controller._sortable_position("   c   ,   d  ")
        self.assertEqual(x, ("c","d"))

    def test_nocomma_nonint(self):
        x = controller._sortable_position("abc")
        self.assertEqual(x, ("abc",))
        x = controller._sortable_position("  def   ")
        self.assertEqual(x, ("def",))

class Test_location_str(unittest.TestCase):
    def test_none(self):
        loc = controller._location_str(session, None)
        self.assertIsNone(loc)

    def test_no_parent(self):
        cntr = session.query(Container).filter(Container.barcode==FREEZER_NAME).one_or_none()
        self.assertIsNotNone(cntr)
        loc = controller._location_str(session, cntr)
        self.assertIsNone(loc)

    def test_with_parent(self):
        # we want to assure the vials have been located
        sub_query = session.query(ContainerContainer.container_id).filter(ContainerContainer.container_id != None)
        vials = session.query(Container).join(Container.type,aliased=True).filter_by(name='vial') \
            .filter(Container.id.in_(sub_query)).all()
        vial_count = len(vials)
        for i in range(10):
            cntr = vials [ random.randint(0,vial_count-1) ]
            loc = []
            cntr_id = cntr.id
            while True:
                cntr_cntr = session.query(ContainerContainer).filter(ContainerContainer.container_id == cntr_id).one_or_none()
                if cntr_cntr is None:
                    break
                loc.insert(0, cntr_cntr.position)
                cntr_id = cntr_cntr.parent_container_id
            self.assertGreater(len(loc), 0)
            # should start with the freezer name
            loc.insert(0, FREEZER_NAME)
            vial_loc = " / ".join(loc)
            cntr_loc = controller._location_str(session, cntr)
            self.assertEqual(vial_loc, cntr_loc)

# both this and the "get_by_barcode" test also test _mk_container_data
# two tests in one???  not really.  we are really verifying what comes back from the controller call against what is in the db.
# NOTE - we assume the ONLY containers with empty children are racks!!! 
class Test_get_container_by_id(unittest.TestCase):
    def test_none(self):
        cntr = controller.get_container_by_id(session, None)
        self.assertIsNone(cntr)

    def test_bad_id(self):
        cntr = controller.get_container_by_id(session, -1)
        self.assertIsNone(cntr)

    # test container which holds other containers which do NOT hold samples 
    def test_shelf(self):
        shelf = session.query(Container).filter(Container.barcode == f'{SHELF_BARCODE+1}').one_or_none()
        self.assertIsNotNone(shelf)
        shelf_children = session.query(ContainerContainer).filter(ContainerContainer.parent_container == shelf).all()
        self.assertGreater(len(shelf_children), 0)
        shelf_children_d = {}
        for child in shelf_children:
            shelf_children_d[child.position] = child
        cntr_d = controller.get_container_by_id(session, shelf.id)
        self.assertIsNotNone(cntr_d)
        self.assertIsInstance(cntr_d, dict)
        self.assertEqual(cntr_d.keys(), PARENT_CONTAINER_KEYS)
        self.assertEqual(cntr_d["id"], shelf.id)
        self.assertEqual(cntr_d["barcode"], shelf.barcode)
        self.assertIsNotNone(cntr_d["position"])
        self.assertGreater(len(cntr_d['position'].strip()), 0)
        self.assertEqual(cntr_d["container_type"], shelf.type.name)
        self.assertIsInstance(cntr_d['containers'], list)
        self.assertEqual(len(cntr_d["containers"]), len(shelf_children))
        expected_keys = set(('id', 'barcode', 'container_type', 'position'))
        for rack in cntr_d['containers']:
            self.assertIsInstance(rack, dict)
            # we must always have a position
            self.assertIsNotNone(rack.get('position'))
            pos = rack['position'].strip()
            self.assertGreater(len(pos), 0)
            child = shelf_children_d[pos]
            self.assertEqual(rack.keys(), CHILD_CONTAINER_KEYS)
            for v in rack.values():
                self.assertIsNotNone(v)
            self.assertEqual(rack['id'], child.container_id)
            self.assertEqual(rack['position'], child.position)
            child_cntr = session.query(Container).get(child.container_id)
            self.assertIsNotNone(child_cntr)
            self.assertEqual(rack['container_type'], child_cntr.type.name)

    # test container which holds other containers which DO hold samples 
    def test_rack(self):
        rack = session.query(Container).filter(Container.barcode == f'{RACK_BARCODE+1}').one_or_none()
        self.assertIsNotNone(rack)
        rack_children = session.query(ContainerContainer).filter(ContainerContainer.parent_container == rack).all()
        self.assertGreater(len(rack_children), 0)
        rack_children_d = {}
        for child in rack_children:
            rack_children_d[child.position] = child
        cntr_d = controller.get_container_by_id(session, rack.id)
        self.assertIsNotNone(cntr_d)
        self.assertIsInstance(cntr_d, dict)
        self.assertEqual(cntr_d.keys(), PARENT_CONTAINER_KEYS)
        self.assertEqual(cntr_d["id"], rack.id)
        self.assertEqual(cntr_d["barcode"], rack.barcode)
        self.assertIsNotNone(cntr_d["position"])
        self.assertGreater(len(cntr_d['position'].strip()), 0)
        self.assertEqual(cntr_d["container_type"], rack.type.name)
        self.assertIsInstance(cntr_d['containers'], list)
        self.assertEqual(len(cntr_d["containers"]), len(rack_children))
        for vial in cntr_d['containers']:
            self.assertIsInstance(vial, dict)
            # we must always have a position
            self.assertIsNotNone(vial.get('position'))
            pos = vial['position'].strip()
            self.assertGreater(len(pos), 0)
            child = rack_children_d[pos]
            if child.container_id is not None:
                # child is a container - should have all expected keys
                self.assertEqual(vial.keys(), CHILD_SAMPLE_CONTAINER_KEYS)
                for v in vial.values():
                    self.assertIsNotNone(v)
                self.assertEqual(vial['id'], child.container_id)
                self.assertEqual(vial['position'], child.position)
                child_cntr = session.query(Container).get(child.container_id)
                self.assertIsNotNone(child_cntr)
                self.assertEqual(vial['container_type'], child_cntr.type.name)
                self.assertEqual(vial['reagent'], child_cntr.lot.reagent.name)
            else:
                # child is an empty position - should only have a position value
                self.assertEqual(len(vial.keys()), 1)

    # test container which holds a sample.  it has no children
    def test_vial(self):
        vial = session.query(Container).filter(Container.barcode == f'{VIAL_BARCODE+1}').one_or_none()
        self.assertIsNotNone(vial)
        self.assertIsNotNone(vial.lot)
        vial_children = session.query(ContainerContainer).filter(ContainerContainer.parent_container == vial).all()
        self.assertEqual(len(vial_children), 0)
        cntr_d = controller.get_container_by_id(session, vial.id)
        self.assertIsNotNone(cntr_d)
        self.assertIsInstance(cntr_d, dict)
        self.assertEqual(cntr_d.keys(), SAMPLE_CONTAINER_KEYS)
        self.assertEqual(cntr_d["id"], vial.id)
        self.assertEqual(cntr_d["barcode"], vial.barcode)
        self.assertIsNotNone(cntr_d["position"])
        self.assertGreater(len(cntr_d['position'].strip()), 0)
        self.assertEqual(cntr_d["container_type"], vial.type.name)
        self.assertEqual(cntr_d["lot"], vial.lot.name)
        self.assertEqual(cntr_d["reagent"], vial.lot.reagent.name)

# same as above, but querying the data by barcode
class Test_get_container_by_barcode(unittest.TestCase):
    def test_none(self):
        cntr = controller.get_container_by_barcode(session, None)
        self.assertIsNone(cntr)

    def test_bad_id(self):
        cntr = controller.get_container_by_barcode(session, 'totally bogus barcode')
        self.assertIsNone(cntr)

    # test container which holds other containers which do NOT hold samples 
    def test_shelf(self):
        l = session.query(Container).join(Container.type,aliased=True).filter_by(name='shelf').all()
        self.assertIsNotNone(l)
        self.assertGreater(len(l), 1)
        shelf = l[1]
        self.assertIsNotNone(shelf)
        shelf_children = session.query(ContainerContainer).filter(ContainerContainer.parent_container == shelf).all()
        self.assertGreater(len(shelf_children), 0)
        shelf_children_d = {}
        for child in shelf_children:
            shelf_children_d[child.position] = child
        cntr_d = controller.get_container_by_barcode(session, shelf.barcode)
        self.assertIsNotNone(cntr_d)
        self.assertIsInstance(cntr_d, dict)
        self.assertEqual(cntr_d.keys(), PARENT_CONTAINER_KEYS)
        self.assertEqual(cntr_d["id"], shelf.id)
        self.assertEqual(cntr_d["barcode"], shelf.barcode)
        self.assertIsNotNone(cntr_d["position"])
        self.assertGreater(len(cntr_d['position'].strip()), 0)
        self.assertEqual(cntr_d["container_type"], shelf.type.name)
        self.assertIsInstance(cntr_d['containers'], list)
        self.assertEqual(len(cntr_d["containers"]), len(shelf_children))
        for rack in cntr_d['containers']:
            self.assertIsInstance(rack, dict)
            # we must always have a position
            self.assertIsNotNone(rack.get('position'))
            pos = rack['position'].strip()
            self.assertGreater(len(pos), 0)
            child = shelf_children_d[pos]
            self.assertEqual(rack.keys(), CHILD_CONTAINER_KEYS)
            for v in rack.values():
                self.assertIsNotNone(v)
            self.assertEqual(rack['id'], child.container_id)
            self.assertEqual(rack['position'], child.position)
            child_cntr = session.query(Container).get(child.container_id)
            self.assertIsNotNone(child_cntr)
            self.assertEqual(rack['container_type'], child_cntr.type.name)

    # test container which holds other containers which DO hold samples 
    def test_rack(self):
        l = session.query(Container).join(Container.type,aliased=True).filter_by(name='rack').all()
        self.assertIsNotNone(l)
        self.assertGreater(len(l), 3)
        rack = l[3]
        self.assertIsNotNone(rack)
        rack_children = session.query(ContainerContainer).filter(ContainerContainer.parent_container == rack).all()
        self.assertGreater(len(rack_children), 0)
        rack_children_d = {}
        for child in rack_children:
            rack_children_d[child.position] = child
        cntr_d = controller.get_container_by_barcode(session, rack.barcode)
        self.assertIsNotNone(cntr_d)
        self.assertIsInstance(cntr_d, dict)
        self.assertEqual(cntr_d.keys(), PARENT_CONTAINER_KEYS)
        self.assertEqual(cntr_d["id"], rack.id)
        self.assertEqual(cntr_d["barcode"], rack.barcode)
        self.assertIsNotNone(cntr_d["position"])
        self.assertGreater(len(cntr_d['position'].strip()), 0)
        self.assertEqual(cntr_d["container_type"], rack.type.name)
        self.assertIsInstance(cntr_d['containers'], list)
        self.assertEqual(len(cntr_d["containers"]), len(rack_children))
        for vial in cntr_d['containers']:
            self.assertIsInstance(vial, dict)
            # we must always have a position
            self.assertIsNotNone(vial.get('position'))
            pos = vial['position'].strip()
            self.assertGreater(len(pos), 0)
            child = rack_children_d[pos]
            if child.container_id is not None:
                # child is a container - should have all expected keys
                self.assertEqual(vial.keys(), CHILD_SAMPLE_CONTAINER_KEYS)
                for v in vial.values():
                    self.assertIsNotNone(v)
                self.assertEqual(vial['id'], child.container_id)
                self.assertEqual(vial['position'], child.position)
                child_cntr = session.query(Container).get(child.container_id)
                self.assertIsNotNone(child_cntr)
                self.assertEqual(vial['container_type'], child_cntr.type.name)
                self.assertEqual(vial['reagent'], child_cntr.lot.reagent.name)
            else:
                # child is an empty position - should only have a position value
                self.assertEqual(len(vial.keys()), 1)

    # test container which holds a sample.  it has no children
    def test_vial(self):
        l = session.query(Container).join(Container.type,aliased=True).filter_by(name='vial').limit(200).all()
        self.assertIsNotNone(l)
        self.assertGreater(len(l), 150)
        vial =l[150]
        self.assertIsNotNone(vial)
        self.assertIsNotNone(vial.lot)
        vial_children = session.query(ContainerContainer).filter(ContainerContainer.parent_container == vial).all()
        self.assertEqual(len(vial_children), 0)
        cntr_d = controller.get_container_by_barcode(session, vial.barcode)
        self.assertIsNotNone(cntr_d)
        self.assertIsInstance(cntr_d, dict)
        self.assertEqual(cntr_d.keys(), SAMPLE_CONTAINER_KEYS)
        self.assertEqual(cntr_d["id"], vial.id)
        self.assertEqual(cntr_d["barcode"], vial.barcode)
        self.assertIsNotNone(cntr_d["position"])
        self.assertGreater(len(cntr_d['position'].strip()), 0)
        self.assertEqual(cntr_d["container_type"], vial.type.name)
        self.assertEqual(cntr_d["lot"], vial.lot.name)
        self.assertEqual(cntr_d["reagent"], vial.lot.reagent.name)
    
class Test_add_container(unittest.TestCase):
    def test_bad_container_type(self):
        # note we MUST pass lot, amount, and concentration since the model is gearred towards adding only vials
        f_model = FormSampleContainer(barcode='00000000', container_type='garbage can', lot='bogus', amount=100, concentration=2)
        with self.assertRaises(controller.ApplicationException) as error:
            controller.add_container(session, f_model)
        self.assertEqual(str(error.exception), "Container type must be a vial")

    def test_not_vial(self):
        f_model = FormSampleContainer(barcode='00000000', container_type='rack', lot='bogus', amount=100, concentration=2)
        with self.assertRaises(controller.ApplicationException) as error:
            controller.add_container(session, f_model)
        self.assertEqual(str(error.exception), "Container type must be a vial")

    def test_invalid_lot(self):
        f_model = FormSampleContainer(barcode='00000000', lot='completely bogus lot', amount=100, concentration=2)
        with self.assertRaises(controller.ApplicationException) as error:
            controller.add_container(session, f_model)
        self.assertEqual(str(error.exception), "Lot is invalid")

    def test_barcode_in_use_1(self):
        lot = session.query(Lot).first()
        self.assertIsNotNone(lot)
        f_model = FormSampleContainer(barcode=f'{VIAL_BARCODE+100}', lot=lot.name, amount=100, concentration=2)
        with self.assertRaises(controller.ApplicationException) as error:
            controller.add_container(session, f_model)
        self.assertEqual(str(error.exception), "Barcode is already in use")

    def test_barcode_in_use_2(self):
        lot = session.query(Lot).first()
        self.assertIsNotNone(lot)
        f_model = FormSampleContainer(barcode=f'{RACK_BARCODE+2}', lot=lot.name, amount=100, concentration=2)
        with self.assertRaises(controller.ApplicationException) as error:
            controller.add_container(session, f_model)
        self.assertEqual(str(error.exception), "Barcode is already in use")

    def test_success(self):
        lot = session.query(Lot).first()
        self.assertIsNotNone(lot)
        barcode = f'{NEW_VIAL_BARCODE+1}'
        cntr = session.query(Container).filter(Container.barcode == barcode).one_or_none()
        self.assertIsNone(cntr)
        f_model = FormSampleContainer(barcode=barcode, lot=lot.name, amount=100, concentration=2)
        cntr_d = controller.add_container(session, f_model)
        self.assertIsNotNone(cntr_d)
        vial = session.query(Container).filter(Container.barcode == barcode).one_or_none()
        self.assertIsNotNone(vial)
        self.assertIsInstance(cntr_d, dict)
        self.assertEqual(cntr_d.keys(), SAMPLE_CONTAINER_KEYS)
        self.assertEqual(cntr_d["id"], vial.id)
        # test the returned data
        self.assertEqual(cntr_d["barcode"], barcode)
        # position should be None as the new vial has not been located
        self.assertIsNone(cntr_d["position"])
        # self.assertGreater(len(cntr_d['position'].strip()), 0)
        self.assertEqual(cntr_d["container_type"], 'vial')
        self.assertEqual(cntr_d["lot"], lot.name)
        self.assertEqual(cntr_d["reagent"], lot.reagent.name)
        self.assertEqual(cntr_d["amount"], f_model.amount)
        self.assertEqual(cntr_d["unit"], f_model.unit)
        self.assertEqual(cntr_d["concentration"], f_model.concentration)
        self.assertEqual(cntr_d["concentration_unit"], f_model.concentration_unit)
        # now test what was in the db (should be the same)
        self.assertEqual(vial.barcode, barcode)
        self.assertEqual(vial.type.name, 'vial')
        self.assertEqual(vial.lot.name, lot.name)
        self.assertEqual(vial.lot.reagent.name, lot.reagent.name)
        self.assertEqual(vial.amount, f_model.amount)
        self.assertEqual(vial.unit, f_model.unit)
        self.assertEqual(vial.concentration, f_model.concentration)
        self.assertEqual(vial.concentration_unit, f_model.concentration_unit)
        # verify it was not located
        cntr_cntr = session.query(ContainerContainer).filter(ContainerContainer.container_id == vial.id).one_or_none()
        self.assertIsNone(cntr_cntr)      
        
class Test_update_container(unittest.TestCase):
    def test_bad_id(self):
        f_model = FormSampleContainer(id=-1, barcode='00000000', container_type='vial', lot='bogus', amount=100, 
                                      concentration=2)
        cntr_d = controller.update_container(session, f_model)
        self.assertIsNone(cntr_d)
    
    def test_not_vial(self):
        cntr = session.query(Container).join(Container.type,aliased=True).filter_by(name='rack').first()
        f_model = FormSampleContainer(id=cntr.id, barcode=cntr.barcode, container_type='vial', lot='bogus', 
                                      amount=100, concentration=2)
        with self.assertRaises(controller.ApplicationException) as error:
            controller.update_container(session, f_model)
        self.assertEqual(str(error.exception), "Container type must be a vial")

    def test_bad_amount(self):
        vial = session.query(Container).filter(Container.barcode == f'{VIAL_BARCODE+10}').one_or_none()
        self.assertIsNotNone(vial)
        f_model = FormSampleContainer(id=vial.id, barcode=vial.barcode, container_type='vial', lot='bogus', 
                                      amount=vial.amount+1, concentration=vial.concentration)
        with self.assertRaises(controller.ApplicationException) as error:
            controller.update_container(session, f_model)
        self.assertEqual(str(error.exception), "Amount cannot be increased")

    def test_bad_concentration(self):
        vial = session.query(Container).filter(Container.barcode == f'{VIAL_BARCODE+10}').one_or_none()
        self.assertIsNotNone(vial)
        f_model = FormSampleContainer(id=vial.id, barcode=vial.barcode, container_type='vial', lot='bogus', 
                                      amount=vial.amount, concentration=vial.concentration+1)
        with self.assertRaises(controller.ApplicationException) as error:
            controller.update_container(session, f_model)
        self.assertEqual(str(error.exception), "Concentration cannot be increased")

    def test_success_decrease_amount(self):
        vial = session.query(Container).filter(Container.barcode == f'{VIAL_BARCODE+10}').one_or_none()
        self.assertIsNotNone(vial)
        lot = vial.lot
        f_model = FormSampleContainer(id=vial.id, barcode=vial.barcode, container_type='vial', lot='bogus', 
                                      amount=vial.amount-1, concentration=vial.concentration)
        cntr_d = controller.update_container(session, f_model)
        self.assertIsNotNone(cntr_d)
        vial = session.query(Container).filter(Container.barcode == f_model.barcode).one_or_none()
        self.assertIsNotNone(vial)
        self.assertIsInstance(cntr_d, dict)
        self.assertEqual(cntr_d.keys(), SAMPLE_CONTAINER_KEYS)
        self.assertEqual(cntr_d["id"], vial.id)
        # test the returned data
        self.assertEqual(cntr_d["barcode"], f_model.barcode)
        # this is a vial created during test setup, so it should have a location
        self.assertIsNotNone(cntr_d["position"])
        self.assertGreater(len(cntr_d['position'].strip()), 0)
        self.assertEqual(cntr_d["container_type"], 'vial')
        self.assertEqual(cntr_d["lot"], lot.name)
        self.assertEqual(cntr_d["reagent"], lot.reagent.name)
        self.assertEqual(cntr_d["amount"], f_model.amount)
        self.assertEqual(cntr_d["unit"], f_model.unit)
        self.assertEqual(cntr_d["concentration"], f_model.concentration)
        self.assertEqual(cntr_d["concentration_unit"], f_model.concentration_unit)
        # now test what was in the db (should be the same)
        self.assertEqual(vial.barcode, f_model.barcode)
        self.assertEqual(vial.type.name, 'vial')
        self.assertEqual(vial.lot.name, lot.name)
        self.assertEqual(vial.lot.reagent.name, lot.reagent.name)
        self.assertEqual(vial.amount, f_model.amount)
        self.assertEqual(vial.unit, f_model.unit)
        self.assertEqual(vial.concentration, f_model.concentration)
        self.assertEqual(vial.concentration_unit, f_model.concentration_unit)

    def test_success_decrease_concentration(self):
        vial = session.query(Container).filter(Container.barcode == f'{VIAL_BARCODE+20}').one_or_none()
        self.assertIsNotNone(vial)
        lot = vial.lot
        f_model = FormSampleContainer(id=vial.id, barcode=vial.barcode, container_type='vial', lot='bogus', 
                                      amount=vial.amount, concentration=vial.concentration-1)
        cntr_d = controller.update_container(session, f_model)
        self.assertIsNotNone(cntr_d)
        vial = session.query(Container).filter(Container.barcode == f_model.barcode).one_or_none()
        self.assertIsNotNone(vial)
        self.assertIsInstance(cntr_d, dict)
        self.assertEqual(cntr_d.keys(), SAMPLE_CONTAINER_KEYS)
        self.assertEqual(cntr_d["id"], vial.id)
        # test the returned data
        self.assertEqual(cntr_d["barcode"], f_model.barcode)
        # this is a vial created during test setup, so it should have a location
        self.assertIsNotNone(cntr_d["position"])
        self.assertGreater(len(cntr_d['position'].strip()), 0)
        self.assertEqual(cntr_d["container_type"], 'vial')
        self.assertEqual(cntr_d["lot"], lot.name)
        self.assertEqual(cntr_d["reagent"], lot.reagent.name)
        self.assertEqual(cntr_d["amount"], f_model.amount)
        self.assertEqual(cntr_d["unit"], f_model.unit)
        self.assertEqual(cntr_d["concentration"], f_model.concentration)
        self.assertEqual(cntr_d["concentration_unit"], f_model.concentration_unit)
        # now test what was in the db (should be the same)
        self.assertEqual(vial.barcode, f_model.barcode)
        self.assertEqual(vial.type.name, 'vial')
        self.assertEqual(vial.lot.name, lot.name)
        self.assertEqual(vial.lot.reagent.name, lot.reagent.name)
        self.assertEqual(vial.amount, f_model.amount)
        self.assertEqual(vial.unit, f_model.unit)
        self.assertEqual(vial.concentration, f_model.concentration)
        self.assertEqual(vial.concentration_unit, f_model.concentration_unit)
        
    def test_success_decrease_concentration_increase_amount(self):
        vial = session.query(Container).filter(Container.barcode == f'{VIAL_BARCODE+30}').one_or_none()
        self.assertIsNotNone(vial)
        lot = vial.lot
        f_model = FormSampleContainer(id=vial.id, barcode=vial.barcode, container_type='vial', lot='bogus', 
                                      amount=vial.amount+100, concentration=vial.concentration-1)
        cntr_d = controller.update_container(session, f_model)
        self.assertIsNotNone(cntr_d)
        vial = session.query(Container).filter(Container.barcode == f_model.barcode).one_or_none()
        self.assertIsNotNone(vial)
        self.assertIsInstance(cntr_d, dict)
        self.assertEqual(cntr_d.keys(), SAMPLE_CONTAINER_KEYS)
        self.assertEqual(cntr_d["id"], vial.id)
        # test the returned data
        self.assertEqual(cntr_d["barcode"], f_model.barcode)
        # this is a vial created during test setup, so it should have a location
        self.assertIsNotNone(cntr_d["position"])
        self.assertGreater(len(cntr_d['position'].strip()), 0)
        self.assertEqual(cntr_d["container_type"], 'vial')
        self.assertEqual(cntr_d["lot"], lot.name)
        self.assertEqual(cntr_d["reagent"], lot.reagent.name)
        self.assertEqual(cntr_d["amount"], f_model.amount)
        self.assertEqual(cntr_d["unit"], f_model.unit)
        self.assertEqual(cntr_d["concentration"], f_model.concentration)
        self.assertEqual(cntr_d["concentration_unit"], f_model.concentration_unit)
        # now test what was in the db (should be the same)
        self.assertEqual(vial.barcode, f_model.barcode)
        self.assertEqual(vial.type.name, 'vial')
        self.assertEqual(vial.lot.name, lot.name)
        self.assertEqual(vial.lot.reagent.name, lot.reagent.name)
        self.assertEqual(vial.amount, f_model.amount)
        self.assertEqual(vial.unit, f_model.unit)
        self.assertEqual(vial.concentration, f_model.concentration)
        self.assertEqual(vial.concentration_unit, f_model.concentration_unit)
        
class Test_delete_container(unittest.TestCase):
    def test_bad_id(self):
        cntr_d = controller.delete_container(session, -1)
        self.assertIsNone(cntr_d)
    
    def test_not_vial(self):
        cntr = session.query(Container).join(Container.type,aliased=True).filter_by(name='rack').first()
        with self.assertRaises(controller.ApplicationException) as error:
            controller.delete_container(session, cntr.id)
        self.assertEqual(str(error.exception), "Container is not a vial")
    
    def test_success_no_location(self):
        cntr_type = session.query(ContainerType).filter(ContainerType.name == 'vial').one_or_none()
        self.assertIsNotNone(cntr_type)
        # just mixing it up
        l = session.query(Lot).limit(100).all()
        self.assertIsNotNone(l)
        self.assertGreater(len(l), 10)
        lot = l[10]
        barcode = f'{NEW_VIAL_BARCODE+100}'
        cntr = Container(barcode=barcode, type=cntr_type, lot=lot, amount=100, unit='uL',
                         concentration=-2, concentration_unit='uM')
        session.add(cntr)
        session.commit()
        # verify it is there
        vial = session.query(Container).filter(Container.barcode == barcode).one_or_none()
        self.assertIsNotNone(vial)
        self.assertIsNotNone(vial.id)
        # paranoid
        self.assertEqual(cntr.barcode, vial.barcode)
        self.assertEqual(cntr.lot_id, vial.lot_id)
        # now delete it.  it returns a Container object since the usual "make dict" method requires the container be in the db.
        deleted_cntr = controller.delete_container(session, vial.id)
        # verify it is gone
        cntr_2 = session.query(Container).get(vial.id)
        self.assertIsNone(cntr_2)
        # and we get the data back
        self.assertIsInstance(deleted_cntr, Container)
        self.assertEqual(deleted_cntr.id, vial.id)
        self.assertEqual(deleted_cntr.barcode, vial.barcode)
        self.assertEqual(deleted_cntr.type.name, 'vial')
        self.assertEqual(deleted_cntr.lot_id, lot.id)
        self.assertEqual(deleted_cntr.lot.reagent.name, lot.reagent.name)
        self.assertEqual(deleted_cntr.amount, vial.amount)
        self.assertEqual(deleted_cntr.unit, vial.unit)
        self.assertEqual(deleted_cntr.concentration, vial.concentration)
        self.assertEqual(deleted_cntr.concentration_unit, vial.concentration_unit)

    # NOTE - we cannot just use a vial created during db setup or it could (did!!!) be picked up by other tests which will
    # fail if there is no position, which is assumed for pre-created vials.
    # seems the easiest way to force some tests to run last is the class names, which are sorted lexically.
    # so Test_zzz_whatever to run last or (better????) Test_0000_whatever to run first
    def test_success_with_location(self):
        cntr_type = session.query(ContainerType).filter(ContainerType.name == 'vial').one_or_none()
        self.assertIsNotNone(cntr_type)
        # just mixing it up
        l = session.query(Lot).limit(100).all()
        self.assertIsNotNone(l)
        self.assertGreater(len(l), 10)
        lot = l[10]
        barcode = f'{NEW_VIAL_BARCODE+110}'
        cntr = Container(barcode=barcode, type=cntr_type, lot=lot, amount=100, unit='uL',
                         concentration=-2, concentration_unit='uM')
        session.add(cntr)
        session.commit()
        # verify it is there
        vial = session.query(Container).filter(Container.barcode == barcode).one_or_none()
        self.assertIsNotNone(vial)
        self.assertIsNotNone(vial.id)
        # paranoid
        self.assertEqual(cntr.barcode, vial.barcode)
        self.assertEqual(cntr.lot_id, vial.lot_id)
        # and locate it - the only empty positions should be in racks (but it really does not matter)
        cntr_cntr = session.query(ContainerContainer).filter(ContainerContainer.container_id == None).first()
        self.assertIsNotNone(cntr_cntr)
        self.assertIsNone(cntr_cntr.container_id)
        cntr_cntr.container = vial
        session.merge(cntr_cntr)
        session.commit()
        cntr_cntr_2 = session.query(ContainerContainer).get(cntr_cntr.id)
        self.assertIsNotNone(cntr_cntr_2)
        self.assertEqual(cntr_cntr_2.parent_container_id, cntr_cntr.parent_container_id)
        self.assertEqual(cntr_cntr_2.position, cntr_cntr.position)
        self.assertEqual(cntr_cntr_2.container_id, vial.id)
        # now delete it.  it returns a Container object since the usual "make dict" method requires the container be in the db.
        deleted_cntr = controller.delete_container(session, vial.id)
        # verify it is gone
        cntr_2 = session.query(Container).get(vial.id)
        self.assertIsNone(cntr_2)
        # and that the location was freed up
        cntr_cntr_3 = session.query(ContainerContainer).get(cntr_cntr.id)
        self.assertIsNotNone(cntr_cntr_3)
        self.assertEqual(cntr_cntr_3.parent_container_id, cntr_cntr.parent_container_id)
        self.assertEqual(cntr_cntr_3.position, cntr_cntr.position)
        self.assertIsNone(cntr_cntr_3.container_id)
        # and we get the data back
        self.assertIsInstance(deleted_cntr, Container)
        self.assertEqual(deleted_cntr.id, vial.id)
        self.assertEqual(deleted_cntr.barcode, vial.barcode)
        self.assertEqual(deleted_cntr.type.name, 'vial')
        self.assertEqual(deleted_cntr.lot_id, lot.id)
        self.assertEqual(deleted_cntr.lot.reagent.name, lot.reagent.name)
        self.assertEqual(deleted_cntr.amount, vial.amount)
        self.assertEqual(deleted_cntr.unit, vial.unit)
        self.assertEqual(deleted_cntr.concentration, vial.concentration)
        self.assertEqual(deleted_cntr.concentration_unit, vial.concentration_unit)

#   locate_container
class Test_locate_container(unittest.TestCase):
    def test_bad_container_barcode(self):
        f_model = FormLocateContainer(barcode='XXXXXXXX', parent_barcode=f'{RACK_BARCODE+1}', position='1')
        with self.assertRaises(controller.ApplicationException) as error:
            cntr_d = controller.locate_container(session, f_model)
        self.assertEqual(str(error.exception), f"Container barcode {f_model.barcode} is invalid")
    
    def test_bad_parent_container_barcode(self):
        f_model = FormLocateContainer(barcode=f'{VIAL_BARCODE+1}', parent_barcode='YYYYYYYY', position='1')
        with self.assertRaises(controller.ApplicationException) as error:
            cntr_d = controller.locate_container(session, f_model)
        self.assertEqual(str(error.exception), f"Parent container barcode {f_model.parent_barcode} is invalid")

    def test_container_not_vial(self):
        f_model = FormLocateContainer(barcode=f'{SHELF_BARCODE+1}', parent_barcode=f'{RACK_BARCODE+1}', position='1')
        with self.assertRaises(controller.ApplicationException) as error:
            cntr_d = controller.locate_container(session, f_model)
        self.assertEqual(str(error.exception), "Container is not a vial")

    def test_parent_container_not_rack(self):
        f_model = FormLocateContainer(barcode=f'{VIAL_BARCODE+1}', parent_barcode=f'{SHELF_BARCODE+1}', position='1')
        with self.assertRaises(controller.ApplicationException) as error:
            cntr_d = controller.locate_container(session, f_model)
        self.assertEqual(str(error.exception), "Parent container is not a rack")

    def test_bad_position(self):
        f_model = FormLocateContainer(barcode=f'{VIAL_BARCODE+1}', parent_barcode=f'{RACK_BARCODE+1}', position='101')
        with self.assertRaises(controller.ApplicationException) as error:
            cntr_d = controller.locate_container(session, f_model)
        self.assertEqual(str(error.exception), f"Position {f_model.position} is invalid")

    def test_occupied_position(self):
        # find an occupied rack position
        cntr_cntr = None
        for rack in session.query(Container).join(Container.type,aliased=True).filter_by(name='rack').all():
            l = session.query(ContainerContainer).filter(ContainerContainer.parent_container == rack) \
                .filter(ContainerContainer.container != None).all()
            if l:
                cntr_cntr = l[0]
                break
        self.assertIsNotNone(cntr_cntr)
        f_model = FormLocateContainer(barcode=f'{VIAL_BARCODE+1}', parent_barcode=cntr_cntr.parent_container.barcode, position=cntr_cntr.position)
        with self.assertRaises(controller.ApplicationException) as error:
            cntr_d = controller.locate_container(session, f_model)
        self.assertEqual(str(error.exception), f"Position is already assigned")

    def test_success_vial_not_previously_located(self):
        # find a free rack position
        cntr_cntr = None
        for rack in session.query(Container).join(Container.type,aliased=True).filter_by(name='rack').all():
            l = session.query(ContainerContainer).filter(ContainerContainer.parent_container == rack) \
                .filter(ContainerContainer.container == None).all()
            if l:
                cntr_cntr = l[0]
                break
        self.assertIsNotNone(cntr_cntr)
        # create a vial
        cntr_type = session.query(ContainerType).filter(ContainerType.name == 'vial').one_or_none()
        self.assertIsNotNone(cntr_type)
        # just mixing it up
        lot = session.query(Lot).first()
        self.assertIsNotNone(lot)
        barcode = f'{NEW_VIAL_BARCODE+200}'
        vial = Container(barcode=barcode, type=cntr_type, lot=lot, amount=100, unit='uL',
                         concentration=-2, concentration_unit='uM')
        session.add(vial)
        session.commit()
        f_model = FormLocateContainer(barcode=barcode, parent_barcode=cntr_cntr.parent_container.barcode, position=cntr_cntr.position)
        cntr_d = controller.locate_container(session, f_model)
        self.assertIsInstance(cntr_d, dict)
        self.assertEqual(cntr_d.keys(), SAMPLE_CONTAINER_KEYS)
        self.assertEqual(cntr_d["id"], vial.id)
        # test the returned data
        self.assertEqual(cntr_d["barcode"], vial.barcode)
        # this is a vial created during test setup, so it should have a location
        self.assertIsNotNone(cntr_d["position"])
        self.assertGreater(len(cntr_d['position'].strip()), 0)
        self.assertEqual(cntr_d["container_type"], 'vial')
        self.assertEqual(cntr_d["lot"], vial.lot.name)
        self.assertEqual(cntr_d["reagent"], vial.lot.reagent.name)
        self.assertEqual(cntr_d["amount"], vial.amount)
        self.assertEqual(cntr_d["unit"], vial.unit)
        self.assertEqual(cntr_d["concentration"], vial.concentration)
        self.assertEqual(cntr_d["concentration_unit"], vial.concentration_unit)
        # and verify that the location is now occuplied
        session.refresh(cntr_cntr)
        self.assertEqual(cntr_cntr.container_id, vial.id)

    def test_success_vial_previously_located(self):
        # find a free rack position
        cntr_cntr_old = cntr_cntr_new = None
        for rack in session.query(Container).join(Container.type,aliased=True).filter_by(name='rack').all():
            l = session.query(ContainerContainer).filter(ContainerContainer.parent_container == rack) \
                .filter(ContainerContainer.container == None).all()
            if len(l) >= 2:
                cntr_cntr_old,cntr_cntr_new = l[0:2]
                break
        self.assertIsNotNone(cntr_cntr_old)
        self.assertIsNotNone(cntr_cntr_new)
        # create a vial
        cntr_type = session.query(ContainerType).filter(ContainerType.name == 'vial').one_or_none()
        self.assertIsNotNone(cntr_type)
        # just mixing it up
        lot = session.query(Lot).first()
        self.assertIsNotNone(lot)
        barcode = f'{NEW_VIAL_BARCODE+201}'
        vial = Container(barcode=barcode, type=cntr_type, lot=lot, amount=100, unit='uL',
                         concentration=-2, concentration_unit='uM')
        session.add(vial)
        # locate it
        cntr_cntr_old.container = vial
        session.merge(cntr_cntr_old)
        session.commit()
        # check the location
        x = session.query(ContainerContainer).get(cntr_cntr_old.id)
        self.assertIsNotNone(x)
        self.assertEqual(x.container_id, vial.id)
        f_model = FormLocateContainer(barcode=barcode, parent_barcode=cntr_cntr_new.parent_container.barcode, position=cntr_cntr_new.position)
        cntr_d = controller.locate_container(session, f_model)
        self.assertIsInstance(cntr_d, dict)
        self.assertEqual(cntr_d.keys(), SAMPLE_CONTAINER_KEYS)
        self.assertEqual(cntr_d["id"], vial.id)
        # test the returned data
        self.assertEqual(cntr_d["barcode"], vial.barcode)
        # this is a vial created during test setup, so it should have a location
        self.assertIsNotNone(cntr_d["position"])
        self.assertGreater(len(cntr_d['position'].strip()), 0)
        self.assertEqual(cntr_d["container_type"], 'vial')
        self.assertEqual(cntr_d["lot"], vial.lot.name)
        self.assertEqual(cntr_d["reagent"], vial.lot.reagent.name)
        self.assertEqual(cntr_d["amount"], vial.amount)
        self.assertEqual(cntr_d["unit"], vial.unit)
        self.assertEqual(cntr_d["concentration"], vial.concentration)
        self.assertEqual(cntr_d["concentration_unit"], vial.concentration_unit)
        # and verify that the old location is free
        session.refresh(cntr_cntr_old)
        self.assertIsNone(cntr_cntr_old.container_id)
        # and that the vial moved to the new location
        session.refresh(cntr_cntr_new)
        self.assertEqual(cntr_cntr_new.container_id, vial.id)

#   generate_pisk_list

if __name__ == '__main__':
    engine = create_engine(config.db_url, echo=False)
    session = Session(engine)
    setup_db()

    unittest.main(verbosity=1)
