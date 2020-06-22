from flask import Request

from events.auth import TokenAuthEventHandler, RegisterUserEventHandler
from events.core import EventHandler
from events.instruction_documents import AddInstructionDocumentEventHandler

ENDPOINT_MAPPING = {
    'auth.authenticate': TokenAuthEventHandler,
    'auth.register': RegisterUserEventHandler,
    'instruction_document.add_doc': AddInstructionDocumentEventHandler
}


def event_handler_for(request: Request) -> EventHandler:
    """ factory function - get EventHanlder based on request.endpoint """
    handler = ENDPOINT_MAPPING.get(request.endpoint, None)
    if not handler: raise NotImplementedError(f'endpoint: {request.endpoint} handler not implemented')
    return handler(request)
