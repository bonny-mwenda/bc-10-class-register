from termcolor import cprint
import cmd
import time
from peewee import *
from models import User, Class_, Student, Checkin

db = SqliteDatabase('register.db')


class Register(cmd.Cmd):
    """Class register cli."""

    prompt = 'class register > '
    intro = "A class register cli."

    def do_create_tables(self, args):
        """Create class register tables.

        Tables:
        users - for signup/signin
        students - record of all students
        class_ - record of all classes
        checkin table - record of classes attended by students
        """

        db.connect
        tables = [User, Student, Class_, Checkin]

        # Create tables only if they exist
        db.create_tables(tables, safe=True)
        for table in tables:
            cprint("Sucessfully created {}s table".format(table))

    def do_drop_tables(self, args):
        """Drop all tables."""

        db.connect
        tables = [User, Student, Class_]
        for table in tables:
            if db.drop_table(table):
                cprint("Sucessfully removed {}s table".format(table))

    def do_create_user(self, args):
        """Create a new user."""

        params = args.split()
        username = params[0]
        password = params[1]

        new_user = User.create(username=username, password=password)
        new_user.save()
        cprint("Created new user:\nName: {0}\tid: {1}".format(
            new_user.username, new_user.id), 'green', 'on_grey')

    def do_create_student(self, args):
        """Create a new student."""

        student_name = args
        checked_in = False

        new_student = Student.create(
            student_name=student_name, checked_in=checked_in)
        new_student.save()
        cprint("Created new student:\nName: {0}\tid: {1}".format(
            new_student.student_name, new_student.id), 'green', 'on_grey')

    def do_check_in(self, args):
        """Check in student to a class"""

        params = args.split()
        student_id = params[0]
        class_id = params[1]

        # Add a check in entry to check_ins table
        check_in = Checkin.create(
            student_id=student_id, class_id=class_id, status=True)
        check_in.save()

        print("checked in student")

        # cprint("Checked in {} to {} class".format(
        #    check_in.student_id, check_in.class_id), 'green', 'on_grey')

    def do_check_out(self, args):
        """Check out student from a class."""

        params = args.split()
        student_id = params[0]
        class_id = params[1]

        # Update checked in status to false
        check_out = Checkin.update(status=False).where(
            Checkin.student_id == student_id and Checkin.class_id == class_id)
        check_out.execute()

        # cprint("Checked out {} from {} class".format(
        #    check_out.student_name, check_out.class_name), 'green', 'on_grey')

    def do_delete_student(self, arg):
        """Delete student."""

        student_id = int(arg)
        student = Student.get(Student.id == student_id)
        student.delete_instance()
        cprint("Student was successfully deleted")

    def do_create_class(self, args):
        """Create a new class."""

        class_name = args
        session = False

        new_class = Class_.create(class_name=class_name, session=session)
        new_class.save()
        cprint("Created new class:\nName: {0}\tid: {1}".format(
            new_class.class_name, new_class.id), 'green', 'on_grey')

    def do_start(self, arg):
        """Start a class session."""

        class_id = int(arg)
        class_instance = Class_.get(Class_.id == class_id)
        start = time.time()

        # Set class session to true
        active = Class_.update(session=True).where(Class_.id == class_id)
        active.execute()

        # Update class time with current start time
        update_start_time = class_instance.update(
            start_time=start)
        update_start_time.execute()

        cprint("{0} class is now in session. Start time: {1}".format(
            class_instance.class_name, class_instance.start_time))

    def do_end(self, arg):
        """End a class session."""

        class_id = int(arg)
        end = time.time()
        class_instance = Class_.get(Class_.id == class_id)

        # Update end time with current time
        update_end_time = class_instance.update(
            end_time=end)
        update_end_time.execute()

        # Set class session to closed
        closed = Class_.update(session=False).where(Class_.id == class_id)
        closed.execute()

        cprint("{0} class has ended. End time: {1}".format(
            class_instance.class_name, class_instance.end_time))

    def do_delete_class(self, arg):
        """Delete class."""

        class_id = int(arg)
        class_ = Class_.get(Class_.id == class_id)
        class_.delete_instance()
        cprint("Class was successfully deleted")

    def do_list_users(self, args):
        """List class register signed up users."""

        for user in User.select():
            cprint(user.username, 'green', 'on_grey')

    def do_list_students(self, args):
        """List students."""

        cprint("List of all students:", 'cyan', 'on_grey')
        for student in Student.select():
            if student.Checkin and student.Checkin.status:
                cprint("\tName: {0}\n\tChecked In: {1}".format(
                    student.student_name, student.Checkin.status), 'green', 'on_grey')
                print("\n")
            cprint("\tName: {0}\n\tChecked In: False".format(
                student.student_name), 'green', 'on_grey')
            print("\n")

    def do_list_classes(self, args):
        """List students."""

        cprint("List of all classes:", 'cyan', 'on_grey')
        for class_ in Class_.select():
            cprint("\tid: {0}\n\tName: {1}\n\tSession Status: {2}".format(class_.id,
                                                                          class_.class_name, class_.session), 'green', 'on_grey')
            print("\n")

    def do_exit(self, args):
        cprint("Good bye!", 'green', 'on_grey')
        exit()


if __name__ == '__main__':
    Register().cmdloop()
