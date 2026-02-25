from langchain_core.tools import tool
from loaders.linkedin_loader import LinkedInConnections

# Module-level instance, initialized from main.py
_connections = LinkedInConnections()


def init_linkedin():
    """Load LinkedIn connections from CSV. Call once at startup."""
    _connections.load()


@tool
def search_connections(query: str) -> str:
    """Search LinkedIn connections by name, company, position, or email.

    Pass a keyword and it will match against all connection fields.

    Args:
        query: Search term to match against name, company, position, or email
    """
    results = _connections.search(query)

    if not results:
        return "No LinkedIn connections found matching your query."

    lines = []
    for i, conn in enumerate(results, 1):
        name = f"{conn['first_name']} {conn['last_name']}".strip()
        lines.append(f"--- Connection {i} ---")
        lines.append(f"Name: {name}")
        if conn["position"]:
            lines.append(f"Position: {conn['position']}")
        if conn["company"]:
            lines.append(f"Company: {conn['company']}")
        if conn["email"]:
            lines.append(f"Email: {conn['email']}")
        if conn["connected_on"]:
            lines.append(f"Connected On: {conn['connected_on']}")
        lines.append("")

    return "\n".join(lines)
