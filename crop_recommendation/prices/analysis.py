"""
Price analysis on the WFP market price data.

We deliberately do not give single-number price predictions: in backtests,
"next month's price = this month's price" was more accurate than both a
LightGBM model and a seasonal adjustment. Instead we show:

  - current prices (latest month, per region and for Tanzania),
  - an outlook *range* for the next 3 months, from how prices actually moved
    from this time of year in the past, with its measured hit rate,
  - the typical seasonal pattern (best month to sell, cheapest month).
"""
import hashlib
import math

import numpy as np
import pandas as pd
from django.core.cache import cache
from django.db.models import Count, Max

from .models import MarketPrice, PriceImport

# Raw crops farmers grow and sell. Processed goods (flour, oil), meat and fuel are left out.
CROP_CATEGORIES = {"cereals and tubers", "pulses and nuts", "vegetables and fruits"}
EXCLUDED_WORDS = ("flour",)

OUTLOOK_MONTHS = 3
RANGE = (0.10, 0.90)        # 80% range
OUTLOOK_YEARS = 10          # recent volatility matters more than 2006
SEASON_YEARS = 15
MIN_SAMPLES = 30
STALE_MONTHS = 6
# Crops whose newest price is older than this (vs the newest data overall) are hidden
CURRENT_MONTHS = 12
CACHE_SECONDS = 60 * 60 * 24


# ---------------------------------------------------------------- helpers

def _version():
    latest = PriceImport.objects.order_by("-id").values_list("id", flat=True).first()
    return f"{latest}-{MarketPrice.objects.count()}"


def clear_cache():
    cache.clear()


def _cached(key, compute):
    # Hash so crop names with spaces or brackets make valid cache keys
    key = "prices:" + hashlib.md5(f"{_version()}:{key}".encode()).hexdigest()
    value = cache.get(key)
    if value is None:
        value = compute()
        cache.set(key, value, CACHE_SECONDS)
    return value


def is_crop(commodity, category):
    return category in CROP_CATEGORIES and not any(w in commodity.lower() for w in EXCLUDED_WORDS)


def choose_price_type(commodity):
    """Prefer wholesale prices (what farmers get) when they are reasonably current."""
    latest = dict(
        MarketPrice.objects.filter(commodity=commodity)
        .values_list("price_type")
        .annotate(last=Max("date"))
    )
    if not latest:
        return None
    newest = max(latest.values())
    wholesale = latest.get(MarketPrice.WHOLESALE)
    if wholesale and (newest.year - wholesale.year) * 12 + newest.month - wholesale.month <= 12:
        return MarketPrice.WHOLESALE
    return max(latest, key=latest.get)


def _frame(commodity, price_type):
    rows = MarketPrice.objects.filter(commodity=commodity, price_type=price_type).values_list(
        "date", "region", "market", "price_per_kg"
    )
    df = pd.DataFrame(list(rows), columns=["date", "region", "market", "kg"])
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
    return df


def _market_series(df):
    """Monthly price per kg, one column per market."""
    return df.pivot_table(index="date", columns="market", values="kg", aggfunc="mean").sort_index()


def _area_series(df, region=None):
    """Monthly average price per kg across the markets in a region (or all of Tanzania)."""
    part = df[df.region == region] if region else df
    return part.groupby("date").kg.mean().sort_index()


def _months_between(a, b):
    return (b.year - a.year) * 12 + b.month - a.month


def _nearby_months(month):
    return {(month - 2) % 12 + 1, month, month % 12 + 1}


def _log_changes(markets, horizon):
    """Log price change over `horizon` months for every market and start month."""
    logp = np.log(markets)
    later = logp.shift(-horizon, freq="MS").reindex(logp.index)
    return (later - logp).stack().rename("change").reset_index().rename(columns={"date": "start"})


def _range_for(changes, start_month, since=None, until=None):
    """Quantiles of past changes that started near this calendar month."""
    data = changes
    if since is not None:
        data = data[data.start >= since]
    if until is not None:
        data = data[data.end <= until]
    seasonal = data[data.start.dt.month.isin(_nearby_months(start_month))].change
    if len(seasonal) < MIN_SAMPLES:
        seasonal = data.change
    if len(seasonal) < MIN_SAMPLES:
        return None
    lo, mid, hi = np.quantile(seasonal, [RANGE[0], 0.5, RANGE[1]])
    return lo, mid, hi


def _round(value):
    return None if value is None or (isinstance(value, float) and math.isnan(value)) else round(float(value))


# ---------------------------------------------------------------- outputs

def outlook(df, area):
    """Likely price range for each of the next months, starting from the latest price."""
    if area.empty:
        return []
    markets = _market_series(df)
    base_date, base_price = area.index[-1], area.iloc[-1]
    since = base_date - pd.DateOffset(years=OUTLOOK_YEARS)
    result = []
    for h in range(1, OUTLOOK_MONTHS + 1):
        changes = _log_changes(markets, h)
        quantiles = _range_for(changes, base_date.month, since=since)
        if not quantiles:
            continue
        lo, mid, hi = quantiles
        result.append({
            "month": (base_date + pd.DateOffset(months=h)).strftime("%Y-%m"),
            "low": _round(base_price * math.exp(lo)),
            "typical": _round(base_price * math.exp(mid)),
            "high": _round(base_price * math.exp(hi)),
        })
    return result


