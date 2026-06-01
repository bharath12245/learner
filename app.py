from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
from database import execute_query
from recommendation_engine import get_recommendations
import os, csv, io, json
from dotenv import load_dotenv
import google.generativeai as genai
from collections import Counter
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "smart_career_secret_key")

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash("Admin access required. Please login.", "danger")
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

print("\n" + "="*40)
print("[START] SMART CAREER SYSTEM: DASHBOARD PRO")
print("="*40)

# Startup AI Test
def test_gemini():
    api_key = os.getenv("SMART_CAREER_GEMINI_KEY")
    if not api_key: return
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        model.generate_content("test")
        print("[SUCCESS] GEMINI AI READY")
    except Exception as e: print(f"[ERROR] AI FAILED: {e}")

test_gemini()

# Structured Mock Fallbacks for Default Careers
FALLBACK_ROADMAPS = {
    "AI Engineer": {
        "mentor_intro": "Welcome! Transitioning into AI Engineering requires a blend of solid mathematical principles and modern programming practices. Here is your structured, professional path.",
        "timeline_duration": "6-8 Months",
        "steps": [
            {
                "step_number": 1,
                "title": "Master Python & Scientific Computing",
                "duration": "Weeks 1-8",
                "focus": "Programming syntax, data analysis, and mathematical foundations.",
                "topics": ["Python OOP", "NumPy & Pandas", "Linear Algebra & Probability", "SQL databases"],
                "project": {
                    "title": "Global Climate Patterns Dashboard",
                    "description": "Analyze and visualize 50 years of temperature data using Pandas and Matplotlib."
                },
                "resources": ["Python for Data Analysis (Book)", "Stanford CS229 Linear Algebra Review"]
            },
            {
                "step_number": 2,
                "title": "Classical Machine Learning",
                "duration": "Weeks 9-16",
                "focus": "Supervised, unsupervised algorithms and feature engineering.",
                "topics": ["Regression & Classification", "Random Forests & SVMs", "Scikit-Learn", "Evaluation Metrics"],
                "project": {
                    "title": "Predictive Real Estate Valuation",
                    "description": "Train a model using Scikit-Learn to estimate home values based on spatial and historical features."
                },
                "resources": ["Hands-On Machine Learning with Scikit-Learn (Book)"]
            },
            {
                "step_number": 3,
                "title": "Deep Learning & Modern AI",
                "duration": "Weeks 17-24+",
                "focus": "Neural networks, frameworks, and large language models.",
                "topics": ["PyTorch basics", "CNNs & RNNs", "Transformers & LLM API integration", "Model Deployment"],
                "project": {
                    "title": "Semantic Document QA Chatbot",
                    "description": "Build an app that indexes PDFs into a vector database (Chroma) and runs RAG using a Gemini LLM."
                },
                "resources": ["Fast.ai - Practical Deep Learning for Coders", "Hugging Face Course"]
            }
        ],
        "mentor_advice": "Focus heavily on understanding *why* algorithms work rather than just calling .fit(). A great AI engineer is a debugger of neural weights and data distributions."
    },
    "Web Developer": {
        "mentor_intro": "Welcome! Web development is a dynamic, highly rewarding field. To stand out, you need to understand both clean client interfaces and robust backend integration.",
        "timeline_duration": "4-6 Months",
        "steps": [
            {
                "step_number": 1,
                "title": "Semantic HTML, Responsive CSS & JS Core",
                "duration": "Weeks 1-6",
                "focus": "Structure, styling, and standard client-side scripting.",
                "topics": ["HTML5 semantics", "Flexbox & CSS Grid", "ES6+ JavaScript", "DOM manipulation"],
                "project": {
                    "title": "Interactive Financial Portfolio Tracker",
                    "description": "Design a responsive frontend app that consumes a public stock API to track mock asset performance."
                },
                "resources": ["MDN Web Docs", "JavaScript.info", "CSS-Tricks"]
            },
            {
                "step_number": 2,
                "title": "Modern Frontend Frameworks",
                "duration": "Weeks 7-14",
                "focus": "State management, component lifecycles, and build tools.",
                "topics": ["React.js / Vue.js", "State (Redux / Context)", "REST API consumption", "Tailwind CSS"],
                "project": {
                    "title": "Collaborative Kanban Board",
                    "description": "Build a task planner (Trello clone) with drag-and-drop mechanics, column lists, and user state."
                },
                "resources": ["React Dev Docs (react.dev)", "Frontend Masters"]
            },
            {
                "step_number": 3,
                "title": "Fullstack Web & Deployment",
                "duration": "Weeks 15-20+",
                "focus": "Backend databases, user authentication, and hosting.",
                "topics": ["Node.js & Express", "SQL / NoSQL (MongoDB)", "JWT Authentication", "Hosting (Vercel, Render)"],
                "project": {
                    "title": "SaaS E-Commerce MVP",
                    "description": "Develop a full-stack store with product listings, user checkout, and payment gateway integration (Stripe sandbox)."
                },
                "resources": ["The Odin Project", "Full Stack Open (University of Helsinki)"]
            }
        ],
        "mentor_advice": "Don't get stuck in tutorial hell. Always build custom projects and solve actual deployment problems. Deploy early and deploy often!"
    },
    "UI/UX Designer": {
        "mentor_intro": "Welcome to UI/UX design. Creating seamless, beautiful human-computer interfaces requires a balance of empathy, cognitive science, and refined visual design capabilities.",
        "timeline_duration": "4-6 Months",
        "steps": [
            {
                "step_number": 1,
                "title": "Design Principles & User Research",
                "duration": "Weeks 1-6",
                "focus": "Learn user empathy, informational layout, and sketching wireframes.",
                "topics": ["User Empathy Mapping", "Wireframing & Flowcharts", "Information Architecture", "User Research Methods"],
                "project": {
                    "title": "Local Community App Wireframes",
                    "description": "Run interviews and draw low-fidelity user flows and wireframes for a community volunteering mobile application."
                },
                "resources": ["Nielsen Norman Group Articles", "Interaction Design Foundation Courses"]
            },
            {
                "step_number": 2,
                "title": "High-Fidelity Visual Design & Prototyping",
                "duration": "Weeks 7-12",
                "focus": "Learn layout design, master Figma, and build animations.",
                "topics": ["Figma mastery", "Typography & Grids", "Color Theory", "High-fidelity interactive prototyping"],
                "project": {
                    "title": "Interactive Smart Home Dashboard",
                    "description": "Create a stunning high-fidelity tablet UI for controlling domestic appliances with interactive states."
                },
                "resources": ["Figma Help Center & Tutorials", "Refactoring UI (Book)"]
            },
            {
                "step_number": 3,
                "title": "Usability Testing & Design Systems",
                "duration": "Weeks 13-18+",
                "focus": "Validate designs with users, write design systems, and manage developer handoffs.",
                "topics": ["Usability Testing", "Design System components", "Auto Layout & Variables", "Developer Handoff spec sheets"],
                "project": {
                    "title": "Responsive SaaS Platform Design",
                    "description": "Develop a unified design system and visual layouts for desktop and mobile web SaaS apps, testing with 5 real users."
                },
                "resources": ["Laws of UX Website", "Google Material Design Guidelines"]
            }
        ],
        "mentor_advice": "Always design with the user's goals in mind, not your own aesthetic preferences. Test your prototypes with real people early and often."
    },
    "Data Scientist": {
        "mentor_intro": "A great data scientist translates raw data numbers into narrative patterns that drive business decisions. Here is your analytical roadmap.",
        "timeline_duration": "6-8 Months",
        "steps": [
            {
                "step_number": 1,
                "title": "Structured Querying & Exploratory Analysis",
                "duration": "Weeks 1-6",
                "focus": "Descriptive statistics, querying databases, and manipulating datasets.",
                "topics": ["Advanced SQL", "Pandas data wrangling", "Descriptive statistics", "Matplotlib & Seaborn visualizations"],
                "project": {
                    "title": "Consumer Behavior Exploratory Dashboard",
                    "description": "Extract, clean, and visualize user retention trends from a relational transaction database."
                },
                "resources": ["Kaggle SQL Tutorials", "Python for Data Analysis (Book)"]
            },
            {
                "step_number": 2,
                "title": "Inferential Statistics & Machine Learning",
                "duration": "Weeks 7-14",
                "focus": "Statistical hypothesis testing, forecasting, and supervised ML.",
                "topics": ["Probability distributions", "A/B Testing", "Regression & Classification models", "Scikit-Learn pipeline creation"],
                "project": {
                    "title": "E-Commerce A/B Test Optimizer",
                    "description": "Evaluate conversion rate changes between two web layouts and build a random forest model to predict user buy intent."
                },
                "resources": ["Introduction to Statistical Learning (Book)", "Khan Academy Probability & Statistics"]
            },
            {
                "step_number": 3,
                "title": "Production Models & Storytelling",
                "duration": "Weeks 15-20+",
                "focus": "Production deployments, model monitoring, and executive communication.",
                "topics": ["Feature engineering at scale", "Pipeline automation", "Tableau / Streamlit dashboard development", "ML deployment basics"],
                "project": {
                    "title": "Credit Risk Underwriting Pipeline",
                    "description": "Build a deployment-ready Streamlit app that runs an underwriting algorithm and explains predictions via SHAP values."
                },
                "resources": ["Machine Learning Engineering (Book)", "Streamlit Docs"]
            }
        ],
        "mentor_advice": "The best data scientists are great storytellers. Your insights are only as valuable as your ability to explain them to a non-technical stakeholder."
    },
    "Backend Developer": {
        "mentor_intro": "Developing scalable backend systems is about reliability, performance under load, and designing clean APIs. Here is your infrastructure guide.",
        "timeline_duration": "5-7 Months",
        "steps": [
            {
                "step_number": 1,
                "title": "Core Backend Language & Databases",
                "duration": "Weeks 1-6",
                "focus": "Object-oriented programming, database relations, and Git version control.",
                "topics": ["Java / Python OOP", "Relational Databases & SQL Schema design", "Git branch workflows"],
                "project": {
                    "title": "Multi-user Library Management API",
                    "description": "Create a command-line backend with standard SQL integration, handling book loans and database updates."
                },
                "resources": ["Head First Java / Python", "SQLBolt interactive tutorials"]
            },
            {
                "step_number": 2,
                "title": "RESTful Web Services & Frameworks",
                "duration": "Weeks 7-14",
                "focus": "API architecture, security, authentication, and endpoint testing.",
                "topics": ["Spring Boot / Django REST Framework", "REST API architecture", "JWT Authentication", "Unit & Integration Testing"],
                "project": {
                    "title": "Secure Blog Platform Engine",
                    "description": "Develop a backend API allowing users to register, publish posts, leave nested comments, secured via token auth."
                },
                "resources": ["Spring Academy website", "Django Project documentation"]
            },
            {
                "step_number": 3,
                "title": "System Scalability & Cloud Deployment",
                "duration": "Weeks 15-22+",
                "focus": "Microservices, caching, containerization, and basic cloud architecture.",
                "topics": ["Microservices", "Docker containerization", "Redis caching layer", "AWS/GCP server deployments"],
                "project": {
                    "title": "High-Traffic Real-Time Chat Gateway",
                    "description": "Develop a containerized backend using WebSockets, storing chat histories in Redis and deploying to a cloud container runtime."
                },
                "resources": ["ByteByteGo System Design primer", "Docker Curriculum guide"]
            }
        ],
        "mentor_advice": "Understand the basics of networking (TCP/IP, HTTP codes, DNS) first. The best backend engineers build systems that are easy to monitor and fail gracefully."
    }
}

