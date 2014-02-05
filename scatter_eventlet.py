"""
    scatter.async.eventlet
    ~~~~~~~~~~~~~~~~~~~~~~

"""
from __future__ import absolute_import

__author__ = 'Andrew Hawker <andrew.r.hawker@gmail.com>'
__all__ = ('EventletService', 'EventletWorker', 'Event',
           'Lock', 'RLock', 'Semaphore', 'BoundedSemaphore', 'Queue', 'Signal')


import functools
import signal

from eventlet import greenpool, greenthread, event, queue, timeout, semaphore, spawn, getcurrent
from eventlet.timeout import Timeout
from scatter.async import Worker, WorkerPool
from scatter.async.greenlet import GreenletService
from scatter.exceptions import ScatterTimeout, ScatterExit, ScatterCancel


Event = None
Condition = None
Lock = None
RLock = None
Semaphore = None
BoundedSemaphore = None
Queue = None
Signal = None


class EventletWorker(Worker):
    """

    """

    def done(self):
        """
        """
        return self._worker.dead

    def running(self):
        """
        """
        return not self.done()

    def stop(self, timeout=None):
        """
        """
        try:
            with Timeout(timeout):
                self._worker.wait()
        except Timeout:
            self._worker.kill(ScatterExit)

    def join(self, timeout=None):
        """
        """
        try:
            with Timeout(timeout):
                self._worker.wait()
                return True
        except Timeout:
            return False

    def cancel(self, timeout=None):
        """
        """
        return self._worker.cancel(ScatterCancel)

    def get_result(self, timeout=None):
        """
        """
        try:
            with Timeout(timeout):
                return self._worker.wait()
        except Timeout:
            raise ScatterTimeout('[{0}] Failed to get result after {1} seconds.'.format(self.name, timeout))

    def add_callback(self, func):
        """
        """
        self._worker.link(self.callback(func))

    def remove_callback(self, func):
        """
        """
        self._worker._exit_funcs.remove(self.callback(func))


class EventletWorkerPool(WorkerPool):
    """

    """

    def __len__(self):
        return self.pool.running()

    def __contains__(self, item):
        return item in self.pool.coroutines_running

    def __iter__(self):
        return iter(self.pool.coroutines_running)

    @property
    def size(self):
        return self.pool.size

    def spawn(self, func, *args, **kwargs):
        """
        """
        return self.pool.spawn(func, *args, **kwargs)

    def spawn_later(self, seconds, func, *args, **kwargs):
        """
        """
        func = functools.partial(self.spawn, func, *args, **kwargs)
        return greenthread.spawn_after(seconds, func)

    def flush(self, timeout=None):
        """
        """
        try:
            self.log.info('Flushing {0} workers.'.format(len(self.workers)))
            with Timeout(timeout):
                for w in self.pool.coroutines_running:
                    w.kill(ScatterExit)
        except Timeout:
            raise ScatterTimeout('[{0}] Failed to flush all workers after {1} seconds.'.format(self.name, timeout))

    def resize(self, size):
        """
        """
        self.pool.resize(size)


class EventletService(GreenletService):
    """

    """

    def spawn(self, func, *args, **kwargs):
        worker = self.workers.spawn(func, *args, **kwargs)
        worker.name = 'Scatter-Worker-Eventlet-{0}'.format(len(self.workers))
        return EventletWorker(worker)

    def spawn_later(self, seconds, func, *args, **kwargs):
        worker = self.workers.spawn_later(seconds, func, *args, **kwargs)
        worker.name = 'Scatter-Worker-Eventlet-{0}'.format(len(self.workers))
        return EventletWorker(worker)

    def sleep(self, seconds):
        return greenthread.sleep(seconds)

    def queue(self, *args, **kwargs):
        return queue.Queue(*args, **kwargs)

    def pool(self, *args, **kwargs):
        return greenpool.GreenPool(*args, **kwargs)

    def worker_pool(self, size):
        return EventletWorkerPool(greenpool.GreenPool, size)

    def group(self, *args, **kwargs):
        pass

    def event(self, *args, **kwargs):
        pass

    def lock(self, *args, **kwargs):
        return semaphore.Semaphore(*args, **kwargs)

    def signal(self, *args, **kwargs):
        return signal.signal(*args, **kwargs)

    def on_initializing(self):
        """
        """
        self.config.setdefault('WORKER_POOL_SIZE', 1000)
        self.config.setdefault('WORKER_STOP_TIMEOUT', 5)

    def on_starting(self):
        """
        """
        self.workers = self.worker_pool(self.worker_pool_size)

    def on_stopping(self):
        """

        """
        #Ensure we're not a member of worker pool we're flushing.
        if getcurrent() in self.workers:
            return spawn(self.on_stopping).join()

        try:
            self.workers.flush(self.worker_stop_timeout)
        except ScatterTimeout:
            self.log.warning('Failed to stop all workers after {0} seconds.'.format(self.worker_stop_timeout))
