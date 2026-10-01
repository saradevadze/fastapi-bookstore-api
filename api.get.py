import requests
response=requests.get("https://jsonplaceholder.typicode.com/posts")
print(response.status_code)
data=response.json()
for post in data:
    if post ["userId"]  == 1:
         print(post["title"])