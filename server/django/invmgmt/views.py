from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed, \
    HttpResponseBadRequest, HttpResponseNotFound, HttpResponseForbidden
from http import HTTPStatus

from typing import Any
import json

from .controller import ApplicationException # just to make life easier
# for the methods, so there are no name conflicts with methods in this module
from . import controller
from .forms import SampleContainerForm, LocateContainerForm, PickListForm

from django.contrib.auth import authenticate, login
from django.shortcuts import redirect

# NOTE - NOT needed to get the csrf cookie
# the authenticate works, but the redirect does not.  would need to find a way to do a "next()"
# after the login succeeds
def app_login(request):
    print(f"*** request type {request.method}")
    print(f"*** POST {request.POST}")
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect("http://localhost:4200")
    else:
        return HttpResponse("Login failed", status=HTTPStatus.FORBIDDEN)
        
# sample security check
def secure(func=None, roles: dict = None):
    role_methods = {
        'admin': ['GET','PUT', 'POST', 'DELETE'],
        'manager': ['GET', 'PUT', 'POST'],
        'reader': ['GET']
    }
    def allow_access(request, roles):
        # no roles - fully open
        if not roles:
            return True
        # at this point we'd need to determine the caller's role and whether they can access the method.
        return False
        
    def decorator_func(func):
        def call_func(*args, **kwargs):
            print("*** security check now ...");
            print(f"*** roles {roles}")
            request = args[0]
            print(f"*** request method {request.method}")
            if allow_access(request, roles):
                return func(*args, **kwargs);
            else:
                return HttpResponseForbidden("Security failure");
            
        return call_func
        
    if func is None:
        return decorator_func
    return decorator_func(func)
        

def _get_request_data(request) -> dict|list|None:
    # content type from angular is application/json
    # print(f"*** content type {request.content_type}")
    # print(f"*** body [{request.body}]")
    body = request.body.strip() if request.body else request.body
    data = None
    if body:
        # if body.startswith(b'{') or body.startswith(b'['):
        if request.content_type == 'application/json':
            # looks like json.  content type is application/x-www-form-urlencoded from curl
            # could also be application/json
            data = json.loads(request.body)
        # elif body.startswith(b'--------------------------'):
        elif request.content_type == 'multipart/form-data':
            # form data.  content type is multipart/form-data from curl and postman
            data = request.POST.dict()
    return data

def _mk_success_return(data: Any) -> JsonResponse :
    return JsonResponse({"success": True, "data": data, "errors": None})

def _mk_app_error_return(messages: Any) -> HttpResponseBadRequest :
    errorMessages = None
    if isinstance(messages,str):
        errorMessages = (messages,)
    elif isinstance(messages,list) or isinstance(messages,tuple) or isinstance(messages,set):
        errorMessages = messages
    elif messages is not None:
        errorMessages = (str(messages),)
    # return HttpResponseBadRequest(errorMessages)
    return JsonResponse({"success":False, "errors":errorMessages}, status=HTTPStatus.BAD_REQUEST)

def _mk_not_found_return() -> HttpResponseNotFound :
    return HttpResponseNotFound("No record found")

@secure(roles=['admin','manager','reader'])
# @secure()
def reagents(request):
    if (request.method == 'GET'):
        s = request.GET.get("limit", '100')
        try:
            limit = int(s)
            if (limit < 1):
                raise ApplicationException("Limit must be > 0")
            reagents = controller.get_reagents(limit)
        except ApplicationException as app_exc:
            return _mk_app_error_return(app_exc.message)
        except ValueError as ve:
            return _mk_app_error_return("Limit must be an int value > 0")

        return _mk_success_return(reagents)
    else:
        return HttpResponseNotAllowed(['GET'], "Method not allowed")

def lots(request):
    if (request.method == 'GET'):
        s = request.GET.get("limit", '100')
        try:
            limit = int(s)
            if (limit < 1):
                raise ApplicationException("Limit must be > 0")
            lots = controller.get_lots(limit)
        except ApplicationException as app_exc:
            return _mk_app_error_return(app_exc.message)
        except ValueError as ve:
            return _mk_app_error_return("Limit must be an int value > 0")
        return _mk_success_return(lots)
    return HttpResponseNotAllowed(['GET'], "Method not allowed")

