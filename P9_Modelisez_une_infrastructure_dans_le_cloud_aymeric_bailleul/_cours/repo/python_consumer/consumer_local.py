import base64
from kafka import KafkaConsumer
import json
from decimal import Decimal

def decode_decimal(base64_str, scale=2):
    decoded_bytes = base64.b64decode(base64_str)
    value = int.from_bytes(decoded_bytes, byteorder='big', signed=True)
    return float(value) / (10 ** scale)

consumer = KafkaConsumer(
    'dbz.public.orders',
    bootstrap_servers='localhost:19092',
    group_id='python_consumer_group',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("Starting listener ...")

for msg in consumer:
    payload = msg.value['payload']['after']
    
    order_id = payload['order_id']
    product_name = payload['product_name']
    quantity_sold = payload['quantity_sold']
    promotion = payload['promotion']
    region = payload['region']
    
    total_sales = decode_decimal(payload['total_sales'])
    unit_price = decode_decimal(payload['unit_price'])

    print(f"✅ New order received! ID: {order_id}, Total: {total_sales}€, Region: {region}")



print("End of listener ...")