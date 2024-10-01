# Django Chatbot Application Overview

This is a Django-based chatbot application that enables users to create and interact with chatbot flows. It supports creating custom flows with dynamic questions and options, recording user responses, and managing different chatbot types such as rule-based, AI-powered, and more.

## Key Features

- **Flow Creation**: Create chatbot flows with steps, questions, and options.
- **Dynamic Navigation**: Navigate between steps based on user choices.
- **User Response Logging**: Store user responses for future analysis.
- **Excel Upload**: Import flow details via Excel.
- **Multi-Flow Support**: Manage multiple chatbot flows simultaneously.
- **DataTable Interface**: Display user responses with search, filter, and modal preview options.
- **Menu Based Chatbot**: A button-based chatbot that diagnoses the user for different illnesses.
- - **Conversational Chatbot**: A conversation AI  chatbot that diagnoses the users for their period related issues

## Table of Contents

1. [Installation](#installation)
2. [Features](#features)
3. [Usage](#usage)
4. [Models](#models)
5. [API Endpoints](#api-endpoints)
6. [Excel Template](#excel-upload)
7. [Contributing](#contributing)
8. [License](#license)

## Installation

Clone the repository:

```bash
git clone https://github.com/m-toufeeq/django-chatbot.git
cd django-chatbotM
```
Install dependencies:

```bash

pip install -r requirements.txt
```

Run migrations:

```bash

python manage.py migrate
```
Create a superuser to access the Django Admin:

```bash

python manage.py createsuperuser
```
Start the development server:
```bash

python manage.py runserver
```
Features
Flow Creation and Management

    Create and Edit Flows: Users can create and manage their own chatbot flows via an intuitive UI.
    Dynamic Flow Steps: Each step can include multiple options that lead to different subsequent steps based on user choices.

User Responses

    Response Logging: All responses from users interacting with the chatbot are logged in the database for review.
    DataTable Display: Responses are shown in a DataTable with options to preview the entire flow history.

Excel Upload

    Import chatbot flows via a pre-defined Excel template. This feature supports bulk flow creation for easier management.

Usage
Create a Chatbot Flow

    Go to the flow creation page.
    Add a flow name and description.
    Add steps with corresponding options, and define the next step for each option.
    Save the flow to be used by users.

Interact with a Chatbot

    Navigate to the chatbot page.
    Select the flow you want to interact with.
    Follow the chatbot's questions and choose your responses.

View User Responses

    Go to the user responses page.
    View all responses in the DataTable.
    Click on the 'Preview' button to see full details of a user’s interaction with a flow.

Models

    Flow: Contains the flow name and description.
    FlowStep: Represents each step within a flow, including step number, text, and whether it's the final step.
    FlowOption: Stores options for each step, with the text and next step number.
    UserResponse: Logs user responses to flow steps, with response text and date.

API Endpoints

    GET /flows: Get all flows.
    POST /create-flow: Create a new flow.
    POST /upload-excel: Upload Excel file to create flows.

Contributing

We welcome contributions to improve this project! To contribute:

    Fork the repository.
    Create a new branch for your feature or bugfix.
    Commit your changes and submit a pull request.

License

This project is licensed under the MIT License. See the LICENSE file for more information.
