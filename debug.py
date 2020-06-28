from wsgi import app
from db.model import InstructionDocument, InstructionDocumentPage
from repository.repos import UserRepository, InstructionDocumentRepository, InstructionDocumentPageRepository
from utils.managers import InstructionDocumentManager


# todo: .gitingore <-


if __name__ == '__main__':
    with app.app_context():
        usr = UserRepository().get(1)
        doc = InstructionDocument(
            'test doc',
            'foo',
            usr
        )
        InstructionDocumentRepository().save(doc)
        managed_doc = InstructionDocumentManager(document_id=doc.id)
        page1 = InstructionDocumentPage(
            document_id=doc.id,
            json={'foo1': 'bar'}
        )
        managed_doc.add_page(page1)
        count = InstructionDocumentManager(document=doc).page_count()
        page2 = InstructionDocumentPage(
            document_id=doc.id,
            json={'foo2': 'bar'},
            page_num=4
        )
        managed_doc.add_page(page2)
        new_count = InstructionDocumentManager(document=doc).page_count()
        managed_doc.delete_page(1)
        ncount = InstructionDocumentManager(document=doc).page_count()

        pages = managed_doc.pages()
        pass
