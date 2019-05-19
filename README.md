Function Annotation
===================

**Table of contents**

* [Introduction](#introduction)
* [Basic workflow](#basic-workflow)
* [Decorator compatiblility](#decorator-compatiblility)


Introduction
------------

A super lightweight function annotation framework for python.

Python3 supports function annotation, but this syntax focuses more on type hinting today and attaching custom information via this feature is discouraged.

This framework provides decorators convert normal function(method) into a callable wrapping object. You can then implement custom annotation types and attach
them to the wrapping objects.


Basic workflow
--------------

To create custom annotation types, implement classes derived from `FunctionAnnotation`. The annotation class itself represents the information you want to
attach to the function, but you can also add additional data via its constructor.

```python
from funcannote import FunctionAnnotation

class APIStateAnnotation(FunctionAnnotation):
    pass

class APIObsolete(APIStateAnnotation):
    pass

class APIDeprecated(APIStateAnnotation):
    pass

class APIVersion(APIStateAnnotation):
    def __init__(self, version='0.0.0'):
        super().__init__()

        self.version = version


@APIVersion(version='1.0.1')
def dosomething():
    pass

@APIObsolete()
@APIVersion(version='0.5.0')
def dosomething_old():
    pass
```

To retrive annotation from decorated functions(methods), use the `get_annotationXXX` methods of the wrapping object.

```python
## get first annotation of the given type

dosomething.get_annotation(APIVersion)
# return APIVersion(version='1.0.1')

dosomething.get_annotation(APIObsolete)
# return None

## get all annotations of the given type

dosomething_old.get_annotations(APIStateAnnotation)
# return [APIObsolete(), APIVersion(version='0.5.0')]
```

Decorator compatiblility
------------------------

Since the annotation framework uses decorator mechanism a lot, it's possible that some code introduce decorators that don't recognize
annotation framework, these decorators could break the wrapping objects and the annotation information is then lost.

To prevent such problem, the best practice is to make sure to apply the annotations on top of the decorator chain. The annotation framework
also provides couple utility decorator functions to make normal decorators aware of the wrapping objects.

```python
import functools
from funcannote import FunctionAnnotation, annotation_compatible, annotation_compatible_ex

class CustomAnnotation(FunctionAnnotation):
    pass

@annotation_compatible
def throw_while_nil(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        if result is None:
            raise RuntimeError("return value is none")
        else:
            return result

    return wrapper

@annotation_compatible_ex
def log_result(prefix=''):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            print(prefix + str(result))
            return result

        return wrapper

    return decorator


@throw_while_nil
@CustomAnnotation()
def example_1():
    return None

@log_result('>>> ')
@CustomAnnotation()
def example_2():
    return 'hello world'
```