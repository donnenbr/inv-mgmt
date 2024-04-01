PRAGMA foreign_keys = ON;

create table reagent_characteristics (
	id integer primary key,
	reagent_name varchar(64) not null,
	mol_wt integer not null,
	num_hydrogens integer not null,
	num_nitrogens integer not null,
	primary_amines integer not null,
	secondary_amines integer not null
);


create unique index reagent_name on reagent_characteristics(reagent_name);
	
