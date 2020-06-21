import pytest
from db.model import InstructionDocument, User, InstructionDocumentPage, get_object


@pytest.mark.unit
@pytest.mark.debug
def test_instruction_doc_created_autodate(app, dbsession):
    """ test automatic date fields setting """
    with app.app_context():
        creator = get_object(User, id=1)
        updator = get_object(User, id=2)

        doc = InstructionDocument(name='test doc', description='...', created_by=creator)
        dbsession.add(doc)
        dbsession.commit()

        created_doc = InstructionDocument.query.filter_by(id=doc.id).first()
        created_doc.update_doc(updator, name='updated test doc', description='i have desription now :)')
        dbsession.commit()

        updated_doc: InstructionDocument = InstructionDocument.query.filter_by(id=doc.id).first()
        assert updated_doc.updated_by_user_id == updator.id
        assert updated_doc.updated is not None
        assert updated_doc.name == 'updated test doc'
        assert updated_doc.description == 'i have desription now :)'


@pytest.mark.unit
def test_instruction_doc_with_pages(app, dbsession):
    """ test creation of doc with pages """
    with app.app_context():
        creator = get_object(User, id=1)

        doc = InstructionDocument(name='test doc', description='...', created_by=creator)
        dbsession.add(doc)
        dbsession.commit()
        page_one = InstructionDocumentPage(
            instruction_document=doc,
            json={
                "foo": "bar"
            }
        )
        dbsession.add(page_one)
        dbsession.commit()
        page_two = InstructionDocumentPage(
            instruction_document=doc,
            json={
                "bar": "baz"
            }
        )
        dbsession.add(page_two)
        dbsession.commit()
        assert page_one.document_id == doc.id
        assert page_two.document_id == doc.id
        assert page_one.page_num == 1
        assert page_two.page_num == 2