def get_generic_fallback_roadmap(career_name, required_skills):
    skills_list = [s.strip() for s in required_skills.split(',') if s.strip()]
    return {
        "mentor_intro": f"Welcome to your career journey to become a {career_name}. This structured path is customized to help you master the key skills and step into the industry.",
        "timeline_duration": "6 Months",
        "steps": [
            {
                "step_number": 1,
                "title": f"Foundations of {career_name}",
                "duration": "Weeks 1-6",
                "focus": f"Learn the essential basics and tools of {career_name}.",
                "topics": skills_list[:3] if len(skills_list) >= 3 else skills_list + ["Core Concepts"],
                "project": {
                    "title": f"Basic {career_name} Project",
                    "description": f"Build a prototype app or script demonstrating the core principles of {career_name}."
                },
                "resources": ["Official Documentation", "Foundational online tutorials"]
            },
            {
                "step_number": 2,
                "title": "Intermediate Specialization",
                "duration": "Weeks 7-12",
                "focus": "Develop deeper skills and learn intermediate technologies.",
                "topics": skills_list[3:6] if len(skills_list) >= 6 else skills_list[-2:] + ["API Integration"],
                "project": {
                    "title": f"Feature-Rich {career_name} Application",
                    "description": "Develop a structured application incorporating intermediate logic and API connections."
                },
                "resources": ["Intermediate online courses", "Recommended GitHub repositories"]
            },
            {
                "step_number": 3,
                "title": "Advanced Capstone & Deployment",
                "duration": "Weeks 13-18+",
                "focus": "Complete a production-grade portfolio project and deploy it.",
                "topics": ["Testing & Performance", "Cloud Hosting", "Continuous Integration"],
                "project": {
                    "title": f"Production-Grade {career_name} Capstone",
                    "description": f"Deploy a fully functional, high-quality system demonstrating mastery of {career_name}."
                },
                "resources": ["Industry Best Practices documentation", "Interview preparation guides"]
            }
        ],
        "mentor_advice": "Stay consistent, practice code daily, and start networking on LinkedIn and GitHub!"
    }

