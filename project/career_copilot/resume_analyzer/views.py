"""
Views for resume analyzer app.
"""
import os
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from .models import Resume
from ai_services.resume_ai import ResumeAIService
from career_progress.models import CareerProgress


ALLOWED_EXTENSIONS = ['.pdf', '.docx']
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@login_required
def resume_analyzer(request):
    """Resume upload and analysis page."""
    resumes = Resume.objects.filter(user=request.user).order_by('-created_at')[:5]
    latest_resume = resumes.first()
    
    return render(request, 'resume/resume_analyzer.html', {
        'resumes': resumes,
        'latest_resume': latest_resume,
    })


@login_required
def upload_resume(request):
    """Handle resume upload and analysis."""
    if request.method != 'POST':
        return redirect('resume_analyzer:resume_analyzer')
    
    resume_file = request.FILES.get('resume_file')
    target_role = request.POST.get('target_role', '').strip()
    job_description = request.POST.get('job_description', '').strip()
    
    if not resume_file:
        messages.error(request, "Please select a resume file to upload.")
        return redirect('resume_analyzer:resume_analyzer')
    
    # Validate file extension
    _, ext = os.path.splitext(resume_file.name)
    ext = ext.lower()
    if ext not in ALLOWED_EXTENSIONS:
        messages.error(request, f"Unsupported file type. Please upload a PDF or DOCX file.")
        return redirect('resume_analyzer:resume_analyzer')
    
    # Validate file content via magic numbers
    header = resume_file.read(4)
    resume_file.seek(0)
    is_pdf = header.startswith(b'%PDF')
    is_docx = header.startswith(b'PK\x03\x04')
    if not (is_pdf or is_docx):
        messages.error(request, "Invalid file content. The file does not appear to be a valid PDF or DOCX.")
        return redirect('resume_analyzer:resume_analyzer')

    # Validate file size
    if resume_file.size > MAX_FILE_SIZE:
        messages.error(request, "File too large. Maximum size is 10MB.")
        return redirect('resume_analyzer:resume_analyzer')
    
    # Check rate limit (e.g. max 5 resumes per day)
    from django.utils import timezone
    from datetime import timedelta
    today = timezone.now() - timedelta(days=1)
    if Resume.objects.filter(user=request.user, created_at__gte=today).count() >= 10:
        messages.error(request, "Daily limit reached. You can only analyze 10 resumes per day.")
        return redirect('resume_analyzer:resume_analyzer')

    try:
        # Save resume
        resume = Resume.objects.create(
            user=request.user,
            resume_file=resume_file,
            target_role=target_role,
            job_description=job_description,
        )
        
        # Extract text
        service = ResumeAIService()
        file_path = resume.resume_file.path if hasattr(resume.resume_file, 'path') else ''
        extracted_text = service.extract_text(file_path, ext)
        resume.extracted_text = extracted_text
        
        if not extracted_text or len(str(extracted_text).strip()) < 50:
            resume.delete()
            messages.error(request, "We couldn't extract text from your resume. Please ensure your file is not a scanned image and try again.")
            return redirect('resume_analyzer:resume_analyzer')
        
        # Get previous ATS score for comparison
        previous_resumes = Resume.objects.filter(user=request.user).exclude(id=resume.id).order_by('-created_at')
        previous_score = previous_resumes.first().ats_score if previous_resumes.exists() else 0
        resume.previous_ats_score = previous_score
        
        # Calculate ATS score (preserves existing scoring)
        analysis = service.calculate_ats_score(extracted_text, job_description, target_role)
        
        if 'error' in analysis:
            resume.delete()
            messages.error(request, analysis['error'])
            return redirect('resume_analyzer:resume_analyzer')
            
        # Add Resume Intelligence 2.0 (Structured extraction and Gap analysis)
        try:
            from resume_analyzer.services import ResumeIntelligenceService
            from careers.models import UserCareerGoal
            from career_intelligence.gap_analysis import calculate_skill_gaps
            
            intel_service = ResumeIntelligenceService()
            structured_data = intel_service.extract_structured_data(extracted_text)
            
            # Fetch goal and gaps for recommendations
            goal = UserCareerGoal.objects.filter(user=request.user).select_related('target_role').first()
            target_role_obj = goal.target_role if goal else None
            gaps_data = None
            if target_role_obj:
                gaps_data = calculate_skill_gaps(request.user, target_role_obj)
            
            recommendations = intel_service.generate_recommendations(analysis, target_role_obj, gaps_data)
            
            analysis['structured_data'] = structured_data
            analysis['intelligence_recommendations'] = recommendations
            analysis['has_target_career'] = bool(target_role_obj)
            
        except Exception as e:
            import logging
            logging.getLogger('resume_analyzer').warning(f"Resume intelligence failed: {e}")
        
        resume.ats_score = analysis['overall_score']
        resume.analysis_data = analysis
        resume.save()
        
        # Record career progress
        CareerProgress.objects.create(
            user=request.user,
            metric_type='ats_score',
            score=analysis['overall_score'],
            previous_score=previous_score,
        )
        
        # Update canonical skills from structured data
        try:
            from career_intelligence.services import SkillEvidenceService
            
            # Collect skills from specific structured data categories (preventing junk generation)
            structured_skills = []
            if 'structured_data' in analysis:
                sd = analysis['structured_data']
                structured_skills.extend(sd.get('programming_languages', []))
                structured_skills.extend(sd.get('frameworks', []))
                structured_skills.extend(sd.get('databases', []))
                structured_skills.extend(sd.get('tools', []))
                structured_skills.extend(sd.get('cloud_technologies', []))
            else:
                # Fallback to old heuristic skills found
                skills_found = analysis.get('skills_found', [])
                for skill_item in skills_found:
                    name = skill_item.get('name') if isinstance(skill_item, dict) else skill_item
                    if name: structured_skills.append(name)
            
            # Remove empty/duplicates while preserving order
            seen = set()
            unique_skills = []
            for s in structured_skills:
                s_strip = s.strip()
                if s_strip and s_strip.lower() not in seen:
                    seen.add(s_strip.lower())
                    unique_skills.append(s_strip)
                    
            for skill_name in unique_skills:
                SkillEvidenceService.record_skill_evidence(
                    user=request.user,
                    skill_name=skill_name,
                    source_type='resume',
                    source_reference=f"resume:{resume.id}",
                    description="Extracted from resume via Resume Intelligence 2.0.",
                    score=50, # Baseline score for resume claim
                    confidence=70
                )
        except Exception as e:
            # Do not block the primary workflow if evidence generation fails
            import logging
            logging.getLogger('resume_analyzer').warning(f"Skill evidence extraction failed: {e}")
        
        messages.success(request, f"Resume analyzed! Your ATS score is {analysis['overall_score']}/100.")
        return redirect('resume_analyzer:ats_report', resume_id=resume.id)
    
    except Exception as e:
        if 'resume' in locals():
            resume.delete()
        messages.error(request, "We couldn't analyze your resume right now. Your file is safe. Please try again.")
        return redirect('resume_analyzer:resume_analyzer')


@login_required
def ats_report(request, resume_id):
    """Display ATS analysis report."""
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    analysis = resume.analysis_data or {}
    
    return render(request, 'resume/ats_report.html', {
        'resume': resume,
        'analysis': analysis,
    })


@login_required
def resume_history(request):
    """Display resume analysis history."""
    resumes = Resume.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'resume/resume_history.html', {'resumes': resumes})
