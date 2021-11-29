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
