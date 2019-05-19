import unittest

from funcannote import *


class AnnotationTypeA(FunctionAnnotation):
    pass

class AnnotationTypeB(FunctionAnnotation):
    pass


class AnnotationTest(unittest.TestCase):
    def test_annotable_function_add_annotation(self):
        func = AnnotableFunction(lambda x: None)

        func.add_annotation(AnnotationTypeA())
        func.add_annotation(AnnotationTypeA())
        func.add_annotation(AnnotationTypeB())
    
        self.assertIsInstance(func.get_annotation(AnnotationTypeA), AnnotationTypeA)
        self.assertIsInstance(func.get_annotation(AnnotationTypeB), AnnotationTypeB)

        annotations = func.get_annotations(AnnotationTypeA)
        self.assertEqual(len(annotations), 2)
        self.assertTrue(all(isinstance(a, AnnotationTypeA) for a in annotations))

        all_annotations = func.get_annotations(FunctionAnnotation)
        self.assertEqual(len(all_annotations), 3)

    def test_add_annotation_decorator(self):

        @AnnotationTypeB()
        @AnnotationTypeA()
        def foo():
            return 10

        self.assertIsInstance(foo, AbstractAnnotableFunction)
        self.assertEqual(foo(), 10)

        self.assertIsNotNone(foo.get_annotation(AnnotationTypeA))
        self.assertIsNotNone(foo.get_annotation(AnnotationTypeB))

    def test_annotation_query_order(self):
        @AnnotationTypeB()
        @AnnotationTypeA()
        def foo():
            return 10

        annotations = foo.get_annotations(FunctionAnnotation)
        self.assertIsInstance(annotations[0], AnnotationTypeB)
        self.assertIsInstance(annotations[1], AnnotationTypeA)

    def test_annotation_method(self):

        class Test(object):
            def __init__(self, data):
                self.data = data

            @AnnotationTypeA()
            def get_data(self):
                return self.data


        instance = Test('test')
        self.assertIsInstance(instance.get_data, AbstractAnnotableFunction)
        self.assertEqual(instance.get_data(), 'test')