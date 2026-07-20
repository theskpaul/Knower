import functools
import logging
import time

current_time = time.localtime()

logging.basicConfig(
    level=logging.INFO,
    format="{asctime} - {levelname} - {name} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    filename=f"tmp/log/{time.strftime('%Y-%m-%d_%H-%M', current_time)}-app.log",
    encoding="utf-8",
    filemode="a",
)


def log(title: str = ""):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*arg, **karg):
            logger = (
                logging.getLogger(func.__module__)
                if title == ""
                else logging.getLogger(f"[Title: {title}]")
            )
            logger.info("%s started", func.__name__)
            try:
                start = time.perf_counter()
                result = func(*arg, **karg)
                elapsed = time.perf_counter() - start
                logger.info("%s finished in %.4fs", func.__name__, elapsed)
                return result
            except Exception:
                logger.exception(f"{func.__name__} failed")
                raise

        return wrapper

    return decorator
