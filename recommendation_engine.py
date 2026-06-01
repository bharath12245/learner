import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

def calculate_rule_based_match(user_skills, required_skills):
    """Fallback rule-based matching preserving casing for display"""
    if not required_skills:
        return 0, []

    req_list = [s.strip() for s in required_skills.split(',') if s.strip()]
    user_list_lower = [s.strip().lower() for s in user_skills if s.strip()]
    
    matched = [s for s in req_list if s.lower() in user_list_lower]
    missing = [s for s in req_list if s.lower() not in user_list_lower]
    
    match_percentage = (len(matched) / len(req_list)) * 100
    return round(match_percentage, 2), missing

def get_recommendations(user_skills, user_interests, careers):
    """
    Rank careers using Gemini semantic matching.
    Falls back to rule-based if AI fails.
    """
    load_dotenv()
    api_key = os.getenv("SMART_CAREER_GEMINI_KEY")
    
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            # Prepare career list for AI
            career_context = []
            for c in careers:
                career_context.append({
                    "id": c['career_id'],
                    "name": c['career_name'],
                    "skills": c['required_skills']
                })

            prompt = f"""
            As an expert Career Counselor, analyze this user's profile:
            Skills: {", ".join(user_skills)}
            Interests: {user_interests}

            Compare them against these possible careers:
            {json.dumps(career_context)}

            Return the TOP 3 most suitable careers in JSON format:
            [
                {{"career_id": 1, "match_percentage": 95, "reason": "short explanation"}},
                ...
            ]
            Only return the JSON array, nothing else.
            """

            response = model.generate_content(prompt)
            json_text = response.text.replace('```json', '').replace('```', '').strip()
            ai_results = json.loads(json_text)

            final_results = []
            for res in ai_results:
                career = next((c for c in careers if c['career_id'] == res['career_id']), None)
                if career:
                    _, missing = calculate_rule_based_match(user_skills, career['required_skills'])
                    final_results.append({
                        'career_id': career['career_id'],
                        'career_name': career['career_name'],
                        'match_percentage': res['match_percentage'],
                        'missing_skills': missing,
                        'salary': career['salary'],
                        'future_scope': career['future_scope'],
                        'description': career['description'],
                        'ai_reason': res['reason']
                    })
            
            if final_results:
                return final_results

        except Exception as e:
            print(f"Gemini Semantic Matching Error: {e}")

    # --- Fallback: Rule-based Ranking ---
    recommendations = []
    for career in careers:
        match_perc, missing = calculate_rule_based_match(user_skills, career['required_skills'])
        recommendations.append({
            'career_id': career['career_id'],
            'career_name': career['career_name'],
            'match_percentage': match_perc,
            'missing_skills': missing,
            'salary': career['salary'],
            'future_scope': career['future_scope'],
            'description': career['description'],
            'ai_reason': "Matched based on keyword overlap (AI unavailable)."
        })
    
    recommendations.sort(key=lambda x: x['match_percentage'], reverse=True)
    return recommendations[:3]
