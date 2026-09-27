"""Custom template tags for the roadmaps app."""
from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Return dictionary[key], supporting both int and string keys."""
    if dictionary is None:
        return None
    try:
        return dictionary.get(int(key), dictionary.get(key))
    except (ValueError, TypeError):
        return dictionary.get(key)


@register.filter
def index(sequence, position):
    """Return sequence[position], or None if out of range."""
    try:
        return sequence[int(position)]
    except (IndexError, TypeError, ValueError):
        return None


@register.simple_tag
def zip_lists(list_a, list_b):
    """Return a zipped list of (a, b) tuples for use in {% for %} loops."""
    return list(zip(list_a, list_b or []))

@register.filter
def get_skill_gap(gaps_dict, skill_name):
    """Return gap dict for skill_name if found in gaps_dict."""
    if not gaps_dict or not skill_name:
        return None
    return gaps_dict.get(skill_name.lower())
