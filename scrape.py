import json
import os
import re
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_single_anime(base_url, total_episodes=1, start_number=1, skip_list=[], all_mode=False):
    print(f"\n🔄 جاري استخراج: {base_url}")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service()
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(base_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="mCSB_1_container"]/li')))
        episode_elements = driver.find_elements(By.XPATH, '//*[@id="mCSB_1_container"]/li/a')
        episode_links = [e.get_attribute("href") for e in episode_elements]

        if all_mode:
            selected_links = episode_links
        else:
            selected_links = episode_links[start_number - 1:start_number - 1 + total_episodes]

        all_episodes = []
        anime_title = "?"

        for idx, link in enumerate(selected_links, start=1):
            if idx in skip_list:
                continue
            try:
                driver.get(link)
                wait = WebDriverWait(driver, 10)
                episode_title_raw = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div/h3"))).text.strip()

                if anime_title == "?":
                    anime_title = re.sub(r"الحلقة\s+\d+", "", episode_title_raw).strip()

                match = re.search(r"الحلقة\s+\d+", episode_title_raw)
                episode_title = match.group(0) if match else episode_title_raw
                episode_number = int(''.join(filter(str.isdigit, episode_title)))

                server_list = driver.find_elements(By.XPATH, '//*[@id="episode-servers"]/li')
                servers = []

                for li in server_list:
                    try:
                        a_tag = li.find_element(By.TAG_NAME, "a")
                        server_name = a_tag.text.strip()
                        href = a_tag.get_attribute("data-ep-url") or a_tag.get_attribute("href")
                        if href:
                            url = href.strip()
                            if url.startswith("//"):
                                url = "https:" + url
                            servers.append({
                                "serverName": server_name,
                                "url": url
                            })
                    except:
                        continue

                clean_title = re.sub(r'[\\/:*?"<>|]', "", anime_title).replace(" ", "-").lower()

                ep_data = {
                    "number": episode_number,
                    "title": episode_title,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "link": f"https://abdo12249.github.io/1/test1/episodes/المشاهده.html?id={anime_title.replace(':', '').replace(' ', '-').lower()}&episode={episode_number}",
                    "image": f"https://abdo12249.github.io/1/images/{clean_title}.webp",
                    "servers": servers
                }

                all_episodes.append(ep_data)

            except Exception as e:
                print(f"❌ فشل استخراج حلقة: {link}")
                print(f"↪ السبب: {e}")

        result = {
            "animeTitle": anime_title,
            "episodes": all_episodes
        }

        safe_title = re.sub(r'[\\/*:?"<>|]', "", anime_title).replace(" ", "-").lower()
        os.makedirs("episodes", exist_ok=True)
        with open(f"episodes/{safe_title}.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"✅ تم حفظ الحلقات في: episodes/{safe_title}.json")

    finally:
        driver.quit()

def main():
    with open("anime_links.json", "r", encoding="utf-8") as f:
        urls = json.load(f)

    for url in urls:
        scrape_single_anime(url, total_episodes=1, start_number=1, skip_list=[], all_mode=False)

if __name__ == "__main__":
    main()