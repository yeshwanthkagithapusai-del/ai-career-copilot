/*
# Create AI Career Copilot Database Schema

1. Overview
This migration creates the complete database schema for the AI Career Copilot platform.
It stores user profiles, resumes, interviews, tests, roadmaps, skills, career progress, and notifications.
All tables are user-scoped with RLS policies ensuring data isolation between users.

2. New Tables
- `user_profiles`: Extended profile information (college, degree, branch, career goal, etc.)
- `resumes`: Uploaded resumes with ATS scores and analysis data
- `interview_sessions`: Mock interview sessions with scores
- `interview_answers`: Individual question-answer pairs in interviews
- `tests`: Assessment sessions with scores and topic performance
- `test_answers`: Individual question answers in tests
- `roadmaps`: Personalized learning roadmaps with progress tracking
- `skills`: User skills with scores and sources
- `career_progress`: Historical performance metrics over time
- `notifications`: User notifications

3. Security
- RLS enabled on all tables
- Owner-scoped CRUD policies (auth.uid() = user_id) on all tables
- Users can only access their own data

4. Important Notes
- All tables use UUID primary keys with gen_random_uuid() defaults
- user_id columns default to auth.uid() for automatic ownership
- Timestamps use timestamptz with now() default
- JSON fields used for flexible analysis data storage
*/

-- User Profiles
CREATE TABLE IF NOT EXISTS user_profiles (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL DEFAULT auth.uid() REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name text DEFAULT '',
    college text DEFAULT '',
    degree text DEFAULT 'btech',
    branch text DEFAULT '',
    academic_year text DEFAULT '1',
    career_goal text DEFAULT '',
    profile_image text,
    bio text DEFAULT '',
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "select_own_profile" ON user_profiles;
CREATE POLICY "select_own_profile" ON user_profiles FOR SELECT
    TO authenticated USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "insert_own_profile" ON user_profiles;
CREATE POLICY "insert_own_profile" ON user_profiles FOR INSERT
    TO authenticated WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "update_own_profile" ON user_profiles;
CREATE POLICY "update_own_profile" ON user_profiles FOR UPDATE
    TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "delete_own_profile" ON user_profiles;
CREATE POLICY "delete_own_profile" ON user_profiles FOR DELETE
    TO authenticated USING (auth.uid() = user_id);

-- Resumes
CREATE TABLE IF NOT EXISTS resumes (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL DEFAULT auth.uid() REFERENCES auth.users(id) ON DELETE CASCADE,
    resume_file text,
    extracted_text text DEFAULT '',
    ats_score integer DEFAULT 0,
    previous_ats_score integer DEFAULT 0,
    target_role text DEFAULT '',
    job_description text DEFAULT '',
    analysis_data jsonb DEFAULT '{}',
    created_at timestamptz DEFAULT now()
);

ALTER TABLE resumes ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "select_own_resumes" ON resumes;
CREATE POLICY "select_own_resumes" ON resumes FOR SELECT
    TO authenticated USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "insert_own_resumes" ON resumes;
CREATE POLICY "insert_own_resumes" ON resumes FOR INSERT
    TO authenticated WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "update_own_resumes" ON resumes;
CREATE POLICY "update_own_resumes" ON resumes FOR UPDATE
    TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "delete_own_resumes" ON resumes;
CREATE POLICY "delete_own_resumes" ON resumes FOR DELETE
    TO authenticated USING (auth.uid() = user_id);

-- Interview Sessions
CREATE TABLE IF NOT EXISTS interview_sessions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL DEFAULT auth.uid() REFERENCES auth.users(id) ON DELETE CASCADE,
    target_role text DEFAULT '',
    interview_type text DEFAULT 'technical',
    difficulty text DEFAULT 'intermediate',
    num_questions integer DEFAULT 5,
    overall_score integer DEFAULT 0,
    technical_score integer DEFAULT 0,
    communication_score integer DEFAULT 0,
    confidence_score integer DEFAULT 0,
    relevance_score integer DEFAULT 0,
    structure_score integer DEFAULT 0,
    clarity_score integer DEFAULT 0,
    strengths jsonb DEFAULT '[]',
    weaknesses jsonb DEFAULT '[]',
    ai_feedback text DEFAULT '',
    completed boolean DEFAULT false,
    created_at timestamptz DEFAULT now()
);

ALTER TABLE interview_sessions ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "select_own_interviews" ON interview_sessions;
CREATE POLICY "select_own_interviews" ON interview_sessions FOR SELECT
    TO authenticated USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "insert_own_interviews" ON interview_sessions;
CREATE POLICY "insert_own_interviews" ON interview_sessions FOR INSERT
    TO authenticated WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "update_own_interviews" ON interview_sessions;
CREATE POLICY "update_own_interviews" ON interview_sessions FOR UPDATE
    TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "delete_own_interviews" ON interview_sessions;
