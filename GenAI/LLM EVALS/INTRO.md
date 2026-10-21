# LLM Evaluation

LLM evaluation is the process of systematically testing Large Language Models to measure their accuracy, reliability, and safety in real-world scenarios. It is a crucial step for developers to catch hallucinations, verify groundedness in external data, and ensure the AI meets specific business or product requirements before deployment.

> **Simple analogy:** Think of LLM evaluation like a school exam — instead of guessing whether a student "seems smart," you give them structured tests to measure what they actually know and where they struggle.

---

## Vibe Testing vs. Proper Evals

### Vibe Testing
Vibe testing means casually trying an LLM app with a few prompts and judging it by feel. It only works for personal projects.

**Example of vibe testing:**
> "I asked the chatbot three questions, it answered well, seems good to go!"

**Why it fails at scale:** Two developers might get completely different "vibes" from the same model. There's no way to compare results before and after a change, and edge cases are never discovered.

---

## Curriculum

1. LLM Evals
2. LLM Evals Landscape
3. LLM Evals Benchmarks
4. LLM-Based Application Evals
5. Evals Pipeline
6. RAG Evals
7. Agent Evals
8. Safety Evals
9. Operational Evals

---

## What are LLM Evals?

LLM evals are **systematic, repeatable tests** used to judge an LLM or LLM-powered system against clear criteria.

> **In plain terms:** An eval answers the question — *"Does this model/app actually do what we need it to do, reliably and consistently?"*

An eval is **not just a metric**. It is the **complete testing setup** — including the dataset, the scoring method, and the criteria for success.

---

### 1. Systematic

Evals should not involve random prompting. You create **planned test cases and datasets** that cover the range of real inputs your system will face.

**Example:**
Instead of randomly asking "What is the capital of France?", a systematic eval for a geography assistant would include:
- Easy questions: "What is the capital of Japan?"
- Tricky questions: "What is the capital of Australia?" *(many people wrongly say Sydney)*
- Edge cases: "What is the capital of Kosovo?" *(disputed internationally)*

---

### 2. Repeatable

The same eval must be runnable again at any point. If you change the prompt, model, retriever, chunking strategy, or system instructions, you should be able to **run the same test and compare results**.

**Example:**
You change your system prompt from `"Be concise"` to `"Answer in 2 sentences or less"`. Running the same eval before and after lets you see exactly whether the change helped or hurt performance — rather than guessing.

---

### 3. Clear Criteria

You must define **what "good" looks like** before running the eval.

**Example — Summarization Task:**

| Criterion | Bad Definition | Good Definition |
|---|---|---|
| Accuracy | "The summary is correct" | "The summary contains all key points from the source and no fabricated facts" |
| Length | "Not too long" | "Between 50–100 words" |
| Tone | "Sounds professional" | "No informal language; no first-person pronouns" |

---

## Model Evals vs. Application Evals

Evaluation in the LLM ecosystem divides into two primary paradigms: evaluating the **underlying model** in isolation versus evaluating the **complete application** that incorporates the model.

### 1. Model Evals

Model evals evaluate the **model itself** — its raw capabilities independent of any application. The goal is to test what the model can do.

**Capabilities typically tested:**
- Reasoning
- Knowledge
- Mathematics
- Coding
- Instruction following
- Long-context understanding
- Multimodal understanding (text + images)
- Tool use

Model capabilities are generally evaluated using **Benchmarks**.

**Example benchmarks:**
- **MMLU** — tests knowledge across 57 academic subjects
- **HumanEval** — tests Python code generation
- **GSM8K** — tests grade-school math reasoning
- **MATH** — tests competition-level mathematics

> **Key point:** Model evals tell you if the *engine* is powerful. Application evals tell you if the *car* drives well for your specific roads.

---

### 2. Application Evals

Application evals assess the **behaviour and performance of an LLM-powered application**, whether at the level of the entire system or a specific component within it.

**Components that may be evaluated:**

| Component | What it Does |
|---|---|
| LLM / Model | Generates the response |
| Prompt Layer | Shapes the model's behaviour via instructions |
| Retrieval System | Fetches relevant context (used in RAG) |
| Embedding Model | Converts text to vectors for search |
| Vector Database | Stores and retrieves embeddings |
| Output Parser | Structures the model's raw output |
| Guardrails | Filters unsafe or off-topic responses |
| Orchestrator / Workflow | Coordinates multi-step logic |
| Tools / APIs | External services the model can call |
| Memory / Context | Stores conversation or session history |
| Monitoring / Logging | Tracks performance in production |
| Feedback Loop | Incorporates user feedback to improve |

