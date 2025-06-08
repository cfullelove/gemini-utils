# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY main.py .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
# The GOOGLE_API_KEY must be passed in at runtime
# e.g., docker run -e GOOGLE_API_KEY="your_api_key" -p 8000:8000 <image_name>
ENV GOOGLE_API_KEY=""

# Run main.py when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
