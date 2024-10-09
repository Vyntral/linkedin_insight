import os
import time
import random
import json
from urllib.parse import urljoin
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from .web_driver import setup_driver
from ..utils.config import LINKEDIN_USERNAME, LINKEDIN_PASSWORD, get_delay_config
from ..utils.logger import setup_logger

logger = setup_logger()
_, delay_config = get_delay_config()

def linkedin_scraper(company_url, output_dir):
    driver = setup_driver()
    wait = WebDriverWait(driver, 30)
    company_network = {}

    try:
        login_to_linkedin(driver, wait)
        navigate_to_company_page(driver, company_url, wait)
        company_details = extract_company_details(driver)
        employees = extract_employees(driver, company_url, output_dir)
        job_descriptions = extract_job_descriptions(driver, company_url, output_dir)

        company_network = {
            "company": company_details,
            "employees": employees,
            "job_descriptions": job_descriptions
        }

        for employee in employees:
            profile_url = employee.get("profile_url")
            employee_name = employee.get("name")
            if profile_url and employee_name:
                navigate_and_save_profile(driver, profile_url, company_details['name'], employee_name, output_dir)

        return company_network

    except Exception as e:
        logger.error(f"An error occurred during scraping: {str(e)}")
        return None
    finally:
        driver.quit()

def login_to_linkedin(driver, wait):
    logger.info("Navigating to LinkedIn login page.")
    driver.get("https://www.linkedin.com/login")
    human_delay(action_type='navigation')

    try:
        cookie_accept_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@data-control-name, 'accept_cookies')]")))
        cookie_accept_button.click()
        logger.info("Cookie consent accepted.")
        human_delay(action_type='navigation')
    except TimeoutException:
        logger.info("No cookie consent dialog found.")

    username_field = safe_find_element(driver, By.ID, "username")
    password_field = safe_find_element(driver, By.ID, "password")
    login_button = safe_find_element(driver, By.XPATH, "//button[@type='submit']")

    if not all([username_field, password_field, login_button]):
        logger.error("Login elements not found.")
        raise Exception("Login elements not found")

    username_field.send_keys(LINKEDIN_USERNAME)
    human_delay(action_type='login')
    password_field.send_keys(LINKEDIN_PASSWORD)
    human_delay(action_type='login')
    login_button.click()
    human_delay(action_type='login')

    # Pause to allow user to solve any CAPTCHA
    input("If there are CAPTCHAs to solve, please resolve them now. Press Enter when ready to continue...")

    logger.info("Resuming scraping after CAPTCHA pause.")

    try:
        wait.until(EC.presence_of_element_located((By.ID, "global-nav")))
        logger.info("Login successful.")
    except TimeoutException:
        logger.error("Login failed. Check credentials or presence of additional CAPTCHAs.")
        raise Exception("Login failed")

def navigate_to_company_page(driver, company_url, wait):
    logger.info(f"Navigating to company page: {company_url}")
    driver.get(company_url)
    human_delay(action_type='navigation')

    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".org-top-card-summary-info-list")))
        logger.info("Company page loaded successfully.")
    except TimeoutException:
        logger.error("Company page not found or loading too slow.")
        raise Exception("Company page not found")

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    human_delay(action_type='navigation')

def extract_company_details(driver):
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "lxml")
    
    company_details = {}
    
    try:
        logo_container = soup.find("div", {"class": "org-top-card-primary-content__logo-container"})
        logo_img = logo_container.find("img") if logo_container else None
        company_details["logo_url"] = logo_img['src'] if logo_img and 'src' in logo_img.attrs else None
    except AttributeError:
        logger.warning("Company logo not found.")
        company_details["logo_url"] = None

    try:
        company_details["name"] = soup.find("h1", {"class": "org-top-card-summary__title"}).get_text(strip=True)
    except AttributeError:
        logger.warning("Company name not found.")
        company_details["name"] = None

    try:
        company_details["description"] = soup.find("p", {"class": "org-top-card-summary__tagline"}).get_text(strip=True)
    except AttributeError:
        logger.warning("Company description not found.")
        company_details["description"] = None

    return company_details

