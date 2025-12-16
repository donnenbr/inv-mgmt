# posting json data : curl -H "Content-Type: application/json" --request POST -d '{"first":"bob","age":65}' localhost:5000/test
# posting form data :

# from typing import Any
# from flask import request, abort
from marshmallow.exceptions import ValidationError

from invmgmt import app
import invmgmt.controller as controller

from invmgmt.form_models import SampleContainer_schema, LocateContainer_schema, PickList_schema

# import * will not work because these are NOT public functions (for now).  we must import them
# explicitly
from invmgmt.views.utils import _mk_success_return, _mk_app_error_return, _mk_not_found_return, \
    _mk_validation_error_return, _get_request_data

@app.route("/pick_list", methods=['POST'])
@app.route("/pick_list/", methods=['POST'])
def generate_pick_list():
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
