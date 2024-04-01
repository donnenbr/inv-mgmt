# posting json data : curl -H "Content-Type: application/json" --request POST -d '{"first":"bob","age":65}' localhost:5000/test
# posting form data :

from typing import Any
from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from marshmallow.exceptions import ValidationError

import config
import controller
from form_models import *

class Base(DeclarativeBase):
  pass

controller.db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = config.db_url
# initialize the app with the extension
controller.db.init_app(app)

# info
app.logger.setLevel(1)

def _mk_success_return(data: Any) -> tuple :
    return {"success": True, "data": data}, 200

def _mk_app_error_return(messages: Any) -> tuple :
    errorMessages = None
    if isinstance(messages,str):
        errorMessages = (messages,)
    elif isinstance(messages,list) or isinstance(messages,tuple) or isinstance(messages,set):
        errorMessages = messages
    elif messages is not None:
        errorMessages = (str(messages),)
    return {"success": False, "errors": errorMessages}, 422

def _mk_not_found_return() -> tuple :
    return {"success": False, "errors": ["No record found"]}, 404

def _mk_validation_error_return(ve: ValidationError) -> tuple:
    error_messages = []
    for fld,errors in ve.normalized_messages().items():
        msg = f"{fld} - {' '.join(errors)}"
        error_messages.append(msg)
    return _mk_app_error_return(error_messages)

def _get_request_data() -> dict:
    return request.json if request.is_json else request.form

@app.route("/test", methods=['POST'])
def test1():
    if request.is_json:
        app.logger.info(f"json: {type(request.json)} {request.json}, form: {request.form}, args: {request.args}")
    else:
        app.logger.info(f"form: {request.form}, args: {request.args}")
    return "whatever"

@app.route("/container_types")
def get_container_types():
    data = controller.get_container_types()
    return _mk_success_return(data)

@app.route("/lots")
def get_lots():
    data = controller.get_lots()
    return _mk_success_return(data)

@app.route("/containers/<container_type>")
@app.route("/containers/<container_type>/<limit>")
def get_containers(container_type, limit=10):
    data = controller.get_containers_by_type(container_type, limit)
    if data:
        return _mk_success_return(data)
    return _mk_not_found_return()

@app.route("/container_by_barcode")
def get_container_by_barcode():
    barcode = request.args.get("barcode")
    barcode = barcode.strip() if barcode else barcode
    if barcode:
        data = controller.get_container_by_barcode(barcode)
        if data is None:
            ret_val =  _mk_not_found_return()
        else:
            ret_val = _mk_success_return(data)
    else:
        ret_val = _mk_app_error_return("Barcode must be supplied")
    return ret_val

@app.route("/container/<id>")
def get_container(id:int):
    data = controller.get_container(id)
    if data is None:
        return _mk_not_found_return()
    return _mk_success_return(data)

@app.route("/container", methods=['POST'])
@app.route("/container/", methods=['POST'])
def add_container():
    try:
        schema = SampleContainer_schema()
        container_data = schema.to_model(_get_request_data())
        print(container_data)
        cntr = controller.add_container(container_data)
    except ValidationError as ve:
        return _mk_validation_error_return(ve)
    except controller.ApplicationException as appExc:
        return _mk_app_error_return(appExc.message)

    return _mk_success_return(cntr)

@app.route("/container/<id>", methods=['PUT'])
def update_container(id: int):
    try:
        schema = SampleContainer_schema()
        container_data = schema.to_model(_get_request_data())
        container_data.id = id
        print(container_data)
        cntr = controller.update_container(container_data)
    except ValidationError as ve:
        return _mk_validation_error_return(ve)
    except controller.ApplicationException as appExc:
        return _mk_app_error_return(appExc.message)
    if cntr is None:
        return _mk_not_found_return()
    return _mk_success_return(cntr)

@app.route("/container/<id>", methods=['DELETE'])
def delete_container(id: int):
    try:
        cntr = controller.delete_container(id)
    except ValidationError as ve:
        return _mk_validation_error_return(ve)
    except controller.ApplicationException as appExc:
        return _mk_app_error_return(appExc.message)
    if cntr is None:
        return _mk_not_found_return()
    return _mk_success_return(cntr)

@app.route("/locate_container", methods=['PUT'])
@app.route("/locate_container/", methods=['PUT'])
def locate_container():
    try:
        schema = LocateContainer_schema()
        locate_data = schema.to_model(_get_request_data())
        cntr = controller.locate_container(locate_data)
    except ValidationError as ve:
        return _mk_validation_error_return(ve)
    except controller.ApplicationException as appExc:
        return _mk_app_error_return(appExc.message)
    return _mk_success_return(cntr)

@app.route("/pick_list", methods=['POST'])
@app.route("/pick_list/", methods=['POST'])
def gemerate_pick_list():
    try:
        print(f"request data {_get_request_data()}")
        schema = PickList_schema()
        models = schema.to_model(_get_request_data())
        print(f"pick list data {models}")
        data = controller.generate_pick_list(models)
        print(f"data {data}")
    except ValidationError as ve:
        return _mk_validation_error_return(ve)
    except controller.ApplicationException as appExc:
        return _mk_app_error_return(appExc.message)
    return _mk_success_return(data)
