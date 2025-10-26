import json
import os
from typing import Dict, List, Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class SkillsManager:
    """AI-powered skills database manager"""
    
    def __init__(self):
        self.skills_file = os.path.join(os.path.dirname(__file__), "skills.json")
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
            print("Warning: GEMINI_API_KEY not found. Using fallback skills database.")
    
    def generate_skills_database(self) -> Dict:
        """Generate comprehensive skills database using AI"""
        if not self.model:
            return self._get_fallback_skills()
        
        prompt = """
        Generate a comprehensive skills database for resume parsing and job matching.
        Return a JSON object with these categories:
        - programming_languages: Popular programming languages
        - web_technologies: Frontend, backend, and web frameworks
        - databases: SQL and NoSQL databases
        - cloud_platforms: Cloud providers and DevOps tools
        - data_science: ML, AI, and data analysis tools
        - mobile_development: Mobile development frameworks and tools
        - devops_tools: CI/CD, version control, deployment tools
        - testing: Testing frameworks and tools
        - design_tools: UI/UX and graphic design tools
        - project_management: Project management and collaboration tools
        - soft_skills: Important soft skills for tech roles
        - certifications: Industry certifications and credentials
        
        Each category should have 15-25 relevant, current skills/tools.
        Focus on popular, in-demand technologies as of 2024.
        Return only valid JSON, no additional text.
        """
        
        try:
            response = self.model.generate_content(prompt)
            content = response.text.strip()
            
            # Clean JSON formatting
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
            
            skills_data = json.loads(content)
            return skills_data
            
        except Exception as e:
            print(f"Error generating skills database with AI: {e}")
            return self._get_fallback_skills()
    
    def load_or_create_skills_database(self) -> Dict:
        """Load existing skills database or create new one"""
        if os.path.exists(self.skills_file):
            try:
                with open(self.skills_file, 'r', encoding='utf-8') as f:
                    skills_data = json.load(f)
                    # Validate the structure
                    if self._validate_skills_structure(skills_data):
                        return skills_data
                    else:
                        print("Invalid skills database structure. Regenerating...")
            except Exception as e:
                print(f"Error loading skills database: {e}. Regenerating...")
        
        # Generate new skills database
        print("Generating skills database using AI...")
        skills_data = self.generate_skills_database()
        self.save_skills_database(skills_data)
        return skills_data
    
    def save_skills_database(self, skills_data: Dict):
        """Save skills database to JSON file"""
        try:
            os.makedirs(os.path.dirname(self.skills_file), exist_ok=True)
            with open(self.skills_file, 'w', encoding='utf-8') as f:
                json.dump(skills_data, f, indent=2, ensure_ascii=False)
            print(f"✅ Skills database saved to: {self.skills_file}")
        except Exception as e:
            print(f"❌ Error saving skills database: {e}")
    
    def update_skills_with_new_technology(self, technology: str, category: Optional[str] = None):
        """Add new technology to skills database using AI categorization"""
        if not self.model:
            print("AI model not available for skill categorization")
            return False
        
        skills_data = self.load_or_create_skills_database()
        
        if not category:
            # Use AI to determine the best category
            prompt = f"""
            Given this technology/skill: "{technology}"
            
            Determine which category it belongs to from these options:
            {', '.join(skills_data.keys())}
            
            Return only the category name, nothing else.
            """
            
            try:
                response = self.model.generate_content(prompt)
                category = response.text.strip().lower().replace(' ', '_')
            except Exception as e:
                print(f"Error categorizing skill: {e}")
                return False
        
        # Add to appropriate category
        if category in skills_data:
            if technology not in skills_data[category]:
                skills_data[category].append(technology)
                skills_data[category].sort()
                self.save_skills_database(skills_data)
                print(f"✅ Added '{technology}' to '{category}' category")
                return True
            else:
                print(f"'{technology}' already exists in '{category}' category")
                return False
        else:
            print(f"Category '{category}' not found")
            return False
    
    def refresh_skills_database(self):
        """Regenerate skills database with latest technologies"""
        print("Refreshing skills database with latest technologies...")
        skills_data = self.generate_skills_database()
        self.save_skills_database(skills_data)
        print("✅ Skills database refreshed!")
    
    def get_trending_skills(self, category: Optional[str] = None) -> List[str]:
        """Get trending skills using AI analysis"""
        if not self.model:
            return []
        
        category_filter = f" in {category}" if category else ""
        prompt = f"""
        List the top 10 trending technologies and skills{category_filter} as of 2024.
        Focus on:
        - Technologies gaining popularity
        - Skills in high demand
        - Emerging frameworks and tools
        
        Return as a simple JSON array of skill names only.
        """
        
        try:
            response = self.model.generate_content(prompt)
            content = response.text.strip()
            
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
            
            trending = json.loads(content)
            return trending if isinstance(trending, list) else []
            
        except Exception as e:
            print(f"Error getting trending skills: {e}")
            return []
    
    def _validate_skills_structure(self, skills_data: Dict) -> bool:
        """Validate skills database structure"""
        required_categories = [
            'programming_languages', 'web_technologies', 'databases',
            'cloud_platforms', 'data_science', 'mobile_development',
            'devops_tools', 'testing', 'design_tools', 'project_management',
            'soft_skills', 'certifications'
        ]
        
        if not isinstance(skills_data, dict):
            return False
        
        for category in required_categories:
            if category not in skills_data or not isinstance(skills_data[category], list):
                return False
        
        return True
    
    def _get_fallback_skills(self) -> Dict:
        """Fallback skills database when AI is not available"""
        return {
            "programming_languages": [
                "Python", "JavaScript", "Java", "C++", "C#", "Ruby", "PHP", "Go", 
                "Rust", "Swift", "Kotlin", "TypeScript", "R"
            ],
            "web_technologies": [
                "React", "Angular", "Vue.js", "Node.js", "Django", "Flask", 
                "Express.js", "Next.js", "HTML", "CSS", "Bootstrap"
            ],
            "databases": [
                "MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite", "Oracle", 
                "DynamoDB", "Elasticsearch"
            ],
            "cloud_platforms": [
                "AWS", "Google Cloud", "Azure", "Docker", "Kubernetes", "Terraform"
            ],
            "data_science": [
                "Machine Learning", "TensorFlow", "PyTorch", "Pandas", "NumPy", 
                "Scikit-learn", "Jupyter"
            ],
            "mobile_development": [
                "React Native", "Flutter", "Swift", "Kotlin", "Android", "iOS"
            ],
            "devops_tools": [
                "Git", "GitHub", "Jenkins", "CI/CD", "Docker", "Kubernetes"
            ],
            "testing": [
                "Jest", "Pytest", "Selenium", "Cypress", "Unit Testing"
            ],
            "design_tools": [
                "Figma", "Adobe XD", "Photoshop", "Sketch"
            ],
            "project_management": [
                "Jira", "Agile", "Scrum", "Kanban", "Trello"
            ],
            "soft_skills": [
                "Leadership", "Communication", "Problem Solving", "Team Work"
            ],
            "certifications": [
                "AWS Certified", "Google Cloud Certified", "PMP", "Scrum Master"
            ]
        }

