import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
import config


def _decode_header_value(value):
    """Decode an email header value into a string."""
    if value is None:
        return ""
    decoded_parts = decode_header(value)
    parts = []
    for part, charset in decoded_parts:
        if isinstance(part, bytes):
            parts.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            parts.append(part)
    return "".join(parts)


def _get_body_text(msg):
    """Extract plain text body from an email message."""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    return payload.decode(charset, errors="replace")
        return ""
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            return payload.decode(charset, errors="replace")
        return ""


def _connect(gmail_address: str = "", gmail_password: str = ""):
    """Connect and login to Gmail IMAP."""
    address = gmail_address or config.GMAIL_ADDRESS
    password = gmail_password or config.GMAIL_APP_PASSWORD
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(address, password)
    return mail


def search_emails(query: str, max_results: int = 10, gmail_address: str = "", gmail_password: str = "") -> list[dict]:
    """
    Search Gmail for emails matching the query.

    The query is used as a Gmail IMAP search term. Supports:
    - Subject search: SUBJECT "keyword"
    - Sender search: FROM "email@example.com"
    - Date search: SINCE "01-Jan-2025"
    - Full text: TEXT "keyword"
    - Combined: (FROM "john" SUBJECT "meeting")

    If the query doesn't look like IMAP syntax, it's wrapped in a TEXT search.
    """
    mail = _connect(gmail_address, gmail_password)
    try:
        mail.select("INBOX", readonly=True)

        # If query doesn't contain IMAP keywords, treat it as a text search
        imap_keywords = ["FROM", "TO", "SUBJECT", "TEXT", "SINCE", "BEFORE", "ON",
                         "BODY", "ALL", "UNSEEN", "SEEN"]
        query_upper = query.upper().strip()
        is_imap_syntax = any(query_upper.startswith(kw) or f"({kw}" in query_upper
                            for kw in imap_keywords)

        if is_imap_syntax:
            search_criteria = query
        else:
            search_criteria = f'(OR (SUBJECT "{query}") (FROM "{query}"))'

        status, message_ids = mail.search(None, search_criteria)
        if status != "OK" or not message_ids[0]:
            return []

        ids = message_ids[0].split()
        # Take the most recent emails (last N ids)
        ids = ids[-max_results:]
        ids.reverse()

        results = []
        for msg_id in ids:
            status, msg_data = mail.fetch(msg_id, "(RFC822)")
            if status != "OK":
                continue

            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            subject = _decode_header_value(msg["Subject"])
            sender = _decode_header_value(msg["From"])
            date_str = msg["Date"]
            date = ""
            if date_str:
                try:
                    date = str(parsedate_to_datetime(date_str))
                except Exception:
                    date = date_str

            body = _get_body_text(msg)
            snippet = body[:500].strip() if body else ""

            results.append({
                "subject": subject,
                "from": sender,
                "date": date,
                "snippet": snippet,
            })

        return results
    finally:
        mail.logout()
