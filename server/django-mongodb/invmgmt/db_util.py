from pymongo import MongoClient

class DbUtil(object):
    DB_URL :str = "mongodb://localhost:27017/inv-mgmt"
    DATABASE = "inv-mgmt"
    ID_FIELD = "_id"

    def __init__(self):
        self.client = MongoClient(self.DB_URL)
        self.db = self.client.get_database(self.DATABASE)
        self.collections = self.db.list_collection_names()

    def _get_collection(self, collection: str):
        if collection not in self.collections:
            raise RuntimeError(f"Collection {collection} is invalid")
        return self.db.get_collection(collection)
    def _get_key_field(self, collection: str):
        return 'barcode' if collection == 'container' else 'name'

    def get_by_id(self, collection: str, id: str):
        coll = self._get_collection(collection)
        d = None
        rec = coll.find_one(id)
        if rec is not None:
            key_field = self._get_key_field(collection)
            # set the key (id) to the appropriate field.  also set "id" so we don't have to
            # change the UI
            rec_id = rec.pop(self.ID_FIELD)
            d = {'id': rec_id, key_field: rec_id}
            d.update(rec)
        # just let it fail otherwise
        return d

    def insert(self, collection: str, row: dict):
        coll = self._get_collection(collection)
        key_field = self._get_key_field(collection)
        # pull the id out of the key field.  it MUST be present!!!
        # preserve the original data
        d = row.copy()
        rec_id = d.pop(key_field, None)
        if rec_id is not None:
            rec_id = rec_id.strip()
        if rec_id is None:
            raise ValueError("ID field not found")
        # also pop off the id field we used just to appease the fronth end
        x = d.pop("id", None)
        # and restore the record's mongo id
        d[self.ID_FIELD] = rec_id
        print(f"*** id {rec_id}, data {d}")
        coll.insert_one(d)
        return self.get_by_id("container", rec_id)

    def update(self, collection: str, row: dict):
        coll = self._get_collection(collection)
        # preserve the original data
        d = row.copy()
        # we expect an id field in the data, so remove it
        rec_id = d.pop('id', None)
        if rec_id is not None:
            rec_id = rec_id.strip()
        if rec_id is None:
            raise ValueError("ID field not found")
        # also remove the ket field
        key_field = self._get_key_field(collection)
        x = d.pop(key_field, None)
        coll.replace_one({self.ID_FIELD:rec_id}, d)
        return self.get_by_id("container", rec_id)

    def delete(self, collection: str, rec_id: str):
        coll = self._get_collection(collection)
        coll.delete_one({self.ID_FIELD: rec_id})

    def run_query(self, collection: str, filter: dict, fields: [str] = None, options: dict|None = None):
        coll = self._get_collection(collection)
        result = coll.find(filter, fields, **options) if options else coll.find(filter, fields)
        l = list()
        key_field = self._get_key_field(collection)
        for row in result:
            rec_id = row.pop(self.ID_FIELD)
            d = { "id": rec_id, key_field: rec_id }
            d.update(row)
            l.append(d)
        return l




