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



@mcp.tool
def add_card(deck_name: str, model_name: str, fields: dict, tags: list[str] = []):
    """
    Add a new card to a given deck.
    
    Args:
        deck_name: The deck to add the card to.
        model_name: The note type/model (e.g., "Basic", "Cloze").
        fields: A dict mapping field names (Front, Back, Text, etc.) to values.
        tags: Optional list of tags.

    Returns:
        The note ID of the created card, or None if failed.
    """
    note = {
        "deckName": deck_name,
        "modelName": model_name,
        "fields": fields,
        "tags": tags,
    }
    return anki_request("addNote", {"note": note})


@mcp.tool
def delete_cards(note_ids: list[int]):
    """
    Delete cards by their note IDs.
    
    Args:
        note_ids: The list of note IDs to delete.
    
    Returns:
        True if successful.
    """
    if not note_ids:
        return False
    return anki_request("deleteNotes", {"notes": note_ids})







if __name__ == "__main__":
    mcp.run()
