"""
Load demo hospitals, doctors, schedules, and optional test users for hackathon demos.
Run: python manage.py seed_demo
"""

import datetime as dt

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from accounts.models import PatientProfile
from hospitals.models import Department, Doctor, DoctorSchedule, Hospital, HospitalResources

User = get_user_model()


class Command(BaseCommand):
    help = "Seed demo data (hospitals, departments, doctors, resources, schedules)."

    def handle(self, *args, **options):
        if Hospital.objects.exists():
            self.stdout.write(self.style.WARNING("Hospitals already exist; skipping seed."))
            return

        # Demo hospitals data with realistic information
        hospitals_data = [
    {
        "name": "AIIMS Patna",
        "slug": "aiims-patna",
        "address": "Phulwari Sharif, Near IIM Patna",
        "city": "Patna",
        "state": "Bihar",
        "postal_code": "801507",
        "latitude": "25.5840",
        "longitude": "85.0870",
        "phone": "+91-612-2451006",
        "email": "info@aiimspatna.org",
        "rating": "4.8",
        "emergency_available": True,
        "description": "Premier government hospital with 750+ beds, advanced surgical care, cardiac center, and trauma care.",
        "cover_image": "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=1200&q=80",
    },
    {
        "name": "Patna Medical College Hospital (PMCH)",
        "slug": "pmch-patna",
        "address": "Ashok Rajpath, Patna City",
        "city": "Patna",
        "state": "Bihar",
        "postal_code": "800004",
        "latitude": "25.6170",
        "longitude": "85.1620",
        "phone": "+91-612-2300343",
        "email": "pmch@bihar.gov.in",
        "rating": "4.4",
        "emergency_available": True,
        "description": "One of oldest & largest govt hospitals with 600+ beds, excellent teaching facility, 24/7 emergency.",
        "cover_image": "https://images.unsplash.com/photo-1586773860418-d37222d8fce3?w=1200&q=80",
    },
    {
        "name": "IGIMS Patna",
        "slug": "igims-patna",
        "address": "Sheikhpura Road, Patna",
        "city": "Patna",
        "state": "Bihar",
        "postal_code": "800014",
        "latitude": "25.6030",
        "longitude": "85.0930",
        "phone": "+91-612-2297099",
        "email": "info@igims.org",
        "rating": "4.6",
        "emergency_available": True,
        "description": "Indira Gandhi Institute with 400+ beds, advanced diagnostic center, ICU & CCU facilities.",
        "cover_image": "https://images.unsplash.com/photo-1551190822-a9333d879b1f?w=1200&q=80",
    },
    {
        "name": "Paras HMRI Hospital",
        "slug": "paras-hospital",
        "address": "Raja Bazar, Patna",
        "city": "Patna",
        "state": "Bihar",
        "postal_code": "800014",
        "latitude": "25.6075",
        "longitude": "85.0890",
        "phone": "+91-612-7107777",
        "email": "info@parashospitals.com",
        "rating": "4.7",
        "emergency_available": True,
        "description": "Multi-specialty private hospital with 300+ beds, modern infrastructure, organ transplant unit.",
        "cover_image": "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=1200&q=80",
    },
    {
        "name": "Ruban Memorial Hospital",
        "slug": "ruban-hospital",
        "address": "Baily Road, Patna",
        "city": "Patna",
        "state": "Bihar",
        "postal_code": "800014",
        "latitude": "25.6090",
        "longitude": "85.0950",
        "phone": "+91-612-2531111",
        "email": "info@rubanhospital.com",
        "rating": "4.5",
        "emergency_available": True,
        "description": "Well-known private hospital with 250+ beds, maternity care, orthopedic center.",
        "cover_image": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1f?w=1200&q=80",
    },
    {
        "name": "Apollo Spectra Hospital",
        "slug": "apollo-spectra",
        "address": "Kankarbagh, Patna",
        "city": "Patna",
        "state": "Bihar",
        "postal_code": "800020",
        "latitude": "25.6005",
        "longitude": "85.1585",
        "phone": "+91-612-2200000",
        "email": "info@apollospectra.com",
        "rating": "4.7",
        "emergency_available": True,
        "description": "Advanced surgical center with 200+ beds, minimally invasive surgery, diagnostic imaging.",
        "cover_image": "https://images.unsplash.com/photo-1559757175-0eb30cd8c063?w=1200&q=80",
    },
    {
        "name": "Nalanda Medical College Hospital",
        "slug": "nmch-patna",
        "address": "Agam Kuan, Patna",
        "city": "Patna",
        "state": "Bihar",
        "postal_code": "800007",
        "latitude": "25.6200",
        "longitude": "85.2000",
        "phone": "+91-612-2301111",
        "email": "nmch@bihar.gov.in",
        "rating": "4.2",
        "emergency_available": True,
        "description": "Government medical college hospital with 400+ beds, teaching hospital, affordable healthcare.",
        "cover_image": "https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=1200&q=80",
    },
    {
        "name": "Kurji Holy Family Hospital",
        "slug": "kurji-hospital",
        "address": "Kurji, Patna",
        "city": "Patna",
        "state": "Bihar",
        "postal_code": "800010",
        "latitude": "25.6300",
        "longitude": "85.1200",
        "phone": "+91-612-2262540",
        "email": "info@kurjihospital.com",
        "rating": "4.6",
        "emergency_available": True,
        "description": "Trusted institution with 180+ beds, expertise in maternity care, pediatrics, and general medicine.",
        "cover_image": "https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=1200&q=80",
    },
    {
        "name": "Apex Hospital Patna",
        "slug": "apex-hospital",
        "address": "Boring Road, Patna",
        "city": "Patna",
        "state": "Bihar",
        "postal_code": "800013",
        "latitude": "25.6150",
        "longitude": "85.1100",
        "phone": "+91-612-2522222",
        "email": "info@apexhospital.com",
        "rating": "4.4",
        "emergency_available": True,
        "description": "Modern hospital with 220+ beds, multi-specialty services, 24/7 laboratory & imaging.",
        "cover_image": "https://images.unsplash.com/photo-1551190822-a9333d879b1f?w=1200&q=80",
    },
    {
        "name": "NMC Gaya Medical College Hospital",
        "slug": "nmc-gaya",
        "address": "Vidyapith Road, Gaya",
        "city": "Gaya",
        "state": "Bihar",
        "postal_code": "823001",
        "latitude": "24.7955",
        "longitude": "85.0027",
        "phone": "+91-631-2242211",
        "email": "info@nmcgaya.org",
        "rating": "4.3",
        "emergency_available": True,
        "description": "Medical college hospital with 350+ beds, serving Gaya region, modern ICU facilities.",
        "cover_image": "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=1200&q=80",
    },
]

        hospitals = []
        for data in hospitals_data:
            hospital = Hospital.objects.create(**data)
            hospitals.append(hospital)

        # Create resources with realistic bed counts for each hospital
        resources_data = [
            {"icu_beds_total": 45, "icu_beds_available": 12, "general_beds_total": 750, "general_beds_available": 145, "ventilators_available": 35, "ambulances_available": 12},  # AIIMS
            {"icu_beds_total": 28, "icu_beds_available": 8, "general_beds_total": 600, "general_beds_available": 110, "ventilators_available": 25, "ambulances_available": 10},   # PMCH
            {"icu_beds_total": 20, "icu_beds_available": 6, "general_beds_total": 400, "general_beds_available": 75, "ventilators_available": 18, "ambulances_available": 8},    # IGIMS
            {"icu_beds_total": 18, "icu_beds_available": 5, "general_beds_total": 300, "general_beds_available": 65, "ventilators_available": 15, "ambulances_available": 7},    # Paras
            {"icu_beds_total": 15, "icu_beds_available": 4, "general_beds_total": 250, "general_beds_available": 55, "ventilators_available": 12, "ambulances_available": 6},    # Ruban
            {"icu_beds_total": 12, "icu_beds_available": 3, "general_beds_total": 200, "general_beds_available": 45, "ventilators_available": 10, "ambulances_available": 5},    # Apollo
            {"icu_beds_total": 20, "icu_beds_available": 7, "general_beds_total": 400, "general_beds_available": 80, "ventilators_available": 16, "ambulances_available": 8},    # Nalanda
            {"icu_beds_total": 10, "icu_beds_available": 3, "general_beds_total": 180, "general_beds_available": 40, "ventilators_available": 8, "ambulances_available": 4},     # Kurji
            {"icu_beds_total": 14, "icu_beds_available": 4, "general_beds_total": 220, "general_beds_available": 50, "ventilators_available": 11, "ambulances_available": 5},    # Apex
            {"icu_beds_total": 18, "icu_beds_available": 6, "general_beds_total": 350, "general_beds_available": 70, "ventilators_available": 14, "ambulances_available": 7},    # NMC Gaya
        ]

        for hospital, resources in zip(hospitals, resources_data):
            HospitalResources.objects.create(hospital=hospital, **resources)

        # Create departments and doctors with better organization
        # Each department will have 2-3 doctors assigned
        
        # Department configuration with doctors for each hospital
        department_config = {
            0: {  # AIIMS Patna
                "Cardiology": [
                    {"first_name": "Rajesh", "last_name": "Kumar", "specialization": "Interventional Cardiology", "experience_years": 14, "bio": "Expert in coronary angioplasty and preventive cardiology.", "rating": "4.7"},
                    {"first_name": "Neha", "last_name": "Mishra", "specialization": "Cardiac Surgery", "experience_years": 12, "bio": "Specializes in complex heart surgeries and valve replacements.", "rating": "4.6"},
                    {"first_name": "Sanjay", "last_name": "Gupta", "specialization": "Echocardiography", "experience_years": 10, "bio": "Expert in cardiac imaging and diagnosis.", "rating": "4.5"},
                ],
                "Orthopedics": [
                    {"first_name": "Priya", "last_name": "Singh", "specialization": "Sports Orthopedics", "experience_years": 9, "bio": "Specializes in joint replacement and sports injuries.", "rating": "4.5"},
                    {"first_name": "Arun", "last_name": "Patel", "specialization": "Spine Surgery", "experience_years": 11, "bio": "Advanced spinal decompression and fusion surgeon.", "rating": "4.6"},
                ],
                "Emergency Medicine": [
                    {"first_name": "Amit", "last_name": "Sharma", "specialization": "Emergency Medicine", "experience_years": 11, "bio": "ER specialist with expertise in trauma care.", "rating": "4.9"},
                ],
            },
            1: {  # PMCH Patna
                "Cardiology": [
                    {"first_name": "Vikram", "last_name": "Rao", "specialization": "Interventional Cardiology", "experience_years": 13, "bio": "Veteran cardiologist with 13+ years experience.", "rating": "4.6"},
                ],
                "Pediatrics": [
                    {"first_name": "Dr. Sunita", "last_name": "Verma", "specialization": "Pediatric Medicine", "experience_years": 16, "bio": "Comprehensive child healthcare specialist.", "rating": "4.6"},
                    {"first_name": "Pooja", "last_name": "Saxena", "specialization": "Pediatric Surgery", "experience_years": 10, "bio": "Expert in pediatric surgical interventions.", "rating": "4.5"},
                ],
                "Internal Medicine": [
                    {"first_name": "Ravi", "last_name": "Kumar", "specialization": "Gastroenterology", "experience_years": 12, "bio": "Specialist in digestive system disorders.", "rating": "4.4"},
                    {"first_name": "Deepak", "last_name": "Singh", "specialization": "General Internal Medicine", "experience_years": 10, "bio": "Expert in chronic disease management.", "rating": "4.5"},
                ],
            },
            2: {  # IGIMS Patna
                "Emergency Medicine": [
                    {"first_name": "Ashok", "last_name": "Kumar", "specialization": "Emergency Medicine", "experience_years": 15, "bio": "Senior ER specialist with trauma expertise.", "rating": "4.8"},
                    {"first_name": "Priya", "last_name": "Yadav", "specialization": "Critical Care", "experience_years": 11, "bio": "ICU specialist with critical patient management.", "rating": "4.7"},
                ],
                "Orthopedics": [
                    {"first_name": "Mahesh", "last_name": "Thakur", "specialization": "Trauma Orthopedics", "experience_years": 13, "bio": "Expert in complex trauma and fracture management.", "rating": "4.6"},
                    {"first_name": "Karan", "last_name": "Verma", "specialization": "Joint Replacement", "experience_years": 9, "bio": "Specialist in hip and knee replacements.", "rating": "4.5"},
                ],
                "Neurology": [
                    {"first_name": "Vikram", "last_name": "Patel", "specialization": "Neurosurgery", "experience_years": 12, "bio": "Advanced neurosurgical interventions specialist.", "rating": "4.7"},
                ],
            },
            3: {  # Paras HMRI Hospital
                "Cardiac Surgery": [
                    {"first_name": "Dr. Rajesh", "last_name": "Singhania", "specialization": "Cardiac Surgery", "experience_years": 15, "bio": "Pioneer in minimally invasive cardiac surgery.", "rating": "4.8"},
                    {"first_name": "Akshay", "last_name": "Desai", "specialization": "Transplant Surgery", "experience_years": 11, "bio": "Expert in organ transplant procedures.", "rating": "4.6"},
                ],
                "Oncology": [
                    {"first_name": "Anjali", "last_name": "Dutta", "specialization": "Medical Oncology", "experience_years": 10, "bio": "Cancer specialist with immunotherapy expertise.", "rating": "4.5"},
                    {"first_name": "Sushant", "last_name": "Gupta", "specialization": "Surgical Oncology", "experience_years": 12, "bio": "Expert in complex cancer surgeries.", "rating": "4.6"},
                ],
            },
            4: {  # Ruban Memorial Hospital
                "Obstetrics & Gynecology": [
                    {"first_name": "Meera", "last_name": "Sharma", "specialization": "Obstetrics", "experience_years": 14, "bio": "Experienced obstetrician with 1000+ deliveries.", "rating": "4.7"},
                    {"first_name": "Isha", "last_name": "Kapoor", "specialization": "Gynecology", "experience_years": 11, "bio": "Gynecologist specializing in women's health.", "rating": "4.5"},
                ],
                "Pediatrics": [
                    {"first_name": "Rohan", "last_name": "Mukherjee", "specialization": "Neonatology", "experience_years": 9, "bio": "Specialist in newborn and premature infant care.", "rating": "4.6"},
                ],
            },
            5: {  # Apollo Spectra Hospital
                "Gastroenterology": [
                    {"first_name": "Satish", "last_name": "Reddy", "specialization": "Gastroenterology", "experience_years": 13, "bio": "Expert in endoscopy and GI disorders.", "rating": "4.6"},
                    {"first_name": "Harpreet", "last_name": "Singh", "specialization": "Hepatology", "experience_years": 11, "bio": "Liver disease specialist.", "rating": "4.5"},
                ],
                "Urology": [
                    {"first_name": "Suresh", "last_name": "Nair", "specialization": "Urology", "experience_years": 12, "bio": "Urological surgery expert including robotic procedures.", "rating": "4.7"},
                ],
            },
            6: {  # Nalanda Medical College
                "General Surgery": [
                    {"first_name": "Gyan", "last_name": "Prakash", "specialization": "General Surgery", "experience_years": 15, "bio": "Laparoscopic and open surgery specialist.", "rating": "4.6"},
                ],
                "Internal Medicine": [
                    {"first_name": "Mamta", "last_name": "Jain", "specialization": "Pulmonology", "experience_years": 11, "bio": "Respiratory diseases specialist.", "rating": "4.5"},
                    {"first_name": "Niraj", "last_name": "Tandon", "specialization": "Endocrinology", "experience_years": 10, "bio": "Diabetes and hormonal disorders specialist.", "rating": "4.5"},
                ],
            },
            7: {  # Kurji Holy Family
                "Obstetrics & Gynecology": [
                    {"first_name": "Sneha", "last_name": "Roy", "specialization": "Obstetrics", "experience_years": 12, "bio": "Renowned obstetrician with maternal care focus.", "rating": "4.7"},
                ],
                "Pediatrics": [
                    {"first_name": "Anupam", "last_name": "Yadav", "specialization": "Pediatrics", "experience_years": 10, "bio": "Pediatrician specializing in immunizations and growth.", "rating": "4.6"},
                    {"first_name": "Divya", "last_name": "Sinha", "specialization": "Pediatric Gastroenterology", "experience_years": 8, "bio": "Child digestive health specialist.", "rating": "4.4"},
                ],
            },
            8: {  # Apex Hospital
                "Cardiology": [
                    {"first_name": "Nikhil", "last_name": "Verma", "specialization": "Cardiology", "experience_years": 11, "bio": "Cardiologist with advanced diagnostic expertise.", "rating": "4.6"},
                ],
                "Orthopedics": [
                    {"first_name": "Yashvant", "last_name": "Bhat", "specialization": "Orthopedic Surgery", "experience_years": 13, "bio": "Orthopedic surgeon with trauma expertise.", "rating": "4.6"},
                ],
                "ENT": [
                    {"first_name": "Vishal", "last_name": "Reddy", "specialization": "ENT", "experience_years": 9, "bio": "Ear, Nose & Throat specialist.", "rating": "4.5"},
                ],
            },
            9: {  # NMC Gaya
                "General Medicine": [
                    {"first_name": "Chandra", "last_name": "Prakash", "specialization": "Internal Medicine", "experience_years": 12, "bio": "General medicine with infectious disease expertise.", "rating": "4.5"},
                ],
                "Pediatrics": [
                    {"first_name": "Alka", "last_name": "Mishra", "specialization": "Pediatrics", "experience_years": 10, "bio": "Child health specialist.", "rating": "4.6"},
                ],
                "Surgery": [
                    {"first_name": "Vivek", "last_name": "Kumar", "specialization": "General Surgery", "experience_years": 11, "bio": "General surgical procedures specialist.", "rating": "4.5"},
                ],
            },
        }

        # Create departments and doctors
        departments = {}
        doctors = []
        
        for hospital_idx, dept_doctors in department_config.items():
            hospital = hospitals[hospital_idx]
            for dept_name, doctor_list in dept_doctors.items():
                # Create department
                dept = Department.objects.create(hospital=hospital, name=dept_name)
                departments[f"{hospital_idx}_{dept_name}"] = dept
                
                # Create doctors for this department
                for doctor_info in doctor_list:
                    doctor = Doctor.objects.create(
                        hospital=hospital,
                        department=dept,
                        **doctor_info
                    )
                    doctors.append(doctor)

        # Weekday schedules (Mon–Fri morning blocks)
        for doc in doctors:
            for wd in list(range(0, 5)) + [5]:  # Mon–Sat for hackathon demos on weekends
                DoctorSchedule.objects.create(
                    doctor=doc,
                    weekday=wd,
                    start_time=dt.time(9, 0),
                    end_time=dt.time(12, 0),
                    slot_minutes=30,
                )
                DoctorSchedule.objects.create(
                    doctor=doc,
                    weekday=wd,
                    start_time=dt.time(13, 0),
                    end_time=dt.time(17, 0),
                    slot_minutes=30,
                )

        # Demo users (password: demo12345 — change immediately in production)
        admin_u = User.objects.create_user(
            username="hospital_admin",
            email="admin@aiimspatna.org",
            password="demo12345",
            role=User.Role.HOSPITAL_ADMIN,
        )
        hospitals[0].admin_user = admin_u
        hospitals[0].save()

        User.objects.create_user(
            username="demo_patient",
            email="patient@demo.com",
            password="demo12345",
            role=User.Role.PATIENT,
        )
        PatientProfile.objects.get_or_create(user=User.objects.get(username="demo_patient"))

        doc_user = User.objects.create_user(
            username="dr_kumar",
            email="rajesh.kumar@aiimspatna.org",
            password="demo12345",
            role=User.Role.DOCTOR,
        )
        doctors[0].user = doc_user
        doctors[0].save()

        self.stdout.write(self.style.SUCCESS(f"Seeded {Hospital.objects.count()} hospitals and demo users."))
        self.stdout.write("Logins: hospital_admin / demo12345 | demo_patient / demo12345 | dr_kumar / demo12345")
