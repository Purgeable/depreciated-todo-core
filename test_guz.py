"""Unit- and behaviour testing of guz.py, a todo organiser."""

# -*- coding: utf-8 -*-

# FIXME: play with delegator 
#import delegator 
#c = delegator.run("python -v")
    
import pytest
import os


from guz import DataStore, FILENAME
from guz import Task, TaskList
from guz import Arguments


TEMP_FILENAME = "temp.pickle"

def set_datastore(filename, contents):
    ds = DataStore(filename)
    ds.to_disk(contents) 

def teardown_module(module):
    """Cleanup temp files."""
    if os.path.exists(TEMP_FILENAME):
        os.remove(TEMP_FILENAME)
    

class Test_DataStore:
    
    def setup_method(self): 
        self._dict = {1:'task one', 2:'task two'}
        set_datastore(TEMP_FILENAME, self._dict)
        self.ds = DataStore(TEMP_FILENAME)
            
    def teardown_method(self):
        """Cleanup temp files."""
        if os.path.exists(TEMP_FILENAME):
            os.remove(TEMP_FILENAME)
    
    def test_on_production_init_directs_to_global_filename(self):        
        ds = DataStore()
        assert ds.filename == FILENAME
    
    def test_on_temp_init_directs_to_other_filename(self):        
        assert self.ds.filename == TEMP_FILENAME

    def test_on_temp_store_write_and_read_back_dictionary(self):        
        assert self.ds.from_disk() == self._dict   

import io

class Test_Task:
    
    def setup_method(self):
        self.t = Task("do this")
        
    def test_init_task_has_subject(self):
        assert self.t.subject == "do this"
        
    def test_init_task_no_status_given(self):
        assert self.t.status == None

REF_DICT = {1:Task('do this'), 2:Task('do that')}

def tasklist(filename=TEMP_FILENAME, tasks_dict=REF_DICT):
    set_datastore(filename, tasks_dict)
    out = io.StringIO()
    return TaskList(filename, out), out

class Test_TaskList_No_Echo:
    
    def setup_method(self):
        self.tasklist, _ = tasklist()         
    
    def test_tasks_attribute_is_dictionary(self):
        self.tasklist.tasks == REF_DICT 


class Test_Arguments:
    
    def test_list(self):
        arglist = ['list']
        assert Arguments(arglist).list is True
    
    
if __name__ == "__main__":
     pytest.main([__file__])
     
#     df = DataFile()
#     assert isinstance(df.from_disk(), dict)
#            
#     # fixture with mock data file
#     mockfile = "mock.pickle"
#     mocklist = TaskList(mockfile)
#     mocklist.delete_all() 
#     
#     #test 1
#     tasklist =  TaskList(mockfile)
#     assert isinstance(tasklist.ids, list)      
#     
#     #test 2
#     t = Task("one task @home - to delete")
#     tasklist.add_item(t) 
#    
#     t = Task("todo everything @home - to stay 1")
#     tasklist.add_item(t)     
#    
#     t = Task("other task @work - to stay 2")
#     tasklist.add_item(t) 
#    
#     # add and delete duplicate
#     t = Task("other task @work")
#     tasklist.add_item(t) 
#     n = tasklist.get_max_id()
#     tasklist.delete_item(n)
#    
#     t4 = Task("edited task 4 - to stay 3")
#     tasklist.replace_item(4, t4)
#    
#     tasklist.delete_item(1)
#   
#     lines = list(TaskList().select_all())
#     assert lines == ['2 todo everything @home - to stay 1',
#                      '3 other task @work - to stay 2',
#                      '4 edited task 4 - to stay 3']
#
#     lines = list(TaskList().select(['@work']))
#     assert lines == ['3 other task @work - to stay 2']
#
#     #print something     
#     TaskList(mockfile).print()
#
#
#
#class Test_DataStore:
#    
#     df = DataFile()
#     assert isinstance(df.from_disk(), dict)
#            
#     # fixture with mock data file
#     mockfile = "mock.pickle"
#     mocklist = TaskList(mockfile)
#     mocklist.delete_all() 
#     
#     #test 1
#     tasklist =  TaskList(mockfile)
#     assert isinstance(tasklist.ids, list)      
#     
#     #test 2
#     t = Task("one task @home - to delete")
#     tasklist.add_item(t) 
#    
#     t = Task("todo everything @home - to stay 1")
#     tasklist.add_item(t)     
#    
#     t = Task("other task @work - to stay 2")
#     tasklist.add_item(t) 
#    
#     # add and delete duplicate
#     t = Task("other task @work")
#     tasklist.add_item(t) 
#     n = tasklist.get_max_id()
#     tasklist.delete_item(n)
#    
#     t4 = Task("edited task 4 - to stay 3")
#     tasklist.replace_item(4, t4)
#    
#     tasklist.delete_item(1)
#   
#     lines = list(TaskList().select_all())
#     assert lines == ['2 todo everything @home - to stay 1',
#                      '3 other task @work - to stay 2',
#                      '4 edited task 4 - to stay 3']
#
#     lines = list(TaskList().select(['@work']))
#     assert lines == ['3 other task @work - to stay 2']
#
#     #print something     
#     TaskList(mockfile).print()
#
