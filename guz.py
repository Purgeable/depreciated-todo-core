"""Organise tasks with (some of) todo.txt rules and extra features:

 - configurable command line syntax (with docopt)
 - custom task status flags

Usage:
  guz.py new <textlines>...
  guz.py list [<patterns>...]
  guz.py del <n> 
  guz.py <n> --edit <textlines>...
  guz.py <n> --mark (unclear | ready | wip | done | fail | cancel | lookafter)
  guz.py <n> -m     (-u      | -r    | -w  | -d   | -f   | -c     | -l       )
  guz.py <n> --unmark
  guz.py <n> --project [<+projects>...]
  guz.py (rebase | delete) all
  guz.py -h

Options:
  -h --help     Show this screen.

TODO:
 - compile to exe
 - export/import todo.txt style
 - more commands

  guz.py <n> wait: [<input>]
  guz.py <n> due <datestamp>
  guz.py <n> file <filename>
  guz.py datafile [<path>]
  guz.py [timer] start <n>
  guz.py [timer] stop
  guz.py <n> @<context> [@<context>]"""


from enum import Enum, unique
import io
import sys
import os
import pickle


from docopt import docopt


FILENAME = 'data.pickle'


def action(tasklist, args):

    assert isinstance(tasklist, TaskList)

    #  guz.py new <textlines>...
    if args.new:
        tasklist.add_item(args.task)

    #  guz.py list [<patterns>...]
    if args.list:
        if args.patterns:
            ids = list(tasklist.select(args.patterns))
            tasklist.list(ids)
        else:
            tasklist.list()

    #  guz.py del <n>
    if args.__getattr__('del'):
        tasklist.delete_item(args.task_id)

    #  guz.py <n> change: <textlines>...
    if args.__getattr__('--edit'):
        tasklist.replace_item(args.task_id, args.task)

    #  guz.py (rebase | delete) all
    if args.all:
        if args.delete:
            tasklist.delete_all()
        elif args.rebase:
            tasklist.rebase()

    #  guz.py <n> --mark *
    if args.__getattr__('--mark'):
        tasklist.set_item_status(args.task_id, args.status)
    # FIXME:
    if args.wait:
        tasklist.set_item_status(args.task_id, args.status)

        #tasklist.set_item_block(args.task_id, args.input)
    if args.__getattr__('--unmark'):
        tasklist.reset_item_status(args.task_id)

    #  guz.py <n> project: [<+projects>...]
    if args.__getattr__('--project'):
        tasklist.set_item_projects(args.task_id, args.projects)

    return tasklist


@unique
class Status(Enum):
    Empty = ' '
    # Not doing
    Unclear = '?'
    Hold = '>'
    Ready = '*'
    # Working on it
    WorkInProgress = 'w'
    # Finished
    Done = '+'
    Failed = 'x'
    Cancelled = '/'


def classify_status(args: dict):
    """
    guz.py <n> mark: (none | unclear | ready | wip | done | fail | cancel | lookafter)

    """

    # Not doing
    if args['none']:
        return Status.Empty
    if args['unclear']:
        return Status.Unclear
    elif args['ready']:
        return Status.Ready
    # Working on it
    elif args['wip']:
        return Status.WorkInProgress
    # Finished
    elif args['done']:
        return Status.Done
    elif args['fail']:
        return Status.Failed
    elif args['cancel']:
        return Status.Cancelled
    elif args['lookafter']:
        return Status.FollowUp
    else:
        raise ValueError("No status defined by {}".format(args))


class Arguments:
    """Convert command line arguments to variables using docopt."""

    def __init__(self, arglist):
        self.args = docopt(__doc__, arglist)

    def __str__(self):
        return str(self.args)

    def __getattr__(self, key):
        try:
            return self.args[key]
        except KeyError:
            return False

    @property
    def task_id(self):
        if self.args['<n>']:
            return int(self.args['<n>'])

    @property
    def task(self):
        subj = " ".join(self.args['<textlines>'])
        return Task(subj)

    @property
    def status(self):
        return classify_status(self.args)

    @property
    def projects(self):
        return self.args['<+projects>']

    @property
    def patterns(self):
        return self.args['<patterns>']


class DataStore(object):
    """Store data in a local pickle"""

    def __init__(self, path=FILENAME):
        self.path = path

    def to_disk(self, x):
        with open(self.path, 'wb') as fp:
            pickle.dump(x, fp)

    def from_disk(self):
        if os.path.exists(self.path):
            with open(self.path, 'rb') as fp:
                return pickle.load(fp)
        else:
            raise FileNotFoundError(self.path)


