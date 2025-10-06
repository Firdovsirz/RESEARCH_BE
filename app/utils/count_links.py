from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

# Selenium setup
chrome_options = Options()
chrome_options.add_argument("--headless") 
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
service = Service("/path/to/chromedriver")  
driver = webdriver.Chrome(service=service, options=chrome_options)

def get_link_by_xpath(xpath):
    try:
        element = driver.find_element(By.XPATH, xpath)
        return element.text  
    except NoSuchElementException:
        return None

def count_links():
    user_links = {
        "scopus": get_link_by_xpath('//*[@id="scopus-author-profile-page-control-microui__general-information-content"]/section/ul/li[2]/div/div/div/div/div[1]/span'),
        # "web_of_science": get_link_by_xpath('//web_of_science_xPath_buraya_qoyun'),
        # "google_scholar": get_link_by_xpath('//google_scholar_xPath_buraya_qoyun')
    }
    return user_links

# URL-i açmaq
driver.get("https://scopus.com/author/...")  # Müvafiq profil linki

links = count_links()
print(links)

driver.quit()
