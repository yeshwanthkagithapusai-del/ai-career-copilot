# AI Career Copilot - Intelligent Student Career Development Platform

A full-stack AI-powered career development web application built for college students and job seekers.

## Features

- **Resume ATS Analyzer**: Upload PDF/DOCX resumes for instant ATS scoring with AI-powered suggestions
- **AI Mock Interviews**: Dynamic interview question generation with text and voice answers
- **Interview Analyzer**: Detailed performance reports with score breakdowns and AI feedback
- **AI Test Center**: Skill-based assessments with AI-generated questions across 12+ skills
- **Test Analyzer**: Topic-level performance analysis with strong/weak topic identification
- **Course Guidance**: Personalized skill recommendations based on career goals and skill gaps
- **Course Roadmap**: AI-generated learning roadmaps with interactive phase tracking
- **Career Progress Tracking**: Real-time analytics with Chart.js graphs showing actual progress
- **AI Career Assistant**: Floating chatbot providing personalized career guidance
- **Skills Tracking**: Auto-detected skills from resumes and tests, plus manual entry

## Technology Stack

### Frontend
- HTML5, CSS3, JavaScript
- Bootstrap 5
- Three.js (3D educational animations)
- GSAP (premium animations)
- Chart.js (graphs and analytics)
- Font Awesome (icons)
- Django Templates

### Backend
- Python + Django
- Django Authentication
- Django REST Framework

### Database
- Supabase PostgreSQL (production)
- SQLite (local development fallback)

### AI Integration
- Modular AI service architecture
- OpenAI API support (optional)
- Heuristic fallback analysis (works without API key)

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables (copy `.env.example` to `.env`):
```
SECRET_KEY=your-secret-key
DEBUG=True
OPENAI_API_KEY=your-openai-key (optional - heuristic analysis works without it)
```

3. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. Create superuser (for admin access):
```bash
python manage.py createsuperuser
```

5. Run the server:
```bash
python manage.py runserver
```

6. Visit `http://localhost:8000` in your browser.

## Database Configuration

The app uses SQLite by default for local development. To connect to Supabase PostgreSQL:

Option 1 - Using DATABASE_URL:
```
DATABASE_URL=postgresql://user:password@host:port/dbname
```

Option 2 - Using individual credentials:
```
SUPABASE_DB_HOST=your-host
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=your-password
SUPABASE_DB_PORT=5432
```

## AI Features

All AI features work with heuristic analysis by default. To enable OpenAI-powered features:

1. Add your OpenAI API key to `.env`:
```
OPENAI_API_KEY=sk-your-key-here
```

2. The system automatically uses OpenAI when available and falls back to heuristic analysis when not.

## Security

- Django CSRF protection
- Password hashing
- Session management
- Login required decorators on all protected pages
- User ownership validation (users only see their own data)
- File validation for resume uploads
- Environment variable-based secret management
- Row Level Security (RLS) on Supabase tables

## Project Structure

```
career_copilot/
    manage.py
    career_copilot/          # Django project settings
    accounts/                # User authentication and profiles
    dashboard/               # Main dashboard
    resume_analyzer/         # Resume upload and ATS analysis
    interviews/              # AI mock interviews
    assessments/             # AI test center
    roadmaps/                # Course guidance and roadmaps
    career_progress/         # Progress tracking and analytics
    ai_services/             # Modular AI service layer
    templates/               # All HTML templates
    static/                  # CSS, JS, and images
    media/                   # User uploads
```

## Testing

The application has been tested for:
- User registration and login
- All protected page access (redirects when unauthenticated)
- Resume analysis with ATS scoring
- Interview question generation and answer evaluation
- Test question generation and evaluation
- Roadmap generation
- Career progress tracking
- AI chatbot responses
- Empty states when no data is available
- Data isolation between users

## License

Built for educational purposes - suitable for B.Tech projects, internship demonstrations, and hackathons.
