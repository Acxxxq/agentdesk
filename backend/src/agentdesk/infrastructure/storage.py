from agentdesk.core.settings import get_settings


def storage_client():
    from minio import Minio
    from urllib3 import PoolManager, Timeout

    settings = get_settings()
    transport = PoolManager(timeout=Timeout(connect=2, read=3), retries=False)
    client = Minio(
        settings.objectstore_endpoint,
        access_key=settings.objectstore_access_key,
        secret_key=settings.objectstore_secret_key,
        secure=settings.objectstore_secure,
        http_client=transport,
    )
    return client, transport
