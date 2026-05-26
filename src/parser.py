import requests
import json
import time
import os

def fetch_steam_data():
    # папка под сырые данные
    os.makedirs("data/raw", exist_ok=True)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    print("апишки нас душат клаудфлеером и ключами. обходим систему.")
    print("берем заранее заготовленный список id популярных и инди игр...")
    
    # захардкодили список appid (тут stardew valley, terraria, hades, hollow knight и т.д.)
    # для пет-проекта и обучения модели нам этого хватит за глаза
    sample_apps = [
        413150, 367520, 105600, 1145360, 250900, 
        646570, 892970, 730, 570, 292030, 400, 
        10, 20, 30, 40, 50, 60, 70, 130, 220, 
        240, 280, 300, 320, 340, 380, 420, 500, 
        550, 620, 72850, 4000, 22320, 252950, 322330
    ]
    
    raw_data = {}
    
    print("идем в официальный стим за деталями (этот метод работает стабильно)...")
    for appid in sample_apps:
        # этот эндпоинт стима отдаст нам все данные без ключей
        details_url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
        
        try:
            app_resp = requests.get(details_url, headers=headers)
            
            if app_resp.status_code != 200:
                print(f"ошибка {app_resp.status_code} на игре {appid}")
                time.sleep(2)
                continue
                
            app_data = app_resp.json()
            
            # проверяем флаг success
            if app_data and str(appid) in app_data and app_data[str(appid)].get('success'):
                raw_data[appid] = app_data[str(appid)].get('data')
                print(f"игра {appid} — собрана успешно")
            else:
                print(f"игра {appid} — нет данных/страница скрыта")
                
            # делаем паузу, уважаем сервера габена
            time.sleep(1.5) 
            
        except Exception as e:
            print(f"упали на {appid}: {e}")
            time.sleep(2)
            
    # сохраняем сырой json
    out_path = "data/raw/steam_raw.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(raw_data, f, ensure_ascii=False, indent=4)
        
    print(f"готово! вытащили {len(raw_data)} игр в {out_path}")

if __name__ == "__main__":
    fetch_steam_data()