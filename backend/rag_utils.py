import json
import os

PRODUCTS_PATH = os.path.join(os.path.dirname(__file__), "products.json")

def load_products():
    with open(PRODUCTS_PATH, "r") as f:
        return json.load(f)

def find_product_by_part_number(part_number):
    products = load_products()
    for product in products:
        if product["id"].lower() == part_number.lower():
            return product
    return None

def find_products_by_model(model):
    products = load_products()
    return [p for p in products if model in p.get("compatibleModels", [])] 