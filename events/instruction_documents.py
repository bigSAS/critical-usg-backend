from flask import Request
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import or_

from db.models import AddInstructionDocumentEventRequestModel, AddInstructionDocumentEventResponseDataModel, \
    DeleteInstructionDocumentEventRequestModel, UpdateInstructionDocumentEventRequestModel, \
    UpdateInstructionDocumentEventResponseDataModel, AddInstructionDocumentPageEventRequestModel, \
    AddInstructionDocumentPageEventResponseDataModel, UpdateInstructionDocumentPageEventRequestModel, \
    UpdateInstructionDocumentPageEventResponseDataModel, DeleteInstructionDocumentPageEventRequestModel, \
    ListInstructionDocumentEventRequestModel, ListInstructionDocumentEventResponseDataModel, \
    SearchInstructionDocumentEventResponseDataModel, SearchInstructionDocumentEventRequestModel, \
    GetInstructionDocumentEventRequestModel, GetInstructionDocumentEventResponsedataModel, \
    InstructionDocumentEntityModel, InstructionDocumentPageEntityModel
from db.schema import User, InstructionDocument, InstructionDocumentPage
from db.serializers import InstructionDocumentPageSerializer, \
    ListInstructionDocumentSerializer, GetInstructionDocumentSerializer
from events.core import EventHandler, EventValidator
from events.validators import MaxLen, MinLen, IsRequired, ObjectExist
from repository.repos import UserRepository, InstructionDocumentRepository, InstructionDocumentPageRepository
from utils.http import JsonResponse, ok_response
from utils.managers import InstructionDocumentManager


# todo: review 3x ;)
class AddInstructionDocumentEventHandler(EventHandler):
    request_model_class = AddInstructionDocumentEventRequestModel

    def get_response(self) -> JsonResponse:
        user: User = UserRepository().get(get_jwt_identity()['id'])
        doc = InstructionDocument(
            created_by=user,
            name=self.request.json['name'].strip(),
            description=self.request.json.get('description', None)
        )
        InstructionDocumentRepository().save(doc)
        return ok_response(AddInstructionDocumentEventResponseDataModel.from_orm(doc))


class DeleteInstructionDocumentEventHandler(EventHandler):
    request_model_class = DeleteInstructionDocumentEventRequestModel

    def get_response(self) -> JsonResponse:
        InstructionDocumentRepository().delete(self.request.json['document_id'])
        return ok_response()


class UpdateInstructionDocumentEventHandler(EventHandler):
    request_model_class = UpdateInstructionDocumentEventRequestModel

    def get_response(self) -> JsonResponse:
        rdoc: UpdateInstructionDocumentEventRequestModel = self.request_model
        managed_doc = InstructionDocumentManager(document_id=rdoc.document_id)
        managed_doc.update(
            get_jwt_identity()['id'],
            name=rdoc.name,
            description=rdoc.description
        )
        return ok_response(UpdateInstructionDocumentEventResponseDataModel.from_orm(managed_doc.document))


class AddInstructionDocumentPageEventHandler(EventHandler):
    request_model_class = AddInstructionDocumentPageEventRequestModel

    def get_response(self) -> JsonResponse:
        rmodel: AddInstructionDocumentPageEventRequestModel = self.request_model
        user_id = get_jwt_identity()['id']
        page = InstructionDocumentPage(
            document_id=rmodel.document_id,
            json_data=rmodel.json_data
        )
        managed_doc = InstructionDocumentManager(document_id=rmodel.document_id)
        page = managed_doc.add_page(page, user_id)
        return ok_response(AddInstructionDocumentPageEventResponseDataModel.from_orm(page))


class UpdateInstructionDocumentPageEventHandler(EventHandler):
    request_model_class = UpdateInstructionDocumentPageEventRequestModel

    def get_response(self) -> JsonResponse:
        user_id = get_jwt_identity()['id']
        rmodel: UpdateInstructionDocumentPageEventRequestModel = self.request_model

        repo = InstructionDocumentPageRepository()
        page: InstructionDocumentPage = repo.get(rmodel.page_id)
        page.json_data = rmodel.json_data
        repo.save(page)

        managed_doc = InstructionDocumentManager(document_id=page.document_id)
        managed_doc.update(user_id)
        return ok_response(UpdateInstructionDocumentPageEventResponseDataModel.from_orm(page))


class DeleteInstructionDocumentPageEventHandler(EventHandler):
    request_model_class = DeleteInstructionDocumentPageEventRequestModel

    def get_response(self) -> JsonResponse:
        rmodel: DeleteInstructionDocumentPageEventRequestModel = self.request_model
        user_id = get_jwt_identity()['id']
        repo = InstructionDocumentPageRepository()
        page: InstructionDocumentPage = repo.get(rmodel.page_id)
        managed_doc = InstructionDocumentManager(document_id=page.document_id)
        managed_doc.delete_page(user_id, page_num=page.page_num)
        return ok_response()


class ListInstructionDocumentEventHandler(EventHandler):
    request_model_class = ListInstructionDocumentEventRequestModel

    def get_response(self) -> JsonResponse:
        docs_paginated = InstructionDocumentRepository() \
            .all_paginated(page=self.request.json['page'], limit=self.request.json['limit'])
        rdata = ListInstructionDocumentEventResponseDataModel(
            total=docs_paginated.total,
            page=docs_paginated.page,
            next_num=docs_paginated.next_num,
            prev_num=docs_paginated.prev_num,
            results=docs_paginated.items
        )
        # serializer = ListInstructionDocumentSerializer(docs_paginated)
        return ok_response(rdata)


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
    request_model_class = SearchInstructionDocumentEventRequestModel

    def get_response(self) -> JsonResponse:
        page = self.request.json['page']
        limit = self.request.json['limit']
        search = self.request.json['search'].lower()
        docs_paginated = InstructionDocumentRepository() \
            .filter_paginated(f=or_(InstructionDocument.name.ilike(f'%{search}%'),
                                    InstructionDocument.description.ilike(f'%{search}%')),
                              page=page,
                              limit=limit)
        rdata = SearchInstructionDocumentEventResponseDataModel(
            total=docs_paginated.total,
            page=docs_paginated.page,
            next_num=docs_paginated.next_num,
            prev_num=docs_paginated.prev_num,
            results=docs_paginated.items
        )
        return ok_response(rdata)


class GetInstructionDocumentEventHandler(EventHandler):
    request_model_class = GetInstructionDocumentEventRequestModel

    def get_response(self) -> JsonResponse:
        rmodel: GetInstructionDocumentEventRequestModel = self.request_model
        doc = InstructionDocumentRepository().get(rmodel.document_id)
        doc_entity = InstructionDocumentEntityModel.from_orm(doc)
        pages = InstructionDocumentPageRepository().filter(InstructionDocumentPage.document_id == doc.id)
        pages_entities = [InstructionDocumentPageEntityModel.from_orm(p) for p in pages]
        data_dict = doc_entity.dict()
        data_dict['pages'] = pages_entities
        rdata = GetInstructionDocumentEventResponsedataModel(**data_dict)
        return ok_response(rdata)
