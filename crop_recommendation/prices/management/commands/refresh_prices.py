from datetime import timedelta
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from prices import analysis
from prices.importer import download_csv, latest_csv_url, load_prices
from prices.models import PriceImport


class Command(BaseCommand):
    help = "Download the latest WFP market prices for Tanzania and load them into the database."

    def add_arguments(self, parser):
        parser.add_argument("--file", help="Load from a local CSV file instead of downloading")
        parser.add_argument("--if-older-than", type=int, metavar="DAYS",
                            help="Only refresh if the last refresh was more than DAYS days ago "
                                 "(used at server start-up, where there is no cron)")

    def handle(self, *args, file=None, if_older_than=None, **options):
        if if_older_than is not None:
            last = PriceImport.objects.order_by("-ran_at").first()
            if last and last.ran_at > timezone.now() - timedelta(days=if_older_than):
                self.stdout.write(f"Prices were refreshed {last.ran_at:%Y-%m-%d}; skipping.")
                return
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
