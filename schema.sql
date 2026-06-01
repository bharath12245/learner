CREATE DATABASE IF NOT EXISTS career_system;
USE career_system;

-- Careers Table
CREATE TABLE IF NOT EXISTS careers (
    career_id INT AUTO_INCREMENT PRIMARY KEY,
    career_name VARCHAR(255) NOT NULL,
    required_skills TEXT NOT NULL,
    salary VARCHAR(100),
    future_scope TEXT,
    companies_hiring TEXT,
    description TEXT
);

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    skills TEXT,
    interests TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Search History / Recommendations Table
CREATE TABLE IF NOT EXISTS recommendations (
    rec_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    career_id INT,
    match_percentage DECIMAL(5,2),
    missing_skills TEXT,
    search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (career_id) REFERENCES careers(career_id) ON DELETE CASCADE
);

-- Seed Data for Careers
INSERT INTO careers (career_name, required_skills, salary, future_scope, companies_hiring, description) VALUES
('AI Engineer', 'Python, Machine Learning, Deep Learning, SQL, Statistics', '$100k - $180k', 'Huge growth with the rise of LLMs and automation.', 'Google, Meta, OpenAI, Microsoft', 'Build and deploy intelligent models to solve complex problems.'),
('Web Developer', 'HTML, CSS, JavaScript, React, Node.js, SQL', '$70k - $130k', 'Steady demand for digital transformation and SaaS.', 'Amazon, Netflix, Adobe, Shopify', 'Create responsive and dynamic websites and web applications.'),
('UI/UX Designer', 'Figma, Adobe XD, Design Principles, User Research, HTML, CSS', '$65k - $120k', 'Critical for product success in a user-centric world.', 'Apple, Airbnb, Uber, Spotify', 'Design intuitive and beautiful user interfaces and experiences.'),
('Data Scientist', 'Python, R, SQL, Data Visualization, Statistics, Machine Learning', '$90k - $150k', 'Essential for data-driven decision making.', 'Tencent, IBM, Oracle, Walmart', 'Extract insights from large datasets to guide business strategy.'),
('Backend Developer', 'Java, Spring Boot, SQL, Docker, Microservices', '$80k - $140k', 'Core infrastructure needs for cloud services.', 'JPMorgan, Goldman Sachs, AWS, PayPal', 'Develop and maintain server-side logic and database integration.');
