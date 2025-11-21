import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from database import db, create_document, get_documents
from schemas import Product, Order, Lead

app = FastAPI(title="Ceremonial Matcha API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Ceremonial Matcha API"}

# -------------------------
# Public products
# -------------------------

@app.get("/api/products", response_model=List[Product])
def list_products():
    try:
        docs = get_documents("product")
        cleaned = []
        for d in docs:
            d.pop("_id", None)
            cleaned.append(Product(**d).model_dump())
        return cleaned
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/products", response_model=str)
def create_product(product: Product):
    try:
        existing = db["product"].find_one({"slug": product.slug}) if db else None
        if existing:
            raise HTTPException(status_code=400, detail="Slug existent")
        inserted_id = create_document("product", product)
        return inserted_id
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/seed")
def seed_products():
    try:
        count = db["product"].count_documents({}) if db else 0
        if count > 0:
            return {"status": "ok", "inserted": 0}
        defaults = [
            Product(slug="kagoshima-supreme", title="Kagoshima Supreme", description="umami intens, dulceață curată", price=149.0, image=None, origin="Kagoshima", tasting_notes="umami, dulce, catifelat", grade="Ceremonial", weight_grams=30, in_stock=True),
            Product(slug="uji-heritage", title="Uji Heritage", description="echilibru fin, catifelat", price=129.0, image=None, origin="Uji", tasting_notes="echilibru, mătăsos", grade="Ceremonial", weight_grams=30, in_stock=True),
            Product(slug="daily-ceremonial", title="Daily Ceremonial", description="versatil, proaspăt", price=99.0, image=None, origin="Kagoshima", tasting_notes="proaspăt, verde", grade="Ceremonial", weight_grams=30, in_stock=True),
        ]
        inserted = 0
        for p in defaults:
            create_document("product", p)
            inserted += 1
        return {"status": "ok", "inserted": inserted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------
# Orders (simple checkout)
# -------------------------

@app.post("/api/orders", response_model=str)
def create_order(order: Order):
    try:
        total = 0.0
        for item in order.items:
            prod = db["product"].find_one({"slug": item.slug}) if db else None
            if not prod:
                raise HTTPException(status_code=400, detail=f"Produs inexistent: {item.slug}")
            total += float(prod.get("price", 0)) * item.quantity
        data = order.model_dump()
        data["total_ron"] = round(total, 2)
        inserted_id = create_document("order", data)
        return inserted_id
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------
# B2B Leads
# -------------------------

@app.post("/api/leads", response_model=str)
def create_lead(lead: Lead):
    try:
        inserted_id = create_document("lead", lead)
        return inserted_id
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Diagnostics remains
@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
