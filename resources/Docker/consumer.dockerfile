# Use the official Flink image as the base
FROM flink:1.16

# Set environment variables
ENV PYTHON_VERSION=3.8.16 \
    TZ=UTC \
    JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# Install required dependencies for building Python and other tools
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libffi-dev \
    openjdk-11-jdk \
    libreadline-dev \
    liblzma-dev \
    libsqlite3-dev \
    wget \
    tzdata && \
    ln -sf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Set JAVA_HOME for PyFlink
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64



# Build and install Python 3.8 from source
RUN wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz && \
    tar -xvf Python-${PYTHON_VERSION}.tgz && \
    cd Python-${PYTHON_VERSION} && \
    ./configure --enable-optimizations && \
    make -j4 && \
    make altinstall && \
    cd .. && \
    rm -rf Python-${PYTHON_VERSION}* && \
    ln -sf /usr/local/bin/python3.8 /usr/bin/python3 && \
    ln -sf /usr/local/bin/pip3.8 /usr/bin/pip3

RUN ln -sf /usr/local/bin/python3.8 /usr/bin/python3 && \
ln -sf /usr/local/bin/python3.8 /usr/bin/python && \
ln -sf /usr/local/bin/pip3.8 /usr/bin/pip3 && \
ln -sf /usr/local/bin/pip3.8 /usr/bin/pip
# Expose the port for Prometheus metrics

# Download Flink Kafka connector JAR
RUN wget -q -O /opt/flink/lib/flink-connector-kafka.jar \
    https://repo1.maven.org/maven2/org/apache/flink/flink-connector-kafka/1.16.2/flink-connector-kafka-1.16.2.jar

# Download Kafka client JAR
RUN wget -q -O /opt/flink/lib/kafka-clients.jar \
    https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.3.2/kafka-clients-3.3.2.jar

# Install Python packages
RUN pip install --no-cache-dir pyflink apache-flink prometheus_client debugpy



# Copy the Flink consumer code into the container
COPY ./src/consumer.py /app/consumer.py

RUN mkdir -p /app/instances

COPY ./src/sleep.sh /app/sleep.sh
RUN chmod -R 777 /app
# Set the working directory inside the container
WORKDIR /app/src
RUN cd /app/src

CMD ["python",  "/app/src/consumer.py"]
