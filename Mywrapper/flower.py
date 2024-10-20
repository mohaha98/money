"""=================不积跬步无以至千里==================
作    者： LEGION
创建时间： 2024/5/30 23:13
文件名： flower.py
功能作用： 
=================不积小流无以成江海=================="""
import time
from functools import wraps
from tools.logger import log

def decorator_with_args(decorator_arg1, decorator_arg2):
    """
    带参数的装饰器
    """
    def my_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 在调用原始函数之前执行的代码
            print(f"前置代码: {decorator_arg1}, {decorator_arg2}")

            result = func(*args, **kwargs)

            # 在调用原始函数之后执行的代码
            print(f"后置代码: {decorator_arg1}, {decorator_arg2}")

            return result
        return wrapper
    return my_decorator


def remove_spaces_decorator(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # Helper function to remove spaces from a string
        def remove_spaces(s):
            if isinstance(s, str):
                return s.replace(" ", "")
            if not s:
                return ""
            if isinstance(s, int):
                return str(s)
            return s
        # 处理位置参数
        cleaned_args = [remove_spaces(arg) for arg in args]
        # 处理关键字参数
        cleaned_kwargs = {key: remove_spaces(value) for key, value in kwargs.items()}
        # print(cleaned_kwargs)
        # Call the original function with cleaned arguments
        return func(self, *cleaned_args, **cleaned_kwargs)
    return wrapper

def validate_inputs(func):
    """
    输入验证装饰器
    输入验证装饰器用于验证函数输入的有效性
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if any(arg is None for arg in args):
            raise ValueError("None is not allowed as an input")
        return func(*args, **kwargs)
    return wrapper

def timer(func):
    """
    计时装饰器
    计时装饰器用于测量函数执行的时间
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        log.info(f"{func.__name__} executed in {end_time - start_time:.2f} seconds")
        return result
    return wrapper

def retry(max_attempts, delay):
    """
    重试装饰器
    用于在函数失败时自动重试，适用于网络请求或不稳定的操作
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    print(f"Attempt {attempts} failed: {e}")
                    time.sleep(delay)
            raise Exception(f"Failed after {max_attempts} attempts")
        return wrapper
    return decorator



def log_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if args:
            log.info(f"'{func.__name__}'函数入参 ---{args}")
        if kwargs:
            log.info(f"'{func.__name__}'函数入参 ---{kwargs}")
        result = func(*args, **kwargs)
        log.info(f"出参 ---{result}")
        return result
    return wrapper

if __name__ == "__main__":
    @log_decorator
    def add(**kwargs):
        for a,v in kwargs.items():
            print(a,v)

    test={'1':2,'3':4}
    add(**test)