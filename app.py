from flask import Flask, render_template, request, redirect, jsonify
import csv
import os
from datetime import datetime, timedelta

app = Flask(__name__)

CSV_FILE = "patients.csv"


# ============================================================
# CONFIGURATION
# ============================================================

# Hospital working hours
START_TIME = "09:00"
END_TIME = "13:00"

# Each appointment takes 30 minutes
SLOT_DURATION = 30


# ============================================================
# PRIORITY CALCULATION
# ============================================================

def calculate_priority(severity):

    priority = {
        "Critical": 100,
        "Severe": 80,
        "Moderate": 60,
        "Mild": 40,
        "Routine": 20
    }

    return priority.get(severity, 0)


# ============================================================
# CSV INITIALIZATION
# ============================================================

def initialize_csv():

    if not os.path.exists(CSV_FILE):

        with open(CSV_FILE, "w", newline="") as file:

            writer = csv.writer(file)

            writer.writerow([
                "patient_id",
                "name",
                "age",
                "gender",
                "phone",
                "disease",
                "severity",
                "priority",
                "appointment_date",
                "appointment_time",
                "status"
            ])


# ============================================================
# READ PATIENTS
# ============================================================

def read_patients():

    initialize_csv()

    patients = []

    with open(CSV_FILE, "r", newline="") as file:

        reader = csv.DictReader(file)

        for row in reader:
            patients.append(row)

    return patients


# ============================================================
# WRITE PATIENTS
# ============================================================

def write_patients(patients):

    with open(CSV_FILE, "w", newline="") as file:

        fieldnames = [
            "patient_id",
            "name",
            "age",
            "gender",
            "phone",
            "disease",
            "severity",
            "priority",
            "appointment_date",
            "appointment_time",
            "status"
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(patients)


# ============================================================
# GENERATE APPOINTMENT SLOTS
# ============================================================

def generate_time_slots():

    slots = []

    start = datetime.strptime(
        START_TIME,
        "%H:%M"
    )

    end = datetime.strptime(
        END_TIME,
        "%H:%M"
    )

    current = start

    while current < end:

        slots.append(
            current.strftime("%I:%M %p")
        )

        current += timedelta(
            minutes=SLOT_DURATION
        )

    return slots


# ============================================================
# GREEDY SCHEDULING ALGORITHM
# ============================================================

def greedy_schedule(patients):

    # --------------------------------------------------------
    # Only patients who are waiting need scheduling.
    # Already completed/cancelled patients are not scheduled.
    # --------------------------------------------------------

    waiting_patients = []

    other_patients = []

    for patient in patients:

        if patient["status"] in ["Waiting", "Scheduled"]:

            waiting_patients.append(patient)

        else:

            other_patients.append(patient)


    # --------------------------------------------------------
    # GREEDY STEP
    #
    # Select the patient with the highest priority first.
    # --------------------------------------------------------

    waiting_patients.sort(
        key=lambda x: int(x["priority"]),
        reverse=True
    )


    # --------------------------------------------------------
    # Generate available appointment slots
    # --------------------------------------------------------

    slots = generate_time_slots()

    today = datetime.now().strftime("%Y-%m-%d")


    # --------------------------------------------------------
    # Assign earliest slot to highest priority patient
    # --------------------------------------------------------

    for index, patient in enumerate(waiting_patients):

        if index < len(slots):

            patient["appointment_date"] = today

            patient["appointment_time"] = slots[index]

            patient["status"] = "Scheduled"

        else:

            patient["appointment_date"] = ""

            patient["appointment_time"] = ""

            patient["status"] = "Waiting"


    # --------------------------------------------------------
    # Combine patients
    # --------------------------------------------------------

    final_patients = waiting_patients + other_patients

    return final_patients


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return render_template("index.html")


# ============================================================
# REGISTER PATIENT
# ============================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        patient_id = request.form["patient_id"]
        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        phone = request.form["phone"]
        disease = request.form["disease"]
        severity = request.form["severity"]

        patients = read_patients()


        # ----------------------------------------------------
        # Check duplicate patient ID
        # ----------------------------------------------------

        for patient in patients:

            if patient["patient_id"] == patient_id:

                return """
                <script>
                    alert("Patient ID already exists!");
                    window.location.href="/register";
                </script>
                """


        # ----------------------------------------------------
        # Calculate priority
        # ----------------------------------------------------

        priority = calculate_priority(severity)


        # ----------------------------------------------------
        # Create new patient
        # ----------------------------------------------------

        new_patient = {

            "patient_id": patient_id,

            "name": name,

            "age": age,

            "gender": gender,

            "phone": phone,

            "disease": disease,

            "severity": severity,

            "priority": str(priority),

            "appointment_date": "",

            "appointment_time": "",

            "status": "Waiting"
        }


        patients.append(new_patient)


        # ----------------------------------------------------
        # Apply Greedy Algorithm
        # ----------------------------------------------------

        patients = greedy_schedule(patients)


        # ----------------------------------------------------
        # Save to CSV
        # ----------------------------------------------------

        write_patients(patients)


        return redirect("/dashboard")


    return render_template("register.html")


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    patients = read_patients()

    # Sort by priority
    patients.sort(
        key=lambda x: int(x["priority"]),
        reverse=True
    )

    return render_template(
        "dashboard.html",
        patients=patients
    )


# ============================================================
# GET PATIENT DATA AS JSON
# ============================================================

@app.route("/api/patients")
def api_patients():

    patients = read_patients()

    patients.sort(
        key=lambda x: int(x["priority"]),
        reverse=True
    )

    return jsonify(patients)


# ============================================================
# CANCEL APPOINTMENT
# ============================================================

@app.route("/cancel/<patient_id>", methods=["POST"])
def cancel_appointment(patient_id):

    patients = read_patients()

    for patient in patients:

        if patient["patient_id"] == patient_id:

            patient["status"] = "Cancelled"

            patient["appointment_date"] = ""

            patient["appointment_time"] = ""


    # Re-run greedy scheduling for remaining patients

    patients = greedy_schedule(patients)

    write_patients(patients)

    return redirect("/dashboard")


# ============================================================
# COMPLETE APPOINTMENT
# ============================================================

@app.route("/complete/<patient_id>", methods=["POST"])
def complete_appointment(patient_id):

    patients = read_patients()

    for patient in patients:

        if patient["patient_id"] == patient_id:

            patient["status"] = "Completed"


    write_patients(patients)

    return redirect("/dashboard")


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    initialize_csv()

    app.run(
        debug=True
    )