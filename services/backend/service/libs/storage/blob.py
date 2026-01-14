from azure.storage.blob import BlobServiceClient
from django.conf import settings


def get_blob_service_client(
    account_name=settings.AZURE_STORAGE_ACCOUNT_NAME,
    account_key=settings.AZURE_STORAGE_ACCOUNT_SAS_TOKEN
) -> BlobServiceClient:
    return BlobServiceClient(
        account_url=f"https://{account_name}.blob.core.windows.net",
        credential=account_key
    )
