import requests
import json

import datetime

import tqdm
from bs4 import BeautifulSoup

PATH = "D:\commerce\Case\services\science_service"


with open(f'{PATH}/config.json','r') as fp:
    config:dict = json.load(fp=fp)


def parse_science_rf():
    dates = []
    today_date = datetime.datetime.today().date()
    for year in list(range(2023, datetime.date.today().year + 1)):
        for month in list(range(1, 12+1)):
            if year == today_date.year and month > today_date.month:
                break 
            dates.append((year, month))

    site_data = config.get('science_rf')
    url = site_data.get('url', None)
    response_data = []
    if url:
        headers = site_data.get('headers', None)
        for date in tqdm.tqdm(dates):
            params = {'year':date[0], 
                      'month':date[1]}
            
            response = requests.request(method='GET',url=url, params=params, headers=headers)
            if response.json()['status'] == 'success':
                items = response.json()['data']['items']
                response_data+=[item for item in items if '/science' in item['detailUrl']]

    with open('science_vars.json','w', encoding= "UTF-8") as fp:
        json.dump({"items":response_data}, fp, ensure_ascii=False)




if __name__ == "__main__":
    # parse_science_rf()

    

    

    # headers = {
    # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    # "Accept-Encoding": "gzip, deflate, br, zstd",
    # "Accept-Language": "ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
    # "Cache-Control": "no-cache",
    # "Pragma": "no-cache",
    # "Priority": "u=0, i",
    # "Referer": "https://rscf.ru/?ysclid=m92v83un92789936313",
    # "Sec-CH-UA": '"Chromium";v="134", "Not:A-Brand";v="24", "Microsoft Edge";v="134"',
    # "Sec-CH-UA-Mobile": "?0",
    # "Sec-CH-UA-Platform": '"Windows"',
    # "Sec-Fetch-Dest": "document",
    # "Sec-Fetch-Mode": "navigate",
    # "Sec-Fetch-Site": "same-origin",
    # "Sec-Fetch-User ": "?1",
    # "Upgrade-Insecure-Requests": "1",
    # "User -Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0"
    # }
    # cookies = {
    # 'BX_USER_ID': 'eef493c3a86bcfde899430b46a5808df',
    # '_ym_uid': '1743776033263968113',
    # '_ym_d': '1743776033',
    # '_ym_isad': '2'
    # }
    

    url = "https://xn--80aa3ak5a.xn--p1ai/science/146184/"
    headers ={
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
    'cache-control': 'no-cache',
    'cookie': 'PHPSESSID=3p8kfYQIkYH1VgkwJxuQRAfs7GExdtst; _ym_uid=1743773770238327048; _ym_d=1743773770; BX_USER_ID=eef493c3a86bcfde899430b46a5808df; _ym_isad=2; _ym_visorc=w',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Microsoft Edge";v="134"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}
    headers['Access-Control-Allow-Origin'] = '*'
    response = requests.request(method="GET", url=url,headers=headers )


    with open('site.html','w', encoding='UTF-8') as fp:
        fp.write(response.text)
    soup = BeautifulSoup(response.text, 'html.parser')
    science_div = soup.find("div", class_ ='u-typography')
    link = science_div.find('<img-wyz')
    desc = science_div.text.replace("\n","")

    # print(f'''link: {link}
    # Текст: {desc}''')

    # print(f'\n\n\n\n\n\n\n {science_div.contents}')
    for element in science_div.contents:
        print(element['src']) if "img" in str(element) else ''