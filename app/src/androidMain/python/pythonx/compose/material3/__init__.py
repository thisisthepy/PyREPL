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
    _SimpleSpacer = _material3.SimpleSpacer
    _SimpleColumn = _material3_android.SimpleColumnWidget
    _SimpleRow = _material3_android.SimpleRowWidget
    _SimpleButton = _material3_android.SimpleButtonWidget
    _SimpleCardWidget = _material3_android.SimpleCardWidget
    _SimpleTextField = _material3_android.SimpleTextField

    _SimpleIcon = _material3.SimpleIcon
    _FavoriteIcon = _material3.FavoriteIcon
    _AddIcon = _material3.AddIcon
    _KeyboardArrowDownIcon = _material3.KeyboardArrowDownIcon
    _KeyboardArrowUpIcon = _material3.KeyboardArrowUpIcon
    _PlayArrowIcon = _material3.PlayArrowIcon
    _DeleteIcon = _material3.DeleteIcon

    class DefaultIcons:
        Favorite = _FavoriteIcon
        Add = _AddIcon
        KeyboardArrowDown = _KeyboardArrowDownIcon
        KeyboardArrowUp = _KeyboardArrowUpIcon
        PlayArrow = _PlayArrowIcon
        Delete = _DeleteIcon

    @Composable
    class Text(Composable):
        @classmethod
        def compose(cls, text: str = "", color: int = 0xFF000000, font_size: float = 16.0):
            _SimpleText(text, color, font_size, cls.composer, 1)

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
        def compose(cls, modifier: Modifier,
                    horizontal_arrangement: Arrangement.Horizontal = Arrangement.Center,
                    vertical_alignment: Alignment.Vertical = Alignment.Vertical.Top,
                    content=lambda: {}):
            _SimpleRow(modifier, horizontal_arrangement, vertical_alignment, content, cls.composer, 1)

    @Composable
    class Button(Composable):
        @classmethod
        def compose(cls, onclick, enabled: bool = True, corner_radius: float = 20.0, color: int = 0xFF000000, content = lambda: {}):
            _SimpleButton(onclick, enabled, corner_radius, color, content, cls.composer, 1)

    @Composable
    class Card(Composable):
        @classmethod
        def compose(cls, modifier: Modifier, corner_radius: float = 20.0, color: int = 0xFF000000, content = lambda: {}):
            _SimpleCardWidget(modifier, corner_radius, color, content, cls.composer, 1)

    @Composable
    class Icon(Composable):
        @classmethod
        def compose(cls, icon, content_description: str = "", modifier: Modifier = Modifier(), color: int = 0xFF000000):
            _SimpleIcon(icon, content_description, modifier, color, cls.composer, 1)

    @Composable
    class Spacer(Composable):
        @classmethod
        def compose(cls, start: float = 0.0, top: float = 0.0, end: float = 0.0, bottom: float = 0.0):
            _SimpleSpacer(start, top, end, bottom, cls.composer, 1)

    @Composable
    class TextField(Composable):
        @classmethod
        def compose(cls, text_state, padding: int = 8):
            _SimpleTextField(text_state, padding, cls.composer, 1)


    _AnnotatedStringText = _material3.AnnotatedStringTextWidget
    #AnnotatedStringText = lambda composer, *args, **kwargs: _AnnotatedStringText(*args, **kwargs, composer, 1)
except Exception as e:
    print("-----------------------------------------------------------------------------------------------------------")
    traceback.print_exc()
    print("ERROR: PyComposeUI Material3 Library is not Found.")
    print("-----------------------------------------------------------------------------------------------------------")
    raise e
