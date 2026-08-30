# AI Interviewer — Vibe Coding Build Specification

## 0. Project Objective

Build an AI-powered interview preparation platform that gives candidates a **real-world interview experience** in both modes:

1. **Focused Practice Mode**
2. **Real Interview Simulation Mode**

The core product principle is:

> Regardless of mode, every interview must feel like a realistic, adaptive interview. Questions must be evidence-driven and personalized using the candidate's target role, organization, job description, resume, core concepts, historically reported interview patterns, frequency, importance, trends, and previous candidate performance.

This is NOT a static question bank and NOT a generic chatbot.

---

# 1. Product Modes

## 1.1 Focused Practice Mode

The candidate chooses one or more question categories to practice.

Examples:

- Technical
- Behavioral / STAR
- Analytical / Problem Solving
- Case Study
- Situational / Hypothetical
- Personal / Motivational
- HR / Culture Fit
- Communication / Clarity
- Curveball / Stress
- Salary / Logistics
- Leadership / Teamwork
- Ethical / Integrity
- Reflective / Self-Growth
- Rapid-fire / Icebreaker

The candidate then experiences a **real interview**, not a quiz.

Example:

```text
Candidate selects:
Technical Practice

Role:
Senior Backend Engineer

Company:
Example Company

        ↓

AI Interviewer:
"Let's start with a system-design problem.
How would you design a rate limiter for a
high-traffic API?"

        ↓

Candidate answers

        ↓

AI evaluates answer

        ↓

AI asks a relevant follow-up

        ↓

Candidate answers

        ↓

AI continues probing or moves to another
technical competency
```

The only constraint is that questions remain within the selected category/categories.

---

## 1.2 Real Interview Simulation Mode

The candidate does NOT select individual question categories.

The candidate provides:

- Target company
- Target role
- Job description
- Resume
- Experience level
- Interview duration

The system researches the role/company and builds an adaptive interview plan.

Example:

```text
Introduction
    ↓
Technical
    ↓
Problem Solving
    ↓
System Design
    ↓
Behavioral / STAR
    ↓
Leadership
    ↓
Situational
    ↓
Closing
```

The sequence is not rigid.

The Interview Engine adapts based on candidate answers.

---

# 2. Core Product Principle

The system must NOT simply ask:

```text
"Generate a technical question."
```

Instead, the question-generation system should consider:

```text
Candidate
    +
Resume
    +
Role
    +
Job Description
    +
Organization
    +
Organization research
    +
Core role concepts
    +
Historically reported questions
    +
Question frequency
    +
Question importance
    +
Recent trends
    +
Experience level
    +
Previous interview performance
    +
Current interview state
```

Then generate or select the most appropriate next question.

---

# 3. High-Level Architecture

```text
                              CANDIDATE
                                  |
                                  v
                         Next.js / React
                                  |
                         HTTPS / WebSocket
                                  |
                                  v
                         FastAPI Backend
                                  |
             +--------------------+--------------------+
             |                    |                    |
             v                    v                    v
      Practice Planner    Simulation Planner    User/Profile APIs
             |                    |
             +----------+---------+
                        |
                        v
                 INTERVIEW ENGINE
                        |
                        v
              QUESTION INTELLIGENCE
                        |
        +---------------+----------------+
        |               |                |
        v               v                v
      Role          Organization      Candidate
    Knowledge         Research         Context
        |               |                |
        +---------------+----------------+
                        |
                        v
                 Question Generator
                        |
                        v
                 Voice / Text Layer
                        |
                        v
                    Candidate
                        |
                        v
                      Answer
                        |
                        v
              Type-Specific Evaluator
                        |
                        v
               Adaptive Decision Engine
                        |
              +---------+---------+
              |                   |
              v                   v
          Follow-up          Next competency
              |                   |
              +---------+---------+
                        |
                        v
                 Final Evaluation
                        |
                        v
                  Candidate Report
```

---

# 4. Technology Stack

## Frontend

Use:

- Next.js
- React
- TypeScript
- Tailwind CSS

## Backend

Use:

- Python
- FastAPI
- Pydantic
- SQLAlchemy 2.x
- Alembic

## Database

Use:

- PostgreSQL
- pgvector

## Authentication

Use:

- Firebase Authentication

Do NOT use Firestore as the primary application database.

## Local Infrastructure

Use:

- Docker
- Docker Compose
- PostgreSQL + pgvector container

