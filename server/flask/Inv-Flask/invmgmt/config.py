import os
from sqlalchemy.engine.url import URL

_DB_FILE_PATH = "/home/bobby/inv-data/inv-data.db"
# _HSQLDB_JAR_PATH = "/home/bobby/hsqldb-2.7.4/hsqldb/lib/hsqldb.jar"
# _H2_DRIVER_JAR = "/home/bobby/git/h2database.git/h2/bin/h2-2.3.239-SNAPSHOT.jar"
_H2_DRIVER_JAR = "/home/bobby/h2-2024-08-11/h2/bin/h2-2.3.232.jar"
_DERBY_DRIVER_JAR = "/home/bobby/apache-derby/db-derby-10.17.1.0-bin/lib/derbyclient.jar"
#
# just for testing the jdbc deriver
#
_POSTGRES_DRIVER_JAR = "/home/bobby/jdbc/postgresql-42.5.2.jar"
_ORACLE_DRIVER_JAR =  "/home/bobby/jdbc/ojdbc11-23.2.0.0.jar"
_MARIADB_DRIVER_JAR =  "/home/bobby/jdbc/mariadb-java-client-3.3.2.jar"
_SQLITE_DRIVER_JAR =  "/home/bobby/jdbc/sqlite-jdbc-3.49.1.0.jar"

# jdbc driver.
# works with mariadb
# error with postgres because it is running with autocommit on and pg errors when trying to do a rollback
# don't see a way to initialize the connection to auto commit off
# error with oracle - it wants to create a jdbc url like :driver://host and cannot create the required
# oracle:thin:@//localhost.  actually it's sqlalchemy???  itr was in sqlajdbc, and fixed.  still an issue
# with the auto commit stuff.

# autocommit stuff fixed in sqlajdbc.

# postgres does NOT like passing string params to integer columns in jdbc.  maybe fix MY code???
# the id generation worked

# oracle - by default the dialog uses LIMIT to limit results and that ain't legit in oracle.
# we'd probably have to look at the driver (postgres, oracle, mysql, mariadb), get the
# corresponding dialog class, then base the BaseDialect on that.  by default it would be
# the default dialect.  this may be impossible.  we don't have access to the url when the dialect
# is created.  also, you can't just replace the existing dialog with a different one (like postgres)
# because it wants the postgres dbapi.

# really looks impossible.  running against a postgres db with the jdbc base dialog based on the postgresql
# dialog was a failure.  the dialog wants the psycopg2 driver because the loaded class is
# sqlalchemy.dialects.postgresql.psycopg2.PGDialect_psycopg2

_DB_DICT = {
    "sqlite" : f"sqlite:///{_DB_FILE_PATH}",
    "postgres" : "postgresql+psycopg2://invmgmt:invmgmt123@localhost:5432/postgres",
    "postgres-ak1" : "postgresql+psycopg2://invmgmt:invmgmt123@192.168.1.6:5432/postgres",
    "mysql": "mysql+mysqlconnector://invmgmt:invmgmt123@localhost/invmgmt",
    # "hsqldb": "hsqldb+jaydebeapi://INVMGMT:invmgmt123@localhost/invmgmt"
    "h2" : URL.create(
        drivername='sqlajdbc',
        # must be host/database
        host='localhost/invmgmt;CASE_INSENSITIVE_IDENTIFIERS=TRUE;AUTOCOMMIT=OFF;',
        query={
            '_class': 'org.h2.Driver',
            # must include the tcp variant as you can't put it in with the host name
            '_driver': 'h2:tcp',
            # userid and password must go here, NOT as username and password params above as this messes
            # up h2 as it uses the WHOLE url and does not chop it off at the query params
            '_dargs': ["invmgmt", "invmgmt123"],
            '_jars': _H2_DRIVER_JAR
        }
    ),
    "derby" : URL.create(
        drivername='sqlajdbc',
        host='localhost:1527//mnt/data/derby-db/invmgmt',
        query={
            '_class': 'org.apache.derby.client.ClientAutoloadedDriver',
            '_driver': 'derby',
            '_dargs': ["invmgmt", "invmgmt123"],
            '_jars': _DERBY_DRIVER_JAR
        }
    ),
    "jdbc-postgres" : URL.create(
        drivername='sqlajdbc',
        host='localhost:5432/postgres',
        query={
            '_class': 'org.postgresql.Driver',
            '_driver': 'postgresql',
            '_dargs': ["invmgmt", "invmgmt123"],
            '_jars': _POSTGRES_DRIVER_JAR
        }
    ),
    "jdbc-oracle" : URL.create(
        drivername='sqlajdbc',
        host='@//localhost:1521/freepdb1',
        query={
            '_class': 'oracle.jdbc.driver.OracleDriver',
            '_driver': 'oracle:thin',
            '_dargs': ["invmgmt", "invmgmt123"],
            '_jars': _ORACLE_DRIVER_JAR
        }
    ),
    "jdbc-mariadb" : URL.create(
        drivername='sqlajdbc',
        host='localhost:3306/invmgmt',
        query={
            '_class': 'org.mariadb.jdbc.Driver',
            '_driver': 'mariadb',
            '_dargs': ["invmgmt", "invmgmt123"],
            '_jars': _MARIADB_DRIVER_JAR
        }
    ),
    "jdbc-sqlite" : URL.create(
        drivername='sqlajdbc',
        host='/home/bobby/inv-data/inv-data.db',
        query={
            '_class': 'java.sql.Driver',
            '_driver': 'sqlite',
            '_dargs': ["invmgmt", "invmgmt123"],
            '_jars': _SQLITE_DRIVER_JAR
        }
    ),
}
SERVER_RELEASE_LEVEL = os.getenv('SERVER_RELEASE_LEVEL', 'prod')
_DB_TYPE = os.getenv("DB_TYPE", "sqlite")
DB_URL_MAP = {
    'prod' : _DB_DICT[_DB_TYPE],
    'test' : 'sqlite://',
    'UnitTest' : 'sqlite://'
}
db_url = DB_URL_MAP [ SERVER_RELEASE_LEVEL ]

print(f"*** db url {db_url}")

# if _DB_TYPE == "hsqldb":
#     os.environ['CLASSPATH'] = _HSQLDB_JAR_PATH
