from events.core import EventHandler
from utils.http import JsonResponse


class TokenAuthEventHanlder(EventHandler):
    def get_response(self) -> JsonResponse:
        pass  # todo: impl <-
