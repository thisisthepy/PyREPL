package ui.theme

import androidx.compose.material3.LocalTextStyle
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Typography
import androidx.compose.runtime.Composable
import androidx.compose.runtime.MutableState
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextLayoutResult
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextDecoration
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.TextUnit
import androidx.compose.ui.unit.sp
import org.jetbrains.compose.resources.Font
import ui.style.AutoSizeTextWithResizer

import pyrepl.app.generated.resources.Res
import pyrepl.app.generated.resources.SUITE_Variable


val SuiteFontFamily: FontFamily
    @Composable get() = FontFamily(
        Font(Res.font.SUITE_Variable, weight = FontWeight.Light),
        Font(Res.font.SUITE_Variable, weight = FontWeight.Normal),
        Font(Res.font.SUITE_Variable, weight = FontWeight.Medium),
        Font(Res.font.SUITE_Variable, weight = FontWeight.SemiBold),
        Font(Res.font.SUITE_Variable, weight = FontWeight.Bold)
    )


val typography
    @Composable get() = Typography(
        displayLarge = TextStyle(
            fontFamily = SuiteFontFamily,
            fontWeight = FontWeight.Bold,
            fontSize = 32.sp
        ),
        displayMedium = TextStyle(
            fontFamily = SuiteFontFamily,
            fontWeight = FontWeight.Bold,
            fontSize = 28.sp
        ),
        displaySmall = TextStyle(
            fontFamily = SuiteFontFamily,
            fontWeight = FontWeight.Bold,
            fontSize = 24.sp
        ),
        headlineLarge = TextStyle(
            fontFamily = SuiteFontFamily,
            fontWeight = FontWeight.SemiBold,
            fontSize = 22.sp
        ),
        headlineMedium = TextStyle(
            fontFamily = SuiteFontFamily,
            fontWeight = FontWeight.SemiBold,
            fontSize = 20.sp
        ),
        headlineSmall = TextStyle(
            fontFamily = SuiteFontFamily,
            fontWeight = FontWeight.SemiBold,
            fontSize = 18.sp
        ),
        titleLarge = TextStyle(
            fontFamily = SuiteFontFamily,
            fontWeight = FontWeight.SemiBold,
            fontSize = 20.sp
        ),
        titleMedium = TextStyle(
            fontFamily = SuiteFontFamily,
            fontWeight = FontWeight.SemiBold,
            fontSize = 18.sp
        ),
        titleSmall = TextStyle(
            fontFamily = SuiteFontFamily,
            fontWeight = FontWeight.SemiBold,
            fontSize = 16.sp
        ),
        bodyLarge = TextStyle(
            fontFamily = SuiteFontFamily,
            fontWeight = FontWeight.Medium,
            fontSize = 18.sp
        ),
        bodyMedium = TextStyle(
            fontFamily = SuiteFontFamily,
            fontWeight = FontWeight.Normal,
            fontSize = 16.sp
        ),
        bodySmall = TextStyle(
            fontFamily = SuiteFontFamily,
            fontWeight = FontWeight.Normal,
            fontSize = 14.sp
        ),
        labelLarge = TextStyle(
            fontFamily = SuiteFontFamily,
            fontWeight = FontWeight.SemiBold,
            fontSize = 14.sp
        ),
        labelMedium = TextStyle(
            fontFamily = SuiteFontFamily,
            fontWeight = FontWeight.SemiBold,
            fontSize = 12.sp
        ),
        labelSmall = TextStyle(
            fontFamily = SuiteFontFamily,
            fontWeight = FontWeight.SemiBold,
            fontSize = 10.sp
        )
    )


