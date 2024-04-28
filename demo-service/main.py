import json
import os
import time

import pika

from utils import get_module_logger

app_name = 'demo-service'
log = get_module_logger(app_name)

rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
task_queue_name = os.getenv('TASK_QUEUE_NAME', 'task_queue')
result_queue_suffix = '/result'


def process_task(task_data):
    task_id = task_data['task_id']
    task_action = task_data['action']
    log.info(f"Processing task: {task_id}")

    time.sleep(5)  # Simulate a long-running task
    result = f"Processed task Action Result: {task_id} : {task_action}"  # Replace with actual task processing logic
    log.info(result)
    return result


def on_message(ch, method, properties, body):
    try:
        task_data = json.loads(body.decode())
        task_id = task_data['task_id']
        log.info(f"Received task: {task_data}")
        result = process_task(task_data)

        # Publish the result to the result queue
        result_queue_name = f"{task_id}{result_queue_suffix}"
        ch.queue_declare(queue=result_queue_name, durable=True)
        ch.basic_publish(
            exchange='',
            routing_key=result_queue_name,
            body=json.dumps({'task_id': task_id, 'result': result}),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        log.info(f"Published result for task: {task_id}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        log.error(f"Error processing task: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False, multiple=False)


# Establish a connection to RabbitMQ server
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()

# Declare a queue named 'task_queue'
channel.queue_declare(queue=task_queue_name, durable=True)

# Set up the consumer
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=task_queue_name, on_message_callback=on_message)

log.info('Waiting for tasks. To exit press CTRL+C')
channel.start_consuming()
