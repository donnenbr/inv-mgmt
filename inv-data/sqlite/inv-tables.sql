PRAGMA foreign_keys = ON;

create table reagent (
	id integer primary key,
	name varchar(64) not null,
		smiles varchar(256)
);

create table lot (
	id integer primary key,
	name varchar(128) not null,
	reagent_id integer not null,
	foreign key (reagent_id) references reagent(id)
);

create table container_type (
	id integer primary key,
	name varchar(128) not null,
	number_rows integer,
	number_columns integer,
	can_hold_sample integer not null default 0,
	can_move integer not null default 0,
	check (can_hold_sample in (0,1)),
	check (can_move in (0,1)),
	check (number_rows is null or number_rows >= 0),
	check (number_columns is null or number_columns >= 0)
);

create table container (
	id integer primary key,
	barcode varchar(20) not null,
	type_id integer not null,
	lot_id integer,
	amount real,
	unit varchar(8),
	concentration real,
	concentration_unit varchar(8),
	foreign key (type_id) references container_type(id),
	foreign key (lot_id) references lot(id)
);

create table container_container (
	id integer primary key,
	container_id integer,
	parent_container_id integer not null,
	position varchar(8) not null,
	foreign key (container_id) references container(id),
	foreign key (parent_container_id) references container(id)
);

create unique index reagent_name on reagent(name);
create unique index lot_name on lot(name);
create unique index cont_barcode on container(barcode);
create index lot_reagent on lot(reagent_id);
create index cont_lot_id on container(lot_id);
create index cont_cont_parent on container_container(parent_container_id);
create unique index cont_cont_container on container_container(container_id);

insert into container_type (name) values ('freezer');
insert into container_type (name,number_rows,number_columns) values ('shelf',10,10);
insert into container_type (name,number_rows,number_columns) values ('rack',10,10);
insert into container_type (name,number_rows,number_columns) values ('box',9,9);
insert into container_type (name,can_hold_sample,can_move) values ('vial',1,1);
insert into container_type (name,number_rows,number_columns,can_move) values ('plate_96',8,12,1);
insert into container_type (name,number_rows,number_columns,can_move) values ('plate_384',16,14,1);
insert into container_type (name,can_hold_sample,can_move) values ('well',1,0);




	
