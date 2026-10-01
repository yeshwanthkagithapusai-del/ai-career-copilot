# Skill Model Unification Plan

## 1. Current Architecture & Problems Identified

Currently, the AI Career Copilot platform contains two distinct `Skill` models, resulting in data fragmentation and disconnected logic:

1. **`roadmaps.models.Skill`** (Legacy)
   * **Purpose**: Maps a specific user to a raw skill string (`skill_name`) along with a `skill_score` and `source`.
   * **Problem**: This model does not normalize skill names (e.g., "python" vs "Python") and forces a direct Many-to-One relationship. It is an isolated model with no Foreign Keys pointing to it from other apps.
   * **Usage**: Used in `roadmaps/views.py` to display user skills and generate roadmaps, and imported into `interviews/views.py` to retrieve a list of user skills.

2. **`skills.models.Skill`** (Canonical)
   * **Purpose**: A global taxonomy of unique, normalized skills (e.g., "Python").
   * **Related Models**: 
     * `SkillAlias`: Maps alternate names to the canonical skill.
     * `SkillEvidence`: Records specific instances where a user demonstrated the skill (e.g., via resume, tests, or manual entry).
     * `UserSkillProficiency`: Calculates a user's overall proficiency based on aggregated `SkillEvidence`.
   * **Problem**: The new `career_intelligence` engine uses this canonical system, but legacy parts of the app (`roadmaps`, `interviews`) are still querying the old `roadmaps.Skill` table.

### Conclusion
**`skills.models.Skill`** (and its related models) must become the single source of truth. The `roadmaps.Skill` model is obsolete and should be deprecated to prevent split brain data storage.

---

## 2. Files Involved

* **Models**:
  * `roadmaps/models.py` (Delete `Skill` class)
  * `skills/models.py` (Retain as canonical)
* **Views**:
  * `roadmaps/views.py` (`course_guidance`, `roadmap_view`, `generate_roadmap`, `skills_view`)
  * `interviews/views.py` (Import `RoadmapSkill` line 50)
  * `dashboard/views.py` (Unused import cleanup)
* **Tests**:
  * `roadmaps/tests.py`
  * `interviews/tests.py`
* **Services**:
  * `career_intelligence/scoring.py` (Used for data migration calculation)

---

## 3. Migration Strategy

To unify the models without losing user data, we must perform a backward-compatible, two-step Django migration:

### Step 1: Data Migration (Python script via `RunPython`)
1. Iterate over all existing records in `roadmaps.models.Skill`.
2. Extract the `skill_name`, `skill_score`, and `source` from the legacy record.
3. Normalize the `skill_name` (lowercase, stripped whitespace).
4. **Get or Create** a canonical `skills.models.Skill` using the normalized name.
5. Create a `SkillEvidence` record for the user linking to the canonical skill, passing the `score` and setting `source_type = 'manual'`.
6. Run `recalculate_user_proficiency(user, skill)` from `career_intelligence.scoring` to update the user's overarching `UserSkillProficiency`.
7. Log the migration of each record for tracking.

### Step 2: Schema Migration
1. After confirming data integrity, execute a schema migration to delete the `roadmaps.Skill` model (dropping the legacy table).

---

## 4. Risks and Recovery Plan

* **Risk 1: Duplicate/Messy Skill Names**
  * *Mitigation*: The data migration will normalize strings. If "Python" and "python" both exist in legacy, they will merge into a single canonical skill, and the user will get two `SkillEvidence` records. The `recalculate_user_proficiency` function automatically handles duplicate evidence by taking the maximum score.
* **Risk 2: Accidental Data Loss**
  * *Mitigation*: The data migration should be written inside a `@transaction.atomic` block. If any error occurs, the database state rolls back automatically.
* **Recovery Strategy**: 
  * Take a full PostgreSQL/SQLite database backup before running migrations.
  * In `RunPython`, define a `reverse_func` that recreates `roadmaps.Skill` records by querying `SkillEvidence` where `source_type='manual'`, ensuring the migration can be safely rolled back using `python manage.py migrate roadmaps <previous_migration_name>`.

---

## 5. Required Code Changes

Once the database migration is complete, update the application logic:

1. **`roadmaps/views.py`**
   * Change: `Skill.objects.filter(user=user)` -> `UserSkillProficiency.objects.filter(user=user).select_related('skill')`.
   * Update template context variables to map `proficiency.skill.name` instead of `legacy_skill.skill_name`.
   * In `skills_view()`, remove the creation of `roadmaps.Skill`. The view already calls `SkillEvidenceService.record_skill_evidence()`, so it is fully compatible once the legacy model creation is deleted.
2. **`interviews/views.py`**
   * Change line 51 from querying `RoadmapSkill` to querying `UserSkillProficiency` to build the list of user skills for the AI context.
3. **`dashboard/views.py`**
   * Remove the unused `Skill` import from `roadmaps.models`.
4. **Templates**
   * Review `roadmap/course_guidance.html`, `roadmap/roadmap.html`, and `roadmap/skills.html` to ensure they handle the `UserSkillProficiency` object structure correctly.

---

## 6. How It Works With Features
By finalizing the unification:
* **Resume Analyzer & Projects**: Already use the `SkillEvidenceService`.
* **Roadmaps & Assessments**: Will now seamlessly share skills with the resume analyzer. A skill added manually in the roadmap will boost career readiness scores, and a skill proven via assessment will automatically satisfy roadmap phase requirements.
* **Career Intelligence**: Everything feeds into `UserSkillProficiency`, allowing the AI chatbot to accurately analyze a user's true skill gaps without checking multiple tables.

---

## 7. Test Plan
1. **Pre-Migration Test**: Write a unit test that creates a legacy `roadmaps.Skill`. Run the data migration and assert that a `UserSkillProficiency` and `SkillEvidence` record is correctly generated.
2. **Rollback Test**: Revert the migration and assert the legacy `roadmaps.Skill` is restored.
3. **Integration Tests**: Run the full test suite (`python manage.py test`) to verify `roadmaps`, `assessments`, and `interviews` modules pass with the updated queries.
4. **Manual UI Test**: Start the development server and manually add a skill in the Roadmap > Skills page. Ensure it appears in the Career Progress analytics graph.

---

## 8. Recommended Implementation Order
1. Create the data migration file (`python manage.py makemigrations --empty roadmaps`) and write the `RunPython` logic.
2. Update the views, tests, and templates to query `UserSkillProficiency`.
3. Delete the `Skill` model from `roadmaps/models.py`.
4. Run `python manage.py makemigrations roadmaps` to create the schema deletion migration.
5. Run tests locally.
6. Commit and deploy.
