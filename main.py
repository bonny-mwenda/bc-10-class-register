"""
Usage:
    register create_user <username> <password>
    register create_student <student_name>
    register create_class <class_name>
    register log_start <class_id>
    register log_end <class_id>
    register check_in <student_id> <class_id>
    register check_out <student_id> <class_id>
    register list_classes
    register list-students
    register classes_log
    register students_log
    register delete_class <class_id>
    register delete_student <student_id>
    register (-i | --interactive)
    register (-h | --help | --version)

Options:
    -i, --interactive  Interactive Mode
    -h, --help  Show this screen and exit.

Examples:
    register create_student <"Good Student">
    register create_class <"Example>
    register check_in <1> <1>
"""

import sys
from docopt import docopt, DocoptExit
from termcolor import cprint
import cmd
import time
from tabulate import tabulate
from peewee import *
from models import User, Class_, Student, Checkin, Checkout_Log

db = SqliteDatabase('register.db')


def docopt_cmd(func):
    """Pass the arguments from docopt to the commands"""

    def fn(self, arg):
        try:
            opt = docopt(fn.__doc__, arg)

        except DocoptExit as e:
            # The DocoptExit is thrown when the args do not match.
            # We print a message to the user and the usage block.

            print('Invalid Command!')
            print(e)
            return

        except SystemExit:
            # The SystemExit exception prints the usage for --help
            # We do not need to do the print here.

            return

        return func(self, opt)

    fn.__name__ = func.__name__
    fn.__doc__ = func.__doc__
    fn.__dict__.update(func.__dict__)
    return fn


class Register(cmd.Cmd):
    """Class register cli."""

    prompt = 'class register > '
    intro = "Class register cli."

    db.connect
    global tables
    tables = [User, Student, Class_, Checkin, Checkout_Log]
    file = None

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

    @docopt_cmd
    def do_create_user(self, args):
        """Usage: create_user <username> <password>"""

        username = args["<username>"]
        password = args["<password>"]

        new_user = User.create(username=username, password=password)
        new_user.save()
        cprint("Created new user:\nName: {0}\tid: {1}".format(
            new_user.username, new_user.id), 'green', 'on_grey')

    @docopt_cmd
    def do_create_student(self, args):
        """Usage: create_student <student_name>"""

        student_name = args["<student_name>"]
        checked_in = False

        new_student = Student.create(
            student_name=student_name, checked_in=checked_in)
        new_student.save()
        cprint("Created new student:\nName: {0}\tid: {1}".format(
            new_student.student_name, new_student.id), 'green', 'on_grey')

    @docopt_cmd
    def do_check_in(self, args):
        """Usage: check_in <student_id> <class_id>"""

        student_id = int(args["<student_id>"])
        class_id = int(args["<class_id>"])

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

    @docopt_cmd
    def do_check_out(self, args):
        """Usage: check_out <student_id> <class_id>"""

        student_id = int(args["<student_id>"])
        class_id = int(args["<class_id>"])

        student = Student.get(Student.id == student_id)
        class_ = Class_.get(Class_.id == class_id)

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

    @docopt_cmd
    def do_delete_student(self, arg):
        """Usage: delete_student <student_id>"""

        student_id = int(arg["<student_id>"])
        student = Student.get(Student.id == student_id)
        student.delete_instance()
        cprint("Student was successfully deleted")

    @docopt_cmd
    def do_create_class(self, args):
        """Usage: create_class <class_name>"""

        class_name = args["<class_name>"]
        session = False

        new_class = Class_.create(class_name=class_name, session=session)
        new_class.save()
        cprint("Created new class:\nName: {0}\tid: {1}".format(
            new_class.class_name, new_class.id), 'green', 'on_grey')

    @docopt_cmd
    def do_log_start(self, arg):
        """Usage: log_start <class_id>"""

        class_id = int(arg["<class_id>"])
        class_instance = Class_.get(Class_.id == class_id)
        start = time.time()

        if class_instance.session:
            cprint("{} is already in session".format(
                class_instance.class_name), 'red')
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

    @docopt_cmd
    def do_end(self, arg):
        """Usage: log_end <class_id>"""

        class_id = int(arg["<class_id>"])
        end = time.time()
        class_instance = Class_.get(Class_.id == class_id)

        if not class_instance.session:
            cprint("{} is not in session".format(
                class_instance.class_name), 'red')
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

    @docopt_cmd
    def do_delete_class(self, arg):
        """Usage: delete_class <class_id>"""

        class_id = int(arg["<class_id>"])
        class_ = Class_.get(Class_.id == class_id)
        class_.delete_instance()
        cprint("Class was successfully deleted")

    @docopt_cmd
    def do_list_users(self, args):
        """Usage: list_users."""

        for user in User.select():
            cprint(user.username, 'green', 'on_grey')

    @docopt_cmd
    def do_list_students(self, args):
        """Usage: list_students"""

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
        print(tabulate(table, headers, tablefmt="simple"))

    @docopt_cmd
    def do_list_classes(self, args):
        """Usage: list_classes"""

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
        print(tabulate(table, headers, tablefmt="simple"))

    @docopt_cmd
    def do_classes_log(self, args):
        """Usage: classes_log <student_id>"""

        student_id = int(args["<student_id>"])
        table = []
        added = []
        headers = ["Id", "class"]

        log = Checkin.select().where(Checkin.student_id == student_id).distinct()
        for item in log:
            if item.id not in added:
                table.append([item.class_.id, item.class_.class_name])
            else:
                pass
            added.append(item.id)
        print(tabulate(table, headers, tablefmt="simple"))

    @docopt_cmd
    def do_students_log(self, args):
        """Usage: students_log <class_id>"""

        class_id = int(args["<class_id>"])
        res = set()
        log = Checkin.select().where(Checkin.class__id == class_id)
        for item in log:
            res.add(item.student.student_name)
        for val in res:
            print(val)

    @docopt_cmd
    def do_exit(self, args):
        cprint("Thanks for using class register", 'green', 'on_grey')
        exit()


opt = docopt(__doc__, sys.argv[1:])

if opt['--interactive']:
    Register().cmdloop()

print(opt)