# Helper for AI Roadmaps
def get_ai_roadmap(career_name, user_skills, required_skills):
    api_key = os.getenv("SMART_CAREER_GEMINI_KEY")
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = f"""
        Act as an elite industry mentor and professional career counselor.
        Create a detailed, professional 3-step learning and career roadmap to help a student transition into a '{career_name}' role.

        Student's Current Skills: {user_skills}
        Required Role Skills: {required_skills}

        You MUST respond ONLY with a valid JSON object matching this schema. Do not output any markdown blocks (like ```json), explanations, or text outside the JSON.

        JSON Schema:
        {{
            "mentor_intro": "A professional, inspiring introduction acting as a mentor, customized to the student's current skills and target role.",
            "timeline_duration": "Estimated total time to readiness (e.g., '6-8 Months')",
            "steps": [
                {{
                    "step_number": 1,
                    "title": "Name of Step 1 (Focus on foundational gaps)",
                    "duration": "Estimated duration (e.g., 'Weeks 1-6')",
                    "focus": "Brief focus description",
                    "topics": ["Specific technology/topic 1", "Specific technology/topic 2", "Specific technology/topic 3"],
                    "project": {{
                        "title": "Name of a concrete portfolio-grade project for this step",
                        "description": "Detailed description of what the project does and what it demonstrates."
                    }},
                    "resources": ["Resource 1 (e.g., specific course or documentation)", "Resource 2"]
                }},
                {{
                    "step_number": 2,
                    "title": "Name of Step 2 (Focus on intermediate specialization)",
                    "duration": "Estimated duration (e.g., 'Weeks 7-12')",
                    "focus": "Brief focus description",
                    "topics": ["Intermediate topic 1", "Intermediate topic 2"],
                    "project": {{
                        "title": "Project name",
                        "description": "Detailed description of the project."
                    }},
                    "resources": ["Resource 1", "Resource 2"]
                }},
                {{
                    "step_number": 3,
                    "title": "Name of Step 3 (Focus on advanced integration and deployment)",
                    "duration": "Estimated duration (e.g., 'Weeks 13-18+')",
                    "focus": "Brief focus description",
                    "topics": ["Advanced topic 1", "Advanced topic 2"],
                    "project": {{
                        "title": "Capstone project name",
                        "description": "Detailed description of the project."
                    }},
                    "resources": ["Resource 1", "Resource 2"]
                }}
            ],
            "mentor_advice": "A professional concluding piece of mentorship advice, encouragement, or industry standard tip."
        }}
        """
        response = model.generate_content(prompt)
        text = response.text.replace('```json', '').replace('```', '').strip()
        parsed = json.loads(text)
        return parsed
    except Exception as e:
        print(f"Roadmap AI generation error: {e}")
        return None

