import re

EMAIL_PATTERN = re.compile(
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
)

def mask_emails(text: str) -> tuple[str, int]:
    matches = EMAIL_PATTERN.findall(text)
    count = len(matches)

    masked_text = EMAIL_PATTERN.sub("|||EMAIL_ADDRESS|||", text)

    return masked_text, count


PHONE_PATTERN = re.compile(
    r"\+?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}"
)

def mask_phone_numbers(text: str) -> tuple[str, int]:
    matches = PHONE_PATTERN.findall(text)
    count = len(matches)

    masked_text = PHONE_PATTERN.sub("|||PHONE_NUMBER|||", text)

    return masked_text, count

IP_PATTERN = re.compile(
    r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
)

def mask_ips(text: str) -> tuple[str, int]:
    matches = IP_PATTERN.findall(text)
    count = len(matches)

    masked_text = IP_PATTERN.sub("|||IP_ADDRESS|||", text)

    return masked_text, count