## Voice

For initial MVP:

- Pipecat

Keep Pipecat isolated behind a voice service interface.

Future alternatives:

- LiveKit Agents
- Vapi (managed, if budget allows and self-hosting becomes a bottleneck)

Do not build custom realtime WebRTC infrastructure initially — Pipecat already handles the realtime audio pipeline plumbing.

## Storage

Use S3-compatible object storage for:

- resumes only

Do NOT store audio or video recordings. Audio is streamed through the voice layer (Pipecat, wrapping STT/TTS), transcribed in real time, and discarded — only the resulting text transcript is persisted in PostgreSQL. This keeps storage cost near-zero and avoids consent/compliance overhead for storing biometric-adjacent voice data.

## Monitoring

Use:

- Sentry
- structured logging

---

# 5. Repository Structure

Use a monorepo initially.

Suggested structure:

```text
ai-interviewer/
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── hooks/
│   ├── types/
│   └── ...
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── repositories/
│   │   ├── services/
│   │   ├── interview/
│   │   ├── ai/
│   │   ├── rag/
│   │   ├── research/
│   │   ├── voice/
│   │   └── infrastructure/
│   │
│   ├── migrations/
│   └── tests/
│
├── docker/
├── docs/
├── .env.example
├── docker-compose.yml
├── README.md
└── .gitignore
```

The exact structure can be adjusted if a cleaner implementation is appropriate.

---

# 6. Backend Architecture

Use a **modular monolith**.

Do NOT create microservices.

Recommended modules:

```text
backend/app/

api/
    auth/
    candidates/
    resumes/
    jobs/
    interviews/
    reports/

interview/
    engine/
    planner/
    state/
    strategies/

ai/
    candidate_analyzer/
    question_generator/
    answer_evaluator/
    followup_generator/
    report_generator/

research/
    organization/
    role/
    sources/

rag/
    ingestion/
    chunking/
    embeddings/
    retrieval/

voice/
    pipecat/
    interfaces/

models/
repositories/
services/
infrastructure/
```

Business logic must not be placed directly inside API routes.

---

# 7. Database Design

Core tables:

```text
users
candidate_profiles

resumes

job_descriptions
job_requirements

roles
competencies
question_types

interviews
interview_plans
interview_plan_items

interview_questions
answers
evaluations

evaluation_rubrics
rubric_criteria

documents
document_chunks

organizations
organization_profiles
organization_sources

question_intelligence
question_observations

candidate_skill_profiles
candidate_performance
```

---

# 8. User and Authentication Model

Firebase handles authentication.

PostgreSQL stores application data.

Conceptually:

```text
Firebase Auth
     |
     | firebase_uid
     v
PostgreSQL users
     |
     v
candidate_profiles
```

Never store plaintext passwords.

Every API request requiring authentication must verify the Firebase ID token.

Every user-owned resource must also be checked for ownership.

---

# 9. Question Taxonomy

Support these question types:

```text
TECHNICAL
BEHAVIORAL
ANALYTICAL
CASE_STUDY
SITUATIONAL
PERSONAL_MOTIVATIONAL
HR_CULTURE
COMMUNICATION
CURVEBALL_STRESS
SALARY_LOGISTICS
LEADERSHIP_TEAMWORK
ETHICAL_INTEGRITY
REFLECTIVE_SELF_GROWTH
RAPID_FIRE_ICEBREAKER
FOLLOW_UP_PROBING
```

`FOLLOW_UP_PROBING` should also be represented as a relationship/strategy rather than only a normal category.

---

# 10. Question Type vs Competency

Do not treat these as the same thing.

Example:

```text
Question:
"Tell me about a time you disagreed with a teammate."

Question Type:
BEHAVIORAL

Competencies:
- Conflict Resolution
- Communication
- Teamwork
```

Another:

```text
Question:
"Design a scalable notification service."

Question Type:
TECHNICAL

Competencies:
- System Design
- Scalability
- Distributed Systems
- Tradeoff Analysis
```

Question metadata should include:

```text
question_type
competencies
role
company
difficulty
interview_stage
rubric
source
confidence
embedding
```

---

# 11. Question Intelligence System

This is one of the core differentiators.

The platform must maintain a Question Intelligence layer.

It should store information such as:

```text
question
role
company
experience_level
question_type
competencies
difficulty

frequency
importance
role_relevance
company_relevance
core_concept_relevance
trend_relevance

source_type
source_url
source_date
confidence

embedding
```

