from langchain_core.tools import tool
from loaders.gmail_loader import search_emails


@tool
def search_gmail(query: str, max_results: int = 10) -> str:
    """Search Gmail inbox for emails matching a query.

    Use IMAP search syntax for precise searches:
    - Subject: SUBJECT "keyword"
    - Sender: FROM "email@example.com"
    - Date: SINCE "01-Jan-2025"
    - Text: TEXT "keyword"

    Or just pass a plain keyword to search subjects and senders.

    Args:
        query: Search query (IMAP syntax or plain keyword)
        max_results: Maximum number of emails to return (default 10)
    """
    try:
        emails = search_emails(query, max_results)
    except Exception as e:
        return f"Error searching Gmail: {e}"

    return _format_emails(emails)


def create_gmail_tool(gmail_address: str, gmail_password: str):
    """Create a search_gmail tool with specific credentials baked in."""

    @tool
    def search_gmail(query: str, max_results: int = 10) -> str:
        """Search Gmail inbox for emails matching a query.

        Use IMAP search syntax for precise searches:
        - Subject: SUBJECT "keyword"
        - Sender: FROM "email@example.com"
        - Date: SINCE "01-Jan-2025"
        - Text: TEXT "keyword"

        Or just pass a plain keyword to search subjects and senders.

        Args:
            query: Search query (IMAP syntax or plain keyword)
            max_results: Maximum number of emails to return (default 10)
        """
        try:
            emails = search_emails(query, max_results,
                                   gmail_address=gmail_address,
                                   gmail_password=gmail_password)
        except Exception as e:
            return f"Error searching Gmail: {e}"

        return _format_emails(emails)

    return search_gmail


def _format_emails(emails: list[dict]) -> str:
    if not emails:
        return "No emails found matching your query."

    lines = []
    for i, em in enumerate(emails, 1):
        lines.append(f"--- Email {i} ---")
        lines.append(f"From: {em['from']}")
        lines.append(f"Subject: {em['subject']}")
        lines.append(f"Date: {em['date']}")
        lines.append(f"Snippet: {em['snippet']}")
        lines.append("")

    return "\n".join(lines)