> **Important:** One LLM-based application may require **several different evals** — one for retrieval quality, one for answer accuracy, one for safety, and so on.

---

### LLM Application Eval Workflow

Here is the standard end-to-end workflow for evaluating an LLM-powered application:

```
1. Define Task & Target
       ↓
2. Define Success Criteria
       ↓
3. Build a Dataset
       ↓
4. Define an Eval Method
       ↓
5. Run the Model
       ↓
6. Evaluate the Results
       ↓
7. Analyze the Results
       ↓
8. Improve the Model/App
       ↓
9. Deploy and Monitor
       ↓
10. Respond to Production Failures
```

**Worked Example — Customer Support Chatbot:**

| Step | Example |
|---|---|
| **Define Task & Target** | Answer customer questions about order status, returns, and billing |
| **Define Success Criteria** | Correct answer rate ≥ 90%, no hallucinated policies, response under 100 words |
| **Build a Dataset** | 200 real customer queries labelled with expected answers |
| **Define Eval Method** | LLM-as-judge + exact-match check for order numbers |
| **Run the Model** | Send all 200 queries through the app |
| **Evaluate Results** | Score each response against the criteria |
| **Analyze Results** | Identify failure patterns (e.g., wrong on billing questions) |
| **Improve** | Add billing FAQs to the retrieval corpus; refine the prompt |
| **Deploy & Monitor** | Track live accuracy, latency, and user thumbs-down rate |
| **Production Failures** | Alert if accuracy drops below threshold; trigger re-eval |

---

> **Summary:** LLM evals move you from "this feels right" to "we know this works." They are the engineering discipline that makes AI products reliable, improvable, and trustworthy.

### Why AI Applications Need Multiple Eval Pipelines

Modern AI applications are compound systems, not monolithic models. A failure in an AI product can stem from an ineffective prompt, poor retrieval, flawed tool execution, or model hallucination. To isolate and diagnose issues effectively, evaluation must occur across three distinct testing tiers:

1. **Component-Level Evaluation (Unit Evals):** Isolating individual architectural building blocks to test their specific performance independent of the rest of the system:
   - **Prompt Layer:** Prompt templates, system instructions, and few-shot formatting.
   - **Retriever:** Keyword (BM25), dense vector, or hybrid retrieval recall and precision.
   - **Reranker:** Cross-encoder scoring and relevance re-ordering accuracy.
   - **Query Rewriter:** Query expansion, decomposition, and conversational context resolution.
   - **Embedding Model:** Domain semantic alignment and vector representation quality.
   - **Vector Database:** Index recall, nearest-neighbor search accuracy, and query latency.
   - **Output Parser:** JSON parsing, structured schema validation, and type extraction.
   - **Tool / Function Selector:** Correct identification and selection of external APIs.
   - **Conversation Memory:** Context window management, message truncation, and summary fidelity.
   - **Guardrails:** Input moderation, PII redaction, and output safety filters.

2. **Workflow-Level Evaluation (Integration Evals):** Validating multi-step pipelines and intermediate execution logic:
   - **RAG Workflow:** End-to-end retrieval, context injection, and answer synthesis loop.
   - **Agent Workflow:** Multi-step reasoning loops, autonomous planning, tool calls, and error recovery.
   - **Multi-Turn Conversation Workflow:** Dialog state tracking, context carryover, and persona consistency.
   - **Structured Output Workflow:** Deterministic schema adherence, extraction fidelity, and fallback handling.
   - **Document Extraction Workflow:** Complex multi-page parsing, table extraction, OCR, and summarization pipelines.

3. **Entire Application Evaluation (System Evals):**
   - Evaluating the complete product end-to-end as a black box against user goals, edge cases, and business KPIs.

---

## Application Eval Risk Categories

Every production LLM application must be evaluated across three primary risk categories:

