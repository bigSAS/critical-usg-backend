from flask import Request
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import or_

from db.models import AddInstructionDocumentEventRequestModel, AddInstructionDocumentEventResponseModel
from db.schema import User, InstructionDocument, InstructionDocumentPage
from db.serializers import InstructionDocumentSerializer, InstructionDocumentPageSerializer, \
    ListInstructionDocumentSerializer, GetInstructionDocumentSerializer
from events.core import EventHandler, EventValidator
from events.validators import MaxLen, MinLen, IsRequired, ObjectExist
from repository.repos import UserRepository, InstructionDocumentRepository, InstructionDocumentPageRepository
from utils.http import JsonResponse, ok_response
from utils.managers import InstructionDocumentManager


# class AddInstructionDocumentEventValidator(EventValidator):
#     def __init__(self, request: Request):
#         super().__init__([
#             MinLen(field_name='name', min_len=3, value=request.json.get('name', None)),
#             MaxLen(field_name='name', max_len=200, value=request.json.get('name', None)),
#             MinLen(field_name='description', min_len=1, value=request.json.get('description', None), optional=True),
#             MaxLen(field_name='description', max_len=500, value=request.json.get('description', None), optional=True)
#         ])


class AddInstructionDocumentEventHandler(EventHandler):
    request_model_class = AddInstructionDocumentEventRequestModel
    # def __init__(self, request: Request):
    #     super().__init__(request, AddInstructionDocumentEventValidator(request))

    def get_response(self) -> JsonResponse:
        user: User = UserRepository().get(get_jwt_identity()['id'])
        doc = InstructionDocument(
            created_by=user,
            name=self.request.json['name'].strip(),
            description=self.request.json.get('description', None)
        )
        InstructionDocumentRepository().save(doc)

        # serializer = InstructionDocumentSerializer(doc)
        rmodel = AddInstructionDocumentEventResponseModel.from_orm(doc)
        return ok_response(rmodel)


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


class UpdateInstructionDocumentEventValidator(EventValidator):
    def __init__(self, request: Request):
        super().__init__([
            IsRequired(field_name='document_id', value=request.json.get('document_id', None)),
            ObjectExist(
                field_name='document_id',
                repository_class=InstructionDocumentRepository,
                object_id=request.json.get('document_id', None)
            ),
            MinLen(field_name='name', min_len=3, value=request.json.get('name', None)),
            MaxLen(field_name='name', max_len=200, value=request.json.get('name', None)),
            MinLen(field_name='description', min_len=1, value=request.json.get('description', None), optional=True),
            MaxLen(field_name='description', max_len=500, value=request.json.get('description', None), optional=True)
        ])


class UpdateInstructionDocumentEventHandler(EventHandler):
    def __init__(self, request: Request):
        super().__init__(request, UpdateInstructionDocumentEventValidator(request))

    def get_response(self) -> JsonResponse:
        user_id = get_jwt_identity()['id']
        doc_repo = InstructionDocumentRepository()
        doc: InstructionDocument = doc_repo.get(self.request.json['document_id'])
        managed_doc = InstructionDocumentManager(document=doc)
        managed_doc.update(
            user_id,
            name=self.request.json['name'],
            description=self.request.json.get('description', None)
        )
        serializer = InstructionDocumentSerializer(doc)
        return ok_response(serializer.data)


class AddInstructionDocumentPageEventValidator(EventValidator):
    def __init__(self, request: Request):
        super().__init__([
            IsRequired(field_name='document_id', value=request.json.get('document_id', None)),
            ObjectExist(
                field_name='document_id',
                repository_class=InstructionDocumentRepository,
                object_id=request.json.get('document_id', None)
            ),
        ])


class AddInstructionDocumentPageEventHandler(EventHandler):
    def __init__(self, request: Request):
        super().__init__(request, AddInstructionDocumentPageEventValidator(request))

    def get_response(self) -> JsonResponse:
        user_id = get_jwt_identity()['id']
        doc_id = self.request.json['document_id']
        page = InstructionDocumentPage(
            document_id=doc_id,
            json=self.request.json.get('json', None)
        )
        managed_doc = InstructionDocumentManager(document_id=doc_id)
        page = managed_doc.add_page(page, user_id)
        serializer = InstructionDocumentPageSerializer(page)
        return ok_response(serializer.data)


class UpdateInstructionDocumentPageEventValidator(EventValidator):
    def __init__(self, request: Request):
        super().__init__([
            IsRequired(field_name='page_id', value=request.json.get('page_id', None)),
            ObjectExist(
                field_name='page_id',
                repository_class=InstructionDocumentPageRepository,
                object_id=request.json.get('page_id', None)
            ),
        ])


