create or replace trigger reagent_ins_trig before insert on reagent
for each row
begin
  :new.id := reagent_seq.nextval();
end;
/

create or replace trigger lot_ins_trig before insert on lot
for each row
begin
  :new.id := lot_seq.nextval();
end;
/

create or replace trigger container_ins_trig before insert on container
for each row
begin
  :new.id := container_seq.nextval();
end;
/

create or replace trigger cntr_cntr_ins_trig before insert on container_container
for each row
begin
  :new.id := container_container_seq.nextval();
end;
/