CREATE POLICY "delete_own_interviews" ON interview_sessions FOR DELETE
    TO authenticated USING (auth.uid() = user_id);

-- Interview Answers
CREATE TABLE IF NOT EXISTS interview_answers (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    interview_id uuid NOT NULL REFERENCES interview_sessions(id) ON DELETE CASCADE,
    question text,
    user_answer text DEFAULT '',
    ai_feedback text DEFAULT '',
    score integer DEFAULT 0,
    technical_score integer DEFAULT 0,
    communication_score integer DEFAULT 0,
    confidence_score integer DEFAULT 0,
    strengths jsonb DEFAULT '[]',
    weaknesses jsonb DEFAULT '[]',
    created_at timestamptz DEFAULT now()
);

ALTER TABLE interview_answers ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "select_own_interview_answers" ON interview_answers;
CREATE POLICY "select_own_interview_answers" ON interview_answers FOR SELECT
    TO authenticated USING (
        EXISTS (SELECT 1 FROM interview_sessions WHERE interview_sessions.id = interview_answers.interview_id AND interview_sessions.user_id = auth.uid())
    );

DROP POLICY IF EXISTS "insert_own_interview_answers" ON interview_answers;
CREATE POLICY "insert_own_interview_answers" ON interview_answers FOR INSERT
    TO authenticated WITH CHECK (
        EXISTS (SELECT 1 FROM interview_sessions WHERE interview_sessions.id = interview_answers.interview_id AND interview_sessions.user_id = auth.uid())
    );

DROP POLICY IF EXISTS "update_own_interview_answers" ON interview_answers;
CREATE POLICY "update_own_interview_answers" ON interview_answers FOR UPDATE
    TO authenticated USING (
        EXISTS (SELECT 1 FROM interview_sessions WHERE interview_sessions.id = interview_answers.interview_id AND interview_sessions.user_id = auth.uid())
    );

DROP POLICY IF EXISTS "delete_own_interview_answers" ON interview_answers;
CREATE POLICY "delete_own_interview_answers" ON interview_answers FOR DELETE
    TO authenticated USING (
        EXISTS (SELECT 1 FROM interview_sessions WHERE interview_sessions.id = interview_answers.interview_id AND interview_sessions.user_id = auth.uid())
    );

-- Tests
CREATE TABLE IF NOT EXISTS tests (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL DEFAULT auth.uid() REFERENCES auth.users(id) ON DELETE CASCADE,
    skill text,
    difficulty text DEFAULT 'beginner',
    num_questions integer DEFAULT 10,
    score integer DEFAULT 0,
    accuracy integer DEFAULT 0,
    correct_count integer DEFAULT 0,
    wrong_count integer DEFAULT 0,
    time_taken integer DEFAULT 0,
    topic_performance jsonb DEFAULT '{}',
    strong_topics jsonb DEFAULT '[]',
    weak_topics jsonb DEFAULT '[]',
    suggestions jsonb DEFAULT '[]',
    completed boolean DEFAULT false,
    created_at timestamptz DEFAULT now()
);

ALTER TABLE tests ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "select_own_tests" ON tests;
CREATE POLICY "select_own_tests" ON tests FOR SELECT
    TO authenticated USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "insert_own_tests" ON tests;
CREATE POLICY "insert_own_tests" ON tests FOR INSERT
    TO authenticated WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "update_own_tests" ON tests;
CREATE POLICY "update_own_tests" ON tests FOR UPDATE
    TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "delete_own_tests" ON tests;
CREATE POLICY "delete_own_tests" ON tests FOR DELETE
    TO authenticated USING (auth.uid() = user_id);

-- Test Answers
CREATE TABLE IF NOT EXISTS test_answers (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    test_id uuid NOT NULL REFERENCES tests(id) ON DELETE CASCADE,
    question text,
    options jsonb DEFAULT '[]',
    selected_answer integer DEFAULT -1,
    correct_answer integer DEFAULT 0,
    is_correct boolean DEFAULT false,
    topic text DEFAULT '',
    created_at timestamptz DEFAULT now()
);

ALTER TABLE test_answers ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "select_own_test_answers" ON test_answers;
CREATE POLICY "select_own_test_answers" ON test_answers FOR SELECT
    TO authenticated USING (
        EXISTS (SELECT 1 FROM tests WHERE tests.id = test_answers.test_id AND tests.user_id = auth.uid())
    );

DROP POLICY IF EXISTS "insert_own_test_answers" ON test_answers;
CREATE POLICY "insert_own_test_answers" ON test_answers FOR INSERT
    TO authenticated WITH CHECK (
        EXISTS (SELECT 1 FROM tests WHERE tests.id = test_answers.test_id AND tests.user_id = auth.uid())
    );

DROP POLICY IF EXISTS "update_own_test_answers" ON test_answers;
CREATE POLICY "update_own_test_answers" ON test_answers FOR UPDATE
    TO authenticated USING (
        EXISTS (SELECT 1 FROM tests WHERE tests.id = test_answers.test_id AND tests.user_id = auth.uid())
    );

