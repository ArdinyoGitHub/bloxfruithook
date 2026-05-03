import os
import requests
import re
import json
from playwright.sync_api import sync_playwright

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")
TARGET_URL = "https://fruityblox.com/stock"

SEARCH_KEYWORDS = ["yeti", "tiger", "mammoth", "gravity", "mythical", "kitsune", "leopard", "dragon", "magma", "dough", "t-rex"]

def check_stock():
    # Siteden gelecek verileri tutacağımız kutular
    scraped_data = {"normal": [], "mirage": []}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        page = browser.new_page()
        
        # Tarayıcı siteyi yüklerken arka planda gidip gelen dosyaları dinliyoruz
        def handle_response(response):
            try:
                # Eğer yanıtın içinde bizim meyvelerin verisi varsa
                text = response.text()
                if '"normal":[' in text and '"mirage":[' in text:
                    # Saf veriyi (JSON) regex ile cımbızla çekiyoruz
                    match = re.search(r'{"normal":\[.*?\],"mirage":\[.*?\]}', text)
                    if match:
                        data = json.loads(match.group(0))
                        scraped_data["normal"] = data.get("normal", [])
                        scraped_data["mirage"] = data.get("mirage", [])
            except:
                pass

        page.on("response", handle_response)
        
        print("Siteye giriliyor ve arka plan verileri dinleniyor...")
        page.goto(TARGET_URL)
        page.wait_for_selector("text=Normal", timeout=20000)
        page.wait_for_timeout(3000) # Verilerin tamamen inmesi için kısa bir bekleme
        
        browser.close()

    # Eğer verileri yakalamayı başardıysak:
    if scraped_data["normal"] or scraped_data["mirage"]:
        found_normal = []
        found_mirage = []
        
        # Sadece aradığımız kelimeleri küçük harfe çevirelim ki eşleşme kolay olsun
        keywords = [kw.lower() for kw in SEARCH_KEYWORDS]
        
        # 1. Normal Stok Kontrolü (Hata payı 0, çünkü sadece Normal klasörüne bakıyor)
        for fruit in scraped_data["normal"]:
            name = fruit.get("name", "")
            fruit_type = fruit.get("type", "")
            
            # Hem isme hem meyvenin türüne bakıyoruz
            for kw in keywords:
                if kw in name.lower() or kw in fruit_type.lower():
                    if name not in found_normal:
                        found_normal.append(name) # Orijinal ismi listeye ekle
                    break
                    
        # 2. Mirage Stok Kontrolü
        for fruit in scraped_data["mirage"]:
            name = fruit.get("name", "")
            fruit_type = fruit.get("type", "")
            
            for kw in keywords:
                if kw in name.lower() or kw in fruit_type.lower():
                    if name not in found_mirage:
                        found_mirage.append(name)
                    break
        
        # Sadece Normal stokta varsa bildirim gönder
        if found_normal:
            print(f"Normal stokta meyve bulundu! Bildirim gönderiliyor...")
            send_discord_alert(found_normal, found_mirage)
        else:
            print("Normal stokta aranan meyve yok. Bildirim gönderilmedi.")
            
    else:
        print("Hata: Veri paketi bulunamadı. Sitenin yapısı değişmiş olabilir.")

def send_discord_alert(normal, mirage):
    msg = "🚨 **Blox Fruits Stok Raporu** 🚨\n\n"
    
    msg += f"🏪 **Normal Stok:** {', '.join(normal)}\n"
    
    if mirage:
        msg += f"🏝️ **Mirage Stoğu:** {', '.join(mirage)}\n"
    else:
        msg += f"🏝️ **Mirage Stoğu:** Aranan değerli meyve yok.\n"
        
    msg += f"\n🔗 Kontrol et: {TARGET_URL}"
    
    requests.post(WEBHOOK_URL, json={"content": msg, "username": "Blox Ajanı", "avatar_url": "https://i.imgur.com/AfFp7pu.png"})

if __name__ == "__main__":
    if WEBHOOK_URL:
        check_stock()
    else:
        print("HATA: Webhook URL bulunamadı!")
