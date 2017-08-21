"""Organise tasks with due date, text file, project and context tags.

  new         Create new task description
  list        List tasks
  <n> command Perform command on task

Usage:
  guz.py new <textlines>...
  guz.py list [<patterns>...]
  guz.py del <n>
  guz.py <n> as <textlines>...
  guz.py <n> mark (done  | -d)
  guz.py <n> mark (fail  | -f)
  guz.py <n> mark (doubt | -?)
  guz.py <n> mark (wait  | -w) [<input>]
  guz.py <n> unmark
  guz.py <n> due <datestamp>
  guz.py <n> file <filename>
  guz.py <n> [+<project>]...
  guz.py <n> [@<context>]...
  guz.py (rebase | delete) all
  guz.py datafile [<path>]
  guz.py [timer] start <n>
  guz.py [timer] stop
  guz.py -h

Options:
  -h --help     Show this screen.
"""

# PROPOSAL 1: compile to exe

import sys
import os
import pickle
import io


from docopt import docopt


# PROPOSAL 2: change to json
FILENAME = 'data.pickle'


class DataStore(object):
    """Store data in a local file.

       Uses pickle with *self.filename* to store data.

    """

    def __init__(self, filename=FILENAME):
        """
        If *filename* does not exist, writes empty
        dictionary to *filename*.
        """
        self.filename = filename
        if not os.path.exists(self.filename):
            self.to_disk({})

    def to_disk(self, x):
        with open(self.filename, 'wb') as fp:
            pickle.dump(x, fp)

    def from_disk(self):
        with open(self.filename, 'rb') as fp:
            return pickle.load(fp)

from enum import Enum, unique

@unique
class Status(Enum):
     Empty = ' '
     Done = '+'
     Failed = 'f'
     Unclear = '?'
     Hold = 'h'
     Wait = '>'
     WorkInProgress = 'w' 

"""todolist data structure in todo_item.go
type Todo struct {
	Id            int      `json:"id"`
	Subject       string   `json:"subject"`
	Projects      []string `json:"projects"`
	Contexts      []string `json:"contexts"`
	Due           string   `json:"due"`
	Completed     bool     `json:"completed"`
	CompletedDate string   `json:"completedDate"`
	Archived      bool     `json:"archived"`
	IsPriority    bool     `json:"isPriority"`
}
"""

class Task(object):

    def __init__(self, subject: str):
        self.__dict__ = dict(subject=subject, status=None)

    def __getattr__(self, key):
        """Return task attibutes by name.

        Example:
            Task("go to holiday").subject
        """
        return self.__dict__[key]

    def __eq__(self, x):
        return bool(self.__dict__ == x.__dict__)

    def __repr__(self):
        return "Task(subject='{}')".format(self.subject)

    def __str__(self):
        return self.subject

    def format_with_id(self, id):
        i = "{:2d}".format(id)  # see pyformat
        status = " "  # {'done':'x', None:" "}[self.status]
        return "{} [{}] {}".format(i, status, self)

    def __setstate__(self, x):
        """Function to work with pickle.load()"""
        self.__dict__ = x

    def __getstate__(self):
        """Function to work with pickle.dump()"""
        return self.__dict__

class TaskListBase:
    """Index handling for *self.tasks*""" 
    
    def __init__(self, _dict={}):
        self.tasks=_dict
    
    @property
    def task_ids(self):
        """Return sorted list of integers, task ids"""
        return sorted([x for x in self.tasks.keys() if isinstance(x, int)])

    def get_max_task_id(self):
        """Return highest number used as task id or 0"""
        return max(self.task_ids + [0])

    def accept_task_id(self, id):
        return bool(id in self.task_ids)

    def len(self):
        return len(self.task_ids)


