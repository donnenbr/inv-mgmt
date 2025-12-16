# posting json data : curl -H "Content-Type: application/json" --request POST -d '{"first":"bob","age":65}' localhost:5000/test
# posting form data :

# from typing import Any
from flask import request
# from marshmallow.exceptions import ValidationError

from invmgmt import app
import invmgmt.controller as controller

from invmgmt.form_models import SampleContainer_schema, LocateContainer_schema, PickList_schema

# import * will not work because these are NOT public functions (for now).  we must import them
# explicitly
from invmgmt.views.utils import _mk_success_return, _mk_app_error_return, _mk_not_found_return, \
    _mk_validation_error_return, _get_request_data

#####################################################################

@app.route("/test", methods=['POST'])
def test1():
    if request.is_json:
        app.logger.info(f"json: {type(request.json)} {request.json}, form: {request.form}, args: {request.args}")
    else:
        app.logger.info(f"form: {request.form}, args: {request.args}")
    return "whatever"

@app.route("/container_types")
def get_container_types():
    print("******* container types !!!")
    data = controller.get_container_types()
    return _mk_success_return(data)

@app.route("/lots")
def get_lots():
    limit = request.args.get("limit", "20")
    print(f"*** limit {limit}")
    limit = limit.strip() if limit else limit
    try:
        limit = int(limit)
        if limit <= 0:
            raise ValueError("Limit must be > 0")
        data = controller.get_lots(limit)
        return _mk_success_return(data)
    except Exception as ex:
        return _mk_app_error_return(ex)

