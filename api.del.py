import requests
response=requests.delete("https://jsonplaceholder.typicode.com/posts/5")
print(response.status_code)