"""Extrusion maker support for different manufacturers."""

from extrusion_decoder.makers.base import ExtrusionMaker
from extrusion_decoder.makers.misumi import MisumiMaker

# Registry of available extrusion makers
EXTRUSION_MAKERS: dict[str, type[ExtrusionMaker]] = {
    "misumi": MisumiMaker,
    # TODO: Add support for other extrusion manufacturers
    # "8020": EightTwentyMaker,
    # "openbuilds": OpenBuildsMaker,
}


def get_maker(maker_name: str) -> ExtrusionMaker | None:
    """Get an extrusion maker instance by name.

    Args:
        maker_name: Name of the maker (e.g., "misumi", "8020")

    Returns:
        ExtrusionMaker instance or None if not found
    """
    maker_class = EXTRUSION_MAKERS.get(maker_name.lower())
    if maker_class:
        return maker_class()
    return None


def list_makers() -> list[str]:
    """List all available extrusion makers.

    Returns:
        List of maker names
    """
    return list(EXTRUSION_MAKERS.keys())
