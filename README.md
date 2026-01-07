# OC_LITReview

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
Make sure you have **Python** installed on your computer.

### 2. Clone the repository
Download the code or clone the repository using Git:
```bash
git clone https://github.com/Mnr04/OC_LITReview.git
cd oc_litreview
```

## 3.Create a Virtual Environment
```bash
python -m venv env
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

## 7. Run the server
```bash
python manage.py runserver
```

You can now access the website in your browser at this adress --> 



