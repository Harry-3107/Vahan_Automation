import time
import os
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

# Initialize WebDriver
driver = webdriver.Chrome()
driver.maximize_window()
driver.get("https://www.sundaramfinance.in/")
wait = WebDriverWait(driver, 20)

# Close popup if it appears
wait.until(EC.presence_of_element_located((By.NAME, "sundaram_01022025")))
wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Close"]')))
driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Close"]').click()

# States to process
states = ["Kerala", "Karnataka", "Tamil Nadu", "Andhra Pradesh"]

# Create output folder
output_folder = "SF_Branch_District_Mapping"
os.makedirs(output_folder, exist_ok=True)

for state in states:
    print(f"\n🔄 Selecting State: {state}")
    
    # Select the state
    wait.until(EC.presence_of_element_located((By.ID, "ddlBLCtrlState")))
    state_dropdown_element = driver.find_element(By.ID, "ddlBLCtrlState")
    driver.execute_script("arguments[0].scrollIntoView(true);", state_dropdown_element)
    Select(state_dropdown_element).select_by_visible_text(state)

    # Wait for districts to load
    wait.until(lambda d: len(Select(d.find_element(By.ID, "ddlBLCtrlLocation")).options) > 1)
    time.sleep(1)

    # Get list of districts dynamically
    district_dropdown_element = driver.find_element(By.ID, "ddlBLCtrlLocation")
    district_dropdown = Select(district_dropdown_element)
    district_options = [opt.text.strip() for opt in district_dropdown.options if opt.text.strip()]
    district_list = district_options[1:]  # skip first "Select" option

    branch_district = []

    for district in district_list:
        print(f"District: {district}")
        
        # Refresh the district dropdown each time
        wait.until(EC.presence_of_element_located((By.ID, "ddlBLCtrlLocation")))
        district_dropdown_element = driver.find_element(By.ID, "ddlBLCtrlLocation")
        district_dropdown = Select(district_dropdown_element)

        try:
            district_dropdown.select_by_visible_text(district)
        except:
            print(f"Skipping unavailable district: {district}")
            continue

        wait.until(EC.presence_of_element_located((By.ID, "ddlBLCtrlBranch")))
        time.sleep(1)

        # Fetch all branches
        branches = driver.find_elements(By.CLASS_NAME, "branch-locator")
        for branch_elem in branches:
            try:
                p_tags = branch_elem.find_elements(By.TAG_NAME, "p")
                branch_name = p_tags[0].find_element(By.TAG_NAME, "strong").text.strip()
                branch_district.append({
                    "Branch": branch_name,
                    "District": district
                })
            except:
                continue

        time.sleep(1)

    # Save to CSV
    filename = os.path.join(output_folder, state.replace(" ", "_") + "_Branch_District_Mapping.csv")
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ["Branch", "District"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(branch_district)

    print(f"Saved: {filename}")
    time.sleep(2)

driver.quit()
