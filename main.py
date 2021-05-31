import json
import urllib.parse
from functools import lru_cache
from pathlib import Path

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Firefox
from selenium.webdriver import FirefoxProfile
from selenium.webdriver.common.keys import Keys

BASEDIR = Path(__file__).parent


class Profile(FirefoxProfile):
    accept_untrusted_certs = True
    assume_untrusted_cert_issuer = False

    def __init__(self, profile_directory=None):
        super().__init__(profile_directory)

        # отключаем WebRTC
        self.set_preference("media.peerconnection.enabled", False)
        self.set_preference("dom.webnotifications.enabled", False)
        self.set_preference("dom.webdriver.enabled", False)
        self.set_preference("browser.aboutConfig.showWarning", False)


class Client(Firefox):
    def __init__(self):
        profile = Profile()
        # profile.set_preference("general.useragent.override", "user-agent")
        super().__init__(firefox_profile=profile,
                         firefox_binary=str(BASEDIR.joinpath("bin", "firefox", "firefox-bin")),
                         executable_path=str(BASEDIR.joinpath("bin", "geckodriver")))

    def post_init(self, proxy=None, cookies=None, headers=None):
        if any((proxy, cookies, headers)):
            if cookies:
                self.raise_if_url_not_set_for(cookies)
            uuid = self.install_addon(str(Path("bin/selenium_helper.xpi").absolute()))
            internal_uuid = self.get_installed_addons()[uuid]
            self.get(f"moz-extension://{internal_uuid}/data/options.html")
            if proxy:
                proxy = urllib.parse.urlparse(proxy)
                proxy = {
                    "type": proxy.scheme,
                    "host": proxy.hostname,
                    "port": proxy.port,
                    "username": proxy.username,
                    "password": proxy.password
                }

            js = f"""saveOptionsEx({json.dumps(proxy)}, {json.dumps(cookies)}, {json.dumps(headers)});"""
            self.execute_script(js)
            self.get("about:blank")

    def raise_if_url_not_set_for(self, cookie):
        all(x["url"] for x in cookie)

    def get_installed_addons(self):
        return json.loads(self._get_preference("extensions.webextensions.uuids"))

    @lru_cache()
    def _get_preference(self, name):

        def get_search_box_with_wait_about_config_approved(_attemps=1):
            try:
                search_box = self.find_element_by_id("about-config-search")
            except NoSuchElementException:
                if _attemps > 1:
                    raise
                input("Approve warning message and press Enter to continue...")
                return get_search_box_with_wait_about_config_approved(_attemps + 1)
            else:
                return search_box

        self.get("about:config")

        search_box = get_search_box_with_wait_about_config_approved()
        # search_box.clear()
        search_box.send_keys(name)
        search_box.send_keys(Keys.ENTER)

        search_result = self.find_elements_by_xpath("//table[@id='prefs']/tr/td/span")
        return search_result[0].text


if __name__ == '__main__':
    browser = Client()
    try:
        browser.post_init(
            proxy="http://***:***@***:8000",
            cookies=[{"url": "https://whoer.net/", "name": "test", "value": "1"}],
            headers={"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27"})
        browser.get("https://whoer.net/")
        input("Enter")
    finally:
        browser.close()
