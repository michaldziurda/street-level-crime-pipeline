FROM python:3.11-slim

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy pipeline scripts
COPY . .

# The command that triggers your script when the container starts
CMD ["python", "pipeline_uk_crime.py"]