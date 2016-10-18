from peewee import *
from playhouse.migrate import *

db = SqliteDatabase('register.db')
migrator = SqliteMigrator(db)


class User(Model):
    username = CharField()
    password = CharField()

    class Meta:
        database = db  # Use register model


class Student(Model):
    student_name = CharField()
    checked_in = BooleanField()

    class Meta:
        database = db  # Use register model


class Class_(Model):
    class_name = CharField()
    session = BooleanField()

    class Meta:
        database = db  # Use register model


class Checkout_Log(Model):
    # student_id = ForeignKeyField(User, related_name='students')
    reason = TextField()

    class Meta:
        database = db  # Use register model


class CurrentCheckins(Model):
    student_id = ForeignKeyField(User, related_name='students')
    class_id = ForeignKeyField(Class_, related_name='classes')
    no_of_checkins = IntegerField(default=0)

    class Meta:
        database = db  # Use register model


class CheckinHistory(Model):
    # student_id = ForeignKeyField(User, related_name='students')
    # class_id = ForeignKeyField(Class_, related_name='classes')
    no_of_checkins = IntegerField(default=0)

    class Meta:
        database = db  # Use register model
