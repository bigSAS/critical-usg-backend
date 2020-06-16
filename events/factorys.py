from flask import Request

from events.auth import TokenAuthEventHanlder, RegisterUserEventHanlder
from events.core import EventHandler

ENDPOINT_MAPPING = {
    'auth.authenticate': TokenAuthEventHanlder,
    'auth.register': RegisterUserEventHanlder
}


def event_handler_for(request: Request) -> EventHandler:
    """ factory function - get EventHanlder based on request.endpoint """
    handler = ENDPOINT_MAPPING.get(request.endpoint, None)
    if not handler: raise NotImplementedError(f'endpoint: {request.endpoint} handler not implemented')
    return handler(request)
