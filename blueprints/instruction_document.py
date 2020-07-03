from flask import request, Blueprint

from events.factorys import event_handler_for
from utils.http import error_response
from utils.permissions import restricted

instruction_document_blueprint = Blueprint('instruction_document', __name__)


@instruction_document_blueprint.errorhandler(Exception)
def handle_error(error: Exception):
    return error_response(error)


@instruction_document_blueprint.route('/add-doc', methods=('POST',))
@restricted(['ADMIN'])
def add_doc():
    """ Create new instruction document """
    return event_handler_for(request).get_response()


@instruction_document_blueprint.route('/delete-doc', methods=('POST',))
@restricted(['ADMIN'])
def delete_doc():
    """ Delete instruction document """
    return event_handler_for(request).get_response()


@instruction_document_blueprint.route('/update-doc', methods=('POST',))
@restricted(['ADMIN'])
def update_doc():
    """ Update instruction document """
    return event_handler_for(request).get_response()


@instruction_document_blueprint.route('/add-page', methods=('POST',))
@restricted(['ADMIN'])
def add_page():
    """ Create new instruction document page """
    return event_handler_for(request).get_response()


@instruction_document_blueprint.route('/update-page', methods=('POST',))
@restricted(['ADMIN'])
def update_page():
    """ Update instruction document page """
    return event_handler_for(request).get_response()


@instruction_document_blueprint.route('/delete-page', methods=('POST',))
@restricted(['ADMIN'])
def delete_page():
    """ Delete instruction document page """
    return event_handler_for(request).get_response()
