# Class Attendance Register
## Introduction
Class attendance register app is a command line application built using Python that enables a user, such as a teacher or instructor to:
* Create new students
* Create new classes
* Start and end class sessions
* Check in and check out students from classes
* List all classes and show number of students in the class if it is in session
* List all students and show their check in status. If they are checked into a class, show the name of the class.
* Display a record of all the classes a student has attended
* Display a record of all the students that have attended a class

## Requirements
The app works with Python 2.7 and has these dependencies:
* [Peewee](http://docs.peewee-orm.com/en/latest/index.html) ORM for modelling database
* [docopt](https://github.com/docopt/docopt) for parsing commands
* Pyfiglet and termcolor for styling


## How to install
* Clone this repo to your local drive and `cd` to the root folder (bc-10-class-register).
* Install a virtual environment, preferably [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/) in this folder and activate it.
* Use a python package installer, such as `pip` for Linux to install the requirements specified in requirements.txt.

	`$ pip install -r requirements.txt`

* Launch the app by executing `main.py` and specify the docopt interactive option, `-i` or `--interactive` to run the app in interactive mode.

	`$ python main.py -i`
* The class attendance is now up running. The usage commands are well documented, and can be accessed any time by passing the `-h` or `--help` option. 

## Usage Example
- Start by creating students and classes.
- Add a new student:	`>> create_student Example`
- Add a new class:	`>> create_class Myclass`
- **Start a class session**:	`>> log_start <class_id>`
- Check in a student to a class:	`>> check_in <student_id> <class_id>`
- **end class session**:	`>> log_end <class_id>` to check out all the students in that class.
- List students: `>> list_students`
- List classes: `>> list_classes`
- List classes attended by student: `>> log_classes <student_id>`
- List students who have attended a class: `>> log_students <class_id`>

More commands can be found using the help menu.

## Licence
Class Attendance Register is built in good faith, under the MIT license. Improvements, opinions and bug reports are highly welcome and encouraged. It would be awesome if you contributed too.