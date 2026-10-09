import re
from functools import reduce
from operator import or_

from django.contrib.auth import get_user_model
from django.db.models import Q

# @username, using the characters Django allows in usernames (letters, digits, _ . + -).
# Not preceded by a word character, so emails like a@b.com are not treated as tags.
MENTION_RE = re.compile(r"(?<![\w@])@([\w.+-]+)")

MAX_MENTIONS = 20


def mentioned_users(text):
    """Users tagged in the text with @username (case-insensitive; unknown names are ignored)."""
    names = {m.rstrip(".") for m in MENTION_RE.findall(text or "")}
    names = [n for n in names if n][:MAX_MENTIONS]
    if not names:
        return []
    query = reduce(or_, (Q(username__iexact=n) for n in names))
    return list(get_user_model().objects.filter(query))
