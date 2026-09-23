# Jev API helper

The helper supports Choice, Noul, and Score. It resolves credentials and model settings itself; the caller supplies only the decision request. It never executes an answer as an action.

## Wire format and transport

```text
POST https://api.typesafe.ai/v1/systemone
Authorization: Bearer <API_KEY>
Content-Type: application/json
Accept: application/json
```

The wire request has `model`, `state`, and `questions`. The helper's input file contains `state` and `questions`; it adds `model` from configuration. The response has `model`, `answers` keyed by the same question IDs, and token `usage`.

The outer schema is fixed, but `state`, question IDs, and criteria are task-defined. State accepts text, an object, or an array. Instructions and rubric descriptions accept text, objects, or arrays. Choice descriptions may be null when their names are sufficient.

**Streaming:** the documented endpoint returns one complete JSON result. The public API and inspected official Python SDK expose no answer-streaming/SSE contract or `stream` option. Async SDK calls mean asynchronous request handling, not streamed answers. This helper validates a complete result.

**History:** the documented request has no conversation/session ID or previous-response continuation field. Treat each call as an independent evaluation. Reusing a key, HTTP client, local folder, or question ID does not supply prior context. The host must put relevant prior answers and actual outcomes into each new `state`. This describes the inference interface, not provider data retention or internal caching.

Questions in the same call see the same state and are evaluated independently. Batch independent questions; send dependent follow-ups in later requests with prerequisite results explicitly included.

## Question and answer types

| Type | `criteria` input | Answer fields |
| --- | --- | --- |
| `noul` | Optional object using `true` and/or `false` description keys | `type`, `noul` (probability of yes, 0–1) |
| `choice` | Map of option IDs to descriptions; at most 255 options | `type`, `choice`, `probabilities`, `confidence` |
| `score` | Ordered array of level descriptions | `type`, `score`, `legend`, `probabilities`, `confidence` |

The helper requires nonempty instructions, 1–255 Choice options, and 2–10 Score levels. The official SDK schema permits a one-level Score, but documentation recommends at least two and this helper enforces that useful rubric boundary. Structured descriptions, null Choice descriptions, and optional Noul descriptions are supported.

Noul values near 0.5 express uncertainty; there is no separate confidence field. Score uses zero-based levels: three criteria produce a score from 0 to 2, possibly fractional. It is the probability-weighted mean of the level indexes. For example, probabilities `[0.1, 0.6, 0.3]` imply a score of `1.2`. Confidence summarizes concentration, not independently verified accuracy.

## Mixed request example

All three questions below independently assess the same research state; none consumes another answer in this call.

```json
{
  "state": {
    "goal": "Explain the difference between two audience reports using verifiable sources.",
    "facts": ["Report A labels 1.2 million as monthly active users.", "Report B labels 2.6 million as registered users."],
    "previous_results": ["The source tables were checked; no transcription error was found."],
    "unknowns": ["Whether dates and populations match."],
    "constraints": ["Support the explanation with source evidence."]
  },
  "questions": {
    "next_step": {
      "type": "choice",
      "instructions": "Which next step would best help explain the difference under the stated constraints?",
      "criteria": {
        "definitions": "Read methodology sections to compare definitions, dates, and populations.",
        "revisions": "Look for corrections to establish whether a published figure changed.",
        "reframe": "Ask the host for better investigation options if neither is adequate."
      }
    },
    "same_definition": {
      "type": "noul",
      "instructions": "Does the available evidence establish that both reports use the same definition of a user?"
    },
    "evidence_quality": {
      "type": "score",
      "instructions": "How well does the evidence support a source-grounded explanation of the difference?",
      "criteria": ["No source evidence is available.", "Source labels exist, but key methods remain unverified.", "Source methods establish definitions, dates, and populations."]
    }
  }
}
```

Illustrative response, **not a live model result**:

```json
{
  "model": "illustrative-model-only",
  "answers": {
    "next_step": {
      "type": "choice",
      "choice": "definitions",
      "probabilities": {"definitions": 0.8, "revisions": 0.15, "reframe": 0.05},
      "confidence": 0.5
    },
    "same_definition": {"type": "noul", "noul": 0.1},
    "evidence_quality": {
      "type": "score",
      "score": 1.2,
      "legend": {"0": "No source evidence is available.", "1": "Source labels exist, but key methods remain unverified.", "2": "Source methods establish definitions, dates, and populations."},
      "probabilities": {"0": 0.1, "1": 0.6, "2": 0.3},
      "confidence": 0.2
    }
  },
  "usage": {"input_tokens": 500, "output_tokens": 50}
}
```

## Running and continuing

```text
python3 <skill-directory>/scripts/ask_jev.py <request-file> --dry-run
python3 <skill-directory>/scripts/ask_jev.py <request-file> --output <response-file>
```

`--dry-run` validates and prints the wire request without a key or network request. Live calls can incur charges. `--output` writes a new file and refuses to overwrite existing evidence. Without it, the complete JSON is printed.

The helper validates types, option/level IDs, numeric ranges, distributions, Score legends and weighted values, and token usage. HTTP failures, timeouts, malformed responses, and missing answers exit nonzero without a fabricated decision. No automatic retries occur; billing may be unknown after a timeout. The helper never modifies private configuration.

For the next round, read the saved answer, perform the selected work, and prepare a new state containing relevant evidence and outcomes. The helper does not automatically replay old files. Local records are not server-side conversation handles.

Preserve the actual model name in each response for comparative experiments.

## Sources checked

Checked 2026-09-23: [HTTP API](https://docs.typesafe.ai/api), [State](https://docs.typesafe.ai/concepts/state), [Choice](https://docs.typesafe.ai/primitives/choice), [Noul](https://docs.typesafe.ai/primitives/noul), [Score](https://docs.typesafe.ai/primitives/score), [Confidence](https://docs.typesafe.ai/confidence).

Official Python SDK inspected at commit `0ffd094c72ed9445223060b24ffd7a56aa781fb4`: [request builder](https://github.com/typesafe-ai/typesafe-sdk-python/blob/0ffd094c72ed9445223060b24ffd7a56aa781fb4/src/typesafe_sdk/_core/endpoints.py), [synchronous client](https://github.com/typesafe-ai/typesafe-sdk-python/blob/0ffd094c72ed9445223060b24ffd7a56aa781fb4/src/typesafe_sdk/_core/client/sync/client.py), [asynchronous client](https://github.com/typesafe-ai/typesafe-sdk-python/blob/0ffd094c72ed9445223060b24ffd7a56aa781fb4/src/typesafe_sdk/_core/client/aio/client.py).
