"""
    scatter_eventlet.core
    ~~~~~~~~~~~~~~~~~~~~~

    Asynchronous primitives for eventlet.
"""
__author__ = 'Andrew Hawker <andrew.r.hawker@gmail.com>'
__all__ = ('Event', 'Condition', 'Lock', 'RLock', 'Semaphore', 'BoundedSemaphore', 'Queue', 'Signal')


import signal

from eventlet import event, semaphore, queue


Event = event.Event
Condition = None
Lock = None
RLock = None
Semaphore = semaphore.Semaphore
BoundedSemaphore = semaphore.BoundedSemaphore
Queue = queue.Queue
Signal = signal.signal