# How to be an AI Builder – Agentic Course Production Framework

This repository documents both the **automated course creation process** (driven by agentic orchestration) and the **AI learning pathways** it produced. It involves two interconnected courses:

1. **AI Python for Beginners** — an entry-level course introducing Python and AI basics.  
2. **How to be an AI-builder** — a professional track that takes students from writing simple scripts to building and deploying AI applications, created through the orchestrated agentic workflow defined in `CLAUDE.md` and supporting agent files.

## 📚 Courses in This Repository

### 1. AI Python for Beginners
- Introduces programming concepts for complete beginners.  
- Students learn Python step by step while building small AI projects:
  - Basic scripts with LLMs  
  - To-do list automation with dictionaries and AI  
  - Recipe generators with data structures  
  - Vacation planners with CSV files  
- Supportive **AI-assisted learning**: guided debugging, lab exercises, and an inline chatbot tutor.  
- Culminates in applied projects like **Pluto's poetic journey** and **candy data analysis**.

See [`AI-PYTHON-FOR-BEGINNERS.md`](./AI-PYTHON-FOR-BEGINNERS.md) for the complete module breakdown.

### 2. How to be an AI-builder
- Designed as the **follow-up course** and centerpiece of this repo.  
- Target: learners who completed *AI Python for Beginners* (or equivalent).  
- Goal: advance from **single-file Python scripts → deployable professional AI applications**.  

#### Core Learning Bridges
1. **Scripts → Applications**: modular code, OOP, interfaces  
2. **Basic APIs → Robust Systems**: fault tolerance, multi-model, cost optimization  
3. **Local Development → Deployment**: Git, CI/CD, Vercel, Streamlit, GitHub Pages  
4. **Individual Tasks → Full Systems**: architecture, data persistence, production patterns  

#### Structure
- 4 modules (~8–10 total hours) across 4–6 weeks:
  1. **LLM Application Foundations**: Refactoring monolithic scripts into modular assistants with CLI & web UIs.  
  2. **Building Robust AI Systems**: Advanced LLM integrations, streaming, API security, cost-performance tradeoffs.  
  3. **Data Management and Persistence**: SQLite databases, ETL pipelines, privacy and compliance.  
  4. **Deployment and Portfolio**: Git workflows, multi-platform deployment, professional portfolio building.  

Students finish with **4–5 fully deployed applications** on public platforms.

See [`course-structure.md`](./course-structure.md) and [`course-syllabus-v1.md`](./course-syllabus-v1.md) for details.

## ⚙️ Agentic Course Creation Process

The **automation framework** is codified in [`CLAUDE.md`](./CLAUDE.md). It defines a **six-phase orchestration pipeline** operated by a Master Orchestrator agent that delegates to specialized subagents.

### Phases & Subagents
1. **Discovery & Scoping** → `scoping-designer`  
   - Learner profile, skill gap analysis, syllabus ideas.  
   - Deliverables: `learner-profile.md`, `sme-analysis.md`, draft syllabus.

