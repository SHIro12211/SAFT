from django import template

register = template.Library()


@register.simple_tag
def save_url(value, urlencode=None):
    respon = "?"
    for elem in urlencode:
        if str(elem) == "page":
            respon = respon + str(elem) + "=" + str(value)
        else:
            respon = respon + str(elem) + "=" + str(urlencode[elem]) + "&"
    if "page" not in respon:
        respon = respon + "page=" + str(value) + "&"
    return respon

@register.simple_tag
def list_name_worker(list):
    print(list)
    return list

@register.simple_tag
def sum(a, b):
    c = int(a) + int(b)
    return c


@register.simple_tag
def res(a, b):
    c = int(a) - int(b)
    return c


@register.simple_tag
def href_url(url):
    print(url)
    return "asd"
