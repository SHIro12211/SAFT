LIST_STR = ['fixedasset', 'worker']

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function redirect_operation(link, operation, id_model) {
    let new_url
    list_temp = ['fixedasset', 'home', 'worker']
    for (let i = 0; i < list_temp.length; i++) {
        if (link.includes('fixedasset') || link.includes('home')) {
            new_url = link.replace('fixedasset', operation + 'fixedasset')
            hidden = document.getElementById('input_hiden_list_id_af')
            form_hidden = document.getElementById('form_hiden_delete_masive_af')
            if (link.includes('home'))
                new_url = link.replace('home', operation + 'fixedasset')
        }
        if (link.includes('worker')) {
            new_url = link.replace('worker', operation + 'worker')
            hidden = document.getElementById('input_hiden_list_id_w')
            form_hidden = document.getElementById('form_hiden_delete_masive_w')
        }
    }
    hidden.setAttribute('value', id_model)
    form_hidden.submit()

}
;

function change_state_toggle() {
    toggle_checkbox = document.getElementById('check-toggle')
    list_check = document.getElementsByClassName('col_check')
    let count = 0
    for (let i = 0; i < list_check.length; i++)
        if (list_check[i].checked) {
            count++
            if (toggle_checkbox.checked)
                toggle_checkbox.checked = false
        }
    if (count == list_check.length)
        toggle_checkbox.checked = true
}

function redirect_delete_masive(link) {
    let list_check = document.getElementsByClassName('col_check')
    list_temp = []
    //para crear los valores de los check marcados
    for (let i = 0; i < list_check.length; i++)
        if (list_check[i].checked)
            list_temp.push(list_check[i].getAttribute('value'))
    if (list_temp.length != 0) {
        let hidden
        let form_hidden
        if (link.includes('worker')) {
            hidden = document.getElementById('input_hiden_list_id_w')
            form_hidden = document.getElementById('form_hiden_delete_masive_w')
        } else {
            hidden = document.getElementById('input_hiden_list_id_af')
            form_hidden = document.getElementById('form_hiden_delete_masive_af')
        }
        hidden.setAttribute('value', list_temp)
        form_hidden.submit()
    }
}
;

