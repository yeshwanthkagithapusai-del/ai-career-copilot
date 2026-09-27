---
name: career-copilot-engineering
description: Permanent engineering rules, architecture principles, and guidelines for developing the AI Career Copilot project.
---

# AI CAREER COPILOT - Engineering Rules

## PROJECT VISION
This application is evolving from a collection of independent career tools into an integrated Career Intelligence Platform.

**Core Product Loop:**
ASSESS → DIAGNOSE → LEARN → PRACTICE → IMPROVE → TRACK → RECOMMEND NEXT ACTION

**Long-term Product Promise:**
"From Career Confusion to Career Readiness."

## ARCHITECTURE PRINCIPLES
1. Keep Django as the primary backend.
2. Keep the application as a modular monolith at this stage.
3. Do not introduce microservices unless there is a demonstrated need.
4. Preserve existing working functionality.
5. Prefer incremental migration over large rewrites.
6. Use the Strangler Fig migration pattern where appropriate.
7. Keep business logic out of Django views.
8. Use service layers for complex business operations.
9. Use selectors/query services for complex read operations.
10. Keep AI logic separated from normal business logic.
11. Treat the Skills domain as the future source of truth for user capabilities.
12. Treat SkillEvidence as the connection between user activity and skill proficiency.
13. Keep user data isolated by ownership and permissions.
14. Prefer relational models for important/queryable business data.
15. Use JSONField only where flexible/unstructured data is genuinely appropriate.

## DJANGO RULES
- Follow Django conventions.
- Keep views thin.
- Use models for persistence and basic domain constraints.
- Use services for workflows.
- Use selectors for complex read/query logic.
- Use transactions for multi-step database operations.
- Avoid circular dependencies.
- Avoid duplicated business logic.
- Reuse existing models when appropriate.
- Do not create duplicate models for concepts that already exist.

## DATABASE RULES
- PostgreSQL should be the production database.
- Preserve SQLite compatibility for local development only when practical.
- Add indexes for frequently queried fields.
- Use foreign keys and relationships instead of unnecessary JSON structures.
- Do not destroy existing data during migrations.
- Write reversible migrations whenever practical.
- Never make destructive schema changes without a migration strategy.
- Maintain backward compatibility during staged migrations.

## SKILL DOMAIN RULES
The future Skills domain should provide normalized skills.
- Examples: `Python`, `python`, `Python Programming` should resolve to the same canonical skill.
- Skill evidence may come from: Resume, Assessment, Interview, Roadmap training, Project, Manual user input.
- Do not blindly trust AI-generated skills. Validate and normalize AI output before storing it.

## AI ENGINEERING RULES
- Never expose API keys.
- Never place secrets in source code.
- Never commit `.env`.
- Use environment variables for secrets.
- Use structured AI outputs where possible.
- Validate AI-generated JSON before storing it.
- Handle malformed AI responses.
- Handle provider failures.
- Add timeouts.
- Add retries only where appropriate.
- Prevent uncontrolled AI loops.
- Add rate limiting to expensive AI endpoints.
- Log AI failures safely.
- Do not log API keys or sensitive user content unnecessarily.
- Do not allow user prompts to override system/developer instructions.
- Treat uploaded documents as untrusted input.
- Treat resume/job-description content as untrusted AI input.
- Never allow user-provided content to modify system-level instructions.

## SECURITY RULES
- Every protected resource must verify ownership.
- Prevent IDOR vulnerabilities.
- Validate uploaded files (size, type).
- Protect forms against CSRF.
- Use Django authentication and authorization correctly.
- Do not expose internal errors to users.
- Use secure production settings.
- Never expose secrets.
- Rate-limit expensive endpoints.
- Avoid leaking sensitive user information.

## API RULES
- Use consistent response structures.
- Validate request data.
- Return appropriate HTTP status codes.
- Handle authentication failures correctly.
- Handle authorization failures correctly.
- Avoid exposing internal exceptions.
- Document important APIs.
- Maintain backward compatibility where possible.

## FRONTEND/UI RULES
The UI should be: professional, responsive, accessible, consistent, clean, fast, understandable.
- Use reusable components/templates.
- Every important page should consider: loading state, empty state, error state, success state.
- Do not introduce excessive animations. Respect `prefers-reduced-motion`.
- Do not use fake metrics or fabricated user progress.
- If user data is unavailable, show an appropriate empty/onboarding state.

## CAREER INTELLIGENCE RULES
The application should progressively move toward:
User Profile → Career Goal → Resume → Skills → Skill Evidence → Skill Gaps → Learning Roadmap → Practice → Assessment → Interview → Progress → Next Best Action

**Note:** Do not implement this entire architecture in one change. Build it incrementally.

## TESTING RULES
Every meaningful new feature should include tests.
Test: business logic, permissions, ownership, models, services, API behavior, AI failure cases, invalid input, edge cases.

Before declaring a task complete:
1. Run Django system checks.
2. Run relevant tests.
3. Run the full test suite when practical.
4. Check migrations.
5. Verify affected UI flows.
6. Check browser console errors when UI changes are made.

## GIT/CHANGE MANAGEMENT
- Make small logical changes.
- Do not mix unrelated refactors with feature development.
- Do not delete working functionality without replacement.
- Explain potentially breaking changes.
- Prefer incremental commits.
- Keep migrations reviewable.
- Do not modify unrelated files.

## DEFINITION OF DONE
A feature is not complete merely because the code was written. It is complete only when:
- implementation exists
- existing functionality remains working
- migrations are correct
- tests pass
- security has been considered
- errors are handled
- UI states are handled
- documentation is updated when appropriate
- browser behavior has been verified for UI changes

## IMPORTANT AGENT BEHAVIOR
Before modifying code:
1. Inspect the relevant existing implementation.
2. Understand dependencies.
3. Identify affected models/views/services/templates.
4. Create an implementation plan.
5. Implement the smallest safe change.
6. Run tests.
7. Verify behavior.
8. Report what changed.

Never perform a large rewrite simply because a cleaner architecture is possible.
