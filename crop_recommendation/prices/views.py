from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from . import analysis

SOURCE = {
    "name": "World Food Programme (WFP), data from Tanzania's Ministry of Industry and Trade",
    "url": "https://data.humdata.org/dataset/wfp-food-prices-for-united-republic-of-tanzania",
    "license": "CC BY-IGO",
}


@api_view(["GET"])
@permission_classes([AllowAny])
def commodity_list(request):
    """Crops with current national prices."""
    return Response({
        "commodities": analysis.commodity_list(),
        "updated": analysis.last_updated(),
        "source": SOURCE,
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def commodity_detail(request):
    """Prices, outlook and seasonal pattern for ?commodity=<name>&region=<optional>."""
    commodity = request.query_params.get("commodity", "").strip()
    region = request.query_params.get("region", "").strip() or None
    if not commodity:
        return Response({"error": "Choose a crop."}, status=400)
    data = analysis.commodity_detail(commodity, region)
    if data is None:
        return Response({"error": f"No prices for {commodity}."}, status=404)
    if "error" in data:
        return Response(data, status=404)
    return Response({**data, "source": SOURCE})
