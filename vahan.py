import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    StaleElementReferenceException,
    ElementClickInterceptedException,
    TimeoutException,
    ElementNotInteractableException
)

# === Set download directory ===
download_dir = os.path.abspath("downloads")
os.makedirs(download_dir, exist_ok=True)

# === Configure Chrome Options ===
options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
    "profile.default_content_settings.popups": 0
}
options.add_experimental_option("prefs", prefs)
# Initialize WebDriver
driver = webdriver.Chrome(options=options)
driver.maximize_window()
driver.get("https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml")
wait = WebDriverWait(driver, 20)

# Utility function to click dropdown and select an option with retries
def click_dropdown_and_select(dropdown_id, panel_id, option_xpath, expected_text=None, retries=3):
    for attempt in range(retries):
        try:
            dropdown = wait.until(EC.presence_of_element_located((By.ID, dropdown_id)))
            wait.until(EC.element_to_be_clickable((By.ID, dropdown_id)))
            driver.execute_script("arguments[0].scrollIntoView(true);", dropdown)
            time.sleep(0.3)
            dropdown.click()
            time.sleep(0.3)

            wait.until(EC.presence_of_element_located((By.ID, panel_id)))
            wait.until(EC.presence_of_element_located((By.XPATH, option_xpath)))
            option = driver.find_element(By.XPATH, option_xpath)
            driver.execute_script("arguments[0].scrollIntoView(true);", option)
            time.sleep(0.3)
            option.click()

            wait.until(EC.invisibility_of_element_located((By.ID, panel_id)))

            if expected_text:
                label_xpath = f"//label[@id='{dropdown_id}' and contains(text(), '{expected_text}')]"
                wait.until(EC.presence_of_element_located((By.XPATH, label_xpath)))
            return
        except (StaleElementReferenceException, ElementClickInterceptedException, TimeoutException, ElementNotInteractableException) as e:
            print(f"[Retry {attempt + 1}] Issue encountered: {e}. Retrying...")
            time.sleep(1)
    raise Exception(f"Failed to select option '{expected_text}' after {retries} attempts.")

# Step 1: Select "Actual Value"
click_dropdown_and_select("j_idt31_label", "j_idt31_panel", "//li[@data-label='Actual Value']", "Actual Value")

# Step 2: Select State → Tamil Nadu
click_dropdown_and_select("j_idt39_label", "j_idt39_panel", "//li[@data-label='Tamil Nadu(148)']", "Tamil Nadu")
wait.until(EC.presence_of_element_located((By.XPATH, "//li[contains(text(), 'AMBATTUR RTO')]")))

# Step 3: Select RTO → AMBATTUR
click_dropdown_and_select("selectedRto_label", "selectedRto_panel", "//li[contains(@data-label, 'AMBATTUR RTO - TN612')]", "AMBATTUR")

# Step 4: X-axis → Vehicle Category
click_dropdown_and_select("xaxisVar_label", "xaxisVar_panel", "//li[@data-label='Vehicle Category']", "Vehicle Category")
wait.until(EC.presence_of_element_located((By.XPATH, "//li[contains(text(), 'Maker')]")))

# Step 5: Y-axis → Maker
click_dropdown_and_select("yaxisVar_label", "yaxisVar_panel", "//li[@data-label='Maker']", "Maker")

# Step 6: Year Type → Financial Year
wait.until(EC.element_to_be_clickable((By.ID, "selectedYearType_label")))
click_dropdown_and_select("selectedYearType_label", "selectedYearType_panel", "//li[@data-label='Financial Year']", "Financial Year")

# Step 7: Year → 2025-2026
wait.until(EC.presence_of_element_located((By.XPATH, "//li[contains(text(), '2025-2026')]")))
click_dropdown_and_select("selectedYear_label", "selectedYear_panel", "//li[@data-label='2025-2026']", "2025-2026")

# Step 8: Click Refresh and wait for table update
table = wait.until(EC.presence_of_element_located((By.ID, "vchgroupTable")))

# Click Refresh
refresh_button = wait.until(EC.element_to_be_clickable((By.ID, "j_idt71")))
driver.execute_script("arguments[0].scrollIntoView(true);", refresh_button)
time.sleep(0.5)
refresh_button.click()
time.sleep(10)

# STEP 10: Click Export Button (Excel icon)
def click_export_button(driver):
    try:
        export_button = driver.find_element(By.ID, "groupingTable:j_idt85")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", export_button)
        time.sleep(0.5)
        try:
            export_button.click()
            print("Export button clicked (normal click).")
        except Exception:
            driver.execute_script("arguments[0].click();", export_button)
            print("Export button clicked (JS click fallback).")
    except Exception as e:
        print("Failed to locate or click Export button:", e)
        driver.save_screenshot("export_click_error.png")
        raise

try:
    click_export_button(driver)
except Exception:
    raise

# Keep browser open to allow download
time.sleep(20)
