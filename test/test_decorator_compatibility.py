import unittest
import functools

from funcannote import *


class AnnotationTypeA(FunctionAnnotation):
    pass

class AnnotationTypeB(FunctionAnnotation):
    pass


class DecoratorTest(unittest.TestCase):
    def test_compatible_decorator(self):

        @annotation_compatible
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return 2 * func(*args, **kwargs)

            return wrapper

        @decorator
        def foo(val):
            return val * 5
        
        @decorator
        @AnnotationTypeA()
        def bar(val):
            return val * 10

        self.assertNotIsInstance(foo, AbstractAnnotableFunction)
        self.assertIsInstance(bar, AbstractAnnotableFunction)

        self.assertEqual(foo(5), 50)
        self.assertEqual(bar(5), 100)

        self.assertIsNotNone(bar.get_annotation(AnnotationTypeA))

    def test_compatible_decorator_factory(self):

        @annotation_compatible_ex
        def decorator_fac(mult):
            def decorator(func):
                @functools.wraps(func)
                def wrapper(*args, **kwargs):
                    return mult * func(*args, **kwargs)

                return wrapper

            return decorator

        @decorator_fac(5)
        def foo(val):
            return val * 5
        
        @decorator_fac(4)
        @AnnotationTypeB()
        def bar(val):
            return val * 10

        self.assertNotIsInstance(foo, AbstractAnnotableFunction)
        self.assertIsInstance(bar, AbstractAnnotableFunction)

        self.assertEqual(foo(5), 125)
        self.assertEqual(bar(5), 200)

        self.assertIsNotNone(bar.get_annotation(AnnotationTypeB))