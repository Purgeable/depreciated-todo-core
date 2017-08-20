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

# PROPOSAL: compile to exe

import sys
import os
import pickle

from docopt import docopt


# PROPOSAL: change to json
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
    

class Status(object):
    # ENUM?
    allowed = {'none': ' ',
               'done': '+', 
               'wait': 'e', 
               'fail': 'f',
               'doubt': '?'}    

class Task(object):
    
    def __init__(self, subject: str):
        self.__dict__ = dict(subject=subject, status=None) 

    def __setstate__(self, x):
        """Function to work with pickle.load()"""
        self.__dict__ = x

    def __getstate__(self):
        """Function to work with pickle.dump()"""
        return self.__dict__

    def __getattr__(self, key): 
        """Return task attibutes by name.
        
        Example:
            Task("go to holiday").subject
        """
        return self.__dict__[key]

    def __repr__(self):  
        return "Task(subject='{}')".format(self.subject)
       
    def __str__(self):  
        return self.subject
    
    def format_with_id(self, id):
        i = "{:2d}".format(id)  # see pyformat
        status = " "            #{'done':'x', None:" "}[self.status]
        return "{} [{}] {}".format(i, status, self)    

        

class TaskList:    
    
    def __init__(self, path=FILENAME, out = sys.stdout):
        self.store = DataStore(path) 
        self.tasks = self.store.from_disk()
        self.out = out
    
    @property   
    def ids(self):
        return [x for x in self.tasks.keys() if isinstance(x, int)]

    def get_max_id(self):
        return max(self.ids + [0])

    def accept_id(self, id):
        if id in self.ids:
           return True
        else:
           self.echo("No such task id: {}".format(id))             
           return False
       
    def rebase(self):
        self.tasks = {(new_id+1):self.tasks[id] for new_id, id 
                                                in enumerate(self.ids)}
        self.echo("Rebased task ids")
        self.save()
            
    def delete_item(self, id, silent=False):
        if self.accept_id(id):
            del self.tasks[id]
            self.save()
            if not silent:
                self.echo("Deleted task {}".format(id))            
        else:
            self.echo("Cannot delete task {}".format(id))

    def delete_all(self):
        for id in self.ids:
           self.delete_item(id, silent=True)   
        self.save()
        self.echo("All tasks deleted. What made you do this?..")

    def add_item(self, task):
        id = self.get_max_id() + 1
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
   
    def select_all(self):
        return sorted(self.ids)
    
    def select(self, patterns):
        def find_pattern(pat, text):
            if pat.startswith("-"):
                return not (pat[1:] in text)
            else:
                return pat in text
        for id in self.ids:
            text = str(self.tasks[id])
            flag = [True for pat in patterns if find_pattern(pat, text)]
            if flag:
                yield id
    
    def list(self, ids=False):
        if not ids:
            ids = self.select_all()
        for id in ids:
            self.echo_task(id)
        msg = "Listed {} of {} tasks".format(len(ids), len(self.ids))    
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

import io
def catch_output(command_lines, file):
    """Intercept stdout stream when executing *command_lines* on *file*.
    """
    for command_line in command_lines.split('\n'):
        arglist = command_line.split(' ')        
        out = io.StringIO()
        main(arglist, file, out)
    return out.getvalue()   

def catch_tasklist(command_lines, file):
    """Execute *command_lines* on *file* and return reulting tasklist."""    
    for command_line in command_lines.split('\n'):
        arglist = command_line.split(" ")
        result = main(arglist, file)
    return result    

    
if __name__ == '__main__':
    
    c = catch_output('delete all', file="temp.pickle")
    assert c == 'All tasks deleted. What made you do this?..\n'

    c = catch_output('del 0', file="temp.pickle")
    assert c == 'No such task id: 0\nCannot delete task 0\n'
    
    ta_li = catch_tasklist("delete all\nnew do this", file="temp.pickle")
    assert ta_li.tasks[1].subject == 'do this'