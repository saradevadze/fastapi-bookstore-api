import requests

url = "https://jsonplaceholder.typicode.com/posts"

choice = input("What do you want? 1-Get 2-Post 3-Put 4-Delete: ")

if choice == "1":
    response = requests.get(url)
    print(response.status_code)
    print(response.json())

elif choice == "2":
    title = input("Product name: ")
    price = int(input("Price: "))

    data = {
        "title": title,
        "price": price
    }

    response = requests.post(url, json=data)
    print(response.status_code)
    print(response.json())

elif choice == "3":
    product_id = input("Product ID: ")
    new_title = input("New product name: ")
    new_price = int(input("New price: "))

    data = {
        "title": new_title,
        "price": new_price
    }

    response = requests.put(
        f"https://jsonplaceholder.typicode.com/posts/{product_id}",
        json=data
    )

    print(response.status_code)
    print(response.json())

elif choice == "4":
    product_id = input("Product ID: ")

    response = requests.delete(
        f"https://jsonplaceholder.typicode.com/posts/{product_id}"
    )

    print(response.status_code)