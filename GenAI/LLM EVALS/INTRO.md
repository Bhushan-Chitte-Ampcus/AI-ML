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

| Criteria | Bad Definition | Good Definition |
|---|---|---|
| Accuracy | "The summary is correct" | "The summary contains all key points from the source and no fabricated facts" |
| Length | "Not too long" | "Between 50–100 words" |
| Tone | "Sounds professional" | "No informal language; no first-person pronouns" |

---

## Model Evals

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

## Application Evals

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
