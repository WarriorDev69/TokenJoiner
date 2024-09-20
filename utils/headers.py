from user_agent import generate_user_agent
import random
import base64
import json

os = ["Windows", "Mac OS X", "Linux", "iOS", "Android"]
browsers = ["Chrome", "Firefox", "Safari", "Edge", "Opera"]


def cr_headers(token, dcfduid, sdcfduid, cfruid) -> dict:
    user = generate_user_agent()
    ros = random.choice(os)
    rbrowser = random.choice(browsers)
    xsuper = {
        "os": ros,
        "browser": rbrowser,
        "device": "",
        "system_locale": "en-JM",
        "browser_user_agent": user,
        "browser_version": "",
        "os_version": "",
        "referrer": "",
        "referring_domain": "",
        "referrer_current": "",
        "referring_domain_current": "",
        "release_channel": "stable",
        "client_build_number": 181832,
        "client_event_source": "null"
    }
    xsuperjson = json.dumps(xsuper)
    xsuper = base64.b64encode(xsuperjson.encode()).decode()
    headers = {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "fr-FR,fr;q=0.9",
        "authorization": token,
        "cache-control": "no-cache",
        "content-type": "application/json",
        "cookie": f"__dcfduid={dcfduid}; __sdcfduid={sdcfduid}; __cfruid={cfruid}; locale=en-US",
        "origin": "https://discord.com",
        "pragma": "no-cache",
        "referer": "https://discord.com/channels/@me",
        "sec-ch-ua": '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": user,
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": xsuper
    }
    return headers
