from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webparser import websettings


class WebParser(object):
    """
    Class for parsing throw selenium
    """

    def __enter__(self):
        options = Options()
        if self.headless:
            options.add_argument("--headless")
        # options.add_argument(websettings.USER_AGENT)
        capabilities = DesiredCapabilities.FIREFOX
        capabilities["marionette"] = True
        try:
            self.driver = webdriver.Firefox(firefox_options=options, capabilities=capabilities)
            self.driver.get(self.url)
            WebDriverWait(self.driver, websettings.TIMEOUT).until(EC.presence_of_element_located(
                (By.CLASS_NAME, websettings.MSC_MAIN_TABLE)))
        except TimeoutException:
            self.error = 'Timeout Selenium'
        except Exception as e:
            self.error = e
        else:
            self.error = 'Ok'
        return self

    def __exit__(self, exp_type, exp_value, traceback):
        self.driver.quit()

    def __init__(self, url, headless=True):
        self.url = url
        self.element = ''
        self.error = 'Ok'
        self.headless = headless
        self.sleeptime = websettings.REFRESH_TIME

    def get_source_html(self):
        """
        get source html throw selenium driver
        :return: raw html
        """
        return self.driver.page_source

    def get_screenshot(self, filename):
        """
        Save screenshot
        :return: True if success
        """
        return self.driver.save_screenshot(filename)