def container_type(request):
    if (request.method == 'GET'):
        cntr_types = controller.get_container_types()
        return JsonResponse({"success":True, "data":cntr_types, "errors":None})
    return HttpResponseNotAllowed(['GET'], "Method not allowed")

def container_by_barcode(request):
    if (request.method == 'GET'):
        try:
            barcode = request.GET.get("barcode")
            if barcode:
                barcode = barcode.strip()
            if not barcode:
                raise ApplicationException("Barcode must be supplied")
            cntr = controller.get_container_by_barcode(barcode)
            if cntr is None:
                return _mk_not_found_return()
        except ApplicationException as app_exc:
            return _mk_app_error_return(app_exc.message)
        return _mk_success_return(cntr)
    return HttpResponseNotAllowed(['GET'], "Method not allowed")

def container(request, id):
    if (request.method == 'GET'):
        cntr = controller.get_container_by_id(id)
        if cntr is None:
            return _mk_not_found_return()
        return _mk_success_return(cntr)
    elif(request.method == 'PUT'):
        data = _get_request_data(request)
        if data:
            frm = SampleContainerForm(data)
            if frm.is_valid():
                try:
                    cntr = controller.update_container(id, frm)
                    if cntr is None:
                        return _mk_not_found_return()
                except ApplicationException as app_exc:
                    return _mk_app_error_return(app_exc.message)
                return _mk_success_return(cntr)
            return _mk_app_error_return(frm.get_errors())
        return _mk_app_error_return("No request body")
    elif (request.method == 'DELETE'):
        try:
            cntr = controller.delete_container(id)
            if cntr is None:
                return _mk_not_found_return()
        except ApplicationException as app_exc:
            return _mk_app_error_return(app_exc.message)
        return _mk_success_return(cntr)

    return HttpResponseNotAllowed(['GET','PUT','DELETE'], "Method not allowed")

def add_container(request):
    if (request.method == 'POST'):
        data = _get_request_data(request)
        print(f"data {data}")
        if data:
            frm = SampleContainerForm(data)
            print(f"form valid {frm.is_valid()}")
            if frm.is_valid():
                try:
                    cntr = controller.add_new_container(frm)
                except ApplicationException as app_exc:
                    print(f"app error {app_exc}")
                    return _mk_app_error_return(app_exc.message)
                return _mk_success_return(cntr)
            return _mk_app_error_return(frm.get_errors())
        return _mk_app_error_return("No request body")

    return HttpResponseNotAllowed(['POST'], "Method not allowed")

def locate_container(request):
    if (request.method == 'PUT'):
        data = _get_request_data(request)
        if data:
            frm = LocateContainerForm(data)
            if frm.is_valid():
                try:
                    cntr = controller.locate_container(frm)
                except ApplicationException as app_exc:
                    return _mk_app_error_return(app_exc.message)
                return _mk_success_return(cntr)
            return _mk_app_error_return(frm.get_errors())
        return _mk_app_error_return("No request body")

    return HttpResponseNotAllowed(['PUT'], "Method not allowed")

def pick_list(request):
    if (request.method == 'POST'):
        data = _get_request_data(request)
        if data:
            if not isinstance(data,list):
                return _mk_app_error_return("Data must be a list")
            form_list = [ PickListForm(row) for row in data ]
            form_errors = []
            for frm in form_list:
                if not frm.is_valid():
                    form_errors.append(frm.get_errors())
            if form_errors:
                return _mk_app_error_return(form_errors)
            # all forms are valid
            try:
                pick_list_data = controller.generate_pick_list(form_list)
            except ApplicationException as app_exc:
                return _mk_app_error_return(app_exc.message)
            return _mk_success_return(pick_list_data)
        return _mk_app_error_return("No request body")

    return HttpResponseNotAllowed(['POST'], "Method not allowed")

def reagent_search(request):
    if (request.method == 'GET'):
        try:
            min_mw = request.GET.get("min_mw","").strip()
            if not min_mw:
                raise ApplicationException("Minimum MW must be supplied")
            max_mw = request.GET.get("max_mw", "").strip()
            if not max_mw:
                raise ApplicationException("Maximum MW must be supplied")
            # just a proof of concept, so we'll just convert
            min_mw,max_mw = int(min_mw),int(max_mw)
            return _mk_success_return(controller.reagent_search(min_mw,max_mw))
        except ApplicationException as app_exc:
            return _mk_app_error_return(app_exc.message)
    return HttpResponseNotAllowed(['GET'], "Method not allowed")
