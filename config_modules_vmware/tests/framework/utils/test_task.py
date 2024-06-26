# Copyright 2024 Broadcom. All Rights Reserved.
import concurrent
import threading
import time

from config_modules_vmware.framework.utils import task


def test_multithreaded_function():
    """
    Test for multithreaded function
    """
    multithreaded_task = invoke_multithreaded_function_1()
    multithreaded_task.result()


def test_max_workers_used():
    """
    Test to make sure max workers are being used.
    max_workers = 3
    no. of tasks = 0-5
    Expected: Tasks 0, 1, 2 should be run on workers; Task 3 will run on MainThread; Task 4 will run on worker once
    previous task is complete.
    """
    task.Task.configure(max_workers=3)
    tasks = {}
    for i in range(5):
        tasks[i] = invoke_multithreaded_function_2(i)
    concurrent.futures.wait(tasks.values())
    results = [(_host, _future.result()) for _host, _future in tasks.items()]


def test_nested_functions():
    """
    Test to make sure that nested functions use available workers.
    max_workers = 3
    """
    task.Task.configure(max_workers=3)
    nested_task = invoke_multithreaded_function_3()
    nested_task.result()


def test_reconfigure_executor_same_max_workers():
    """
    Test to make sure reconfiguring executor with same worker count reuses executor.
    """
    thread_pool_task = task.threadpool()
    executor = thread_pool_task.executor
    thread_pool_task.configure(max_workers=executor.max_workers)
    assert executor is thread_pool_task.executor
    thread_pool_task.configure(max_workers=executor.max_workers)
    assert executor is thread_pool_task.executor


def test_reconfigure_executor_different_max_workers():
    """
    Test to make sure reconfiguring executor with different worker count shuts down old executor and starts new one.
    """
    thread_pool = task.threadpool()
    executor = thread_pool.executor
    thread_pool.configure(max_workers=executor.max_workers)
    assert executor is thread_pool.executor
    thread_pool.configure(max_workers=executor.max_workers + 1)
    assert executor is not thread_pool.executor


def test_manual_executor_shutdown():
    """
    Test case to check if new executor is configured when existing one is shutdown.
    """
    thread_pool_task = task.threadpool()
    executor = thread_pool_task.executor
    thread_pool_task.shutdown()
    thread_pool_task.configure()
    new_executor = thread_pool_task.executor
    assert executor is not new_executor


@task.threadpool
def invoke_multithreaded_function_1(thread=None):
    assert threading.current_thread() is not threading.main_thread()
    assert threading.current_thread() is not thread


@task.threadpool
def invoke_multithreaded_function_2(index):
    print("{} {}".format(index, threading.current_thread()))
    thread_pool = task.threadpool()
    executor = thread_pool.executor
    if index == 3 and hasattr(executor, "_idle_semaphore"):
        assert threading.current_thread() is threading.main_thread()
        time.sleep(5)  # sleep longer on the main thread to ensure a worker finishes first.
    elif index == 4 and not hasattr(executor, "_idle_semaphore"):
        assert threading.current_thread() is threading.main_thread()
        time.sleep(5)  # sleep longer on the main thread to ensure a worker finishes first.
    else:
        assert threading.current_thread() is not threading.main_thread()
        time.sleep(3)  # sleep to occupy workers


@task.threadpool
def invoke_multithreaded_function_3():
    assert threading.current_thread() is not threading.main_thread()
    multithreaded_task = invoke_multithreaded_function_1(threading.current_thread())
    multithreaded_task.result()
