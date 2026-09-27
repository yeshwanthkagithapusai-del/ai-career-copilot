"""
Career AI service - analyzes career progress and powers the AI assistant chatbot.
"""
import json
from .openai_service import AIService


class CareerAIService:
    """Service for career progress analysis and AI assistant."""
    
    def __init__(self):
        self.ai = AIService()
    
    def generate_progress_summary(self, user_data):
        """
        Generate an AI-powered career progress summary.
        user_data: dict with progress metrics, scores, trends
        """
        if self.ai.is_available:
            ai_summary = self._generate_ai_summary(user_data)
            if ai_summary:
                return ai_summary
        
        return self._heuristic_summary(user_data)
    
    def _generate_ai_summary(self, user_data):
        """Generate progress summary using OpenAI."""
        prompt = f"""As a career coach, analyze this student's progress data and provide a personalized summary.

User data:
{json.dumps(user_data, indent=2, default=str)}

Provide:
1. A 2-3 sentence summary of their overall progress
2. Key achievements
3. Areas needing improvement
4. Specific actionable recommendations

Respond as JSON:
{{
  "summary": "Overall summary text",
  "achievements": ["achievement1", "achievement2"],
  "improvements": ["area1", "area2"],
  "recommendations": ["rec1", "rec2"]
}}"""

        messages = [
            {"role": "system", "content": "You are an expert career coach. Respond with valid JSON only."},
            {"role": "user", "content": prompt}
        ]
        
        result = self.ai.chat_completion_json(messages, temperature=0.5, max_tokens=1000)
        if result and 'summary' in result:
            return result
        return None
    
    def _heuristic_summary(self, user_data):
        """Generate progress summary using heuristics."""
        summary_parts = []
        achievements = []
        improvements = []
        recommendations = []
        
        # ATS progress
        ats_scores = user_data.get('ats_scores', [])
        if len(ats_scores) >= 2:
            latest = ats_scores[-1]
            previous = ats_scores[-2]
            diff = latest - previous
            if diff > 0:
                summary_parts.append(f"Your resume ATS score improved by {diff} points (from {previous} to {latest}).")
                achievements.append(f"ATS score increased by {diff} points")
            elif diff < 0:
                summary_parts.append(f"Your resume ATS score decreased by {abs(diff)} points (from {previous} to {latest}).")
                improvements.append("Resume ATS score needs attention")
                recommendations.append("Review your latest resume analysis suggestions and upload an improved version.")
            else:
                summary_parts.append(f"Your resume ATS score remained stable at {latest}.")
        elif len(ats_scores) == 1:
            summary_parts.append(f"You've completed your first resume analysis with an ATS score of {ats_scores[0]}.")
            achievements.append("Completed first resume analysis")
        
        # Interview progress
        interview_scores = user_data.get('interview_scores', [])
        if len(interview_scores) >= 2:
            latest = interview_scores[-1]
            previous = interview_scores[-2]
            tech_diff = latest.get('technical', 0) - previous.get('technical', 0)
            comm_diff = latest.get('communication', 0) - previous.get('communication', 0)
            
            if tech_diff > 0:
                summary_parts.append(f"Your technical interview performance improved by {tech_diff} points.")
                achievements.append(f"Technical interview score up by {tech_diff} points")
            elif tech_diff < 0:
                summary_parts.append(f"Your technical interview performance decreased by {abs(tech_diff)} points.")
                improvements.append("Technical interview performance declined")
                recommendations.append("Practice more technical interview questions and review fundamental concepts.")
            
            if comm_diff > 0:
                summary_parts.append(f"Your communication score improved by {comm_diff} points.")
                achievements.append(f"Communication score up by {comm_diff} points")
            elif comm_diff < 0:
                summary_parts.append(f"Your communication score decreased by {abs(comm_diff)} points.")
                improvements.append("Communication score declined")
                recommendations.append("Practice structured answer techniques like the STAR method to improve communication.")
        elif len(interview_scores) == 1:
            summary_parts.append(f"You've completed your first mock interview with a score of {interview_scores[0].get('overall', 0)}.")
            achievements.append("Completed first mock interview")
        
        # Test progress
        test_scores = user_data.get('test_scores', [])
        if len(test_scores) >= 2:
            latest = test_scores[-1]
            previous = test_scores[-2]
            diff = latest - previous
            if diff > 0:
                summary_parts.append(f"Your latest test score improved by {diff} points.")
                achievements.append(f"Test score increased by {diff} points")
            elif diff < 0:
                summary_parts.append(f"Your latest test score decreased by {abs(diff)} points.")
                improvements.append("Test performance declined")
                recommendations.append(f"Review the topics from your latest assessment and practice weak areas.")
        elif len(test_scores) == 1:
            summary_parts.append(f"You've completed your first assessment with a score of {test_scores[0]}.")
            achievements.append("Completed first assessment")
        
        # Roadmap progress
        roadmap_progress = user_data.get('roadmap_progress', 0)
        if roadmap_progress > 0:
            summary_parts.append(f"Your roadmap completion is at {roadmap_progress}%.")
            if roadmap_progress >= 50:
                achievements.append(f"Roadmap {roadmap_progress}% complete")
        
        # Overall
        if not summary_parts:
            summary_parts.append("Welcome to your career journey! Start by uploading your resume or taking an assessment to track your progress.")
        
        if not achievements:
            achievements.append("Started your career development journey")
        
        if not improvements:
            improvements.append("Complete more activities to identify areas for improvement")
        
        if not recommendations:
            recommendations.append("Upload your resume for ATS analysis to get started.")
            recommendations.append("Take a practice test to assess your current skills.")
            recommendations.append("Generate a personalized roadmap for your career goal.")
        
        return {
            'summary': ' '.join(summary_parts),
            'achievements': achievements[:5],
            'improvements': improvements[:5],
            'recommendations': recommendations[:5],
        }
    
    def generate_suggestions(self, user_data):
        """
        Generate personalized AI suggestions based on user activity.
        """
        suggestions = []
        
        # Resume suggestions
        ats_scores = user_data.get('ats_scores', [])
        if len(ats_scores) >= 2:
            latest = ats_scores[-1]
            previous = ats_scores[-2]
            if latest < previous:
                suggestions.append(f"Your ATS score decreased from {previous} to {latest}. Review the suggestions from your latest analysis and upload an improved resume.")
        
        # Test suggestions
        test_data = user_data.get('latest_test', {})
        if test_data:
            weak_topics = test_data.get('weak_topics', [])
            if weak_topics:
                top_weak = weak_topics[0]
                suggestions.append(f"Your performance in {top_weak[0]} was {top_weak[1]}%. Focus on reviewing the core concepts and practicing more problems.")
        
        # Interview suggestions
        interview_data = user_data.get('latest_interview', {})
        if interview_data:
            tech_score = interview_data.get('technical_score', 0)
            comm_score = interview_data.get('communication_score', 0)
            if tech_score < 70:
                suggestions.append(f"Your technical interview score is {tech_score}. Practice more technical questions related to your target role.")
            if comm_score < 70:
                suggestions.append(f"Your communication score is {comm_score}. Practice the STAR method for structured answers.")
        
        # Skill gap suggestions
        missing_skills = user_data.get('missing_skills', [])
        if missing_skills:
            suggestions.append(f"Focus on learning {missing_skills[0]} — it's a key skill for your career goal that you haven't acquired yet.")
        
        # Roadmap suggestions
        roadmap_progress = user_data.get('roadmap_progress', 0)
        if roadmap_progress == 0 and user_data.get('has_roadmap', False):
            suggestions.append("Start your roadmap from Phase 1 to build a strong foundation.")
        
        if not suggestions:
            suggestions.append("Upload your resume to get a personalized ATS score and improvement suggestions.")
            suggestions.append("Take a practice test to identify your strong and weak areas.")
            suggestions.append("Generate a personalized roadmap to guide your learning journey.")
        
        return suggestions[:5]
    
    def chat(self, message, user_context=None):
        """
        AI Career Assistant chatbot.
        Provides personalized responses based on user context.
        """
        context_str = ''
        if user_context:
            context_str = f"\n\nUser context (use this to personalize your response):\n{json.dumps(user_context, indent=2, default=str)}"
        
        if self.ai.is_available:
            ai_response = self._chat_with_ai(message, context_str)
            if ai_response:
                return ai_response
        
        return self._heuristic_chat(message, user_context)
    
    def _chat_with_ai(self, message, context_str):
        """Chat using OpenAI."""
        messages = [
            {"role": "system", "content": f"You are AI Career Copilot, a friendly and knowledgeable career advisor for college students. Provide helpful, specific, and actionable advice. Keep responses concise (3-5 sentences).{context_str}"},
            {"role": "user", "content": message}
        ]
        
        response = self.ai.chat_completion(messages, temperature=0.7, max_tokens=500)
        return response
    
    def _heuristic_chat(self, message, user_context=None):
        """Provide a helpful response using heuristics."""
        message_lower = message.lower()
        
        # Resume-related
        if any(word in message_lower for word in ['resume', 'ats', 'cv']):
            return "Your resume is your first impression on recruiters. Make sure to: 1) Use a clean format with clear sections, 2) Include relevant keywords from the job description, 3) Use action verbs like 'developed', 'led', 'optimized', 4) Quantify your achievements with numbers. Upload your resume on the Resume ATS page to get a detailed score and personalized suggestions."
        
        # Interview-related
        if any(word in message_lower for word in ['interview', 'mock', 'hr', 'technical interview']):
            return "Interviews can be nerve-wracking but practice makes perfect! Try our AI Mock Interview feature to practice with dynamically generated questions. For technical interviews, focus on data structures and problem-solving. For HR interviews, use the STAR method (Situation, Task, Action, Result) to structure your answers."
        
        # Test/assessment-related
        if any(word in message_lower for word in ['test', 'assessment', 'exam', 'quiz']):
            return "Regular assessments help track your learning progress. Visit our Test Center to take skill-based assessments in Python, SQL, Java, and more. After each test, you'll get a detailed analysis of your strong and weak topics to guide your study plan."
        
        # Roadmap-related
        if any(word in message_lower for word in ['roadmap', 'plan', 'path', 'journey']):
            return "A personalized roadmap can guide your career journey step by step. Visit the Course Roadmap page to generate one based on your career goal, current skills, and available study time. Each phase includes skills to learn, topics to cover, and a suggested project."
        
        # Skill-related
        if any(word in message_lower for word in ['skill', 'learn', 'study', 'course']):
            return "Building skills systematically is key to career success. Check out the Course Guidance page for personalized recommendations based on your career goal and current skill gaps. Focus on one skill at a time and build projects to practice what you learn."
        
        # Career-related
        if any(word in message_lower for word in ['career', 'job', 'goal', 'future']):
            goal = user_context.get('career_goal', 'your career goal') if user_context else 'your career goal'
            return f"Your journey toward {goal} starts with understanding what skills you need. I recommend: 1) Upload your resume for an ATS analysis, 2) Take a few skill assessments to identify gaps, 3) Generate a personalized roadmap, 4) Practice with mock interviews. Use the dashboard to track your progress over time!"
        
        # General
        return "I'm your AI Career Copilot! I can help you with resume analysis, interview preparation, skill assessments, career roadmaps, and study guidance. Try asking about any of these topics, or visit the specific pages from the sidebar to get started."