# Global instance
skills_manager = SkillsManager()

# Convenience functions for backward compatibility
def get_skills_database() -> Dict:
    """Get the complete skills database"""
    return skills_manager.load_or_create_skills_database()

def get_all_skills() -> List[str]:
    """Get flat list of all skills"""
    skills_db = get_skills_database()
    all_skills = []
    for category in skills_db.values():
        all_skills.extend(category)
    return sorted(list(set(all_skills)))

def search_skills(query: str) -> List[str]:
    """Search for skills matching query"""
    all_skills = get_all_skills()
    query_lower = query.lower()
    return [skill for skill in all_skills if query_lower in skill.lower()]

def get_skills_by_category(category: str) -> List[str]:
    """Get skills for specific category"""
    skills_db = get_skills_database()
    return skills_db.get(category, [])

def add_new_skill(skill: str, category: Optional[str] = None) -> bool:
    """Add new skill using AI categorization"""
    return skills_manager.update_skills_with_new_technology(skill, category)

def refresh_skills() -> bool:
    """Refresh skills database with latest technologies"""
    try:
        skills_manager.refresh_skills_database()
        return True
    except Exception:
        return False

def get_trending_skills(category: Optional[str] = None) -> List[str]:
    """Get trending skills using AI"""
    return skills_manager.get_trending_skills(category)