class TaskList(TaskListBase):

    def __init__(self, path=FILENAME, out=sys.stdout):
        self.store = DataStore(path)
        self.tasks = self.store.from_disk()
        self.out = out

    def rebase(self):
        self.tasks = {(new_id + 1): self.tasks[id]
                      for new_id, id
                      in enumerate(self.task_ids)}
        self.echo("Rebased task ids")
        self.save()

    def delete_item(self, id, silent=False):
        if self.accept_task_id(id):
            del self.tasks[id]
            self.save()
            if not silent:
                self.echo("Deleted task {}".format(id))
        else:
            self.echo("Task id not found: {}".format(id))

    def delete_all(self):
        for id in self.task_ids:
            self.delete_item(id, silent=True)
        self.save()
        self.echo("All tasks deleted. What made you do this?..")

    def add_item(self, task):
        id = self.get_max_task_id() + 1
        self.tasks[id] = task
        self.save()
        self.echo("New task added:")
        self.echo_task(id)

    def replace_item(self, id, task):
        self.tasks[id] = task
        self.save()
        self.echo("Task changed:")
        self.echo_task(id)

    def save(self):
        self.store.to_disk(self.tasks)

    def echo(self, msg):
        print(msg, file=self.out)

    def echo_task(self, id):
        task_repr = self.tasks[id].format_with_id(id)
        print(task_repr, file=self.out)

    def select(self, patterns):
        def find_pattern(pat, text):
            if pat.startswith("-"):
                return not (pat[1:] in text)
            else:
                return pat in text
        for id in self.task_ids:
            text = str(self.tasks[id])
            flag = [True for pat in patterns if find_pattern(pat, text)]
            if flag:
                yield id

    def list(self, ids=False):
        if not ids:
            ids = self.task_ids
        for id in ids:
            self.echo_task(id)
        msg = "Listed {} of {} tasks".format(len(ids), len(self.task_ids))
        self.echo(msg)


class Arguments:
    """Convert command line arguments to variables using docopt.
    """

    def __init__(self, arglist):
        self.args = docopt(__doc__, arglist)

    def __str__(self):
        return str(self.args)

    def __getattr__(self, key):
        return self.args[key]

    @property
    def all_args(self):
        return self.args

    @property
    def id(self):
        if self.args['<n>']:
            return int(self.args['<n>'])

    @property
    def task(self):
        subj = " ".join(self.args['<textlines>'])
        return Task(subj)


def main(arglist=sys.argv[1:], file=FILENAME, out=sys.stdout):
    args = Arguments(arglist)
    tasklist = TaskList(file, out)
    #  guz.py new <textlines>...
    if args.new:
        tasklist.add_item(args.task)
    #  guz.py list [<patterns>...]
    if args.list:
        tasklist.list()
    #  guz.py del <n>
    if args.__getattr__('del'):
        tasklist.delete_item(args.id)
    #  guz.py <n> as <textlines>...
    if args.__getattr__('as'):
        tasklist.replace_item(args.id, args.task)
    #  guz.py (rebase | delete) all
    if args.all:
        if args.delete:
            tasklist.delete_all()
        elif args.rebase:
            tasklist.rebase()
    return tasklist

#  guz.py <n> mark (done  | -d)
#  guz.py <n> mark (fail  | -f)
#  guz.py <n> mark (doubt | -?)
#  guz.py <n> mark (wait  | -w) [<input>]
#  guz.py <n> unmark

#  guz.py <n> due <datestamp>
#  guz.py <n> file <filename>
#  guz.py <n> [+<project>]...
#  guz.py <n> [@<context>]...
#  guz.py datafile [<path>]
#  guz.py [timer] start <n>
#  guz.py [timer] stop


def catch_output(command_lines, file):
    """Intercept stdout stream when executing *command_lines* on *file*.
    
       Args:
           command_lines (list)
           file (string)
    
       Returns:
           Output to stdout as string.
    """
    for command_line in command_lines.split('\n'):
        arglist = command_line.split(' ')
        out = io.StringIO()
        main(arglist, file, out)
    return out.getvalue()


def catch_tasklist(command_lines, path):
    """Execute *command_lines* list of command strings on *file* 
       and return resulting tasklist. Used in testing.
       
       Args:
           command_lines (list)
           file (string)
           
       Returns:
           TaskList() instance           
       """
    for command_line in command_lines:
        arglist = command_line.split(" ")
        result = main(arglist, path)
    return result


if __name__ == '__main__':
    main()