# AI Career Copilot - Application Audit

## 1. Existing Features Identified
Based on the codebase analysis, the application contains a robust set of features organized into multiple Django apps:

* **Dashboard**: The main hub showing Career Readiness, Next Best Action, Skill Gaps, and Activity.
* **Resume Analyzer**: Supports PDF/DOCX uploads, extracts text, calculates an ATS score, extracts skills, and records career progress.
* **Assessments (Test Center)**: Allows users to take AI-generated tests to validate skills and records topic performance.
* **Interviews (AI Mock Interview)**: Provides a simulated interview experience and analyzes technical/communication skills.
* **Roadmaps (Course Guidance)**: AI-generated personalized learning paths consisting of phases, tasks, and phase-specific training quizzes.
* **Projects**: Suggests projects based on a user's skill gaps. Completing projects generates skill evidence.
* **Career Progress & Intelligence**: Centralized tracking of skill proficiencies, evidence from multiple sources (resume, tests, manual), and gap analysis against a target career.
* **Chatbot Assistant**: A globally available, context-aware AI assistant integrated into the UI.

## 2. UI Problems & Considerations
* **Z-Index and Layering (Homepage)**: There are known issues where background graphics (like Three.js objects) overlap text elements. Text contrast against certain backgrounds lacks the required WCAG 4.5:1 ratio (specifically some feature descriptions using `#334155`).
* **Inconsistent Component Styling**: While Bootstrap 5 is used throughout, custom CSS (`dashboard.css`, `main.css`, `animations.css`) overrides elements without a cohesive design system, leading to fragmented button sizes and padding across apps (e.g., dashboard cards vs. roadmap quizzes).
* **Mobile Responsiveness**: The sidebar uses an overlay for mobile, but certain complex layouts (like the skill gap charts and chatbot panel) may overflow or clip on smaller screens.
* **Accessibility**: Many interactive elements lack proper `aria-labels` or semantic HTML structures, which can affect screen readers.

## 3. Backend & Architecture Problems
* **Duplicated Data Models (High Priority)**: The application has two separate `Skill` models. One exists in `roadmaps/models.py` and another canonical one in `skills/models.py`. This fragmentation causes disconnected logic when updating user skills.
* **Cross-App Coupling**: Apps are tightly coupled. For instance, `roadmaps` heavily imports from `assessments` (reusing the `Test` model) and `career_intelligence`. `projects` relies directly on `career_intelligence.gap_analysis`.
* **Aggressive 404 Masking**: The main `urls.py` uses a catch-all regex `re_path(r'^.+$', redirect_to_landing)` that redirects all broken URLs to the landing page. This masks true 404 errors, making debugging difficult.
* **Silent Failures**: In multiple places (e.g., `resume_analyzer/views.py` and `projects/services.py`), exceptions during skill evidence generation are caught and logged as warnings, allowing the process to silently fail without the user knowing evidence wasn't recorded.

## 4. Security Concerns
* **Environment-Dependent Security**: Crucial security measures (like `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`) are entirely dependent on environment variables. If missing, they default to insecure values, which is risky if deployed improperly.
* **File Uploads**: The `resume_analyzer` restricts files by size (10MB) and checks magic bytes for PDF/DOCX. While good, there's no virus scanning or deeper sanitization for malicious macro-enabled DOCX files.
* **Default Django Admin**: The default `/admin/` URL is exposed and should ideally be obfuscated or IP-restricted in production.
* *(Note: No API keys or passwords are hardcoded in the repository. They are properly abstracted into environment variables).*

## 5. Features Needing Improvement (Incomplete/Disconnected)
* **Skill Evidence Synchronization**: Generating evidence via the `ResumeIntelligenceService` and `ProjectService` works, but manual skill additions in the `roadmaps` app create weak, untrusted evidence that conflicts with the centralized `career_intelligence` engine.
* **AI Provider Fallback**: While there is a heuristic fallback if OpenAI is unavailable, some fallback responses are static and generic, which severely limits the app's usefulness in offline/error states.
* **Progress Aggregation**: The `CareerProgress` model captures snapshots, but calculating the overarching "Career Readiness" score relies heavily on on-the-fly calculations that could cause performance bottlenecks at scale.

## 6. Suggested Order for Upgrading
1. **Refactor and Unify the DB Models**: Remove the redundant `roadmaps.Skill` model and point all logic to the canonical `skills.Skill` model to prevent data fragmentation.
2. **Fix the URL Router**: Remove the wildcard 404 redirect and implement proper custom `404.html` and `500.html` error templates.
3. **Overhaul the UI/UX System**: Consolidate `dashboard.css`, `main.css`, and inline styles. Establish a clear CSS variable system for typography, colors, and shadows to fix contrast and overlap issues.
4. **Decouple App Dependencies**: Abstract the cross-app imports (like `assessments.Test` in `roadmaps`) by creating dedicated service layers or interfaces.
5. **Enhance Error Handling**: Replace silent `try/except` evidence failures with background task retries (e.g., Celery) or prominent user-facing notifications.
6. **Improve AI Resiliency**: Expand the heuristic fallbacks to provide more dynamic mock data when the AI service times out.
