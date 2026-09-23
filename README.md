# Grill Jev

A self-contained skill that lets a host model consult Jev at decision points while
carrying out your task. Delegate task choices to Jev while your existing model
keeps investigating, reasoning, writing, and acting. The host brings observed
results back into the next decision.

- **Choice:** select among concrete alternatives.
- **Noul:** evaluate a yes/no proposition as a probability.
- **Score:** rate a dimension against an ordered rubric.

No grill-me installation is required.

## Philosophy

An agent can understand a task, identify several plausible approaches, and still
pause to ask: "I found these options. Which should I pursue?" That decision handoff
is the starting point for Grill Jev. Within the goal and discretion the user has
already delegated, the host can direct such questions to Jev and continue working.

Jev takes the role of a decision partner at those branch points. The general
model continues to do the reasoning that makes a choice meaningful: investigating
the situation, developing hypotheses, generating alternatives, and understanding
the consequences. It also writes the code or other output, operates tools, and
checks the result. The skill makes this division of work explicit inside an
existing agent.

The aim is to reduce interruptions where the agent already has enough information
to frame a bounded choice. Jev can choose within the user's stated preferences
and delegated discretion. It cannot supply an unknown personal preference or
grant new permission; those decisions still require the user. Calling it a
decision partner describes a workflow role, not a claim that it knows what the
user would think or always makes a better choice.

An open-ended task becomes a sequence of smaller decisions as evidence arrives.
Grill Jev uses a general-purpose model to discover those decisions and express
them as questions Jev can evaluate. The host supplies the goal, observations,
constraints, and alternatives; Jev supplies a typed answer; the host takes the
next step and checks what actually happened.

The division of work is deliberate:

| Component | Responsibility |
| --- | --- |
| Host model | Understand the task, investigate, generate viable alternatives, formulate questions, interpret answers, and verify outcomes |
| Jev | Resolve delegated decision questions through Choice, Noul, and Score |
| Existing tools | Carry out the host's actions: read sources, browse, write files, or run code within the task's permissions |

The question set evolves with the task. You do not need to enumerate every
possible action at the start. The host turns the current uncertainty into
questions, then revises the remaining questions as evidence arrives.

The questioning method borrows four ideas from grill-me: investigate facts
before asking, expose assumptions, settle prerequisite decisions first, and
reshape follow-up questions around the answers. Here, Jev answers the task's
decision questions while the host continues the work. User preferences and
permissions still belong to the user.

### Why bring Jev into the loop?

