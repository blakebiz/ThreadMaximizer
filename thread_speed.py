import time, threading
from itertools import permutations

class BestTime:
    def __init__(self, workers):
        self.best = None
        self.order = []
        self.index = 0
        self.length = 0
        self.workers = workers

    def __str__(self):
        return f'time: {round(self.best, 2)}, order: {self.order}, workers: {self.workers}'

    def store(self, best, order):
        self.length += 1
        if self.best is None or best < self.best:
            self.best = best
            self.order = order
            self.index = self.length

def wrap_mult(*args):
    def wrapper():
        for arg in args:
            arg()
    return wrapper

def timer(f, store=None):
    def wrapper():
        best, order = f()
        if store:
            store.store(best, order)
        return best, order
    return wrapper

def simulate_threads(threads, limit):
    thrds = threads.copy()
    running = []
    timer = 0
    while threads or running:
        if len(running) < limit and threads:
            running.append(threads.pop(0))
        else:
            low = min(running)
            ind = 0
            timer += low
            for _ in range(len(running)):
                if running[ind] == low:
                    running.pop(ind)
                else:
                    running[ind] -= low
                    ind += 1
    return timer, thrds

def limit_threads(limit, threads, reverse=True, interval=.1, time_limit=None):
    '''
    :param limit:
    An int limit of how many threads max should run at a time
    :param threads:
    A list of threads that haven't been started
    :param reverse:
    By default for efficiency reasons the threads will be ran in reverse order of passed in but change this to False
    to run it in the order it was passed in.
    :param interval:
    How long the function sleeps for before checking to see if a thread dies to start a new one
    :param time_limit:
    An int representing the max times the threads will be allowed to run. Once this limit is reached the current
    threads will be allowed to finish but no new ones will be started.
    '''
    if time_limit is not None:
        start = time.time()
    if not reverse:
        threads.reverse()
    running = []
    count = 0
    while threads:
        ind = 0
        for _ in range(len(running)):
            if not running[ind].is_alive():
                running.pop(ind)
            else:
                ind += 1
        if len(running) < limit:
            thread = threads.__next__()
            thread.start()
            running.append(thread)
        if count >= limit:
            time.sleep(interval)
        count += 1
        if time_limit is not None:
            if (time.time() - start) > time_limit:
                break
    for thrd in running:
        thrd.join()

def testFuncsGen(count, funcs, store, grouping=1, condensed=True):
    '''
    :param count:
    The amount of times each function is to be ran
    :param funcs:
    all of the functions to be ran
    :param time_limit:
    In the case of long lists completion time grows exponentially. To limit this specify time_limit as a positive
    integer representing the max time the program should run before returning a solution.
    WARNING - this does not speed up the program it simply stops it after x seconds, when using a time_limit you
    are NOT guaranteed to get the best-case result it will return the best case it was able to find in the time given.
    :return:
    '''
    if condensed:
        running = True
        while running:
            try:
                fncs = []
                for _ in range(grouping):
                    fncs.append(timer(funcs.__next__(), store=store))
                if count > 1:
                    fncs *= count
                yield threading.Thread(target=wrap_mult(*fncs))
            except StopIteration:
                running = False

    else:
        for func in funcs:
            for i in range(count):
                yield threading.Thread(target=timer(func, store=store))

def run_tests(count, funcs, thread_limit=1, time_limit=None, workers=None):
    store = BestTime(workers)
    threads = testFuncsGen(count, funcs, store)
    limit_threads(thread_limit, threads, time_limit=time_limit, interval=0)
    # for thread in threads:
    #     thread.start()
    return store

def get_tests(threads, limit):
    for perm in permutations(threads):
        yield wrap(simulate_threads, list(perm), limit)

def order_threads(gThreads, limit, thread_count=1, time_limit=None):
    """
    :param gThreads:
    A list of integers being the run time of your threads in seconds in the same order your threads are in
    :param limit:
    the amount of threads that can run at one time in your program
    :param thread_count:
    Increase this to increase test speed with same accuracy in results, warning the total amount of threads ran by the
    program will be thread_count * limit
    :param time_limit:
    In the case of long lists completion time grows exponentially. To limit this specify time_limit as a positive
    integer representing the max time the program should run before returning a solution.
    WARNING - this does not speed up the program it simply stops it after x seconds, when using a time_limit you
    are NOT guaranteed to get the best-case result it will return the best case it was able to find in the time given.
    :return:
    A tuple of the best order to run your threads in for fastest run time
    """

    store = run_tests(1, get_tests(gThreads, limit), thread_limit=thread_count, time_limit=time_limit, workers=limit)
    # print(f'Choice was index {store.index} of {store.length}')
    return store

def wrap(func, arg1, arg2):
    def wrapper():
        return func(arg1, arg2)
    return wrapper


def wrap_thread(thread):
    def wrapper():
        thread.run()
    return wrapper

def main(tc=1):
    # # for a step by step guide on how to use this just uncomment everything below
    # # Make a list of threads
    # threads = []
    # for i in range(2, 9, 2):
    #     # make a thread
    #     thread = threading.Thread(target=sleeper, args=[i])
    #     # add the thread to the list
    #     threads.append(thread)
    # # Wrap the threads in a function so they can be time-tested
    # wrapped_threads =[]
    # for thread in threads:
    #     # wrap each thread in a function (if you already have a list you can just iterate through your list of threads
    #     # and append them to a new list wrapped in a function like shown below. This is just for testing time it takes
    #     # the threads to run
    #     wrapped_thread = wrap_thread(thread)
    #     # add the wrapped thread to the list
    #     wrapped_threads.append(wrapped_thread)
    # times = testFuncs(1, wrapped_threads)
    # # unnecessary step I'm just rounding off the times
    # for ind in range(len(times)):
    #     times[ind] = int(times[ind][0])
    # print(times)
    # # Order the threads
    # # I chose my limit as 2, choose whatever you want
    # order = order_threads(times, 2)
    # # done, order is the best case order for your threads
    # print(order)

    start = time.time()
    print(order_threads([22, 6, 2, 12, 4, 8, 6, 14, 8, 3, 5, 2], 2, thread_count=tc))
    print(f'Run time: {time.time()-start}')

if __name__ == '__main__':
    main(1000000000)