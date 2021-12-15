from django import template

register = template.Library()


@register.filter
def get_recipe_tags(values):
    tags = {
        'BREAKFAST': '<span class="badge badge_style_orange">Завтрак</span>',
        'LUNCH': '<span class="badge badge_style_green">Обед</span></li>',
        'DINNER': '<span class="badge badge_style_purple">Ужин</span></li>',
    }
    html_tags = []
    for tag in values:
        html_tags.append(tags[tag])
    return html_tags


@register.filter
def get_list(dictionary, key):
    return dictionary.getlist(key)


@register.simple_tag()
def filter_tag_url(method, key, value):
    url = method.urlencode()
    if 'page' in url:
        url = url[:-7]
    return url.replace(f'{key}={value}', '')


@register.simple_tag()
def filter_page_url(method, key, value):
    url2 = method.urlencode().split('&')
    for i in url2:
        n = i.split('=')
        if key == 'page':
            if i in url2 and n[0] == key and n[1] != value:
                url2.remove(i)
    return '&'.join(url2)

