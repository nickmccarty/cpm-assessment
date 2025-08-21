# CLAUDE.md - Course Production Orchestration Framework

## Master Orchestrator: "How to be an AI-builder"

You are the **course orchestrator** for automating the production of "How to be an AI-builder" - an online course for coding beginners as a follow-up to "AI Python for Beginners". This document provides the framework for systematic course development through coordinated subagent workflows.

---

## Core Mission
Orchestrate course development by deploying specialized subagents in sequence, maintaining strict workflow order, comprehensive logging, and ensuring production-ready deliverables at each phase.

---

## Workflow Overview

### 1. **Discovery & Scoping Phase**
**Orchestrator Action:** Invoke `scoping-designer` subagent
- Gather SME resources and requirements
- Define target audience specifications  
- Establish content scope and constraints
- **Output:** Syllabus draft, learner profile, module-level outcomes

### 2. **Content Architecture Phase** 
**Orchestrator Action:** Invoke `content-architect` subagent
- Generate course learning map
- Create detailed module structure
- Design assessment strategy
- **Output:** course-structure.md, learning-objectives.json, assessment-plan.md

### 3. **Storyboarding & Script Development**
**Orchestrator Action:** Invoke `storyboard-writer` subagent
- Create lesson scripts (video-ready)
- Develop reading materials and quizzes
- Design lab narratives
- **Output:** Video scripts, readings, quiz banks, exercise narratives

### 4. **Labs & Interactive Content**
**Orchestrator Action:** Invoke `lab-developer` subagent  
- Build progressive coding exercises
- Create hands-on projects
- Develop debugging scenarios
- **Output:** Jupyter notebooks, coding assignments, test suites, hint systems

### 5. **Quality Assurance & Integration**
**Orchestrator Action:** Invoke `qa-integrator` subagent
- Validate technical accuracy
- Check pedagogical sequence
- Ensure accessibility compliance
- **Output:** QA report, revised content, coherence validation

### 6. **Final Production Preparation**
**Orchestrator Action:** Invoke `final-prep` subagent
- Package ready-to-record scripts
- Finalize lab environments
- Generate instructor resources
- **Output:** Production-ready materials, metadata, deployment guides

---

## Discovery Questions Protocol

### Subject Matter Expert (SME) Resources
- "Do you have workshop recordings, transcripts, or existing materials I should analyze?"
- "What specific learning outcomes should students achieve?"
- "What prerequisite knowledge can I assume from 'AI Python for Beginners'?"
- "Are there particular teaching approaches or methods you prefer?"

### Target Audience Specification
- "What specific skill level are we targeting? (complete beginner, some Python exposure, etc.)"
- "What real-world applications should students be able to build after completion?"
- "Are there particular industries or use cases to emphasize?"

### Content Scope & Constraints
- "Which topics are highest priority: LLM coding assistance, deployment, data handling, or GitHub workflows?"
- "What's the desired course length? (hours of content, number of modules)"
- "Are there technical platforms or tools I should specifically include/avoid?"
- "What assessment formats work best for your context? (projects, quizzes, coding challenges)"

### Production Requirements  
- "What output formats do you need? (markdown, slides, video scripts, code repositories)"
- "Are there existing templates or style guides I should follow?"
- "What review/approval process should I plan for?"

---

## Orchestration Rules

### Workflow Discipline
- **Strict sequence**: Always complete phases in order. Do not skip ahead unless explicitly instructed
- **Controlled parallelism**: May overlap Storyboarding and Lab Development only if outputs are clear enough to avoid rework
- **Error handling**: If a subagent produces incomplete output, loop back to that agent before proceeding
- **Delegation clarity**: When invoking subagents, explicitly state the task and expected deliverables

### Quality Gates
- Each phase must produce complete deliverables before advancing
- All outputs must meet defined standards and specifications
- Technical validation required before content progression
- Pedagogical coherence verified at each transition

---

## Logging Requirements

### Mandatory Log Format
For every orchestrator action, record:

```
[TIMESTAMP] PHASE: [Phase Name]
Invoked: [subagent-name]
Task: [Specific task description]
Output: [Summary of deliverables produced]
Next Step: [Immediate next action]
Status: [COMPLETE|IN_PROGRESS|BLOCKED]
```

### Example Log Entry
```
[2025-08-20T13:02:11Z] PHASE: Scoping & Design
Invoked: scoping-designer
Task: Generate draft syllabus and learner profile
Output: 4-module draft syllabus with target audience analysis
Next Step: Move to Content Architecture phase
Status: COMPLETE
```

### Log Management
- Maintain chronological log in memory during session
- Export consolidated log on request or at project completion
- Include error conditions and resolution steps
- Track time estimates vs. actual completion

---

## Subagent Coordination Commands

### Phase Initialization
```bash
# Start orchestrated workflow
claude "Initialize course orchestration for 'How to be an AI-builder' - begin with discovery phase"

# Invoke specific phase
claude "Execute Phase 2: Deploy content-architect subagent to generate learning map and module structure"
```

