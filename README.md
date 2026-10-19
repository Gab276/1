# Letterboxd reviews for sentiment analysis

Runs the Apify task "Extract Letterboxd Reviews for Sentiment Analysis" with the
[Letterboxd Film Reviews Scraper](https://apify.com/delectable_incubator/letterboxd-film-reviews-scraper-low-cost)
Actor and saves the reviews to `output/reviews.json` and `output/reviews.csv`.

The input is the task's preset: up to 60 reviews each from the *War* and *Drama*
review pages, fetched through Apify's residential proxy.

## Run

```sh
pip install -r requirements.txt
export APIFY_TOKEN=...   # https://console.apify.com/settings/integrations
python run_letterboxd_reviews.py --max-charge-usd 1.00
```

Check the Actor's pricing on its Apify page before the first run. The run is
billed to your Apify account, and the residential proxy adds to the cost.
`--max-charge-usd` stops the run once it has charged that much, but only for
pay-per-event Actors.

Each row has the reviewer, rating, liked flag, date, like and comment counts,
review text, and language (`reviewLang`). Long reviews come back truncated
(`reviewTextTruncated`); the full text is at `fullTextUrl`.