The goal is to answer:

> "What are the most relevant questions/concepts to ask this candidate for this role and organization right now?"

---

# 12. Evidence Hierarchy

The question engine should prefer evidence in this approximate order:

## Level 1 — Official information

- Official job description
- Official career pages
- Official interview process information
- Company principles/values
- Official role requirements

## Level 2 — Platform's own interview data

As the platform grows:

- Candidate interview reports
- Questions encountered
- Candidate performance
- Question outcomes

## Level 3 — Publicly reported interview experiences

Use publicly available sources and store:

- source
- date
- role
- company
- reported question
- confidence

## Level 4 — General role knowledge

Core concepts expected for the role.

## Level 5 — AI-generated questions

Used to fill gaps and create realistic variations.

Do NOT allow the LLM to invent unsupported claims about company interview practices.

---

# 13. Organization Research

When a candidate selects a company, the system should eventually build an Organization Interview Profile.

Input:

```text
Organization
Role
Job Description
```

Research sources may include:

```text
Official company career pages
Official job descriptions
Official interview process documentation
Public interview experiences
Publicly reported question patterns
Company values/principles
Role-specific requirements
```

Output:

```text
Organization Interview Profile
```

Example:

```text
company
role
experience_level

common_question_types
important_competencies
interview_stages

technical_weight
behavioral_weight
case_study_weight
leadership_weight
communication_weight

common_topics
reported_question_patterns

research_confidence
last_researched_at
```

Do not state that an organization "always asks" a question unless there is strong evidence.

Use language such as:

> "Frequently reported in publicly available interview experiences."

or:

> "Relevant based on the organization's published role requirements."

---

# 14. Research Source Tracking

Every research item should preserve provenance.

Suggested fields:

```text
source_type
source_url
source_title
source_date
retrieved_at
company
role
claim
confidence
```

Distinguish:

```text
OFFICIAL
PUBLICLY_REPORTED
PLATFORM_DATA
GENERAL_ROLE_KNOWLEDGE
AI_GENERATED
```

This is important for trust and debugging.

---

# 15. Question Ranking

Question selection should consider multiple dimensions.

Conceptually:

```text
Question Relevance
=
Role relevance
+ Company relevance
+ Job description relevance
+ Core concept importance
+ Historical frequency
+ Recent trend relevance
+ Difficulty fit
+ Candidate weakness
+ Interview coverage
```

Do not blindly select the most frequently asked question.

A question may be important even if it is not frequently reported.

---

# 16. Past Question Analysis

Do not simply copy old questions.

Instead:

```text
Historical question
       |
       v
Extract underlying concept
       |
       v
Identify competency
       |
       v
Identify difficulty
       |
       v
Generate realistic variation
```

Example:

Historical pattern:

```text
"Design a URL shortener."
```

Generated realistic variation:

```text
"Design a URL-shortening service capable of
handling 100 million redirects per day."
```

The candidate practices the underlying concept rather than memorizing exact wording.

---

# 17. Practice Mode Architecture

Practice mode must be a realistic adaptive interview.

Flow:

```text
Candidate
   |
   v
Select Practice
   |
   v
Select Company
   |
   v
Select Role
   |
   v
Select Resume
   |
   v
Select Question Type(s)
   |
   v
Research + Question Intelligence
   |
   v
Practice Interview Plan
   |
   v
AI Interviewer
   |
   v
Candidate Answer
   |
   v
Evaluation
   |
   v
Follow-up or next question
   |
   v
Continue interview
   |
   v
Final practice report
```

Practice mode only constrains the question categories.

The interview remains adaptive.

---

# 18. Practice Mode Example

Candidate chooses:

```text
Technical
Role: Backend Engineer
Company: Example Company
```

AI:

> "How would you design a rate limiter for a high-traffic API?"

Candidate answers.

AI evaluates.

AI:

> "You mentioned Redis for maintaining counters. How would your design behave if Redis became temporarily unavailable?"

Candidate answers.

AI evaluates.

AI:

> "Now let's discuss the consistency tradeoffs in your design."

This is one continuous technical interview.

Do NOT make it a list of unrelated questions.

---

# 19. Behavioral Practice

Use a STAR-aware evaluator.

Evaluate:

```text
Situation
Task
Action
Result
```

Also evaluate:

```text
Ownership
Specificity
Impact
Reflection
Communication
```

