import json
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options as EdgeOptions


class SessionHandler:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

    def save_config(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def cookies_to_session(self, cookies):
        session = requests.Session()
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])
        return session

    def is_session_valid(self, session):
        try:
            headers = self.config["headers"]
            resp = session.get("https://www.pixiv.net/dashboard", headers=headers)
            return resp.status_code == 200 
        except Exception:
            return False

    def create_session_with_cookies(self):
        print("try to use local cookies……")
        return self.cookies_to_session(self.config["cookies"])

    def create_session_with_login(self):

        username = self.config["auth"]["username"]
        password = self.config["auth"]["password"]

        if not username or not password:
            print("no username or password, please set it in config.json")
            return None

        options = EdgeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)

        browser = webdriver.Edge(options=options)
        browser.set_window_size(1366, 768)
        browser.get("https://www.pixiv.net/")
        time.sleep(2)

        # 点击“登录”
        browser.find_element(
            By.CSS_SELECTOR, 
            '#wrapper > div.signup-form > div > div:nth-child(2) > a.signup-form__submit--login'
        ).click()
        time.sleep(2)

        browser.find_element(
            By.CSS_SELECTOR, 
            '#app-mount-point > div > div > div.sc-fvq2qx-4.bntRDI > div.sc-2oz7me-0.iGLGot > form > fieldset.sc-bn9ph6-0.bYwpCj.sc-2o1uwj-5.brtxjH > label > input'
        ).send_keys(username)
        browser.find_element(
            By.CSS_SELECTOR, 
            '#app-mount-point > div > div > div.sc-fvq2qx-4.bntRDI > div.sc-2oz7me-0.iGLGot > form > fieldset.sc-bn9ph6-0.bYwpCj.sc-2o1uwj-6.eTXdqi > label > input'
        ).send_keys(password)
        time.sleep(2)
        browser.find_element(
            By.CSS_SELECTOR, 
            '#app-mount-point > div > div > div.sc-fvq2qx-4.bntRDI > div.sc-2oz7me-0.iGLGot > form > button.charcoal-button.sc-2o1uwj-10.divuub'
        ).click()
        time.sleep(2)

        cookies = browser.get_cookies()
        browser.close()

        self.config["cookies"] = cookies
        self.save_config()

        print("login success, has updated local cookies")
        return self.cookies_to_session(cookies)

    #接口方法
    def get_session(self):
        if "cookies" in self.config:
            session = self.create_session_with_cookies()
            if self.is_session_valid(session):
                print("Successfully use local cookies to login")
                return session
            else:
                print("local cookies is invalid, try to login……")
                return self.create_session_with_login()
        else:
            print("no local cookies, try to login……")
            return self.create_session_with_login()
