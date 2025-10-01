import requests
from fastmcp import FastMCP

ANKI_CONNECT_URL = "http://localhost:8765"
mcp = FastMCP(name="Anki MCP")

def anki_request(action, params=None):
    response = requests.post(
        ANKI_CONNECT_URL,
        json={
            "action": action,
            "version": 6,
            "params": params or {}
        }
    )
    response.raise_for_status()
    return response.json()["result"]




@mcp.tool
def list_decks() -> list[str]:
    """Return all deck names from Anki."""
    return anki_request("deckNames")

@mcp.tool
def deck_stats(deck_name: str):
    """Return statistics for a specific deck."""
    return anki_request("getDeckStats", {"decks": [deck_name]})

@mcp.tool
def get_cards(deck_name: str):
    """Return all cards (note fields/tags) from a specific deck."""
    note_ids = anki_request("findNotes", {"query": f"deck:{deck_name}"})
    if not note_ids:
        return []
    return anki_request("notesInfo", {"notes": note_ids})

@mcp.tool
def get_recent_cards(n: int = 200):
    note_ids = anki_request("findNotes", {"query": ""})
    if not note_ids:
        return []
    
    # Sort descending by ID (newest first)
    note_ids.sort(reverse=True)
    
    # Grab the top N
    recent_ids = note_ids[:n]
    
    # Fetch info
    return anki_request("notesInfo", {"notes": recent_ids})

if __name__ == "__main__":
    mcp.run(transport="http", port=8000)
