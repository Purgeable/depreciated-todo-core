"""Unit- and behaviour testing of guz.py, a todo organiser."""

# -*- coding: utf-8 -*-

# FIXME: play with delegator 
#import delegator 
#c = delegator.run("python -v")
    
import pytest
import os


from guz import DataStore, FILENAME
from guz import Task
from guz import Arguments


class Test_DataStore:
    
    def teardown_method(self):
        """Cleanup temp files."""
        fn = "temp.pickle"
        if os.path.exists(fn):
            os.remove(fn)
    
    def test_on_production_init_directs_to_global_filename(self):        
        ds = DataStore()
        assert ds.filename == FILENAME
    
    def test_on_temp_init_directs_to_other_filename(self):        
        ds = DataStore("temp.pickle")
        assert ds.filename == "temp.pickle"

    def test_on_temp_store_write_and_read_back_dictionary(self):        
        ds = DataStore("temp.pickle")
        __dict__ = {1:'abc'}
        ds.to_disk(__dict__) 
        assert ds.from_disk() == __dict__   


class Test_Task:
    
    def setup_method(self):
        self.t = Task("do this")
        
    def test_init_task_has_subject(self):
        assert self.t.subject == "do this"
        
    def test_init_task_no_status_given(self):
        assert self.t.status == None

    
# TaskList testing here    


class Test_Arguments:
    
    def test_list(self):
        assert Arguments(['list']).list is True
    
    
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
