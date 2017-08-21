"""Unit- and behaviour testing of guz.py, a todo organiser."""

# -*- coding: utf-8 -*-

# FIXME: play with delegator
#import delegator
#c = delegator.run("python -v")

import pytest
import os
import io


from guz import DataStore, FILENAME
from guz import Task, TaskList
from guz import Arguments


TEMP_FILENAME = "temp.pickle"


def with_newline(x):
    newline = '\n'
    return '{}{}'.format(x, newline)


def set_datastore(filename, contents):
    ds = DataStore(filename)
    ds.to_disk(contents)


REF_DICT = {1: Task('do this'), 5: Task('do that')}


def tasklist(filename=TEMP_FILENAME, tasks_dict=REF_DICT):
    set_datastore(filename, tasks_dict)
    out = io.StringIO()
    return TaskList(filename, out), out


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

    def test_init_task_has_subject(self):
        assert self.t.subject == "do this"

    def test_init_task_no_status_given(self):
        assert self.t.status is None


class Test_TaskList:

    def setup_method(self):
        self.tasklist, self.out = tasklist()

    def test_tasks_attribute_is_dictionary(self):
        self.tasklist.tasks == REF_DICT

    def test_ids_attribute_is_list(self):
        assert isinstance(self.tasklist.ids, list)

    def test_on_list(self):
        self.tasklist.list()
        assert self.out.getvalue() == """ 1 [ ] do this
 5 [ ] do that
Listed 2 of 2 tasks
"""

    def test_on_delete_success(self):
        self.tasklist.delete_item(1)
        assert self.tasklist.tasks == {5: Task('do that')}
        assert self.out.getvalue() == \
            with_newline('Deleted task 1')
        self.setup_method()

    def test_on_delete_failed(self):
        self.tasklist.delete_item(0)
        assert self.out.getvalue() == (
            with_newline('No such task id: 0') +
            with_newline('Cannot delete task 0')
        )

    def test_on_rebase(self):
        self.tasklist.rebase()
        self.tasklist.tasks == {1: Task('do this'), 2: Task('do that')}
        assert self.out.getvalue() == \
            with_newline('Rebased task ids')


class Test_Arguments:

    def test_list(self):
        arglist = ['list']
        assert Arguments(arglist).list is True


def empty_tasklist():
    mockfile = "mock.pickle"
    silent = io.StringIO()
    mocklist = TaskList(mockfile, silent)
    mocklist.delete_all()
    return mocklist


class Test_Behaviour_Testing:

    def setup_method(self):
        pass

    def test_multiple_commands(self):
        tasklist = empty_tasklist()
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
        # FIXME: does not exit, not really replacing
        tasklist.replace_item(4, t4)
        tasklist.delete_item(1)

        lines = [tasklist.tasks[i].subject for i in tasklist.select_all_ids()]
        assert lines == ['todo everything @home - to stay 1',
                         'other task @work - to stay 2',
                         'edited task 4 - to stay 3']

# TODO:
#     lines = list(TaskList().select(['@work']))
#     assert lines == ['3 other task @work - to stay 2']
#


if __name__ == "__main__":
    pytest.main([__file__])
