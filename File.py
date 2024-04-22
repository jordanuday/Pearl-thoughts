from flask import Flask, jsonify, request

app = Flask(__name__)

doctors = [
    {
        "id": 1,
        "name": "Dr. Smith",
        "specialty": "Cardiology",
        "schedule": {
            "Monday": ["18:00", "19:00", "20:00"],
            # Add schedules for other days
        },
        "max_patients_per_slot": 5  # Assuming each slot can have a maximum of 5 patients
    },
    # Add other doctor entries
]

appointments = []

@app.route('/api/doctors', methods=['GET'])
def get_doctors():
    return jsonify(doctors)

@app.route('/api/doctors/<int:doctor_id>', methods=['GET'])
def get_doctor(doctor_id):
    doctor = next((doctor for doctor in doctors if doctor['id'] == doctor_id), None)
    if doctor:
        return jsonify(doctor)
    return jsonify({"message": "Doctor not found"}), 404

@app.route('/api/doctors/<int:doctor_id>/availability', methods=['GET'])
def get_availability(doctor_id):
    doctor = next((doctor for doctor in doctors if doctor['id'] == doctor_id), None)
    if doctor:
        date = request.args.get('date')
        if not date:
            return jsonify({"message": "Date parameter is missing"}), 400
        # Implement logic to check availability based on the doctor's schedule and existing appointments
        available_slots = doctor['schedule'].get(date, [])
        for appointment in appointments:
            if appointment['doctor_id'] == doctor_id and appointment['date'] == date:
                available_slots = [slot for slot in available_slots if slot != appointment['time']]
        return jsonify({"available_slots": available_slots})
    return jsonify({"message": "Doctor not found"}), 404

@app.route('/api/appointments/book', methods=['POST'])
def book_appointment():
    data = request.json
    doctor_id = data.get('doctor_id')
    patient_id = data.get('patient_id')
    date = data.get('date')
    time = data.get('time')
    if not all([doctor_id, patient_id, date, time]):
        return jsonify({"message": "Missing required parameters"}), 400
    doctor = next((doctor for doctor in doctors if doctor['id'] == doctor_id), None)
    if doctor:
        # Check if the appointment slot is available
        if time in doctor['schedule'].get(date, []) and len([appointment for appointment in appointments if appointment['doctor_id'] == doctor_id and appointment['date'] == date and appointment['time'] == time]) < doctor['max_patients_per_slot']:
            appointments.append({"doctor_id": doctor_id, "patient_id": patient_id, "date": date, "time": time})
            return jsonify({"message": "Appointment booked successfully"})
        return jsonify({"message": "Slot not available"}), 400
    return jsonify({"message": "Doctor not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
