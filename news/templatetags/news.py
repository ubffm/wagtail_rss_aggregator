from django.template.defaultfilters import register


@register.filter(name='dict_key')
def dict_key(dict,key):
    return dict.get(key)


@register.filter(name='length')
def length(item):
    return len(item)
