from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
import time
import csv


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


url = "https://www.titck.gov.tr/kubkt"
driver.get(url)

time.sleep(3)

select = Select(driver.find_element(By.NAME, 'posts_length'))
select.select_by_visible_text('100')  



time.sleep(3)


def get_records():
    rows = driver.find_elements(By.CLASS_NAME, 'table-row') 
    data = []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, 'td')
        if len(cols) > 0:
            data.append({
                'İlaç Adı': cols[0].text.strip(),
                'Etken Madde': cols[1].text.strip(),
                'Üretici': cols[2].text.strip(),
                'Tarih': cols[3].text.strip(),
                'PDF Linki': cols[6].find_element(By.TAG_NAME, 'a').get_attribute('href').strip()
            })
    return data


all_data = []
all_data.extend(get_records())


while True:
    try:
     
        next_button = driver.find_element(By.LINK_TEXT, 'Sonraki')  
        next_button.click()
        time.sleep(3)  
        
       
        all_data.extend(get_records()) 

    except Exception as e:
        print("Sonraki sayfa bulunamadı veya son sayfaya ulaşıldı.")
        break


for entry in all_data:
    print(entry)


driver.quit()


print(f"Toplam kayıt sayısı: {len(all_data)}")

import json


json_file_path = "ilac_linkleri.json"
with open(json_file_path, 'w', encoding='utf-8') as json_file:
    json.dump(all_data, json_file, ensure_ascii=False, indent=4)

print(f"Tüm kayıtlar '{json_file_path}' dosyasına aktarıldı.")