DROP POLICY IF EXISTS "delete_own_test_answers" ON test_answers;
CREATE POLICY "delete_own_test_answers" ON test_answers FOR DELETE
    TO authenticated USING (
        EXISTS (SELECT 1 FROM tests WHERE tests.id = test_answers.test_id AND tests.user_id = auth.uid())
    );

-- Roadmaps
CREATE TABLE IF NOT EXISTS roadmaps (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL DEFAULT auth.uid() REFERENCES auth.users(id) ON DELETE CASCADE,
    target_career text,
    current_skills jsonb DEFAULT '[]',
    experience_level text DEFAULT 'beginner',
    study_hours_per_week integer DEFAULT 10,
    roadmap_data jsonb DEFAULT '[]',
    progress integer DEFAULT 0,
    completed_phases jsonb DEFAULT '[]',
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

ALTER TABLE roadmaps ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "select_own_roadmaps" ON roadmaps;
CREATE POLICY "select_own_roadmaps" ON roadmaps FOR SELECT
    TO authenticated USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "insert_own_roadmaps" ON roadmaps;
CREATE POLICY "insert_own_roadmaps" ON roadmaps FOR INSERT
    TO authenticated WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "update_own_roadmaps" ON roadmaps;
CREATE POLICY "update_own_roadmaps" ON roadmaps FOR UPDATE
    TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "delete_own_roadmaps" ON roadmaps;
CREATE POLICY "delete_own_roadmaps" ON roadmaps FOR DELETE
    TO authenticated USING (auth.uid() = user_id);

-- Skills
CREATE TABLE IF NOT EXISTS skills (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL DEFAULT auth.uid() REFERENCES auth.users(id) ON DELETE CASCADE,
    skill_name text,
    skill_score integer DEFAULT 0,
    source text DEFAULT 'manual',
    updated_at timestamptz DEFAULT now(),
    created_at timestamptz DEFAULT now(),
    UNIQUE(user_id, skill_name)
);

ALTER TABLE skills ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "select_own_skills" ON skills;
CREATE POLICY "select_own_skills" ON skills FOR SELECT
    TO authenticated USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "insert_own_skills" ON skills;
CREATE POLICY "insert_own_skills" ON skills FOR INSERT
    TO authenticated WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "update_own_skills" ON skills;
CREATE POLICY "update_own_skills" ON skills FOR UPDATE
    TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "delete_own_skills" ON skills;
CREATE POLICY "delete_own_skills" ON skills FOR DELETE
    TO authenticated USING (auth.uid() = user_id);

-- Career Progress
CREATE TABLE IF NOT EXISTS career_progress (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL DEFAULT auth.uid() REFERENCES auth.users(id) ON DELETE CASCADE,
    metric_type text,
    score integer DEFAULT 0,
    previous_score integer DEFAULT 0,
    recorded_at timestamptz DEFAULT now()
);

ALTER TABLE career_progress ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "select_own_progress" ON career_progress;
CREATE POLICY "select_own_progress" ON career_progress FOR SELECT
    TO authenticated USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "insert_own_progress" ON career_progress;
CREATE POLICY "insert_own_progress" ON career_progress FOR INSERT
    TO authenticated WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "update_own_progress" ON career_progress;
CREATE POLICY "update_own_progress" ON career_progress FOR UPDATE
    TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "delete_own_progress" ON career_progress;
CREATE POLICY "delete_own_progress" ON career_progress FOR DELETE
    TO authenticated USING (auth.uid() = user_id);

-- Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL DEFAULT auth.uid() REFERENCES auth.users(id) ON DELETE CASCADE,
    title text,
    message text,
    is_read boolean DEFAULT false,
    created_at timestamptz DEFAULT now()
);

ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "select_own_notifications" ON notifications;
CREATE POLICY "select_own_notifications" ON notifications FOR SELECT
    TO authenticated USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "insert_own_notifications" ON notifications;
CREATE POLICY "insert_own_notifications" ON notifications FOR INSERT
    TO authenticated WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "update_own_notifications" ON notifications;
CREATE POLICY "update_own_notifications" ON notifications FOR UPDATE
    TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "delete_own_notifications" ON notifications;
CREATE POLICY "delete_own_notifications" ON notifications FOR DELETE
    TO authenticated USING (auth.uid() = user_id);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_resumes_user_id ON resumes(user_id);
CREATE INDEX IF NOT EXISTS idx_interview_sessions_user_id ON interview_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_tests_user_id ON tests(user_id);
CREATE INDEX IF NOT EXISTS idx_roadmaps_user_id ON roadmaps(user_id);
CREATE INDEX IF NOT EXISTS idx_skills_user_id ON skills(user_id);
CREATE INDEX IF NOT EXISTS idx_career_progress_user_id ON career_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_career_progress_metric_type ON career_progress(metric_type);
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
