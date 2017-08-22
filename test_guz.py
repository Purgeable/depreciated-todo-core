"""Unit- and behaviour testing of guz.py, a todo organiser."""

# -*- coding: utf-8 -*-

# FIXME: play with delegator
#import delegator
#c = delegator.run("python -v")

import pytest
import os
import io


from guz import DataStore, FILENAME
from guz import Task, TaskList, TaskListBase, Status
from guz import Arguments
from guz import catch_output, catch_tasklist


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

def tasklist(taskdict=REF_DICT):
    out = io.StringIO()
    return TaskList(taskdict, out), out


def teardown_module(module):
    """Cleanup temp files."""
    for filename in ("mock.pickle", TEMP_FILENAME):
        if os.path.exists(filename):
            os.remove(filename)


class Test_DataStore:

    def test_on_production_init_directs_to_global_filename(self):
        ds = DataStore()
        assert ds.filename == FILENAME


class Test_DataStore_with_temp_file:

    def setup_method(self):
        # some varialble to put and get from store
        self.contents = 'abc', 0
        set_datastore(TEMP_FILENAME, self.contents)
        self.ds = DataStore(TEMP_FILENAME)

    def test_on_temp_init_directs_to_other_filename(self):
        assert self.ds.filename == TEMP_FILENAME

    def test_on_temp_store_write_and_read_back_dictionary(self):
        assert self.ds.from_disk() == self.contents


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


class Test_TaskListBase:

    def setup_method(self):
        self.tasklist = TaskListBase({5: 'content 5', 1: 'content 1'})

    def test_task_ids_attribute(self):
        assert self.tasklist.task_ids == [1, 5]        

    def test_task_items_are_read_with_bracket(self):
        assert self.tasklist[1] == 'content 1'
        assert self.tasklist[5] == 'content 5'

    def test_is_valid_task_id_success(self):
        for n in [1, 5]:
            self.tasklist.is_valid_task_id(n) is True

    def test_is_valid_task_id_fails(self):
        for k in [x for x in range(-1,10) if x not in [1,5]]:
            self.tasklist.is_valid_task_id(k) is False    

    def test_get_max_task_id(self):
        self.tasklist.get_max_task_id() == 5
        
    def test_len(self):
        self.tasklist.len() == 2     


class Test_TaskList:

    def setup_method(self):
        self.tasklist, self.out = tasklist()

    def test_task_ids_attribute_repeated_test(self):
        assert self.tasklist.task_ids == [1, 5]        

    def test_tasks_attribute_is_dictionary(self):
        self.tasklist.tasks == {1: Task('do this'), 5: Task('do that')}
        
    def test_on_list(self):
        self.tasklist.list()
        assert self.out.getvalue() == concat([' 1 [ ] do this',
                                              ' 5 [ ] do that',
                                              'Listed 2 of 2 tasks'])

    def test_on_delete_success(self):
        self.tasklist.delete_item(1)
        assert self.tasklist.tasks == {5: Task('do that')}
        assert self.out.getvalue() == with_newline('Deleted task 1')
        self.setup_method()

    def test_on_delete_failed(self):
        self.tasklist.delete_item(0)
        assert self.out.getvalue() == with_newline('Task id not found: 0')

    def test_on_rebase(self):
        self.tasklist.rebase()
        self.tasklist.tasks == {1: Task('do this'), 2: Task('do that')}
        assert self.out.getvalue() ==  with_newline('Rebased task ids')
        self.setup_method()


class Test_Arguments:

    def test_list(self):
        arglist = ['list']
        assert Arguments(arglist).list is True

    def test_all_args(self):
        d = Arguments(['1', 'mark', 'done']).get_dict()
        assert isinstance(d, dict)


def empty_tasklist():
    silent = io.StringIO()
    return TaskList({}, silent)


class Test_Behaviour_On_Adding_Deleting_and_Replacing:

    def test_multiple_commands(self):
        tasklist = empty_tasklist()
        t = Task("one task @home - to delete")
        tasklist.add_item(t)
        t = Task("todo everything @home - to stay 1")
        tasklist.add_item(t)
        t = Task("other task @work - to stay 2")
        tasklist.add_item(t)
        t = Task("other task @work - to delete")
        tasklist.add_item(t)
        n = tasklist.get_max_task_id()
        tasklist.delete_item(n)
        t = Task("forth task - to be replaced")
        tasklist.add_item(t)
        t4 = Task("edited task 4 - to stay 3")
        # FIXME: not really replacing, adding even if not exists
        tasklist.replace_item(4, t4)
        tasklist.delete_item(1)

        lines = [tasklist.tasks[i].subject for i in tasklist.task_ids]
        assert lines == ['todo everything @home - to stay 1',
                         'other task @work - to stay 2',
                         'edited task 4 - to stay 3']


class Test_Catch_Output_After_Command(object):
    
    def setup_method(self):
        DataStore(TEMP_FILENAME).to_disk({})
        self.catch_output = lambda command_line: \
                            catch_output(command_line, path=TEMP_FILENAME)        

    def test_delete_returns_proper_message_strings(self):
        assert self.catch_output('delete all') == \
            with_newline('All tasks deleted. What made you do this?..')

        assert self.catch_output('del 0') == \
            with_newline('Task id not found: 0')

class Test_Catch_TaskList_After_Command(object):
    
    def setup_method(self):
        DataStore(TEMP_FILENAME).to_disk({})
        self.catch_tasklist = lambda command_list: \
                            catch_tasklist(command_list, path=TEMP_FILENAME)        

    def test_1(self):
        tlist = self.catch_tasklist(['delete all', 'new do this task'])
        assert tlist.tasks[1].subject == 'do this task'

# TODO:
#     lines = list(TaskList().select(['@work']))
#     assert lines == ['3 other task @work - to stay 2']
#


if __name__ == "__main__":
    pytest.main([__file__])
