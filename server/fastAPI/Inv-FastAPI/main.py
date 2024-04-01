from typing import Any

from fastapi import FastAPI, Response, status
from fastapi.exceptions import RequestValidationError, ValidationException
from fastapi.responses import PlainTextResponse, JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from form_models import *
import config
import controller

#
# IMPORTANT NOTE!!!
# you can have uvicorn send back response headers by specifying --header TEXT  (name:value)
# when you start uvicorn.  How cool!!!
#

engine = create_engine(config.db_url, echo=False)
session = Session(engine)

app = FastAPI()
    
def mk_success_return(data: Any):
    return {"success": True, "data": data}

def mk_app_error_return(response: Response=None, messages: Any=None):
    errorMessages = None
    if isinstance(messages,str):
        errorMessages = (messages,)
    elif isinstance(messages,list) or isinstance(messages,tuple) or isinstance(messages,set):
        errorMessages = messages
    elif messages is not None:
        errorMessages = (str(messages),)
    if response:
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    return {"success": False, "errors": errorMessages}

def mk_not_found_return(response: Response):
    response.status_code = status.HTTP_404_NOT_FOUND
    return {"success": False, "errors": ["No record found"]}

@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(request, exc):
    print(f"errors {exc.errors()}, body {exc.body}")
    # note the input data is exc.body()
    # extract the errors and put them into a list of error messages in the form of field - message
    errorMsgs = []
    for x in exc.errors():
        loc = x['loc']
        msg = x['msg']
        fld = loc[1] if loc[0] == 'body' else f"{loc[0]}.{loc[1]}"
        errorMsgs.append(f"{fld} - {msg}")
    d = mk_app_error_return(messages=errorMsgs)
    return JSONResponse(d, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

@app.get("/container_type")
async def get_container_type():
    cntrTypes = controller.get_container_type(session)
    return mk_success_return(cntrTypes)

@app.get("/containers_by_type")
async def get_containers_by_type(container_type:str, limit:int = 10):
    cntrs = controller.get_containers_by_type(session, container_type, limit)
    return mk_success_return(cntrs)

@app.get("/container_by_barcode", status_code=200)
async def get_container_by_barcode(barcode:str, response: Response):
    try:
        cntr = controller.get_container_by_barcode(session, barcode)
    except controller.ApplicationException as appExc:
        return mk_app_error_return(response, appExc.message)
    if cntr is None:
        return mk_not_found_return(response)
    return mk_success_return(cntr)

@app.get("/container/{container_id}", status_code=200)
async def get_container(container_id:int, response: Response):
    cntr = controller.get_container_by_id(session, container_id)
    if cntr is None:
        return mk_not_found_return(response)
    return mk_success_return(cntr)

# you can only add, update, and delete vials.  for update, you can only decrease the amount or increase the concentration.
# need a pydantic model for these:
#   container id (or barcode)
#   parent container id (or barcode)
#   position
#   lot name
#   amount and unit
#   concentration and units
@app.post("/container", status_code=200)
async def add_container(model: FormSampleContainer, response: Response):
    """
    add a new container (vial only) what the f*** did you think it did???
    :return:
    """
    print(f"model {model}")
    try:
        cntr = controller.add_container(session, model)
    except controller.ApplicationException as appExc:
        return mk_app_error_return(response, appExc.message)
    return mk_success_return(cntr)

@app.put("/container/{container_id}", status_code=200)
async def update_container(container_id: int, model: FormSampleContainer, response: Response):
    print(f"container id {container_id}, model {model}")
    model.id = container_id
    try:
        cntr = controller.update_container(session, model)
    except controller.ApplicationException as appExc:
        return mk_app_error_return(response, appExc.message)
    if cntr is None:
        return mk_not_found_return(response)
    return mk_success_return(cntr)

@app.delete("/container/{container_id}", status_code=200)
async def delete_container(container_id:int, response: Response):
    try:
        cntr = controller.delete_container(session, container_id)
    except controller.ApplicationException as appExc:
        return mk_app_error_return(response, appExc.message)
    if cntr is None:
        return mk_not_found_return(response)
    return mk_success_return(cntr)

# you can only locate vials.  parent container must be a rack
@app.put("/locate_container", status_code=200)
async def locate_container(model: FormLocateContainer, response: Response):
    # input container_id, parent_container_id, position
    # or barcodes for vial and rack, and position
    # new position must be unoccupied
    print(f"model {model}")
    try:
        cntr = controller.locate_container(session, model)
    except controller.ApplicationException as appExc:
        return mk_app_error_return(response, appExc.message)
    if cntr is None:
        return mk_not_found_return(response)
    return mk_success_return(cntr)

# maybe???
# to quote Prince, "let's go crazy!!!"
# create a pick list given a list of reagent, amount, and concentration.  one passes in a jason serialized
# list
# post because it must have a body
@app.post("/pick_list")
async def generate_pick_list(models: List[FormPickListItem],  response: Response):
    print(f"models {models}")
    try:
        data = controller.generate_pick_list(session, models)
        print(f"data {data}")
    except controller.ApplicationException as appExc:
        return mk_app_error_return(response, appExc.message)
    return mk_success_return(data)
