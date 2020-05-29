import random
import threading
import time
import itertools

from thread_speed import simulate_threads, order_threads


class Storage:
    def __init__(self):
        self.n = 0
    def __str__(self):
        return str(self.n)


def gen_tests(count, mn, mx, tp=float):
    rv = []
    for _ in range(count):
        tasks = []
        for _ in range(random.randint(mn, mx)):
            if tp == float:
                tasks.append(random.randint(1, 1000)/100)
            else:
                tasks.append(random.randint(1, 10))
        workers = random.randint(1, 6)
        rv.append((tasks, workers))
    return rv
        

def order_tasks(tasks,workers):
    tasks= list(itertools.permutations(tasks));best_tasks_ = tasks[0]
    def order_tasks_(tasks_, workers_):
        time = 0
        while tasks_ != []:
            time, tasks_ = time + [round(1 if min(tasks_[:workers_]) > 1 else min(tasks_[:workers_]), 2) for i, val in enumerate(tasks_)][0], [round(val - (1 if min(tasks_[:workers_]) > 1 else min(tasks_[:workers_])), 2) if i < workers_ and val > 0 else round(val, 2) for i, val in enumerate(tasks_)];tasks_ = list(filter(lambda x: x > 0, tasks_))
        return round(time, 2)
    best_tasks_ = [x if order_tasks_(x,workers)<order_tasks_(best_tasks_,workers) else best_tasks_ for x in tasks[1:]][0]
    return [order_tasks_(best_tasks_,workers),best_tasks_,workers]

def test_case(test, tot1, tot2, p, f):
    start1 = time.time()
    testing = order_tasks(test[0].copy(), test[1])
    end1 = time.time() - start1
    start2 = time.time()
    valid = order_threads(test[0].copy(), test[1])
    end2 = time.time() - start2
    tot1.n += end1
    tot2.n += end2
    # print(f'input: {test}')
    # print(str(valid) + '\n')
    if round(testing[0], 1) == round(valid.best, 1):
        if round(simulate_threads(list(testing[1]).copy(), testing[2])[0], 1) == round(testing[0], 1):
            p.n += 1
            print("Passed!")
        else:
            f.n += 1
            print("Right time, wrong order")
            print(
            f'tasks: {test[0]}, workers: {test[1]}\nuser result: {testing}, biz result: {valid}, workers: {test[1]}\n')
    else:
        f.n += 1
        print(f'tasks: {test[0]}, workers: {test[1]}\nuser result: {testing}, biz result: {valid}, workers: {test[1]}\n')

def test_main():
    test_cases = gen_tests(10, 3, 7)

    tot1, tot2, p, f = Storage(), Storage(), Storage(), Storage()
    threads = []
    for test in test_cases:
        thread = threading.Thread(target=test_case, args=(test, tot1, tot2, p, f))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    print(f'user passed: {p}, user failed: {f}')
    print(f'user run time: {tot1}')
    print(f'Biz run time: {tot2}')


test_main()



