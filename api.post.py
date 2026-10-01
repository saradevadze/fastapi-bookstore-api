import requests
url="https://jsonplaceholder.typicode.com/posts"
title = input("product name")
price = int(input("price"))

data = {
    "title": "title",
    "price":  "price"
}
response=requests.post(url,json=data)
print(response.status_code)
print(response.json())
result = response.json()
print(result["id"])