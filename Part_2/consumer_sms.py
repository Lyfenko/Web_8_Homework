import pika
from models import Contact
from mongoengine import connect


connect(host='mongodb+srv://lyfenko:KBATYRj2@cluster0.au6w27m.mongodb.net/?retryWrites=true&w=majority')


credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
channel = connection.channel()


channel.queue_declare(queue='sms')


def callback(ch, method, properties, body):
    contact_id = body.decode()

    contact = Contact.objects.get(id=contact_id)

    contact.send_by_sms = True
    contact.save()

    print(f'Sent SMS to {contact.full_name} ({contact.phone_number})')


channel.basic_consume(queue='sms', on_message_callback=callback, auto_ack=True)

print('Waiting for SMS messages...')
channel.start_consuming()
