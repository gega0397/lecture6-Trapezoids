import concurrent.futures
import random
import time
import operator


glob_results = {}
def timeis(func):
    # Decorator that reports the execution time.
    def wrap(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()

        print(func.__name__, end - start)
        return result

    return wrap


def generate_three(n=10):
    # generates 'n' element list of list of three random integers eg: [[1,2,3],[3,4,5]]
    return [[random.randint(1, 200)] * 3 for _ in range(n)]


class TrapezoidError(Exception):
    pass


class Trapezoid:

    @staticmethod
    def check_other(other):
        return isinstance(other, Trapezoid)

    def __init__(self, *args):
        if len(args) == 3:
            self.a, self.b, self.h = args
        else:
            raise TrapezoidError(f"wrong number of parameters: {len(args)}, {args}")

    def __str__(self):
        return f"trapezoid:\n\tsides:\t{self.a}, {self.b} \n\theight:\t{self.h}"

    def area(self):
        a1 = min(self.a, self.b) * self.h
        a2 = (abs(self.a - self.b) * self.h) / 2
        return a1 + a2

    def __le__(self, other):
        if self.check_other(other):
            return self.area() <= other.area()
        else:
            raise TrapezoidError(f"expected class:\t{self.__class__}\nreceived:\t{type(other)}")

    def __lt__(self, other):
        if self.check_other(other):
            return self.area() < other.area()
        else:
            raise TrapezoidError(f"expected class:\t{self.__class__}\nreceived:\t{type(other)}")

    def __ge__(self, other):
        return not self.__lt__(other)

    def __gt__(self, other):
        return not self.__le__(other)

    def __eq__(self, other):
        if self.check_other(other):
            return self.area() == other.area()
        else:
            raise TrapezoidError(f"expected class:\t{self.__class__}\nreceived:\t{type(other)}")

    def __add__(self, other):
        if self.check_other(other):
            return self.area() + other.area()
        else:
            raise TrapezoidError(f"expected class:\t{self.__class__}\nreceived:\t{type(other)}")

    def __sub__(self, other):
        if self.check_other(other):
            return abs(self.area() - other.area())
        else:
            raise TrapezoidError(f"expected class:\t{self.__class__}\nreceived:\t{type(other)}")

    def __mod__(self, other):
        if self.check_other(other):
            return self.area() // other.area()
        else:
            raise TrapezoidError(f"expected class:\t{self.__class__}\nreceived:\t{type(other)}")


class Rectangle(Trapezoid):

    def __init__(self, *args):
        if len(args) == 2:
            self.a, self.h = args
            super().__init__(self.a, self.a, self.h)
        else:
            raise TrapezoidError("wrong number of parameters")

    def __str__(self):
        return f"Rectangle:\n\tside:\t{self.a} \n\theight:\t{self.h}"


class Square(Trapezoid):
    def __init__(self, *args):
        if len(args) == 1:
            self.a, = args
            super().__init__(*[self.a] * 3)
        else:
            raise TrapezoidError("wrong number of parameters")

    def __str__(self):
        return f"Square:\n\tside:\t{self.a}"


def problem(choices, problem_repetition):
    operators = [operator.gt, operator.lt, operator.add, operator.mod, operator.mod, operator.le]

    for i in range(problem_repetition):
        a, b, c = choices
        a = Trapezoid(*a)
        b = Rectangle(b[0], b[1])
        c = Square(c[0])

        shapes = [a, b, c]

        _len = len(shapes)
        for a in range(_len):
            for b in range(a + 1, _len):
                _a = shapes[a]
                _b = shapes[b]
                for op in operators:
                    opa = op(_a, _b)

def _executor(problem, arr, n_repetitions, problem_repetition, max_processes, max_threads):
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_processes) as executor:
        futures = []
        n_repetitions = n_repetitions // max_processes

        if max_threads == 1:
            for _ in range(max_processes):
                future = executor.submit(run_sequential, problem, arr, n_repetitions, problem_repetition)
                futures.append(future)
        else:
            for _ in range(max_processes):
                future = executor.submit(_thread, problem, arr, n_repetitions, problem_repetition, max_threads)
                futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            future.result()


def _thread(problem, arr, n_repetitions, problem_repetition, max_threads):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as thread_executor:
        futures = []
        for _ in range(n_repetitions):
            choices = random.choices(arr, k=3)
            future = thread_executor.submit(problem, choices, problem_repetition)
            futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            future.result()


def run_threads(problem, arr, n_repetitions, problem_repetition, n_threads):
    attempts = {}
    for max_thread in range(2, n_threads + 1):
        start = time.time()
        _thread(problem, arr, n_repetitions, problem_repetition, max_thread)
        end = time.time()
        print(f"took with {max_thread} threads:\t{end - start}")
        attempts[f"0-{max_thread}"] = end - start
    return attempts


def run_sequential(problem, arr, n_repetitions, problem_repetition, _print=False):
    if _print:
        start = time.time()
    for i in range(n_repetitions):
        choices = random.choices(arr, k=3)
        problem(choices, problem_repetition)

    if _print:
        end = time.time()
        print(f"took sequentially:\t{end - start}")
        return {"0-0": end-start}


def run_process_thread(problem, arr, n_repetitions, problem_repetition, n_processes, n_threads):
    attempts = {}
    for max_process in range(2, n_processes + 1):
        for max_thread in range(1, n_threads + 1):
            start = time.time()
            _executor(problem, arr, n_repetitions, problem_repetition, max_process, max_thread)
            end = time.time()
            print(f"took with {max_process} process and {max_thread} thread:\t{end - start}")
            attempts[f"{max_process}-{max_thread}"] = end - start
    return attempts


if __name__ == "__main__":
    n_repetitions = 100
    n_processes = 3
    n_threads = 5
    problem_repetitions = 100
    arr = generate_three()

    scores = {}

    for problem_repetition in range(problem_repetitions):

        print("problem rep: \t", problem_repetition)
        scores[problem_repetition] = {}

        d1 = run_process_thread(problem, arr, n_repetitions, problem_repetition, n_processes, n_threads)

        d2 = run_threads(problem, arr, n_repetitions, problem_repetition, n_threads)

        d3 = run_sequential(problem, arr, n_repetitions, problem_repetition, _print=True)

        scores[problem_repetition].update(d1)
        scores[problem_repetition].update(d2)
        scores[problem_repetition].update(d3)

    max_scores = {}
    for k, v in scores.items():
        #print(k,v)
        max_scores[k] = min(v, key=v.get)
    for k,v in max_scores.items():
        print(k, v, scores[k][v])
