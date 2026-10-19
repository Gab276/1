"""Offline tests for run_letterboxd_reviews.py, using a fake Apify client."""

import csv
import json
import sys
from decimal import Decimal
from types import SimpleNamespace

import pytest

import run_letterboxd_reviews as runner

# The task's preset input, copied here so an accidental edit to the script fails CI.
TASK_INPUT = {
    "urls": [
        "https://letterboxd.com/film/war/reviews/by/activity/",
        "https://letterboxd.com/film/drama/reviews/by/activity/",
    ],
    "max_items_per_url": 60,
    "proxy": {
        "useApifyProxy": True,
        "apifyProxyGroups": ["RESIDENTIAL"],
    },
}

ITEMS = [
    {
        "id": "r1",
        "reviewerUsername": "alice",
        "rating": 4.5,
        "liked": True,
        "reviewText": 'Loved it,\nsaid "wow".',
        "reviewTextTruncated": False,
        "reviewLang": "en",
        "notInSchema": "dropped from CSV",
    },
    {"id": "r2", "reviewerUsername": "bob", "rating": 1.0, "reviewLang": "fr"},
]


@pytest.fixture
def apify(monkeypatch):
    state = SimpleNamespace(status="SUCCEEDED", items=ITEMS, started=True, calls=[])

    class FakeClient:
        def __init__(self, token):
            state.token = token

        def actor(self, actor_id):
            state.actor_id = actor_id

            def call(**kwargs):
                state.calls.append(kwargs)
                if not state.started:
                    return None
                return SimpleNamespace(
                    id="RUN1",
                    status=state.status,
                    usage_total_usd=0.0123,
                    default_dataset_id="DS1",
                )

            return SimpleNamespace(call=call)

        def dataset(self, dataset_id):
            state.dataset_id = dataset_id
            return SimpleNamespace(iterate_items=lambda: iter(state.items))

    monkeypatch.setattr(runner, "ApifyClient", FakeClient)
    monkeypatch.setenv("APIFY_TOKEN", "test-token")
    return state


def run(monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["run_letterboxd_reviews.py", *args])
    return runner.main()


def test_calls_actor_with_task_input(apify, monkeypatch, tmp_path):
    assert run(monkeypatch, "--out-dir", str(tmp_path)) == 0
    assert apify.token == "test-token"
    assert apify.actor_id == "delectable_incubator/letterboxd-film-reviews-scraper-low-cost"
    assert apify.calls == [{"run_input": TASK_INPUT, "max_total_charge_usd": None}]
    assert apify.dataset_id == "DS1"


def test_passes_charge_cap(apify, monkeypatch, tmp_path):
    run(monkeypatch, "--out-dir", str(tmp_path), "--max-charge-usd", "1.50")
    assert apify.calls[0]["max_total_charge_usd"] == Decimal("1.50")


def test_writes_json_and_csv(apify, monkeypatch, tmp_path):
    run(monkeypatch, "--out-dir", str(tmp_path))

    assert json.loads((tmp_path / "reviews.json").read_text(encoding="utf-8")) == ITEMS

    with (tmp_path / "reviews.csv").open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert reader.fieldnames == runner.FIELDS
    assert [row["id"] for row in rows] == ["r1", "r2"]
    assert rows[0]["reviewText"] == 'Loved it,\nsaid "wow".'
    assert rows[1]["reviewLang"] == "fr"
    assert rows[1]["reviewText"] == ""


def test_missing_token_fails_without_calling_apify(apify, monkeypatch, tmp_path):
    monkeypatch.delenv("APIFY_TOKEN")
    assert run(monkeypatch, "--out-dir", str(tmp_path / "out")) == 1
    assert apify.calls == []
    assert not (tmp_path / "out").exists()


def test_run_that_did_not_start_fails(apify, monkeypatch, tmp_path):
    apify.started = False
    assert run(monkeypatch, "--out-dir", str(tmp_path / "out")) == 1
    assert not (tmp_path / "out").exists()


def test_failed_run_still_saves_partial_results_but_exits_nonzero(apify, monkeypatch, tmp_path):
    apify.status = "FAILED"
    assert run(monkeypatch, "--out-dir", str(tmp_path)) == 1
    assert (tmp_path / "reviews.csv").exists()
