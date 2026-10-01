import requests
response=requests.put("https://jsonplaceholder.typicode.com/posts/5")
data = {
       "title": "my new title"
}
response=requests.put("https://jsonplaceholder.typicode.com/posts/5",  json=data)
print(response.status_code)
print(response.json())
result=(response.json())
print(result["title"])