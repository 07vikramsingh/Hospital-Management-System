from flask import Flask, render_template
from db_config import get_connection
app = Flask(__name__)


def get_dashboard_counts():
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM patients")
        patients = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM doctors")
        doctors = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM appointments")
        appointments = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM bills WHERE payment_status = 'UNPAID'"
        )
        unpaid = cursor.fetchone()[0]

        return patients, doctors, appointments, unpaid

    finally:
        cursor.close()
        connection.close()


@app.route("/")
def dashboard():
    try:
        patients, doctors, appointments, unpaid = get_dashboard_counts()

        return render_template(
            "index.html",
            patients=patients,
            doctors=doctors,
            appointments=appointments,
            unpaid=unpaid
        )

    except Exception as error:
        return (
            "<h2>Database connection error</h2>"
            "<p>Check db_config.py and your Oracle database.</p>"
            f"<pre>{error}</pre>",
            500
        )


@app.route("/patients", methods=["GET", "POST"])
def patients_page():
    from flask import request, redirect, url_for, flash

    if request.method == "POST":
        try:
            patient_id = int(request.form["patient_id"])
            patient_name = request.form["patient_name"].strip()
            age = int(request.form["age"])
            gender = request.form["gender"]
            phone = request.form["phone"].strip()

            if not patient_name or not (0 <= age <= 120):
                return "Invalid patient name or age.", 400

            connection = get_connection()
            cursor = connection.cursor()

            try:
                cursor.execute(
                    """
                    INSERT INTO patients
                    (patient_id, patient_name, age, gender, phone)
                    VALUES (:1, :2, :3, :4, :5)
                    """,
                    (patient_id, patient_name, age, gender, phone)
                )
                connection.commit()
            finally:
                cursor.close()
                connection.close()

            return redirect(url_for("patients_page"))

        except Exception as error:
            return f"Unable to register patient: {error}", 400

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT patient_id, patient_name, age, gender, phone
            FROM patients
            ORDER BY patient_id
        """)
        patient_list = cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

    return render_template(
        "patients.html",
        patient_list=patient_list
    )


@app.route("/doctors")
def doctors_page():
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT doctor_id, doctor_name, specialization,
                   consultation_fee
            FROM doctors
            ORDER BY doctor_id
        """)
        doctor_list = cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

    return render_template(
        "doctors.html",
        doctor_list=doctor_list
    )


@app.route("/appointments")
def appointments_page():
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT a.appointment_id,
                   p.patient_name,
                   d.doctor_name,
                   TO_CHAR(a.appointment_date, 'DD-MON-YYYY HH:MI AM'),
                   a.appointment_status
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            JOIN doctors d ON a.doctor_id = d.doctor_id
            ORDER BY a.appointment_date DESC
        """)
        appointment_list = cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

    return render_template(
        "appointments.html",
        appointment_list=appointment_list
    )



if __name__ == "__main__":
    app.run(debug=True)
