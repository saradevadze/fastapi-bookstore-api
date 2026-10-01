from database import engine
from sqlalchemy import text

def clean_database():
    with engine.connect() as connection:
        # შლის ყველა მონაცემს users, books, cart_items, orders ცხრილებიდან
        connection.execute(text("TRUNCATE TABLE users, books CASCADE;"))
        connection.commit()
        print("✅ ბაზა წარმატებით გასუფთავდა!")

if __name__ == "__main__":
    clean_database()