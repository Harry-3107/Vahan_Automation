import time
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException

# === Setup Chrome WebDriver ===
download_dir = os.path.abspath("Tamil_Nadu_Files")
os.makedirs(download_dir, exist_ok=True)

options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
    "profile.default_content_settings.popups": 0
}
options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(options=options)
driver.maximize_window()
driver.get("https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml")
wait = WebDriverWait(driver, 20)

# === Robust Dropdown Selector ===
def click_dropdown_and_select(current_value_text, option_text, retries=3):
    for attempt in range(retries):
        try:
            print(f"[Attempt {attempt+1}] Trying to locate dropdown for: '{current_value_text}'")
            dropdowns = driver.find_elements(By.CLASS_NAME, "ui-selectonemenu")
            matched_dropdown = None
            for dropdown in dropdowns:
                try:
                    label = dropdown.find_element(By.CLASS_NAME, "ui-selectonemenu-label")
                    if normalize_spaces(label.text) == normalize_spaces(current_value_text):
                        matched_dropdown = dropdown
                        break
                except (NoSuchElementException, StaleElementReferenceException) as inner_e:
                    continue

            if not matched_dropdown:
                raise NoSuchElementException(f"Dropdown with label '{current_value_text}' not found.")

            trigger = matched_dropdown.find_element(By.CLASS_NAME, "ui-selectonemenu-trigger")
            driver.execute_script("arguments[0].scrollIntoView(true);", trigger)
            time.sleep(0.3)
            trigger.click()
            print(f"[Info] Opened dropdown: '{current_value_text}'")
            time.sleep(1)
            options_list = driver.find_elements(By.XPATH, "//ul[contains(@id, '_items')]/li[@role='option']")
            print("[Debug] Elements Found")
            time.sleep(1)
            for opt in options_list:
                if normalize_spaces(option_text) in normalize_spaces(opt.text):
                    driver.execute_script("arguments[0].scrollIntoView(true);", opt)
                    time.sleep(0.3)
                    opt.click()
                    print(f"[✓] Selected: '{option_text}'")
                    driver.find_element(By.TAG_NAME, "body").click()
                    time.sleep(0.5)
                    return

            raise NoSuchElementException(f"Option '{option_text}' not found in dropdown '{current_value_text}'")

        except (NoSuchElementException, StaleElementReferenceException, TimeoutException) as e:
            print(f"[Retry {attempt+1}] {type(e).__name__} occurred at line {e.__traceback__.tb_lineno}: {e}")
            time.sleep(1)
        except Exception as e:
            print(f"[Retry {attempt+1}] Unexpected error at line {e.__traceback__.tb_lineno}: {type(e).__name__} - {e}")
            time.sleep(1)

    driver.save_screenshot(f"dropdown_error_{current_value_text.replace(' ', '_')}.png")
    raise Exception(f"[X] Failed to select '{option_text}' from '{current_value_text}' after {retries} attempts.")

# === Export Button ===
def click_export_button_dynamically(driver):
    try:
        export_icon = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//img[@title='Download EXCEL file']"))
        )
        export_link = export_icon.find_element(By.XPATH, "./ancestor::a")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", export_link)
        time.sleep(0.5)
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

# === Rename File ===
def rename_latest_download(download_dir, state, rto_name):
    try:
        files = [f for f in os.listdir(download_dir) if f.endswith('.xls') or f.endswith('.xlsx')]
        if not files:
            print("[X] No downloaded Excel file found.")
            return
        full_paths = [os.path.join(download_dir, f) for f in files]
        latest_file = max(full_paths, key=os.path.getmtime)
        state_safe = state.replace(" ", "_").replace("(", "").replace(")", "")
        rto_safe = rto_name.split(" - ")[0].replace(" ", "_")
        new_name = f"{state_safe}_{rto_safe}.xlsx"
        new_path = os.path.join(download_dir, new_name)
        os.rename(latest_file, new_path)
        print(f"[✓] Renamed '{latest_file}' → '{new_name}'")
    except Exception as e:
        print(f"[X] Failed to rename downloaded file: {e}")
def normalize_spaces(s):
    return re.sub(r'\s+', ' ', s.strip())

# === Start Automation ===
click_dropdown_and_select("Actual Value", "Actual Value")
click_dropdown_and_select("All Vahan4 Running States (35/36)", "Tamil Nadu(148)")
wait.until(EC.presence_of_element_located((By.XPATH, "//li[contains(text(), 'TN')]")))
#click_dropdown_and_select("All Vahan4 Running Office(68/68)", "All Vahan4 Running Office(68/68)")

try:
    rto_list_items = driver.find_elements(By.CSS_SELECTOR, "#selectedRto_items li")
    rto_names = [item.get_attribute("data-label") for item in rto_list_items if item.get_attribute("data-label")]
    print("\n=== RTO Branches ===")
    for idx, rto in enumerate(rto_names, start=1):
        print(f"{idx:02d}. {rto}")
except Exception as e:
    print(f"[X] Failed to extract RTO names: {e}")

temp = True
for i in range(len(rto_names) - 1):
    click_dropdown_and_select(rto_names[i], rto_names[i + 1])

    if temp:
        click_dropdown_and_select("Vehicle Category Group", "Vehicle Category")
        wait.until(EC.presence_of_element_located((By.XPATH, "//li[contains(text(), 'Maker')]")))
        click_dropdown_and_select("Vehicle Class", "Maker")
        click_dropdown_and_select("Calendar Year", "Financial Year")
        wait.until(EC.presence_of_element_located((By.XPATH, "//li[contains(text(), '2025-2026')]")))
        click_dropdown_and_select("Select Year", "2025-2026")
        temp = False

    try:
        refresh_button = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//button/span[contains(text(),'Refresh')]/.."
        )))
        driver.execute_script("arguments[0].scrollIntoView(true);", refresh_button)
        time.sleep(0.5)
        refresh_button.click()
        print("[✓] Clicked Refresh")
    except Exception as e:
        print("[X] Could not click Refresh:", e)
        driver.save_screenshot("refresh_error.png")

    time.sleep(10)
    click_export_button_dynamically(driver)
    time.sleep(2)
    rename_latest_download(download_dir, "Tamil_Nadu", rto_names[i + 1])
    time.sleep(5)

time.sleep(5)
driver.quit()
