"""
Fill a fresh database with demo data so the app can be tried straight away:

    python manage.py migrate
    python manage.py seed_demo

Creates demo accounts, marketplace listings across Tanzania and published
education posts with comments. Safe to run again: it replaces its own demo
data and leaves everything else alone.
"""
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from education.models import Comment, Content
from market_place.models import MarketplaceItem

User = get_user_model()

DEFAULT_PASSWORD = "AgroSmart-demo-2026"

# Fake NIDA numbers: valid format (real birth dates, adults) but not real people
USERS = [
    dict(username="demo_buyer", email="buyer@demo.agrosmart.test", first_name="Neema", last_name="Mushi",
         phone_number="0712000001"),
    dict(username="asha_farms", email="asha@demo.agrosmart.test", first_name="Asha", last_name="Juma",
         phone_number="0712000002", id_number="19850615123450000101", nida_verified=True),
    dict(username="baraka_mkulima", email="baraka@demo.agrosmart.test", first_name="Baraka", last_name="Mollel",
         phone_number="0712000003", id_number="19900304123450000102"),
]

# (crop, seller, region, town, price TZS, quantity kg, category, days ago, description)
LISTINGS = [
    ("Maize", "asha_farms", "Dodoma", "Kondoa", 1800, 500, "Cereals", 150, "Dry, clean maize from the short rains harvest."),
    ("Maize", "asha_farms", "Dodoma", "Kondoa", 1950, 400, "Cereals", 110, "Well-dried maize, stored in hermetic bags."),
    ("Maize", "baraka_mkulima", "Arusha", "Karatu", 2100, 300, "Cereals", 70, "Yellow maize, good for animal feed."),
    ("Maize", "asha_farms", "Dodoma", "Chamwino", 2250, 600, "Cereals", 30, "Fresh harvest, moisture below 13%."),
    ("Maize", "baraka_mkulima", "Arusha", "Monduli", 2400, 250, "Cereals", 5, "White maize, sorted and cleaned."),
    ("Rice", "asha_farms", "Morogoro", "Ifakara", 2600, 800, "Cereals", 60, "Kilombero aromatic rice, polished."),
    ("Rice", "baraka_mkulima", "Mbeya", "Kyela", 2800, 350, "Cereals", 12, "Kyela rice, long grain."),
    ("Coffee", "baraka_mkulima", "Kilimanjaro", "Moshi", 9500, 120, "Cash crops", 40, "Arabica parchment coffee from the slopes of Kilimanjaro."),
    ("Bananas", "baraka_mkulima", "Arusha", "Arumeru", 900, 400, "Fruits", 8, "Cooking bananas (ndizi), fresh bunches."),
    ("Cashew Nuts", "asha_farms", "Mtwara", "Newala", 4200, 200, "Cash crops", 25, "Raw cashew nuts, grade one."),
    ("Beans", "baraka_mkulima", "Mbeya", "Mbozi", 3000, 300, "Legumes", 18, "Red kidney beans, cleaned."),
    ("Sunflower", "asha_farms", "Singida", "Manyoni", 1300, 700, "Cash crops", 35, "Sunflower seed for oil pressing."),
    ("Tomatoes", "asha_farms", "Iringa", "Ilula", 1500, 150, "Vegetables", 3, "Fresh tomatoes, harvested this week."),
    ("Cassava", "baraka_mkulima", "Lindi", "Nachingwea", 800, 500, "Roots & tubers", 20, "Fresh cassava roots."),
    ("Tea", "asha_farms", "Njombe", "Mufindi", 2800, 250, "Cash crops", 45, "Green tea leaf, Mufindi estates."),
    ("Irish Potatoes", "baraka_mkulima", "Njombe", "Makambako", 1100, 900, "Roots & tubers", 10, "Clean potatoes, 100 kg bags available."),
    ("Avocados", "asha_farms", "Kilimanjaro", "Rombo", 1600, 200, "Fruits", 6, "Hass avocados for export and local markets."),
    ("Pigeon Peas", "baraka_mkulima", "Manyara", "Babati", 2300, 300, "Legumes", 22, "Dry pigeon peas (mbaazi)."),
]

POSTS = [
    dict(
        title="Simple composting for small farms",
        type=Content.ARTICLE,
        url_or_text=(
            "Compost improves soil structure and feeds your crops for free.\n\n"
            "1. Pick a shaded spot near your field.\n"
            "2. Layer dry material (maize stalks, dry leaves) with green material "
            "(fresh weeds, kitchen peelings) and a little manure.\n"
            "3. Keep the heap moist like a squeezed sponge and turn it every two weeks.\n"
            "4. After about 8 to 10 weeks it is dark, crumbly and ready to use.\n\n"
            "Apply two handfuls per planting hole before the long rains."
        ),
        author="asha_farms",
        days_ago=20,
    ),
    dict(
        title="How to start a small farm",
        type=Content.YOUTUBE,
        url_or_text="https://www.youtube.com/watch?v=heTxEsrPVdQ",
        author="baraka_mkulima",
        days_ago=12,
    ),
]


class Command(BaseCommand):
    help = "Create demo accounts, marketplace listings and education posts."

    def add_arguments(self, parser):
        parser.add_argument("--password", default=DEFAULT_PASSWORD,
                            help=f"Password for the demo accounts (default: {DEFAULT_PASSWORD})")

    @transaction.atomic
    def handle(self, *args, password, **options):
        now = timezone.now()
        users = {}
        for data in USERS:
            data = dict(data)
            user, _ = User.objects.update_or_create(username=data.pop("username"), defaults=data)
            user.set_password(password)
            user.save()
            users[user.username] = user

        demo_users = list(users.values())
        MarketplaceItem.objects.filter(seller__in=demo_users).delete()
        Content.objects.filter(author__in=demo_users).delete()

        for crop, seller, region, town, price, qty, category, days, description in LISTINGS:
            item = MarketplaceItem.objects.create(
                seller=users[seller], name=crop, description=description, price=Decimal(price),
                quantity=qty, category=category, region=region, location=town,
                contact_info=users[seller].phone_number,
            )
            MarketplaceItem.objects.filter(pk=item.pk).update(created_at=now - timedelta(days=days))

        posts = {}
        for data in POSTS:
            data = dict(data)
            days = data.pop("days_ago")
            author = users[data.pop("author")]
            post = Content.objects.create(author=author, status=Content.APPROVED, **data)
            Content.objects.filter(pk=post.pk).update(created_at=now - timedelta(days=days))
            posts[post.title] = post

        compost = posts["Simple composting for small farms"]
        question = Comment.objects.create(
            content=compost, author=users["demo_buyer"],
            text="Can I use chicken manure in the heap? @asha_farms",
        )
        question.mentions.add(users["asha_farms"])
        answer = Comment.objects.create(
            content=compost, author=users["asha_farms"], parent=question,
            text="@demo_buyer yes, it works very well. Use thin layers so the heap does not smell.",
        )
        answer.mentions.add(users["demo_buyer"])
        question.likes.add(users["baraka_mkulima"])
        answer.likes.add(users["demo_buyer"], users["baraka_mkulima"])
        Comment.objects.create(
            content=posts["How to start a small farm"], author=users["asha_farms"],
            text="Great overview. Start small and grow step by step.",
        ).likes.add(users["demo_buyer"])

        self.stdout.write(self.style.SUCCESS(
            f"Demo data ready: {len(users)} accounts, {len(LISTINGS)} listings, {len(POSTS)} posts."
        ))
        self.stdout.write("Log in as demo_buyer, asha_farms (verified seller) or baraka_mkulima "
                          f"with password: {password}")
