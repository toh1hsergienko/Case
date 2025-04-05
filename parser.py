# parser.py
import json
from threading import Thread
from queue import Queue
from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
from transformers import BertModel, BertTokenizer
import torch
import numpy as np

# Глобальные настройки
BASE_URL = "https://xn--80aa3ak5a.xn--p1ai"
WORKER_THREADS = 4
BATCH_SIZE = 8

# Инициализация модели один раз при запуске
tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
model = BertModel.from_pretrained('bert-base-multilingual-cased', output_hidden_states=True)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

def worker(url_queue, result_queue):
    with sync_playwright() as p:
        # Запускаем браузер один раз на поток
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-gpu']
        )
        
        while True:
            url = url_queue.get()
            if url is None:
                break
                
            try:
                # Создаем новый контекст для каждого URL
                context = browser.new_context(
                    bypass_csp=True,
                    ignore_https_errors=True
                )
                page = context.new_page()
                
                # Блокировка ресурсов
                page.route('**/*.{png,jpg,jpeg,webp,svg,gif,css,woff,woff2}', lambda route: route.abort())
                
                # Увеличиваем таймаут
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                
                # Парсинг данных
                title = page.query_selector('h1.u-inner-header__title').inner_text().strip()
                content = page.query_selector('div.u-typography').inner_text().strip()
                
                result_queue.put((url, title, content))
                
                # Закрываем контекст после обработки
                context.close()
                
            except Exception as e:
                print(f"ERROR {url}: {str(e)}")
                context.close()  # Всегда закрываем контекст при ошибке
                continue
                
        browser.close()  # Закрываем браузер только после завершения всех задач

def vectorize_batch(texts):
    inputs = tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=256,
        return_tensors="pt"
    ).to(device)
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    hidden_states = outputs.hidden_states[-2]
    return torch.mean(hidden_states, dim=1).cpu().numpy()

def process_all_pages(json_path, output_file, max_count=10):
    # Загрузка URL
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    urls = [
        urljoin(BASE_URL, item['detailUrl']) 
        for item in data['items'][:max_count] 
        if item.get('hasDetail', False)
    ]
    
    # Многопоточная обработка
    url_queue = Queue()
    result_queue = Queue()
    
    # Запуск воркеров
    threads = []
    for _ in range(WORKER_THREADS):
        t = Thread(target=worker, args=(url_queue, result_queue))
        t.start()
        threads.append(t)
    
    # Добавление задач в очередь
    for url in urls:
        url_queue.put(url)
    
    # Сигналы завершения
    for _ in range(WORKER_THREADS):
        url_queue.put(None)
    
    # Сбор результатов
    results = {}
    titles = []
    contents = []
    urls_order = []
    
    for _ in range(len(urls)):
        url, title, content = result_queue.get()
        results[url] = {'title': title, 'desc': content}
        titles.append(title)
        urls_order.append(url)
    
    # Пакетная векторизация
    vectors = vectorize_batch(titles)
    
    # Объединение результатов
    for url, vec in zip(urls_order, vectors):
        results[url]['vectorise'] = vec.tolist()
    
    # Сохранение в файл
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"Обработано {len(results)} страниц")

if __name__ == "__main__":
    process_all_pages('science_vars.json', 'result.json', max_count=10)