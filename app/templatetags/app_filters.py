from django import template

register = template.Library()


@register.filter
def get_recipe_tags(values):
    """
     Фильтр принимает список тегов и возвращает html для этих тегов
    """
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
def get_list(request, key):
    """
    Фильтр возвращает данные по ключу из запроса в виде списка
    """
    return request.GET.getlist(key)


@register.simple_tag()
def clear_url(request, key, value):
    """Удаляет таг и пагинацию из url"""
    url = request.GET.urlencode()
    if 'page' in url:
        url = url[:-7]
    return url.replace(f'{key}={value}', '')
