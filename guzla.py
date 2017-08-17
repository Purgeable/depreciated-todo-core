# -*- coding: utf-8 -*-
"""
Simple command-line todo application in 60 lines of Python. 
"""

import pickle


FILE = 'data.pkl'

class Task(object):
    
    def __init__(self, subject: str):
       self.__dict__= dict(subject=subject) 

    def __repr__(self):  
        return self.__dict__['subject']
       
    def __str__(self):  
        return self.__dict__['subject']

class TaskList:    
    
    def __init__(self):
        self.refresh()

    def ids(self):
        return list(self.__dict__.keys())

    def get_max_id(self):
        return max(self.ids())    

    def rebase_ids(self):
        pass

    def delete_item(self, id):
        if id in self.ids():
           del self.__dict__[id]   
        self.save()

    def add_item(self, task):
        key = self.get_max_id() + 1
        self.__dict__[key] = task
        self.save()
        
    def replace_item(self, id, task):
        self.__dict__[id] = task
        self.save()             
    
    def save(self, file=FILE):
        with open(file, 'wb') as fp:
            pickle.dump(self, fp)
            
    def refresh(self, file=FILE):
        with open(file, 'rb') as fp:
            self.__dict__ = pickle.load(fp).__dict__        
    
    def print(self):
        for id in sorted(self.ids()):
            print(id, self.__dict__[id])

if __name__ = '__main__':

  tasklist = TaskList() 

  t = Task("other task")
  tasklist.add_item(t) 

  n = tasklist.get_max_id()
  tasklist.delete_item(n)

  t4 = Task("edited task 4")
  tasklist.replace_item(4, t4)

  tasklist.delete_item(1)
  tasklist.delete_item(5)

  z = TaskList() 
  z.print()
