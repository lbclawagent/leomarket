## Problem:
- Data source not found because server issue or cannot understand web crawling into internal pages/link investigation
- Inaccurate data problem because of source has other minimally related data
- And playwright getting banned or blocked by secured site
- Different data signal source carries different level of confidence weight. High Data source require higher amount of data.
- Some of the govt. data are image based .pdf files which means images saved in pdf format. we need to check our pipeline .py script whether llamaindex, pypdf or other projects are set properly in the `~/.openclaw/workspace/leopump/script/` 
- 

---

## Data Source  Location:
### Dealer Pricing Signals (Bdstall, Othoba, Walton, MEL mart, Pedrollo Different Types of Pump Price Data
- Daraz.bd.com is not the only data source for water pump pricing data extraction. As alternative we need to use other specially for submersible water pump pricing:
```
[Bdstall.com](https://www.bdstall.com/water-pump/)
[Othoba.com](https://othoba.com/water-pump?orderby=0&pagesize=80)
Walton Plaza
[MEL mart BD](https://www.melmartbd.com/product-category/water-pump/)
[esmart.com.bd](https://esmart.com.bd/product-category/industrial-supplies/real-estate-industry/water-pump/?srsltid=AfmBOorqwBpMIjYzkd-NcMNmVePzg0U5OKbqnMz7EE6JDCyBRgBtv6Q-)
[gcart.com.bd](https://gcart.com.bd/category/pumps-motors)
[pedrollo](https://pedrollo.com.bd/brand/pedrollo/)
```

### NBR Import Data Source
- Actual Website to collect data:
```
https://nbr.gov.bd/publications/all-publication/eng
```
- Imports statement files are mainly pdf and they are available for every month and there are two data source `bond` and `commercial`. File naming format in the website:
```
1. Import Statment-IM-7-Bond(Month Name, Year)
2. Import Statement-IM-4-Commercial(Month Name, Year)
```

### Faostat data can be found here

```
https://www.fao.org/aquastat/en/geospatial-information/global-maps-irrigated-areas/irrigation-by-country/country/BGD

```

### BADC data source for installed irrigation base:

#### Main Links:(pdf files image based need to run - parser_pipeline.py based on llamaindex installed .venv)

