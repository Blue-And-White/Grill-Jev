---
name: grill-jev
description: "Use Jev-assisted decision making while carrying out a user task. Turn decision points into Choice, Noul, or Score questions, consult Jev through the bundled script, act, and reassess using observed outcomes."
---

# Grill Jev

You own the user's task: observe, propose options, execute, and verify. For each new unresolved judgment within the user-delegated scope, frame typed questions for Jev, call the bundled helper, and use its answers to continue. Repeat until complete, genuinely blocked, or stopped by the user.

This skill contains the full questioning method and API helper. No other skill is required. Once loaded, apply this loop at each new substantive decision during the task; there is no need to reload the skill for every question.

Task scheduling, parallel sessions, permissions, and budgets belong to the host and user. Loading this skill does not itself create additional sessions or tasks.

## When to consult

Consult Jev when progress requires a new judgment within the delegated scope: interpreting evidence, comparing approaches, choosing which information to obtain, accepting or excluding a candidate, revising direction, or assessing whether evidence meets a qualitative completion criterion. Excluding a candidate and deciding to stop are decisions too. Do not reserve Jev for major milestones or for moments when you feel uncertain; host confidence alone is not a reason to skip a delegated judgment.

Distinguish choosing an action from executing it. Selecting which of several relevant documents to inspect may require Jev; reading the already selected document does not. Interpreting whether its contents change the conclusion is a new judgment. Keep investigating, reasoning, generating candidates, and executing yourself; Jev evaluates the questions you frame.

Follow choices the user already made, calculate deterministic facts directly, and execute steps settled by an existing decision without asking again. Tool use itself is neither a trigger nor an exemption. Consult Jev when you would otherwise ask the user for an approach choice they have already delegated; ask the user when their preference, requirement, or new authorization is missing. Jev cannot supply those on their behalf. Respect task scope and call or time limits; exhausting a limit does not silently transfer delegated judgments back to the host.

## Decision loop

### 1. Observe and build the current state

Keep your existing task context. Prepare a compact `state` containing:

- The user's goal, completion criteria, and relevant constraints.
- Relevant observations and short source excerpts or tool results, separate from candidate explanations. Include supporting and conflicting evidence, unsettled assumptions, and gaps that could change the judgment; do not send only your preferred conclusion or silently remove plausible alternatives through an unexamined assumption.
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
| `score` | Rate one dimension on an ordered rubric | 2–10 concrete level descriptions; state the dimension and direction; indexes start at zero |

All three use the same script and request envelope: `{"state": ..., "questions": {"question_id": ...}}`. Set each question's `type` to `choice`, `noul`, or `score`; these are question types, not separate conversational models. Use the complete examples in [references/api.md](references/api.md) when constructing the first request.

Choose a question pattern from the current decision's structure. Reconsider it when the evidence or candidate set changes; do not keep using a single "what next?" Choice by habit.

| Decision structure | Useful approach |
| --- | --- |
| One clear judgment | A single Choice, Noul, or Score; extra questions are unnecessary |
| Several judgments share evidence | Batch independent and explicitly conditional questions, then use the relevant answers |
| The best candidate might still be unsuitable | Selection plus a separate suitability judgment or a "none fits" outcome |
| Several competing dimensions matter | Score dimensions separately; apply task-specific constraints and combine results locally |
| Too many candidates or an existing hierarchy | Shortlist and inspect more detail, or traverse branches while retaining useful alternatives |
| A source span or generated result needs checking | Select from extracted spans, or evaluate specific claims against original evidence |
| An action changes what is known | Update state and construct new questions or candidates from its observed result |

Read the relevant section of [references/patterns.md](references/patterns.md) when applying an unfamiliar pattern. Its examples are a starting point, not an exhaustive menu. Adapt and combine them, generate task-specific questions and candidates, and use other compositions supported by the API when they fit better. A round need not contain all three types, and using an advanced pattern is not a goal in itself.

Do not embed your preferred answer or leading labels in the question. If the alternatives might be inadequate, include an actionable option to gather evidence or reframe the candidates. After that option is selected, investigate and construct revised alternatives yourself; Jev cannot generate the missing options.

Bound coverage questions to supplied material and explicit criteria. For example, ask whether the proposed report outline addresses the requirements quoted in state, rather than asking whether anything has been missed anywhere. A negative or uncertain assessment calls for host inspection and revised candidates, not an invented explanation from Jev. A positive assessment cannot establish coverage of unseen material. Use this check when coverage affects the decision, not as a mandatory extra question in every call.

Put the actual question in `instructions` and option or level meanings in `criteria`. Question IDs are routing keys, not instructions. Generate candidates from the current task instead of imposing a fixed domain menu. Describe each Score level independently; do not use bare numbers or "better than the previous level."

