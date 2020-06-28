from flask import request, Blueprint

from events.factorys import event_handler_for
from events.instruction_documents import AddInstructionDocumentEventHandler, DeleteInstructionDocumentEventHandler
from utils.http import error_response
from utils.permissions import restricted

instruction_document_blueprint = Blueprint('instruction_document', __name__)


@instruction_document_blueprint.errorhandler(Exception)
def handle_error(error: Exception):
    return error_response(error)


# noinspection PyTypeChecker
@instruction_document_blueprint.route('/add-doc', methods=('POST',))
@restricted(['ADMIN'])
def add_doc():
    """ Create new instruction document """
    handler: AddInstructionDocumentEventHandler = event_handler_for(request)
    return handler.get_response()


# noinspection PyTypeChecker
@instruction_document_blueprint.route('/delete-doc', methods=('POST',))
@restricted(['ADMIN'])
def delete_doc():
    """ Delete instruction document """
    handler: DeleteInstructionDocumentEventHandler = event_handler_for(request)
    return handler.get_response()
