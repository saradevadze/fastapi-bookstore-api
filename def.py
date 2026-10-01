prices = [80, 40, 120, 150, 200]

def discount(price):
    if price >= 100:
        return price - 20
    else:
        return price

for price in prices:
    result = discount(price)
    print(result)


    