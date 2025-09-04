# Priority API

**Priority** is an API designed for intelligent task management. 

Users can create their own rules for prioritization based on their criteria for what makes tasks important. \
(eg. Tasks in the work category, with a priority tag, and within 2 days of the deadline get a boost of 10 priority points). 
This makes it a fully customizable task prioritization system.


## Tech Stack

-   **Backend Framework**: Flask
-   **Database**: PostgreSQL
-   **ORM**: SQLAlchemy
-   **Database Migrations**: Flask-Migrate
-   **Dependency Management**: Poetry
-   **Validation & Serialization**: Pydantic
-   **Authentication**: Flask-JWT-Extended
-   **API Documentation**: Spectree
-   **Containerization**: Docker & Docker Compose


## Setup

1. Create environment file

`cp .env.example .env`

2. Build and run the Docker containers:

`docker compose up --build`  

3. Run database migrations in a new terminal:
    
`docker compose exec web flask db upgrade`

The application is now running on `http://localhost:8000`

The interactive and documented API with examples can be accessed at: 

```http://localhost:8000/apidoc/swagger```

There is an authorize button where the access token can be put to access all endpoints.
