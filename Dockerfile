# Use a slim Python image for smaller size
FROM python:3.10-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file (we'll create this next)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Command to run the application
# We'll use a wrapper script or entrypoint for running,
# but for now, this is the basic command.
CMD ["python", "Elysia.py"]