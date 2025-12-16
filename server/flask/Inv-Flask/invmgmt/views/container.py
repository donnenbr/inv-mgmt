# posting json data : curl -H "Content-Type: application/json" --request POST -d '{"first":"bob","age":65}' localhost:5000/test
# posting form data :

# from typing import Any
from flask import request
from marshmallow.exceptions import ValidationError

from invmgmt import app
import invmgmt.controller as controller

from invmgmt.form_models import SampleContainer_schema, LocateContainer_schema, PickList_schema

# import * will not work because these are NOT public functions (for now).  we must import them
# explicitly
from invmgmt.views.utils import _mk_success_return, _mk_app_error_return, _mk_not_found_return, \
    _mk_validation_error_return, _get_request_data

@app.route("/containers/<container_type>")
@app.route("/containers/<container_type>/<limit>")
def get_containers(container_type, limit=10):
    print(f"******* containers by type {container_type} {limit}")
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
        print("*** schema")
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
        container_data.id = int(id)
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

