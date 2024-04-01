An application for the inventory handling of pharmaceautical samples.  
- Register a vial of samples
- Search for samples mrom any part of the location hierarchy (more on that below)
- Put a sample into a specific location
- Create a "pick list" report showing the locations of samples a scientist requestes based on
  reagent name, concentration, and desired amount.  This is similar to order fulfillment you'd
  expect at companies like Amazon.

The application was a way of learning about different backend and frontend frameworks by implementing the
same functionality in them.

Some background - A sample is a specific "reagent" with a name and some other characteristics.  In this case the 
name is a vendor specific id and a "smiles string" which identifies the chemical composition of the reagent.  A 
reagent has one or more "lots", which are production runs of the reagent and something physical which you can hold
in your hand.  For example, the lot identifier on a bottle of aspirin.

Lots of a reagent are held in one or more vials, A vial is placed in a rack which can hold (in our case) 100 vials in
a 10 X 10 array.  Racks are held on shelves, also in a 10 X 10 array.  These shelves are placed in freezers which can 
hold 10 shelves each.  The location of a vial is in the format
	freezer / shelf position / rack position / vial position
where "shelf position" is the position of the shelf in the freezer (1 to 10), "rack position" is the position of the
rack on the shelf (1`,1 to 10,10) and "vial position" is the position of the vial in the rack (also 1,1 to 10,10).
For example: freezer-32 / 06 / 5,6 / 2,7
Also, every location has a barcode which must be unique as it is searchable.  For the sample search mentioned above,
one can start at the freezer and see the shelves within it.  One can the click on a shelf and see the racks within it.
Click on a rack to see the vials.  Click on a vial to see the sample info: reagent, lot, amount, concentration.

====================================================================================================================

The code is broken up into two sections: server and client.  The server sections contains python based backend web
service implementations in Flask, FastAPI, and Django.  All implementations were done using a SQL database with 
sqlite used by default.  Simple changes to the database URI allowed the use of Oracle XE and PostgreSQL.  The django
implementation includes the required django db (sqlite) for users, security, etc.  It also references a separate 
sqlite db for reagent "characteristics" which was just a test of "joining" info from two different dbs in the same
application.  This is NOT used in the main app, but just in a test web service.  Lastly, there are django
implementations which use couchbase and mongodb for the databases as a test of using nosql dbs.  Both use the 
container's barcode for the container primary key and are, as you'd expect, denormalized.  Both have separate
collections for reagents and lots, but each reagent also has the lots as a simple array of strings in the document. 
This was done as an invevstication on how easy that concept is to handle.  The actual code uses the separate lot
collection.

The client sections have the client UI implemented using Ext/JS, AngularJS, NextJS, and Vue.  The Ext/JS version has
a look based on the built-in Ext/JS controls which were not tweaked through Sencha's themer utility.  The others all
have the same look because I wrote the CSS for that.  The exception is the bootstrap version of the angularJS 
implementation which used the bootstrap controls.  I personally did not like them.  The different implementations
have 99% of the same behavior as I sometimes thought of a tweak or two when developing a later implementation.

