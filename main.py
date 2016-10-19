from termcolor import cprint
import cmd
import time
from peewee import *
from models import User, Class_, Student, Checkin, Checkout_Log

db = SqliteDatabase('register.db')


class Register(cmd.Cmd):
    """Class register cli."""

    prompt = 'class register > '
    intro = "A class register cli."

    db.connect
    global tables
    tables = [User, Student, Class_, Checkin, Checkout_Log]

    def do_create_tables(self, args):
        """Create class register tables.

        Tables:
        users - for signup/signin
        students - record of all students
        class_ - record of all classes
        checkin table - record of classes attended by students
        """

        # Create tables only if they exist
        db.create_tables(tables, safe=True)
        for table in tables:
            cprint("Sucessfully created {}s table".format(table))

    def do_drop_tables(self, args):
        """Drop all tables."""

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
        student_id = int(params[0])
        class_id = int(params[1])

        student = Student.get(Student.id == student_id)
        class_ = Class_.get(Class_.id == class_id)

        if student.checked_in:
            cprint("{} is already checked in".format(
                student.student_name), 'red', 'on_grey')
        elif not class_.session:
            cprint("{} is not in session".format(
                class_.class_name), 'red', 'on_grey')
        else:
            # Add a check in entry to check_ins table
            check_in = Checkin.create(
                student=student, class_=class_, status=True)
            check_in.save()

            # Set the student's check_in status to true
            qry = Student.update(checked_in=1).where(Student.id == student_id)
            qry.execute()

            cprint("Checked in {} to {} class".format(
                student.student_name, class_.class_name), 'green', 'on_grey')

    def do_check_out(self, args):
        """Check out student from a class."""

        params = args.split()
        student_id = int(params[0])
        class_id = int(params[1])

        student = Student.get(Student.id == student_id)
        class_ = Class_.get(Class_.id == class_id)

        # Prevent checking out if class is not in session
        if class_.session == 1:
            cprint("Warning! Class in session. End class to check out student", 'red', 'on_grey')
            cprint("Force checkout? y/N", 'cyan')
            ans = raw_input()
            if ans.lower() == 'y':
                cprint("Reason for checking out {}".format(
                    student.student_name), 'cyan')
                text = raw_input()
                log = Checkout_Log.create(student_name=student.student_name, student_id=student.id, reason=text)
                log.save()
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

        if class_instance:
            cprint("{} is already in session".format(class_instance.class_name), 'red')
        else:
            # Set class session to true
            active = Class_.update(session=True).where(Class_.id == class_id)
            active.execute()

            # Update class time with current start time
            update_start_time = Class_.update(
                start_time=start).where(Class_.id == class_id)
            update_start_time.execute()

            cprint("{0} class is now in session. Start time: {1}".format(
                class_instance.class_name, class_instance.start_time))

    def do_end(self, arg):
        """End a class session."""

        class_id = int(arg)
        end = time.time()
        class_instance = Class_.get(Class_.id == class_id)

        if not class_instance.session:
            cprint("{} is not in session".format(class_instance.class_name), 'red')
        else:
            # Update end time with current time
            update_end_time = Class_.update(
                end_time=end).where(Class_.id == class_id)
            update_end_time.execute()

            # Set class session to closed
            closed = Class_.update(session=False).where(Class_.id == class_id)
            closed.execute()

            cprint("{0} class has ended. End time: {1}".format(
                class_instance.class_name, class_instance.end_time))

            # Checkout all students in the class
            for entry in Checkin.select().where(Checkin.class__id == class_id and Checkin.status == 1):
                qry = entry.student.update(checked_in=0)
                qry.execute()

            cprint("Checked out all students", 'green', 'on_grey')

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
            if student.checked_in:
                sc = Checkin.select().where(Checkin.student_id ==
                                            student.id and Checkin.status == 1).get()
                cprint("\tId: {}\n\tName: {}\n\tChecked In: {}\n\tClass: {}".format(student.id,
                                                                                    student.student_name, student.checked_in, sc.class_.class_name), 'green', 'on_grey')
                print("\n")
            cprint("\tId: {}\tName: {}\n\tChecked In: False".format(student.id,
                                                                    student.student_name), 'green', 'on_grey')
            print("\n")

    def do_list_classes(self, args):
        """List students."""

        cprint("List of all classes:", 'cyan', 'on_grey')
        for class_ in Class_.select():
            if class_.session:
                n = Checkin.select().where((Checkin.class__id == class_.id)
                                           and (Checkin.status == 1))
                cprint("\tid: {0}\n\tName: {1}\n\tSession Status: {2}\n\tStudents: {3}".format(
                    class_.id, class_.class_name, class_.session, n.count()), 'green', 'on_grey')
                print("\n")
            else:
                cprint("\tid: {0}\n\tName: {1}\n\tSession Status: {2}".format(
                    class_.id, class_.class_name, class_.session), 'green', 'on_grey')
                print("\n")

    def do_class_log(self, args):
        """List classes that a student has attended."""

        student_id = int(args[0])
        c_log = set()

        log = Checkin.select().where(Checkin.student_id == student_id)
        for item in log:
            c_log.add(item.class_.class_name)
        for val in c_log:
            print(val)

    def do_student_log(self, args):
        """List students that have ever attended a class."""

        class_id = int(args[0])
        res = set()
        log = Checkin.select().where(Checkin.class__id == class_id)
        for item in log:
            res.add(item.student.student_name)
        for val in res:
            print(val)

    def do_exit(self, args):
        cprint("Good bye!", 'green', 'on_grey')
        exit()


if __name__ == '__main__':
    Register().cmdloop()
