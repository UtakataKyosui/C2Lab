---
name: Ollama Consult
description: >
  Use this skill when planning approaches, comparing implementation options, or validating
  design decisions by consulting a local LLM via Ollama. Activate when the user says
  "壁打ちしたい", "ローカルLLMに相談", "アプローチを比較したい", "方針を確認したい",
  "ローカルで検討", or when brainstorming is needed before committing to an approach.
  Also activates when offloading lightweight reasoning to reduce Claude API usage.
version: 0.1.0
---

# Ollama Consult

Consult a local LLM (Ollama) for planning, approach comparison, and decision validation.
The local LLM acts as a fast, private sounding board—not a source of ground truth.

## When to Use

**Use `consult_local_llm` when:**
- Brainstorming multiple implementation approaches before choosing one
- Validating a plan against tradeoffs (performance vs simplicity, etc.)
- Checking whether a direction makes sense before diving deep
- Generating alternative perspectives on a design problem
- Lightweight reasoning that doesn't require Claude's full capabilities

**Do NOT use for:**
- Security-sensitive analysis (credentials, auth flows, vulnerabilities)
- Tasks requiring up-to-date knowledge (latest APIs, recent events)
- Authoritative technical decisions—always validate the output
- Large codebases or complex multi-file reasoning (local LLMs have smaller context)

## How to Consult Effectively

### 1. Ask Specific Questions

```
Bad:  "Should I use React?"
Good: "I'm building a dashboard that needs real-time updates and has 3 devs
       familiar with Vue. Should I use React or Vue? Key constraints: 6-week
       deadline, no SSR needed."
```

### 2. Provide Relevant Context

Use the `context` parameter to share background information:

```
question: "Which database indexing strategy fits this access pattern?"
context: "Table has 10M rows. Primary queries: lookup by user_id (80%),
          range scan by created_at (15%), full-text search (5%).
          PostgreSQL 15, < 500ms p99 latency required."
```

### 3. Request Structured Output

Ask for comparisons, pros/cons, or numbered options:

```
"List 3 approaches for [X]. For each: one-line summary, main advantage,
 main disadvantage."
```

## Interpreting Results

The local LLM provides a **perspective**, not a verdict:
- Cross-check important recommendations with documentation or tests
- Use the output as a starting point for deeper analysis
- The model may be outdated or hallucinate—verify before implementing

## Check Setup First

Before consulting, verify Ollama is running and configured:
1. Call `list_models` to confirm connection and available models
2. Ensure `.claude/settings.local.json` has `env.OLLAMA_MODEL` set to your desired model
3. If Ollama is not running: `ollama serve`

## Example Workflow

```
User: "Redisとin-memoryキャッシュ、どちらが良い？"

1. Call consult_local_llm:
   question: "Redis vs in-memory cache for session storage. Which fits better?"
   context: "Single-instance Node.js app, ~1000 concurrent users, sessions
             expire in 30min, no horizontal scaling planned yet."

2. Review the local LLM's tradeoff analysis

3. Synthesize with your own knowledge and present to user
```
