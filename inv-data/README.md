This folder contains utilities for creating the data for the Inventory Management app.  This includes:
	- reagents
	- lots
	- containers (freezers, shelves, racks, vials)
	- assigning vials to racks, racks to shelves, shelves to freezers.

The sqlite folder contains the ddl scripts for the tables and initial data for the container_type table

In the top level folder, mk_reagents.py creates the reagents and lot data from an input file in CSV format.
This file is NOT included becauae it is quite large and contains proprietary information.  Any CSV file with 
the reagent name in the molIdx column, and smiles in canonical_smile column will do.  The smiles data is not
used in the app so any random string will do.  mk_containers.py creates the freezers, shelves, and racks.
mk_vials.py creates the vials.  Run mk_reagents, mk_containers, mk_vials in that order.  The numbner of 
freezers (over 200) is based on the number of rows in the reagent file I used (1025000).  These python scripts
use straight dbapi calls to create the db data.  The folders oracle and postgres have custom sqlscripts to 
create the tables (and triggers for oracle pks) as well as custom versions of the mk_*.py scripts.

The folders couchbase and mongodb have scripts which create csv files of reagents and lots (mk_reagents.py), 
freezers, shelves, racks (mk_containers.py) and vials (mk_vials.py).  These files are then loaded into the db 
using the valious load_*.py scripts.  There is also load_container_types.py which creates the container types.
The mongodb and caouchbase variants have the same container structure so they both use the same format csv files.