If an answer is incomplete, generate a natural follow-up.

Example:

```text
Situation ✓
Task ✓
Action ?
Result ?

        ↓

Follow-up:
"What specifically did you do to resolve the problem?"
```

---

# 20. Technical Practice

Evaluate:

```text
Correctness
Depth
Reasoning
Tradeoffs
Problem solving
Communication
```

Adaptive behavior:

```text
Strong answer
    ↓
Increase difficulty / depth

Weak answer
    ↓
Probe fundamentals

Missing concept
    ↓
Targeted follow-up
```

---

# 21. Case Study Practice

Keep the session around a coherent case.

Example:

```text
Case:
Food delivery expansion into tier-2 cities
```

Then progressively probe:

```text
Problem framing
      ↓
Assumptions
      ↓
Prioritization
      ↓
Analysis
      ↓
Solution
      ↓
Metrics
      ↓
Tradeoffs
```

Do not ask unrelated case questions.

---

# 22. Communication Practice

Evaluate:

```text
Clarity
Structure
Conciseness
Audience adaptation
Technical accuracy
```

Example:

> "Explain database indexing to a non-technical manager."

Follow-up:

> "Now explain it to a backend engineer."

---

# 23. Real Interview Simulation

Simulation mode should allow the AI to select question types.

Inputs:

```text
Candidate
Resume
Company
Role
Job Description
Experience level
Duration
```

The system generates an initial interview blueprint.

Example:

```text
Introduction
   ↓
Technical
   ↓
Problem Solving
   ↓
System Design
   ↓
Behavioral
   ↓
Leadership
   ↓
Situational
   ↓
Closing
```

The plan is adaptive.

If the candidate performs poorly in a competency:

```text
Weak competency
      ↓
Additional probing
      ↓
Re-evaluation
      ↓
Continue
```

If the candidate demonstrates strong mastery:

```text
Strong competency
      ↓
Increase difficulty
or
Move to next competency
```

---

# 24. Adaptive Interview Engine

The engine should NOT use a rigid sequence.

Use:

```text
Interview State
      |
      v
Evaluate latest answer
      |
      +---- Strong ------> Increase difficulty / next competency
      |
      +---- Weak --------> Probe fundamentals
      |
      +---- Incomplete --> Follow-up
      |
      +---- Interesting -> Deeper probe
      |
      +---- Competency complete -> Next competency
```

Maintain state such as:

```text
current_question
current_competency
current_question_type
difficulty
questions_asked
topics_covered
topics_remaining
candidate_strengths
candidate_weaknesses
followup_depth
time_remaining
interview_status
```

---

# 25. Follow-up Questions

Follow-ups should be generated based on the answer.

Reasons include:

```text
Incomplete STAR
Weak technical depth
Incorrect concept
Unclear reasoning
Missing tradeoff
Contradiction
Interesting claim
Need for evidence
Need for clarification
```

Database should support:

```text
parent_question_id
```

This allows question trees:

```text
Q1
 |
 +-- Q2 follow-up
      |
      +-- Q3 deeper follow-up
```

---

# 26. Evaluation Rubrics

Do not use one universal rubric.

## Technical

```text
Correctness
Depth
Reasoning
Tradeoffs
Communication
```

## Behavioral

```text
STAR completeness
Ownership
Specificity
Impact
Reflection
Communication
```

## Case Study

```text
Problem framing
Assumptions
Structure
Analysis
Tradeoffs
Recommendation
```

## Communication

```text
Clarity
Structure
Conciseness
Audience adaptation
Accuracy
```

## Ethical

```text
Ethical reasoning
Integrity
Stakeholder awareness
Risk assessment
Decision justification
```

## Leadership

```text
Ownership
Influence
Decision making
Conflict management
Team impact
Reflection
```

---

# 27. Candidate Performance Memory

Store candidate performance over time.

Example:

```text
Interview 1
System Design: 5/10

Interview 2
System Design: 5.5/10

Interview 3
System Design: 6.5/10
```

Use this data to personalize future practice.

The system should eventually identify:

```text
Strengths
Weaknesses
Improvement trends
Repeated mistakes
Unpracticed competencies
```

---

# 28. Voice Architecture

For MVP:

```text
Candidate
   |
Microphone
   |
Pipecat
   |
Speech-to-text
   |
Interview Engine
   |
LLM
   |
Text-to-speech
   |
Pipecat
   |
Candidate
```

