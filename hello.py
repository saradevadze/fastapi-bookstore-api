import os
import requests
from requests.exceptions import RequestException
from dotenv import load_dotenv

# 1. .env ფაილის ჩატვირთვა
load_dotenv()

# 2. სრული API კლასი
class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json; charset=UTF-8",
            "User-Agent": "MyLearningApp/1.0"
        })

    def get_product(self, product_id):
        try:
            response = self.session.get(f"{self.base_url}/{product_id}", timeout=5)
            if response.status_code == 404:
                return "❌ პროდუქტი ვერ მოიძებნა (404)"
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            return f"🚨 ქსელური შეცდომა: {e}"

    def create_product(self, title, price):
        data = {"title": title, "price": price}
        try:
            response = self.session.post(self.base_url, json=data, timeout=5)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            return f"🚨 ქსელური შეცდომა: {e}"

    def update_product(self, product_id, title, price):
        data = {"title": title, "price": price}
        try:
            response = self.session.put(f"{self.base_url}/{product_id}", json=data, timeout=5)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            return f"🚨 ქსელური შეცდომა: {e}"

    def delete_product(self, product_id):
        try:
            response = self.session.delete(f"{self.base_url}/{product_id}", timeout=5)
            response.raise_for_status()
            return "✅ პროდუქტი წარმატებით წაიშალა!"
        except RequestException as e:
            return f"🚨 ქსელური შეცდომა: {e}"


# 3. .env-იდან URL-ის ამოღება და ტესტირება
url_from_env = os.getenv("BASE_URL")

client = APIClient(url_from_env)

print("--- 1. GET ტესტი ---")
print(client.get_product(1))

print("\n--- 2. POST ტესტი ---")
print(client.create_product("iPhone 15", 1200))

print("\n--- 3. DELETE ტესტი ---")
print(client.delete_product(1))