/*
@Composable
fun HeadText(
    text: String,
    modifier: Modifier = Modifier,
    color: Color = MaterialTheme.colorScheme.onPrimary,
    fontSize: TextUnit = headTextFontSize,
    fontStyle: FontStyle? = null,
    fontWeight: FontWeight = FontWeight.SemiBold,
    letterSpacing: TextUnit = TextUnit.Unspecified,
    textDecoration: TextDecoration? = null,
    textAlign: TextAlign? = null,
    lineHeight: TextUnit = TextUnit.Unspecified,
    overflow: TextOverflow = TextOverflow.Ellipsis,
    softWrap: Boolean = true,
    maxLines: Int = 1,
    minLines: Int = 1,
    onTextLayout: (TextLayoutResult) -> Unit = {},
    style: TextStyle = LocalTextStyle.current
) {
    Text(
        text, modifier, color, fontSize, fontStyle, fontWeight, letterSpacing,
        textDecoration, textAlign, lineHeight, overflow, softWrap,
        maxLines, minLines, onTextLayout, style
    )
}


@Composable
fun BodyText(
    text: String,
    modifier: Modifier = Modifier,
    color: Color = MaterialTheme.colorScheme.onBackground,
    fontSize: TextUnit = bodyTextFontSize,
    fontStyle: FontStyle? = null,
    fontWeight: FontWeight = FontWeight.SemiBold,
    letterSpacing: TextUnit = TextUnit.Unspecified,
    textDecoration: TextDecoration? = null,
    textAlign: TextAlign? = null,
    lineHeight: TextUnit = TextUnit.Unspecified,
    overflow: TextOverflow = TextOverflow.Ellipsis,
    softWrap: Boolean = true,
    maxLines: Int = 1,
    minLines: Int = 1,
    onTextLayout: (TextLayoutResult) -> Unit = {},
    style: TextStyle = LocalTextStyle.current
) {
    Text(
        text, modifier, color, fontSize, fontStyle, fontWeight, letterSpacing,
        textDecoration, textAlign, lineHeight, overflow, softWrap,
        maxLines, minLines, onTextLayout, style
    )
}


@Composable
fun BodyText(
    text: String,
    modifier: Modifier = Modifier,
    color: Color = MaterialTheme.colorScheme.onBackground,
    fontSize: TextUnit = bodyTextFontSize,
    fontStyle: FontStyle? = null,
    fontWeight: FontWeight = FontWeight.SemiBold,
    letterSpacing: TextUnit = TextUnit.Unspecified,
    textDecoration: TextDecoration? = null,
    textAlign: TextAlign? = null,
    lineHeight: TextUnit = TextUnit.Unspecified,
    overflow: TextOverflow = TextOverflow.Clip,
    softWrap: Boolean = true,
    maxLines: Int = 1,
    minLines: Int = 1,
    onTextLayout: (TextLayoutResult) -> Unit = {},
    style: TextStyle = LocalTextStyle.current,
    resizer: MutableState<Float> = remember { mutableStateOf(1f) }
) {
    AutoSizeTextWithResizer(
        text, modifier, color, fontSize, fontStyle, fontWeight, suiteFontFamily, letterSpacing,
        textDecoration, textAlign, lineHeight, overflow, softWrap,
        maxLines, minLines, onTextLayout, style, resizer
    )
}


@Composable
fun FootText(
    text: String,
    modifier: Modifier = Modifier,
    color: Color = MaterialTheme.colorScheme.onBackground,
    fontSize: TextUnit = footTextFontSize,
    fontStyle: FontStyle? = null,
    fontWeight: FontWeight = FontWeight.SemiBold,
    letterSpacing: TextUnit = TextUnit.Unspecified,
    textDecoration: TextDecoration? = null,
    textAlign: TextAlign? = null,
    lineHeight: TextUnit = TextUnit.Unspecified,
    overflow: TextOverflow = TextOverflow.Ellipsis,
    softWrap: Boolean = true,
    maxLines: Int = 1,
    minLines: Int = 1,
    onTextLayout: (TextLayoutResult) -> Unit = {},
    style: TextStyle = LocalTextStyle.current
) {
    Text(
        text, modifier, color, fontSize, fontStyle, fontWeight, letterSpacing,
        textDecoration, textAlign, lineHeight, overflow, softWrap,
        maxLines, minLines, onTextLayout, style
    )
}


@Composable
fun StatusText(
    text: String,
    modifier: Modifier = Modifier,
    color: Color = MaterialTheme.colorScheme.onPrimary,
    fontSize: TextUnit = statusTextFontSize,
    fontStyle: FontStyle? = null,
    fontWeight: FontWeight = FontWeight.Normal,
    letterSpacing: TextUnit = TextUnit.Unspecified,
    textDecoration: TextDecoration? = null,
    textAlign: TextAlign? = null,
    lineHeight: TextUnit = TextUnit.Unspecified,
    overflow: TextOverflow = TextOverflow.Ellipsis,
    softWrap: Boolean = true,
    maxLines: Int = 1,
    minLines: Int = 1,
    onTextLayout: (TextLayoutResult) -> Unit = {},
    style: TextStyle = LocalTextStyle.current
) {
    Text(
        text, modifier, color, fontSize, fontStyle, fontWeight, letterSpacing,
        textDecoration, textAlign, lineHeight, overflow, softWrap,
        maxLines, minLines, onTextLayout, style
    )
}


@Composable
fun StatusText(
    text: String,
    modifier: Modifier = Modifier,
    color: Color = MaterialTheme.colorScheme.onPrimary,
    fontSize: TextUnit = statusTextFontSize,
    fontStyle: FontStyle? = null,
    fontWeight: FontWeight = FontWeight.Normal,
    letterSpacing: TextUnit = TextUnit.Unspecified,
    textDecoration: TextDecoration? = null,
    textAlign: TextAlign? = null,
    lineHeight: TextUnit = TextUnit.Unspecified,
    overflow: TextOverflow = TextOverflow.Clip,
    softWrap: Boolean = true,
    maxLines: Int = 1,
    minLines: Int = 1,
    onTextLayout: (TextLayoutResult) -> Unit = {},
    style: TextStyle = LocalTextStyle.current,
    resizer: MutableState<Float> = remember { mutableStateOf(1f) }
) {
    AutoSizeTextWithResizer(
        text, modifier, color, fontSize, fontStyle, fontWeight, suiteFontFamily, letterSpacing,
        textDecoration, textAlign, lineHeight, overflow, softWrap,
        maxLines, minLines, onTextLayout, style, resizer
    )
}
*/