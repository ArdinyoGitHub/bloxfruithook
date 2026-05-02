import os
import requests
from playwright.sync_api import sync_playwright

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")
TARGET_URL = "https://fruityblox.com/stock"
SEARCH_KEYWORDS = ["elemental", "mythical", "kitsune", "leopard", "dragon", "dough", "t-rex", "mammoth"]

def check_stock():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(TARGET_URL)
        
        try:
            # Sayfanın yüklenmesini bekle
            page.wait_for_selector("text=Normal", timeout=20000)
            page.wait_for_timeout(5000)
            
            # Normal ve Mirage alanlarını ayrı ayrı yakalayalım
            # Sitedeki HTML yapısına göre bu alanları bölüyoruz
            normal_section = page.locator("div:has-text('Normal')").first.inner_text().lower()
            mirage_section = page.locator("div:has-text('Mirage')").first.inner_text().lower()
            
            found_normal = [word.capitalize() for word in SEARCH_KEYWORDS if word in normal_section]
            found_mirage = [word.capitalize() for word in SEARCH_KEYWORDS if word in mirage_section]
            
            if found_normal or found_mirage:
                send_discord_alert(found_normal, found_mirage)
            else:
                print("İki dükkanda da aranan meyve yok.")
                
        except Exception as e:
            print(f"Hata: {e}")
        browser.close()

def send_discord_alert(normal, mirage):
    msg = "🚨 **Blox Fruits Stok Raporu** 🚨\n\n"
    
    if normal:
        msg += f"🏪 **Normal Stok:** {', '.join(normal)}\n"
    if mirage:
        msg += f"🏝️ **Mirage Stoğu:** {', '.join(mirage)}\n"
        
    msg += f"\n🔗 Kontrol et: {TARGET_URL}"
    
    requests.post(WEBHOOK_URL, json={"content": msg, "username": "Blox Ajanı"})
