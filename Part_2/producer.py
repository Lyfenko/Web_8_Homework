import pika
from faker import Faker
from models import Contact
from mongoengine import connect


connect(host='mongodb+srv://lyfenko:KBATYRj2@cluster0.au6w27m.mongodb.net/?retryWrites=true&w=majority')


credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
channel = connection.channel()


channel.queue_declare(queue='email')
channel.queue_declare(queue='sms')


fake = Faker()
for i in range(10):
    full_name = fake.name()
    email = fake.email()
    phone_number = fake.phone_number()

    contact = Contact(full_name=full_name, email=email, phone_number=phone_number)

    contact.save()

    channel.basic_publish(exchange='', routing_key='email', body=str(contact.id).encode())

    channel.basic_publish(exchange='', routing_key='sms', body=str(contact.id).encode())

connection.close()
