---
name: grill-jev
description: "Use Jev-assisted decision making while carrying out a user task. Turn decision points into Choice, Noul, or Score questions, consult Jev through the bundled script, act, and reassess using observed outcomes."
---

# Grill Jev

You own the user's task: observe, propose options, execute, and verify. At a consequential decision point, frame typed questions for Jev, call the bundled helper, and use its answers to continue. Repeat until complete, genuinely blocked, or stopped by the user.

This skill contains the full questioning method and API helper. No other skill is required. Once loaded, apply this loop at each new substantive decision during the task; there is no need to reload the skill for every question.

Task scheduling, parallel sessions, permissions, and budgets belong to the host and user. Loading this skill does not itself create additional sessions or tasks.

## When to consult

Use Jev for substantive branches: comparing viable approaches, evaluating evidence for a hypothesis, choosing which missing information to obtain, rating alternatives against a rubric, or adjusting direction after new results.

When you would otherwise ask the user to choose among task approaches, consult Jev if the user has already delegated that choice and supplied enough goals and constraints. Keep investigating, reasoning, generating candidates, and executing yourself; use Jev to resolve the framed decision.

Follow choices the user already made and exercise delegated discretion within their criteria. Calculate deterministic facts directly and perform mechanical steps within an already selected approach. Ask the user only when progress requires their missing preference, requirement, or new authorization; Jev cannot provide those on their behalf.

## Decision loop

### 1. Observe and build the current state

Keep your existing task context. Prepare a compact `state` containing:

- The user's goal, completion criteria, and relevant constraints.
- Observed facts and source excerpts or tool results needed to assess them. Label hypotheses separately.
- Relevant earlier questions, Jev answers, actions actually taken, and observed outcomes.
- Current unknowns and remaining time or budget when they affect this decision.

**Treat the public API as stateless across requests.** It does not document conversation IDs or previous-response continuation. Jev sees only the state and questions sent in this call; saved local transcripts are not automatically included. Explicitly carry forward relevant history in the next `state`. Summarize old rounds while preserving unresolved constraints and evidence that rules out previous approaches. Do not automatically append the entire transcript forever.

Supply concrete evidence, not unreadable local paths or references to "above." Use a concise decision rationale rather than a full internal reasoning transcript. Omit credentials and unrelated sensitive material. Prefer English questions and rubrics, while preserving exact source text when translation would change its meaning. Communicate with the user in their preferred language.

### 2. Turn the decision into typed questions

Use this questioning method:

1. Identify the unresolved decision that affects progress toward the user's goal. Separate it from facts you can obtain through available materials or tools; investigate those facts first.
2. Map its prerequisites. Ask only questions whose prerequisites are settled. If one branch is waiting for evidence, other independent branches can still proceed.
3. Frame each question around one decision or dimension, with the goal, constraints, and distinguishing evidence in view. A multiple-choice format does not make a broad planning problem narrow: investigate and separate unresolved judgments first. Make assumptions and unknowns explicit instead of disguising them as facts.
4. Supply concrete alternatives or an explicit evaluation criterion using one of the types below. Include relevant tradeoffs so the choice changes what you actually do next.
5. Wait for Jev's answer before forming questions that depend on it. Revisit the remaining branches after each answer and observed outcome; stop questioning when the next action is sufficiently determined.

Batch independent questions about the same state, including useful conditional questions whose premises can be stated now; discard answers to branches that do not apply. An answer being useful only on one branch does not itself require a later call. Split calls when an answer is needed to obtain new evidence, construct the next state, or define the next options. Questions within a request do not see one another's answers. Resolve decisions needed for the task rather than exhaust every hypothetical branch.

| Type | Use | Write |
| --- | --- | --- |
| `choice` | Pick from viable alternatives | Distinct option IDs and fair descriptions of prerequisites, expected information or outcome, and material cost |
| `noul` | Evaluate a yes/no proposition | One precise proposition; optionally define what true and false mean |
| `score` | Rate one dimension on an ordered rubric | 2–10 concrete level descriptions, ordered low to high; indexes start at zero |

