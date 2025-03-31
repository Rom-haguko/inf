import sqlite3


connection = sqlite3.connect("STUDENT.db")
cursor = connection.cursor()

# 1. Количество всех студентов
cursor.execute("SELECT COUNT(*) FROM students")
total_students = cursor.fetchone()[0]
print(f"1. Общее количество студентов: {total_students}")

# 2. Количество студентов по направлениям
print("\n2. Количество студентов по направлениям:")
cursor.execute("""
    SELECT p.name, COUNT(s.student_id) as count
    FROM students s
    JOIN programs p ON s.program_id = p.program_id
    GROUP BY p.name
""")
for row in cursor.fetchall():
    print(f"Направление: {row[0]}, Количество студентов: {row[1]}")

# 3. Количество студентов по формам обучения
print("\n3. Количество студентов по формам обучения:")
cursor.execute("""
    SELECT e.name, COUNT(s.student_id) as count
    FROM students s
    JOIN education_types e ON s.education_type_id = e.education_type_id
    GROUP BY e.name
""")
for row in cursor.fetchall():
    print(f"Форма обучения: {row[0]}, Количество студентов: {row[1]}")

# 4. Максимальный, минимальный, средний баллы студентов по направлениям
print("\n4. Максимальный, минимальный, средний баллы по направлениям:")
cursor.execute("""
    SELECT p.name, 
           MAX(s.average_score) as max_score, 
           MIN(s.average_score) as min_score, 
           AVG(s.average_score) as avg_score
    FROM students s
    JOIN programs p ON s.program_id = p.program_id
    GROUP BY p.name
""")
for row in cursor.fetchall():
    print(f"Направление: {row[0]}, Макс. балл: {row[1]}, Мин. балл: {row[2]}, Средний балл: {row[3]:.2f}")

# 5. Средний балл студентов по направлениям, уровням и формам обучения
print("\n5. Средний балл по направлениям, уровням и формам обучения:")
cursor.execute("""
    SELECT p.name as program, 
           sl.name as level, 
           e.name as education_type, 
           AVG(s.average_score) as avg_score
    FROM students s
    JOIN programs p ON s.program_id = p.program_id
    JOIN study_levels sl ON s.level_id = sl.level_id
    JOIN education_types e ON s.education_type_id = e.education_type_id
    GROUP BY p.name, sl.name, e.name
""")
for row in cursor.fetchall():
    print(f"Направление: {row[0]}, Уровень: {row[1]}, Форма: {row[2]}, Средний балл: {row[3]:.2f}")

# 6. Отбор 5 студентов направления "Computer Science"
print("\n6. Топ-5 студентов направления 'Computer Science' очной формы для стипендии:")
cursor.execute("""
    SELECT s.surname, s.name, s.patronymic, s.average_score
    FROM students s
    JOIN programs p ON s.program_id = p.program_id
    JOIN education_types e ON s.education_type_id = e.education_type_id
    WHERE p.name = 'Computer Science' AND e.name = 'Full-time'
    ORDER BY s.average_score DESC
    LIMIT 5
""")
for row in cursor.fetchall():
    print(f"Студент: {row[0]} {row[1]} {row[2]}, Средний балл: {row[3]}")

# 7. Сколько однофамильцев в базе
print("\n7. Однофамильцы (фамилии, которые встречаются более 1 раза):")
cursor.execute("SELECT surname, COUNT(*) as count FROM students GROUP BY surname HAVING count > 1")
homonyms = cursor.fetchall()
for row in homonyms:
    print(f"Фамилия: {row[0]}, Количество: {row[1]}")
print(f"Общее количество однофамильцев: {sum(row[1] for row in homonyms)}")

# 8. Проверка на полных тёзок (совпадение фамилии, имени и отчества)
print("\n8. Полные тёзки (совпадение фамилии, имени и отчества):")
cursor.execute("""
    SELECT surname, name, patronymic, COUNT(*) as count
    FROM students
    GROUP BY surname, name, patronymic
    HAVING count > 1
""")
full_homonyms = cursor.fetchall()
if full_homonyms:
    for row in full_homonyms:
        print(f"Полный тёзка: {row[0]} {row[1]} {row[2]}, Количество: {row[3]}")
else:
    print("Полных тёзок нет.")
connection.close()
