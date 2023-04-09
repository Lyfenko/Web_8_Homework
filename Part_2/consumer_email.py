import pika
from models import Contact
from mongoengine import connect


connect(host='mongodb+srv://lyfenko:KBATYRj2@cluster0.au6w27m.mongodb.net/?retryWrites=true&w=majority')

credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
channel = connection.channel()

channel.queue_declare(queue='email')


def callback(ch, method, properties, body):
    contact_id = body.decode()

    contact = Contact.objects.get(id=contact_id)

    contact.send_by_email = True
    contact.save()

    print(f'Sent email to {contact.full_name} ({contact.email})')


channel.basic_consume(queue='email', on_message_callback=callback, auto_ack=True)

print('Waiting for email messages...')
channel.start_consuming()
