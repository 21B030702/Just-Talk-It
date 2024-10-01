import logging

# Инициализация логгера для использования в middleware
logger = logging.getLogger(__name__)

class RequestLogMiddleware:
    """
    Middleware для логирования всех запросов, сделанных аутентифицированными пользователями.
    Записывает имя пользователя и путь запроса в лог.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Выполняется до обработки запроса
        if request.user.is_authenticated:
            logger.info(f"User '{request.user.username}' accessed {request.path}")

        # Передача запроса следующему middleware или представлению
        response = self.get_response(request)

        # Выполняется после обработки запроса
        return response
