from utils.console import *
import toml
import httpx

with open("assets/config.toml") as f:
    config = toml.load(f)
for section_key, section_value in list(config.items()):
    if isinstance(section_value, dict):
        for key, value in section_value.items():
            config[key] = value
        del config[section_key]



def solve(rqdata, site_key, websiteURL, useragent, token) -> str:
    task_payload = {
        "clientKey": config["capmonster"],
        "task": {
            "type": "HCaptchaTaskProxyless",
            "isInvisible": True,
            "data": rqdata,
            "websiteURL": websiteURL,
            "websiteKey": site_key,
            "userAgent": useragent,
        },
    }
    key = None
    with httpx.Client(
        headers={"content-type": "application/json", "accept": "application/json"},
        timeout=30,
    ) as client:
        task_id = client.post(
            f"https://api.capmonster.cloud/createTask", json=task_payload
        ).json()["taskId"]
        get_task_payload = {
            "clientKey": config["capmonster"],
            "taskId": task_id,
        }

        while key is None:
            response = client.post(
                "https://api.capmonster.cloud/getTaskResult", json=get_task_payload
            ).json()
            try:
                if response["status"] == "ready":
                    key = response["solution"]["gRecaptchaResponse"]
                    debug(
                        "Solved a captcha",
                        token=f"{token[:min(len(token), 30)]}*******",
                        solution=f"{key[:min(len(token), 40)]}******",
                    )
                else:
                    time.sleep(1)
            except Exception as E:
                debug(
                    "Error solving captcha",
                    token=f"{token[:min(len(token), 30)]}*******",
                    err=E,
                )
                return "123"

    return key
