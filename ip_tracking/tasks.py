from celery import shared_task
from django.utils.timezone import now, timedelta
from .models import RequestLog, SuspiciousIP

@shared_task
def detect_suspicious_ips():
    one_hour_ago = now() - timedelta(hours=1)

    # 1. Flag IPs exceeding 100 requests/hour
    heavy_users = (
        RequestLog.objects.filter(timestamp__gte=one_hour_ago)
        .values("ip_address")
        .annotate(count=models.Count("id"))
        .filter(count__gt=100)
    )

    for entry in heavy_users:
        SuspiciousIP.objects.get_or_create(
            ip_address=entry["ip_address"],
            reason="Exceeded 100 requests/hour"
        )

    # 2. Flag IPs accessing sensitive paths
    sensitive_paths = ["/admin", "/login"]
    suspicious_requests = RequestLog.objects.filter(
        timestamp__gte=one_hour_ago,
        path__in=sensitive_paths
    )

    for req in suspicious_requests:
        SuspiciousIP.objects.get_or_create(
            ip_address=req.ip_address,
            reason=f"Accessed sensitive path {req.path}"
        )