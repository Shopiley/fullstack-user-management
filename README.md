# moni-africa-backend-test
## Project Structure

This project is a monolith application. You will find three folders namely:

1. backend
2. frontend

Depending on your track, you are to work in the folder that concerns you.

## Setup

### Backend

- Fork this repository to have a copy of it in your own github account
- Clone the forked repo to your PC, this gives you access to the repo locally
- Install Python from <https://www.python.org/downloads/> if you haven't
- cd into the project folder
- cd into the backend folder
- Ensure a virtual environment has been created and activated by either using

    ```bash
    python -m venv venv # to create a virtualenv
    source venv/bin/activate # activate for linux
    venv\Scripts\activate # activate for windows
    ```

- Install all dependencies

  ```bash
  pip install -r requirements.txt
  ```

- Run the somman below to start the server

  ```bash
  uvicorn main:app --reload
  ```
