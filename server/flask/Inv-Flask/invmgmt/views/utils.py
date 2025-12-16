from typing import Any
from flask import request
from marshmallow.exceptions import ValidationError

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

