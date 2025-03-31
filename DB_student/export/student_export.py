import sqlite3

connection = sqlite3.connect("STUDENT.db")
cursor = connection.cursor()

cursor.executescript("""
CREATE TABLE IF NOT EXISTS `study_levels` (
    `level_id` INTEGER NOT NULL PRIMARY KEY UNIQUE,
    `name` VARCHAR NOT NULL
);
CREATE TABLE IF NOT EXISTS `programs` (
    `program_id` INTEGER NOT NULL PRIMARY KEY UNIQUE,
    `name` VARCHAR NOT NULL
);
CREATE TABLE IF NOT EXISTS `education_types` (
    `education_type_id` INTEGER NOT NULL PRIMARY KEY UNIQUE,
    `name` VARCHAR NOT NULL
);
CREATE TABLE IF NOT EXISTS `students` (
    `student_id` INTEGER NOT NULL PRIMARY KEY UNIQUE,
    `level_id` INTEGER NOT NULL,
    `program_id` INTEGER NOT NULL,
    `education_type_id` INTEGER NOT NULL,
    `surname` VARCHAR NOT NULL,
    `name` VARCHAR NOT NULL,
    `patronymic` VARCHAR NOT NULL,
    `average_score` INTEGER NOT NULL,
    FOREIGN KEY (`level_id`) REFERENCES `study_levels` (`level_id`),
    FOREIGN KEY (`program_id`) REFERENCES `programs` (`program_id`),
    FOREIGN KEY (`education_type_id`) REFERENCES `education_types` (`education_type_id`)
);
""")


for table, file in [
    ('study_levels', 'study_levels.txt'),
    ('programs', 'programs.txt'),
    ('education_types', 'education_types.txt'),
    ('students', 'students.txt')
]:
    with open(file, 'r', encoding='utf-8') as f:
        for line in f:
            fields = line.strip().split(',')
            if table == 'students':
                fields[-1] = int(fields[-1])
            cursor.execute(f"INSERT INTO {table} VALUES ({','.join(['?' for _ in fields])})", fields)

connection.commit()
connection.close()

print("Данные успешно добавлены в базу данных!")
