import os
import requests
import re
import json
from playwright.sync_api import sync_playwright

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")
TARGET_URL = "https://fruityblox.com/stock"

# BURA ÇOK ÖNEMLİ: Telefonda oluşturduğun benzersiz ntfy kanal adını buraya yaz!
NTFY_TOPIC = "bloxfruitmythic_ardao" 

SEARCH_KEYWORDS = ["pain", "yeti", "tiger", "mammoth", "gravity", "mythical", "kitsune", "leopard", "dragon", "magma", "dough", "t-rex"]

def check_stock():
    scraped_data = {"normal": [], "mirage": []}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        page = browser.new_page()
        
        def handle_response(response):
            try:
                text = response.text()
                if '"normal":[' in text and '"mirage":[' in text:
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
        
        try:
            page.wait_for_selector("text=Normal", timeout=20000)
            page.wait_for_timeout(3000)
        except:
            print("Sayfa yüklenirken zaman aşımı oldu ama veriler gelmiş olabilir.")
            
        browser.close()

    if scraped_data["normal"] or scraped_data["mirage"]:
        found_normal = []
        found_mirage = []
        keywords = [kw.lower() for kw in SEARCH_KEYWORDS]
        
        for fruit in scraped_data["normal"]:
            name = fruit.get("name", "")
            fruit_type = fruit.get("type", "")
            for kw in keywords:
                if kw in name.lower() or kw in fruit_type.lower():
                    if name not in found_normal:
                        found_normal.append(name)
                    break
                    
        for fruit in scraped_data["mirage"]:
            name = fruit.get("name", "")
            fruit_type = fruit.get("type", "")
            for kw in keywords:
                if kw in name.lower() or kw in fruit_type.lower():
                    if name not in found_mirage:
                        found_mirage.append(name)
                    break
        
        if found_normal:
            print(f"Normal stokta meyve bulundu! Bildirimler gönderiliyor...")
            send_alerts(found_normal, found_mirage)
        else:
            print("Normal stokta aranan meyve yok. Bildirim gönderilmedi.")
    else:
        print("Hata: Veri paketi bulunamadı.")

def send_alerts(normal, mirage):
    # --- ORTAK MESAJ METNİ ---
    msg = "🚨 Blox Fruits Stok Raporu 🚨\n\n"
    msg += f"🏪 Normal Stok: {', '.join(normal)}\n"
    if mirage:
        msg += f"🏝️ Mirage Stoğu: {', '.join(mirage)}\n"
    else:
        msg += f"🏝️ Mirage Stoğu: Aranan değerli meyve yok.\n"
    msg += f"\n🔗 Kontrol et: {TARGET_URL}"
    
    # 1. DISCORD BİLDİRİMİ
    if WEBHOOK_URL:
        try:
            requests.post(WEBHOOK_URL, json={"content": msg, "username": "Blox Ajanı", "avatar_url": "https://i.imgur.com/AfFp7pu.png"})
            print("Discord bildirimi gönderildi.")
        except Exception as e:
            print(f"Discord hatası: {e}")

    # 2. TELEFON (NTFY) BİLDİRİMİ
    if NTFY_TOPIC != "bloxfruitmythic_ardao":
        try:
            # Başlıktaki emojiyi kaldırdık ve Türkçe karakter kullanmadık (latin-1 hatası almamak için).
            # "Tags" kısmına "fire" ekledik; ntfy telefonu titretecek ve başlığa 🔥 emojisini kendi koyacak.
            headers = {
                "Title": "STOK ALARMI",
                "Priority": "high", 
                "Tags": "fire,warning,video_game"
            }
            requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'), headers=headers)
            print("Telefon bildirimi gönderildi.")
        except Exception as e:
            print(f"Telefon bildirim hatası: {e}")

if __name__ == "__main__":
    check_stock()
