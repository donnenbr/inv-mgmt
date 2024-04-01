from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/inv-mgmt")
db = client.get_database("inv-mgmt")
coll = db.get_collection("container-type")

# the positions
FREEZER_POSITIONS = [ f"{i+1:02d}" for i in range(10) ]
# tube rack will be the same as plate_96
PLATE_96_POSITIONS = [ f"{y}{x+1}" for x in range(12) for y in "ABCDEFGH" ]
PLATE_384_POSITIONS = [ f"{y}{x+1}" for x in range(24) for y in "ABCDEFGHIJKLMNOP" ]
# rack will be the same as shelf
SHELF_POSITIONS = [ f"{x+1},{y+1}" for x in  range(10) for y in range(10) ]

# the models
data = [
	{ '_id': 'freezer', 'number_rows':10, 'number_columns':1, 'positions': FREEZER_POSITIONS, 'can_hold': 'shelf'},
	{ '_id': 'shelf', 'number_rows':10, 'number_columns':10, 'positions': SHELF_POSITIONS, 'can_hold': 'rack' },
	{ '_id': 'rack', 'number_rows':10, 'number_columns':10, 'positions': SHELF_POSITIONS, 'can_hold': 'vial' },
	{ '_id': 'plate 96', 'number_rows':8, 'number_columns':12, 'positions': PLATE_96_POSITIONS, 'can_hold': 'standard well' },
	{ '_id': 'plate 384', 'number_rows':16, 'number_columns':24, 'positions': PLATE_384_POSITIONS, 'can_hold': 'micro well' },
	{ '_id': 'tube rack', 'number_rows':8, 'number_columns':12, 'positions': PLATE_96_POSITIONS, 'can_hold': 'tube' },
	{ '_id': 'vial', 'can_move': True, 'can_hold_sample': True, 'max_volume': 750, 'volume_unit': 'uL' },
	{ '_id': 'tube', 'can_move': True, 'can_hold_sample': True, 'max_volume': 500, 'volume_unit': 'uL' },
	{ '_id': 'standard well', 'can_move': False, 'can_hold_sample': True, 'max_volume': 250, 'volume_unit': 'uL' },
	{ '_id': 'micro well', 'can_move': False, 'can_hold_sample': True, 'max_volume': 100, 'volume_unit': 'uL' },
]	

coll.insert_many(data)

