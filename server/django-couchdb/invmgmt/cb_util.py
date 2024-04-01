from couchbase.cluster import Cluster
from couchbase.auth import PasswordAuthenticator
from couchbase.options import ClusterOptions, QueryOptions
from couchbase.exceptions import DocumentNotFoundException

# querying with named params
# lot_list = some list of lot names
# params = ",".join([f"$l{i}" for i in range(len(lot_list))])
# d = {}
# for i,lot in enumerate(lot_list):
#    d[f"l{i}"] = lot
# cntrs = self.run_query("container", None, f"where lot in [ {params} ]", d)
#
# with positional params which can be in the form ?,?,?,... or $1,$2,$3,...
# must be 1 based
# params = ",".join([f"${i+1}" for i in range(len(lot_list))])
# or
# params = ",".join("?"*len(lot_list))
# cntrs = self.run_query("container", None, f"where lot in [ {params} ]", lot_list)

class CoucbaseUtil(object):
    CB_URL :str = "couchbase://localhost"
    APP_USER :str = "invmgmt"
    APP_PASSWORD :str = "invmgmt123"
    APP_BUCKET :str = "inv-mgmt"

    def __init__(self):
        auth = PasswordAuthenticator(self.APP_USER, self.APP_PASSWORD);
        self.cluster = Cluster.connect(self.CB_URL, ClusterOptions(auth))
        self.bucket = self.cluster.bucket(self.APP_BUCKET)
        self.query_context = f"{self.bucket.name}._default"

    def _get_key_field(self, collection: str):
        return 'barcode' if collection == 'container' else 'name'

    def get_by_id(self, collection: str, id: str):
        cb_coll = self.bucket.collection(collection)
        d = None
        try:
            rec = cb_coll.get(id)
            key_field = self._get_key_field(collection)
            # set the key (id) to the appropriate field.  also set "id" so we don't have to
            # change the UI
            d = {'id': rec.key, key_field: rec.key}
            d.update(rec.value)
        except DocumentNotFoundException:
            return None
        # just let it fail otherwise
        return d

    def insert(self, collection: str, row: dict):
        cb_coll = self.bucket.collection(collection)
        key_field = self._get_key_field(collection)
        # pull the id out of the key field.  it MUST be present!!!
        # preserve the original data
        d = row.copy()
        id = d.pop(key_field, None)
        if id is not None:
            id = id.strip()
        if id is None:
            raise ValueError("ID field not found")
        print(f"*** id {id}, data {d}")
        cb_coll.insert(id, d)
        return self.get_by_id("container", id)

    def update(self, collection: str, row: dict):
        cb_coll = self.bucket.collection(collection)
        # preserve the original data
        d = row.copy()
        # we expect an id field in the data, so remove it
        id = d.pop('id', None)
        if id is not None:
            id = id.strip()
        if id is None:
            raise ValueError("ID field not found")
        # also remove the ket field
        key_field = self._get_key_field(collection)
        x = d.pop(key_field, None)
        print(f"*** id {id}, data {d}")
        cb_coll.upsert(id, d)
        return self.get_by_id("container", id)

    def delete(self, collection: str, id: str):
        cb_coll = self.bucket.collection(collection)
        cb_coll.remove(id)

    #
    # NOTE - if you supply field names (which can include aliases), you will get rows back structured like this:
    #   { "id": "X9146084-3",
    #     "smiles": "CCOC(=O)c1ccc(cc1)n2c(c(c3c2nc4ccccc4n3)C(=O)OC5CCCCC5)N"
    #   }
    # if you do not, they will be structured like this, with "*" becoming the document without the id
    #   { "id": "X9184492-9",
    #     "reagent": {
    #         "smiles": "Cc1c(c(n(n1)c2ccccc2)Cl)C=C3C(=O)NC(=S)S3"
    #      }
    #   }
    #
    def run_query(self, collection: str, fields: list = None, extra_clause: str = None, query_params: dict|list|tuple = None):
        field_names = ",".join(fields) if fields else "*"
        sql = f"select meta().id, {field_names} from {collection}"
        if extra_clause:
            sql += " " + extra_clause
        print(f"*** sql {sql}")
        print(f"*** query params {query_params}")
        if query_params is None:
            query_opts = QueryOptions(query_context=self.query_context)
        elif isinstance(query_params,dict):
            query_opts = QueryOptions(query_context=self.query_context, named_parameters=query_params)
        else:
            query_opts = QueryOptions(query_context=self.query_context, positional_parameters=query_params)
        result = self.cluster.query(sql, query_opts)
        l = list()
        key_field = self._get_key_field(collection)
        for row in result:
            # see above as for what we get back
            if fields:
                d = row.copy()
            else:
                d = { 'id': row['id'] }
                d.update(row[collection])
            d[key_field] = d['id']
            l.append(d)
        return l




