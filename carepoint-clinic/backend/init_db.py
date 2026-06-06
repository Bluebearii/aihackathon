from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def get_password_hash(password):
    return pwd_context.hash(password)

import models
from database import SessionLocal, engine
from datetime import date, time, datetime, timedelta

# Drop all tables and recreate (avoids file lock issues on Windows)
models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)

def init_db():
    db = SessionLocal()
    if not db.query(models.User).first():
        hashed_pw = get_password_hash("password123")
        today = date.today()
        
        # ==========================================
        # Admin user
        # ==========================================
        admin = models.User(
            first_name="Anthony",
            last_name="Tran",
            email="anthony_tran@careflowai.com",
            password_hash=hashed_pw,
            phone="555-0200",
            address="456 Clinic Way, Dallas, TX 75201",
            date_of_birth=date(1985, 8, 22),
            gender="Male",
            insurance_provider=None,
            role="admin"
        )
        db.add(admin)
        db.flush()
        
        # ==========================================
        # 10 Sample Patients
        # ==========================================
        patients_data = [
            {
                "first_name": "Maria", "last_name": "Garcia",
                "email": "maria.garcia@email.com", "phone": "214-555-0101",
                "address": "1234 Oak Lane, Dallas, TX 75201",
                "date_of_birth": date(1988, 3, 15), "gender": "Female",
                "insurance_provider": "Blue Cross Blue Shield",
                "no_show_count": 0, "last_visit_date": today - timedelta(days=7)
            },
            {
                "first_name": "James", "last_name": "Wilson",
                "email": "james.wilson@email.com", "phone": "214-555-0102",
                "address": "5678 Elm Street, Dallas, TX 75202",
                "date_of_birth": date(1975, 7, 22), "gender": "Male",
                "insurance_provider": "Aetna",
                "no_show_count": 0, "last_visit_date": None
            },
            {
                "first_name": "Sarah", "last_name": "Chen",
                "email": "sarah.chen@email.com", "phone": "214-555-0103",
                "address": "910 Maple Drive, Plano, TX 75023",
                "date_of_birth": date(1992, 11, 8), "gender": "Female",
                "insurance_provider": "UnitedHealthcare",
                "no_show_count": 0, "last_visit_date": today - timedelta(days=14)
            },
            {
                "first_name": "Robert", "last_name": "Johnson",
                "email": "robert.johnson@email.com", "phone": "214-555-0104",
                "address": "2345 Pine Road, Arlington, TX 76001",
                "date_of_birth": date(1965, 1, 30), "gender": "Male",
                "insurance_provider": "Medicare",
                "no_show_count": 2, "last_visit_date": today - timedelta(days=60)
            },
            {
                "first_name": "Emily", "last_name": "Rodriguez",
                "email": "emily.rodriguez@email.com", "phone": "214-555-0105",
                "address": "6789 Cedar Blvd, Irving, TX 75060",
                "date_of_birth": date(2000, 5, 12), "gender": "Female",
                "insurance_provider": "Cigna",
                "no_show_count": 0, "last_visit_date": None
            },
            {
                "first_name": "Michael", "last_name": "Thompson",
                "email": "michael.thompson@email.com", "phone": "214-555-0106",
                "address": "3456 Birch Ave, Frisco, TX 75034",
                "date_of_birth": date(1980, 9, 3), "gender": "Male",
                "insurance_provider": "Blue Cross Blue Shield",
                "no_show_count": 0, "last_visit_date": today - timedelta(days=3)
            },
            {
                "first_name": "Lisa", "last_name": "Park",
                "email": "lisa.park@email.com", "phone": "214-555-0107",
                "address": "7890 Walnut St, Richardson, TX 75080",
                "date_of_birth": date(1995, 4, 18), "gender": "Female",
                "insurance_provider": "Humana",
                "no_show_count": 1, "last_visit_date": today - timedelta(days=21)
            },
            {
                "first_name": "David", "last_name": "Kim",
                "email": "david.kim@email.com", "phone": "214-555-0108",
                "address": "4567 Willow Lane, Garland, TX 75040",
                "date_of_birth": date(1970, 12, 25), "gender": "Male",
                "insurance_provider": "Aetna",
                "no_show_count": 0, "last_visit_date": None
            },
            {
                "first_name": "Jessica", "last_name": "Brown",
                "email": "jessica.brown@email.com", "phone": "214-555-0109",
                "address": "8901 Spruce Court, McKinney, TX 75070",
                "date_of_birth": date(1998, 6, 7), "gender": "Female",
                "insurance_provider": "UnitedHealthcare",
                "no_show_count": 0, "last_visit_date": today - timedelta(days=90)
            },
            {
                "first_name": "Daniel", "last_name": "Martinez",
                "email": "daniel.martinez@email.com", "phone": "214-555-0110",
                "address": "2468 Aspen Way, Allen, TX 75002",
                "date_of_birth": date(1983, 2, 14), "gender": "Male",
                "insurance_provider": "Cigna",
                "no_show_count": 0, "last_visit_date": today - timedelta(days=5)
            },
        ]
        
        patient_objects = []
        for pdata in patients_data:
            p = models.User(
                first_name=pdata["first_name"],
                last_name=pdata["last_name"],
                email=pdata["email"],
                phone=pdata["phone"],
                address=pdata["address"],
                date_of_birth=pdata["date_of_birth"],
                gender=pdata["gender"],
                insurance_provider=pdata["insurance_provider"],
                no_show_count=pdata["no_show_count"],
                last_visit_date=pdata["last_visit_date"],
                password_hash=hashed_pw,
                role="patient"
            )
            db.add(p)
            patient_objects.append(p)
        
        db.flush()  # Get IDs assigned
        
        # ==========================================
        # Sample Appointments
        # ==========================================
        appointment_types = [
            "Annual Eye Exam", "Contact Lens Exam", "Follow-up Visit",
            "Medical Office Visit", "New Patient Visit", "Emergency Visit", "Consultation"
        ]
        providers = ["Dr. Smith", "Dr. Patel", "Dr. Lee"]
        
        appointments_data = [
            # Maria Garcia - Completed annual exam
            {"patient": 0, "type": "Annual Eye Exam", "date": today - timedelta(days=7),
             "time": time(9, 0), "status": "Completed", "provider": "Dr. Smith",
             "reason": "Annual eye examination", "notes": "Vision stable, new prescription issued"},
            # Maria Garcia - Upcoming follow-up
            {"patient": 0, "type": "Follow-up Visit", "date": today + timedelta(days=14),
             "time": time(10, 30), "status": "Confirmed", "provider": "Dr. Smith",
             "reason": "Follow-up on new prescription", "notes": None},
            # James Wilson - Pending contact lens exam
            {"patient": 1, "type": "Contact Lens Exam", "date": today + timedelta(days=3),
             "time": time(11, 0), "status": "Pending", "provider": "Dr. Patel",
             "reason": "Contact lens fitting and exam", "notes": None},
            # Sarah Chen - Confirmed follow-up
            {"patient": 2, "type": "Follow-up Visit", "date": today + timedelta(days=1),
             "time": time(14, 0), "status": "Confirmed", "provider": "Dr. Lee",
             "reason": "Follow-up on treatment progress", "notes": None},
            # Sarah Chen - Completed visit
            {"patient": 2, "type": "Medical Office Visit", "date": today - timedelta(days=14),
             "time": time(9, 30), "status": "Completed", "provider": "Dr. Lee",
             "reason": "Dry eye treatment", "notes": "Prescribed artificial tears"},
            # Robert Johnson - No Show
            {"patient": 3, "type": "Annual Eye Exam", "date": today - timedelta(days=30),
             "time": time(10, 0), "status": "No Show", "provider": "Dr. Smith",
             "reason": "Annual checkup", "notes": "Patient did not show, no call"},
            # Robert Johnson - Another No Show
            {"patient": 3, "type": "Follow-up Visit", "date": today - timedelta(days=10),
             "time": time(15, 0), "status": "No Show", "provider": "Dr. Patel",
             "reason": "Rescheduled from previous no-show", "notes": "Second consecutive no-show"},
            # Robert Johnson - Pending reschedule
            {"patient": 3, "type": "Annual Eye Exam", "date": today + timedelta(days=7),
             "time": time(13, 0), "status": "Pending", "provider": "Dr. Smith",
             "reason": "Rescheduled annual exam", "notes": None},
            # Emily Rodriguez - New patient, upcoming
            {"patient": 4, "type": "New Patient Visit", "date": today + timedelta(days=5),
             "time": time(8, 30), "status": "Pending", "provider": "Dr. Patel",
             "reason": "First visit, general eye exam", "notes": None},
            # Michael Thompson - Multiple visits
            {"patient": 5, "type": "Annual Eye Exam", "date": today - timedelta(days=3),
             "time": time(10, 0), "status": "Completed", "provider": "Dr. Lee",
             "reason": "Annual eye examination", "notes": "Everything looks good"},
            {"patient": 5, "type": "Consultation", "date": today + timedelta(days=10),
             "time": time(11, 30), "status": "Confirmed", "provider": "Dr. Lee",
             "reason": "Discuss LASIK options", "notes": None},
            {"patient": 5, "type": "Medical Office Visit", "date": today - timedelta(days=45),
             "time": time(14, 30), "status": "Completed", "provider": "Dr. Smith",
             "reason": "Eye strain from computer work", "notes": "Recommended blue light glasses"},
            # Lisa Park - Emergency visit completed
            {"patient": 6, "type": "Emergency Visit", "date": today - timedelta(days=21),
             "time": time(16, 0), "status": "Completed", "provider": "Dr. Patel",
             "reason": "Sudden vision changes", "notes": "Diagnosed with migraine-related visual disturbance"},
            # Lisa Park - No show once
            {"patient": 6, "type": "Follow-up Visit", "date": today - timedelta(days=5),
             "time": time(9, 0), "status": "No Show", "provider": "Dr. Patel",
             "reason": "Follow-up on emergency visit", "notes": "Called, will reschedule"},
            # David Kim - Pending consultation
            {"patient": 7, "type": "Consultation", "date": today + timedelta(days=2),
             "time": time(13, 30), "status": "Pending", "provider": "Dr. Lee",
             "reason": "Discuss cataract surgery options", "notes": None},
            # Jessica Brown - Cancelled
            {"patient": 8, "type": "Annual Eye Exam", "date": today - timedelta(days=2),
             "time": time(10, 0), "status": "Cancelled", "provider": "Dr. Smith",
             "reason": "Annual eye exam", "notes": "Patient cancelled due to schedule conflict"},
            # Jessica Brown - Rescheduled
            {"patient": 8, "type": "Annual Eye Exam", "date": today + timedelta(days=8),
             "time": time(15, 0), "status": "Confirmed", "provider": "Dr. Smith",
             "reason": "Rescheduled annual eye exam", "notes": None},
            # Daniel Martinez - Completed medical visit
            {"patient": 9, "type": "Medical Office Visit", "date": today - timedelta(days=5),
             "time": time(11, 0), "status": "Completed", "provider": "Dr. Lee",
             "reason": "Glaucoma screening", "notes": "No signs of glaucoma, will monitor annually"},
            # Daniel Martinez - Upcoming
            {"patient": 9, "type": "Follow-up Visit", "date": today + timedelta(days=30),
             "time": time(9, 30), "status": "Pending", "provider": "Dr. Lee",
             "reason": "Annual follow-up on glaucoma screening", "notes": None},
            # Today's appointments for demo
            {"patient": 0, "type": "Medical Office Visit", "date": today,
             "time": time(9, 0), "status": "Confirmed", "provider": "Dr. Smith",
             "reason": "Prescription adjustment", "notes": None},
            {"patient": 2, "type": "Follow-up Visit", "date": today,
             "time": time(10, 30), "status": "Pending", "provider": "Dr. Lee",
             "reason": "Check treatment progress", "notes": None},
            {"patient": 5, "type": "Contact Lens Exam", "date": today,
             "time": time(14, 0), "status": "Confirmed", "provider": "Dr. Patel",
             "reason": "Annual contact lens renewal", "notes": None},
            {"patient": 7, "type": "New Patient Visit", "date": today,
             "time": time(15, 30), "status": "Pending", "provider": "Dr. Lee",
             "reason": "Initial consultation", "notes": None},
        ]
        
        appt_objects = []
        for adata in appointments_data:
            appt = models.Appointment(
                patient_id=patient_objects[adata["patient"]].id,
                appointment_type=adata["type"],
                appointment_date=adata["date"],
                appointment_time=adata["time"],
                status=adata["status"],
                provider=adata["provider"],
                reason_for_visit=adata["reason"],
                notes=adata["notes"],
                insurance_provider=patient_objects[adata["patient"]].insurance_provider
            )
            db.add(appt)
            appt_objects.append(appt)
        
        db.flush()
        
        # ==========================================
        # Sample Points
        # ==========================================
        points_data = [
            # Maria Garcia - 35 points
            {"patient": 0, "appt_idx": 0, "points": 10, "reason": "Showed up - Annual Eye Exam"},
            {"patient": 0, "appt_idx": None, "points": 5, "reason": "Completed medical history form"},
            {"patient": 0, "appt_idx": None, "points": 20, "reason": "Referred a patient"},
            # James Wilson - 20 points
            {"patient": 1, "appt_idx": None, "points": 20, "reason": "Referred a patient"},
            # Sarah Chen - 50 points
            {"patient": 2, "appt_idx": 4, "points": 10, "reason": "Showed up - Medical Office Visit"},
            {"patient": 2, "appt_idx": None, "points": 5, "reason": "Completed medical history form"},
            {"patient": 2, "appt_idx": None, "points": 15, "reason": "Manual adjustment - loyal patient bonus"},
            {"patient": 2, "appt_idx": None, "points": 20, "reason": "Referred a patient"},
            # Robert Johnson - 5 points
            {"patient": 3, "appt_idx": None, "points": 5, "reason": "Completed medical history form"},
            # Michael Thompson - 75 points
            {"patient": 5, "appt_idx": 9, "points": 10, "reason": "Showed up - Annual Eye Exam"},
            {"patient": 5, "appt_idx": 11, "points": 10, "reason": "Showed up - Medical Office Visit"},
            {"patient": 5, "appt_idx": None, "points": 5, "reason": "Completed medical history form"},
            {"patient": 5, "appt_idx": None, "points": 20, "reason": "Referred a patient"},
            {"patient": 5, "appt_idx": None, "points": 20, "reason": "Referred a patient"},
            {"patient": 5, "appt_idx": None, "points": 10, "reason": "Manual adjustment - community event participation"},
            # Lisa Park - 15 points
            {"patient": 6, "appt_idx": 12, "points": 10, "reason": "Showed up - Emergency Visit"},
            {"patient": 6, "appt_idx": None, "points": 5, "reason": "Completed medical history form"},
            # David Kim - 10 points
            {"patient": 7, "appt_idx": None, "points": 10, "reason": "Manual adjustment - welcome bonus"},
            # Daniel Martinez - 45 points
            {"patient": 9, "appt_idx": 17, "points": 10, "reason": "Showed up - Medical Office Visit"},
            {"patient": 9, "appt_idx": None, "points": 5, "reason": "Completed medical history form"},
            {"patient": 9, "appt_idx": None, "points": 20, "reason": "Referred a patient"},
            {"patient": 9, "appt_idx": None, "points": 10, "reason": "Manual adjustment - feedback survey"},
        ]
        
        for pdata in points_data:
            pt = models.Point(
                patient_id=patient_objects[pdata["patient"]].id,
                appointment_id=appt_objects[pdata["appt_idx"]].id if pdata["appt_idx"] is not None else None,
                points_added=pdata["points"],
                reason=pdata["reason"],
                added_by_staff_id=admin.id
            )
            db.add(pt)
        
        # ==========================================
        # Sample Medical Histories
        # ==========================================
        # Maria Garcia - complete
        mh1 = models.MedicalHistory(
            patient_id=patient_objects[0].id,
            patient_name="Maria Garcia",
            height_ft=5, height_in=4, weight=135,
            latex_allergy_yes=False, latex_allergy_no=True,
            diagnosis="Myopia, mild astigmatism",
            hospitalized=False, surgery=False,
            falls_past_year=False, previous_treatment=True,
            treatment_summary="Corrective lenses since age 12",
            asthma=True, allergies=True, headaches=True,
            emergency_contact_name="Carlos Garcia",
            emergency_contact_phone="214-555-0201",
            current_medications="Albuterol inhaler (as needed)",
            completed_at=datetime.utcnow() - timedelta(days=7)
        )
        db.add(mh1)

        # Sarah Chen - complete
        mh2 = models.MedicalHistory(
            patient_id=patient_objects[2].id,
            patient_name="Sarah Chen",
            height_ft=5, height_in=6, weight=128,
            latex_allergy_yes=False, latex_allergy_no=True,
            diagnosis="Dry eye syndrome",
            hospitalized=False, surgery=False,
            falls_past_year=False, previous_treatment=True,
            treatment_summary="Artificial tears for 6 months",
            anxiety_panic=True, depression=True,
            emergency_contact_name="Wei Chen",
            emergency_contact_phone="214-555-0203",
            current_medications="Sertraline 50mg daily",
            completed_at=datetime.utcnow() - timedelta(days=14)
        )
        db.add(mh2)

        # Robert Johnson - complete but with conditions
        mh3 = models.MedicalHistory(
            patient_id=patient_objects[3].id,
            patient_name="Robert Johnson",
            height_ft=5, height_in=10, weight=195,
            latex_allergy_yes=False, latex_allergy_no=True,
            diagnosis="Presbyopia, early cataracts",
            hospitalized=True, hospitalized_date="2020-03-15",
            surgery=False,
            falls_past_year=True, falls_count=1,
            previous_treatment=True, treatment_summary="Progressive lenses since 2018",
            diabetes=True, high_blood_pressure=True, hearing_impairment=True,
            emergency_contact_name="Patricia Johnson",
            emergency_contact_phone="214-555-0204",
            current_medications="Metformin 500mg, Lisinopril 10mg",
            completed_at=datetime.utcnow() - timedelta(days=30)
        )
        db.add(mh3)

        # Michael Thompson - complete
        mh4 = models.MedicalHistory(
            patient_id=patient_objects[5].id,
            patient_name="Michael Thompson",
            height_ft=6, height_in=0, weight=180,
            latex_allergy_yes=False, latex_allergy_no=True,
            diagnosis="Computer vision syndrome",
            hospitalized=False, surgery=False,
            falls_past_year=False, previous_treatment=True,
            treatment_summary="Blue light glasses prescribed 2024",
            back_injury=True, headaches=True,
            emergency_contact_name="Jennifer Thompson",
            emergency_contact_phone="214-555-0206",
            current_medications="Ibuprofen as needed",
            completed_at=datetime.utcnow() - timedelta(days=3)
        )
        db.add(mh4)

        # Lisa Park - complete
        mh5 = models.MedicalHistory(
            patient_id=patient_objects[6].id,
            patient_name="Lisa Park",
            height_ft=5, height_in=3, weight=115,
            latex_allergy_yes=True, latex_allergy_no=False,
            topical_allergy="Neomycin",
            diagnosis="Migraine with aura",
            hospitalized=False, surgery=False,
            falls_past_year=False, previous_treatment=True,
            treatment_summary="Migraine management since 2023",
            mri=True,
            headaches=True, dizzy_fainting=True, nausea_vomiting=True,
            emergency_contact_name="Soo Park",
            emergency_contact_phone="214-555-0207",
            current_medications="Sumatriptan as needed, Magnesium supplement",
            completed_at=datetime.utcnow() - timedelta(days=21)
        )
        db.add(mh5)

        # Daniel Martinez - complete
        mh6 = models.MedicalHistory(
            patient_id=patient_objects[9].id,
            patient_name="Daniel Martinez",
            height_ft=5, height_in=9, weight=170,
            latex_allergy_yes=False, latex_allergy_no=True,
            diagnosis="Glaucoma suspect, borderline IOP",
            hospitalized=False, surgery=False,
            falls_past_year=False, previous_treatment=True,
            treatment_summary="Annual monitoring since 2024",
            smoking=True, high_blood_pressure=True,
            emergency_contact_name="Rosa Martinez",
            emergency_contact_phone="214-555-0210",
            current_medications="Amlodipine 5mg",
            completed_at=datetime.utcnow() - timedelta(days=5)
        )
        db.add(mh6)

        # Dashboard
        default_dash = models.ExternalDashboard(
            name="Main Analytics",
            url="http://localhost:8501",
            description="The primary internal data visualization dashboard."
        )
        db.add(default_dash)
        
        db.commit()
        print("[OK] Database initialized with 10 sample patients, appointments, points, and medical histories.")
    else:
        print("Database already initialized.")
    db.close()

if __name__ == "__main__":
    init_db()
