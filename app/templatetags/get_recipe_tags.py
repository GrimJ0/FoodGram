from django import template

register = template.Library()

@register.filter
def get_recipe_tags(values):
    tags = {
        'BREAKFAST': '<li class="card__item"><span class="badge badge_style_orange">Завтрак</span></li>',
        'LUNCH': '<li class="card__item"><span class="badge badge_style_green">Обед</span></li>',
        'DINNER': '<li class="card__item"><span class="badge badge_style_purple">Ужин</span></li>',
    }
    html_tags = ''
    for tag in values:
        html_tags += tags[tag]
    return html_tags
