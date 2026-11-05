AthletePath is a sports training management application that I developed as part of my COM661 coursework using Python Flask and MongoDB. The main aim of the project is to help athletes organise their training activities and track their progress over time. The application provides a central platform where users can manage goals, tasks, sporting events, bookings, performance records, and personalised training plans.

The project was developed using Python, Flask, MongoDB, Postman, and JWT authentication. These technologies were chosen to create a secure and efficient RESTful API while ensuring reliable data storage and user management.

The application uses a MongoDB database called AthletePath, which contains seven collections: Users, Goals, Tasks, Events, Bookings, PerformanceRecords, and TrainingPlans. These collections store and manage all athlete-related information and support the functionality of the system.

AthletePath allows users to register and log in securely, as well as create, view, update, and delete records. Users can manage their training goals and daily tasks, organise sports events and bookings, record performance results, and view statistics to monitor their progress. JWT authentication is implemented to protect API endpoints and ensure secure access to user data.

To verify the functionality of the system, the API was tested using both Postman and Python's unittest framework. The original API passed 10 Postman assertions and 9 Python unit tests before the code was reorganised into Blueprints. The reorganised version should be tested again against the local MongoDB database before submission.

The Flask application runs locally at http://127.0.0.1:5050 and connects to a local MongoDB database named AthletePath. This database stores all user, training, booking, and performance information required by the application.

## How to run the project

1. Install Python and MongoDB Community Server.

2. Open the project folder in VS Code.

3. Open a terminal and install the required Python packages:
   pip install -r requirements.txt

4. Make sure MongoDB is running on localhost:27017.

5. Import the seven JSON files from the database ZIP into a
   MongoDB database called AthletePath.

6. Create a .env file in the project folder with a JWT_SECRET_KEY.

7. Start the Flask application:
   python app.py

8. Open http://127.0.0.1:5050/api/health to check the API.

9. Use Postman to test the API endpoints.

## Dataset information

I used information from three public datasets for my project.

These included the wger exercise dataset, the Milano Cortina 2026 Olympic event schedule, and a gym members exercise tracking dataset from Kaggle.

I changed parts of the data to fit the needs of AthletePath. I also created sample data for goals, tasks, bookings, users and training plans.

The project uses seven MongoDB collections, including records with nested information.

Some data was taken from public sources, while other records were created for demonstration and testing.

## AI acknowledgement

I used ChatGPT to help me understand Flask, MongoDB, JWT authentication and API testing.

I also used it for guidance when writing and checking code, fixing errors and preparing documentation.

I tested the application using Postman and Python unittest and reviewed the results myself.

## Code structure

`app.py` sets up Flask and JWT and registers the Blueprints. Each folder in `blueprints/` contains the routes for one part of the application. `extensions.py` contains the shared MongoDB connection. `test_api.py` contains API tests.

The modular version has not yet been tested against the local MongoDB database. Run `python -m unittest test_api.py -v` and check the main routes in Postman before using it for submission.


## HTTP Basic Authentication (Postman)
Protected endpoints accept HTTP Basic Auth as well as the existing Bearer JWT.
In Postman, select **Authorization > Basic Auth**. Set **Username** to the email
address of a user registered through `POST /api/register`, and **Password** to
that user's password. Send `GET http://127.0.0.1:5050/api/goals` to verify a
`200 OK` response. Incorrect credentials return `401`.

Basic Auth transmits base64-encoded credentials, not encrypted credentials.
Use it only on localhost for this coursework; deploy with HTTPS if used remotely.
Never put actual passwords or JWTs in shared Postman exports or screenshots.
