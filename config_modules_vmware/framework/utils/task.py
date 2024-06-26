import concurrent.futures
import functools
import threading
import typing
from concurrent.futures import Future


class Task:
    """
    Class that wraps the passed functions and submits them to the ThreadPoolExecutor.
    The Task Class holds the single instance of the ThreadPoolExecutor.
    """

    __executor = None

    @classmethod
    def configure(cls: typing.Type["Task"], max_workers=None) -> None:
        """Pool executor create and configure.
        :param max_workers: Maximum workers
        """
        if isinstance(cls.__executor, ThreadPoolExecutor) and not cls.__executor.is_shutdown:
            if cls.__executor.max_workers == max_workers:
                return
            cls.__executor.shutdown()
        cls.__executor = ThreadPoolExecutor(max_workers=max_workers)

    @classmethod
    def shutdown(cls: typing.Type["Task"]) -> None:
        """Shutdown executor."""
        if cls.__executor is not None:
            cls.__executor.shutdown()

    @property
    def executor(self) -> "ThreadPoolExecutor":
        """Executor instance."""
        if not isinstance(self.__executor, ThreadPoolExecutor) or self.__executor.is_shutdown:
            self.configure()
        return self.__executor

    @property
    def _func(self):
        """Get wrapped function."""
        return self.__func

    def __init__(self, func=None) -> None:
        """Init method
        :param func: function
        """
        self.__func = func

    def _get_function_wrapper(self, func):
        """Here wrapper is constructed and returned.
        :param func: Wrapped function
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """Main function wrapper.
            :return: function
            """
            return self.executor.check_and_submit(func, *args, **kwargs)

        return wrapper

    def __call__(self, *args, **kwargs):
        """Callable instance.
        :return: Future
        """

        if self._func:
            wrapped = self._func
        else:
            wrapped = list(args).pop(0)
        wrapper = self._get_function_wrapper(wrapped)
        if self.__func:
            return wrapper(*args, **kwargs)
        self.__func = wrapper
        return wrapper


def threadpool(func=None):
    """Post function to ThreadPoolExecutor.
    :param func: function to wrap
    :return: ThreadPool instance, if called as function or argumented decorator, else callable wrapper
    Usages:
    (1)
        multithreaded_task = invoke_multithreaded_function_1()
        multithreaded_task.result()

        @task.threadpool()  # function
        def invoke_multithreaded_function_1():
            assert threading.current_thread() is not threading.main_thread()

    (2)
        multithreaded_task = invoke_multithreaded_function_1()
        multithreaded_task.result()

        @task.threadpool    # argument decorator
        def invoke_multithreaded_function_1():
            assert threading.current_thread() is not threading.main_thread()

    (3)
        multithreaded_task = task.threadpool(invoke_multithreaded_function_1) # callable wrapper
        f = multithreaded_task()
        f.result()

    """
    if func is None:
        return Task(func=func)
    return Task(func=None)(func)


class ThreadPoolExecutor(concurrent.futures.ThreadPoolExecutor):
    """
    Class that submits functions to be completed on a separate worker thread if one is available.
    If no worker threads are available, it executes the function on the current thread and returns the result.
    """

    def __init__(self, max_workers):
        super().__init__(max_workers=max_workers)
        self.lock = threading.Lock()

    def check_free_workers(self) -> bool:
        """Check if workers are available.
        :rtype: bool
        """
        if len(self._threads) < self._max_workers:
            return True
        if hasattr(self, "_idle_semaphore"):
            acquire = self._idle_semaphore.acquire(blocking=False)  # pylint: disable=E1101
            if acquire:
                self._idle_semaphore.release()  # pylint: disable=E1101
                return True
        # Below elif is a workaround to support Python 3.7 where the _idle_semaphore had not been implemented yet.
        # It means that if no worker threads are available, one more task will be queued and the next would execute on
        #   the current thread. This is slightly different than in Python 3.8+ where that one task would not be queued.
        elif hasattr(self, "_work_queue"):
            if self._work_queue.empty():
                return True
        return False

    @property
    def max_workers(self) -> int:
        """MaxWorkers.
        :rtype: int
        """
        return self._max_workers

    @property
    def is_shutdown(self) -> bool:
        """Executor shutdown state.
        :rtype: bool
        """
        return self._shutdown

    def check_and_submit(self, func, *args, **kwargs):
        """Checks for free workers and submits the work.
        @param func: callable function
        @param args:
        @param kwargs:
        @return: a future instance
        """
        with self.lock:
            future = Future()
            if self.check_free_workers():
                future = self.submit(func, *args, **kwargs)
            else:
                future.set_result(func(*args, **kwargs))
            return future
