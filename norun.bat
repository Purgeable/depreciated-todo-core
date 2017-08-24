python guz.py delete all
@REM https://stackoverflow.com/questions/39435598/why-does-the-command-if-errorlevel-1-do-result-in-an-pause-of-batch-file-proc
@if errorlevel 1 pause
python guz.py new do task __ 1 +home
@if errorlevel 1 pause
python guz.py 1 edit: do task 1
@if errorlevel 1 pause
python guz.py 1 project: +home
@if errorlevel 1 pause
python guz.py list 
@if errorlevel 1 pause
python guz.py list +home
@if errorlevel 1 pause
python guz.py 1 mark unclear
@if errorlevel 1 pause
python guz.py 1 mark -?
@if errorlevel 1 pause
REM python guz.py 1 wait [<input>]
python guz.py 1 mark done
@if errorlevel 1 pause
python guz.py 1 mark fail
@if errorlevel 1 pause
python guz.py 1 mark cancel
@if errorlevel 1 pause
python guz.py 1 unmark
@if errorlevel 1 pause
python guz.py new do task 2 
@if errorlevel 1 pause
python guz.py new do task 3 
@if errorlevel 1 pause
python guz.py del 1
@if errorlevel 1 pause
python guz.py rebase all
@if errorlevel 1 pause
python guz.py -h
@if errorlevel 1 pause
