import requests
from django.utils.timezone import now
from django.core.cache import cache
from .models import RequestLog

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip_address = self.get_client_ip(request)

        # Cache lookup
        cache_key = f"geo_{ip_address}"
        geo_data = cache.get(cache_key)

        if not geo_data:
            try:
                response = requests.get(f"https://ipapi.co/{ip_address}/json/")
                data = response.json()
                geo_data = {
                    "country": data.get("country_name"),
                    "city": data.get("city"),
                }
                cache.set(cache_key, geo_data, timeout=86400)  # 24h
            except Exception:
                geo_data = {"country": None, "city": None}

        # Log request
        RequestLog.objects.create(
            ip_address=ip_address,
            timestamp=now(),
            path=request.path,
            country=geo_data.get("country"),
            city=geo_data.get("city"),
        )

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip