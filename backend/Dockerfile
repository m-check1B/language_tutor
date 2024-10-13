# Use an official Python runtime as a parent image
FROM python:3.9-slim as builder

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev

# Copy the current directory contents into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --user --no-cache-dir -r requirements.txt

# Start a new stage
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Copy the current directory contents into the container at /app
COPY . .

# Make sure scripts in .local are usable:
ENV PATH=/root/.local/bin:$PATH

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run app when the container launches
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
