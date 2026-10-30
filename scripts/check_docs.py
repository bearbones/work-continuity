#!/usr/bin/env python3
"""Check local documentation links and the synthetic replay fixture.

This does not execute an assistant or evaluate the expected natural-language answers.
External research URLs are intentionally not fetched by this local check.
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
errors = []


def require(condition, message):
    if not condition:
        errors.append(message)


def timestamp(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(parsed.tzinfo is not None, f"Naive timestamp: {value}")
    return parsed


docs = list(ROOT.rglob("*.md"))
link_count = 0
for doc in docs:
    body = doc.read_text()
    require(body.count("```") % 2 == 0, f"Unbalanced code fence: {doc}")
    for destination in re.findall(r"!?\[[^\]]*\]\(([^\s)]+)\)", body):
        url = urlsplit(destination)
        if url.scheme or url.netloc or not url.path:
            continue
        link_count += 1
        target = (doc.parent / unquote(url.path)).resolve()
        require(target.is_relative_to(ROOT), f"Link leaves repository: {doc}: {destination}")
        require(target.exists(), f"Broken local link: {doc}: {destination}")

fixture = json.loads((ROOT / "examples/scenario.json").read_text())
require(fixture["synthetic"] is True, "Fixture must be explicitly synthetic")
events = {event["id"]: event for event in fixture["events"]}
require(len(events) == len(fixture["events"]), "Duplicate event IDs")
identities = {(e["source_key"], e["revision"]) for e in events.values()}
require(len(identities) == len(events), "Duplicate source revision identities")
for event in events.values():
    require(timestamp(event["observed_at"]) >= timestamp(event["occurred_at"]),
            f"Observation precedes occurrence: {event['id']}")
    for ref in event.get("evidence_refs", []) + event.get("derived_from", []):
        require(ref in events, f"Unknown event reference: {event['id']} -> {ref}")
    previous = event.get("supersedes_event")
    if previous:
        require(previous in events, f"Unknown superseded event: {previous}")
        if previous in events:
            require(events[previous]["source_key"] == event["source_key"],
                    f"Supersedes different source: {event['id']}")
            require(timestamp(events[previous]["occurred_at"]) < timestamp(event["occurred_at"]),
                    f"Non-increasing source history: {event['id']}")
    if "source_url" in event:
        require(urlsplit(event["source_url"]).hostname == "example.invalid",
                f"Fixture contains a non-synthetic URL: {event['id']}")

cases = fixture["cases"]
require(len({c["id"] for c in cases}) == len(cases), "Duplicate case IDs")
for case in cases:
    timestamp(case["world_at"])
    known_at = timestamp(case["known_at"])
    require(bool(case["expected"]) and bool(case["forbidden"]), f"Missing rubric: {case['id']}")
    for ref in case["evidence_refs"]:
        require(ref in events, f"Unknown case evidence: {case['id']} -> {ref}")
        if ref in events:
            require(timestamp(events[ref]["observed_at"]) <= known_at,
                    f"Future evidence leaks into case: {case['id']} -> {ref}")
    for ref in case.get("excluded_evidence_refs", []):
        require(ref in events, f"Unknown excluded evidence: {case['id']} -> {ref}")
        require(ref not in case["evidence_refs"], f"Included and excluded: {case['id']} -> {ref}")
    duplicate = case.get("setup", {}).get("duplicate_event")
    if duplicate:
        require(duplicate in events, f"Unknown duplicate event: {case['id']}")

svg = ElementTree.parse(ROOT / "assets/architecture.svg")
require(svg.getroot().tag.endswith("svg"), "Architecture asset is not SVG")

if errors:
    print("\n".join(errors), file=sys.stderr)
    sys.exit(1)
print(f"OK: {len(docs)} Markdown files, {link_count} local links, "
      f"{len(events)} synthetic events, {len(cases)} replay rubrics, and SVG XML.")
print("Assistant behavior and external integrations have not been executed.")
