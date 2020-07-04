from flask import Request

from events.auth import TokenAuthEventHandler, RegisterUserEventHandler, DeleteUserEventHandler
from events.core import EventHandler
from events.instruction_documents import AddInstructionDocumentEventHandler, DeleteInstructionDocumentEventHandler, \
    UpdateInstructionDocumentEventHandler, AddInstructionDocumentPageEventHandler, \
    UpdateInstructionDocumentPageEventHandler, DeleteInstructionDocumentPageEventHandler, \
    ListInstructionDocumentEventHandler, SearchInstructionDocumentEventHandler, GetInstructionDocumentEventHandler

ENDPOINT_MAPPING = {
    'auth.authenticate': TokenAuthEventHandler,
    'auth.register_user': RegisterUserEventHandler,
    'auth.delete_user': DeleteUserEventHandler,

    'instruction_document.add_doc': AddInstructionDocumentEventHandler,
    'instruction_document.delete_doc': DeleteInstructionDocumentEventHandler,
    'instruction_document.update_doc': UpdateInstructionDocumentEventHandler,

    'instruction_document.add_page': AddInstructionDocumentPageEventHandler,
    'instruction_document.update_page': UpdateInstructionDocumentPageEventHandler,
    'instruction_document.delete_page': DeleteInstructionDocumentPageEventHandler,
    'instruction_document.list_docs': ListInstructionDocumentEventHandler,
    'instruction_document.search_docs': SearchInstructionDocumentEventHandler,
    'instruction_document.get_doc': GetInstructionDocumentEventHandler
}


def event_handler_for(request: Request) -> EventHandler:
    """ factory function - get EventHanlder based on request.endpoint """
    handler = ENDPOINT_MAPPING.get(request.endpoint, None)
    if not handler: raise NotImplementedError(f'endpoint: {request.endpoint} handler not implemented')
    return handler(request)