Jev offers an interface built around decisions. Choice returns an option and a
distribution over alternatives; Noul returns a yes probability; Score evaluates
an ordered rubric. These outputs give the host explicit values to inspect and
record. They can expose ambiguity that a single selected label would hide.
See the official [question types](https://docs.typesafe.ai/primitives/choice)
and [API contract](https://docs.typesafe.ai/api).

TypeSafe positions Jev around low latency and low cost for decision workloads.
That makes frequent, small decision calls an interesting design to test.
Those are [vendor-reported advantages](https://typesafe.ai/), not measured
end-to-end improvements for this skill. Their value depends on the task and
the cost of preparing each question.

The practical hypothesis is that a specialized decision model can be useful
alongside a capable general model. A conventional model with structured output
can also fill this role. Jev must earn its place through measured task quality,
latency, and total cost; a typed interface alone does not establish superiority.

### A small bridge into an existing agent

The skill is the integration layer. Load it into a host that can read local
files and run Python, configure a Jev key, and keep using the host's existing
tools. The bundled script handles authentication, request validation, the API
call, and response validation. The host handles question construction and the
rest of the task, so trying the combination does not require a new agent runtime.

```text
Observe → frame a decision → ask Jev → interpret → act → verify
   ↑                                                      |
   └──────────── update the relevant state ────────────────┘
```

The host retains its own task context and sends a compact, explicit snapshot
with each request. This integration does not transfer KV caches or hidden
internal reasoning between models. Its continuity comes from shared facts,
constraints, previous decisions, and observed outcomes. That makes the handoff
inspectable, but its quality depends on what the host includes or leaves out.

### Multiple rounds with feedback

A round carries a decision through to an observable outcome. Before acting, the
host identifies what the selected step is expected to accomplish or clarify.
After acting, it compares that expectation with the actual result and updates
the next request. A failed action may reveal a bad assumption, missing evidence,
poor options, or an execution problem; the next question should address the
identified issue rather than simply ask Jev to choose again.

For example, suppose the user asks the agent to explain conflicting figures in
two research reports:

| Round | Host prepares | Jev decides | Host acts and feeds back |
| --- | --- | --- | --- |
| 1 | Known figures, uncertainties, and concrete sources to inspect | Which source is most relevant to clarifying the metric definition? | Reads the selected methodology section; records that it omits the definition |
| 2 | The failed lookup, remaining uncertainty, and newly discovered source candidates | Which candidate source best addresses the missing definition? | Reads the glossary and obtains the definition |
| 3 | Both definitions and their supporting excerpts | Do the supplied definitions describe the same metric? | Checks the answer against the excerpts and writes the supported explanation |

This is an illustrative workflow, not a live Jev result. Round 2 exists because
the action changed the evidence and available options. Independent questions
answerable from the same evidence can be sent together, including questions
whose answers are useful only on a particular branch. A later round is needed
when new evidence or an earlier answer is required to construct its questions.

The host maintains the loop under the skill's instructions; the Python helper
performs one API request per invocation. Feedback updates the next request's
state and question design. It does not train Jev, transfer hidden reasoning, or
create a persistent Jev conversation. Stop when the task's completion criteria
are verified, or when further rounds have no useful evidence to obtain within
the task's budget.

This design draws on TypeSafe's guidance on
[question dependencies](https://docs.typesafe.ai/primitives#when-one-question-depends-on-another)
and its [feedback-driven question discovery example](https://docs.typesafe.ai/cookbooks/autoresearch_feature_discovery).
Grill Jev applies those ideas to decisions during the host's current task.

### What we want to learn

The most useful decision points have concrete alternatives or a clear rubric:
which missing information to collect, which approach to try next, or whether
the available evidence supports a claim. The host still has to discover useful
options. If it supplies a misleading summary or omits a good option, Jev may
choose poorly; adding another model does not remove that limitation.

This project is an experiment in that collaboration. Compare it with the same
host working alone, and with a cheaper structured-output model making the same
decisions. Measure completed-task quality, total elapsed time, total model cost,
unnecessary actions, and avoidable requests for user decisions. Include the
host's question-writing and interpretation overhead. On 2026-09-23, a small
synthetic Codex task completed two live Jev rounds with a source lookup and
observed feedback between them. A separate live request verified structured
instructions and criteria for all three question types. These checks establish
connectivity and the handoff mechanism, not general decision quality or an
end-to-end performance advantage.

### Flexible questions, a small transport layer

The helper fixes authentication and the API envelope. The host chooses what to
ask, what evidence to include, and how many relevant questions to batch. A round
can contain one Noul, several Scores, or a mixed set; it need not always ask
"which action next?" or use all three types.

The [pattern guide](references/patterns.md) gives examples of structured option
boundaries, conditional batching, selection with a suitability check, scoring
separate dimensions, narrowing a catalog or hierarchy, selecting source spans,
checking generated work, and revising questions from observed outcomes. These
are building blocks to adapt to the task, rather than a preset task workflow.

TypeSafe's [building guide](https://docs.typesafe.ai/concepts/how-to-build-with-system-one)
emphasizes narrow judgments inside software whose code controls the workflow.
Grill Jev applies those question-design principles inside an existing agent:
the host discovers decision points as the task develops. The API helper does
not determine that workflow, and a skill instruction alone is not a hard runtime
guarantee that the host will consult Jev correctly at every branch.

## Installation

Requires Python 3.9+ and network access to the Jev API. The helper uses only the
Python standard library; no Python packages need to be installed.

Place the complete `grill-jev` directory in `~/.codex/skills/` (or the `skills/`
directory under your custom `CODEX_HOME`). Keep `SKILL.md`, `scripts/`, and
`references/` together. In commands below, replace `<skill-directory>` with the
absolute path to that installed directory.

## Configuration

Environment variables override corresponding private configuration fields:

- `TYPESAFE_API_KEY`: API credential.
- `TYPESAFE_MODEL`: model name; defaults to `jev-latest`.

Alternatively create or edit `~/.config/grill-jev/config.json` locally:

```json
{"api_key": "YOUR_API_KEY", "model": "jev-latest"}
```

Keep this private file outside the distributed skill, preferably with mode `600`. Do not put real keys in chat or command arguments. Desktop apps may not inherit variables exported in a separate terminal; use the config file in that case. `--config <path>` selects another private configuration file.

```text
python3 <skill-directory>/scripts/ask_jev.py --check
```

This prints the model, whether a key is present, and its source. Exit code zero means the settings are present; it does not verify the credential or model with the service.

For comparative experiments, configure a specific model version available to
your account; the default `jev-latest` can change.

## Use

Ask Codex, for example:

> Use $grill-jev to compare these research reports and explain their differences.

Describe your task, constraints, and what completion means. The skill instructs
the host to consult Jev when a substantive decision arises and continue the task
using the result. Routine execution does not require another decision request.

For a manual check, save the request example from [the API reference](references/api.md)
as a JSON file, then run:

```text
python3 <skill-directory>/scripts/ask_jev.py <request-file> --dry-run
python3 <skill-directory>/scripts/ask_jev.py <request-file> --output <response-file>
```

The first command validates the request without network access or a key. The
second calls Jev and can incur charges; choose a new output filename in an
existing directory. It returns a complete JSON response, not streamed text.
A local configuration check does not prove that your key or model is accepted
by the service.

The host includes relevant history explicitly in each request. The helper does
not maintain server-side conversation state or execute returned choices itself.

Streaming is about receiving an answer incrementally; memory is about which
past information the next request can access. One does not imply the other.
The documented TypeSafe API returns complete JSON and exposes no session
continuation field. Its asynchronous SDK can overlap requests but still returns
a complete result. History can be managed by the host in files, a database, or
its own task context; only the material included in a request reaches Jev.

## Official API and OpenRouter

As checked on 2026-09-23, both [TypeSafe](https://docs.typesafe.ai/models) and
[OpenRouter's Jev listing](https://openrouter.ai/typesafe/jev-1.13) show $0.042
per million input tokens and free output tokens. OpenRouter separately lists a
5.5% Standard platform fee on its [pricing page](https://openrouter.ai/pricing);
its [FAQ](https://openrouter.ai/docs/faq) describes fees when purchasing credits.
Equal model rates do not establish equal final payment costs. Check the current
checkout terms for minimum fees, taxes, and payment-method differences.

OpenRouter offers a [TypeSafe-compatible endpoint](https://openrouter.ai/docs/guides/community/typesafe-sdk)
at `https://openrouter.ai/api/v1/systemone`, using an OpenRouter key and billing
the OpenRouter account. This helper currently calls the official TypeSafe
endpoint only; changing its API key alone does not switch providers. A gateway
integration would require an explicit endpoint and credential change. Existing
official credentials and credits remain configured for direct TypeSafe calls.

## Files

- `SKILL.md`: instructions for the model's decision and execution loop.
- `scripts/ask_jev.py`: shared API helper for all three question types.
- `references/api.md`: request/response schemas and examples for the model.
- `references/patterns.md`: task-dependent question patterns with runnable request examples.
- `THIRD-PARTY-NOTICES.md`: upstream attribution and license notice.

## Attribution

The questioning method adapts Matt Pocock's
[grill-me and grilling skills](https://github.com/mattpocock/skills), licensed under
MIT. The adaptation retains evidence gathering, dependency-aware questioning,
and follow-up questions informed by previous answers. It applies those ideas to
Jev-assisted task execution.

See [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md) for the exact source revision
and preserved copyright and license text. Retain that notice when redistributing
the adapted material. It covers the upstream portions and does not assign a
license to unrelated original files.
