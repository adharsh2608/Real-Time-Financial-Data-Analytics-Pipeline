from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.datastream import MapFunction
import json
import os
import time

# Kafka Settings
KAFKA_BROKER = "kafka:9092"  # Kafka broker address
INPUT_TOPIC = "stock_prices"  # Kafka topic to consume data from
OUTPUT_FOLDER = "stocks_consumed"  # Folder to store stock data files



# Example of a MapFunction to process the consumed data
class ProcessKafkaData(MapFunction):
    def map(self, value):
        """Process each Kafka record and write to file."""
        # Assuming the incoming data is in JSON format
        data = json.loads(value)
        
        # Extract stock name and write to a file named <stock_name>.json
        stock_name = data['stock']
        file_path = os.path.join(OUTPUT_FOLDER, f"{stock_name}.json")
        
        while True:
            try:
                with open(file_path, "a") as f:
                    f.write(json.dumps(data) + "\n")  # Append data as JSON line
                break
            except Exception as e:
                time.sleep(1)
                continue
        
        print(f"Written record for stock {stock_name}: {data}")
        return value  # You can return the transformed data if necessary

def get_instance(file_path):
    if os.path.exists(file_path):
        # File exists, read the current number, increment by 1
        with open(file_path, 'r') as file:
            current_number = int(file.read().strip())
            if current_number > 2:
                current_number = -1
        new_number = current_number + 1
    else:
        # File does not exist, create it with 0
        new_number = 0
    
    if new_number > 2:
        new_number = 0
    
    # Write the new number back to the file
    with open(file_path, 'w') as file:
        file.write(str(new_number))
    return new_number

def split_array(arr):
    # Ensure the array length is divisible by 3
    if len(arr) % 3 != 0:
        raise ValueError("Array length must be divisible by 3")
    
    # Split the array into 3 equal parts
    part_length = len(arr) // 3
    part1 = arr[:part_length]
    part2 = arr[part_length:2*part_length]
    part3 = arr[2*part_length:]
    
    return [part1, part2, part3]

def main():
    # Set up the Flink environment
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)

    # Kafka consumer configuration
    properties = {
        'bootstrap.servers': KAFKA_BROKER,  # Kafka brokers
        'group.id': 'flink-consumer-group',  # Consumer group ID
    }
    
    #file_names = split_array(sorted(os.listdir("/app/data")))[get_instance("/app/instances/consumer_instance.txt")]
    file_names = sorted(os.listdir("/app/data"))
    topics = [f.replace("_minute.csv", "") for f in file_names]
    
    # Create a Kafka consumer for the topic
    kafka_consumer = FlinkKafkaConsumer(
        topics=topics,  # Kafka topic to read from
        deserialization_schema=SimpleStringSchema(),  # Deserialize each message as a string
        properties=properties  # Kafka properties
    )

    # Add the Kafka consumer as a source in the Flink job
    stream = env.add_source(kafka_consumer)

    # Apply transformations (e.g., MapFunction)
    processed_stream = stream.map(ProcessKafkaData())  # Process each record with custom logic

    # Execute the Flink job
    env.execute("Kafka Consumer Example")

if __name__ == "__main__":
    main()
