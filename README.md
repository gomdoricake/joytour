# JOYTOURHUB

> A web application that handles everything from tour guide expense reporting to office review, approval, and payment. After a Day Tour or Inbound Tour, the guide only needs to enter the tour code and the expenses incurred. The correct rates are applied automatically based on the guide's grade and the vehicle used, and the report is sent straight to the office. 

# Table of Contents
- [Screenshots](#screenshots)
- [Tech Stack](#tech-stack)
- [Key Features](#key-features)
- [Bonus: Google Sheet to Calendar Automation](#bonus-google-sheet-to-calendar-automation)
- [User Roles](#user-roles)
- [Payment Cycle](#payment-cycle)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)
- [Project Structure](#project-structure)

# Screenshots
> All screenshots use test data. Guide names, ABNs, contact details, and bank account numbers shown here are not real. 

### Office (Admin)
**Overview**
Shows the payable amounts for the selected weekly period (e.g. Nov.4 - Nov.10, 2026). 

* Summary cards at the top: total payable amount due (excluding super), total guide fee, total guide expenses, and total super. 
* Per-guide breakdown: each guide's number of reports, fee, expenses, super, and total, so staff can see at a glance who is owed what this week. 

![Admin Overview](/joytour/docs/admin_overview.png)

**Reports Detail List**
Lists every invoice in the selected period (e.g. 30 invoices). 
* Columns: invoice date, guide name, group code, guide fee, expense, amount due, and status. 
* Status filters: CONFIRMED, PAID, and WAITING. 
* Search by group code or guide name to quickly find a specific report. 
* Click a row to open the report detail page. 

![Admin Detail List](/joytour/docs/admin_detail_list.png)

**Guide Report Detail**
Tha page staff use to review a single report before payment. 

* Guide payment details: guide name, ABN, contact number, and bank details (BSB/account). 
* Bill To: the company the invoice is issued to. 
* Tour information: tour type (Day/Inbound), role, coach type, and passenger summary (ADT/CHD/TC). 
* Events: each day's event code and hours with its fee, plus the event subtotal (inc.GST). 
* Guide expenses: itemized expenses with the expense subtotal and the report total (inc. GST). 
* Super annuation amount, BP (fuel) records, and per-day attraction headcounts. 
* Actions: confirm (with undo), mark as pad, download PDF, print, and delete. 


![Admin Detail](/joytour/docs/admin_detail.png)

**PDF Export**
The report exported as a PDF for printing or record keeping, containing the same invoice information shown on the detail page. 

![Admin PDF](/joytour/docs/admin_pdf.png)

**Guide Fee Rates**
Where office staff manage the guide fee table. 
* Register / update form: grade, tour type (Day/Inbound), event code or hours, seat type / FIT / group, group fee, and sponsored status. 
* Rate list (e.g. 161 rates): each rate shows its conditions and fee, with Update and Delete buttons. 
* Rates are applied automatically when guides submit reports. 

![Admin Rate](/joytour//docs/admin_rate.png)

**Receipt**
Receipt images that guides attached to their expenses, stored in AWS S3, so staff can verify each expense during review. 

![Admin Receipt](/joytour/docs/admin_receipt.png)

### Guide

**My Page**
The guide's personal space. 

* Profile: initial training date, grade, birthday, contact, address, ABN, and bank account details. Changes are made through the office. 
* New report button to create a new report (cannot be edited after creation). 
* Overview: the guide's total payable amount, guide fee, and expenses. 
* Report & invoice list: filter by ALL / UNPAID / CONFIRMED / PAID and search by group code or invoice number. 

![Guide Mypage](/joytour/docs/guide_mypage.png)


**Report Summary**
The final check before submitting a report. 
* Event information: tour type, vehicle seat size, event code, report date, and the automatically calculated guide fee. 
* BP (fuel) and guide expenses with item, memo, and amount. 
* Grand total of the amount to be paid. 
* A Submit button sends the report to the office, and a link returns to edit expenses. 

![Guide Summary](/joytour/docs/guide_summary.png)


# Tech Stack
| Category | Technology | 
| Framework | Python, Django | 
| Database | PostgreSQL | 
| Infrastructure | AWS Lightsail | 
| File Storage | AWS S3 (uploaded images) | 
| Containerization | Docker | 
| Automation | Google Apps Script (Google Sheets / Google Calendar) | 


# Key Features
### 1. Automated Report Creation After Each Tour (Guide)
* When a tour ends, the guide enters the tour code and the expenses incurred during the tour. 
* Based on the tour type (Day/Inbound), tour code, the guide's grade, and the vehicle used, the applicable amounts are filled in automatically. 
* Images (e.g. receipts) can be attached to report and are stored in AWS S3. 
* The report is submitted to the office immediately. 

### 2. Personal Tour & Report Management (Guide)
* Guides can freely view and manage their own tours and reports from their own account. 

### 3. Weekly Payment Review (Office)
* Office staff can review reports for each weekly cycle, grouped by status: 
  - Payable: reports ready for payment
  - Unpaid: reports not yet paid
  - Paid: reports already paid
* Payable reports can be reviewed and confirmed, exported to PDF, and printed. 
* The Overview page provides a full view of all reports. 

### 4. Guide Fee Rates Management(Office)
* Office staff can directly register and edit the Guide Fee Rates (the rate table for tour guides). 
* Updated rates are applied to subsequent report calculations. 

#### 5. Guide Profiles & Automatic Grade Calculation (Office)
* A guide's grade is calculated automatically based on initial training completion and sponsorship status. 
* Office staff can manage each guide's contact details, ABN, and bank account. 

### 6. Guide Report Search (Office)
* Quickly find an individual guide's reports using the search function. 


# Bonus: Google Sheet to Calendar Automation
A Google Apps Script for day tour operations is included. 

1. Enter customer information into a Google Sheet. 
2. Clicke the Update Calendar button. 
3. Customer information is automatically added to the correct dates in Google Calendar, according to the conditions of each tour. 



# User Roles
| Role | Permissions | 
| --- | ---- |
| Guide | Submit expense reports; view and manage own tours and reports | 
| Office | Review and confirm reports, export PDF, print; manage fee rates; manage guide profiles and grades; search reports

# Payment Cycle
* Weekly cycle: last Wednesday through this Tuesday
* Reports within this period are classified as Payable/Unpaid/Paid. 


# Getting Started
Docker is used only for the PostgreSQL database. The Django app itself runs directly on the host with `python manage.py runserver`, so the database container container must  be running first. 

## Requirements
* Python 3.x
* Docker

### 1. Start the PostgreSQL container
```
docker run -d \
  --name tour-report-db \
  -e POSTGRES_DB=your_db \
  -e POSTGRES_USER=your_user \
  -e POSTGRES_PASSWORD=your_password \
  -p 5432:5432 \
  -v tour_report_pgdata:/var/lib/postgresql/data \
  postgres:16
```

If the container already exists, just start it: 

```
docker start tour-report-db
```

### 2. Set up the Django app
```
# Clone the repository
git clone <repository-url>
cd <project-directory>

# Create a virtual environment and install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Prepare the environment file
cp .env.example .en
```

### 3. Run migrations and start the server
```
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

# Environment Variables
Set the following in your `.env` file (adjustto match your project). The values must match the ones used when starting the PostgreSQL container. 

```
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=your-domain.com,localhost

POSTGRES_DB=your_db
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

# Deployment
* Hosted on an AWS Lightsal instance. 
* PostgreSQL runs in a Docker container on the instance; the Django app runse on the host. 
```
# Make sure the database container is running
docker start tour-report-db

# Pull the latest code and apply changes
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

# Project Structure
Adjust to match your actual structure. 

```
joyapp/
   joytour/
   |------ guidereports/            # Expense reports
   |------ guides/                  # Guide Profiles
   |------ joyadmin/                # Guide Fee Rates, payment status
   |------ joyproject/              # Django project settings
   |------ mypage/                  # Individual's reports
   |------ inbound/     
   |------ invoices/
   |------ script/
   |------ static/
   |------ staticfiles/
   |------ templates/
   |------ requirements.txt

```


# ERD
![joytourhub_erd.png](./joytourhub_erd.png)

