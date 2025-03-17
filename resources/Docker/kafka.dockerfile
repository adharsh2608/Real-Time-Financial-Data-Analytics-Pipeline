# Use a base image with Python
FROM python:3.9-slim

# Install confluent-kafka
RUN pip install confluent-kafka pandas debugpy && mkdir -p /app/data

# Set up environment variables for Kafka configuration
ENV KAFKA_BROKER=kafka:9092
ENV KAFKA_TOPIC=my-topic

# Copy the producer.py script from the src folder (relative to the build context)
COPY ./src/producer.py /app/producer.py
COPY ./src/sleep.sh /app/sleep.sh

# Set the working directory
WORKDIR /app

RUN chmod -R 777 /app

RUN mkdir -p /app/instances


#CMD ["sh", "sleep.sh"]
# Command to run your producer
CMD ["python", "/app/src/producer.py"]