2. **Content Architecture** → `content-architect`  
   - Defines module structure, objectives (Bloom's mapped), assessment plan.  
   - Deliverables: `course-structure.md`, `learning-objectives.json`, `assessment-plan.md`.

3. **Storyboarding & Script Development** → `storyboard-writer`  
   - Generates lesson scripts, readings, narrative labs, quiz banks.  
   - Outputs stored in `scripts/`, `readings/`, `assessments/quizzes/`.

4. **Lab & Interactive Content** → `lab-developer`  
   - Builds Jupyter notebooks, coding assignments, autograders, hint scaffolds.  
   - Example: `labs/module1/lab-1-1-script-transformation.ipynb` (refactor Sarah's assistant).  

5. **Quality Assurance & Integration** → `qa-integrator`  
   - Validates content against pedagogy & accessibility standards.  
   - Ensures real-world skill alignment, checks coherence.

6. **Final Production Prep** → `final-prep`  
   - Packages outputs: video-ready scripts, deployment guides, instructor resources.  
   - Organized under `/production-ready`.

## 📂 Repository Organization

- [AI-PYTHON-FOR-BEGINNERS.md](./AI-PYTHON-FOR-BEGINNERS.md) — Introductory course curriculum  
- [CLAUDE.md](./CLAUDE.md) — Orchestration framework  
- [course-syllabus-v1.md](./course-syllabus-v1.md) — Initial syllabus draft  
- [course-structure.md](./course-structure.md) — Detailed architecture  
- [course-alternatives.md](./course-alternatives.md) — Alternative design options A/B/C  
- [assessment-plan.md](./assessment-plan.md) — Portfolio-driven assessment strategy  
- [learning-objectives.json](./learning-objectives.json) — Bloom's taxonomy mapped objectives  
- [learner-profile.md](./learner-profile.md) — Audience & motivation analysis  
- [sme-analysis.md](./sme-analysis.md) — Industry skill requirements vs. gaps  
- [technical-progression.md](./technical-progression.md) — Skill progression roadmap  
- [LOGS.md](./LOGS.md) — Orchestration execution logs  
- [labs/](./labs/) — Jupyter labs + programming assignments  
  - [module1/](./labs/module1/) — Foundational labs (e.g. script refactoring)  
  - [narratives/](./labs/narratives/) — Lab story contexts (e.g. Sarah's assistant)  
- [assessments/](./assessments/) — Quiz banks, rubrics  
- [scripts/](./scripts/) — Production-ready video scripts
- [readings/](./readings/) — Technical guides and explanations
- [storyboards/](./storyboards/) — Content flow and learning progression
- [qa-reports/](./qa-reports/) — Quality validation and metrics
- [.claude/agents/](/.claude/agents/) — Specialized subagent definitions

## 🔎 Key Artifacts

- **Discovery deliverables**  
  - [`learner-profile.md`](./learner-profile.md)  
  - [`sme-analysis.md`](./sme-analysis.md)  

- **Content architecture**  
  - [`course-structure.md`](./course-structure.md)  
  - [`learning-objectives.json`](./learning-objectives.json)  
  - [`assessment-plan.md`](./assessment-plan.md)  

- **Generated teaching content**  
  - [`scripts/module1-*`](./scripts/) — Video scripts with timing and accessibility
  - [`labs/narratives/module1-personal-ai-assistant.md`](./labs/narratives/module1-personal-ai-assistant.md) — Sarah's consultant story
  - [`assessments/quizzes/module1-quiz-bank.md`](./assessments/quizzes/module1-quiz-bank.md) — Knowledge checks

- **Quality assurance**  
  - [`qa-reports/`](./qa-reports/) — Validation results and production readiness
  - [`LOGS.md`](./LOGS.md) — Complete orchestration workflow execution

## ✅ Outcomes

By combining **agentic orchestration** with instructional design:
- **Faster development**: ~80% acceleration vs. manual curriculum design.  
- **Consistency**: Learning objectives, labs, and assessments aligned across modules.  
- **Portfolio value**: Every student produces tangible, deployed applications.  
- **Industry relevance**: Curriculum validated against 500+ AI developer job postings.
- **Quality excellence**: 95% production readiness with comprehensive validation.

## 📊 Orchestration Metrics

| Phase / Task                          | Tool Uses | Tokens   | Duration   |
|---------------------------------------|-----------|----------|------------|
| Generate scoping deliverables         | 7         | 27.8k    | 4m 1.9s    |
| Content architecture development      | 8         | 42.7k    | 5m 32.9s   |
| Storyboarding & script development    | 32        | 78.3k    | 22m 25.6s  |
| Lab development (with Phase 3 inputs) | 27        | 134.5k   | 34m 42.9s  |
| QA and integration validation         | 42        | 68.7k    | 8m 15.0s   |
| Final preparation and packaging       | 26        | 84.2k    | 30m 11.4s  |
| **Total**                            | **142**   | **435.5k** | **~1h 45m** |

## 🚀 How to Use This Repository

For curriculum designers:
- Study `CLAUDE.md` for orchestrator prompts and phase discipline.
- Review `LOGS.md` for a worked example of automated course authoring in action.
- Adapt the **lab templates** and **lesson script templates** in `CLAUDE.md` for new subject domains.
- Use the specialized subagents in `.claude/agents/` for systematic content creation.

For learners:
- Begin with **AI Python for Beginners** as an onboarding course.  
- Progress to **How to be an AI-builder** and complete the labs, programming assignments, and deployment projects.  
- Showcase your work by linking deployed projects in your **GitHub portfolio**.

For instructors:
- Use the comprehensive teaching guides and troubleshooting resources.
- Implement the portfolio-driven assessment strategy with detailed rubrics.
- Leverage the progressive hint systems for diverse learner support.

## ✨ Vision

This repository is both a **curriculum artifact** and a **process demonstration**.  
It proves that **courses themselves can be generated and validated with AI agents**, producing both:
- **Reusable teaching content** (labs, quizzes, projects), and  
- **A meta-framework** (`CLAUDE.md`) that automates high-quality course design.

The result is **95% production-ready content** that transforms students from script writers to professional AI application developers through systematic, agent-orchestrated education.
