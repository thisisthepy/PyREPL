from __future__ import annotations
from inspect import isfunction
import traceback


from pythonx.compose.runtime.internal import ComposableLambdaImpl




def cp_info(target, ori):
    if ori is None:
        raise ValueError(f"Error: Origin of Target Composable should not be None. - <Origin>[{ori}], <Target>[{target}]")
    else:
        target.__dict__['__name__'] = ori.__name__
        target.__dict__['__doc__'] = ori.__doc__
        target.__dict__['__module__'] = ori.__module__


class Composable(ComposableLambdaImpl):
    """ Composable Maker Decorator for Jetpack Compose """
    __composers = []

    def _on_new_app(self, _id: str, composer):
        self.__composers = (_id, composer)

    @property
    def composer(self):
        return self.__composers[-1][1]

    def __new__(cls, composable=None):
        """ When @Composable is called """
        if not issubclass(composable, ComposableLambdaImpl):  # is child of ComposableLambdaImpl
            return super().__new__(composable)  # return an instance of the composable argument
        else:
            return super().__new__(cls)  # return a new instance of the Composable class

    def __init__(self, composable=None):
        """ When @Composable is called """
        if isfunction(composable):  # When the decorative target is a function
            self.compose = composable
            cp_info(self, composable)
            self.from_function = True
        elif composable is None or issubclass(composable, Composable):  # When the decorative target is a child class of Composable or itself
            cp_info(self, type(self) if composable is None else composable)
        else:  # When the decorative target is an object other than a child class of Composable
            if hasattr(composable, "content"):
                target = composable  # When the compose method is staticmethod/classmethod
                if isinstance(composable, staticmethod):  # When the compose method is staticmethod
                    self.from_function = True
            else:
                target = composable()  # When the compose method is instancemethod
            self.compose = target.compose
            cp_info(self, composable)

    def __repr__(self):
        return f"<{self.__module__}.{self.__name__} @Composable object at {hex(id(self))}>"

    def __str__(self):
        return self.__repr__()

    @staticmethod
    def compose(*args, **kwargs):
        """ Composition Content method for compose """
        pass

    def __invoke(self, *args, **kwargs):
        """ Invoke composableLambda / composableLambdaInstance
        Ref: https://sungbin.land/jetpack-compose-%EB%9F%B0%ED%83%80%EC%9E%84%EC%97%90%EC%84%9C-%EC%9D%BC%EC%96%B4%EB%82%98%EB%8A%94-%EB%A7%88%EB%B2%95-%EC%99%84%EC%A0%84%ED%9E%88-%ED%8C%8C%ED%95%B4%EC%B9%98%EA%B8%B0-composeinitial-4c4c306c0a8c
        !WARNING! keyword 'content' must be specified in the kwargs not in the args
        :raises ValueError: When content is not callable
        """
        composer = self.composer
        content = kwargs.pop("content", None)

        try:
            if isinstance(content, ComposableLambdaImpl):  # isinstance(content, JavaClass)
                # TODO: Find a way to check if the content is a JavaClass
                content = KotlinComposable(content)  # Raw Kotlin Composable
            elif content is None or callable(content):  # In case of None, Function, Method
                pass
            else:
                raise ValueError(f"Error: Invalid Content Type. Please check your Composable's arguments - Current content type: {type(content)}")

            if content is not None:
                kwargs['content'] = content

            return self.compose(*args, **kwargs)  # Python Composable
        except Exception as err:
            print("-----------------------------------------------------------------------------------------------------------")
            traceback.print_exc()
            print("-----------------------------------------------------------------------------------------------------------")
            raise err

    def __call__(self, *args, **kwargs):
        """ Do Composition
        :raises RuntimeError: When Composer is not set from Kotlin before Python is loaded
        """
        if self.composer is None:
            raise RuntimeError("Composer for Composable must be registered before Composition starts.")
        vars = self.compose.__code__.co_varnames
        try:
            # Check if content variable is set and where it is
            index = vars.index("content") - (0 if self.from_function else 1)  # ValueError could be raised

            # Find the actual content variable
            if "content" in kwargs:
                content = kwargs.pop("content")
            else:
                args = list(args)
                # if pop failed, that means the content argument is set but the content variable not been received
                content = args.pop(index)  # IndexError could be raised

            if content is None:
                content = EmptyComposable
        except (ValueError, IndexError) as _:
            content = None

        kwargs['content'] = content
        return self.__invoke(*args, **kwargs)


class KotlinComposable(Composable):
    """ Raw Kotlin Composable Wrapper Class """
    def __new__(cls, content):
        return super().__new__(cls)

    def __init__(self, content):
        super().__init__()
        self.content = content

    def compose(self, *args):
        ComposableWrapper(self.content, args, self.composer, 1)


class ComposeApp(Composable):
    """ App Class for Compose (should be instanced in Kotlin side) """

    def __init__(self, composer):
        super().__init__()
        self._register_composer(composer)

    def __del__(self):
        self._register_composer(None)
