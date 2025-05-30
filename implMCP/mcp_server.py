import asyncio
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, CallToolResult
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP


# Mêmes données
FOOD_DATA = {
    "pizza": ["farine", "tomate", "mozzarella", "huile d'olive", "basilic"],
    "salade": ["laitue", "tomate", "concombre", "vinaigrette", "oignon"],
    "omelette": ["œufs", "beurre", "sel", "poivre", "herbes"],
    "pâtes": ["pâtes", "sauce tomate", "parmesan", "ail", "huile"],
}

BOOK_DATA = {
    "1984": {
        "titre": "1984",
        "auteur": "George Orwell",
        "annee": 1949,
        "resume": "Roman dystopique sur la surveillance totalitaire",
    },
    "gatsby": {
        "titre": "Gatsby le Magnifique",
        "auteur": "F. Scott Fitzgerald",
        "annee": 1925,
        "resume": "Histoire tragique du rêve américain dans les années 20",
    },
    "hamlet": {
        "titre": "Hamlet",
        "auteur": "William Shakespeare",
        "annee": 1603,
        "resume": "Tragédie du prince du Danemark",
    },
}

# Créer le serveur MCP
app = FastMCP("demo-food-books")


@app.tool()
def get_food_ingredients(food_name: str) -> dict:
    """Récupère la liste des ingrédients d'un plat"""
    food_name = food_name.lower()
    if food_name in FOOD_DATA:
        return {"plat": food_name, "ingredients": FOOD_DATA[food_name]}
    else:
        return {
            "error": f"Plat '{food_name}' non trouvé",
            "plats_disponibles": list(FOOD_DATA.keys()),
        }


@app.tool()
def list_available_foods() -> dict:
    """Liste tous les plats disponibles"""
    return {"plats_disponibles": list(FOOD_DATA.keys())}


# Book related tools
@app.tool()
def get_book_info(book_name: str) -> dict:
    """Récupère les informations d'un livre"""
    book_name = book_name.lower()
    if book_name in BOOK_DATA:
        return BOOK_DATA[book_name]
    else:
        return {
            "error": f"Livre '{book_name}' non trouvé",
            "livres_disponibles": list(BOOK_DATA.keys()),
        }


@app.tool()
def list_available_books() -> dict:
    """Liste tous les livres disponibles"""
    return {"livres_disponibles": list(BOOK_DATA.keys())}


async def main():
    """Point d'entrée principal"""
    print("Serveur MCP démarré!")

    try:
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                #   initialization_options={}
            )
    except Exception as e:
        print(f"Erreur lors de l'exécution du serveur: {e}")
        raise


if __name__ == "__main__":
    # asyncio.run(main())
    # Initialize and run the server
    app.run(transport="stdio")
