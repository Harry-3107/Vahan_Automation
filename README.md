# Automated Market Sales Analysis

This project automates the end-to-end process of extracting vehicle market sales data from the VAHAN dashboard and combines it with dummy Sundaram Finance (SF) branch data to analyze state-wise and district-wise market share using MySQL and Power BI.

---

## 🚀 Objective

To automate the scraping, integration, and analysis of market sales data and branch mappings across multiple states for strategic business insights.

---

## 📌 Key Features

- 🔍 **Web Scraping**:
  - Extracts total market sales data (vehicle-wise) from the **VAHAN Dashboard**
  - Scrapes **Sundaram Finance** official website to get a list of branches and their corresponding districts

- 🗂️ **Data Mapping**:
  - Uses manually created CSVs to map each RTO and SF branch to its corresponding district

- 📊 **Aggregation**:
  - Aggregates RTO-wise sales data to the **district level**
  - Computes **branch-wise sales** using dummy logic

- 🛢️ **Database Integration**:
  - Dumps the processed data into a **MySQL database** using `mysql-connector-python`
  - Creates normalized tables for RTOs, Branches, Districts, and Sales

- 📈 **Visualization**:
  - Data is queried from MySQL and visualized in **Power BI**
  - Dashboards include district-wise sales distribution, SF branch market share, and other insights

---

## 🛠️ Technologies Used

- Python 3
- Selenium (for scraping)
- Pandas
- MySQL + MySQL Connector
- Power BI (for dashboard and reporting)

---

## 🗃️ Folder Structure

Vahan Automation Project/<br>
├── Phase 2/<br>
│ ├── andhra.py<br>
│ ├── kerala.py<br>
│ ├── karnataka.py<br>
│ ├── tn.py<br>
├── RTO_District_Mapping/<br>
│ ├── Andhra_Pradesh_RTO_District_Mapping.csv<br>
│ ├── Karnataka_RTO_District_Mapping.csv<br>
│ ├── Kerala_RTO_District_Mapping.csv<br>
│ ├── Tamil_Nadu_RTO_District_Mapping.csv<br>
├── SF_Branch_District_Mapping/<br>
│ ├── Andhra_Pradesh_SF_Branch_District_Mapping.csv<br>
│ ├── Karnataka_SF_Branch_District_Mapping.csv<br>
│ ├── Kerala_SF_Branch_District_Mapping.csv<br>
│ ├── Tamil_Nadu_SF_Branch_District_Mapping.csv<br>
├── District_Data_Aggregation.py<br>
├── DayWiseData.py<br>
├── MySQL_Data_Dumping.py<br>
├── Market Share Analysis.pbix<br>
├── README.md<br>
├── SFDistrict.py<br>
├── SF_Branch_Dummy_Data.py<br>

---

## 📄 Requirements

```bash
pip install selenium pandas mysql-connector-python
```

---

## ▶️ How to Run

1. Run `SFDistrict.py` to fetch the list of all branches from the SF website.  
2. Run the VAHAN scraper script to get vehicle sales data across all RTOs.  
3. Use `District_Aggregation` script to:
    - Clean the scraped data  
    - Map RTOs and branches to districts using manual CSVs  
    - Aggregate sales at the **district** and **branch** level  
4. Load the final aggregated dataset into **MySQL** using the provided script.  
5. Open the **Power BI** report and connect it to your MySQL instance.

---

## 📊 Power BI Report Highlights

- State-wise and district-wise vehicle sales  
- SF Branch market penetration by district  
- Comparison between SF branches and total market size  
- Filtered views for selected states

