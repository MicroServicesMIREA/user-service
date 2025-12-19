import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from .metrics import http_requests_total, http_request_duration_seconds, http_requests_errors_total

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Получаем метод и путь
        method = request.method
        path = request.url.path
        
        # Исключаем метрики и health check из метрик
        if path in ['/metrics', '/health', '/']:
            response = await call_next(request)
            return response
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            
            # Записываем метрики
            http_requests_total.labels(
                method=method,
                endpoint=path,
                status_code=status_code
            ).inc()
            
            duration = time.time() - start_time
            http_request_duration_seconds.labels(
                method=method,
                endpoint=path
            ).observe(duration)
            
            # Если ошибка (4xx или 5xx), увеличиваем счетчик ошибок
            if status_code >= 400:
                http_requests_errors_total.labels(
                    method=method,
                    endpoint=path,
                    status_code=status_code
                ).inc()
            
            return response
        except Exception as e:
            # В случае исключения тоже записываем метрику
            status_code = 500
            http_requests_total.labels(
                method=method,
                endpoint=path,
                status_code=status_code
            ).inc()
            http_requests_errors_total.labels(
                method=method,
                endpoint=path,
                status_code=status_code
            ).inc()
            raise