class UpdateInstructionDocumentPageEventHandler(EventHandler):
    def __init__(self, request: Request):
        super().__init__(request, UpdateInstructionDocumentPageEventValidator(request))

    def get_response(self) -> JsonResponse:
        user_id = get_jwt_identity()['id']
        page_id = self.request.json['page_id']
        repo = InstructionDocumentPageRepository()

        page: InstructionDocumentPage = repo.get(page_id)
        page.json = self.request.json.get('json', None)
        repo.save(page)

        managed_doc = InstructionDocumentManager(document_id=page.document_id)
        managed_doc.update(user_id)
        serializer = InstructionDocumentPageSerializer(page)
        return ok_response(serializer.data)


class DeleteInstructionDocumentPageEventValidator(EventValidator):  # todo: duplicate ?
    def __init__(self, request: Request):
        super().__init__([
            IsRequired(field_name='page_id', value=request.json.get('page_id', None)),
            ObjectExist(
                field_name='page_id',
                repository_class=InstructionDocumentPageRepository,
                object_id=request.json.get('page_id', None)
            ),
        ])


class DeleteInstructionDocumentPageEventHandler(EventHandler):
    def __init__(self, request: Request):
        super().__init__(request, UpdateInstructionDocumentPageEventValidator(request))

    def get_response(self) -> JsonResponse:
        user_id = get_jwt_identity()['id']
        page_id = self.request.json['page_id']
        repo = InstructionDocumentPageRepository()

        page: InstructionDocumentPage = repo.get(page_id)
        managed_doc = InstructionDocumentManager(document_id=page.document_id)
        managed_doc.delete_page(user_id, page_num=page.page_num)
        return ok_response()


class ListInstructionDocumentEventValidator(EventValidator):
    def __init__(self, request: Request):
        super().__init__([
            IsRequired(field_name='page', value=request.json.get('page', None)),
            IsRequired(field_name='limit', value=request.json.get('limit', None)),
            # todo: min page, max limit validation
        ])


class ListInstructionDocumentEventHandler(EventHandler):
    def __init__(self, request: Request):
        super().__init__(request, ListInstructionDocumentEventValidator(request))

    def get_response(self) -> JsonResponse:
        docs_paginated = InstructionDocumentRepository() \
            .all_paginated(page=self.request.json['page'], limit=self.request.json['limit'])
        serializer = ListInstructionDocumentSerializer(docs_paginated)
        return ok_response(serializer.data)


class SearchInstructionDocumentEventValidator(EventValidator):
    def __init__(self, request: Request):
        super().__init__([
            MinLen(field_name='search', min_len=3, value=request.json.get('search', None)),
            MaxLen(field_name='search', max_len=100, value=request.json.get('search', None)),
            IsRequired(field_name='page', value=request.json.get('page', None)),
            IsRequired(field_name='limit', value=request.json.get('limit', None)),
            # todo: min page, max limit validation
        ])


class SearchInstructionDocumentEventHandler(EventHandler):
    def __init__(self, request: Request):
        super().__init__(request, SearchInstructionDocumentEventValidator(request))

    def get_response(self) -> JsonResponse:
        page = self.request.json['page']
        limit = self.request.json['limit']
        search = self.request.json['search'].lower()
        docs_paginated = InstructionDocumentRepository() \
            .filter_paginated(f=or_(InstructionDocument.name.ilike(f'%{search}%'),
                                    InstructionDocument.description.ilike(f'%{search}%')),
                              page=page,
                              limit=limit)
        serializer = ListInstructionDocumentSerializer(docs_paginated)
        return ok_response(serializer.data)


class GetInstructionDocumentEventValidator(EventValidator):
    def __init__(self, request: Request):
        super().__init__([
            IsRequired(field_name='document_id', value=request.json.get('document_id', None)),
            ObjectExist(
                field_name='document_id', repository_class=InstructionDocumentRepository,
                object_id=request.json.get('document_id', None)
            )
        ])


class GetInstructionDocumentEventHandler(EventHandler):
    def __init__(self, request: Request):
        super().__init__(request, GetInstructionDocumentEventValidator(request))

    def get_response(self) -> JsonResponse:
        doc = InstructionDocumentRepository().get(self.request.json['document_id'])
        serializer = GetInstructionDocumentSerializer(doc)
        return ok_response(serializer.data)
