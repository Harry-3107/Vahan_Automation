# Phase 1
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
#driver.maximize_window()
driver.get("https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml")

wait = WebDriverWait(driver, 20)
body = wait.until(EC.element_to_be_clickable((By.TAG_NAME, "body")))

# Step 1: Select "Actual Value"
type_dropdown = wait.until(EC.element_to_be_clickable((By.ID, "j_idt31_label")))
type_dropdown.click()
type_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[@data-label='Actual Value']")))
type_option.click()

body.click()

# Step 2: Select State
state_dropdown = wait.until(EC.element_to_be_clickable((By.ID, "j_idt41_label")))
state_dropdown.click()
state_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[@data-label='Tamil Nadu(148)']")))
state_option.click()

# Wait for RTOs to load
wait.until(EC.presence_of_element_located((By.XPATH, "//li[contains(text(), 'AMBATTUR RTO')]")))

# Step 3: Select RTO
rto_dropdown = wait.until(EC.element_to_be_clickable((By.ID, "selectedRto_label")))
rto_dropdown.click()
rto_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[contains(@data-label, 'All Vahan4 Running Office(148/148)')]")))
rto_option.click()
wait.until(EC.invisibility_of_element_located((By.XPATH, "//li[contains(@id,'selectedRto_')]")))

# Step 4: Select X-axis → Norms
xaxis_dropdown = wait.until(EC.element_to_be_clickable((By.ID, "xaxisVar_label")))
xaxis_dropdown.click()
xaxis_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[@data-label='Vehicle Category']")))
xaxis_option.click()

# Step 5: Select Y-axis -> Maker
wait.until(EC.presence_of_element_located((By.XPATH, "//li[contains(text(), 'State')]")))
yaxis_dropdown = wait.until(EC.element_to_be_clickable((By.ID, "yaxisVar_label")))
yaxis_dropdown.click()
yaxis_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[@data-label='Maker']")))
yaxis_option.click()

# Step 6: Select Year Type -> Financial Year
yrtype_dropdown = wait.until(EC.element_to_be_clickable((By.ID, "selectedYearType_label")))
yrtype_dropdown.click()
yrtype_chosen = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[@data-label='Financial Year']")))
yrtype_chosen.click()

# Step 7: Select Year -> 2025-2026
wait.until(EC.presence_of_element_located((By.XPATH, "//li[contains(text(), '2025-2026')]")))
yr_dropdown = wait.until(EC.element_to_be_clickable((By.ID, "selectedYear_label")))
yr_dropdown.click()
yr_chosen = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[@data-label='2025-2026']")))
yr_chosen.click()

refresh_button = wait.until(EC.element_to_be_clickable((By.ID, "j_idt72")))
refresh_button.click()

body.click()

# Wait for the table to appear
wait.until(EC.presence_of_element_located((By.ID, "vchgroupTable")))

# Wait and click export button
try:
    export_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a#vchgroupTable\\:xls")))
    driver.execute_script("arguments[0].click();", export_button)
    print("Export clicked.")
except Exception as e:
    print(" Export button not found or clickable.")
    driver.save_screenshot("export_failed.png")
    raise

# Keep the browser open for download
time.sleep(20)
