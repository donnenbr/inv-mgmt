import csv
from random import randint

reagents = []

with open("/media/bobby/Removable 1TB/RDSS-MoleculeAnnotations-master/test_data//ChemAcx_Numeric_Annotation_1000000.csv","rt") as f:
	rdr = csv.DictReader(f)
	for row in rdr:
		reagents.append({'name':row['molIdx'],'smiles':row['canonical_smile']})
		
print("reagents ...")
with open("reagent.csv","wt") as f:
	wtr = csv.DictWriter(f, fieldnames=('name','smiles'))
	wtr.writeheader()
	for reag in reagents:
		wtr.writerow(reag)
	f.flush()

# make lots
print("lots ...")
with open("lot.csv","wt") as f:
	wtr = csv.DictWriter(f, fieldnames=('name','reagent'))
	wtr.writeheader()
	for reag in reagents:
		num_lots = randint(3,10)
		lots = []
		for i in range(num_lots):
			reagent_name = reag['name']
			lots.append({'reagent':reagent_name, 'name':f"{reagent_name}-{i}"})
		wtr.writerows(lots)
	f.flush()

