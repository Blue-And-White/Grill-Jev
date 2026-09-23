# Grill Jev

Give your coding agent a Jev decision partner.

Grill Jev is a self-contained skill for Codex, OpenCode, and Claude Code. Your
existing model investigates the task, develops options, and carries out the work.
At decision points, it turns its uncertainty into structured questions for Jev,
uses the answers, and brings the observed results into the next round.

It works with general tasks: research, document analysis, choosing an approach,
or checking generated work. No separate grill-me installation is required.

## Philosophy

An agent often reaches a point where it has gathered evidence and identified
several plausible approaches, but pauses to ask: "Which direction should I take?"
When the user has already delegated that choice, Jev can be the decision partner
the agent consults to keep moving.

The host model still does the thinking that makes a decision meaningful. It
understands the goal, explores the situation, develops hypotheses, finds viable
alternatives, and explains the result. Jev evaluates the bounded questions the
host prepares. The host then executes the selected work and checks what happened.

The questioning method adapts the spirit of grill-me: investigate before asking,
surface assumptions, settle prerequisites, and use each answer to sharpen the
next question. Here, those questions go to Jev as part of completing a task.
You do not need to enumerate the entire decision tree in advance; the host
discovers new decisions as evidence arrives.

This division of work makes Jev easy to try inside an agent you already use.
Its typed decisions and probability distributions give the host something
concrete to act on and reassess. The useful question is whether this cooperation
helps complete your task; adding a decision model does not automatically make
the agent better.

User intent remains the foundation. Jev chooses within the goals, constraints,
and discretion you supply. Missing personal preferences and new permissions
still belong to you.

## How it works

```text
Host observes → frames questions → Jev answers → host acts and verifies
       ↑                                               |
       └──────── observed results inform the next round ┘
```

| Question type | What it does | Example |
| --- | --- | --- |
| Choice | Selects among supplied alternatives | Which source should we inspect to resolve this uncertainty? |
| Noul | Evaluates a yes/no proposition | Does this source support the proposed explanation? |
| Score | Rates one dimension against an ordered rubric | How directly does this evidence address the claim? |

The host can ask one question or batch several independent questions. It chooses
the format for the task rather than forcing every decision into the same template.
The bundled Python helper handles authentication, validation, and the API call.
Your agent's existing tools do the actual work.

For example, while comparing two reports, the host might ask Jev which source to
inspect, read the selected methodology, then use the newly discovered definitions
to ask whether the reported figures are comparable. Each round carries forward
relevant evidence and actual outcomes. The host maintains this continuity;
the helper does not automatically remember previous calls.

## Installation

You need Git, Python 3.9+, a TypeSafe API key, and an agent that can read local
files, run Python, and reach the API. No additional Python packages are required.

### Ask your agent to install it

Paste this into Codex, OpenCode, or Claude Code:

```text
Install Grill Jev from https://github.com/Blue-And-White/Grill-Jev into this tool's user-level skills directory as grill-jev; the skill is at the repository root, so keep SKILL.md, scripts, and references together, preserve any existing installation and private configuration, then help me configure my TypeSafe key locally and run the helper's --check without printing the key.
```

In Codex, you can also ask the built-in installer:

```text
$skill-installer install the skill at the root of https://github.com/Blue-And-White/Grill-Jev as grill-jev
```

### Manual installation

The commands below are for macOS, Linux, or WSL and create a user-level
installation. Choose the section for your tool. If the destination already
exists, update the existing installation instead of cloning over it.

**Codex**

```bash
mkdir -p ~/.agents/skills
git clone https://github.com/Blue-And-White/Grill-Jev.git ~/.agents/skills/grill-jev
```

Codex discovers user skills in `~/.agents/skills/`. If an installer has already
placed this skill in another directory recognized by your Codex installation,
keep using that copy to avoid duplicate entries. See the
[Codex skill documentation](https://learn.chatgpt.com/docs/build-skills).

**OpenCode**

```bash
mkdir -p ~/.config/opencode/skills
git clone https://github.com/Blue-And-White/Grill-Jev.git ~/.config/opencode/skills/grill-jev
```

See the [OpenCode skill documentation](https://opencode.ai/docs/skills/).

**Claude Code**

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/Blue-And-White/Grill-Jev.git ~/.claude/skills/grill-jev
```

See the [Claude Code skill documentation](https://code.claude.com/docs/en/skills).

For an installation limited to one project, use the corresponding directory
inside that project instead:

| Tool | Project skill directory |
| --- | --- |
| Codex | `.agents/skills/grill-jev/` |
| OpenCode | `.opencode/skills/grill-jev/` |
| Claude Code | `.claude/skills/grill-jev/` |

If the skill does not appear, start a new session. For a Git-based installation,
update it with `git -C <skill-directory> pull --ff-only`.

## Configuration

Create a key in the [TypeSafe console](https://console.typesafe.ai/keys). Save it
locally in `~/.config/grill-jev/config.json`, outside the skill directory:

```json
{
  "api_key": "YOUR_TYPESAFE_API_KEY",
  "model": "jev-latest"
}
```

Use file permissions `600` on macOS or Linux. Keep the real key out of chat and
Git. All three tools can use this same private configuration on the same machine.

Alternatively, set `TYPESAFE_API_KEY` and optionally `TYPESAFE_MODEL` in the
environment used to launch your agent. Environment variables override the
corresponding configuration fields. The private file is useful for desktop apps
that do not inherit your terminal's environment.

Replace `<skill-directory>` with the absolute path to your installed skill:

```text
python3 <skill-directory>/scripts/ask_jev.py --check
```

This reports the model and whether a key is configured without displaying it.
It checks local settings; your first live task verifies API access. The helper
uses the official TypeSafe API. Use `--config <path>` to select a different
private configuration file.

## Usage

Give the agent your task, constraints, and definition of completion.

**Codex**

```text
Use $grill-jev to compare these reports and explain why their figures differ. Use the original sources and finish with an evidence-backed explanation.
```

**OpenCode**

```text
Load the grill-jev skill and use it to compare these reports and explain why their figures differ. Use the original sources and finish with an evidence-backed explanation.
```

**Claude Code**

```text
/grill-jev Compare these reports and explain why their figures differ. Use the original sources and finish with an evidence-backed explanation.
```

You can delegate approach choices explicitly: "Choose the investigation order
yourself; consult Jev at meaningful decision points and continue until the
explanation is supported." Add time, call, or scope limits when they matter.

The host frames the questions and calls Jev for you. It continues the work after
each answer, gathers more evidence when needed, and verifies completion against
your goal. Routine steps within an already chosen approach do not need another
Jev call.

### Advanced use

The [question pattern guide](references/patterns.md) covers structured options,
conditional batching, selection plus suitability, multiple scoring dimensions,
shortlists and hierarchies, source-span extraction, verification, and feedback.
These patterns can be combined as the task changes.

For direct helper usage, save a request from the
[API reference](references/api.md), then run:

```text
python3 <skill-directory>/scripts/ask_jev.py <request-file> --dry-run
python3 <skill-directory>/scripts/ask_jev.py <request-file> --output <response-file>
```

The first command checks the request locally. The second sends it to Jev and
saves the result; use a new output filename in an existing directory.

## Attribution

The questioning method adapts Matt Pocock's
[grill-me and grilling skills](https://github.com/mattpocock/skills), licensed
under MIT. No separate installation of those skills is required.

See [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md) for the source revision,
copyright, and license text. Retain that notice when redistributing the adapted
material. It covers the upstream portions and does not assign a license to
unrelated original files.
