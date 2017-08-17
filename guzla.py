# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 00:49:02 2017

@author: Евгений
"""
import os
import pickle


FILENAME = 'data.pkl'

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
            
    def print(self):
        for id in sorted(self.ids):
            print(id, self.tasks[id])

if __name__ == "__main__":
     
     df = DataFile()
     assert isinstance(df.from_disk(), dict)
            
     tasklist = TaskList() 
     assert isinstance(tasklist.ids, list)      
     
     tasklist.delete_all() 
    
     t = Task("one task @home - to delete")
     tasklist.add_item(t) 
    
     t = Task("todo everything @home - to stay 1")
     tasklist.add_item(t)     
    
     t = Task("other task @work - to stay 2")
     tasklist.add_item(t) 
    
     # add and delete duplicate
     t = Task("other task @work")
     tasklist.add_item(t) 
     n = tasklist.get_max_id()
     tasklist.delete_item(n)
    
     t4 = Task("edited task 4 - to stay 3")
     tasklist.replace_item(4, t4)
    
     tasklist.delete_item(1)
   
     z = TaskList() 
     z.print()    

