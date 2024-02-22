import os
import json
import time
import traceback
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys

def load_data(file_name):
    file_path = f'./public/json/{file_name}.json'
    default_data = {
        "file_created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "posts": {}
    }
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):  
        return default_data

def save_data_to_json(posts_data, file_name):
    file_creation_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    final_data = {
        "file_created_at": file_creation_time,
        "posts": posts_data
    }
    file_path = f'./public/json/{file_name}.json'
    
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(final_data, file, ensure_ascii=False, indent=4)
    
    return file_creation_time

def ensure_data_file_exists(file_name):
    file_path = f'./public/json/{file_name}.json'
    if not os.path.exists(file_path):
        initial_data = {
            "file_created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "posts": {}
        }
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(initial_data, file, ensure_ascii=False, indent=4)

def setup_driver(chrome_options):
    service = Service(executable_path="./chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(300)
    return driver

def capture_directory_exists(ch):
    path = f'./public/capture/{ch}'

    if not os.path.exists(path):
        os.makedirs(path)
    return path

def clean_url(url):
    prefixes = ["http://www.", "https://www.", "http://", "https://"]
    for prefix in prefixes:
        if url.startswith(prefix):
            return url[len(prefix):]
    return url

def fetch_and_parse_html(driver, url):
    try:
        driver.get(url)
        time.sleep(20)  
        return BeautifulSoup(driver.page_source, 'html.parser')
    except TimeoutException:
            print(f"타임아웃 에러 발생 URL: {url}. 다시 시도해주시길 바랍니다.")
            driver.quit()  
            raise TimeoutException(f"Failed to load {url}, browser closed.")

def take_screenshot(v, driver, number, victim, capture_path):
    if v == 'lockbit':
        css_selector = f'.post-block:nth-child({number})'
    elif v == 'blacksuit':
        css_selector = f'.card:nth-child({number})'
    elif v == 'alphv':
        css_selector = f'.post:nth-child({number})'
    elif v == 'leakbase':
        css_selector = f'.structItem:nth-child({number})'
    
    element = driver.find_element(By.CSS_SELECTOR, css_selector)
    driver.execute_script("arguments[0].scrollIntoView();", element)
    element.screenshot(os.path.join(capture_path, f'{victim}.png'))
    print("[+] Screenshot!", flush=True)



def get_data(ch):
    new_titles = []
    print("크롤링 작업 수행 중...")
    chrome_options = Options()
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('disable-gpu')
    chrome_options.add_argument('start-maximized')
    chrome_options.add_argument('ignore-certificate-errors')
    chrome_options.add_argument('hide-scrollbars')
    chrome_options.add_argument("--proxy-server=socks5://127.0.0.1:9150")
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36')

    capture_directory = capture_directory_exists(ch)
    
    file_name = f'json_{ch}'
    ensure_data_file_exists(file_name)

    existing_data = load_data(file_name)

    data_updated = False
    
    try:
        if ch == 'lockbit':
            URL = "http://lockbitapt2yfbt7lchxejug47kmqvqqxvvjpqkmevv4l3azl3gy6pyd.onion"
            posts_data = {}
            driver = setup_driver(chrome_options)

            soup = fetch_and_parse_html(driver, URL)
            
            post_container = soup.find('div', class_='post-big-list')
            if post_container:
                post_blocks = post_container.find_all('a', class_='post-block')

                for number, post in enumerate(post_blocks, start=1):
                    try:
                        title = post.find('div', class_='post-title').text.strip()
                        post_text = post.find('div', class_='post-block-text').text.strip()
                        updated_date = post.find('div', class_='updated-post-date').text.strip()
                        victim = "".join(x for x in title if x.isalnum() or x.isspace())
                        days = post.find('span', class_='days').text.strip() if post.find('span', class_='days') else ''
                        
                        if title not in existing_data.get("posts", {}):
                            new_titles.append(title)
                            take_screenshot(ch, driver, number, victim, capture_directory)
                            existing_data["posts"][title] = {
                                'post-title': title,
                                'post_timer': days,
                                'post-text': post_text,
                                'updated-date': updated_date,
                                'ch':'LockBit',
                            }            
                            data_updated = True

                        if title in existing_data.get("posts", {}):
                            if existing_data["posts"][title]['post_timer'] != days:
                                take_screenshot(ch, driver, number, victim, capture_directory)
                                existing_data["posts"][title] = {
                                'post-title': title,
                                'post_timer': days,
                                'post-text': post_text,
                                'updated-date': updated_date,
                                'ch':'LockBit',
                            }    
                            data_updated = True


                    except Exception as e:
                        traceback.print_exc()

            if data_updated:
                save_time = save_data_to_json(existing_data["posts"], file_name)                
                return {"status": "success", "time": save_time, "new_titles": new_titles}  
            else:
                return {"status": "success", "message": "No new data to update.", "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "new_titles": new_titles}

        if ch == 'blacksuit':
            URL = "http://weg7sdx54bevnvulapqu6bpzwztryeflq3s23tegbmnhkbpqz637f2yd.onion"
            posts_data = {}
            current_page_number = 1
            driver = setup_driver(chrome_options)

            try:
                while True:
                    soup = fetch_and_parse_html(driver, f"{URL}/?page={current_page_number}")
                    post_container = soup.find('main')
                    if post_container:
                        post_blocks = post_container.find_all('div', class_='card')
                        for number, post in enumerate(post_blocks, start=1):
                            try:
                                title = post.find('div', class_='url').find('a')['href'].strip()
                                clean_title = clean_url(title)
                                post_text = post.find('div', class_='text').text.strip()
                                victim = "".join(x for x in clean_title if x.isalnum() or x.isspace())
                                
                                links = []
                                link_div = post.find('div', class_='links')
                                if link_div:
                                    for lk in link_div.find_all('a'):
                                        url_title = lk.text.strip()
                                        url_link = lk['href']
                                        
                                        links.append({
                                            'url-title': url_title,
                                            'url-link': url_link,
                                        })

                                if clean_title not in existing_data.get("posts", {}):
                                    new_titles.append(title)
                                    take_screenshot(ch, driver, number, victim, capture_directory)
                                    existing_data["posts"][clean_title] = {
                                        'post-title': clean_title,
                                        'post-text': post_text,
                                        'ch':'BlackSuit',
                                        'post-url': links,
                                    } 
                                    data_updated = True

                            except Exception as e:
                                traceback.print_exc()

                            
                    
                    pagination_links = driver.find_elements(By.CSS_SELECTOR, ".pagination a")
                    if pagination_links and current_page_number < int(pagination_links[-1].text):
                        current_page_number += 1
                    else:
                        break

            except Exception as e:
                traceback.print_exc()
                        
            if data_updated:
                save_time = save_data_to_json(existing_data["posts"], file_name)                
                return {"status": "success", "time": save_time, "new_titles": new_titles}  
            else:
                return {"status": "success", "message": "No new data to update.", "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "new_titles": new_titles}  

        
        if ch == 'alphv':
            URL = "http://alphvuzxyxv6ylumd2ngp46xzq3pw6zflomrghvxeuks6kklberrbmyd.onion"
            posts_data = {}
            current_page_number = 1
            driver = setup_driver(chrome_options)

            try:
                while True:
                    soup = fetch_and_parse_html(driver, f"{URL}/?page={current_page_number}")
                    post_container = soup.find('div', class_='posts')
                    if post_container:
                        post_blocks = post_container.find_all('div', class_='post')
                        for number, post in enumerate(post_blocks, start=1):
                            try:
                                title = post.find('div', class_='post-header').text.strip()
                                post_text = post.find('div', class_='post-description').text.strip()
                                victim = "".join(x for x in title if x.isalnum())
                
                                if title not in existing_data.get("posts", {}):
                                    new_titles.append(title)
                                    take_screenshot(ch, driver, number, victim, capture_directory)
                                    existing_data["posts"][title] = {
                                        'post-title': title,
                                        'post-text': post_text,
                                        'ch':'ALPHV',
                                    }  
                                    data_updated = True

                            except Exception as e:
                                traceback.print_exc()
                                
                    pagination_buttons = driver.find_elements(By.CSS_SELECTOR, ".bx--pagination-nav__accessibility-label")
                    page_numbers = [int(btn.text) for btn in pagination_buttons if btn.text.isdigit()]

                    print(page_numbers and current_page_number < max(page_numbers))
                    if page_numbers and current_page_number < max(page_numbers):
                        current_page_number += 1
                    else:
                        break

            except Exception as e:
                traceback.print_exc()
                        
            if data_updated:
                save_time = save_data_to_json(existing_data["posts"], file_name)                
                return {"status": "success", "time": save_time, "new_titles": new_titles} 
            else:
                return {"status": "success", "message": "No new data to update.", "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "new_titles": new_titles}  # 수정된 부분

        
        if ch == 'leakbase':
            URL = "https://leakbase.io/forums/apbchucky"
            posts_data = {}
            driver = setup_driver(chrome_options)

            try:
                soup = fetch_and_parse_html(driver, URL)
                post_container = soup.find('div', class_='structItemContainer-group')
                if post_container:
                    post_blocks = post_container.find_all('div', class_='structItem')
                    for number, post in enumerate(post_blocks, start=1):
                        try:
                            title = post.find('div', class_='structItem-title').find('a').text.strip()
                            print(title)
                            post_box = post.find('div', class_='structItem-minor')
                            tags_text_list = [tag.text.strip() for tag in post_box.find_all('span', 'prefix-steam')]
                            username = post_box.find('span', class_='username--style3').text.strip()
                            start_date = post_box.find('time', class_='u-dt')['datetime']

                            victim = "".join(x for x in title if x.isalnum())

                            if title not in existing_data.get("posts", {}):
                                    new_titles.append(title)
                                    take_screenshot(ch, driver, number, victim, capture_directory)
                                    existing_data["posts"][title] = {
                                        'post-title': title,
                                        'tag': tags_text_list,
                                        'user': username,
                                        'date': start_date,
                                        'ch': 'LeakBase',  
                                    }  
                                    data_updated = True
                        except Exception as e:
                            traceback.print_exc()

                if data_updated:
                    save_time = save_data_to_json(existing_data["posts"], file_name)                
                    return {"status": "success", "time": save_time, "new_titles": new_titles}  
                else:
                    return {"status": "success", "message": "No new data to update.", "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "new_titles": new_titles}  

            except Exception as e:
                traceback.print_exc()

    except Exception as e:
        traceback.print_exc()
        return {"status": "error", "message": "크롤링 중 오류 발생"}


