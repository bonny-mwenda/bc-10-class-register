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
    register list_students
    register classes_log <student_id>
    register students_log <class_id>
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
# from colorama import Fore, Back, Style
from pyfiglet import Figlet, figlet_format
from termcolor import cprint
import os
import sys
from docopt import docopt, DocoptExit
import cmd
from register import *


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


def intro():
    cprint(figlet_format('Class Register', font='slant'),
           'green', attrs=['bold'])
    cprint(__doc__)


class Register(cmd.Cmd):
    """Class register cli."""

    prompt = 'class register > '
    intro = "Class register cli."

    file = None

    def do_drop_tables(self, args):
        """Drop all tables."""

        for table in tables:
            if db.drop_table(table):
                cprint("Sucessfully removed table", 'cyan')

    @docopt_cmd
    def do_create_user(self, args):
        """Usage: create_user <username> <password>"""

        create_user(args["<username>"], args["<password>"])

    @docopt_cmd
    def do_create_student(self, args):
        """Usage: create_student <student_name>"""

        create_student(args["<student_name>"])

    @docopt_cmd
    def do_check_in(self, args):
        """Usage: check_in <student_id> <class_id>"""

        check_in(int(args["<student_id>"]), int(args["<class_id>"]))

    @docopt_cmd
    def do_check_out(self, args):
        """Usage: check_out <student_id> <class_id>"""

        check_out(int(args["<student_id>"]), int(args["<class_id>"]))

    @docopt_cmd
    def do_delete_student(self, arg):
        """Usage: delete_student <student_id>"""

        delete_student(int(arg["<student_id>"]))

    @docopt_cmd
    def do_create_class(self, args):
        """Usage: create_class <class_name>"""

        create_class(args["<class_name>"])

    @docopt_cmd
    def do_log_start(self, arg):
        """Usage: log_start <class_id>"""

        log_start(int(arg["<class_id>"]))

    @docopt_cmd
    def do_log_end(self, arg):
        """Usage: log_end <class_id>"""

        log_end(int(arg["<class_id>"]))

    @docopt_cmd
    def do_delete_class(self, arg):
        """Usage: delete_class <class_id>"""

        delete_class(int(arg["<class_id>"]))

    @docopt_cmd
    def do_list_users(self, args):
        """Usage: list_users."""

        list_users()

    @docopt_cmd
    def do_list_students(self, args):
        """Usage: list_students"""

        list_students()

    @docopt_cmd
    def do_list_classes(self, args):
        """Usage: list_classes"""

        list_classes()

    @docopt_cmd
    def do_classes_log(self, args):
        """Usage: classes_log <student_id>"""

        classes_log(int(args["<student_id>"]))

    @docopt_cmd
    def do_students_log(self, args):
        """Usage: students_log <class_id>"""

        students_log(int(args["<class_id>"]))

    def do_clear(self, args):
        os.system('clear')

    def do_exit(self, args):
        cprint("Thanks for using class register", 'green', 'on_grey')
        exit()


opt = docopt(__doc__, sys.argv[1:])

if opt['--interactive']:
    create_tables()
    os.system('clear')
    intro()
    Register().cmdloop()

print(opt)
