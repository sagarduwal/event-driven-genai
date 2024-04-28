import uuid

from flask import Flask, request, jsonify
import pika
import json
from pika.exceptions import AMQPError

from utils import get_module_logger

app_name = 'api-gateway'
log = get_module_logger(app_name)

app = Flask(app_name)

rabbitmq_host = 'rabbitmq'
queue_name = 'task_queue'
result_queue_suffix = '/result'



@app.route('/', methods=['GET'])
def index():
    return jsonify({'result': "API Gateway"})


@app.route('/send-task', methods=['POST'])
def send_task():
    try:
        data = request.json
        task = data.get('task')
        log.info(f"Received task: {task}")

        task_id = str(uuid.uuid4())[:8]
        task_details = {
            'name': task['name'],
            'action': task['action'],
            'payload': task['payload'],
            'task_id': task_id
        }
        if not task:
            log.info('No task provided')
            return jsonify({'error': 'No task provided'}), 400

        # Establish a connection to RabbitMQ server
        connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host))
        channel = connection.channel()

        channel.queue_declare(queue=queue_name, durable=True)

        # Publish the message
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(task_details),
            properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
        )

        log.info(f"[x] Sent {str(task_details)}")
        connection.close()

        return jsonify({
            'response': {
                'status': 'Task sent',
                'task_id': task_id
            }}), 202
    except AMQPError as amqpEx:
        log.error('Error with event. Notified...', amqpEx)
        return jsonify({'error': 'Error with event.'})
    except Exception as ex:
        log.error('Something went wrong. Please try again later.', ex)
        return jsonify({'error': 'Something went wrong. Please try again later.'})


@app.route('/get-result/<task_id>', methods=['GET'])
def get_result(task_id):
    try:
        result_queue_name = f"{task_id}{result_queue_suffix}"
        log.info(f"Checking result for task: {task_id}")

        # Establish a connection to RabbitMQ server
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
        channel = connection.channel()

        # Declare the result queue and consume one message
        channel.queue_declare(queue=result_queue_name, durable=True)
        method_frame, header_frame, body = channel.basic_get(queue=result_queue_name, auto_ack=True)

        connection.close()

        if method_frame:
            task_result = json.loads(body.decode())
            # TODO once received result store result in db for the task_id
            return jsonify({'response': task_result}), 200
        else:
            return jsonify({'error': 'No result available yet'}), 404
    except AMQPError as amqpEx:
        log.error('Error with event. Notified...', amqpEx)
        return jsonify({'error': 'Error with event.'})
    except Exception as ex:
        log.error('Something went wrong. Please try again later.', ex)
        return jsonify({'error': 'Something went wrong. Please try again later.'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
