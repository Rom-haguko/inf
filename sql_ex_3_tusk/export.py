import sqlite3
from datetime import datetime

connection = sqlite3.connect("EX_1_var_3.db")
cursor = connection.cursor()


cursor.executescript("""
CREATE TABLE IF NOT EXISTS `shop` (
    `id_shop` TEXT PRIMARY KEY NOT NULL UNIQUE,
    `district` TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS `product` (
    `article_number` INTEGER PRIMARY KEY NOT NULL UNIQUE,
    `department` TEXT NOT NULL,
    `name_product` TEXT NOT NULL,
    `unit` TEXT NOT NULL,
    `count` INTEGER NOT NULL,
    `provider` TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS `trade` (
    `id_operation` INTEGER PRIMARY KEY NOT NULL UNIQUE,
    `date` TEXT NOT NULL,
    `shop` INTEGER NOT NULL,
    `article_number` INTEGER NOT NULL,
    `operation` TEXT NOT NULL,
    `count_obj` INTEGER NOT NULL,
    `price` INTEGER NOT NULL,
    FOREIGN KEY(`shop`) REFERENCES `shop`(`id_shop`),
    FOREIGN KEY(`article_number`) REFERENCES `product`(`article_number`)
);
""")

list_shop = []
with open('shop.txt', 'r', encoding='utf-8') as file:
    for line in file:
        parts = line.strip().split('\t')  # Удаляем пробелы и разбиваем по табуляции
        if len(parts) == 2:  # Проверяем, что есть ровно 2 элемента
            parts[0] = parts[0].strip()  # Удаляем пробелы у id_shop
            parts[1] = parts[1].strip()  # Удаляем пробелы у district
            list_shop.append(parts)
        
cursor.executemany("INSERT OR IGNORE INTO shop (id_shop, district) VALUES (?, ?)", list_shop)

list_product = list()
with open('product.txt', 'r', encoding='utf-8') as file:
    for line in file:
        line_data = line.strip().split('\t')
        line_data[0] = int(line_data[0])
        list_product.append(line_data)

product_data = list_product
cursor.executemany("INSERT OR IGNORE INTO `product` (`article_number`, `department`, `name_product`, `unit`, `count`, `provider`) VALUES (?, ?, ?, ?, ?, ?)", product_data)

list_trade = list()
with open('trade.txt', 'r',  encoding='utf-8') as file:
    for line in file:
        line_data = line.strip().split('\t')
        line_data[0] = int(line_data[0])
        date_obj = datetime.strptime(line_data[1], "%d.%m.%Y")
        line_data[1] = date_obj.strftime("%Y-%m-%d %H:%M:%S")
        line_data[2] = line_data[2].strip()
        line_data[4] = line_data[4].strip()
        line_data[3] = int(line_data[3])
        line_data[5] = int(line_data[5])
        line_data[6] = int(line_data[6])
        list_trade.append(line_data)

trade_data = list_trade
cursor.executemany("INSERT OR IGNORE INTO `trade` (`id_operation`, `date`, `shop`, `article_number`, `operation`, `count_obj`, 'price') VALUES (?, ?, ?, ?, ?, ?, ?)", trade_data)

connection.commit()
connection.close()