| Risk Category | Core Question | Focus Areas |
|---|---|---|
| **1. Application Quality** | *Is the response accurate, relevant, and well-structured?* | Task correctness, groundedness, completeness, and instruction following |
| **2. Safety & Security** | *Could the response cause harm, leak data, or be manipulated?* | Toxicity, bias, prompt injection, jailbreaks, and PII leakage |
| **3. Operational Performance** | *Is it fast, reliable, and cost-effective at scale?* | Latency (TTFT & E2E), cost per request, token efficiency, and error rates |

---

## 1. Application Quality

### 1a. Core Generation Quality

| Criterion | Description |
|---|---|
| **Correctness / Accuracy** | Whether the factual claims in the answer are objectively true and verifiable. |
| **Relevance** | Whether the answer directly addresses the user's specific intent without extraneous filler. |
| **Completeness** | Whether the answer addresses all parts and constraints of a multi-part query. |
| **Instruction Following** | Whether the output strictly obeys formatting, length, tone, and negative constraints. |
| **Conciseness** | Whether the output conveys the necessary information without unnecessary verbosity or fluff. |

---

### 1b. RAG-Specific Quality

In Retrieval-Augmented Generation (RAG), quality centers on the **RAG Triad** (Context Relevance, Groundedness, and Answer Relevance) alongside retrieval effectiveness:

| Criterion | Description |
|---|---|
| **Context Relevance** | Whether the retrieved document chunks are relevant to the user query and free of irrelevant noise. |
| **Retrieval Recall** | Whether all source chunks required to answer the query were successfully retrieved in the top $k$ results. |
| **Groundedness / Faithfulness** | Whether every factual claim in the generated response is strictly derived from the retrieved context (no hallucination). |
| **Answer Relevance** | Whether the generated response directly answers the user query based on the retrieved context. |
| **Citation Accuracy** | Whether inline citations and source attributions genuinely support the claims they reference. |

---

### 1c. Agent / Tool-Use Quality

For autonomous agents interacting with APIs, code execution environments, or external tools:

| Criterion | Description |
|---|---|
| **Tool Selection** | Whether the agent correctly chose the appropriate tool for the specific sub-task. |
| **Parameter Correctness** | Whether the tool was invoked with valid, correctly typed, and well-formatted arguments. |
| **Task Completion** | Whether the agent successfully achieved the user's overall goal within a reasonable step limit. |
| **Error Recovery** | Whether the agent handled tool failures, exceptions, or timeouts gracefully and retried sensibly. |
| **Trajectory Efficiency** | Whether the agent took an optimal sequence of actions without circular loops or redundant tool calls. |

---

### 1d. Multi-Turn Conversation Quality

| Criterion | Description |
|---|---|
| **Context Retention / Memory** | Whether the model remembers facts, constraints, and preferences established earlier in the conversation. |
| **Clarification Behavior** | Whether the model asks clarifying questions when a request is ambiguous rather than guessing. |
| **Persona & Tone Consistency** | Whether the model maintains its designated tone, persona, and voice consistently across multiple turns. |
| **Conversational Coherence** | Whether replies flow naturally from previous exchanges without contradictory statements or repetitive loops. |

---

## 2. Safety & Security

Evaluating against safety and security risks ensures regulatory compliance, protects brand reputation, and prevents malicious exploitation:

| Criterion | Description |
|---|---|
| **Toxicity & Abuse** | Whether the output contains offensive, hateful, harassing, or profane language. |
| **Harmful Content** | Whether the model provides dangerous instructions (e.g., self-harm, cyberattacks, weapon synthesis, illegal acts). |
| **Bias & Fairness** | Whether outputs demonstrate demographic prejudice, stereotyping, or unfair discrimination across groups. |
| **PII & Secret Leakage** | Whether the model inadvertently exposes personally identifiable information (PII), API keys, or proprietary internal data. |
| **Prompt Injection Resistance** | Whether the system resists direct and indirect prompt injections designed to hijack model instructions. |
| **Jailbreak Resistance** | Whether the model resists adversarial roleplay, cipher tricks, or cognitive framing aimed at bypassing safety guardrails. |
| **System Prompt Exfiltration** | Whether the model prevents users from extracting proprietary system prompts and internal guidelines. |

---

## 3. Operational & System Performance

Operational metrics evaluate the engineering viability, speed, and unit economics of running the system in production:

