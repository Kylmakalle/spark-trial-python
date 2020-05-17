# Spark Equation trial task

This code base serves as the trial task for Python developers.

## Task
See `Backend Engineer (Python) 3hr Trial.pdf` file.

## Comments on solution

**API Endpoints** - `app/endpoints/products.py`

Five endpoints with - GET for all products, GET for single product, POST, PUT, DELETE methods.

Responses are unified to have a `result` or an `error` key. Requests required to have a valid json and `application/json` mimetype.

Since we have pretty simplified API, any categories and brands are created automatically with product creation. Client should just pass an ID of category or brand.


**Validation logic** - `app/utils/main.py`

Firstly, all the requests must be validated with json scheme, which is done by in-built flask function `request.get_json()`.

Then we're validating incoming json with database scheme via `is_valid_json_for_model` function.

We're comparing column type from model with incoming type from json. This function allows us to change DB model without changing validation process. Some of the types may require manual conversion, like `datetime`, `date` and etc.


`validate_product_obj` - here's some business logic we need in task.

`validate_category` & `validate_brand` - automatic parsing and creation categories and brands.


Tests coverage is about `76%`, some exceptions are not tested.

**Additionaly**, docker container provided in this solution, `alpine` image used for container.


## Code characteristics

* Works on Python 2.6, 2.7, 3.3, 3.4, 3.5 and 3.6

## Setting up a development environment

We assume that you have `virtualenv` and `virtualenvwrapper` installed.

    # Create the virtual environment
    mkvirtualenv -p PATH/TO/PYTHON python_trial

    # Install required Python packages
    workon python_trial
    pip install -r requirements.txt


# Adding settings

Copy the `local_settings_example.py` file to `local_settings.py`.

    cp app/local_settings_example.py app/local_settings.py

Edit the `local_settings.py` file.


## Initializing the Database

    # Create DB tables and populate the tables
    python manage.py db upgrade


## Running the app

    # Start the Flask development web server
    python manage.py runserver

Point your web browser to http://localhost:5000/products


## Running the automated tests

    # Run tests
    py.test tests/


## Trouble shooting

If you make changes in the Models and run into DB schema issues, delete the sqlite DB file `app.sqlite`.
