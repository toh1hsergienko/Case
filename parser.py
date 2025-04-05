import json
from playwright.sync_api import sync_playwright
from urllib.parse import urljoin

BASE_URL = "https://xn--80aa3ak5a.xn--p1ai"

def parse_page(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto(url, wait_until="domcontentloaded")
            
            # Получаем тему из заголовка h1
            theme_element = page.wait_for_selector(
                'h1.u-inner-header__title.u-inner-header__title--maxw-1024',
                timeout=10000
            )
            theme = theme_element.inner_text().strip()

            # Получаем основной текст
            content_element = page.wait_for_selector(
                'div.u-typography.science-detail-page__typography',
                timeout=10000
            )
            content = content_element.inner_text().strip()
            content = ' '.join(content.split())

            return {
                "title": theme,
                "desc": content
            }
            
        except Exception as e:
            print(f"Ошибка при обработке {url}: {str(e)}")
            return {
                "title": "",
                "desc": ""
            }
            
        finally:
            browser.close()

def load_endpoints(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    endpoints = []
    for item in data['items']:
        if item.get('hasDetail', False):
            full_url = urljoin(BASE_URL, item['detailUrl'])
            endpoints.append(full_url)
    
    return endpoints

def process_all_pages(json_path, output_file, max_count=10):
    endpoints = load_endpoints(json_path)[:max_count]
    result = {}
    
    for i, url in enumerate(endpoints, 1):
        print(f"Обработка {i}/{len(endpoints)}: {url}")
        page_data = parse_page(url)
        result[url] = page_data
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Успешно обработано {len(endpoints)} страниц. Результат сохранен в {output_file}")

if __name__ == "__main__":
    process_all_pages('science_vars.json', 'result.json', 10)