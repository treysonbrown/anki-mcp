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




# ---------- Deck Management ----------

@mcp.tool
def list_decks() -> list[str]:
    return anki_request("deckNames")



@mcp.tool
def create_deck(deck_name: str) -> bool:
    result = anki_request("createDeck", {"deck": deck_name})
    return bool(result)

@mcp.tool
def delete_deck(deck_name: str, cards_too: bool = False) -> bool:
    result = anki_request(
        "deleteDecks",
        {"decks": [deck_name], "cardsToo": cards_too}
    )
    return bool(result)

@mcp.tool
def rename_deck(old_name: str, new_name: str) -> bool:
    return anki_request(
        "renameDeck", {"oldName": old_name, "newName": new_name}
    )


# ---------- Card + Note Management ----------

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
def add_cards(notes: list[dict]):
    """Batch add multiple notes/cards at once"""
    return anki_request("addNotes", {"notes": notes})

@mcp.tool
def delete_cards(note_ids: list[int]):
    if not note_ids:
        return False
    return anki_request("deleteNotes", {"notes": note_ids})

@mcp.tool
def update_note_fields(note_id: int, fields: dict) -> bool:
    result = anki_request("updateNoteFields", {"note": {"id": note_id, "fields": fields}})
    return bool(result)


# ---------- Searching + Retrieval ----------

@mcp.tool
def find_notes(query: str) -> list[int]:
    return anki_request("findNotes", {"query": query})

@mcp.tool
def get_notes_info(note_ids: list[int]):
    if not note_ids:
        return []
    return anki_request("notesInfo", {"notes": note_ids})

@mcp.tool
def get_recent_cards(n: int = 200):
    note_ids = anki_request("findNotes", {"query": ""})
    if not note_ids:
        return []
    note_ids.sort(reverse=True)
    return anki_request("notesInfo", {"notes": note_ids[:n]})


# ---------- Models / Templates ----------

@mcp.tool
def list_models() -> list[str]:
    return anki_request("modelNames")

@mcp.tool
def model_field_names(model_name: str) -> list[str]:
    return anki_request("modelFieldNames", {"modelName": model_name})


# ---------- Scheduling ----------

@mcp.tool
def suspend_cards(card_ids: list[int]):
    return anki_request("suspendCards", {"cards": card_ids})

@mcp.tool
def unsuspend_cards(card_ids: list[int]):
    return anki_request("unsuspendCards", {"cards": card_ids})

@mcp.tool
def set_due_date(card_ids: list[int], due: str):
    """Due string example: 'tomorrow', '3', '2025-10-03'"""
    return anki_request("setDueDate", {"cards": card_ids, "due": due})


# ---------- Statistics ----------

@mcp.tool
def deck_stats(deck_name: str):
    return anki_request("getDeckStats", {"decks": [deck_name]})

@mcp.tool
def get_card_stats(card_id: int):
    return anki_request("cardStats", {"cardId": card_id})




if __name__ == "__main__":
    mcp.run()
