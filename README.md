# LaTeX Editor with Citation Hover (Dockerized)

This project packages a simple LaTeX editor with citation hover functionality into a Docker container.

## Prerequisites

*   Docker installed on your system.

## Building the Docker Image

1.  Navigate to the directory containing the `Dockerfile`, `latex_editor.py`, and `requirements.txt` in your terminal.
2.  Build the Docker image using the following command:

    ```bash
    docker build -t latex-editor .
    ```

    This command will build an image named `latex-editor` in your local Docker repository.

## Running the Docker Container

To run the LaTeX editor in a Docker container, use the following command:

```bash
docker run -it latex-editor