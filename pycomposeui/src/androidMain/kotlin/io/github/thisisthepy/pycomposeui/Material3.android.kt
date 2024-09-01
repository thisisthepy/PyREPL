package io.github.thisisthepy.pycomposeui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.MutableState
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Shape
import androidx.compose.ui.unit.dp
import com.chaquo.python.PyObject


@JvmName("SimpleColumnWidget")
@Composable
fun SimpleColumnWidget(
    modifier: Modifier,
    verticalArrangement: Arrangement.Vertical,
    horizontalAlignment: Alignment.Horizontal,
    content: PyObject
) {
    Column(modifier, verticalArrangement, horizontalAlignment) {
        content.call()
    }
}


@JvmName("SimpleRowWidget")
@Composable
fun SimpleRowWidget(
    modifier: Modifier,
    horizontalArrangement: Arrangement.Horizontal,
    verticalAlignment: Alignment.Vertical,
    content: PyObject
) {
    Row(modifier, horizontalArrangement, verticalAlignment) {
        content.call()
    }
}


@JvmName("SimpleButtonWidget")
@Composable
fun SimpleButtonWidget(
    onClick: PyObject,
    enabled: Boolean,
    cornerRadius: Float,
    color: Long,
    content: PyObject
) {
    Button({ onClick.call() }, Modifier, enabled, RoundedCornerShape(cornerRadius.dp), ButtonColors(
        containerColor = Color(color),
        contentColor = Color.Unspecified,
        disabledContainerColor = Color(color),
        disabledContentColor = Color.Unspecified
    )) {
        content.call()
    }
}


@JvmName("SimpleCardWidget")
@Composable
fun SimpleCardWidget(
    modifier: Modifier,
    cornerRadius: Float,
    color: Long,
    content: PyObject
) {
    Card(modifier, RoundedCornerShape(cornerRadius.dp), CardColors(
        containerColor = Color(color),
        contentColor = Color.Unspecified,
        disabledContainerColor = Color(color),
        disabledContentColor = Color.Unspecified
    )){
        content.call()
    }
}


@JvmName("SimpleTextField")
@Composable
fun SimpleTextField(
    textState: MutableState<String>,
    padding: Int
) {
    TextField(
        value = textState.value, // 외부에서 받은 텍스트 상태 사용
        onValueChange = { textState.value = it }, // 텍스트 값이 변경될 때 호출되는 콜백
        placeholder = null, // placeholder 생략
        modifier = Modifier
            .fillMaxWidth()
            .padding(padding.dp),
        singleLine = false
    )
}