# --- Middleware ---
@app.context_processor
def inject_now():
    from datetime import datetime
    return {'now': datetime.utcnow()}

# --- Core Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            name, email, password = request.form.get('name'), request.form.get('email'), request.form.get('password')
            skills_raw, interests = request.form.get('skills', ''), request.form.get('interests', '')
            skills = [s.strip() for s in skills_raw.split(',') if s.strip()]
            
            # Check duplicate email
            existing = execute_query("SELECT user_id FROM users WHERE email = ?", (email,), fetch=True)
            if existing:
                flash("Email address already registered. Please login or use a different email.", "warning")
                return redirect(url_for('register'))
                
            hashed_password = generate_password_hash(password)
            execute_query("INSERT INTO users (name, email, password, interests) VALUES (?, ?, ?, ?)", (name, email, hashed_password, interests))
            user = execute_query("SELECT user_id FROM users WHERE email = ?", (email,), fetch=True)[0]
            
            for skill in skills: 
                execute_query("INSERT INTO user_skills (user_id, skill_name) VALUES (?, ?)", (user['user_id'], skill))
                
            session.update({'user_id': user['user_id'], 'user_name': name, 'user_skills': skills, 'user_interests': interests})
            return redirect(url_for('results'))
        except Exception as e: 
            flash(f"Registration Error: {e}", "danger")
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = execute_query("SELECT * FROM users WHERE email = ?", (request.form['email'],), fetch=True)
        if user:
            u = user[0]
            if check_password_hash(u['password'], request.form['password']):
                skills = execute_query("SELECT skill_name FROM user_skills WHERE user_id = ?", (u['user_id'],), fetch=True)
                session.update({'user_id': u['user_id'], 'user_name': u['name'], 'user_interests': u['interests'], 'user_skills': [s['skill_name'] for s in skills]})
                return redirect(url_for('results'))
        flash("Invalid email or password", "danger")
    return render_template('login.html')

