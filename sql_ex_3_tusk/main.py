import sqlite3

connection = sqlite3.connect("EX_1_var_3.db")

cursor = connection.cursor()

cursor.execute("""
    SELECT SUM(trade.count_obj * trade.price) 
    FROM trade
    JOIN shop ON trade.shop = shop.id_shop
    JOIN product ON trade.article_number = product.article_number
    WHERE trade.operation = 'Продажа'
    AND product.department = 'Бакалея'
    AND shop.district = 'Первомайский'
    AND trade.date BETWEEN '2021-06-14' AND '2021-06-21';
""")

result = cursor.fetchone()[0]
print(f"Общая сумма выручки: {result} рублей")
connection.close()
