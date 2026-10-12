from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from prices import analysis
from prices.importer import download_csv, latest_csv_url, load_prices


class Command(BaseCommand):
    help = "Download the latest WFP market prices for Tanzania and load them into the database."

    def add_arguments(self, parser):
        parser.add_argument("--file", help="Load from a local CSV file instead of downloading")

    def handle(self, *args, file=None, **options):
        if file:
            path = Path(file)
            if not path.exists():
                raise CommandError(f"File not found: {path}")
            text, url = path.read_text(encoding="utf-8"), ""
            self.stdout.write(f"Loading {path} ...")
        else:
            try:
                url = latest_csv_url()
                self.stdout.write(f"Downloading {url} ...")
                text = download_csv(url)
            except Exception as exc:
                raise CommandError(f"Could not download prices: {exc}") from exc

        record = load_prices(text, source_url=url)
        analysis.clear_cache()
        self.stdout.write(self.style.SUCCESS(
            f"Saved {record.rows_saved} prices. Latest month: {record.latest_date:%B %Y}."
        ))
