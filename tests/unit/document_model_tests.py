import pytest
from db.model import InstructionDocument, InstructionDocumentPage
from repository.repos import InstructionDocumentRepository, InstructionDocumentPageRepository


@pytest.mark.unit
@pytest.mark.docs
def test_instruction_doc_created_autodate(app, dbsession, user, superuser):
    """ test automatic date fields setting """
    with app.app_context():
        creator = user
        updator = superuser

        doc = InstructionDocument(name='test doc', description='...', created_by=creator)
        repo = InstructionDocumentRepository()
        repo.save(doc)

        created_doc: InstructionDocument = repo.get(doc.id)
        created_doc.name = 'updated test doc'
        created_doc.updated_by_user_id = updator.id
        repo.save(created_doc)

        updated_doc: InstructionDocument = InstructionDocumentRepository().get(doc.id)
        assert updated_doc.updated_by_user_id == updator.id
        assert updated_doc.updated is not None
        assert updated_doc.name == 'updated test doc'


@pytest.mark.unit
@pytest.mark.model
@pytest.mark.docs
def test_instruction_doc_with_pages(app, dbsession, user):
    """ test creation of doc with pages """
    with app.app_context():
        creator = user
        doc_repo = InstructionDocumentRepository()
        page_repo = InstructionDocumentPageRepository()
        doc = InstructionDocument(name='test doc', description='...', created_by=creator)
        doc_repo.save(doc)
        page_one = InstructionDocumentPage(
            instruction_document=doc,
            json={
                "foo": "bar"
            }
        )
        page_two = InstructionDocumentPage(
            instruction_document=doc,
            json={
                "bar": "baz"
            }
        )
        page_repo.save(page_one)
        page_repo.save(page_two)

        f = filter
        pages = InstructionDocumentPageRepository().filter(InstructionDocumentPage.doc(doc.id), order="page_num desc")
        assert pages[0].document_id == doc.id
        assert pages[1].document_id == doc.id
        assert pages[0].page_num == 1
        assert pages[1].page_num == 2

# todo: other tests
