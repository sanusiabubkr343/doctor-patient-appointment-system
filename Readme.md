# Doctor-Patient Appointment System

This project is a system designed to facilitate the interaction between doctors and patients by enabling appointment scheduling and management.

## API Documentation

Access the API documentation at: [API Docs](http://127.0.0.1:8000/api/v1/docs#/)

## Features

1. **Doctor Registration**
  - Doctors can register and provide their details.
  - Capture doctor’s work experience.
  - Capture doctor’s academic history.

2. **Patient Registration**
  - Patients can register and create their profiles.

3. **Doctor Availability Setup**
  - Doctors can set up their availability for the week (e.g., on Tuesday, the doctor is free from 10 AM - 2 PM).

4. **Appointment Booking**
  - Patients can book appointments with doctors based on their availability.

5. **Appointment Management**
  - Doctors can cancel appointments.
  - Patients can reschedule appointments.

## Getting Started

Follow the instructions in the API documentation to interact with the system.


## How to Start the Application

1. **Create a `.env` File**  
  Create a `.env` file in the root directory of the project with the following sample content:
  ```env
  DATABASE_URL=postgresql://user:password@localhost:5432/doctor_patient_db
  SECRET_KEY=your_secret_key
  DEBUG=True
  ```

## How to Run the Docker File

2. **Build and Run the Docker Container**

### Step 1: Build the Docker Image
Run the following command to build the Docker image:
```bash
docker build -t doctor-patient-appointment-system .
```

### Step 2: Run the Docker Container
Run the Docker container, passing environment variables from the `.env` file:
```bash
docker run -p 8000:8000 --env-file .env doctor-patient-appointment-system
```

The application will be accessible at: [http://127.0.0.1:8000/api/v1/docs#/](http://127.0.0.1:8000/api/v1/docs#/)
