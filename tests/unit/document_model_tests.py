import pytest
from db.model import InstructionDocument, User


@pytest.mark.unit
def test_instruction_doc_created_autodate(app, dbsession):
    """ test automatic date fields setting """
    with app.app_context():
        creator = User.query.filter_by(id=1).first()
        updator = User.query.filter_by(id=2).first()

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
