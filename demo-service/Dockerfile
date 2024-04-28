# Dockerfile for Python Microservice

# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy just the requirements.txt first to leverage Docker cache
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the codebase into the container
COPY . .

# Set environment variables
ENV RABBITMQ_HOST=rabbitmq
ENV QUEUE_NAME=task_queue

# The command to run the microservice
CMD ["python", "./main.py"]