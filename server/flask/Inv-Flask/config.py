import os

SERVER_RELEASE_LEVEL = os.getenv('SERVER_RELEASE_LEVEL', 'prod')

_db_file_path = "/home/bobby/inv-data/inv-data.db"

DB_URL_MAP = {
    'prod' : f"sqlite:///{_db_file_path}",
    'test' : 'sqlite://',
    'UnitTest' : 'sqlite://'
}
db_url = DB_URL_MAP [ SERVER_RELEASE_LEVEL ]