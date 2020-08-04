import logging

from json import dumps
from flask import Request

import events.auth as auth
import events.instruction_documents as instruct
from events.core import EventHandler


ENDPOINT_MAPPING = {
    'auth.authenticate': auth.TokenAuthEventHandler,
    'auth.register_user': auth.RegisterUserEventHandler,
    'auth.delete_user': auth.DeleteUserEventHandler,
    'auth.get_user_data': auth.GetUserDataEventHandler,

    'instruction_document.add_doc': instruct.AddInstructionDocumentEventHandler,
    'instruction_document.delete_doc': instruct.DeleteInstructionDocumentEventHandler,
    'instruction_document.update_doc': instruct.UpdateInstructionDocumentEventHandler,

    'instruction_document.add_page': instruct.AddInstructionDocumentPageEventHandler,
    'instruction_document.update_page': instruct.UpdateInstructionDocumentPageEventHandler,
    'instruction_document.delete_page': instruct.DeleteInstructionDocumentPageEventHandler,
    'instruction_document.list_docs': instruct.ListInstructionDocumentEventHandler,
    'instruction_document.search_docs': instruct.SearchInstructionDocumentEventHandler,
    'instruction_document.get_doc': instruct.GetInstructionDocumentEventHandler
}


def event_handler_for(request: Request) -> EventHandler:
    """ factory function - get EventHanlder based on request.endpoint """
    # todo: magic from endpoint name to instantiate handler class (keep note snippet)
    logging.debug(f'@{request.endpoint}')
    logging.debug(f'request -> {dumps(request.json)}')
    handler = ENDPOINT_MAPPING.get(request.endpoint, None)
    if not handler: raise NotImplementedError(f'endpoint: {request.endpoint} handler not implemented')
    return handler(request)
