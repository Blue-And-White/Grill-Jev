#!/usr/bin/env python3
"""Ask Jev typed questions. This helper never executes a selected action."""

import argparse
import json
import math
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request

ENDPOINT = "https://api.typesafe.ai/v1/systemone"
DEFAULT_CONFIG = Path.home() / ".config/grill-jev/config.json"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def description(value):
    return nonempty(value) or isinstance(value, (dict, list)) and bool(value)


def load_json(path):
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def settings(path):
    config = load_json(path) if Path(path).exists() else {}
    require(isinstance(config, dict), "Config must be a JSON object.")
    key = os.environ.get("TYPESAFE_API_KEY") or config.get("api_key", "")
    model = os.environ.get("TYPESAFE_MODEL") or config.get("model", "jev-latest")
    require(isinstance(key, str), "api_key must be a string.")
    require(nonempty(model), "model must be a nonempty string.")
    require(all(33 <= ord(c) <= 126 for c in key.strip()), "API key must contain printable ASCII without whitespace.")
    source = "environment" if os.environ.get("TYPESAFE_API_KEY") else "config_file"
    return key.strip(), model.strip(), source


def prepare(data, model):
    require(isinstance(data, dict), "Request must be a JSON object.")
    require(set(data) == {"state", "questions"}, "Request must contain only state and questions; set model in config.")
    require(isinstance(data["state"], (str, dict, list)) and bool(data["state"]), "state must contain context.")
    questions = data["questions"]
    require(isinstance(questions, dict) and bool(questions), "questions must be a nonempty object.")
    require(all(nonempty(name) for name in questions), "Question IDs must be nonempty strings.")
    for question in questions.values():
        require(isinstance(question, dict), "Each question must be an object.")
        require(set(question) <= {"type", "instructions", "criteria"}, "Unsupported question field.")
        require(description(question.get("instructions")), "instructions must be nonempty text, an object, or an array.")
        kind = question.get("type")
        require(isinstance(kind, str) and kind in {"choice", "noul", "score"}, "Supported question types: choice, noul, score.")
        criteria = question.get("criteria")
        if kind == "choice":
            require(isinstance(criteria, dict) and 1 <= len(criteria) <= 255, "Choice needs 1–255 options.")
        elif kind == "score":
            require(isinstance(criteria, list) and 2 <= len(criteria) <= 10, "Score needs 2–10 ordered levels.")
            require(all(description(level) for level in criteria), "Score levels need text, object, or array descriptions.")
            continue
        elif criteria is not None:
            require(isinstance(criteria, dict) and set(criteria) <= {"true", "false"}, "Noul criteria may only use true and false.")
        if criteria is not None:
            require(all(nonempty(k) and (v is None or description(v)) for k, v in criteria.items()), "Invalid criteria IDs or descriptions.")
    return {"model": model, **data}


def probability(value):
    return type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 1


def validate_response(result, questions):
    require(isinstance(result, dict) and nonempty(result.get("model")), "Response is missing its model identifier.")
    answers = result.get("answers")
    require(isinstance(answers, dict) and set(answers) == set(questions), "Response question IDs do not match request.")
    for name, question in questions.items():
        answer = answers[name]
        require(isinstance(answer, dict) and answer.get("type") == question["type"], "Invalid answer type.")
        if question["type"] == "noul":
            require(probability(answer.get("noul")), "Invalid Noul probability.")
            continue
        is_score = question["type"] == "score"
        options = {str(i): level for i, level in enumerate(question["criteria"])} if is_score else question["criteria"]
        probabilities = answer.get("probabilities")
        require(isinstance(probabilities, dict) and set(probabilities) == set(options), "Invalid probability keys.")
        require(all(probability(p) for p in probabilities.values()), "Invalid probabilities.")
        require(abs(sum(probabilities.values()) - 1) <= 0.02, "Probabilities do not sum to one.")
        require(probability(answer.get("confidence")), "Invalid confidence.")
        if is_score:
            score = answer.get("score")
            require(type(score) in (int, float) and math.isfinite(score) and 0 <= score <= len(options) - 1, "Invalid Score value.")
            require(answer.get("legend") == options, "Score legend does not match requested levels.")
            expected = sum(int(level) * p for level, p in probabilities.items())
            require(abs(score - expected) <= 0.02 * (len(options) - 1), "Score is inconsistent with probabilities.")
        else:
            choice = answer.get("choice")
            require(isinstance(choice, str) and choice in options, "Choice is outside the provided options.")
            require(probabilities[choice] >= max(probabilities.values()) - 1e-6, "Choice is inconsistent with probabilities.")
    usage = result.get("usage")
    require(isinstance(usage, dict) and all(type(usage.get(k)) is int and usage[k] >= 0 for k in ("input_tokens", "output_tokens")), "Invalid or missing token usage.")
    return result


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("API redirect refused; verify the official endpoint.")


def ask(body, key):
    request = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(body, ensure_ascii=False, allow_nan=False).encode("utf-8"),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    opener = urllib.request.build_opener(NoRedirect())
    with opener.open(request, timeout=30) as response:
        result = json.load(response)
    return validate_response(result, body["questions"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", nargs="?", type=Path)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    key, model, source = settings(args.config)
    if args.check:
        print(json.dumps({"model": model, "key_configured": bool(key), "key_source": source if key else None}))
        return 0 if key else 2
    require(args.request is not None, "Provide a request JSON file.")
    require(args.output is None or not args.output.exists(), "Output file exists; use a new round filename.")
    require(args.output is None or args.output.parent.is_dir(), "Output directory must already exist.")
    body = prepare(load_json(args.request), model)
    # Reject non-JSON numeric values before any network request.
    json.dumps(body, allow_nan=False)
    if args.dry_run:
        result = body
    else:
        require(bool(key), "Set TYPESAFE_API_KEY or api_key in the private config file.")
        result = ask(body, key)
    rendered = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(rendered)
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except urllib.error.HTTPError as error:
        print(f"Jev HTTP {error.code}; no valid decision returned. No automatic retry.", file=sys.stderr)
    except (urllib.error.URLError, TimeoutError):
        print("Jev connection failed or timed out; no valid decision returned. Billing status may be unknown.", file=sys.stderr)
    except json.JSONDecodeError:
        print("Invalid JSON in request, config, or API response; no valid decision returned.", file=sys.stderr)
    except OSError:
        print("File or network I/O failed; no usable result saved. Check paths and connectivity.", file=sys.stderr)
    except ValueError as error:
        print(str(error), file=sys.stderr)
    sys.exit(1)
