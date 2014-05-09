from functools import wraps
import jsend

from openerp import SUPERUSER_ID
from openerp.addons.web.http import request

def _is_logged_in():
    """ Returns True if the user is logged in (i.e. not the public user) otherwise False """
    cr, uid, pool = request.cr, request.uid, request.registry
    public_user_id = pool['website'].get_public_user(cr, SUPERUSER_ID)
    if uid == public_user_id:
        return False
    else:
        return True

def require_login(func):
    """
    Wrapper for OpenERP routes to require that the user is logged in
    """
    @wraps(func)
    def wrapped(*args, **kwargs):
        if not _is_logged_in():
            return request.redirect("/web/login?redirect=/account/")
        else:
            return func(*args, **kwargs)
    return wrapped

def require_login_jsend(func):
    """
    Wrapper for OpenERP JSEND routes to require that the user is logged in. If they are not,
    jsend_fail will be returned
    """
    @wraps(func)
    def wrapped(*args, **kwargs):
        if not _is_logged_in():
            return jsend.jsend_fail({'login': 'The user is not logged in'})
        else:
            return func(*args, **kwargs)
    return wrapped

def isnumeric(val):
    """ Tests if a value is numeric and returns True or False accordingly """
    if isinstance(val, (int, float)):
        return True
    elif isinstance(val, (str, unicode)):
        try:
            float(val)
            return True
        except ValueError:
            return False
