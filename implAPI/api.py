from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

# Données simples pour la démo
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


@app.get("/food/{food_name}")
async def get_food_ingredients(food_name: str):
    """API pour récupérer les ingrédients d'un plat"""
    food_name = food_name.lower()
    if food_name in FOOD_DATA:
        return {"plat": food_name, "ingredients": FOOD_DATA[food_name]}
    else:
        raise HTTPException(status_code=404, detail="Plat non trouvé")


@app.get("/book/{book_name}")
async def get_book_info(book_name: str):
    """API pour récupérer les infos d'un livre"""
    book_name = book_name.lower()
    if book_name in BOOK_DATA:
        return BOOK_DATA[book_name]
    else:
        raise HTTPException(status_code=404, detail="Livre non trouvé")


@app.get("/foods")
async def list_foods():
    """Liste tous les plats disponibles"""
    return {"plats_disponibles": list(FOOD_DATA.keys())}


@app.get("/books")
async def list_books():
    """Liste tous les livres disponibles"""
    return {"livres_disponibles": list(BOOK_DATA.keys())}


if __name__ == "__main__":
    import uvicorn

    print("API Nourriture & Livres démarrée")
    uvicorn.run(app, host="0.0.0.0", port=8000)
