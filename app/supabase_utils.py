import os
import uuid
from urllib.parse import unquote, urlparse

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "ecommerce-bucket")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in environment")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def upload_image_to_supabase(file, filename: str | None = None) -> str:
    """
    Upload a Django UploadedFile or file-like object to Supabase storage.
    Returns the public URL string.
    Raises RuntimeError on failure.
    """
    if filename is None:
        filename = f"{uuid.uuid4().hex}_{getattr(file, 'name', 'upload')}"
    path = filename.lstrip("/")

    # accept UploadedFile or file-like
    file_obj = getattr(file, "file", file)
    try:
        file_obj.seek(0)
    except Exception:
        pass
    data = file_obj.read()
    if isinstance(data, str):
        data = data.encode()

    content_type = getattr(file, "content_type", "application/octet-stream")

    res = supabase.storage.from_(SUPABASE_BUCKET).upload(
        path, data, {"content-type": content_type}
    )
    # supabase-py may return dict with 'error'
    if isinstance(res, dict) and res.get("error"):
        raise RuntimeError(f"Supabase upload error: {res['error']}")

    pub = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(path)
    if isinstance(pub, dict):
        url = pub.get("publicURL") or pub.get("public_url")
    else:
        url = pub

    if not url:
        raise RuntimeError("Failed to obtain public URL after upload")

    return url


def delete_image_from_supabase(public_url: str) -> bool:
    """
    Delete a file from Supabase given its public URL (or storage path).
    Returns True if removed (or no-op), False on error.
    """
    if not public_url:
        return False

    # try to extract storage path after the bucket name
    try:
        parsed = urlparse(public_url)
        path = unquote(parsed.path)
        marker = f"/{SUPABASE_BUCKET}/"
        if marker in path:
            storage_path = path.split(marker, 1)[1]
        else:
            # fallback to basename
            storage_path = os.path.basename(path)
    except Exception:
        storage_path = os.path.basename(public_url)

    res = supabase.storage.from_(SUPABASE_BUCKET).remove([storage_path])
    # check for error key
    if isinstance(res, dict) and res.get("error"):
        return False
    return True
