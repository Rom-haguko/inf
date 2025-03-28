import sqlite3

connection = sqlite3.connect("company.db")
cursor  = connection.cursor()

# Создание таблицы `job_titles`
cursor.execute("""
    CREATE TABLE IF NOT EXISTS `job_titles` (
        `id_job_title` INTEGER PRIMARY KEY NOT NULL UNIQUE,
        `name` TEXT NOT NULL
    );
""")

# Создание таблицы `employees`
cursor.execute("""
    CREATE TABLE IF NOT EXISTS `employees` (
        `id` INTEGER PRIMARY KEY NOT NULL UNIQUE,
        `surname` TEXT NOT NULL,
        `name` TEXT NOT NULL,
        `phone` TEXT,
        `id_job_title` INTEGER NOT NULL,
        FOREIGN KEY(`id_job_title`) REFERENCES `job_titles`(`id_job_title`)
    );
""")

# Создание таблицы `clients`
cursor.execute("""
    CREATE TABLE IF NOT EXISTS `clients` (
        `id_client` INTEGER PRIMARY KEY NOT NULL UNIQUE,
        `organization` TEXT NOT NULL,
        `phone` TEXT
    );
""")

# Создание таблицы `orders`
cursor.execute("""
    CREATE TABLE IF NOT EXISTS `orders` (
        `id_order` INTEGER PRIMARY KEY NOT NULL UNIQUE,
        `id_client` INTEGER NOT NULL,
        `id_employee` INTEGER NOT NULL,
        `amount` REAL NOT NULL,
        `completion_date` TEXT,
        `is_completed` INTEGER DEFAULT 0,
        FOREIGN KEY(`id_client`) REFERENCES `clients`(`id_client`),
        FOREIGN KEY(`id_employee`) REFERENCES `employees`(`id`)
    );
""")

#заполнение таблицы

job_titles_data = [
    (1, 'Менеджер'),
    (2, 'Разработчик'),
    (3, 'Аналитик'),
    (4, 'Дизайнер')
]

cursor.executemany("INSERT OR IGNORE INTO `job_titles` (`id_job_title`, `name`) VALUES (?, ?)", job_titles_data)

employees_data = [
    (1, 'Иванов', 'Иван', '+79111234567', 2),
    (2, 'Петров', 'Петр', '+79119876543', 1),
    (3, 'Сидорова', 'Мария', '+79112345678', 3),
    (4, 'Козлов', 'Алексей', '+79118765432', 2),
    (5, 'Васильева', 'Ольга', '+79117654321', 4)
]

cursor.executemany("INSERT OR IGNORE INTO `employees` (`id`, `surname`, `name`, `phone`, `id_job_title`) VALUES (?, ?, ?, ?, ?)", employees_data)

clients_data = [
    (1, 'ООО "Ромашка"', '+74951234567'),
    (2, 'ИП Сидоров', '+74959876543'),
    (3, 'ЗАО "Лучик"', '+74952345678')
]

cursor.executemany("INSERT OR IGNORE INTO `clients` (`id_client`, `organization`, `phone`) VALUES (?, ?, ?)", clients_data)

orders_data = [
    (1, 1, 2, 1000.50, '2023-10-01', 1),
    (2, 2, 1, 2000.75, '2023-10-05', 0),
    (3, 3, 3, 1500.00, '2023-10-10', 1)
]

cursor.executemany("INSERT OR IGNORE INTO `orders` (`id_order`, `id_client`, `id_employee`, `amount`, `completion_date`, `is_completed`) VALUES (?, ?, ?, ?, ?, ?)", orders_data)

connection.commit()

# Выборка всех сотрудников
cursor.execute("SELECT * FROM employees")
employees = cursor.fetchall()
for employee in employees:
    print(employee)

#  Выборка всех заказов с информацией о клиентах и сотрудниках
cursor.execute("""
    SELECT o.id_order, c.organization, e.surname, e.name, o.amount, o.completion_date
    FROM orders o
    JOIN clients c ON o.id_client = c.id_client
    JOIN employees e ON o.id_employee = e.id
""")
orders = cursor.fetchall()
for order in orders:
    print(order)

# Выборка всех невыполненных заказов
cursor.execute("SELECT * FROM orders WHERE is_completed = 0")
uncompleted_orders = cursor.fetchall()
for order in uncompleted_orders:
    print(order)

# Обновление статуса заказа
cursor.execute("UPDATE orders SET is_completed = 1 WHERE id_order = 2")
connection.commit()

#  Удаление сотрудника
cursor.execute("DELETE FROM employees WHERE id = 5")
connection.commit()

connection.close()
