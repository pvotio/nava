# nava

## Overview

Nava is a Django-based web application designed for efficient and dynamic report generation, invoice processing, and more. The system leverages Django's back-end capabilities, along with additional services such as Redis and Celery for task queuing and Puppeteer for PDF generation.

## Features

- **Dynamic Report Generation**: Create, modify, and generate various reports.
- **PDF Generation**: Convert reports to PDF format using Puppeteer.
- **Task Scheduling and Management**: Utilize Celery for asynchronous task management.
- **Caching with Redis**: Enhance performance through caching mechanisms.
- **Admin Panel**: Manage reports and configurations via a custom Django admin interface.
- **RESTful API Endpoints**: Facilitate interaction with the system through REST API.


## Installation & Setup
### Clone the Repository
   ```bash
   git clone git@github.com:alimghmi/reporting-django.git
   cd reporting-django
   ```
### Environment Setup
   - Copy sample.env and sample.db.env to .env and .db.env
   - Update the environment variables in these files as per your setup.
### Docker Setup
   - Run `docker compose -f docker-compose.yml up` to build and start the containers.
   - The application should now be running with all its services.
### Admin user setup
   - Admin user must be setup to access the management dashboard.
   - Run `docker compose -f docker-compose-prod.yml exec web /bin/bash` to open the interactive shell of django container.
   - Run `python manage.py createsuperuser`.
  

## Usage

### Generating Reports
- Navigate to the admin panel at http://localhost:8000/service/nava/portal/.
- Login with superuser credentials you created earlier.
- Create or modify reports and generate them in real-time or schedule them using Celery tasks.

### API Endpoints
Utilize the RESTful API endpoints for interacting with the report system from external platforms/services programmatically.

### Connection Strings
- *Postgres, MariaDB and MySQL* 
   - host=[db_host];user=[db_user];password=[db_password];database=[db_name];port=[db_port]
- *MSSQL*
   - DRIVER={ODBC Driver 17 for SQL Server};SERVER=[db_host];DATABASE=[db_name];UID=[db_user];PWD=[db_password];MARS_Connection=yes;
