A better designed (IMHO) version NOT following Flask's example.  The views are separate files
(based on functionality) in the views module.  Although a bit extreme considering pick list is
ONE method, it's an example on how the app can be broken up.

From the project's top folder, run with flask --app invmgmt.main:app run
or gunicorn --config gunicorn_config.py invmgmt.main:app
They both run on port 5000.  apache is wired so localhost/service/invmgmt forwards to this
port.

Docker NOT tested with new version.

###############################################################################################
#
old doc, slot still valid

Run with the command: flask --app main:app run
Test with http://localhost:5000/container_types
to run in PRODUCTION mode: gunicorn --config gunicorn_config.py main:app


By default, it uses sqlite.  To run with postgres:
start the postgres server with
	sudo docker start pg-sql
all db docker instances are pre-built!!!
then ...
export DB_TYPE="postgres"
and issue "flask run"

Docker:
had to downgrade python to 3.12 (same as pc) because postgres python lib has issues with version 3.13.
changed config.py to use real pc ip address (not localhost) for postgres.
build with: sudo docker build -t invmgmt-flask  --build-context root=. docker
may want to pass env var to specify postgres???  or just put it in the dockerfile.
run with: sudo docker run -it -p 5000:5000 invmgmt-flask
with pg-sql container running.  success!!!!!!!
should give it a name

Dr. Bob decides we will NOT use nginx, but just gunicorn.  The available docker image for flask/nginx uses python 3.8 which
does not support some of the typing stuff.  If combining an nginx image with a python image using docker compose, you get
a container for EACH.  too complicated!!!
Potential issue - SiteMinter, https.  we shall see.

