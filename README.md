# Simple CRM

Simple CRM system built with FastAPI, SQLite, HTML, CSS and Jinja2 templates.

## Features

- Clients management
- Deals management
- Tasks management
- Client search
- Deal status filter
- Client card with related deals and tasks
- CRM statistics
- SQLite database
- Web interface

## Project structure

```text
PyCharmMiscProject
├── main.py
├── auth.py
├── database.py
├── models.py
├── crm.db
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
├── routes
│   ├── __init__.py
│   ├── clients.py
│   ├── deals.py
│   ├── tasks.py
│   ├── stats.py
│   └── web.py
├── templates
│   ├── home.html
│   ├── login.html
│   ├── clients.html
│   ├── client_full.html
│   ├── confirm_delete_client.html
│   ├── error.html
│   ├── deals.html
│   ├── tasks.html
│   ├── stats.html
│   ├── edit_client.html
│   └── edit_deal.html
└── static
    └── style.css
```

## Installation

Install project dependencies:

```bash
pip install -r requirements.txt
```
## Environment variables

Create a `.env` file in the project root based on `.env.example`:

```text
CRM_USERNAME=admin
CRM_PASSWORD=your_secure_password

```text
http://127.0.0.1:8000/web
```

## Run project

Start the FastAPI server for development:

```bash
python -m uvicorn main:app --reload
```

Or start the project using `run.py`:

```bash
python run.py
```

Then open the CRM web interface in browser:

```text
http://127.0.0.1:8000/web
```



## API documentation

FastAPI automatically generates API documentation.

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Main API groups:

```text
/clients
/deals
/tasks
/stats
```

## Database

The project uses SQLite database:

```text
crm.db
```

Database tables:

```text
clients
deals
tasks
```

The database is initialized automatically when the application starts.

## Main pages

```text
/web
/web/clients
/web/deals
/web/tasks
/web/stats
```

## How to stop the server

In the PyCharm terminal press:

```text
Control + C
```