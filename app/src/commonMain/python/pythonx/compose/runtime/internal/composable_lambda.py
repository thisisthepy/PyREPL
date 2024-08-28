from androidx.compose.runtime.internal import ComposableLambdaImpl as _ComposableLambdaImpl
from java import dynamic_proxy


class ComposableLambdaImpl(dynamic_proxy(_ComposableLambdaImpl)):
    def __init__(self, lambda_):
        super().__init__(lambda_)

    def invoke(self, *args, composer=None, changed=0):
        return self.lambda_(*args)
