from couchbase.cluster import Cluster
from couchbase.auth import PasswordAuthenticator
from couchbase.options import ClusterOptions, QueryOptions

# the positions
FREEZER_POSITIONS = [ f"{i+1:02d}" for i in range(10) ]
# tube rack will be the same as plate_96
PLATE_96_POSITIONS = [ f"{y}{x+1}" for x in range(12) for y in "ABCDEFGH" ]
PLATE_384_POSITIONS = [ f"{y}{x+1}" for x in range(24) for y in "ABCDEFGHIJKLMNOP" ]
# rack will be the same as shelf
SHELF_POSITIONS = [ f"{x+1},{y+1}" for x in  range(10) for y in range(10) ]

# the models
data = {
	'freezer' : { 'number_rows':10, 'number_columns':1, 'positions': FREEZER_POSITIONS, 'can_hold': 'shelf'},
	'shelf' : { 'number_rows':10, 'number_columns':10, 'positions': SHELF_POSITIONS, 'can_hold': 'rack' },
	'rack' : { 'number_rows':10, 'number_columns':10, 'positions': SHELF_POSITIONS, 'can_hold': 'vial' },
	'plate_96' : { 'number_rows':8, 'number_columns':12, 'positions': PLATE_96_POSITIONS, 'can_hold': 'plate_96_well' },
	'plate_384' : { 'number_rows':16, 'number_columns':24, 'positions': PLATE_384_POSITIONS, 'can_hold': 'plate_384_well' },
	'tube_rack' : { 'number_rows':8, 'number_columns':12, 'positions': PLATE_96_POSITIONS, 'can_hold': 'tube' },
	'vial' : { 'can_move': True, 'can_hold_sample': True, 'max_volume': 750, 'volume_unit': 'uL' },
	'tube' : { 'can_move': True, 'can_hold_sample': True, 'max_volume': 500, 'volume_unit': 'uL' },
	'plate_96_well' : { 'can_move': False, 'can_hold_sample': True, 'max_volume': 250, 'volume_unit': 'uL' },
	'plate_384_well' : { 'can_move': False, 'can_hold_sample': True, 'max_volume': 100, 'volume_unit': 'uL' },
}
	

auth = PasswordAuthenticator('invmgmt','invmgmt123');
cluster = Cluster.connect('couchbase://localhost', ClusterOptions(auth))
cb = cluster.bucket('inv-mgmt')

cb_coll = cb.collection('container_type')
for (k,v) in data.items():
	cb_coll.insert(k,v)


