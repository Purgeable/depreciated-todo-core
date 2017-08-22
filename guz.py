"""Organise tasks with due date, associated text file and (some of) todo.txt 
   rules.

Usage:
  guz.py new <textlines>...
  guz.py list [<patterns>...]
  guz.py del <n>
  guz.py <n> as <textlines>...
  guz.py <n> mark (done  | -d)
  guz.py <n> mark (fail  | -f)
  guz.py <n> mark (hold  | -h)
  guz.py <n> mark (doubt | -?)
  guz.py <n> mark (wait  | -i) [<input>]
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
     Done = '+'
     Failed = 'f'
     Unclear = '?'
     Hold = 'h'
     WaitForInput = '>'
     WorkInProgress = 'w' 

def classify_status(args: dict):
    if args['-?'] or args['doubt']:
        return Status.Unclear
    elif args['-d'] or args['done']:
        return Status.Done
    elif args['-f'] or args['fail']:
        return Status.Failed
    elif args['-h'] or args['hold']:
        return Status.Hold
    elif args['-i'] or args['wait']:
        return Status.WaitForInput
    elif args['-g'] or args['go']:
        return Status.WorkInProgress
    else:
        raise ValueError("No status defined")

class DataStore(object):
    """Store data in a local file. Uses pickle at *self.path*"""

    def __init__(self, path=FILENAME):
        self.path = path
        if not os.path.exists(self.path):
            self.to_disk({})

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
        """Return attibute by *name*, ex:
              Task("go to holiday").subject
        """
        return self.__dict__[name]

    def __setattr__(self, name, value):
        """Set attibute *name* to *value*, ex:            
              Task("go to holiday").status = Status.Done
        """
        self.__dict__[name] = value

    def __getstate__(self):
        return self.__dict__
    
    def __setstate__(self, x):
        self.__dict__ =  x

    def __eq__(self, x):
        return bool(self.__dict__ == x.__dict__)

    def __repr__(self):        
        msg = "Task(subject='{}')".format(self.subject)
        args = self.__dict__.copy()
        args.pop('subject')
        if args:
            return msg + ".update({})".format(args)
        else:
            return msg 

    def __str__(self):
        tokens = ['[{}]'.format(self.status.value), 
                  self.subject]
        return ' '.join(tokens)

    def format_with_id(self, i):
        return "{:2d} {}".format(i, self)
    
class TaskListBase:
    """Index handling for *self.tasks*""" 
    
    def __init__(self, tasks={}):
        if isinstance(tasks, dict):
            self.tasks=tasks
        else:
            raise TypeError(tasks)
            
    def new_index(self):        
        if self.keys():
            return max(self.keys()) + 1
        else:
            return 0 + 1
        
    def keys(self):
        """Return sorted self.tasks keys as list of integers"""
        return sorted([x for x in self.tasks.keys() if isinstance(x, int)])
    
    def is_valid_task_id(self, i):
        return bool(i in self.keys())

    def __len__(self):
        return len(self.tasks)

    # EXPERIMENTAL, not used:
        
    def __getitem__(self, i):
        if self.is_valid_task_id(i):
            return self.tasks[i]
        else:
            raise KeyError("Index {} not in {}".format(i, self.task_ids))

    def __setitem__(self, i, x):
        if isinstance (i, int):
            self.tasks[i]
        else:
            raise TypeError(i)

    # END EXPERIMENTAL


class TaskList(TaskListBase):

    def __init__(self, taskdict: dict, out=sys.stdout):
        self.tasks = taskdict
        self.out = out

    def rebase(self):
        self.tasks = {(new_id + 1): self.tasks[id]
                      for new_id, id
                      in enumerate(self.keys())}
        self.echo("Rebased task ids")

    def delete_item(self, id, silent=False):
        if self.is_valid_task_id(id):
            del self.tasks[id]
            if not silent:
                self.echo("Deleted task {}".format(id))
        else:
            self.echo_not_found(id)

    def delete_all(self):
        for id in self.keys():
            self.delete_item(id, silent=True)
        self.echo("All tasks deleted. What made you do this?..")

    def add_item(self, task):
        i = self.new_index()
        self.tasks[i] = task
        self.echo("New task added:")        
        self.echo_task(i)

    def replace_item(self, i, task):
        if self.is_valid_task_id(i):
            self.tasks[i] = task
            self.echo("Task changed:")
            self.echo_task(i)
        else:
            self.echo_not_found(id)
            
    def set_item_status(self, i, status):
        self.tasks[i].status = status        
        
    def reset_item_status(self, i):
        self.tasks[i].status = Status.Empty

    def echo(self, msg):
        print(msg, file=self.out)

    def echo_task(self, i):
        task_repr = self.tasks[i].format_with_id(i)
        print(task_repr, file=self.out)

    def echo_not_found(self, i):
        self.echo("Task id not found: {}".format(i))

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

    def list(self, ids=False):
        if not ids:
            ids = self.keys()
        for id in ids:
            self.echo_task(id)
        msg = "Listed {} of {} tasks".format(len(ids), len(self))
        self.echo(msg)

class Arguments:
    """Convert command line arguments to variables using docopt."""

    def __init__(self, arglist):
        self.args = docopt(__doc__, arglist)

    def __str__(self):
        return str(self.args)

    def __getattr__(self, key):
        return self.args[key]

    def get_dict(self):
        return self.args

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

    #  guz.py <n> mark (done  | -d)
    #  guz.py <n> mark (fail  | -f)
    #  guz.py <n> mark (doubt | -?)
    #  guz.py <n> mark (wait  | -w) [<input>]
    #  guz.py <n> unmark
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


class TaskDB:
    
    def __init__(self, file=FILENAME, out=sys.stdout):
        self.path = file
        self.out = out
        taskdict = DataStore(self.path).from_disk()
        self.tasklist = TaskList(taskdict, self.out)
    
    def transact(self, args):
        self.tasklist = action(self.tasklist, args)
    
    def get_output(self):
        return self.out.getvalue()
        
    def save(self):
        DataStore(self.path).to_disk(self.tasklist.tasks)


def main(arglist=sys.argv[1:], file=FILENAME, out=sys.stdout):
    args = Arguments(arglist)
    db = TaskDB(file, out)
    db.transact(args)
    db.save
    return db.tasklist
    
    
def catch_output(command_lines, path):
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
        main(arglist, path, out)
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