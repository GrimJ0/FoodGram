from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    """Функция добавляет class к полю"""
    return field.as_widget(attrs={"class": css})
