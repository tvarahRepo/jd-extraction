import os
from config import get_mistral_client

client = get_mistral_client()


def upload_file(file_path: str) -> str:
    """Upload PDF/DOCX to Mistral OCR storage, return signed URL."""
    filename = os.path.basename(file_path)

    uploaded_file = client.files.upload(
        file={
            "file_name": filename,
            "content": open(file_path, "rb"),
        },
        purpose="ocr",
    )

    signed_url = client.files.get_signed_url(file_id=uploaded_file.id)
    return signed_url.url


def get_ocr_response(file_url: str):
    """Process OCR on uploaded file URL, return OCRResponse with markdown pages."""
    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": file_url,
        },
        include_image_base64=True,
    )
    return ocr_response
