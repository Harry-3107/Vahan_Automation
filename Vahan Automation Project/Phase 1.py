# Phase 1 
# State = TN ; RTO = Ambattur 
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# === Setup Chrome WebDriver ===
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

# === Open the Vahan report page ===
driver.get("https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml")

# === Universal Dropdown Selector ===
def click_dropdown_and_select(current_value_text, option_text, retries=3):
    for attempt in range(retries):
        try:
            # 1. Locate label
            label = wait.until(EC.presence_of_element_located((
                By.XPATH,
                f"//label[contains(@class, 'ui-selectonemenu-label') and normalize-space(text())='{current_value_text}']"
            )))

            # 2. Ascend to the container
            container = label.find_element(By.XPATH, "./ancestor::div[contains(@class, 'ui-selectonemenu')]")

            # 3. If not already expanded, click trigger
            if container.get_attribute("aria-expanded") != "true":
                trigger = container.find_element(By.CLASS_NAME, "ui-selectonemenu-trigger")
                driver.execute_script("arguments[0].scrollIntoView(true);", trigger)
                time.sleep(0.2)
                trigger.click()
                print(f"[Info] Opened dropdown: '{current_value_text}'")
                time.sleep(0.3)
            else:
                print(f"[Skip] Dropdown already open: '{current_value_text}'")

            # 4. Select the desired option
            option_xpath = f"//li[@role='option' and contains(normalize-space(.), '{option_text}')]"
            option = wait.until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
            driver.execute_script("arguments[0].scrollIntoView(true);", option)
            time.sleep(0.2)
            option.click()
            print(f"[\u2713] Selected: '{option_text}'")

            # 5. Blur to close dropdown
            driver.find_element(By.TAG_NAME, "body").click()
            time.sleep(0.5)
            return

        except Exception as e:
            print(f"[Retry {attempt+1}] Failed to select '{option_text}' from '{current_value_text}': {e}")
            time.sleep(1)

    driver.save_screenshot(f"dropdown_error_{current_value_text.replace(' ', '_')}.png")
    raise Exception(f"[X] Failed to select '{option_text}' from '{current_value_text}' after {retries} attempts.")

# === Perform Dropdown Selections ===
click_dropdown_and_select("Actual Value", "In Crore")
click_dropdown_and_select("All Vahan4 Running States (35/36)", "Tamil Nadu(148)")

# Wait for RTOs to load
wait.until(EC.presence_of_element_located((By.XPATH, "//li[contains(text(), 'AMBATTUR RTO')]")))
click_dropdown_and_select("All Vahan4 Running Office(148/148)", "AMBATTUR RTO - TN612( 07-JUN-2018 )")

click_dropdown_and_select("Vehicle Category Group", "Vehicle Category")
wait.until(EC.presence_of_element_located((By.XPATH, "//li[contains(text(), 'Maker')]")))
click_dropdown_and_select("Vehicle Class", "Maker")

click_dropdown_and_select("Calendar Year", "Financial Year")
wait.until(EC.presence_of_element_located((By.XPATH, "//li[contains(text(), '2025-2026')]")))
click_dropdown_and_select("Select Year", "2025-2026")

# === Click Refresh Button ===
try:
    refresh_button = wait.until(EC.element_to_be_clickable((
        By.XPATH, "//button/span[contains(text(),'Refresh')]/.."
    )))
    driver.execute_script("arguments[0].scrollIntoView(true);", refresh_button)
    time.sleep(0.5)
    refresh_button.click()
    print("[\u2713] Clicked Refresh")
except Exception as e:
    print("[X] Could not click Refresh:", e)
    driver.save_screenshot("refresh_error.png")
time.sleep(15)

# === Click Export Button ===
def click_export_button_dynamically(driver):
    try:
        # 1. Locate the <img> with title 'Download EXCEL file'
        export_icon = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH, "//img[@title='Download EXCEL file']"
            ))
        )

        # 2. Ascend to the parent <a> tag (the actual clickable link)
        export_link = export_icon.find_element(By.XPATH, "./ancestor::a")

        # 3. Scroll into view
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", export_link)
        time.sleep(0.5)

        # 4. Try clicking the <a> tag
        try:
            export_link.click()
            print("[✓] Export link clicked (normal click).")
        except Exception:
            driver.execute_script("arguments[0].click();", export_link)
            print("[✓] Export link clicked (JS fallback).")

    except Exception as e:
        print("[X] Failed to locate or click export link:", e)
        driver.save_screenshot("export_click_error.png")
        raise

click_export_button_dynamically(driver)

# Wait to observe or download results
time.sleep(15)
driver.quit()