@app.route('/results')
def results():
    if 'user_id' not in session: return redirect(url_for('login'))
    careers = execute_query("SELECT * FROM careers", fetch=True)
    recs = get_recommendations(session.get('user_skills', []), session.get('user_interests', ''), careers)
    return render_template('results.html', recommendations=recs)

@app.route('/search')
def search():
    q = request.args.get('q', '')
    careers = execute_query("SELECT * FROM careers WHERE career_name LIKE ? OR description LIKE ? OR required_skills LIKE ?", (f'%{q}%', f'%{q}%', f'%{q}%'), fetch=True)
    return render_template('search.html', careers=careers, query=q)

@app.route('/career/<int:career_id>')
def career_detail(career_id):
    career = execute_query("SELECT * FROM careers WHERE career_id = ?", (career_id,), fetch=True)
    if not career: return redirect(url_for('results'))
    return render_template('career_detail.html', career=career[0])

@app.route('/generate_roadmap/<int:career_id>')
def generate_roadmap(career_id):
    career = execute_query("SELECT * FROM careers WHERE career_id = ?", (career_id,), fetch=True)
    if not career: return jsonify({"error": "Not found"}), 404
    
    career_name = career[0]['career_name']
    required_skills = career[0]['required_skills']
    user_skills_str = ", ".join(session.get('user_skills', []))
    
    # Try calling AI
    roadmap = get_ai_roadmap(career_name, user_skills_str, required_skills)
    
    # Fallback if AI fails or key is missing
    if not roadmap:
        print(f"Fallback mode activated for career: {career_name}")
        roadmap = FALLBACK_ROADMAPS.get(career_name)
        if not roadmap:
            # Generate generic dynamic fallback based on required skills
            roadmap = get_generic_fallback_roadmap(career_name, required_skills)
            
    return jsonify(roadmap)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- Admin Routes ---
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('email') == 'admin@career.com' and request.form.get('password') == 'admin123':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        flash("Admin access denied")
    return render_template('admin/login.html')

