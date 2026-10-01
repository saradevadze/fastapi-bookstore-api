import requests

url = "https://api.openweathermap.org/data/2.5/weather"

params = {
    "q": "Tbilisi",
    "appid": "783e1b60dfcf84b3dc6e12ba38dea5a0",
    "units": "metric"

}

response = requests.get(url, params=params)

print(response.status_code)

data = response.json()

print(data["name"])
print(data["main"]["temp"])