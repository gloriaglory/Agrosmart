from collections import defaultdict

from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import MarketplaceItem
from .permissions import IsOwnerOrReadOnly, IsSellerOrReadOnly
from .serializers import MarketplaceItemSerializer


class MarketplaceItemViewSet(viewsets.ModelViewSet):
    """
    Marketplace listings.

    Anyone can browse. Logged-in sellers can post; only the owner can edit or delete.
    Query params: ?region=<name>, ?search=<text>
    """
    serializer_class = MarketplaceItemSerializer
    permission_classes = [IsSellerOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        qs = MarketplaceItem.objects.select_related('seller')
        region = self.request.query_params.get('region')
        if region:
            qs = qs.filter(region__iexact=region)
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(description__icontains=search)
                           | Q(location__icontains=search))
        return qs

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def mine(self, request):
        """Listings posted by the logged-in user."""
        qs = MarketplaceItem.objects.filter(seller=request.user)
        return Response(self.get_serializer(qs, many=True).data)

    @action(detail=False, permission_classes=[AllowAny])
    def regions(self, request):
        """
        Crops currently listed in each region, for the map:
        [{region, listings, crops: [{name, listings, avg_price}]}]
        """
        grouped = defaultdict(lambda: defaultdict(list))
        for item in MarketplaceItem.objects.exclude(region='').only('region', 'name', 'price'):
            grouped[item.region][item.name.strip().title()].append(float(item.price))

        data = []
        for region, crops in sorted(grouped.items()):
            crop_rows = sorted(
                (
                    {'name': name, 'listings': len(prices),
                     'avg_price': round(sum(prices) / len(prices))}
                    for name, prices in crops.items()
                ),
                key=lambda c: c['name'],
            )
            data.append({
                'region': region,
                'listings': sum(c['listings'] for c in crop_rows),
                'crops': crop_rows,
            })
        return Response(data)
