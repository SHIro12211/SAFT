function clean_select(varr) {
    list_option = varr.children
    new_list_option = ''
    for (let i = 0; i < list_option.length; i++) {
        if (list_option[i].innerText) {
            list_attr = list_option[i].getAttributeNames().find(element => element.toString() == 'selected')
            if (list_attr)
                new_list_option += '<option selected="" value="' + list_option[i].getAttribute('value') + '">' + list_option[i].innerText + '</option>'
            else
                new_list_option += '<option value="' + list_option[i].getAttribute('value') + '">' + list_option[i].innerText + '</option>'
        }
    }
    varr.innerHTML = new_list_option
}