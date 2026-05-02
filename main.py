import os
import requests
from playwright.sync_api import sync_playwright

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")
TARGET_URL = "https://fruityblox.com/stock"

# Aranan meyveler listesi (İstediğin zaman buraya yeni isimler ekleyebilirsin)
SEARCH_KEYWORDS = ["yeti", "tiger", "mammoth", "gravity", "mythical", "kitsune", "leopard", "dragon", "magma", "dough", "t-rex"]

def check_stock():
    with sync_playwright() as p:
        # Sitenin bot olduğumuzu anlamaması için ufak bir güvenlik atlatma parametresi ekledik
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        page = browser.new_page()
        
        print("Siteye giriliyor...")
        page.goto(TARGET_URL)
        
        try:
            # Sayfanın yüklenmesini bekle
            page.wait_for_selector("text=Normal", timeout=20000)
            page.wait_for_timeout(5000)
            
            # Normal ve Mirage alanlarını siteden ayrı ayrı çekiyoruz
            normal_section = page.locator("div:has-text('Normal')").first.inner_text().lower()
            mirage_section = page.locator("div:has-text('Mirage')").first.inner_text().lower()
            
            # İki dükkan için de aranan meyveleri listeliyoruz
            found_normal = [word.capitalize() for word in SEARCH_KEYWORDS if word in normal_section]
            found_mirage = [word.capitalize() for word in SEARCH_KEYWORDS if word in mirage_section]
            
            # KRİTİK ŞART: Sadece Normal stokta meyve varsa bildirim at
            if found_normal:
                print(f"Normal stokta meyve bulundu! Bildirim gönderiliyor...")
                send_discord_alert(found_normal, found_mirage)
            else:
                print("Normal stokta aranan meyve yok. Bildirim gönderilmedi.")
                
        except Exception as e:
            print(f"Hata oluştu: {e}")
            
        browser.close()

def send_discord_alert(normal, mirage):
    msg = "🚨 **Blox Fruits Stok Raporu** 🚨\n\n"
    
    # Normal stok zaten dolu olduğu için direkt yazdırıyoruz
    msg += f"🏪 **Normal Stok:** {', '.join(normal)}\n"
    
    # Mirage stoğunda meyve varsa yazdır, yoksa "Bulunamadı" de
    if mirage:
        msg += f"🏝️ **Mirage Stoğu:** {', '.join(mirage)}\n"
    else:
        msg += f"🏝️ **Mirage Stoğu:** Aranan değerli meyve yok.\n"
        
    msg += f"\n🔗 Kontrol et: {TARGET_URL}"
    
    # Discord'a veriyi gönderiyoruz
    requests.post(WEBHOOK_URL, json={"content": msg, "username": "Blox Ajanı", "avatar_url": "https://i.imgur.com/AfFp7pu.png"})

if __name__ == "__main__":
    if WEBHOOK_URL:
        check_stock()
    else:
        print("HATA: Webhook URL bulunamadı!")
