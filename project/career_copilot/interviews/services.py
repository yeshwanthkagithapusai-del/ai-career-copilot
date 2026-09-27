"""
Services for Interview Intelligence 2.0
"""
from typing import Dict, Any, List, Optional
from ai_services.openai_service import AIService
from careers.models import UserCareerGoal
from career_intelligence.gap_analysis import calculate_skill_gaps

class InterviewIntelligenceService:
    """Service for handling advanced interview intelligence mapping."""
    
    def __init__(self):
        self.ai = AIService()

    def identify_question_skill(self, question: str, target_role: str, user_career_goal=None) -> str:
        """
        Identify the specific primary skill being assessed by the question.
        Uses AI with a strict format requirement to avoid hallucination.
        """
        if not self.ai.is_available:
            return ""

        context_gaps = ""
        if user_career_goal:
            # We can include high-level gap context if needed, but for mapping a question to a skill,
            # we just need to identify what the question is asking.
            pass
            
        prompt = f"""Identify the SINGLE primary technical or professional skill being tested in this interview question.
Target role: {target_role or 'General'}

Question: {question}

Return ONLY a JSON object containing a "skill" key with the name of the skill as a string.
Example: {{"skill": "Python"}}
If the question is purely behavioral or HR-related without a specific skill, return {{"skill": ""}}.
Do NOT invent new complex skills. Use standard canonical names (e.g. 'React', 'SQL', 'System Design', 'Communication').
"""
        messages = [
            {"role": "system", "content": "You are a strict technical skill classifier. Respond with valid JSON only."},
            {"role": "user", "content": prompt}
        ]
        
        result = self.ai.chat_completion_json(messages, temperature=0.0, max_tokens=100)
        if isinstance(result, dict):
            return str(result.get('skill', '')).strip()
        return ""

    def process_interview_evidence(self, user, interview_session, answers_list: list):
        """
        Extract reliable skill signals from interview answers and create canonical SkillEvidence.
        """
        from career_intelligence.services import SkillEvidenceService
        
        # We also want to record evidence for the target role as a holistic domain skill
        # based on the overall technical score, and communication.
        
        if interview_session.technical_score >= 50 and interview_session.target_role:
            try:
                SkillEvidenceService.record_skill_evidence(
                    user=user,
                    skill_name=interview_session.target_role,
                    source_type='interview',
                    source_reference=f"interview:{interview_session.id}_tech",
                    description=f"Holistic technical performance in {interview_session.interview_type} mock interview",
                    score=interview_session.technical_score,
                    confidence=80
                )
            except Exception as e:
                import logging
                logging.getLogger('interviews').warning(f"Failed to record target role tech evidence: {e}")

        if interview_session.communication_score >= 50:
            try:
                SkillEvidenceService.record_skill_evidence(
                    user=user,
                    skill_name="Communication",
                    source_type='interview',
                    source_reference=f"interview:{interview_session.id}_comm",
                    description="Evaluated communication skills across interview session",
                    score=interview_session.communication_score,
                    confidence=80
                )
            except Exception as e:
                import logging
                logging.getLogger('interviews').warning(f"Failed to record communication evidence: {e}")

        # Now, process individual question answers if they mapped to a specific skill
        for ans in answers_list:
            skill = getattr(ans, 'assessed_skill', '')
            if skill and skill.lower() != 'none':
                # Map performance to evidence score
                # If technical score > 0, we can use it.
                # If the score is too low (< 40), we don't award evidence of proficiency.
                # Or we can award evidence with the low score so the system knows they are weak!
                # Actually, weak performance -> weak evidence (score < 50) is good for gaps.
                try:
                    SkillEvidenceService.record_skill_evidence(
                        user=user,
                        skill_name=skill,
                        source_type='interview',
                        source_reference=f"interview_answer:{ans.id}",
                        description=f"Performance on specific interview question.",
                        score=ans.technical_score,
                        confidence=70
                    )
                except Exception as e:
                    import logging
                    logging.getLogger('interviews').warning(f"Failed to record question skill evidence: {e}")

        # Trigger notification
        try:
            from accounts.services import NotificationService
            from django.urls import reverse
            url = reverse('interviews:interview_history')
            NotificationService.notify_milestone(
                user=user,
                event_name="Interview Analyzed",
                detail=f"Your {interview_session.interview_type} interview analysis is complete.",
                action_url=url,
                ref_id=f"interview_completed_{interview_session.id}"
            )
        except Exception as e:
            import logging
            logging.getLogger('interviews').error(f"Failed to generate interview notification: {e}")
                    
    def generate_next_practice_recommendation(self, interview_session, gaps_data: Dict = None) -> str:
        """Generate a deterministic recommendation based on weak points."""
        weak_answers = interview_session.answers.filter(technical_score__lt=70).order_by('technical_score')
        
        if weak_answers.exists():
            weakest = weak_answers.first()
            skill_focus = weakest.assessed_skill if hasattr(weakest, 'assessed_skill') and weakest.assessed_skill else "the concepts discussed in your weakest answers"
            return f"Practice {skill_focus}. Your interview performance indicates this is an improvement area."
            
        if interview_session.communication_score < 70:
            return "Focus on structuring your answers more clearly using the STAR method."
            
        return "Great performance! Continue practicing advanced topics for your target role."
