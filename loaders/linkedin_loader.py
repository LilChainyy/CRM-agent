import csv
import os
import config


class LinkedInConnections:
    """Loads and queries LinkedIn connections from a CSV export."""

    def __init__(self):
        self.connections: list[dict] = []

    def load(self):
        """Load connections from the CSV file."""
        path = config.LINKEDIN_CSV_PATH
        if not os.path.exists(path):
            print(f"Warning: LinkedIn CSV not found at {path}")
            return

        with open(path, newline="", encoding="utf-8") as f:
            # LinkedIn CSVs often have some junk lines at the top; skip them
            # The header row contains: First Name, Last Name, Email Address, Company, Position, Connected On
            reader = csv.DictReader(f)
            for row in reader:
                self.connections.append({
                    "first_name": row.get("First Name", "").strip(),
                    "last_name": row.get("Last Name", "").strip(),
                    "email": row.get("Email Address", "").strip(),
                    "company": row.get("Company", "").strip(),
                    "position": row.get("Position", "").strip(),
                    "connected_on": row.get("Connected On", "").strip(),
                })

        print(f"Loaded {len(self.connections)} LinkedIn connections.")

    def search(self, query: str) -> list[dict]:
        """
        Search connections by substring match across name, company, position, and email.
        Returns matching connections.
        """
        query_lower = query.lower()
        results = []
        for conn in self.connections:
            searchable = " ".join([
                conn["first_name"],
                conn["last_name"],
                conn["email"],
                conn["company"],
                conn["position"],
            ]).lower()
            if query_lower in searchable:
                results.append(conn)
        return results
