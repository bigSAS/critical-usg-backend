from flask import Request

from events.auth import TokenAuthEventHanlder
from events.core import EventHandler

ENDPOINT_MAPPING = {
    'auth.authenticate': TokenAuthEventHanlder
}


def event_handler_for(request: Request) -> EventHandler:
    """ factory function - get handler based on endpoint """
    handler = ENDPOINT_MAPPING.get(request.endpoint, None)
    if not handler: raise NotImplementedError(f'endpoint: {request.endpoint} handler not implemented')
    return handler(request)
