# CrewConnect – Employee Management System

CrewConnect is a web-based Employee Management System developed using Python and Django to simplify HR operations and employee management. It provides a centralized platform for managing employee information, leave requests, and HR activities.

## Features

- **Employee Management:** Add, view, update, and manage employee information.
- **HR Dashboard:** Provides an interface for HR-related operations.
- **Employee Dashboard:** Allows employees to access their dashboard and relevant information.
- **Leave Management:** Employees can submit leave requests, and HR can review and approve or reject them.
- **Leave Calendar:** View and manage leave schedules.
- **Employee Profiles:** Access and manage employee profile information.
- **Password Reset:** Supports password reset functionality.

## Technologies Used

- **Backend:** Python, Django
- **Frontend:** HTML, CSS, Bootstrap, JavaScript
- **Database:** SQLite (development configuration)
- **Version Control:** Git and GitHub

## Project Structure

```text
CrewConnect/
├── CrewConnect/       # Django project configuration
├── employee/          # Employee-related functionality
├── hr/                # HR-related functionality
├── static/             # CSS and static assets
├── templates/          # HTML templates
├── manage.py           # Django management utility
└── README.md           # Project documentation
```

## Installation and Setup

### Prerequisites

- Python 3.x
- pip
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/bhuvan098/CrewConnect.git
cd CrewConnect
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Ensure that the `requirements.txt` file is included in the repository and contains the project's required Python packages.

### 4. Apply Database Migrations

```bash
python manage.py migrate
```

### 5. Start the Development Server

```bash
python manage.py runserver
```

Open your browser and visit:

http://127.0.0.1:8000/

## Security

- Keep Django secret keys and credentials out of source control.
- Use environment variables for sensitive configuration.
- Configure production security settings before deployment.

## Future Enhancements

- Deploy the application to a public hosting platform.
- Add automated testing.
- Enhance reporting and analytics.
- Improve production security and scalability.

## Author

**Bhuvan Bestha**

GitHub: [bhuvan098](https://github.com/bhuvan098)

## License

This project is available for educational and portfolio purposes. Add a formal open-source license if you intend to grant specific reuse and distribution permissions.
