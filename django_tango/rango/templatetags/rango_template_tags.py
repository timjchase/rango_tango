from django import template
from rango.models import Category

register = template.Library()


@register.inclusion_tag("rango/cats.html")
def get_category_list(cat=None):
    cats = Category.objects.all()
    return {"cats": cats, "act_cat": cat}
