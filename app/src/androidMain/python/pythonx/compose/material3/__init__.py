from pythonx.compose.runtime import Composable
from pythonx.compose.ui import Modifier, Alignment
from pythonx.compose.layout import Arrangement

from java import jclass
import traceback

try:
    _material3 = jclass("io.github.thisisthepy.pycomposeui.Material3Kt")
    print("Compose Material3:", _material3)
    _material3_android = jclass("io.github.thisisthepy.pycomposeui.Material3_androidKt")
    print("Compose Android Material3:", _material3_android)
    _Text = _material3.TextWidget
    #Text = lambda composer, *args, **kwargs: _Text(*args, **kwargs, composer, 1)
    _SimpleText = _material3.SimpleTextWidget
    _SimpleColumn = _material3_android.SimpleColumnWidget
    _SimpleRow = _material3_android.SimpleRowWidget
    _SimpleButton = _material3_android.SimpleButtonWidget

    @Composable
    class Text(Composable):
        @classmethod
        def compose(cls, text: str = ""):
            _SimpleText(text, cls.composer, 1)

    @Composable
    class Column(Composable):
        @classmethod
        def compose(cls, modifier: Modifier,
                    vertical_arrangement: Arrangement.Vertical = Arrangement.Center,
                    horizontal_alignment: Alignment.Horizontal = Alignment.Horizontal.Start,
                    content=lambda: {}):
            _SimpleColumn(modifier, vertical_arrangement, horizontal_alignment, content, cls.composer, 1)

    @Composable
    class Row(Composable):
        @classmethod
        def compose(cls, content):
            _SimpleRow(content, cls.composer, 1)

    @Composable
    class Button(Composable):
        @classmethod
        def compose(cls, onclick, content):
            _SimpleButton(onclick, content, cls.composer, 1)

    _AnnotatedStringText = _material3.AnnotatedStringTextWidget
    #AnnotatedStringText = lambda composer, *args, **kwargs: _AnnotatedStringText(*args, **kwargs, composer, 1)
except Exception as e:
    print("-----------------------------------------------------------------------------------------------------------")
    traceback.print_exc()
    print("ERROR: PyComposeUI Material3 Library is not Found.")
    print("-----------------------------------------------------------------------------------------------------------")
    raise e
