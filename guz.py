"""Organise tasks with status, due date, associated .txt file and 
   (some of) todo.txt rules.

Usage:
  guz.py new <textlines>...
  guz.py list [<patterns>...]
  guz.py del <n>
  guz.py <n> as <textlines>... []
  guz.py <n> (mark unclear | -u)
  guz.py <n> (mark hold [<input>])
  guz.py <n> (mark go     | -g)
  guz.py <n> (mark done   | -d)
  guz.py <n> (mark fail   | -f)
  guz.py <n> (mark cancel | -c)
  guz.py <n> unmark
  guz.py <n> due <datestamp>
  guz.py <n> file <filename>
  guz.py <n> +<project> [+<project>]...
  guz.py (rebase | delete) all
  guz.py datafile [<path>]
  guz.py [timer] start <n>
  guz.py [timer] stop
  guz.py -h

Options:
  -h --help     Show this screen.
"""

"""guz.py <n> @<context> [+<project>]..."""

# PROPOSAL 1: compile to exe
from enum import Enum, unique
import io
import sys
import os
import pickle


from docopt import docopt


# PROPOSAL 2: change to json
FILENAME = 'data.pickle'


@unique
class Status(Enum):
    Empty = ' '
    # Not doing
    Unclear = '?'
    Hold = '>'
    # Working on it
    WorkInProgress = 'w'
    # Finished
    Done = '+'
    Failed = 'f'
    Cancelled = 'x'


def classify_status(args: dict):
    """
  guz.py <n> mark (unclear | -u)
  guz.py <n> mark hold [<input>]  
  guz.py <n> mark (go      | -g)
  guz.py <n> mark (done    | -d)
  guz.py <n> mark (fail    | -f)
  guz.py <n> mark (cancel  | -c)"""    
    
    # Not doing
    if args['-u'] or args['unclear']:
        return Status.Unclear
    elif args['hold']:
        return Status.Hold
    # Working on it
    elif args['-g'] or args['go']:
        return Status.WorkInProgress
    # Finished
    elif args['-d'] or args['done']:
        return Status.Done
    elif args['-f'] or args['fail']:
        return Status.Failed
    elif args['-c'] or args['cancel']:
        return Status.Cancelled
    else:
        raise ValueError("No status defined with {}".format(args))


class DataStore(object):
    """Store data in a local file. Uses pickle at *self.path*"""

    def __init__(self, path=FILENAME):
        self.path = path
        if not os.path.exists(self.path):
            self.to_disk(TaskList({0:Task('')}))

    def to_disk(self, x):
        with open(self.path, 'wb') as fp:
            pickle.dump(x, fp)

    def from_disk(self):
        with open(self.path, 'rb') as fp:
            return pickle.load(fp)


class Task(object):

    def __init__(self, subject, **kwarg):
        self.__dict__['subject'] = subject
        self.status = Status.Empty
        self.update(kwarg)

    def update(self, kwarg):
        self.__dict__.update(kwarg)
        return self

    def __getattr__(self, name):
        """Return attibute by *name*.
           Example: Task("go to holiday").subject
        """
        try:
            return self.__dict__[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        """Set attibute *name* to *value*.
           Example: Task("go to holiday").status = Status.Done
        """
        self.__dict__[name] = value

    def __eq__(self, x):
        return bool(self.__dict__ == x.__dict__)

    def __repr__(self):
        return "Task(subject='{}')".format(self.subject)

    def __str__(self):
        tokens = ['[{}]'.format(self.status.value),
                  self.subject]
        return ' '.join(tokens)

    def format_with_id(self, i):
        return "{:2d} {}".format(i, str(self))


class TaskListBase:
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
        """Return sorted self.tasks keys as list of integers"""
        return sorted([x for x in self.tasks.keys() if isinstance(x, int)])

    def is_valid_index(self, i):
        return bool(i in self.keys())

    def __len__(self):
        return len(self.tasks)



class TaskList(TaskListBase):

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
        except AttributeError:
            return []

    def add_item(self, task):
        i = self.new_index()
        self.tasks[i] = task
        self.messages = ["New task added:", self.tasks[i]]

    def replace_item(self, i, task):
        if self.is_valid_index(i):
            self.tasks[i] = task
            self.messages = ["Task changed:", self.tasks[i]]
        else:
            self.messages = ["Task id not found: {}".format(i)]

    def delete_item(self, i, silent=False):
        if self.is_valid_index(i):
            del self.tasks[i]
            if not silent:
                self.messages = ["Deleted task {}".format(i)]
        else:
            self.messages = ["Task id not found: {}".format(i)]  

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
        self.tasks[i].status = status
        self.messages = ["Status changed:", self.tasks[i]]

    def reset_item_status(self, i):
        self.tasks[i].status = Status.Empty
        self.set_item_status(i, Status.Empty.name)

    def select(self, patterns):
        def find_pattern(pat, text):
            if pat.startswith("-"):
                return not (pat[1:] in text)
            else:
                return pat in text
        for i in self.task_ids:
            text = str(self.tasks[i])
            flag = [True for pat in patterns if find_pattern(pat, text)]
            if flag:
                yield id

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


def action(tasklist, args):
    
    assert isinstance(tasklist, TaskList)

    #  guz.py new <textlines>...
    if args.new:
        tasklist.add_item(args.task)

    #  guz.py list [<patterns>...]
    if args.list:
        tasklist.list()

    #  guz.py del <n>
    if args.__getattr__('del'):
        tasklist.delete_item(args.task_id)

    #  guz.py <n> as <textlines>...
    if args.__getattr__('as'):
        tasklist.replace_item(args.task_id, args.task)

    #  guz.py (rebase | delete) all
    if args.all:
        if args.delete:
            tasklist.delete_all()
        elif args.rebase:
            tasklist.rebase()

    #  guz.py <n> mark *
    if args.mark:
        tasklist.set_item_status(args.task_id, args.status)
    if args.unmark:
        tasklist.reset_item_status(args.task_id)

    #  guz.py <n> due <datestamp>
    #  guz.py <n> file <filename>
    #  guz.py <n> [+<project>]...
    #  guz.py <n> [@<context>]...
    #  guz.py datafile [<path>]
    #  guz.py [timer] start <n>
    #  guz.py [timer] stop
    return tasklist


class Messenger:
    
    def __init__(self, tasklist, silent=False):
        try:
            self.messages = tasklist.get_messages()
        except AttributeError:    
            raise AttributeError(tasklist.tasks)
        if silent:
            self.out=io.StringIO()
        else:
            self.out=sys.stdout

    def print(self):
       for msg in self.messages:
           print(msg, file=self.out)
       return self   

    def catch_output(self):
        return self.out.getvalue()


class TaskDB:

    def __init__(self, file=FILENAME):
        self.path = file
        self.tasklist = DataStore(self.path).from_disk()  
        assert isinstance(self.tasklist, TaskList)
    
    def transact(self, arglist):
        args = Arguments(arglist)
        self.tasklist = action(self.tasklist, args)

    def save(self):
        DataStore(self.path).to_disk(self.tasklist)


def main(arglist=sys.argv[1:], file=FILENAME):
    db = TaskDB(file)
    db.transact(arglist)
    db.save()
    Messenger(db.tasklist, silent=False).print()    
    return db.tasklist


if __name__ == '__main__':    
    arglist=sys.argv[1:]
    args = Arguments(arglist)   
    tasklist = DataStore(FILENAME).from_disk()
    main()


# Reference -------------------------------------------------------------------

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
