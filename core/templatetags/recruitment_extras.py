from django import template

register = template.Library()

@register.filter
def get_item(data, key):
    """Get item from a dict by key."""
    if isinstance(data, dict):
        return data.get(key, "")
    return ""


@register.filter
def file_icon(filename: str) -> str:
    """Return Font Awesome class based on file extension."""
    if not filename:
        return "fa-file"
    ext = filename.split(".")[-1].lower()
    if ext in ["xls", "xlsx"]:
        return "fa-file-excel"
    if ext == "pdf":
        return "fa-file-pdf"
    return "fa-file"


@register.filter
def truncate_middle(value: str, arg: int = 30) -> str:
    """Truncate long strings keeping start and end."""
    if not isinstance(value, str):
        return value
    try:
        length = int(arg)
    except (TypeError, ValueError):
        length = 30
    if len(value) <= length:
        return value
    half = max(1, (length - 3) // 2)
    return f"{value[:half]}...{value[-half:]}"
