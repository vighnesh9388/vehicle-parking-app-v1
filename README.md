# 🚗 Park-Karo!
**Park-Karo!** Is a **Parking Lot Management System** that allows users to view availability, search, and book parking spots in a parking lot of their choice, along with their parking history. The app also has a separate dashboard for Admin that allows them to manage lots, monitor spot usage, search lots or users, view user details and analyze revenue/lot statistics.   


![image](https://github.com/user-attachments/assets/0e862cb7-dc59-4627-9f44-e04f1c241f6c) ![image](https://github.com/user-attachments/assets/634b5afc-a614-421a-9e9f-66970895859f)

## Technologies Used

- HTML/CSS/JavaScript

- Flask (web framework)

- SQLite (for database)

- Flask-SQLAlchemy (ORM for database)

- Jinja2 (templating engine in Flask)

- Werkzeug (password hashing and verification)

- Bootstrap 5 (UI framework)

- Chart.js (for rendering charts)


## How to Run

1. Create a virtual environment and activate it:

```
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Mac/Linux
```

2. Install dependencies:

```
pip install -r requirements.txt
```

3. Run the app:

```
flask run --debug
```

## Admin Credentials

- **Email:** admin@email.com
- **Password:** admin

## Issues Encountered and Fixes

- Replaced hard deletion of parking lots with soft deletion using an `is_active` flag in the `Lot` model to avoid crashes in user reservation history.
- Added `was_occupied` flag in the `Spot` model to prevent deletion of spots that have been previously used, which would otherwise break reservation records.
