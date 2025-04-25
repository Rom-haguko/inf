import sqlite3
from datetime import datetime
import os

DATABASE_NAME = 'store.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL CHECK(price > 0),
            stock_quantity INTEGER NOT NULL CHECK(stock_quantity >= 0)
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Sales (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_date TEXT NOT NULL,
            total_amount REAL NOT NULL CHECK(total_amount >= 0)
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SaleItems (
            sale_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity_sold INTEGER NOT NULL CHECK(quantity_sold > 0),
            price_at_sale REAL NOT NULL CHECK(price_at_sale >= 0),
            FOREIGN KEY (sale_id) REFERENCES Sales(sale_id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES Products(product_id) ON DELETE RESTRICT
        );
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_sale_date ON Sales(sale_date);
    ''')
    cursor.execute('''
         CREATE INDEX IF NOT EXISTS idx_saleitems_sale_product ON SaleItems(sale_id, product_id);
     ''')

    conn.commit()
    conn.close()
    print("Таблицы проверены/созданы.")

def add_product(name, category, price, stock_quantity):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO Products (name, category, price, stock_quantity)
            VALUES (?, ?, ?, ?)
        ''', (name, category, price, stock_quantity))
        conn.commit()
        print(f"Товар '{name}' добавлен.")
    except sqlite3.Error as e:
        print(f"Ошибка добавления товара: {e}")
        conn.rollback()
    finally:
        conn.close()

def get_available_products():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT product_id, name, category, price, stock_quantity
        FROM Products
        WHERE stock_quantity > 0
        ORDER BY category, name
    ''')
    products = cursor.fetchall()
    conn.close()
    return products

def get_product_details(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT product_id, name, category, price, stock_quantity
        FROM Products
        WHERE product_id = ?
    ''', (product_id,))
    product = cursor.fetchone()
    conn.close()
    return product

def record_sale(cart_items):
    if not cart_items:
        print("Корзина пуста, продажа не записана.")
        return False, "Корзина пуста."

    conn = get_db_connection()
    cursor = conn.cursor()
    sale_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    total_amount = sum(item['quantity'] * item['price'] for item in cart_items)

    try:
        conn.execute("BEGIN TRANSACTION;")

        for item in cart_items:
            cursor.execute("SELECT stock_quantity FROM Products WHERE product_id = ?", (item['product_id'],))
            result = cursor.fetchone()
            if result is None or result['stock_quantity'] < item['quantity']:
                 conn.rollback()
                 conn.close()
                 print(f"Ошибка: Недостаточно товара '{item.get('name', item['product_id'])}' на складе.")
                 return False, f"Недостаточно товара '{item.get('name', item['product_id'])}' на складе."

        cursor.execute('''
            INSERT INTO Sales (sale_date, total_amount) VALUES (?, ?)
        ''', (sale_time, total_amount))
        sale_id = cursor.lastrowid

        for item in cart_items:
            cursor.execute('''
                INSERT INTO SaleItems (sale_id, product_id, quantity_sold, price_at_sale)
                VALUES (?, ?, ?, ?)
            ''', (sale_id, item['product_id'], item['quantity'], item['price']))

            cursor.execute('''
                UPDATE Products
                SET stock_quantity = stock_quantity - ?
                WHERE product_id = ?
            ''', (item['quantity'], item['product_id']))

        conn.commit()
        print(f"Продажа #{sale_id} успешно записана.")
        conn.close()
        return True, f"Чек #{sale_id} успешно создан."

    except sqlite3.Error as e:
        conn.rollback()
        print(f"Ошибка записи продажи: {e}")
        conn.close()
        return False, f"Ошибка базы данных: {e}"


def get_sales_report_by_date(report_date_str):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT p.name, SUM(si.quantity_sold) as total_quantity
        FROM SaleItems si
        JOIN Products p ON si.product_id = p.product_id
        JOIN Sales s ON si.sale_id = s.sale_id
        WHERE date(s.sale_date) = ?
        GROUP BY p.product_id, p.name
        ORDER BY p.name;
    ''', (report_date_str,))
    items_sold = cursor.fetchall()

    cursor.execute('''
        SELECT SUM(s.total_amount) as total_revenue
        FROM Sales s
        WHERE date(s.sale_date) = ?;
    ''', (report_date_str,))
    revenue_result = cursor.fetchone()
    total_revenue = revenue_result['total_revenue'] if revenue_result and revenue_result['total_revenue'] is not None else 0.0

    conn.close()
    return items_sold, total_revenue

def initialize_database():
    db_exists = os.path.exists(DATABASE_NAME)
    create_tables()
    if not db_exists:
        print("База данных не найдена, добавляем тестовые данные...")
        add_product("Молоко", "Молочные продукты", 75.50, 50)
        add_product("Хлеб", "Хлебобулочные", 40.00, 100)
        add_product("Сыр Гауда", "Молочные продукты", 650.00, 20)
        add_product("Яблоки Голден", "Фрукты", 120.50, 80)
        add_product("Бананы", "Фрукты", 99.90, 60)
        add_product("Мыло", "Хозтовары", 55.00, 70)
        print("Тестовые данные добавлены.")

if __name__ == '__main__':
    initialize_database()

    print("\nДоступные товары:")
    products = get_available_products()
    for p in products:
        print(f"ID: {p['product_id']}, Имя: {p['name']}, Категория: {p['category']}, Цена: {p['price']:.2f}, На складе: {p['stock_quantity']}")

    today = datetime.now().strftime('%Y-%m-%d')
    print(f"\nОтчет за {today}:")
    items, revenue = get_sales_report_by_date(today)
    if items:
        for item in items:
            print(f"- {item['name']}: {item['total_quantity']} шт.")
    else:
        print("- Товаров не продано.")
    print(f"Общая выручка: {revenue:.2f} руб.")
