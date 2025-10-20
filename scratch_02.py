import yaml
import sqlite3
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
yaml_path = os.path.join(DATA_DIR, "grammar_concept_map.yaml")
print(yaml_path)

# Load the YAML file
with open(yaml_path, 'r') as file:
    data = yaml.safe_load(file)


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
yaml_path = os.path.join(DATA_DIR, "grammar_concept_map.yaml")
# print(yaml_path)

# Connect to SQLite database (creates if it doesn't exist)
conn = sqlite3.connect('data/homework_helper.db')
cursor = conn.cursor()

# print
# Drop the table if it exists to start fresh
# cursor.execute('DROP TABLE IF EXISTS main.concept_map')

# Create the table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS main.concept_map (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT,
        category TEXT,
        topic TEXT,
        question_focus TEXT
    )
''')

# Parse the data and insert rows
grammar_data = data.get('grammar', {})
# print(grammar_data)?
subject = 'grammar'
for category, topics in grammar_data.items():
    for topic, details in topics.items():
        question_focus = details.get('question_focus', '')
        cursor.execute('''
            INSERT INTO concept_map (subject, category, topic, question_focus)
            VALUES (?, ?, ?, ?)
        ''', (subject, category, topic, question_focus))

# Commit changes and close connection
conn.commit()
conn.close()

print("Data successfully imported into homework_helper.db")