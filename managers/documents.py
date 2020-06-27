from db.model import InstructionDocument, InstructionDocumentPage
from repository.repos import InstructionDocumentRepository, InstructionDocumentPageRepository


class InstructionDocumentManager:
    def __init__(self, document: InstructionDocument):
        self.__document = document

    def page_count(self):
        return len(InstructionDocumentPageRepository().filter(InstructionDocumentPage.doc(self.__document.id)))
