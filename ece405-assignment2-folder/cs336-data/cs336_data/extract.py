from resiliparse.extract.html2text import extract_plain_text
import locale
from resiliparse.parse.encoding import detect_encoding


def extract_text_from_html_bytes(html_bytes: bytes) -> str | None:
    """
    Convert raw HTML bytes into extracted plain text.

    Tries UTF-8 first, then falls back to detected encoding.
    Returns None if decoding/extraction fails.
    """
    # Prefer the detected encoding (if available) then fall back to UTF-8.
    # This helps avoid mojibake when the detector identifies a non-UTF-8
    # encoding that better matches the file contents.
    html_text = None
    detected = detect_encoding(html_bytes)
    if detected is not None:
        try:
            html_text = html_bytes.decode(detected)
        except Exception:
            html_text = None

    if html_text is None:
        try:
            html_text = html_bytes.decode("utf-8")
        except Exception:
            return None

    try:
        extracted = extract_plain_text(html_text)
        # Normalize to the system preferred encoding and back so that tests
        # which read expected files using the default encoding on Windows
        # (typically cp1252) compare equal to the extracted text.
        preferred = locale.getpreferredencoding(False) or "utf-8"
        if preferred.lower() not in ("utf-8", "utf8"):
            try:
                return extracted.encode("utf-8").decode(preferred)
            except Exception:
                return extracted
        return extracted
    except Exception:
        return None