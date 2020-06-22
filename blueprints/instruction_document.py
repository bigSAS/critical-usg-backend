from flask import request, Blueprint

from events.factorys import event_handler_for
from events.instruction_documents import AddInstructionDocumentEventHandler
from utils.permissions import restricted

instruction_document_blueprint = Blueprint('instruction_document', __name__)


# noinspection PyTypeChecker
@instruction_document_blueprint.route('/add-doc', methods=('POST',))
@restricted('ADMIN')
def add_doc():
    """ Create new instruction document """
    handler: AddInstructionDocumentEventHandler = event_handler_for(request)
    return handler.get_response()
