def get_slug(text: str) -> str:
    return '-'.join([word.strip() for word in text.split(' ')])