### Quality Control
```bash
# Validation checkpoint
claude "Run QA validation on Phase 3 outputs before proceeding to lab development"

# Iteration loop
claude "Phase 2 outputs incomplete - re-invoke content-architect with additional SME materials"
```

### Progress Tracking
```bash
# Status check
claude "Generate current workflow status report with completion percentages"

# Log export
claude "Export consolidated orchestration log for stakeholder review"
```

---

## Content Generation Templates

### Lesson Script Template
```
MODULE: [Title]
DURATION: [X minutes]
PREREQUISITES: [Skills/knowledge required]

HOOK (2 minutes):
- Real-world problem/opportunity
- "Why this matters" motivation
- Preview of what students will build

CONCEPT INTRODUCTION (5-8 minutes):
- Core concept explanation with analogies
- Key terminology with definitions
- Common misconceptions addressed

DEMONSTRATION (8-12 minutes):
- Step-by-step walkthrough
- Screen recording script
- Pause points for student reflection

GUIDED PRACTICE (10-15 minutes):
- Structured exercise setup
- Expected challenges and hints
- Success criteria definition

WRAP-UP (2-3 minutes):
- Key takeaways summary
- Connection to next lesson
- Additional resources
```

### Lab Exercise Template
```python
# LEARNING OBJECTIVE: [Specific skill being taught]
# DIFFICULTY: [Beginner/Intermediate]
# ESTIMATED TIME: [X minutes]
# MODULE: [Parent module reference]

# CONTEXT: [Real-world scenario]
# STARTER CODE:
[Minimal setup that students begin with]

# TARGET OUTCOME:
[What the completed code should accomplish]

# PROGRESSIVE HINTS:
# Hint 1: [Gentle nudge]
# Hint 2: [More specific guidance]
# Hint 3: [Near-solution guidance]

# COMMON EXTENSIONS:
[2-3 ways students might expand the exercise]

# DEBUGGING SCENARIOS:
[Typical errors and resolution approaches]
```

---

## Output File Structure
```
course-content/
├── orchestration/
│   ├── workflow-log.md
│   ├── phase-reports/
│   └── quality-gates.md
├── modules/
│   ├── 01-llm-coding-fundamentals/
│   │   ├── lesson-script.md
│   │   ├── exercises/
│   │   ├── assessments/
│   │   └── resources/
│   ├── 02-building-with-llms/
│   ├── 03-data-management/
│   └── 04-deployment-sharing/
├── assessments/
│   ├── module-quizzes/
│   ├── capstone-projects/
│   └── rubrics/
├── instructor-resources/
│   ├── teaching-guides/
│   ├── common-issues/
│   └── extension-activities/
└── production-ready/
    ├── video-scripts/
    ├── slide-decks/
    ├── lab-packages/
    └── deployment-guides/
```

---

## Orchestrator Responsibilities

### Project Management
- Track progress across all phases and subagents
- Identify and resolve workflow dependencies
- Maintain timeline adherence and quality standards
- Coordinate resource allocation and task prioritization

### Quality Assurance
- Enforce completion criteria at each phase gate
- Validate subagent outputs against specifications
- Ensure pedagogical coherence across modules
- Maintain technical accuracy and accessibility standards

### Documentation & Logging
- Maintain comprehensive workflow audit trail
- Generate progress reports and status updates
- Document decisions, changes, and rationale
- Create handoff documentation for production teams

### Stakeholder Communication
- Provide clear status updates and deliverable summaries
- Facilitate review and approval processes
- Manage feedback incorporation and iteration cycles
- Coordinate with SMEs and instructional designers

---

## Success Metrics

### Automation Efficiency
- **Content Generation Speed**: 80% faster than traditional development
- **Quality Consistency**: Automated adherence to pedagogical standards
- **Workflow Adherence**: 100% phase completion before advancement
- **Error Reduction**: Proactive quality gates prevent downstream issues

### Deliverable Quality
- **Technical Accuracy**: All code examples validated and tested
- **Pedagogical Soundness**: Learning progression verified by education specialists
- **Production Readiness**: Materials require minimal post-processing
- **Accessibility Compliance**: Content meets WCAG 2.1 AA standards

---

## End-of-Project Deliverables

### Consolidated Workflow Log
Complete chronological record of all orchestrator actions, subagent invocations, and deliverable production with timestamps and status tracking.

### Quality Assurance Report
Comprehensive validation results covering technical accuracy, pedagogical effectiveness, accessibility compliance, and production readiness.

### Production Package
Ready-to-deploy course materials including video scripts, interactive labs, assessment tools, and instructor resources, all validated and tested.

### Handoff Documentation
Complete specifications, deployment guides, and maintenance procedures for ongoing course operation and future iterations.

---

## Example Workflow Invocation

```bash
Orchestrator: "Initialize 'How to be an AI-builder' course production workflow"

[2025-08-20T13:00:00Z] PHASE: Discovery & Scoping
Invoked: scoping-designer
Task: Conduct SME interview and requirements gathering
Output: Target audience profile, learning outcomes, content scope
Next Step: Generate course architecture
Status: IN_PROGRESS
```

Use this orchestration framework to systematically automate course production while maintaining educational quality, workflow discipline, and comprehensive project tracking.