import sqlite3
import os

DB_PATH = 'career_system.db'

def init_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("Existing database removed for fresh start.")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Users Table
    cursor.execute('''
    CREATE TABLE users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        interests TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # User Skills Table
    cursor.execute('''
    CREATE TABLE user_skills (
        skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        skill_name TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    )
    ''')

    # Careers Table
    cursor.execute('''
    CREATE TABLE careers (
        career_id INTEGER PRIMARY KEY AUTOINCREMENT,
        career_name TEXT NOT NULL,
        required_skills TEXT NOT NULL,
        salary TEXT,
        future_scope TEXT,
        companies_hiring TEXT,
        description TEXT
    )
    ''')

    # Seed Data
    careers = [
        ('AI Engineer', 'Python, Machine Learning, Deep Learning, SQL', '$100k - $180k', 'Huge growth with the rise of LLMs.', 'Google, Meta, OpenAI, Microsoft', 'Build and deploy intelligent models.'),
        ('Web Developer', 'HTML, CSS, JavaScript, React, Node.js', '$70k - $130k', 'Steady demand for digital transformation.', 'Amazon, Netflix, Adobe, Shopify', 'Create responsive and dynamic websites.'),
        ('UI/UX Designer', 'Figma, Adobe XD, Design Principles', '$65k - $120k', 'Critical for product success.', 'Apple, Airbnb, Uber, Spotify', 'Design intuitive user interfaces.'),
        ('Data Scientist', 'Python, SQL, Statistics, Visualization', '$90k - $150k', 'Essential for data-driven decisions.', 'Tencent, IBM, Oracle, Walmart', 'Extract insights from large datasets.'),
        ('Backend Developer', 'Java, Spring Boot, SQL, Docker', '$80k - $140k', 'Core infrastructure needs.', 'JPMorgan, Goldman Sachs, AWS, PayPal', 'Develop and maintain server-side logic.')
    ]

    cursor.executemany('INSERT INTO careers (career_name, required_skills, salary, future_scope, companies_hiring, description) VALUES (?, ?, ?, ?, ?, ?)', careers)

    conn.commit()
    conn.close()
    print("Database successfully initialized with ALL columns!")

if __name__ == '__main__':
    init_db()
