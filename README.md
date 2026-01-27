# LITReview - Book Review Application

## Description
This project is a web application developed with Django. It allows a community of users to share their opinions on books.

Users can:
* Ask for a review by creating a Ticket.
* Post a Review in response to a ticket.
* Follow other users to see their activity in the Feed.
* Block users to stop seeing their content.

This project was developed as part of the OpenClassrooms Python Developer path (Project 9).

## Technologies Used
* **Language:** Python 3
* **Framework:** Django
* **Database:** SQLite
* **Frontend:** HTML5, CSS3

## Installation Guide

Follow these steps to run the project locally on your machine.

### 1. Prerequisite
Make sure you have Python installed on your computer.

### 2. Clone the repository
Download the code or clone the repository using Git:
```bash
git clone https://github.com/Mnr04/OCLITReview.git
cd oclitreview
```

## 3.Create a Virtual Environment
```bash
python3 -m venv env
```

## 4. Activate the virtual environment
On windows
```bash
env\Scripts\activate
```

On Mac
```bash
source env/bin/activate
```

## 5. Install Dependencies
```bash
pip install -r requirements.txt
```

## 6. Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## 7. Configuration

This project uses local configuration variables for security purposes (SECRET_KEY).
Since this file is ignored by Git, you must create it manually for the project to run.

1.  In the `litrevu/` folder (at the same level as `settings.py`), create a file named `local_settings.py`.
2.  Add the following content:

```python
# litrevu/local_settings.py
SECRET_KEY = 'enter-your-random-secret-key-here'
DEBUG = True
```

## 8. Run the server
```bash
python manage.py runserver
```

## 9. You can now access the website in your browser at this address
http://127.0.0.1:8000/

## 10. Generate Flake8 Report (Optional)

To generate the code quality report:
```bash
flake8 --format=html --htmldir=flake8_rapport
```

