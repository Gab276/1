"""Run the "Extract Letterboxd Reviews for Sentiment Analysis" Apify task.

Calls the Letterboxd Film Reviews Scraper Actor with the task's preset input
and saves the resulting dataset to JSON and CSV.

Usage:
    export APIFY_TOKEN=...   # from https://console.apify.com/settings/integrations
    python run_letterboxd_reviews.py [--max-charge-usd 1.00] [--out-dir output]
"""

import argparse
import csv
import json
import os
import sys
from decimal import Decimal
from pathlib import Path

from apify_client import ApifyClient

ACTOR_ID = "delectable_incubator/letterboxd-film-reviews-scraper-low-cost"

# Preset input from the task, used as-is.
RUN_INPUT = {
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

# Column order from the Actor's output schema.
FIELDS = [
    "id",
    "reviewerUsername",
    "reviewerDisplayName",
    "reviewerAvatar",
    "filmUrl",
    "watchedType",
    "rating",
    "ratingDisplay",
    "liked",
    "date",
    "dateDisplay",
    "commentsCount",
    "likesCount",
    "reviewText",
    "reviewTextTruncated",
    "reviewLang",
    "fullTextUrl",
    "sourceUrl",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--max-charge-usd",
        type=Decimal,
        help="Stop the run once it has charged this much (pay-per-event Actors only).",
    )
    parser.add_argument("--out-dir", type=Path, default=Path("output"))
    args = parser.parse_args()

    token = os.environ.get("APIFY_TOKEN")
    if not token:
        print("Set APIFY_TOKEN to your Apify API token.", file=sys.stderr)
        return 1

    client = ApifyClient(token)
    run = client.actor(ACTOR_ID).call(
        run_input=RUN_INPUT,
        max_total_charge_usd=args.max_charge_usd,
    )
    if run is None:
        print("The Actor run did not start.", file=sys.stderr)
        return 1

    print(f"Run {run.id} finished with status {run.status}")
    if run.usage_total_usd is not None:
        print(f"Platform usage: ${run.usage_total_usd:.4f}")

    items = list(client.dataset(run.default_dataset_id).iterate_items())
    print(f"Fetched {len(items)} reviews")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.out_dir / "reviews.json"
    csv_path = args.out_dir / "reviews.csv"

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(items)

    print(f"Wrote {json_path} and {csv_path}")
    return 0 if run.status == "SUCCEEDED" else 1


if __name__ == "__main__":
    sys.exit(main())