Use objects or arrays for instructions and criteria when named fields clarify evidence or boundaries. Reference the relevant state field directly, such as `observations.reader_report`; do not flatten useful structure into a long prose prompt. Keep arithmetic, date comparisons, and hard constraints in host code.

### 3. Call the API helper

Save each round's request and response in the task's working files. A default layout is `work/grill-jev/<session-id>/001.request.json` with corresponding response files; an existing task logging layout is also suitable. Keep concurrent sessions' records distinct and preserve earlier rounds. Save JSON with a file-writing tool; do not interpolate task text or credentials into shell commands.

```text
python3 <skill-directory>/scripts/ask_jev.py <request-file> --output <response-file>
```

The helper resolves credentials and model settings, validates the request, sends one HTTP POST, validates the complete JSON response, and saves it without overwriting earlier evidence. It does not stream tokens, maintain a conversation, or execute selected actions.

If the helper reports missing configuration, direct the user to [README.md](README.md#configuration). Continue independent evidence collection and mechanical work, but leave Jev-dependent decisions pending. Never fabricate a Jev response or silently substitute your own answer.

Wait for the actual result and inspect `answers`, `model`, and `usage`. An API failure is not a negative answer. Report the failure; do not keep retrying ambiguous network outcomes indefinitely. If Jev remains unavailable, explain the blocker and let the user decide whether to continue using the host model's judgment.

### 4. Interpret, act, and observe

- **Choice:** map the returned ID to the full option you defined, then perform the corresponding next step.
- **Suitability:** a Choice winner is relative to its alternatives. When all candidates could be inadequate, also check absolute suitability or retain an actionable "none fits" option before proceeding.
- **Noul:** retain its probability of yes. A value near the middle expresses uncertainty, not partial task completion.
- **Score:** interpret the score on the supplied `0..N-1` scale alongside its distribution and legend. A fractional score is a weighted position, not a percentage or success probability. Keep rubrics comparable when ranking alternatives; any weights across dimensions belong to the task specification.

Jev's answer informs a decision; it is not a new fact, authorization, or proof of completion. Do not invent an explanation Jev did not return. Confidence summarizes the probability distribution, not independently verified correctness. Use thresholds justified by the task's error costs and evaluations, not an arbitrary universal cutoff.

If the answer is ambiguous or conflicts with observed facts or task constraints, pause that action, obtain distinguishing evidence or narrow the question. Record why the returned answer was not followed; do not silently replace it with your preferred option. Ask the user when the missing information is actually their preference or requirement. Before acting, identify what the selected step should accomplish or clarify. Record that expectation, the action, and the observed outcome beside this round's request and response, labeling your interpretation separately from Jev's output.

### 5. Feed results into the next round or finish

After each selected action or coherent execution step, check whether its result creates a new unresolved judgment. If so, update state and consult Jev before resolving it; otherwise continue the settled steps. This check is required, but another API call is not required when no new judgment exists.

Compare the expected and observed outcomes. If progress stalled or the result contradicted the expectation, check whether evidence was missing, a question was ambiguous, candidates were inadequate, or execution failed. Preserve uncertainty about the cause rather than blaming Jev by default.

Build the next request around what changed: carry forward the relevant previous decision, actual result, invalidated assumptions, and remaining uncertainty. Obtain missing evidence, sharpen the question, or revise candidates as appropriate. Keep failed approaches visible when their results rule them out; an execution failure alone does not disprove the underlying approach. Treat previous Jev answers as judgments to reassess, not established facts.

Ask a new question when a new delegated judgment arises. Reopen an already answered question only when relevant evidence, outcomes, goals, or alternatives materially change. Do not repeatedly rephrase an unchanged question until Jev agrees with you. Feedback is carried in the next request; the helper does not retain a conversation or update model weights.

Verify completion using the task's observable acceptance criteria. Stop and retain state if no new information can resolve a recurring blocker, the budget is exhausted, or the user stops the task. Report meaningful choices and task results without narrating every API exchange.

## Keep decisions inspectable

Maintain brief decision notes alongside the round files or in the existing task log. For substantive judgments, record the question, who resolved it (Jev, host, or user), the answer or request/response reference, the resulting action, and its observed outcome. If the host resolves a judgment without Jev, state the applicable reason, such as an explicit user choice or a deterministic rule; confidence alone is not an exemption. Record any departure from Jev's answer separately from its actual output. Group routine execution steps rather than logging every tool call, and use concise reasons rather than internal reasoning transcripts.

When reporting a trial, distinguish calls from questions and task outcomes from Jev's contribution. Note whether its answers changed actions and where the host made judgments independently. Call count alone does not establish compliance or usefulness, and one task result without a comparable baseline does not establish improvement.
