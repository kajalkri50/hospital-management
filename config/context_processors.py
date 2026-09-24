"""Template context: expose public config like Google Maps API key."""

from django.conf import settings


def google_maps_key(request):
    """Expose GOOGLE_MAPS_API_KEY only if it's a valid production key.
    
    This prevents 'InvalidKeyMapError' by not exposing placeholder keys to templates.
    Valid keys: start with 'AIza' and are at least 40 characters long.
    """
    key = getattr(settings, "GOOGLE_MAPS_API_KEY", "")
    # Only expose valid API keys to prevent InvalidKeyMapError
    if key and key.startswith("AIza") and len(key) > 39:
        return {"GOOGLE_MAPS_API_KEY": key}
    # Return empty key for placeholders/invalid keys - templates will skip Maps
    return {"GOOGLE_MAPS_API_KEY": ""}