class Task(object):

    def __init__(self, subject, **kwarg):
        self.__dict__['subject'] = subject
        self.status = Status.Empty
        self.projects = []
        self.__dict__.update(kwarg)

    def format_with_id(self, i):
        """Return string representation of task using index *i*."""
        return "{:2d} {}".format(i, str(self))

    def __getattr__(self, name):
        """Return attibute by *name*.
           Example: Task("go on holiday").subject
        """
        try:
            return self.__dict__[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        """Set attibute *name* to *value*.
           Example: Task("buy tickets").status = Status.Done
        """
        self.__dict__[name] = value

    def __eq__(self, x):
        return bool(self.__dict__ == x.__dict__)

    def __repr__(self):
        params = ["subject='{}'".format(self.subject)]
        if self.status != Status.Empty:
            params.append('status=Status.{}'.format(self.status.Name))
        return "Task({})".format(', '.join(params))

    def __str__(self):
        tokens = [
            # status
            '[{}]'.format(self.status.value),
            # subject
            self.subject]
        if self.projects:
            tokens.append(' '.join(self.projects))
        return ' '.join(tokens)


class TaskListBaseIndexer:
    """Index handling for *self.tasks*"""

    def __init__(self, tasks={}):
        if isinstance(tasks, dict):
            self.tasks = tasks
        else:
            raise TypeError(tasks)

    def new_index(self):
        if self.keys():
            return max(self.keys()) + 1
        else:
            return 1

    def keys(self):
        """Return list of integers containing sorted self.tasks keys"""
        return sorted([x for x in self.tasks.keys() if isinstance(x, int)])

    def is_valid_index(self, i):
        return bool(i in self.keys())

    def __len__(self):
        return len(self.tasks)


class TaskList(TaskListBaseIndexer):

    def __init__(self, taskdict: dict={}):
        self.tasks = taskdict

    def __getstate__(self):
        return self.tasks

    def __setstate__(self, x):
        self.tasks = x

    def __eq__(self, x):
        return bool(self.tasks == x.tasks)

    def get_messages(self):
        try:
            return self.messages
        # protect when instance recovered from pickle
        except AttributeError:
            return []

    def add_item(self, task):
        i = self.new_index()
        self.tasks[i] = task
        self.messages = ["New task added:", self.format_item(i)]

    def accept_index(self, i):
        if self.is_valid_index(i):
            return True
        else:
            self.messages = ["Task id not found: {}".format(i)]
            return False

    def replace_item(self, i, task):
        if self.accept_index(i):
            self.tasks[i] = task
            self.messages = ["Task changed:", self.format_item(i)]

    def delete_item(self, i, silent=False):
        if self.accept_index(i):
            del self.tasks[i]
            if not silent:
                self.messages = ["Deleted task {}".format(i)]

    def delete_all(self):
        for id in self.keys():
            self.delete_item(id, silent=True)
        self.messages = ["All tasks deleted. What made you do this?.."]

    def rebase(self):
        self.tasks = {(new_id + 1): self.tasks[id]
                      for new_id, id
                      in enumerate(self.keys())}
        self.messages = ["Rebased task ids"]

    def set_item_status(self, i, status):
        assert isinstance(status, Status)
        self.tasks[i].status = status
        self.messages = ["Status changed:", self.format_item(i)]

    def reset_item_status(self, i):
        self.set_item_status(i, Status.Empty)

    def set_item_projects(self, i, projects):
        assert isinstance(projects, list)
        self.tasks[i].projects = projects

    def select(self, patterns):
        def find_pattern(pat, text):
            if pat.startswith("-"):
                return not (pat[1:] in text)
            else:
                return pat in text
        for i in self.keys():
            text = str(self.tasks[i])
            flag = [True for pat in patterns if find_pattern(pat, text)]
            if flag:
                yield i

    def format_item(self, i):
        return self.tasks[i].format_with_id(i)

    def list(self, ids=False):
        if not ids:
            ids = self.keys()
        self.messages = []
        for i in ids:
            self.messages.append(self.format_item(i))
        msg = "Listed {} of {} tasks".format(len(ids), len(self))
        self.messages.append(msg)


class Messenger:

    def __init__(self, tasklist, silent=False):
        self.messages = tasklist.get_messages()
        if silent:
            self.out = io.StringIO()
        else:
            self.out = sys.stdout

    def print(self):
        for msg in self.messages:
            print(msg, file=self.out)
        return self

    def catch_output(self):
        return self.out.getvalue()


class TaskDB:

    def __init__(self, file=FILENAME):
        self.path = file
        if not os.path.exists(self.path):
            self.init_db()
        self.tasklist = DataStore(self.path).from_disk()
        assert isinstance(self.tasklist, TaskList)

    def transact(self, arglist):
        args = Arguments(arglist)
        self.tasklist = action(self.tasklist, args)

    def save(self):
        DataStore(self.path).to_disk(self.tasklist)

    def init_db(self):
        empty_tasklist = TaskList({})
        DataStore(self.path).to_disk(empty_tasklist)


def main(arglist=sys.argv[1:], file=FILENAME):
    db = TaskDB(file)
    db.transact(arglist)
    db.save()
    Messenger(db.tasklist, silent=False).print()
    return db.tasklist


if __name__ == '__main__':
    # for debugging
    args = Arguments(sys.argv[1:])
    try:
        tasklist = DataStore(FILENAME).from_disk()
    except FileNotFoundError:
        tasklist = TaskList({})
    tasklist = action(tasklist, args)
    # for use
    main()

# Reference ---------------------------------

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
# -----------------------------------------
