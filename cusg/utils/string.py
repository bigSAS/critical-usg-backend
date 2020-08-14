def get_slug(text: str) -> str:
    return '-'.join([word.strip() for word in text.split(' ')])


def replace_in_html(html_string: str, tag: str, new_tag: str):
    return html_string.replace(tag, new_tag)


DOC_RULES = [
    {
        'tag': '<h1>',
        'new_tag': '<div class="text-h1">'
    },
    {
        'tag': '</h1>',
        'new_tag': '</div>'
    },
    {
        'tag': '<h2>',
        'new_tag': '<div class="text-h2">'
    },
    {
        'tag': '</h2>',
        'new_tag': '</div>'
    },
    {
        'tag': '<h3>',
        'new_tag': '<div class="text-h3">'
    },
    {
        'tag': '</h3>',
        'new_tag': '</div>'
    },
    {
        'tag': '<h4>',
        'new_tag': '<div class="text-h4">'
    },
    {
        'tag': '</h4>',
        'new_tag': '</div>'
    },
    {
        'tag': '<h5>',
        'new_tag': '<div class="text-h5">'
    },
    {
        'tag': '</h5>',
        'new_tag': '</div>'
    },
    {
        'tag': '<h6>',
        'new_tag': '<div class="text-h6">'
    },
    {
        'tag': '</h6>',
        'new_tag': '</div>'
    },
    {
        'tag': '<p>',
        'new_tag': '<p class="text-justify">'
    },
    {
        'tag': '</p>',
        'new_tag': '</div>'
    }
]


def quasarify_html(html_string: str) -> str:
    result = html_string
    for rule in DOC_RULES:
        result = replace_in_html(result, rule['tag'], rule['new_tag'])

    return result
