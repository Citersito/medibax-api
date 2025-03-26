# Use an official Python runtime as a base
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy main requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy AI model requirements and install
COPY ai/requirements-model.txt ai/requirements-model.txt
RUN pip install --no-cache-dir -r ai/requirements-model.txt

# Copy the entire project
COPY . .

# Expose the Flask API port
EXPOSE 5500

# Run the application
CMD ["python", "run.py"]
