from prometheus_client import Counter, Histogram, Gauge, generate_latest

# HTTP метрики
http_requests_total = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
)

http_requests_errors_total = Counter(
    'http_requests_errors_total',
    'Total number of HTTP errors',
    ['method', 'endpoint', 'status_code']
)

# Метрики базы данных
database_connections_active = Gauge(
    'database_connections_active',
    'Number of active database connections'
)

def get_metrics():
    """Возвращает метрики в формате Prometheus"""
    return generate_latest()

