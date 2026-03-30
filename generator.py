import requests
import re
import yaml
import os

def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_category(info_upper, category_map):
    for category, keywords in category_map.items():
        # Keywords listesini düzleştiriyoruz (eğer YAML'da alt alta yazdıysan)
        for keyword in keywords:
            if keyword.upper() in info_upper:
                return category
    return "GENERAL"

def run_global_generator():
    print("--- Behind The Grid: Küresel Sentez Operasyonu Başladı ---")
    config = load_config()
    
    welcome = config['settings']['welcome_channel']
    final_output = "#EXTM3U\n"
    # Başlangıca özel markalı kanalını ekle
    final_output += f'#EXTINF:-1 tvg-logo="{welcome["logo"]}" group-title="SD SPECIAL", {welcome["name"]}\n{welcome["url"]}\n'

    for code, data in config['countries'].items():
        country_name = data['name']
        print(f"[*] {country_name} kanalları işleniyor...")
        
        try:
            response = requests.get(data['url'], timeout=15)
            if response.status_code != 200: 
                print(f"    [!] Hata: {country_name} kaynağına ulaşılamadı (HTTP {response.status_code})")
                continue
            
            lines = response.text.split('\n')
            channel_count = 0
            
            for i in range(len(lines)):
                if lines[i].startswith("#EXTINF"):
                    info = lines[i]
                    stream_url = lines[i+1].strip() if (i+1) < len(lines) else ""
                    
                    if not stream_url.startswith("http"): continue

                    # Kategori belirleme (Büyük harf duyarlı kontrol)
                    cat = get_category(info.upper(), config['categories'])
                    
                    # Yeni grup başlığı: "TURKEY | SPORTS" veya "RUSSIA | MOVIES" gibi
                    new_group = f"{country_name} | {cat}"
                    
                    # Group-title etiketini güncelle veya yoksa ekle
                    if 'group-title="' in info:
                        updated_info = re.sub(r'group-title="[^"]*"', f'group-title="{new_group}"', info)
                    else:
                        updated_info = info.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{new_group}"')
                    
                    final_output += f"{updated_info}\n{stream_url}\n"
                    channel_count += 1
            
            print(f"    [+] {channel_count} kanal başarıyla sentezlendi.")
                        
        except Exception as e:
            print(f"    [!] Beklenmedik Hata ({country_name}): {e}")

    # Sonuç dosyasını kaydet
    output_path = config['settings']['output_file']
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_output)
    
    print(f"\n--- Operasyon Tamamlandı! '{output_path}' Dosyan Hazır. ---")

if __name__ == "__main__":
    run_global_generator()
