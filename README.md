# LaTeX Editor with Citation Hover (Dockerized)

This project packages a simple LaTeX editor with citation hover functionality into a Docker container.

## Prerequisites

*   Docker and Docker Compose installed on your system.

## Running the Application with Docker Compose

1. Navigate to the directory containing the `docker-compose.yml` file.
2. Start the application using Docker Compose:

    ```bash
    docker-compose up --build
    ```

    This command will build and run the container.

3. Access the application in your browser at:

    ```
    http://localhost:8080
    ```

## Stopping the Application

To stop the running containers, use:

```bash
docker-compose down
```

This will shut down the application and remove the running containers.