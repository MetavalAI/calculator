🚀 Formula Calculator System

A dynamic Flask-based Formula Calculator web application that allows users to create custom engineering and mathematical formulas with unit conversion support, calculation history, and Excel export functionality.

✨ Features
✅ Dynamic Formula Creation
✅ Variable-Based Calculations
✅ Unit Conversion System
✅ Common Unit Dropdown Support
✅ Scientific Formula Support (sqrt, powers, etc.)
✅ Calculation History
✅ Excel Export (.xlsx)
✅ Formula Edit/Delete
✅ Responsive UI using Bootstrap
✅ Cv (Flow Coefficient) Calculator Support
🖥️ Tech Stack
Backend: Flask (Python)
Frontend: HTML, CSS, Bootstrap, JavaScript
Database: SQLite + SQLAlchemy
Excel Export: Pandas + OpenPyXL
📂 Project Structure
calculator/
│
├── app/
│   ├── templates/
│   ├── static/
│   ├── models.py
│   ├── routes.py
│   ├── services.py
│   ├── utils.py
│   ├── unit_conversions.py
│   └── __init__.py
│
├── exports/
├── instance/
├── run.py
├── requirements.txt
└── README.md
⚙️ Installation
1️⃣ Clone Repository
git clone https://github.com/MetavalT/calculator.git
2️⃣ Move Into Project
cd calculator
3️⃣ Create Virtual Environment
python -m venv venv
4️⃣ Activate Virtual Environment
Windows
venv\Scripts\activate
Linux/Mac
source venv/bin/activate
📦 Install Dependencies
pip install -r requirements.txt
▶️ Run Project
python run.py

Server will start on:

http://127.0.0.1:5000
🧮 Example Cv Formula

Formula:

Cv=Q
DP
	​

SG
	​

	​


Variables
Variable	Meaning
Q	Flow Rate
SG	Specific Gravity
DP	Pressure Drop
🔁 Supported Unit Conversions
Flow Rate
GPM
LPM
m3/hr
Pressure
PSI
Bar
kPa
Speed
km/hr
m/s
Time
hr
min
sec
📊 Excel Export

The application automatically exports:

Formula-wise sheets
Values used
Answers
Created date & time

into:

exports/calculations.xlsx
📸 Screenshots
Home Page
Formula listing
Recent calculations
Navigation system
Calculator Page
Dynamic input fields
Common unit selector
Live calculation results
🛠️ Future Improvements
Dynamic Result Unit Detection
Formula Validation Engine
User Authentication
PDF Export
Advanced Engineering Calculators
Graph Plotting Support
👨‍💻 Author

Developed by:

Torque🔥

GitHub:

MetavalT Calculator Repository