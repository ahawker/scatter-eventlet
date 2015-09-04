"""
    scatter_eventlet.worker
    ~~~~~~~~~~~~~~~~~~~~~~~

"""
__author__ = 'Andrew Hawker <andrew.r.hawker@gmail.com>'
__all__ = ('EventletWorkerService',)


from eventlet import greenthread

from scatter.async import Worker, WorkerService
from scatter.exceptions import ScatterExit
from scatter_eventlet.core import Event


class ScatterEventlet(greenthread.GreenThread):
    """

    """

    def __init__(self, *args, **kwargs):
        super(ScatterEventlet, self).__init__(*args, **kwargs)
        self._started = Event()
        self._completed = Event()

    def started(self):
        """
        """
        pass

    def running(self):
        """
        """
        pass

    def cancelled(self):
        """
        """
        pass

    def completed(self):
        """
        """
        pass

    def run(self):
        pass

    def cancel(self):
        pass

    def stop(self, exception=ScatterExit, block=True, timeout=None):
        pass

    def join(self, timeout=None):
        pass

    def is_current(self):
        """
        """
        return greenthread.getcurrent() is self


class EventletWorker(Worker):
    """
    """

    worker_cls = ScatterEventlet


class EventletWorkerService(WorkerService):
    """
    """

    def on_initializing(self, *args, **kwargs):
        """
        """
        self.worker_class = EventletWorker