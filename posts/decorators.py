import json
from functools import wraps

from flask import request, Response

def accept(mimetype):
    def decorator(func):
        """
        Decorator which returns a 406 Not Acceptable if the client
        will not accept a certain mimetype
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if supplied mimetype is in the Accept header
            # If yes, continue the route as usual
            if mimetype in request.accept_mimetypes:
                return func(*args, **kwargs)
            # If no, then a response with JSON message and 406 status code is sent
            message = "Request must accept {} data".format(mimetype)
            data = json.dumps({"message": message})
            return Response(data, 406, mimetype="application/json")
        return wrapper
    return decorator