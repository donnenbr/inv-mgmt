create table reagent (
	id integer primary key,
	name varchar2(64) not null,
		smiles varchar2(1024)
);

create table lot (
	id integer primary key,
	name varchar2(128) not null,
	reagent_id integer not null,
	foreign key (reagent_id) references reagent(id)
);

create table container_type (
	id integer primary key,
	name varchar2(128) not null,
	number_rows integer,
	number_columns integer,
	can_hold_sample integer default 0 not null,
	can_move integer default 0 not null,
	check (can_hold_sample in (0,1)),
	check (can_move in (0,1)),
	check (number_rows is null or number_rows >= 0),
	check (number_columns is null or number_columns >= 0)
);

create table container (
	id integer primary key,
	barcode varchar2(20) not null,
	type_id integer not null,
	lot_id integer,
	amount real,
	unit varchar2(8),
	concentration real,
	concentration_unit varchar2(8),
	foreign key (type_id) references container_type(id),
	foreign key (lot_id) references lot(id)
);

create table container_container (
	id integer primary key,
	container_id integer,
	parent_container_id integer not null,
	position varchar2(8) not null,
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

/* not bothering with a sequence for this */
insert into container_type (id,name) values (1,'freezer');
insert into container_type (id,name,number_rows,number_columns) values (2,'shelf',10,10);
insert into container_type (id,name,number_rows,number_columns) values (3,'rack',10,10);
insert into container_type (id,name,number_rows,number_columns) values (4,'box',9,9);
insert into container_type (id,name,can_hold_sample,can_move) values (5,'vial',1,1);
insert into container_type (id,name,number_rows,number_columns,can_move) values (6,'plate_96',8,12,1);
insert into container_type (id,name,number_rows,number_columns,can_move) values (7,'plate_384',16,14,1);
insert into container_type (id,name,can_hold_sample,can_move) values (8,'well',1,0);




	
