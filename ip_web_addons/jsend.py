import traceback
from functools import wraps
import json

"""
A simple implementation of the jsend standard. See:
http://labs.omniti.com/labs/jsend
"""

def jsend_success(data):
    """ 
    Used when everything was fine with the call.
    @return json: {status: "success", data: data} 
    """
    assert isinstance(data, dict), 'data must be a dictionary'
    return json.dumps({"status": "success", "data": data})

def jsend_fail(data):
    """
    Used when there was a problem with the request's data or some state wasn't satisfied.
    Data should be a dictionary of error messages usually keyed by field names.
    @return json: {status: "fail", data: data}
    """
    assert isinstance(data, dict), 'data must be a dictionary'
    return json.dumps({"status": "fail", "data": data})

def jsend_error(message, code=None, data=None):
    """
    Used when there was an exception during a valid API call.
    @param message: A human readable error message
    @param code: A numeric error code
    @param data: a dict containing any other error information for example stack traces
    @return json: {status: "error", message: message, <code: code, data: data>}
    """
    assert isinstance(message, (str, unicode)), 'message must be a string or unicode'
    if data:
        assert isinstance(data, dict), 'data must be None or a dictionary'
    if code:
        assert isinstance(code, (int, float)), 'code must be None or numeric (int or float)'
    res = {"status": "error", "message": message}
    if code:
        res["code"] = code
    if data:
        res["data"] = data
    return json.dumps(res)

def jsend_error_catcher(func):
    """
    Wrapper for json ajax routes.
    It will convert JsendValueError and JsendTypeError exceptions into jsend_fail 
    It will catch any uncaught exceptions and return a jsend_error.
    If the route returns nothing, it will return an jsend_success with an empty data dict.
    """
    @wraps(func)
    def wrapped(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
            return res or jsend_success({})
        except JsendValueError as e:
            return jsend_fail({e.field_name: e.message})
        except JsendTypeError as e:
            return jsend_fail({e.field_name: e.message})
        except Exception as e:
            print traceback.format_exc()
            data = {
                "type": type(e).__name__,
                "message": unicode(e),
                "stack_trace": traceback.format_exc(), 
            }
            return jsend_error("An error occured", data=data)

    return wrapped

class JsendValueError(ValueError):
    """ 
    Raise this instead of a value error while inside a route marked with the jsend_error_catcher decorator
    and the field and message parameters will be used to generate a jsend_fail response 
    """
    def __init__(self, field_name, message):
        super(JsendValueError, self).__init__(message)
        self.field_name = field_name

class JsendTypeError(JsendValueError):
    """ 
    Raise this instead of a type error while inside a route marked with the jsend_error_catcher decorator
    and the field and message parameters will be used to generate a jsend_fail response 
    """
    pass

class FailCheck(object):
    """ Used to return a jsend_fail with multiple errors all at once """
    def __init__(self):
        super(FailCheck, self).__init__()
        self.fails = {}
    
    def add(self, field, description):
        self.fails[field] = description
        
    def failed(self):
        return bool(self.fails)
        
    def fail(self):
        if(self.failed()):
            return jsend_fail(self.fails)
