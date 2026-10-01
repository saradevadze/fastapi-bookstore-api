from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

import models
from database import engine
from routers import users, books, cart, orders

# ბაზის ცხრილების შექმნა
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-commerce API")

# შევქმნათ static/uploads საქაღალდე სურათებისთვის
os.makedirs("static/uploads", exist_ok=True)

# Static ფაილების გაზიარება
app.mount("/static", StaticFiles(directory="static"), name="static")

# როუტერების ჩამატება
app.include_router(users.router)
app.include_router(books.router)
app.include_router(cart.router)
app.include_router(orders.router)


@app.get("/")
def home():
    return {"message": "Welcome to E-commerce API!"}