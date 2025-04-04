import requests
import json


PATH = "D:\commerce\Case\services\science_service"


with open(f'{PATH}/config.json','r') as fp:
    config:dict = json.load(fp=fp)


def parse_science_rf():
    site_data = config.get('science_rf')
    url = site_data.get('url', None)
    if url:
        params = site_data.get('params', None)
        headers = site_data.get('headers', None)
        response = requests.request(method='GET',url=url, params=params, headers=headers)
        with open('science_vars.json','w') as fp:
            json.dump(response.json(), fp)




if __name__ == "__main__":
    parse_science_rf()