Pipecat is only the voice interface.

The Interview Engine owns:

- interview state
- question selection
- evaluation
- follow-ups
- progression
- completion

Do not put core interview business logic inside Pipecat.

Later, Pipecat can be replaced with:

- LiveKit Agents
- Vapi (managed)
- another voice provider

without rewriting the Interview Engine.

---

# 29. Transcript

Persist the interview transcript.

Each interaction should contain:

```text
speaker
text
timestamp
question_id
```

Audio itself is never stored — only the transcribed text is persisted. No user consent flow is needed for recording storage since no recording file exists.

Evaluation works from transcript text.

---

# 30. RAG

Use PostgreSQL + pgvector initially.

RAG sources:

```text
Candidate Resume
Job Description
Role Knowledge
Organization Research
Public Interview Reports
Curated Question Bank
```

Pipeline:

```text
Source
  ↓
Text Extraction
  ↓
Chunking
  ↓
Embedding
  ↓
PostgreSQL + pgvector
  ↓
Metadata-filtered Retrieval
  ↓
Relevant Context
  ↓
Question Generator / Evaluator
```

Important metadata:

```text
candidate_id
company_id
role_id
source_type
competency
question_type
difficulty
source_date
confidence
```

Always filter retrieval by authorization and ownership.

---

# 31. Frontend UX

Dashboard:

```text
AI Interviewer

[ Focused Practice ]

Practice exactly what you want
to improve.

[ Real Interview Simulation ]

Experience a realistic interview
for your target role and company.
```

---

# 32. Focused Practice UX

Flow:

```text
Practice
   ↓
Company
   ↓
Role
   ↓
Resume
   ↓
Question Type
   ↓
Show representative examples
   ↓
Start Interview
```

Example preview:

```text
Behavioral / STAR

Examples:

"Tell me about a time you disagreed
with a teammate."

"Describe a time you failed and what
you learned."

"Tell me about a time you worked
under pressure."

These examples explain the practice category.
They are not necessarily the exact questions
used in the session.
```

Then:

```text
[ Start Behavioral Interview ]
```

---

# 33. Real Interview Simulation UX

Flow:

```text
Real Interview
   ↓
Company
   ↓
Role
   ↓
Resume
   ↓
Job Description
   ↓
Experience level
   ↓
Duration
   ↓
Start Simulation
```

Do not reveal the exact upcoming question sequence.

The candidate should experience uncertainty similar to a real interview.

---

# 34. Security

Implement from the beginning:

- Firebase authentication
- server-side authorization
- ownership checks
- HTTPS in production
- input validation
- file type validation
- file size limits
- rate limiting
- secure environment variables
- no secrets in Git
- signed URLs for private files
- database least privilege
- prompt-injection protection
- tenant/candidate data isolation

Treat resumes, documents, retrieved content, and candidate answers as untrusted data.

Do not allow retrieved content to override system instructions.

---

# 35. Docker

Use Docker from the beginning.

Local:

```text
Docker Compose
├── PostgreSQL
└── FastAPI
```

Next.js can run locally during development.

Production:

```text
FastAPI container
       |
       v
Managed PostgreSQL
```

Do not run production PostgreSQL in the same container as FastAPI.

---

# 36. Production Architecture for Initial Low Traffic

```text
                     Internet
                        |
                        v
                    Vercel
                  Next.js App
                        |
                        v
                FastAPI Container
                        |
         +--------------+--------------+
         |              |              |
         v              v              v
    PostgreSQL      Firebase Auth   Object Storage
    + pgvector
         |
         v
      LLM APIs
```

Do not initially add:

- Kubernetes
- Kafka
- microservices
- Redis cluster
- dedicated vector database
- GPU infrastructure
- self-managed production database

---

# 37. Initial API

Use `/api/v1`.

Candidate:

```text
GET  /api/v1/profile
PUT  /api/v1/profile
```

Resume:

```text
POST   /api/v1/resumes
GET    /api/v1/resumes
DELETE /api/v1/resumes/{id}
```

Jobs:

```text
POST /api/v1/jobs
GET  /api/v1/jobs
GET  /api/v1/jobs/{id}
```

Interviews:

```text
POST /api/v1/interviews
GET  /api/v1/interviews
GET  /api/v1/interviews/{id}
POST /api/v1/interviews/{id}/start
POST /api/v1/interviews/{id}/answers
POST /api/v1/interviews/{id}/complete
```

