import inspect
import logging

from .request import Request

logger = logging.getLogger(__name__)


def middleware(middleware_generator):
    assert inspect.isgeneratorfunction(middleware_generator)

    def decorator(fn):
        if not hasattr(fn, '__middleware__'):
            fn.__middleware__ = []

        fn.__middleware__.append(middleware_generator)
        return fn

    decorator.__middleware_instance__ = middleware_generator
    return decorator


def log(id):
    @middleware
    def inner(req: Request):
        logger.info(f'{id}: Logger called')
        logger.info(f'{id}: {req}')
        yield
        logger.info(f'{id}: After handeler')

    return inner