"""Class register module"""

from peewee import *
from termcolor import cprint
import time
from tabulate import tabulate
from models import User, Class_, Student, Checkin, Checkout_Log

db = SqliteDatabase('register.db')
db.connect
tables = [User, Student, Class_, Checkin, Checkout_Log]


def create_tables():
        """Create class register tables.

        Tables:
        users - for signup/signin
        students - record of all students
        class_ - record of all classes
        checkin table - record of classes attended by students
        """

        # Create tables only if they exist
        db.create_tables(tables, safe=True)


def create_user(username, password):
    """Create new user"""

    new_user = User.create(username=username, password=password)
    new_user.save()
    cprint("Created new user:", 'green', 'on_grey')
    cprint("\tName: {0}\n\tid: {1}".format(new_user.username, new_user.id), 'cyan')


def create_student(student_name):
    """Create new student"""

    checked_in = False
    new_student = Student.create(
        student_name=student_name, checked_in=checked_in)
    new_student.save()
    cprint("Created new student:", 'green', 'on_grey')
    cprint("\tId: {0}\n\tName: {1}".format(
        new_student.id, new_student.student_name), 'cyan')


def check_in(student_id, class_id):
    """Checkin student to a class"""

    try:
        student = Student.get(Student.id == student_id)
    except Exception:
        cprint('Student Id Not Found', 'red')
        return
    try:
        class_ = Class_.get(Class_.id == class_id)
    except Exception:
        cprint('Class Not Found', 'red')
        return

    if student.checked_in:
        cprint("{} is already checked in".format(
            student.student_name), 'red', 'on_grey')
    elif not class_.session:
        cprint("{} is not in session".format(
            class_.class_name), 'red', 'on_grey')
    else:
        # Add a check in entry to check_ins table
        check_in = Checkin.create(
            student=student, class_=class_, status=1)
        check_in.save()

        # Set the student's check_in status to true
        qry = Student.update(checked_in=1).where(Student.id == student_id)
        qry.execute()

        cprint("Checked in {} to {} class".format(
            student.student_name, class_.class_name), 'green', 'on_grey')


def check_out(student_id, class_id):
    """Check_out student from a class"""

    try:
        student = Student.get(Student.id == student_id)
    except Exception:
        cprint('Student Not Found', 'red')
        return
    try:
        class_ = Class_.get(Class_.id == class_id)
    except Exception:
        cprint('Class Not Found', 'red')
        return

    # Prevent checking out if class is not in session
    if class_.session == 1:
        cprint(
            "Warning! Class in session. End class to check out student", 'red', 'on_grey')
        cprint("Force checkout? y/N", 'cyan')
        ans = raw_input()
        if ans.lower() == 'y':
            cprint("Reason for checking out {}".format(
                student.student_name), 'cyan')
            text = raw_input()
            log = Checkout_Log.create(
                student_name=student.student_name, student_id=student.id, reason=text)
            log.save()

            check_out = Checkin.update(status=0).where(
            (Checkin.student_id == student_id) and (Checkin.class__id == class_id))
            check_out.execute()

            # Set the student's check_in status to false
            qry = Student.update(checked_in=0).where(Student.id == student_id)
            qry.execute()

            cprint("Checked out {} from {}.\n\tReason: {}".format(
                student.student_name, class_.class_name, log.reason), 'cyan', 'on_grey')
    else:
        # Update checked in status to false
        check_out = Checkin.update(status=0).where(
            (Checkin.student_id == student_id)and (Checkin.class__id == class_id))
        check_out.execute()

        # Set the student's check_in status to false
        qry = Student.update(checked_in=0).where(Student.id == student_id)
        qry.execute()

        cprint("Checked out {} from {} class".format(
            student.student_name, class_.class_name), 'green', 'on_grey')


def delete_student(student_id):
    """Delete student"""

    try:
        student = Student.get(Student.id == student_id)
    except Exception:
        cprint("Student not found", 'red')
        return

    student.delete_instance()
    cprint("Student was successfully deleted", 'green', 'on_grey')


