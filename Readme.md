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



## How to Run the Docker File

1. **Create a `.env` File**  
  Copy the content of `.env.sample` into a new `.env` file in the root directory of the project.
  ```plaintext
  # Web App Environment Variables
  SECRET_KEY=your-secret-key
  ALGORITHM=HS256
  ACCESS_TOKEN_EXPIRE_MINUTES=30
  DATABASE_URL=postgresql://postgres:postgrespw@db:5432/la-hospital

  # PostgreSQL Environment Variables
  POSTGRES_USER=postgres
  POSTGRES_PASSWORD=postgrespw
  POSTGRES_DB=la-hospital
  POSTGRES_HOST=db
  POSTGRES_PORT=5432
  ```

2. **Run the Application**  
  Use the following command to start the application:
  ```bash
  docker-compose up --build
  ```

3. **Access the API Documentation**  
  Once the application is running, open your browser and navigate to [http://0.0.0.0:8000/api/v1/docs/](http://0.0.0.0:8000/api/v1/docs/) to use the Swagger UI.

## API Documentation Preview

![image](https://github.com/user-attachments/assets/67a419c2-f9d7-420a-b1bc-ac09ddbd2909)

This image provides a preview of how the API documentation (Swagger UI) looks.

## Running Tests

To run the tests for the application, use the following command:

```bash
docker-compose -f docker-compose.yml run web -c "pytest -vv"
```
## Test Results Preview

![image](https://github.com/user-attachments/assets/789ea20c-ec6d-40e3-8b38-29c1d908d002)

This image provides a preview of the test results when running `pytest`.