@app.route('/admin')
@admin_required
def admin_dashboard():
    # Calculate Real Stats
    all_users = execute_query("SELECT * FROM users", fetch=True)
    all_careers = execute_query("SELECT * FROM careers", fetch=True)
    
    # Dynamic Recommendation Share
    tally = Counter()
    for u in all_users:
        u_skills = execute_query("SELECT skill_name FROM user_skills WHERE user_id = ?", (u['user_id'],), fetch=True)
        skills_list = [s['skill_name'] for s in u_skills]
        recs = get_recommendations(skills_list, u['interests'] or '', all_careers)
        if recs:
            tally[recs[0]['career_name']] += 1
            
    chart_labels = list(tally.keys())
    chart_data = list(tally.values())
    
    # Fallback if no user tallies
    if not chart_labels and all_careers:
        chart_labels = [c['career_name'] for c in all_careers]
        chart_data = [0] * len(all_careers)
        
    most_rec_tally = tally.most_common(1)
    top_career = most_rec_tally[0][0] if most_rec_tally else "None"
    
    # Skill Distribution Data
    all_skills = execute_query("SELECT skill_name FROM user_skills", fetch=True)
    skill_counts = Counter([s['skill_name'] for s in all_skills]).most_common(5)
    
    stats = {
        'total_users': len(all_users),
        'total_searches': len(all_users) * 3, # Mock for demo
        'most_recommended': top_career,
        'skill_counts': skill_counts,
        'recent_users': all_users[-5:] if all_users else [],
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data)
    }
    return render_template('admin/dashboard.html', **stats)

@app.route('/admin/users')
@admin_required
def manage_users():
    users = execute_query("SELECT * FROM users", fetch=True)
    final_users = []
    for u in users:
        u_dict = dict(u)
        skills = execute_query("SELECT skill_name FROM user_skills WHERE user_id = ?", (u['user_id'],), fetch=True)
        u_dict['skills'] = ", ".join([s['skill_name'] for s in skills])
        u_dict['id'] = u['user_id']
        final_users.append(u_dict)
    return render_template('admin/users.html', users=final_users)

@app.route('/admin/users/delete/<int:user_id>')
@admin_required
def delete_user(user_id):
    execute_query("DELETE FROM users WHERE user_id = ?", (user_id,))
    flash("User deleted")
    return redirect(url_for('manage_users'))

@app.route('/admin/users/export')
@admin_required
def export_users():
    users = execute_query("SELECT * FROM users", fetch=True)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Email', 'Interests'])
    for u in users: writer.writerow([u['user_id'], u['name'], u['email'], u['interests']])
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-disposition": "attachment; filename=users.csv"})

@app.route('/admin/careers')
@admin_required
def manage_careers():
    careers = execute_query("SELECT * FROM careers", fetch=True)
    return render_template('admin/manage_careers.html', careers=careers)

@app.route('/admin/careers/add', methods=['POST'])
@admin_required
def add_career():
    f = request.form
    execute_query("INSERT INTO careers (career_name, required_skills, salary, future_scope, companies_hiring, description) VALUES (?,?,?,?,?,?)",
                  (f['career_name'], f['required_skills'], f['salary'], f['future_scope'], f['companies_hiring'], f['description']))
    return redirect(url_for('manage_careers'))

@app.route('/admin/careers/edit/<int:career_id>', methods=['POST'])
@admin_required
def edit_career(career_id):
    f = request.form
    execute_query("UPDATE careers SET career_name=?, required_skills=?, salary=?, future_scope=?, companies_hiring=?, description=? WHERE career_id=?",
                  (f['career_name'], f['required_skills'], f['salary'], f['future_scope'], f['companies_hiring'], f['description'], career_id))
    return redirect(url_for('manage_careers'))

