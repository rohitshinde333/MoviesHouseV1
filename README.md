# MAD-1 Project README

This is a MAD-1 project README with instructions on how to set up the
necessary libraries and Python virtual environment (venv) to run the
project on a Windows machine. API endpoints are also mentioned here.

## Authors

-   Rohit Vishwas Shinde (21f3002241)

## Requirements

Python 3.6+

pip package manager

Flask

Flask-RESTful

Flask-Login

FlaskForm

Flask-Bcrypt

datetime

SQLAlchemy

SQLite

## Installation

This project is developed on windows machine with python virtual
environment.

1.cd to application directory of project

``` bash
  cd application
```

2.Create a virtual environment and activate it:

``` bash
  python -m venv venv
  .\venv\Scripts\activate
```

3.Install the required Python libraries:

``` bash
  pip install -r requirements.txt
```

## Running the project

1.Activate the virtual environment:

``` bash
  venv\Scripts\activate
```

2.Run the Flask application:

``` bash
  python app.py
```

3.Access the application by visiting http://localhost:5000 in your web
browser. \## API Usage 1.API for crud operations on Theatres and shows
is defined in app.py file.

2.The API has the following endpoints: \### Theaters

GET /theaters - Get a list of all theaters

GET /theaters/`<id>`{=html} - Get a theater by ID

POST /theaters - Add a new theater

PUT /theaters/`<id>`{=html} - Update a theater by ID

DELETE /theaters/`<id>`{=html} - Delete a theater by ID

### shows

GET /shows - Get a list of all shows

GET /shows/`<id>`{=html} - Get a show by ID

POST /shows - Add a new show

PUT /shows/`<id>`{=html} - Update a show by ID

DELETE /shows/`<id>`{=html} - Delete a show by ID

### Response Format

The API returns responses in JSON format. The response format for each
endpoint is documented in the API specification.

### API Specification

The API specification is documented in the OpenAPI format and can be
found in the swagger.yaml file in the root directory. The specification
includes details about the request and response formats, authentication,
and available endpoints.
