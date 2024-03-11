import concurrent.futures
import random
import time


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
        return issubclass(other.__class__, Trapezoid)

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


def problem(choices):
    a, b, c = choices
    a = Trapezoid(*a)
    b = Rectangle(b[0], b[1])
    c = Square(c[0])

    shapes = [a, b, c]

    for i in range(1000):
        for a in shapes:
            for b in shapes:
                _ = a > b
                _ = a < b
                _ = a + b
                _ = a % b
                _ = b % a
                _ = a <= b

    return True


def _executor(func, repetitions, arr, max_processes, max_threads):
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_processes) as executor:
        futures = []
        _repetitions = repetitions // max_processes

        for _ in range(max_processes):
            future = executor.submit(_thread, func, _repetitions, arr, max_threads)
            futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            future.result()


def _thread(func, repetitions, arr, max_threads):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as thread_executor:
        futures = []
        for _ in range(repetitions):
            choices = random.choices(arr, k=3)
            future = thread_executor.submit(func, choices)
            futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            future.result()

def run_threads(problem, n_threads, arr, n_repetitions):
    for max_thread in range(2, n_threads + 1):
        start = time.time()
        _thread(problem, n_repetitions, arr, max_thread)
        end = time.time()
        print(f"took with {max_thread} threads:\t{end - start}")

def run_sequential(problem, arr, n_repetitions):
    start = time.time()
    for i in range(n_repetitions):
        choices = random.choices(arr, k=3)
        problem(choices)

    end = time.time()
    print(f"took sequentially:\t{end - start}")

def run_process_thread(problem, arr, n_repetitions, n_processes, n_threads):
    attempts = {}
    for max_process in range(2, n_processes + 1):
        for max_thread in range(2, n_threads + 1):
            start = time.time()
            task = _executor(problem, n_repetitions, arr, max_process, max_thread)
            end = time.time()
            print(f"took with {max_process} and {max_thread}:\t{end - start}")
            attempts[f"{max_process}-{max_thread}"] = end - start


if __name__ == "__main__":
    n_repetitions = 100
    n_processes = 3
    n_threads = 10
    arr = generate_three()

    run_process_thread(problem, arr, n_repetitions, n_processes, n_threads)

    run_threads(problem, arr, n_repetitions, n_threads)

    run_sequential(problem, arr, n_repetitions)