def backtest_coverage(df, test_months=12):
    """
    How often real prices fell inside the outlook range, simulating the past
    `test_months` months using only data that would have been available then.
    """
    markets = _market_series(df)
    if markets.empty:
        return None
    last = markets.index[-1]
    hits = total = 0
    for h in range(1, OUTLOOK_MONTHS + 1):
        changes = _log_changes(markets, h)
        changes["end"] = changes.start + pd.DateOffset(months=h)
        starts = [d for d in markets.index if 0 < _months_between(d, last) <= test_months
                  and _months_between(d, last) >= h]
        for start in starts:
            quantiles = _range_for(changes, start.month,
                                   since=start - pd.DateOffset(years=OUTLOOK_YEARS), until=start)
            if not quantiles:
                continue
            lo, _mid, hi = quantiles
            actual = changes[changes.start == start].change
            hits += int(((actual >= lo) & (actual <= hi)).sum())
            total += len(actual)
    return round(100 * hits / total) if total else None


def seasonality(df):
    """Typical price in each calendar month relative to the yearly average (%)."""
    markets = _market_series(df)
    if markets.empty:
        return None
    since = markets.index[-1] - pd.DateOffset(years=SEASON_YEARS)
    changes = _log_changes(markets, 1)
    changes = changes[changes.start >= since]
    changes["month"] = (changes.start + pd.DateOffset(months=1)).dt.month
    counts = changes.groupby("month").change.count()
    if len(counts) < 12 or counts.min() < 10:
        return None
    monthly = changes.groupby("month").change.median().reindex(range(1, 13))
    monthly = monthly - monthly.mean()  # remove inflation so the year closes on itself
    level = monthly.cumsum()
    level = level - level.mean()
    pct = (np.exp(level) - 1) * 100
    best, cheapest = int(pct.idxmax()), int(pct.idxmin())
    return {
        "months": [{"month": m, "index_pct": round(float(pct[m]), 1)} for m in range(1, 13)],
        "best_month": best,
        "cheapest_month": cheapest,
        "spread_pct": round(float(pct.max() - pct.min()), 1),
    }


def regions_latest(df):
    """Latest average price per region, newest first within each region."""
    if df.empty:
        return []
    overall_latest = df.date.max()
    out = []
    for region, part in df.groupby("region"):
        last = part.date.max()
        latest = part[part.date == last]
        out.append({
            "region": region,
            "price": _round(latest.kg.mean()),
            "date": last.strftime("%Y-%m"),
            "markets": int(latest.market.nunique()),
            "stale": _months_between(last, overall_latest) > STALE_MONTHS,
        })
    return sorted(out, key=lambda r: (r["stale"], r["region"]))


def commodity_list():
    """Crops with data, with their latest national price and monthly change."""
    def compute():
        rows = (
            MarketPrice.objects.values("commodity", "category")
            .annotate(n=Count("id"), last=Max("date"))
            .order_by("-n")
        )
        newest = max((row["last"] for row in rows), default=None)
        result = []
        for row in rows:
            if not is_crop(row["commodity"], row["category"]):
                continue
            # Skip crops that WFP stopped tracking; old prices would look current
            if _months_between(row["last"], newest) > CURRENT_MONTHS:
                continue
            price_type = choose_price_type(row["commodity"])
            area = _area_series(_frame(row["commodity"], price_type))
            if area.empty:
                continue
            change = None
            if len(area) > 1 and _months_between(area.index[-2], area.index[-1]) == 1:
                change = round(float(area.iloc[-1] / area.iloc[-2] - 1) * 100, 1)
            result.append({
                "commodity": row["commodity"],
                "category": row["category"],
                "price_type": price_type,
                "price": _round(area.iloc[-1]),
                "date": area.index[-1].strftime("%Y-%m"),
                "change_pct": change,
            })
        return result
    return _cached("list", compute)


def commodity_detail(commodity, region=None, history_years=5):
    """Everything the prices page needs for one crop, optionally narrowed to a region."""
    def compute():
        price_type = choose_price_type(commodity)
        if not price_type:
            return None
        df = _frame(commodity, price_type)
        area = _area_series(df, region)
        if area.empty:
            return {"error": f"No {commodity} prices for {region}."}

        last = area.index[-1]
        previous = area.iloc[-2] if len(area) > 1 and _months_between(area.index[-2], last) == 1 else None
        recent = area[area.index >= last - pd.DateOffset(years=history_years)]
        scope_df = df[df.region == region] if region else df
        return {
            "commodity": commodity,
            "price_type": price_type,
            "region": region or "Tanzania",
            "current": {
                "price": _round(area.iloc[-1]),
                "date": last.strftime("%Y-%m"),
                "change_pct": None if previous is None else round(float(area.iloc[-1] / previous - 1) * 100, 1),
                "markets": int(scope_df[scope_df.date == last].market.nunique()),
                "stale": _months_between(last, df.date.max()) > STALE_MONTHS,
            },
            "history": [{"month": d.strftime("%Y-%m"), "price": _round(p)} for d, p in recent.items()],
            "outlook": outlook(df, area),
            "outlook_hit_rate_pct": _cached(f"coverage:{commodity}", lambda: backtest_coverage(df)),
            "seasonality": _cached(f"season:{commodity}", lambda: seasonality(df)),
            "regions": regions_latest(df),
        }
    return _cached(f"detail:{commodity}:{region}", compute)


def last_updated():
    record = PriceImport.objects.order_by("-ran_at").first()
    return None if not record else {
        "ran_at": record.ran_at.isoformat(),
        "latest_month": record.latest_date.strftime("%Y-%m") if record.latest_date else None,
    }
