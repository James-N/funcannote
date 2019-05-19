import functools
from abc import ABCMeta, abstractmethod


__all__ = ['FunctionAnnotation', 'AbstractAnnotableFunction', 'AnnotableFunction',
           'annotation_compatible', 'annotation_compatible_ex']


class FunctionAnnotation(object, metaclass=ABCMeta):
    """
    base class for function annotation
    """
    
    def __call__(self, func):
        if not isinstance(func, AnnotableFunction):
            func = convert_to_annotable(func)

        func.add_annotation(self)
        return func


class AbstractAnnotableFunction(object, metaclass=ABCMeta):
    """
    abstract base class for annotable functions
    """

    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass

    @abstractmethod
    def add_annotation(self, annotation):
        pass

    @abstractmethod
    def get_annotation(self, annotation_type):
        pass

    @abstractmethod
    def get_annotations(self, annotation_type):
        pass

    @abstractmethod
    def get_annotations_by_types(self, *annotation_types):
        pass


class AnnotableFunction(AbstractAnnotableFunction):
    """
    functor provides ability to attach annotation
    """

    __slots__ = ('_func', '_annotations')


    def __init__(self, func):
        if not callable(func):
            raise TypeError("func must be callable")

        self._func = func
        self._annotations = []

    def __call__(self, *args, **kwargs):
        func = self._func
        return func(*args, **kwargs)

    def __get__(self, instance, owner):
        """
        use getter function intercepts method call
        """

        delegate = AnnotableFunctionDelegate(self, instance)
        functools.update_wrapper(delegate, wrapped=self,
                                 assigned=functools.WRAPPER_ASSIGNMENTS, updated=())

        return delegate

    def add_annotation(self, annotation):
        if not isinstance(annotation, FunctionAnnotation):
            raise TypeError("invalid annotation")

        self._annotations.append(annotation)

    def get_annotation(self, annotation_type):
        if not issubclass(annotation_type, FunctionAnnotation):
            raise TypeError("invalid annotation type")

        if len(self._annotations) > 0:
            for annotation in reversed(self._annotations):
                if isinstance(annotation, annotation_type):
                    return annotation
            else:
                return None
        else:
            return None

    def get_annotations(self, annotation_type):
        if not issubclass(annotation_type, FunctionAnnotation):
            raise TypeError("invalid annotation type")

        if len(self._annotations) > 0:
            return [a for a in reversed(self._annotations) if isinstance(a, annotation_type)]
        else:
            return []

    def get_annotations_by_types(self, *annotation_types):
        if any((not issubclass(t, FunctionAnnotation)) for t in annotation_types):
            raise TypeError("contains invalid annotation_type")

        if len(self._annotations) > 0:
            found = []
            for annotation in reversed(self._annotations):
                if any(isinstance(annotation, t) for t in annotation_types):
                    found.append(annotation)

            return found
        else:
            return []

    def apply_decorator(self, decorator):
        if not callable(decorator):
            raise TypeError("decorator must be callable")

        func = self._func
        self._func = decorator(func)


class AnnotableFunctionDelegate(AbstractAnnotableFunction):
    """
    delegate class used when attach annotation framework to methods
    """

    __slots__ = ('_afunc', '_caller')

    def __init__(self, afunc, caller):
        self._caller = caller
        self._afunc = afunc

    def __call__(self, *args, **kwargs):
        func = self._afunc
        return func.__call__(self._caller, *args, **kwargs)

    def add_annotation(self, annotation):
        self._afunc.add_annotation(annotation)

    def get_annotation(self, annotation_type):
        return self._afunc.get_annotation(annotation_type)

    def get_annotations(self, annotation_type):
        return self._afunc.get_annotations(annotation_type)

    def get_annotations_by_types(self, *annotation_types):
        return self._afunc.get_annotations_by_types(*annotation_types)


###############################
# support functions
###############################

def annotation_compatible(decorator):
    """
    makes a decorator compatible with AnnotableFunction,
    make sure not to break the information during a decoration chain
    """

    @functools.wraps(decorator)
    def wrapper(func):
        if isinstance(func, AnnotableFunction):
            func.apply_decorator(decorator)
            return func
        else:
            return decorator(func)

    return wrapper

def annotation_compatible_ex(decorator_fac):
    """
    makes a decorator factory compatible with AnnotableFunction
    """

    @functools.wraps(decorator_fac)
    def wrapper_fac(*args, **kwargs):
        decorator = decorator_fac(*args, **kwargs)
        return annotation_compatible(decorator)

    return wrapper_fac

def convert_to_annotable(func):
    """
    convert any function into AnnotableFunction
    """

    annotable = AnnotableFunction(func)
    functools.update_wrapper(annotable, wrapped=func,
                             assigned=functools.WRAPPER_ASSIGNMENTS, updated=())

    return annotable
