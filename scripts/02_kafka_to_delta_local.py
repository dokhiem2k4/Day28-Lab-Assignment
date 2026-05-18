# Simulate Prefect flow: Kafka -> Delta Lake (runs from host using localhost:9092)
from kafka import KafkaConsumer
import json, os, pandas as pd
from datetime import datetime

consumer = KafkaConsumer(
    "data.raw",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    consumer_timeout_ms=5000,
    value_deserializer=lambda m: json.loads(m.decode())
)

records = [msg.value for msg in consumer]
print(f"Consumed {len(records)} records from Kafka")

if records:
    df = pd.DataFrame(records)
    path = "delta-lake/raw"
    os.makedirs(path, exist_ok=True)
    out = f"{path}/batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet"
    df.to_parquet(out)
    print(f"Integration 2 OK: {len(df)} records saved -> {out}")
else:
    print("No records found in Kafka topic")
