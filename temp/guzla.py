"""Organise tasks with due date, text file, project and context tags.

  new    Create new task 
  list   List tasks 
  list   List tasks 

Usage:
  guz.py new <textlines>...
  guz.py list
  guz.py list <patterns>...
  guz.py <n> due <datestamp> 
  guz.py <n> due <datestamp> 
  guz.py <n> file <filename> 
  guz.py <n> [+<project>]... 
  guz.py <n> [@<context>]...

Options:
  -h --help     Show this screen.
"""

# PROPOSAL: compile to exe

from docopt import docopt
   
import os
import pickle

# PROPOSAL: change to json
FILENAME = 'data.pickle'


class DataFile():
    
    def __init__(self, _filename=FILENAME):
        self.filename = _filename            
        if not os.path.exists(self.filename):
            self.to_disk({})
    
    def to_disk(self, __dict__):
        with open(self.filename, 'wb') as fp:
            pickle.dump(__dict__, fp)

    def from_disk(self):
        with open(self.filename, 'rb') as fp:
            return pickle.load(fp)    
    

class Task(object):
    
    def __init__(self, _subject: str):
        self.__dict__= dict(subject=_subject) 

    def __repr__(self):  
        return self.__dict__['subject']
       
    def __str__(self):  
        return self.__dict__['subject']
    
    def format_with_id(self, id):
        return "{} {}".format(id, self)    
        


class TaskList:    
    
    def __init__(self, _filename=FILENAME):
        self.store = DataFile(_filename) 
        self.tasks = self.store.from_disk()   
    
    @property   
    def ids(self):
        return list(self.tasks.keys())

    def get_max_id(self):
        if self.ids:
            return max(self.ids)    
        else:
            return 0

    def rebase_ids(self):
        pass

    def delete_item(self, id):
        if id in self.ids:
           del self.tasks[id]   
        self.save()

    def delete_all(self):
        for id in self.ids:
           self.delete_item(id)   
        self.save()

    def add_item(self, task):
        key = self.get_max_id() + 1
        self.tasks[key] = task
        self.save()
        
    def replace_item(self, id, task):
        self.tasks[id] = task
        self.save()             
    
    def save(self):
        self.store.to_disk(self.tasks) 
            
    def select_all(self):
        for id in sorted(self.ids):
            yield self.tasks[id].format_with_id(id)
    
    def select(self, search_strings):
        for id in sorted(self.ids):
            text = str(self.tasks[id])
            flag = sum([1 for s in search_strings if s in text])
            if flag:
                yield self.tasks[id].format_with_id(id)           
    
    def print(self):
        for text in self.select_all():
            print(text)

if __name__ == '__main__':
    arguments = docopt(__doc__)
    print(arguments)
     