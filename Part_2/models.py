from mongoengine import Document, StringField, BooleanField


class Contact(Document):
    full_name = StringField(required=True)
    email = StringField(required=True)
    phone_number = StringField(required=True)
    sent_by_email = BooleanField(default=False)
    send_by_sms = BooleanField(default=False)
