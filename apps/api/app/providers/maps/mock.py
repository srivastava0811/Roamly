from app.providers.base import ProviderResult, ProviderProvenance, ProvenanceSource
from app.providers.maps.base import BaseMapsProvider


class MockMapsProvider(BaseMapsProvider):
    async def get_map_tile_style_url(self) -> ProviderResult[str]:
        # Free open-source map style
        open_style = "https://demotiles.maplibre.org/style.json"
        return ProviderResult(
            data=open_style,
            provenance=ProviderProvenance(
                source=ProvenanceSource.LIVE_PROVIDER,
                provider_name="MapLibreDemoTiles",
                confidence_score=1.0,
                is_live=True,
                notes="Free public OpenStreetMap / MapLibre demo tile style.",
            ),
        )
