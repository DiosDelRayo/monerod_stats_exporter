# Use a lightweight Python image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the Python script and configuration files
COPY prometheus_exporter.py config.yaml /app/

# Install required Python libraries
RUN pip install prometheus-client requests pyyaml

# Expose the default Prometheus exporter port
EXPOSE 9123

# Run the Prometheus exporter
CMD ["python", "prometheus_exporter.py"]

