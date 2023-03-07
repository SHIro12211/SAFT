async function call_api(qs) {
    const api_url = document.getElementById('api_url').dataset.api_url;
    prom = await fetch(api_url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie("csrftoken")
        },
        body: JSON.stringify({'query': qs})
    }).catch(error => console.log(error));
    if (prom) {
        if (prom.ok) {
            prom = (await prom.json())
            return prom.data
        } else
            console.log(prom.status)
    }
    return prom
}

async function search_ls_api(id_person) {
    qs = '{personById(id:' + id_person + '){id, name, isActive, area{name}}}'
    let text_list_name = localStorage.getItem('saft_list_person_id_name')
    text_list_name = JSON.parse(text_list_name)
    if (text_list_name) {//si hay datos en el Local Storage
        worker = text_list_name.find(element => element.id == id_person)
        console.log(worker)
        if (!worker) {
            worker = await call_api(qs)
            if (worker) {
                worker = {
                    id: worker.personById.id,
                    name: worker.personById.name,
                    area: worker.personById.area.name,
                    active: worker.personById.isActive,
                    no_storage: true
                }
            }
        }
        return worker
    } else
        return null
}


async function fill_localstorage(user) {
    text_list_name = localStorage.getItem("saft_list_person_id_name")
    if (!text_list_name) {
        url_class = 'http://172.16.100.182:8000/inventory/filllocalstorage/'
        prom = await fetch(url_class, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie("csrftoken")
            },
            body: JSON.stringify({'user': user})
        }).catch(error => console.log(error));
        if (prom) {
            if (prom.ok) {
                prom = (await prom.json())
                localStorage.setItem("saft_list_person_id_name", JSON.stringify(prom.data))

            } else
                console.log('ERROR: status code del fetch: ' + prom.status)
        }

    } else {
        console.log('La local storage del navegador tiene datos del sistema')
    }
}
