from flask import Request
from flask_jwt_extended import get_jwt_identity

from db.model import db, User, InstructionDocument
from events.core import EventHandler, EventValidator
from events.validators import MaxLen, MinLen
from utils.http import JsonResponse, ok_response


class AddInstructionDocumentEventValidator(EventValidator):
    def __init__(self, request: Request):
        super().__init__([
            MinLen(field_name='name', min_len=3, value=request.json.get('name', None)),
            MaxLen(field_name='name', max_len=200, value=request.json.get('name', None)),
            MinLen(field_name='description', min_len=1, value=request.json.get('name', None), optional=True),
            MaxLen(field_name='description', max_len=500, value=request.json.get('name', None), optional=True),
        ])


class AddInstructionDocumentEventHandler(EventHandler):
    def __init__(self, request: Request):
        super().__init__(request, AddInstructionDocumentEventValidator(request))

    def get_response(self) -> JsonResponse:
        document = self.__create_document()
        return ok_response(document.as_dict())

    def __create_document(self):
        # todo: ! from repo
        pass
        # user = get_object(User, id=get_jwt_identity()['id'])
        # new_document = InstructionDocument(
        #     created_by=user,
        #     name=self.request.json['name'].strip(),
        #     description=self.request.json.get('description', None)
        # )
        # db.session.add(new_document)
        # db.session.commit()
        # return new_document
