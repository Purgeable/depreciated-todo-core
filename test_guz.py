# -*- coding: utf-8 -*-
"""Unit- and behaviour testing of guz.py, a todo organiser."""

# FIXME: play with delegator
#import delegator
#c = delegator.run("python -v")

import pytest
import os
import pickle

from guz import DataStore, FILENAME
from guz import Task, TaskList, TaskListBaseIndexer, Status
from guz import Arguments, TaskDB, Messenger


TEMP_FILENAME = "temp.pickle"

def concat(strings):
    return ''.join([with_newline(s) for s in strings])


def with_newline(x):
    newline = '\n'
    return '{}{}'.format(x, newline)


def set_datastore(filename, contents):
    ds = DataStore(filename)
    ds.to_disk(contents)


REF_DICT = {1: Task('do this'), 5: Task('do that')}


def tasklist():
    return TaskList(REF_DICT)


def teardown_module(module):
    """Cleanup temp files."""
    for filename in ("mock.pickle", TEMP_FILENAME):
        if os.path.exists(filename):
            os.remove(filename)

# testing

def test_basic_testing():
    d = {1: Task('abc')}
    t = TaskList({1: Task('abc')})
    
    assert d == pickle.loads(pickle.dumps(d))
    assert t == pickle.loads(pickle.dumps(t))
    
    DataStore(TEMP_FILENAME).to_disk(t)
    assert t == DataStore(TEMP_FILENAME).from_disk()
    
    t.list()
    
    s = Messenger(t, silent=True).print().catch_output()    
    assert s == ' 1 [ ] abc\nListed 1 of 1 tasks\n'
    assert s == '\n'.join(t.get_messages() + [''])
    
    # TODO: add transaction with save
    
    db = TaskDB(TEMP_FILENAME)
    db.transact(['list'])    
    Messenger(db.tasklist).print()


class Test_DataStore:

    def setup_method(self):        
        self.contents = {'hello': 'world'}
        set_datastore(TEMP_FILENAME, self.contents)
        self.ds = DataStore(TEMP_FILENAME)

    def test_on_temp_init_directs_to_other_filename(self):
        assert self.ds.path == TEMP_FILENAME

    def test_on_temp_store_write_and_read_back_dictionary(self):
        assert self.ds.from_disk() == self.contents


class Test_Production_DataStore:
        
    def test_on_init_directs_to_global_filename(self):
        ds = DataStore()
        assert ds.path == FILENAME 
        # FILENAME may or may not exist


class Test_Task:

    def setup_method(self):
        self.t = Task("do this")

    def test_on_init_task_has_subject(self):
        assert self.t.subject == "do this"

    def test_on_init_task_no_status_given(self):
        assert self.t.status == Status.Empty

    def test_on_init_str_is_callable(self):
        assert str(self.t)

    def test_on_init_repr_is_callable(self):
        assert repr(self.t)

    def test_on_init_format_with_id_retruns_string(self):        
        assert isinstance(self.t.format_with_id(0), str)


class Test_TaskListBaseIndexer:

    def setup_method(self):
        self.tasklist = TaskListBaseIndexer({5: 'content 5', 1: 'content 1'})

    def test_task_items_are_accessible(self):
        assert self.tasklist.tasks[1] == 'content 1'
        assert self.tasklist.tasks[5] == 'content 5'

    def test_keys(self):
        assert self.tasklist.keys() == [1, 5]

    def test_is_valid_task_id_success(self):
        for n in [1, 5]:
            self.tasklist.is_valid_index(n) is True

    def test_is_valid_task_id_fails(self):
        for k in [x for x in range(-1, 10) if x not in [1, 5]]:
            self.tasklist.is_valid_index(k) is False

    def test_len(self):
        len(self.tasklist) == 2


class Test_TaskList:

    def setup_method(self):
        self.tasklist = tasklist()

    def test_tasks_attribute_is_dictionary(self):
        self.tasklist.tasks == {1: Task('do this'), 5: Task('do that')}

    def test_on_list(self):
        self.tasklist.list()
        assert self.tasklist.get_messages() == ([' 1 [ ] do this',
                                                 ' 5 [ ] do that',
                                                 'Listed 2 of 2 tasks'])

    def test_on_delete_success(self):
        self.tasklist.delete_item(1)
        assert self.tasklist.tasks == {5: Task('do that')}
        assert self.tasklist.get_messages() == ['Deleted task 1']
        self.setup_method()

    def test_on_delete_failed(self):
        self.tasklist.delete_item(0)
        assert self.tasklist.get_messages() == ['Task id not found: 0']

    def test_on_rebase(self):
        self.tasklist.rebase()
        self.tasklist.tasks == {1: Task('do this'), 2: Task('do that')}
        assert self.tasklist.get_messages() == ['Rebased task ids']
        self.setup_method()



class Test_TaskList_Behaviour_On_Adding_Deleting_Replacing:
    
    
    def setup_method(self):
        tasklist = TaskList()
        t = Task("one task @home - to delete")
        tasklist.add_item(t)
        t = Task("todo everything @home - to stay as #2")
        tasklist.add_item(t)
        t = Task("other task @work - to stay as #3")
        tasklist.add_item(t)
        t = Task("other task @work - to delete")
        tasklist.add_item(t)
        n = max(tasklist.keys())
        tasklist.delete_item(n)
        t = Task("forth task - to be replaced")
        tasklist.add_item(t)
        t4 = Task("edited task 4 - to stay as #4")
        tasklist.replace_item(4, t4)
        tasklist.delete_item(1)
        self.tasklist = tasklist
    
    def test_multiple_commands(self):      
        tasklist = self.tasklist
        lines = [tasklist.tasks[i].subject for i in tasklist.keys()]
        assert lines == ['todo everything @home - to stay as #2',
                         'other task @work - to stay as #3',
                         'edited task 4 - to stay as #4']
        
@pytest.fixture
def test_db():
    os.remove(TEMP_FILENAME)
    db = TaskDB(TEMP_FILENAME)
    db.init_db()
    return db
    

class Test_Commands:
    
    def setup_method(self):
        self.commands = ['delete all'
                  , 'new one task @home - to delete'
                  , 'new todo everything @home - to stay as #2'
                  , 'new other task @work - to stay as #3'
                  , 'new other task @work - to delete'
                  , 'del 4'
                  , 'new forth task - to be replaced'
                  , '4 edit: edited task 4 - to stay as #4'
                  , 'del 1']

    def test_commands_series(self, test_db):
        db = test_db
        for command in self.commands:
            db.transact(command)
        
        assert db.tasklist.tasks == {2: Task(subject='todo everything @home - to stay as #2'), 
                                     3: Task(subject='other task @work - to stay as #3'), 
                                     4: Task(subject='edited task 4 - to stay as #4')}
    
    def test_list(self, test_db):
        db = test_db
        db.transact(['del', '0'])
        db.transact(['list'])
        s = Messenger(db.tasklist, silent=True).print().catch_output()
        assert s == 'Listed 0 of 0 tasks\n'


class Test_Arguments:

    def test_list(self):
        arglist = ['list']
        assert Arguments(arglist).list is True

    def test_all_args(self):
        d = Arguments(['1', 'mark:', 'done'])
        assert isinstance(d.args, dict)

# TODO:
#     lines = list(TaskList().select(['@work']))
#     assert lines == ['3 other task @work - to stay 2']

if __name__ == "__main__":
    pytest.main([__file__, '--maxfail=1'])
