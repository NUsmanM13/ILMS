from django import template
import re

register = template.Library()

@register.filter
def youtube_embed(url):
    """YouTube linkini embed formatiga o'tkazadi"""
    if not url:
        return ""
    regex = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(regex, url)
    if match:
        video_id = match.group(1)
        return f"https://www.youtube.com/embed/{video_id}"
    return url