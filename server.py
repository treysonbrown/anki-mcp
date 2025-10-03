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
    return anki_request("deckNames")

@mcp.tool
def deck_stats(deck_name: str):
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
    
    note_ids.sort(reverse=True)
    
    recent_ids = note_ids[:n]
    
    return anki_request("notesInfo", {"notes": recent_ids})



@mcp.tool
def add_card(deck_name: str, model_name: str, fields: dict, tags: list[str] = []):
    note = {
        "deckName": deck_name,
        "modelName": model_name,
        "fields": fields,
        "tags": tags,
    }
    return anki_request("addNote", {"note": note})


@mcp.tool
def delete_cards(note_ids: list[int]):
    if not note_ids:
        return False
    return anki_request("deleteNotes", {"notes": note_ids})


@mcp.tool
def create_deck(deck_name: str) -> bool:
    result = anki_request("createDeck", {"deck": deck_name})
    return bool(result)




if __name__ == "__main__":
    mcp.run()