Results:

```text
GET /api/v1/interviews/{id}/results
GET /api/v1/interviews/{id}/answers
GET /api/v1/progress
```

Research:

```text
POST /api/v1/research/company
GET  /api/v1/research/company/{id}
```

The research endpoints can initially be internal/admin functionality rather than exposed directly to all candidates.

---

# 38. AI Provider Abstraction

Do not hard-code one LLM provider everywhere.

Use:

```text
Interview Engine
      |
      v
AI Service Interface
      |
      +---- LLM Provider
      +---- Embedding Provider
      +---- Evaluation Provider
```

This allows future provider changes.

Use structured outputs for:

- question generation
- evaluation
- interview planning
- final reports

Do not rely on free-form AI responses for critical application state.

---

# 39. What to Build Now

## Phase 1 — Foundation

- [ ] Git repository
- [ ] Next.js + TypeScript
- [ ] FastAPI
- [ ] Docker
- [ ] PostgreSQL
- [ ] pgvector
- [ ] SQLAlchemy
- [ ] Alembic
- [ ] Firebase Auth
- [ ] environment configuration

## Phase 2 — Candidate

- [ ] Profile
- [ ] Resume upload
- [ ] Resume extraction
- [ ] Job description
- [ ] Role selection

## Phase 3 — Question Intelligence Foundation

- [ ] Question taxonomy
- [ ] Competencies
- [ ] Role profiles
- [ ] Question metadata
- [ ] Basic curated question examples
- [ ] Basic question ranking
- [ ] Evaluation rubrics

## Phase 4 — Interview Engine

- [ ] Interview state machine
- [ ] Practice strategy
- [ ] Simulation strategy
- [ ] Question generation
- [ ] Answer storage
- [ ] Evaluation
- [ ] Follow-ups
- [ ] Adaptive progression
- [ ] Final report

## Phase 5 — RAG / Research

- [ ] Resume RAG
- [ ] JD RAG
- [ ] Role knowledge
- [ ] Organization research
- [ ] Public interview source ingestion
- [ ] Source tracking
- [ ] pgvector retrieval
- [ ] Evidence/confidence tracking

## Phase 6 — Voice

- [ ] Pipecat integration
- [ ] Speech recognition
- [ ] TTS
- [ ] Transcript persistence
- [ ] Voice interview completion

## Phase 7 — Launch

- [ ] Production deployment
- [ ] Managed PostgreSQL
- [ ] Object storage
- [ ] HTTPS
- [ ] Sentry
- [ ] Logging
- [ ] Backup verification
- [ ] AI cost tracking
- [ ] Basic rate limiting

---

# 40. Build Later

Do not implement these in the MVP:

## Voice

- LiveKit migration
- Vapi migration (managed voice, if needed later)
- custom WebRTC
- advanced interruption handling
- self-hosted GPU-based STT/TTS infrastructure

## Infrastructure

- Redis
- background workers
- queues
- autoscaling
- load balancing
- microservices
- Kubernetes

## AI

- fine-tuning
- custom evaluation models
- ML readiness prediction
- advanced reranking
- dedicated vector DB

## Interview types

- coding sandbox
- system design canvas
- video interview
- case simulation environment

## Business

- subscriptions
- payments
- enterprise accounts
- recruiter dashboards
- team analytics
- SSO

Only add these based on real user requirements.

---

# 41. Future Coding Interview Security

If coding interviews are added later:

```text
Candidate Code
      |
      v
Secure Sandbox
      |
      v
Tests
      |
      v
Execution Results
      |
      v
AI Evaluation
```

Never execute candidate code directly inside the FastAPI process.

Docker alone should not be treated as a complete production-grade security sandbox.

---

# 42. Monitoring

Track:

```text
interviews_started
interviews_completed
average_interview_duration
questions_asked
followups_generated
AI_errors
voice_errors
tokens_used
AI_cost_per_interview
evaluation_scores
```

Also track question intelligence quality:

```text
question_source
question_selection_reason
question_confidence
question_relevance
```

---

# 43. V1 Definition of Done

A candidate should be able to complete:

```text
Sign up
   ↓
Create profile
   ↓
Upload resume
   ↓
Enter job description
   ↓
Select company + role
   ↓
Choose:

Focused Practice
OR
Real Interview Simulation

   ↓
Research / Question Intelligence
   ↓
Start voice interview
   ↓
AI asks realistic question
   ↓
Candidate answers
   ↓
AI evaluates
   ↓
AI asks adaptive follow-up
   ↓
Interview continues
   ↓
Interview completes
   ↓
Candidate receives report
```

The experience must feel like a real interview, not a chatbot questionnaire.

---

# 44. Critical Engineering Rules

1. Build a modular monolith.
2. Do not build microservices.
3. Do not build Kubernetes.
4. Use PostgreSQL + pgvector initially.
5. Use Firebase Auth, not Firestore, for application data.
6. Use Docker for local infrastructure.
7. Keep Pipecat separate from Interview Engine.
8. Do not hard-code one LLM provider into the business logic.
9. Do not make the LLM responsible for authorization or unrestricted database operations.
10. Use structured AI outputs.
11. Every user-owned resource requires authorization checks.
12. Store source/provenance for organization research.
13. Never fabricate company-specific interview patterns.
14. Distinguish official information from public reports and AI-generated predictions.
15. Do not blindly repeat historical questions; generate conceptually relevant variations.
16. Practice Mode must remain adaptive and interview-like.
17. Simulation Mode must dynamically choose the question mix.
18. Both modes must use the same Interview Engine and Question Intelligence.
19. Don't store large files in PostgreSQL.
20. Never commit secrets.
21. Keep development and production environments separate.
22. Add complexity only when actual usage requires it.

---

# 45. Most Important Product Requirement

The system should optimize for:

**REALISM + RELEVANCE + ADAPTIVITY**

For every question, the system should effectively answer:

```text
Why this candidate?
Why this role?
Why this company?
Why this question type?
Why this question now?
What evidence supports asking it?
What competency does it test?
How should the answer be evaluated?
What should the interviewer ask next?
```

The candidate should feel that a knowledgeable human interviewer researched the role and organization before the interview.

---

# 46. Final Architecture

```text
                              CANDIDATE
                                  |
                                  v
                         Next.js / React
                                  |
                                  v
                         FastAPI Backend
                                  |
                 +----------------+----------------+
                 |                                 |
                 v                                 v
          PRACTICE STRATEGY                 SIMULATION STRATEGY
                 |                                 |
                 |                           AI selects mix
                 |                                 |
                 +----------------+----------------+
                                  |
                                  v
                         INTERVIEW ENGINE
                                  |
                                  v
                      QUESTION INTELLIGENCE
                                  |
          +-----------------------+-----------------------+
          |                       |                       |
          v                       v                       v
        ROLE                 ORGANIZATION             CANDIDATE
     KNOWLEDGE                 RESEARCH                CONTEXT
          |                       |                       |
          |                       |                       |
          +-----------------------+-----------------------+
                                  |
                                  v
                         EVIDENCE / RAG LAYER
                                  |
          +-----------------------+-----------------------+
          |                       |                       |
          v                       v                       v
       Official             Public Reports          Platform Data
       Sources              / Trends                / History
                                  |
                                  v
                         QUESTION RANKING
                                  |
                                  v
                       QUESTION GENERATOR
                                  |
                                  v
                        Pipecat Voice Layer
                                  |
                                  v
                              CANDIDATE
                                  |
                                  v
                               ANSWER
                                  |
                                  v
                     TYPE-SPECIFIC EVALUATOR
                                  |
                                  v
                      ADAPTIVE DECISION ENGINE
                                  |
                    +-------------+-------------+
                    |                           |
                    v                           v
                FOLLOW-UP                 NEXT COMPETENCY
                    |                           |
                    +-------------+-------------+
                                  |
                                  v
                           FINAL REPORT
                                  |
                                  v
                       CANDIDATE PROGRESS
```

---

# 47. Final Product Definition

The product should be understood as:

> **An evidence-driven AI interview simulator that researches the candidate's target role and organization, analyzes relevant interview patterns and core concepts, and conducts realistic adaptive interviews. Candidates can either practice a specific question category through a focused interview or enter a full simulation where the AI dynamically determines the interview structure.**

The long-term moat should not be "we have voice AI."

The long-term moat should be:

```text
Role Intelligence
       +
Organization Intelligence
       +
Question Intelligence
       +
Interview Performance Data
       +
Adaptive Interview Engine
       +
Personalized Candidate Learning
```

Build the MVP around this principle, but keep the initial implementation simple enough for a solo developer.