@app.route('/admin/careers/delete/<int:career_id>')
@admin_required
def delete_career(career_id):
    execute_query("DELETE FROM careers WHERE career_id = ?", (career_id,))
    return redirect(url_for('manage_careers'))

@app.route('/mentor_chat', methods=['POST'])
def mentor_chat():
    data = request.get_json() or {}
    message = data.get('message', '')
    career_name = data.get('career_name', '')
    
    if not message or not career_name:
        return jsonify({"response": "I didn't receive a message or career context. Please ask again!"}), 400
        
    api_key = os.getenv("SMART_CAREER_GEMINI_KEY")
    
    try:
        if api_key and api_key != "your_gemini_api_key_here":
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')
            prompt = f"""
            Act as an elite tech industry recruiter and professional career mentor.
            The user is asking a question about preparing for a career as a '{career_name}'.
            Question: "{message}"
            
            Provide a concise, professional, and actionable answer (maximum 3-4 sentences). Act as a supportive but realistic guide.
            """
            response = model.generate_content(prompt)
            return jsonify({"response": response.text.strip()})
    except Exception as e:
        print(f"Mentor chat AI error: {e}")
        
    # Fallback response system when AI key is missing or fails
    fallback_responses = {
        "AI Engineer": [
            "To excel as an AI Engineer, focus on mastering linear algebra, statistics, and PyTorch pipelines. Practical experience with data modeling is more important than theoretical exams.",
            "For junior roles, building 2-3 end-to-end projects (like a fine-tuned text agent or object detection app) and hosting them on GitHub will instantly put you ahead of other applicants.",
            "I highly recommend keeping an eye on MLops tools like MLflow or Docker, as deployment skills are in extremely high demand right now."
        ],
        "Web Developer": [
            "In Web Development, consistency in building and deployment is key. Build a clean responsive portfolio site and host it on Vercel or Netlify to showcase your DOM and CSS skills.",
            "For interviews, practice coding core JavaScript without frameworks to prove you understand how asynchronous calls, event handlers, and data scopes work.",
            "Modern companies look for developers who understand Git workflows and CI/CD pipelines, so make sure your GitHub profile shows collaborative pull requests."
        ],
        "UI/UX Designer": [
            "To build a strong design portfolio, include at least one complete case study showing your wireframes, user research steps, and how you solved user friction.",
            "Figma is the industry standard. Focus on mastering variables, auto-layouts, and component libraries to show developers you design with implementation in mind.",
            "Usability testing is critical. Make sure you can explain why you made specific layout choices based on user feedback, not just personal aesthetic tastes."
        ],
        "Data Scientist": [
            "For Data Science, ensure you are comfortable writing clean SQL queries. Most real-world work involves gathering and cleaning data before any modeling starts.",
            "Understand mathematical model parameters (like why tree depth matters or how loss functions are calculated) rather than just calling import statements.",
            "Create interactive dashboards using tools like Streamlit or Tableau to communicate your findings clearly to non-technical managers."
        ],
        "Backend Developer": [
            "In Backend Development, focus on system design fundamentals, database normalization, and RESTful constraints.",
            "Mastering relational SQL databases is critical. Be prepared to explain database index optimization and how join statements work under the hood.",
            "Understand containerization (Docker) and basic microservice structures, as modern cloud infrastructure relies heavily on these frameworks."
        ]
    }
    
    import random
    replies = fallback_responses.get(career_name, [
        f"Master the core required skills for {career_name}, build a solid portfolio project, and ensure you deploy your work so employers can test it.",
        f"Networking is just as important as coding. Connect with professionals working as a {career_name} on LinkedIn and join tech community meetups.",
        "Take one skill at a time, practice daily, and don't rush through tutorials. Building projects from scratch is where real learning happens."
    ])
    
    return jsonify({"response": random.choice(replies)})

if __name__ == '__main__':
    app.run(debug=True)