|SL|Title|Report Type|Attachment Files|Publish Date|Action|
|---|---|---|---|---|---|
|1|Irrigation related Survey Report 2023-24|Irragation-Survey-Report|[](https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-badc/2024/12/0ccd7b55c5ec4aa69c3e82eeaa836545.pdf "office-badc/2024/12/0ccd7b55c5ec4aa69c3e82eeaa836545.pdf")|09-04-2025|[View](https://badc.gov.bd/pages/reports/irrigation-related-survey-report-2023-24-0f39b0-6922ddf6dbfbab28ce067764)|
|2|Irrigation related Survey Report 2022-23|Irragation-Survey-Report|[](https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-badc/2024/12/320bbcf9984c4e94aa523107e8e65bf2.pdf "office-badc/2024/12/320bbcf9984c4e94aa523107e8e65bf2.pdf")|19-02-2025|[View](https://badc.gov.bd/pages/reports/irrigation-related-survey-report-2022-23-3cc7c6-6922ddebdbfbab28ce067485)|
|3|Irrigation related Survey Report 2021-22|Irragation-Survey-Report|[](https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-badc/2024/12/04708c73ef7c4eed8840cecce44c6c5d.pdf "office-badc/2024/12/04708c73ef7c4eed8840cecce44c6c5d.pdf")|02-02-2025|[View](https://badc.gov.bd/pages/reports/irrigation-related-survey-report-2021-22-4eda04-6922dbeedbfbab28ce05c936)|
|4|Irrigation related Survey Report 2019-20|Irragation-Survey-Report|[](https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-badc/2024/12/a98bb6d485e44e938c2daaf6f404b239.pdf "office-badc/2024/12/a98bb6d485e44e938c2daaf6f404b239.pdf")|15-01-2025|[View](https://badc.gov.bd/pages/reports/irrigation-related-survey-report-2019-20-aa9b51-6922df03dbfbab28ce06cf3d)|
|5|Irrigation related Survey Report 2020-21|Irragation-Survey-Report|[](https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-badc/2024/12/878452b7fc8e4c798ede0709abcabfe1.pdf "office-badc/2024/12/878452b7fc8e4c798ede0709abcabfe1.pdf")|05-01-2025|[View](https://badc.gov.bd/pages/reports/irrigation-related-survey-report-2020-21-6335bd-6922ddb1dbfbab28ce066710)|
|6|Irrigation related Survey Report 2018-19|Irragation-Survey-Report|[](https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-badc/2024/12/ef25b41036c44fc2b7903f1793fd8ac4.pdf "office-badc/2024/12/ef25b41036c44fc2b7903f1793fd8ac4.pdf")|02-01-2025|[View](https://badc.gov.bd/pages/reports/irrigation-related-survey-report-2018-19-123105-6922de79dbfbab28ce069cb8)|
|7|Irrigation related Survey Report 2017-18|Irragation-Survey-Report|[](https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-badc/2024/12/e1a0642b427d446ba6fe8f46e5a2e3cb.pdf "office-badc/2024/12/e1a0642b427d446ba6fe8f46e5a2e3cb.pdf")|01-01-2025|[View](https://badc.gov.bd/pages/reports/irrigation-related-survey-report-2017-18-d3932c-6922dbb7dbfbab28ce05b9c6)|
#### fallback link:
#### tbsnews:
https://www.tbsnews.net/economy/corporates/badc-expands-irrigation-infrastructure-improve-water-management-1353841

##### Ministry of Bangladesh:
- https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-badc/2024/12/e1a0642b427d446ba6fe8f46e5a2e3cb.pdf
- https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-badc/2024/12/350fe4d2a38a44679d05e331221e0617.pdf

### IDCOL Solar Pump Installation Records

```
https://ndre.sreda.gov.bd/index.php?id=01&i=4&s=&ag=&di=&ps=&sg=&fs=&ob=1&submit=Search
```

### BSTI Certification / Policy Updates
```
Go find related link yourself that is needed for this project





```

### Urban Housing Permit Data (RAJUK, CDA, KDA)
- Based on the leo water pump research objective figure out first which data we needs then go to the links to download necessary data as their mounting amount data at the rajuk portal. 
```
1. [rajuk](https://rajuk.gov.bd/pages/static-pages/6922dbda933eb65569e0d00c)
2. 
```

### Industrial Expansion Announcements (Textile, Pharma)
### Source-Specific Time Window Recommendations

| Data Source                                                        | Primary Temporal Unit             | Recommended Collection Range                                       | Rationale & Alignment Logic                                                                                                                                         |
| ------------------------------------------------------------------ | --------------------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **NBR Customs / HS 8413 Import Data**                              | Monthly shipment records          | 36 months rolling (3 years) + current YTD                          | Captures full agricultural cycle repetition, policy shift detection (e.g., tariff changes), and FX volatility impact. Minimum 24 months required for CAGR baseline. |
| **BADC Installed Irrigation Base Census**                          | Annual survey + quarterly updates | Last 3 full fiscal years (July–June) + latest quarterly bulletin   | BADC reporting follows Bangladesh fiscal year. Triangulation requires multi-year trend to isolate replacement demand vs. new installation growth.                   |
| **IDCOL Solar Pump Installation Records**                          | Project completion date           | Last 24 months + active pipeline (next 6 months)                   | IDCOL subsidy rounds are batch-driven. Recent installations signal near-term demand; pipeline data informs forward-looking estimates.                               |
| **Dealer Pricing Signals (Daraz, BDStall, regional distributors)** | Daily price listings              | 90-day rolling window + seasonal peak snapshots (Nov–Jan, Mar–Apr) | Prices fluctuate sharply during Boro preparation and peak irrigation. Short window captures volatility; seasonal snapshots anchor normalization logic.              |
| **Bengali News / Local Interviews / Facebook Marketplace**         | Event-driven / ad-hoc             | 180-day rolling window, weighted by recency (exponential decay)    | Qualitative signals degrade rapidly. Apply 0.95^days decay factor in triangulation to prevent stale anecdotes from skewing estimates.                               |
| **BSTI Certification / Policy Updates**                            | Publication date                  | All records from 2020 onward + real-time monitoring                | Regulatory shifts (e.g., energy efficiency mandates) have multi-year market impact. Historical baseline required for compliance cost modeling.                      |
| **Urban Housing Permit Data (RAJUK, CDA, KDA)**                    | Quarterly approvals               | 24 months rolling + current quarter                                | Domestic pump demand lags construction permits by 3–6 months. Two-year window captures approval-to-installation pipeline.                                           |
| **Industrial Expansion Announcements (Textile, Pharma)**           | Project commissioning date        | 36 months backward + forward-looking project registry              | Industrial pump demand is project-driven. Long window captures lead time from announcement to equipment procurement.                                                |


