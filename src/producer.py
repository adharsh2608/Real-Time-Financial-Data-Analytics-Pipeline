from confluent_kafka import Producer
import os
import pandas as pd
import json
import time

#time.sleep(60)

KAFKA_BROKER = "kafka:9092"
TOPIC = "stock_prices"

# Configure Kafka Producer
producer_config = {
    'bootstrap.servers': KAFKA_BROKER,
    'client.id': 'stock-producer'
}
producer = Producer(producer_config)

# Function to deliver messages
def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")
    else:
        print(f"Delivered message {msg.value()} to {msg.topic()} [{msg.partition()}]")
        

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

# Read CSV files and publish to Kafka
def publish_to_kafka(dataset_dir):
    batch_size = 10000  # Flush after every 500 messages
    message_count = 0  # Counter to track messages in the current batch
    message_number = 0  # Counter to track total messages processed
    while True:
        try:
            instance = get_instance("/app/instances/producer_instance.txt")
            break
        except:
            continue
    
    for file in split_array(sorted(os.listdir(dataset_dir)))[instance]:
        print(f"Processing file: {file}")
        if file.endswith("_minute.csv"):
            stock_name = file.split("_minute")[0]
            file_path = os.path.join(dataset_dir, file)
            data = pd.read_csv(file_path)        
            for _, row in data.iterrows():
                if message_number >= 20000:
                    producer.flush()
                    message_count = 0
                    message_number = 0
                    print("going to the next file")
                    break
                message_number += 1
                print(f"Processing message: {message_number}")
                message = {
                    "stock": stock_name,
                    "timestamp": row['date'],
                    "open": row['open'],
                    "high": row['high'],
                    "low": row['low'],
                    "close": row['close'],
                    "volume": row['volume']
                }
                # Produce message to Kafka
                producer.produce(stock_name, json.dumps(message), callback=delivery_report)
                message_count += 1

                # Flush when batch size is reached
                if message_count >= batch_size:
                    producer.flush()
                    message_count = 0  # Reset the counter

    # Flush remaining messages after processing all files
    if message_count > 0:
        producer.flush()
        print(f"Flushed remaining {message_count} messages.")

if __name__ == "__main__":
    time.sleep(60)
    publish_to_kafka("/app/data")
