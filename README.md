# Grill Jev

A self-contained skill that lets a host model consult Jev at decision points while
carrying out your task. The host gathers evidence, formulates questions, executes
the selected next step, and brings observed results into the next decision.

- **Choice:** select among concrete alternatives.
- **Noul:** evaluate a yes/no proposition as a probability.
- **Score:** rate a dimension against an ordered rubric.

No grill-me installation is required.

## Philosophy

An open-ended task becomes a sequence of smaller decisions as evidence arrives.
Grill Jev uses a general-purpose model to discover those decisions and express
them as questions Jev can evaluate. The host supplies the goal, observations,
constraints, and alternatives; Jev supplies a typed answer; the host takes the
next step and checks what actually happened.

The division of work is deliberate:

| Component | Responsibility |
| --- | --- |
| Host model | Understand the task, investigate, generate viable alternatives, formulate questions, interpret answers, and verify outcomes |
| Jev | Evaluate the supplied state through Choice, Noul, and Score questions |
| Existing tools | Carry out the host's actions: read sources, browse, write files, or run code within the task's permissions |

The question set evolves with the task. You do not need to enumerate every
possible action at the start. For example, when two research reports disagree,
the host can first ask which evidence to inspect, then use the new evidence to
ask whether the reports measure the same thing. Each round makes the next
decision more concrete.

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

### What we want to learn

The most useful decision points have concrete alternatives or a clear rubric:
which missing information to collect, which approach to try next, or whether
the available evidence supports a claim. The host still has to discover useful
options. If it supplies a misleading summary or omits a good option, Jev may
choose poorly; adding another model does not remove that limitation.

This project is an experiment in that collaboration. Compare it with the same
host working alone, and with a cheaper structured-output model making the same
decisions. Measure completed-task quality, total elapsed time, total model cost,
and unnecessary actions. Include the host's question-writing and interpretation
overhead. So far, the helper has been validated offline; this project has not
established live Jev decision quality or an end-to-end performance advantage.

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

## Files

- `SKILL.md`: instructions for the model's decision and execution loop.
- `scripts/ask_jev.py`: shared API helper for all three question types.
- `references/api.md`: request/response schemas and examples for the model.
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