def extract_employees(driver, company_url, output_dir):
    employees = []
    employees_url = f"{company_url.rstrip('/')}/people/"

    logger.info(f"Navigating to employees page: {employees_url}")
    driver.get(employees_url)
    human_delay(action_type='navigation')

    for _ in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        human_delay(action_type='navigation')

    soup = BeautifulSoup(driver.page_source, "lxml")
    employee_containers = soup.find_all("div", {"class": "org-people-profile-card__profile-info"})

    if not employee_containers:
        logger.warning("No employees found. Please check the CSS selector.")

    for card in employee_containers:
        employee = {}
        try:
            name_tag = card.find("div", {"class": "org-people-profile-card__profile-title"})
            title_tag = card.find("div", {"class": "lt-line-clamp--multi-line"})
            profile_tag = card.find("a", {"class": "app-aware-link"})
            img_tag = card.find("img", {"src": True})

            employee["name"] = name_tag.get_text(strip=True) if name_tag else None
            employee["title"] = title_tag.get_text(strip=True) if title_tag else None
            employee["profile_url"] = urljoin("https://www.linkedin.com", profile_tag['href']) if profile_tag and 'href' in profile_tag.attrs else None
            employee["photo_url"] = img_tag['src'] if img_tag and 'src' in img_tag.attrs else None

            if employee["name"] or employee["title"] or employee["profile_url"]:
                employees.append(employee)
        except AttributeError as e:
            logger.warning(f"Error extracting employee data: {str(e)}")

    return employees

def extract_job_descriptions(driver, company_url, output_dir):
    job_descriptions = []
    jobs_url = f"{company_url.rstrip('/')}/jobs/"

    logger.info(f"Navigating to jobs page: {jobs_url}")
    driver.get(jobs_url)
    human_delay(action_type='navigation')

    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        human_delay(action_type='navigation')

    soup = BeautifulSoup(driver.page_source, "lxml")
    job_cards = soup.find_all("li", {"class": "result-card job-result-card"})

    if not job_cards:
        logger.warning("No job listings found. Please check the CSS selector.")

    for card in job_cards:
        job = {}
        try:
            title_tag = card.find("h3", {"class": "base-search-card__title"})
            company_tag = card.find("a", {"class": "hidden-nested-link"})
            location_tag = card.find("span", {"class": "job-search-card__location"})
            job["title"] = title_tag.get_text(strip=True) if title_tag else None
            job["company"] = company_tag.get_text(strip=True) if company_tag else None
            job["location"] = location_tag.get_text(strip=True) if location_tag else None
            if job["title"] or job["location"]:
                job_descriptions.append(job)
        except AttributeError as e:
            logger.warning(f"Error extracting job data: {str(e)}")

    return job_descriptions

def navigate_and_save_profile(driver, profile_url, company_name, employee_name, output_dir):
    try:
        logger.info(f"Navigating to profile: {profile_url}")
        driver.get(profile_url)
        human_delay(action_type='profile')
        
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
        
        sanitized_name = ''.join(c if c.isalnum() else '_' for c in employee_name)
        save_html(driver, f"{company_name}_profile_{sanitized_name}", output_dir)
    except TimeoutException:
        logger.error(f"Timeout loading profile: {profile_url}")
    except Exception as e:
        logger.error(f"Error navigating to profile {profile_url}: {str(e)}")

def human_delay(action_type='default'):
    if not delay_config.enabled:
        return
    
    delay_map = {
        'login': delay_config.login,
        'navigation': delay_config.navigation,
        'profile': delay_config.profile,
        'default': (1, 3)
    }
    delay = random.uniform(*delay_map.get(action_type, delay_map['default']))
    logger.debug(f"Delay of {delay:.2f} seconds ({action_type})")
    time.sleep(delay)

def safe_find_element(driver, by, value, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
    except TimeoutException:
        logger.warning(f"Element not found: {by}={value}")
        return None

def save_html(driver, filename, output_dir):
    html = driver.page_source
    filepath = os.path.join(output_dir, f"{filename}_{int(time.time())}.html")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    logger.info(f"HTML saved: {filepath}")