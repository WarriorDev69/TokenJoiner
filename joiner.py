import toml
from datetime import datetime
from concurrent.futures   import ThreadPoolExecutor

from utils.console import *
from utils.cookies import *
from utils.headers import *
from utils.session import *
from utils.captcha import *
import os

trnn = datetime.now().strftime("%H-%d-%m-%S")
dcfduid, sdcfduid, cfruid = get_cookies()
os.makedirs(f"output/{trnn}", exist_ok=True)
with open('assets/config.toml') as f:
    config = toml.load(f)


def get_headers(token) -> dict:
    headers = cr_headers(token, dcfduid, sdcfduid, cfruid)
    return headers


for section_key, section_value in list(config.items()):
    if isinstance(section_value, dict):
        for key, value in section_value.items():
            config[key] = value
        del config[section_key]

def get_proxy() -> dict:
    if config["proxyless"]:
        return
    try:
        proxy = random.choice(open("assets/proxies.txt", "r").read().splitlines())
        return {"http": f"http://{proxy}", "https": f"http://{proxy}"}
    except Exception as e:
        pass


def format(token) -> str:
    if ":" in token:
        tokeny = token.split(":")
        return tokeny[-1]
    else:
        return token


def jsv(headers, invite, token2):
    token = format(token2)
    outcome = False
    guild_id = 0
    sesh = get_session()
    try:
        for i in range(config["retries"]):

            response = sesh.post(f'https://discord.com/api/v9/invites/{invite}', json={}, headers = headers, proxy=get_proxy())
            if response.status_code == 429:
                err(
                    f"Cloudflare error, please add proxies or wait for some time",
                    token=f"{token[:min(len(token), 30)]}*******",
                    invite=f".gg/{invite}"
                )
                break


            if response.status_code == 401:
                err(
                    f"Token invalid",
                    token=f"{token[:min(len(token), 30)]}*******",
                    invite=f".gg/{invite}"
                )
                break



            elif response.status_code in [200, 204]:
                outcome = True
                guild_id = response.json()["guild"]["id"]
                debug(
                    f"Joined server",
                    token=f"{token[:min(len(token), 30)]}*******",
                    invite=f".gg/{invite}",
                    guild=guild_id,
                )
                break


            elif "captcha_rqdata" in response.text:
                debug(
                    f"Captcha, solving...",
                    token=f"{token[:min(len(token), 30)]}*******",
                    invite=f".gg/{invite}",
                )
                r = response.json()
                solution = solve(rqdata = r['captcha_rqdata'], site_key = r['captcha_sitekey'], websiteURL = "https://discord.com", useragent="Mozilla/5.0 (Macintosh; U; PPC Mac OS X; de-de) AppleWebKit/85.8.5 (KHTML, like Gecko) Safari/85", token=token)
                if solution == None:
                    break

                response = sesh.post(f'https://discord.com/api/v9/invites/{invite}', json={'captcha_key': solution,'captcha_rqtoken': r['captcha_rqtoken']}, headers = headers, proxy=get_proxy())
                if response.status_code in [200, 204]:
                    outcome = True
                    guild_id = response.json()["guild"]["id"]
                    debug(
                        f"Joined server after captcha",
                        token=f"{token[:min(len(token), 30)]}*******",
                        invite=f".gg/{invite}",
                        guild=guild_id,
                    )
                    break
                elif response.status_code == 403:
                    outcome = False
                    err(
                        f"Error joining server",
                        token=f"{token[:min(len(token), 30)]}*******",
                        invite=f".gg/{invite}",
                        response=response.text,
                    )
                    break



                else:
                    err(
                        f"Error joining server, retrying",
                        token=f"{token[:min(len(token), 30)]}*******",
                        invite=f".gg/{invite}",
                        response=response.text,
                    )                    

        if outcome:
            os.makedirs(f"output/{trnn}", exist_ok=True)
            with open(f"output/{trnn}/success.txt", "a") as f:
                f.write(token2 + '\n')
        else:
            os.makedirs(f"output/{trnn}", exist_ok=True)
            with open(f"output/{trnn}/error.txt", "a") as f:
                f.write(token2 + '\n')
        return outcome, guild_id

            
    except Exception as e:
        err(
            f"Error joining server, retrying",
            token=f"{token[:min(len(token), 30)]}*******",
            invite=f".gg/{invite}",
            error=e
        )    
        jsv(headers, invite, token)



def join(token, invite):
        headers = get_headers(format(token))
        jsv(headers, invite, token)


def main():
    max = config["threads"]
    debug("Enter server invite")
    invite = inpt("discord.gg/")
    with open("assets/tokens.txt", "r") as f:
        tokens = f.read().splitlines()
    with ThreadPoolExecutor(max_workers=max) as executor:
        futures = [executor.submit(join, token, invite) for token in tokens]
        for future in futures:
            future.result()

asciiprint()
main()
inpt("Complete, press enter to exit")