from pythonx.compose.runtime import Composable

from androidx.compose.material3 import ButtonKt


@Composable
class Button(Composable):
    """ M3 filled button """

    @classmethod
    def compose(
            cls,
            on_click,
            modifier,
            enabled,
            shape,
            colors,
            elevation,
            border,
            content_padding,
            interaction_source,
            content
    ):
        ButtonKt.Button(
            onClick=on_click,
            modifier=modifier,
            enabled=enabled,
            shape=shape,
            colors=colors,
            elevation=elevation,
            border=border,
            contentPadding=content_padding,
            interactionSource=interaction_source,
            content=content,
            c=cls.composer,
            changed=1
        )


@Composable
class ElevatedButton(Composable):
    """ M3 elevated button """

    @classmethod
    def compose(
            cls,
            on_click,
            modifier,
            enabled,
            shape,
            colors,
            elevation,
            border,
            content_padding,
            interaction_source,
            content
    ):
        ButtonKt.ElevatedButton(
            onClick=on_click,
            modifier=modifier,
            enabled=enabled,
            shape=shape,
            colors=colors,
            elevation=elevation,
            border=border,
            contentPadding=content_padding,
            interactionSource=interaction_source,
            content=content,
            c=cls.composer,
            changed=1
        )


@Composable
class FilledTonalButton(Composable):
    """ M3 filled tonal button """

    @classmethod
    def compose(
            cls,
            on_click,
            modifier,
            enabled,
            shape,
            colors,
            elevation,
            border,
            content_padding,
            interaction_source,
            content
    ):
        ButtonKt.FilledTonalButton(
            onClick=on_click,
            modifier=modifier,
            enabled=enabled,
            shape=shape,
            colors=colors,
            elevation=elevation,
            border=border,
            contentPadding=content_padding,
            interactionSource=interaction_source,
            content=content,
            c=cls.composer,
            changed=1
        )


@Composable
class OutlinedButton(Composable):
    """ M3 outlined button """

    @classmethod
    def compose(
            cls,
            on_click,
            modifier,
            enabled,
            shape,
            colors,
            elevation,
            border,
            content_padding,
            interaction_source,
            content
    ):
        ButtonKt.OutlinedButton(
            onClick=on_click,
            modifier=modifier,
            enabled=enabled,
            shape=shape,
            colors=colors,
            elevation=elevation,
            border=border,
            contentPadding=content_padding,
            interactionSource=interaction_source,
            content=content,
            c=cls.composer,
            changed=1
        )


@Composable
class TextButton(Composable):
    """ M3 text button """

    @classmethod
    def compose(
            cls,
            on_click,
            modifier,
            enabled,
            shape,
            colors,
            elevation,
            border,
            content_padding,
            interaction_source,
            content
    ):
        ButtonKt.TextButton(
            onClick=on_click,
            modifier=modifier,
            enabled=enabled,
            shape=shape,
            colors=colors,
            elevation=elevation,
            border=border,
            contentPadding=content_padding,
            interactionSource=interaction_source,
            content=content,
            c=cls.composer,
            changed=1
        )