def create_class(class_name):
    """Create new class"""

    session = False

    new_class = Class_.create(class_name=class_name, session=session)
    new_class.save()
    cprint("Created new class:\n\tName: {0}\n\tid: {1}".format(
        new_class.class_name, new_class.id), 'green', 'on_grey')


def log_start(class_id):
    """Start a class session"""

    try:
        class_instance = Class_.get(Class_.id == class_id)
    except Exception:
        cprint('Class Not Found', 'red')
        return

    start = time.time()

    if class_instance.session:
        cprint("{} is already in session".format(
            class_instance.class_name), 'red')
    else:
        # Set class session to true
        active = Class_.update(session=1).where(Class_.id == class_id)
        active.execute()

        # Update class time with current start time
        update_start_time = Class_.update(
            start_time=start).where(Class_.id == class_id)
        update_start_time.execute()

        cprint("{0} class is now in session".format(
            class_instance.class_name
        ), 'green', 'on_grey')


def log_end(class_id):
    """End class session"""

    try:
        class_instance = Class_.get(Class_.id == class_id)
    except Exception:
        cprint('Student Not Found', 'red')
        return

    end = time.time()

    if not class_instance.session:
        cprint("{} is not in session".format(
            class_instance.class_name), 'red')
    else:
        # Update end time with current time
        update_end_time = Class_.update(
            end_time=end).where(Class_.id == class_id)
        update_end_time.execute()

        # Set class session to closed
        closed = Class_.update(session=1).where(Class_.id == class_id)
        closed.execute()

        cprint("{0} class has ended".format(
            class_instance.class_name), 'green', 'on_grey')

        # Checkout all students in the class
        for entry in Checkin.select().where(Checkin.class__id == class_id and Checkin.status == 1):
            qry = entry.student.update(checked_in=0)
            qry.execute()

        cprint("Checked out all students", 'green', 'on_grey')


def delete_class(class_id):
    """Delete class"""

    try:
        class_ = Class_.get(Class_.id == class_id)
    except Exception:
        cprint("Class not found", 'red')
        return

    class_.delete_instance()
    cprint("Class was successfully deleted", 'green', 'on_grey')


def list_users():
    """List users"""

    for user in User.select():
        cprint(user.username, 'green', 'on_grey')


def list_students():
    """List all students"""

    # cprint(figlet_format('List of all students:'),
    #       'green', attrs=['bold'])
    cprint("List of all students:", 'cyan', 'on_grey')
    table = []
    headers = ["Id", "Name", "Checked In", "Class"]
    for student in Student.select():
        if student.checked_in:
            sc = Checkin.select().where(Checkin.student_id ==
                                        student.id and Checkin.status == 1).get()
            c = sc.class_.class_name
        else:
            c = ""
        table.append(
            [student.id, student.student_name, student.checked_in, c])
    print(tabulate(table, headers, tablefmt="fancy_grid"))


def list_classes():
    """List all classes"""

    cprint("List of all classes:", 'cyan', 'on_grey')
    table = []
    headers = ["Id", "Name", "In Session", "Students"]
    for class_ in Class_.select():
        if class_.session:
            n = Checkin.select().where((Checkin.class__id == class_.id)
                                       and (Checkin.status == 1))
            count = n.count()
        else:
            count = ""
        table.append([class_.id, class_.class_name, class_.session, count])
    print(tabulate(table, headers, tablefmt="fancy_grid"))


def classes_log(student_id):
    """List all classes a student has ever attended"""

    try:
        log = Checkin.select().distinct().where(Checkin.student_id == student_id)
    except Exception:
        cprint("Student not found", 'red')
        return

    table = []
    added = []
    headers = ["Id", "class"]

    for item in log:
        if item.id not in added:
            table.append([item.class_.id, item.class_.class_name])
        else:
            pass
        added.append(item.id)
    print(tabulate(table, headers, tablefmt="fancy_grid"))


def students_log(class_id):
    """List all students that have ever attended a class"""

    try:
        log = Checkin.select().distinct().where(Checkin.class__id == class_id)
    except Exception:
        cprint("Student not found", 'red')
        return

    table = []
    headers = ["Id", "Student"]
    for item in log:
        table.append([item.student.id, item.student.student_name])
    print(tabulate(table, headers, tablefmt="fancy_grid"))