All three use the same script and request envelope: `{"state": ..., "questions": {"question_id": ...}}`. Set each question's `type` to `choice`, `noul`, or `score`; these are question types, not separate conversational models. Use the complete examples in [references/api.md](references/api.md) when constructing the first request.

Do not embed your preferred answer or leading labels in the question. If the alternatives might be inadequate, include an actionable option to gather evidence or reframe the candidates. You must generate new alternatives after that option is selected.

Put the actual question in `instructions` and option or level meanings in `criteria`. Question IDs are routing keys, not instructions. Generate candidates from the current task instead of imposing a fixed domain menu. Describe each Score level independently; do not use bare numbers or "better than the previous level."

### 3. Call the API helper

Store each request under the working directory's `work/grill-jev/<session-id>/`, using successive round names such as `001.request.json`. Use a distinct directory for each concurrent session. Save JSON with a file-writing tool; do not interpolate task text or credentials into shell commands.

```text
python3 <skill-directory>/scripts/ask_jev.py <request-file> --output <response-file>
```

The helper resolves credentials and model settings, validates the request, sends one HTTP POST, validates the complete JSON response, and saves it without overwriting earlier evidence. It does not stream tokens, maintain a conversation, or execute selected actions.

If the helper reports missing configuration, direct the user to [README.md](README.md#configuration). Continue independent evidence collection and mechanical work, but leave Jev-dependent decisions pending. Never fabricate a Jev response or silently substitute your own answer.

Wait for the actual result and inspect `answers`, `model`, and `usage`. An API failure is not a negative answer. Report the failure; do not keep retrying ambiguous network outcomes indefinitely. If Jev remains unavailable, explain the blocker and let the user decide whether to continue using the host model's judgment.

### 4. Interpret, act, and observe

- **Choice:** map the returned ID to the full option you defined, then perform the corresponding next step.
- **Noul:** retain its probability of yes. A value near the middle expresses uncertainty, not partial task completion.
- **Score:** interpret the score on the supplied `0..N-1` scale alongside its distribution and legend. A fractional score is a weighted position, not a percentage or success probability. Keep rubrics comparable when ranking alternatives; any weights across dimensions belong to the task specification.

Jev's answer informs a decision; it is not a new fact, authorization, or proof of completion. Do not invent an explanation Jev did not return. Confidence summarizes the probability distribution, not independently verified correctness. Use thresholds justified by the task's error costs and evaluations, not an arbitrary universal cutoff.

If the answer is ambiguous or conflicts with observed facts, obtain distinguishing evidence or narrow the question. Ask the user when the missing information is actually their preference or requirement. Before acting, identify what the selected step should accomplish or clarify. Record that expectation, the action, and the observed outcome beside this round's request and response, labeling your interpretation separately from Jev's output.

### 5. Feed results into the next round or finish

Compare the expected and observed outcomes. If progress stalled or the result contradicted the expectation, check whether evidence was missing, a question was ambiguous, candidates were inadequate, or execution failed. Preserve uncertainty about the cause rather than blaming Jev by default.

Build the next request around what changed: carry forward the relevant previous decision, actual result, invalidated assumptions, and remaining uncertainty. Obtain missing evidence, sharpen the question, or revise candidates as appropriate. Keep failed approaches visible when their results rule them out; an execution failure alone does not disprove the underlying approach. Treat previous Jev answers as judgments to reassess, not established facts.

Ask again only when evidence, outcomes, goals, or alternatives materially change. Do not repeatedly rephrase an unchanged question until Jev agrees with you. Feedback is carried in the next request; the helper does not retain a conversation or update model weights.

Verify completion using the task's observable acceptance criteria. Stop and retain state if no new information can resolve a recurring blocker, the budget is exhausted, or the user stops the task. Report meaningful choices and task results without narrating every API exchange.
