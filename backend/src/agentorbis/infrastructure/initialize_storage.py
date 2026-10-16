"""Create the application's private document bucket once at stack startup."""

from agentorbis.core.settings import get_settings
from agentorbis.infrastructure.storage import storage_client


def main() -> None:
    from minio.error import S3Error

    client, transport = storage_client()
    bucket = get_settings().objectstore_bucket
    try:
        if not client.bucket_exists(bucket):
            try:
                client.make_bucket(bucket)
            except S3Error as exc:
                if exc.code != "BucketAlreadyOwnedByYou":
                    raise
        print(f"Document bucket ready: {bucket}")
    finally:
        transport.clear()


if __name__ == "__main__":
    main()
