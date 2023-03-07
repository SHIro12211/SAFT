import requests
from decouple import config

AREA = "Dirección de Infocomunicaciones"


class GraphqlService:
    api_url = config('API_URL')

    def get_api_url(self):
        return self.api_url

    def get_person_by_id(self, id_person):
        query = '{personById(id:' + str(id_person) + '){id, name, position, isActive, area{id,name}}}'
        resp = requests.post(
            self.api_url,
            {"query": query}
        )
        if resp.status_code == 200:
            resp = resp.json()
            return resp['data']['personById']
        if resp.status_code == 400:
            return "ERROR del cliente: Revise los datos solicitados"
        if resp.status_code == 500:
            return "ERROR interno del servidor: Contatcte con el administrador del software"

    def get_person_name_by_id(self, id_person):
        query = '{personById(id:' + str(id_person) + '){name}}'
        resp = requests.post(
            self.api_url,
            {"query": query}
        )
        if resp.status_code == 200:
            resp = resp.json()
            return resp['data']['personById']
        if resp.status_code == 400:
            return "ERROR del cliente: Revise los datos solicitados"
        if resp.status_code == 500:
            return "ERROR interno del servidor: Contatcte con el administrador del software"

    def get_person_by_name(self, name_person):  # arreglar
        query = '{personByName(name:"' + name_person + '"){id,area{id,name}}}'
        resp = requests.post(
            self.api_url,
            {"query": query}
        )

        if resp.status_code == 200:
            resp = resp.json()
            return resp['data']['personByName']
        if resp.status_code == 400:
            return "ERROR del cliente: Revise los datos solicitados"
        if resp.status_code == 500:
            return "ERROR interno del servidor: Contatcte con el administrador del software"

    def get_all_person_for_area(self, area):
        query = '{areaByName(name: "' + area + '"){personSet{id, name, isActive}}}'
        resp = requests.post(
            self.api_url,
            {"query": query}
        )
        if resp.status_code == 200:
            resp = resp.json()
            return resp['data']['areaByName'][0]['personSet']
        if resp.status_code == 400:
            return "ERROR del cliente: Revise los datos solicitados"
        if resp.status_code == 500:
            return "ERROR interno del servidor: Contatcte con el administrador del software"

    def person_active_to_choice(self):
        res = []
        list_person_area = self.get_all_person_for_area(AREA)
        if type(list_person_area) == type([]):
            for p in list_person_area:
                if p['isActive'] == True:
                    id_person = int(p['id'])
                    name = p['name']
                    res.append((id_person, name))
            return res
        else:
            return res

    def get_all_person_to_choice(self):
        res = []
        query = '{allPerson{id,name,isActive, area{id,name}}}'
        resp = requests.post(
            self.api_url,
            {"query": query}
        )
        if resp.status_code == 200:
            resp = resp.json()
            for p in resp['data']['allPerson']:
                if p:
                    id_person = int(p['id'])
                    name_person = p['name']
                    res.append((id_person, name_person))

            return sorted(res, key=lambda x: x[1])
        if resp.status_code == 400:
            return "ERROR del cliente: Revise los datos solicitados"
        if resp.status_code == 500:
            return "ERROR interno del servidor: Contatcte con el administrador del software"

    def get_all_person(self):
        res = []
        query = '{allPerson{id,name,isActive, area{id,name}}}'
        resp = requests.post(
            self.api_url,
            {"query": query}
        )
        if resp.status_code == 200:
            resp = resp.json()
            return resp
        if resp.status_code == 400:
            return "ERROR del cliente: Revise los datos solicitados"
        if resp.status_code == 500:
            return "ERROR interno del servidor: Contatcte con el administrador del software"

    def area_to_choice(self):  # devulve una lista de duplas
        res = []
        query = '{allAreas{id, name}}'
        dict_all_area = requests.post(
            self.api_url,
            {"query": query}
        )
        dict_all_area = dict_all_area.json()
        for p in dict_all_area['data']['allAreas']:
            if p:
                id_area = int(p['id'])
                name_area = p['name']
                res.append((id_area, name_area))
        return res

    def get_name_area_by_id(self, id):
        query = '{areaById(id: "' + id + '"){name}}'
        print(query)
        resp = requests.post(
            self.api_url,
            {"query": query}
        )
        if resp.status_code == 200:
            resp = resp.json()
            return resp['data']['areaById']
        if resp.status_code == 400:
            return "ERROR del cliente: Revise los datos solicitados"
        if resp.status_code == 500:
            return "ERROR interno del servidor: Contatcte con el administrador del software"