| Criterion | Description |
|---|---|
| **Time to First Token (TTFT)** | Latency until the first token streams to the user (critical for real-time interactive UX). |
| **End-to-End Latency** | Total elapsed time from initial request submission to the final token received. |
| **Throughput (Tokens/Sec)** | Processing capacity and token generation speed under concurrent production load. |
| **Cost Per Request** | Total expenditure across input tokens, output tokens, embedding API calls, and external tool invocations. |
| **Token Efficiency** | Whether the prompt and output convey the required information with minimal token overhead. |
| **Error & Timeout Rate** | Percentage of requests that fail due to API timeouts, rate limits, parsing errors, or server crashes. |
| **Latency Under Load** | System stability, queueing delays, and performance degradation under peak concurrent traffic. |

---

## LLM Application Evals: Methods

An **evaluation method** is the mechanism used to decide whether an LLM output meets defined quality standards — the specific procedure that ingests an input, context, and output, and produces a quantitative score or qualitative verdict.

Evaluation methods fall into three broad paradigms:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        EVALUATION METHODS                              │
├─────────────────────┬──────────────────────────┬───────────────────────┤
│ 1. Programmatic     │ 2. Human Evaluation      │ 3. Model-Graded       │
│    (Deterministic)  │    (Human-in-the-Loop)   │    (LLM-as-a-Judge)   │
├─────────────────────┼──────────────────────────┼───────────────────────┤
│ • Exact Match/Regex │ • Direct Rubric Grading  │ • Single-Answer Score │
│ • Schema Validation │ • Pairwise A/B Arena     │ • Pairwise Comparison │
│ • NLP Metrics       │ • Red Teaming            │ • Reference-Backed    │
│ • IR Metrics        │ • Production A/B Testing │ • Reference-Free      │
└─────────────────────┴──────────────────────────┴───────────────────────┘
```

### 1. Programmatic / Deterministic Evaluation
Deterministic code executes tests without invoking an LLM. It is fast, 100% reproducible, cost-free, and ideal for automated CI/CD regression pipelines.

- **Rule-Based Checks:** Exact string matching, regex pattern validation, substring presence/absence, character/word length limits, and forbidden word filters.
- **Schema & Syntax Validation:** Verifying JSON structure, Pydantic model parsing, SQL syntax correctness, and data type validation.
- **Lexical & NLP Metrics:** Measuring textual overlap against reference answers:
  - **ROUGE (Recall-Oriented Understudy for Gisting Evaluation):** Measures n-gram overlap, commonly used for summarization tasks.
  - **BLEU (Bilingual Evaluation Understudy):** Measures precision of n-grams, commonly used for machine translation.
  - **Levenshtein Distance:** Quantifies character edit distance between predicted and expected strings.
- **Information Retrieval (IR) Metrics:** Mathematical metrics used to evaluate retriever performance in RAG systems:
  - **Recall@k:** Fraction of all relevant documents captured within the top $k$ retrieved results:
    $$\text{Recall@k} = \frac{\text{Relevant items retrieved in top } k}{\text{Total relevant items}}$$
  - **Precision@k:** Fraction of retrieved items in the top $k$ results that are genuinely relevant:
    $$\text{Precision@k} = \frac{\text{Relevant items retrieved in top } k}{k}$$
  - **Mean Reciprocal Rank (MRR):** Evaluates how high up in the ranking the first relevant document appears.
  - **NDCG (Normalized Discounted Cumulative Gain):** Evaluates ranked retrieval where higher-ranking relevant documents contribute more score than lower-ranking ones.

### 2. Human Evaluation
Human judgment remains the gold standard for nuanced, subjective qualities such as tone, humor, domain expertise, complex reasoning, and real-world alignment.

- **Direct Rubric Grading:** Domain experts review model outputs and assign scores based on explicit criteria (e.g., 1–5 scale for helpfulness, tone, and accuracy).
- **Pairwise Comparison (Side-by-Side / Arena):** Evaluators review outputs from Model A and Model B blind and vote on which response is superior (or declare a tie).
- **Red Teaming:** Security and domain specialists actively attack the application to discover vulnerabilities, jailbreaks, logic traps, and safety breaches.
- **A/B Testing in Production:** Live end users act as graders via behavioral signals (e.g., thumbs up/down, response copy rate, session completion, and retention).
- **Gold Dataset Curation:** Subject matter experts author and verify canonical reference answers, edge cases, and ground-truth test splits.
- **Human-in-the-Loop (HITL):** A human reviewer acts as a verification checkpoint inside high-stakes production workflows (e.g., medical, legal, financial) before responses are delivered to end users.

### 3. Model-Graded Evaluation (LLM-as-a-Judge)
An advanced, highly capable LLM (such as GPT-4o, Claude 3.5 Sonnet, or Gemini 1.5 Pro) evaluates application outputs using structured prompts and scoring rubrics. This bridges the gap between the speed of programmatic evals and the nuance of human judgment.

- **Single-Response Scoring:** The judge evaluates an individual output against a rubric (e.g., 1–5 scale) using **Chain-of-Thought (CoT)** reasoning to explain its score before outputting the final rating.
- **Pairwise Comparison:** The judge evaluates two candidate responses side-by-side, determining which is better according to specified criteria.
- **Reference-Backed vs. Reference-Free Judging:** The judge can evaluate against a ground-truth reference answer or evaluate standalone qualities (e.g., groundedness against retrieved context, politeness, adherence to instructions) without any reference.

> [!TIP]
> **Mitigating Common LLM-as-a-Judge Biases:**
> - **Position Bias:** Judges often favor whichever response is presented first in pairwise evaluations. *Fix: Swap response order and run twice, averaging the results.*
> - **Verbosity Bias:** Models naturally favor longer, wordier answers even when bloated. *Fix: Explicitly penalize verbosity and fluff in the judging rubric.*
> - **Self-Enhancement Bias:** LLMs tend to favor outputs generated by models from their own family. *Fix: Use neutral or cross-family judge models.*

---

## Reference-Based vs. Reference-Free Evals

When evaluating generated text, evals fall into two fundamental paradigms depending on whether a predetermined "correct" answer is required:

### 1. Reference-Based Evals (Ground-Truth Evals)
In reference-based evaluation, each test case includes a **known correct reference answer** (gold standard) created in advance. The eval grades the system output by directly comparing it against the reference.

- **How it works:** Compares model output to the pre-written ground truth for factual overlap, semantic similarity, or exact equivalence.
- **Best suited for:** Fact-based QA, summarization with gold summaries, code generation with unit tests, mathematical problem-solving, and entity extraction.
- **Common techniques:** Exact match, F1 score, BLEU / ROUGE, BERTScore, semantic embedding similarity, and reference-guided LLM judging.
- **Key challenge:** Authoring and maintaining comprehensive, high-quality reference answers is labor-intensive and expensive.

### 2. Reference-Free Evals (Criterion-Based Evals)
In reference-free evaluation, there is **no predetermined ground-truth answer**. The eval inspects the generated output directly on its own merits, evaluating whether it complies with specific criteria, rubrics, or input context.

- **How it works:** Assesses the output against a standard rubric (e.g., "Is the tone empathetic?"), constraints (e.g., "Is it under 100 words?"), or source material (e.g., "Is every claim supported by the retrieved context?").
- **Best suited for:** Open-ended creative generation, conversational chatbots, tone and style compliance, safety/toxicity screening, and RAG groundedness / hallucination detection.
- **Common techniques:** LLM-as-a-judge rubrics, rule-based constraint checkers, toxicity classifiers, and faithfulness verifiers (e.g., Ragas, TruLens).
- **Key advantage:** Highly scalable for real production traffic because no human needs to write answers in advance.

### Comparison Summary

| Dimension | Reference-Based Evals | Reference-Free Evals |
|---|---|---|
| **Ground Truth Required** | Yes (pre-written gold standard answer) | No (evaluates against rubrics, constraints, or context) |
| **Dataset Creation Effort** | High (experts must author and verify target answers) | Low-to-Moderate (requires only representative user inputs) |
| **Primary Focus** | Factual correctness, precision, exact equivalence | Groundedness, relevance, safety, style, and fluency |
| **Common Tasks** | Math, coding, closed-domain QA, translation | RAG groundedness, conversational AI, creative writing, safety |
| **Production Applicability** | Primarily used in offline pre-deployment test suites | Can run directly on live production logs without human labels |
| **Evaluation Speed & Cost** | Fast and cheap when using deterministic metrics | Can incur LLM API costs if using LLM-as-a-judge |