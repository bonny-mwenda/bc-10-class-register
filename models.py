from peewee import *
from playhouse.migrate import *

db = SqliteDatabase('register.db')
migrator = SqliteMigrator(db)


class BaseModel(Model):
    """Base class that specifies the database."""

    class Meta:
        database = db


class User(BaseModel):
    """Users model."""

    username = CharField()
    password = CharField()


class Student(BaseModel):
    """Students model."""

    student_name = CharField()
    checked_in = BooleanField()


class Class_(BaseModel):
    """Class in model."""

    class_name = CharField()
    session = BooleanField()
    start_time = DateTimeField(default=0)
    end_time = DateTimeField(default=0)


class Checkout_Log(BaseModel):
    """Chekout model."""

    student_name = CharField()
    reason = TextField()


class Checkin(BaseModel):
    """Checkin model."""

    student = ForeignKeyField(Student, related_name='students')
    class_ = ForeignKeyField(Class_, related_name='classes')
    no_of_checkins = IntegerField(default=0)
    status = BooleanField()


class CheckinHistory(BaseModel):
    # student_id = ForeignKeyField(User, related_name='students')
    # class_id = ForeignKeyField(Class_, related_name='classes')
    no_of_checkins = IntegerField(default=0)
