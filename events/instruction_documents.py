from flask import Request
from flask_jwt_extended import get_jwt_identity

from db.model import User, InstructionDocument
from db.serializers import InstructionDocumentSerializer
from events.core import EventHandler, EventValidator
from events.validators import MaxLen, MinLen, IsRequired, ObjectExist
from repository.repos import UserRepository, InstructionDocumentRepository
from utils.http import JsonResponse, ok_response


class AddInstructionDocumentEventValidator(EventValidator):
    def __init__(self, request: Request):
        super().__init__([
            MinLen(field_name='name', min_len=3, value=request.json.get('name', None)),
            MaxLen(field_name='name', max_len=200, value=request.json.get('name', None)),
            MinLen(field_name='description', min_len=1, value=request.json.get('name', None), optional=True),
            MaxLen(field_name='description', max_len=500, value=request.json.get('name', None), optional=True)
        ])


class AddInstructionDocumentEventHandler(EventHandler):
    def __init__(self, request: Request):
        super().__init__(request, AddInstructionDocumentEventValidator(request))

    def get_response(self) -> JsonResponse:
        user: User = UserRepository().get(get_jwt_identity()['id'])
        document = InstructionDocument(
            created_by=user,
            name=self.request.json['name'].strip(),
            description=self.request.json.get('description', None)
        )
        InstructionDocumentRepository().save(document)

        serializer = InstructionDocumentSerializer(document)
        return ok_response(serializer.data)


class DeleteInstructionDocumentEventValidator(EventValidator):
    def __init__(self, request: Request):
        super().__init__([
            IsRequired(field_name='document_id', value=request.json.get('document_id', None)),
            ObjectExist(
                field_name='document_id',
                repository_class=InstructionDocumentRepository,
                object_id=request.json.get('document_id', None)
            )
        ])


class DeleteInstructionDocumentEventHandler(EventHandler):
    def __init__(self, request: Request):
        super().__init__(request, DeleteInstructionDocumentEventValidator(request))

    def get_response(self) -> JsonResponse:
        InstructionDocumentRepository().delete(self.request.json['document_id'])
        return ok_response()
