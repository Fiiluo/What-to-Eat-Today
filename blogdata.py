import requests
from bs4 import BeautifulSoup
import re
import random
import json
import os
import time
from urllib.parse import urlparse


def crawl_random_title(url, cache_expiration_time=24*60*60):
    # 從 URL 中擷取最後6位數字作為檔案名稱的一部分
    match = re.search(r'pack/(\d{6})', url)
    if match:
        url_id = match.group(1)
    else:
        raise ValueError("URL 中未找到有效的數字 ID")

    # 生成以 URL ID 為名的快取檔案名稱
    cache_file = f"{url_id}_title_data.json"

    # 檢查是否有快取檔案
    if os.path.exists(cache_file):
        # 取得快取檔案的最後修改時間
        file_mod_time = os.path.getmtime(cache_file)
        current_time = time.time()

    # 如果有沒過期的快取檔案，直接讀取
        if current_time - file_mod_time < cache_expiration_time:
            with open(cache_file, 'r', encoding='utf-8') as f:
                title_data = json.load(f)
                # 隨機挑選一筆資料
                random_pick = random.choice(title_data)
                return random_pick
        else:
            # 如果快取檔案過期，刪除舊快取
            os.remove(cache_file)
            print(f'快取檔案過期，重新爬取資料:{url}')
    # 取得chrome版本
    chrome_version = os.listdir(r'C:\Program Files\Google\Chrome\Application')[
        0].split('.')[0]
    # 設定headers
    headers = {
        'User-Agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version}.0.0.0 Safari/537.36'}

    # 取得網頁資料
    # HTTP 狀態碼 檢查
    res = requests.get(url, headers=headers)
    # 編碼設定為utf-8
    res.encoding = 'utf-8'
    # 預存網頁資料
    all_data = BeautifulSoup(res.text, 'html.parser')

    # 標題篩選條件 H3
    pattren_title_h3 = r'\d+\.\s*(.*?)｜(.*?)(?:【Google\s*(\d+(?:\.\d+)?)[星星]】|\s*$)'
    # 標題篩選條件 H2
    pattren_title_h2 = r"(\d+)\.\s+([\w（)（）\u4e00-\u9fa5]+)\s+(.*)"
    # 標題資料處理
    title_data = []
    # 找尋H3標籤的資料
    for i in all_data.select('h3'):
        # 找尋H3標籤條件的資料
        title = re.search(pattren_title_h3, i.text)
        # 如果有符合條件的資料
        if title:
            # 清除\xa0
            title_clear = title.group().replace('\xa0', ' ')
            # 放入title_data
            title_data.append(title_clear)
    # 如果沒有符合條件的資料
    if title_data == []:
        # 再找尋H2標籤條件的資料
        for i in all_data.select('h2'):
            title = re.search(pattren_title_h2, i.text)
            # 如果有符合條件的資料
            if title:
                # 清除\xa0
                title_clear = title.group().replace('\xa0', ' ')
                # 放入title_data
                title_data.append(title_clear)
    # 儲存檔案
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(title_data, f, ensure_ascii=False, indent=4)

    print(f'執行爬蟲並儲存資料，快取檔案:{cache_file}')

    # 隨機挑選一筆資料

    random_pick = random.choice(title_data)

    return random_pick
