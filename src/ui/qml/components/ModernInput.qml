import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

/**
 * ModernInput - Componente de input moderno
 * Baseado no FRONTEND_MAP_MODERN.md
 */
Rectangle {
    id: root
    
    // ===== PUBLIC PROPERTIES =====
    property string text: ""
    property string placeholderText: ""
    property string label: ""
    property string helperText: ""
    property string errorText: ""
    property bool hasError: errorText !== ""
    property bool disabled: false
    property bool readOnly: false
    property string size: "md"          // sm, md, lg
    property string variant: "outlined"  // outlined, filled
    property string inputType: "text"    // text, password, email, number
    property string leftIcon: ""
    property string rightIcon: ""
    property bool multiline: false
    property int maxLength: 0
    property bool clearable: false
    property bool showCharacterCount: false
    
    // ===== DESIGN SYSTEM =====
    DesignSystem { id: ds }
    
    // ===== COMPUTED PROPERTIES =====
    readonly property int inputHeight: {
        switch(size) {
            case "sm": return ds.inputHeightSm
            case "lg": return ds.inputHeightLg
            case "md":
            default: return ds.inputHeightMd
        }
    }
    
    readonly property int fontSize: {
        switch(size) {
            case "sm": return ds.text_sm
            case "lg": return ds.text_lg
            case "md":
            default: return ds.text_base
        }
    }
    
    readonly property int paddingHorizontal: {
        switch(size) {
            case "sm": return ds.space3
            case "lg": return ds.space4
            case "md":
            default: return ds.space3
        }
    }
    
    readonly property color borderColor: {
        if (hasError) return ds.danger
        if (disabled) return ds.border
        if (getCurrentField().activeFocus) return ds.accent
        if (mouseArea.containsMouse) return ds.textSecondary
        return ds.border
    }
    
    readonly property color backgroundColor: {
        if (disabled) return ds.bgSurface
        if (variant === "filled") return ds.bgSurface
        return ds.bgCard
    }
    
    // ===== LAYOUT PROPERTIES =====
    width: 200
    height: multiline ? Math.max(inputHeight * 2, contentColumn.implicitHeight) : 
                       label !== "" ? inputHeight + ds.space6 : inputHeight
    radius: ds.radius_md
    color: backgroundColor
    border.color: borderColor
    border.width: 1
    
    // ===== CONTENT LAYOUT =====
    ColumnLayout {
        id: contentColumn
        anchors.fill: parent
        anchors.margins: 0
        spacing: ds.space1
        
        // Label
        Text {
            Layout.fillWidth: true
            Layout.leftMargin: ds.space1
            text: label
            font.pixelSize: ds.text_sm
            font.weight: ds.fontMedium
            color: hasError ? ds.danger : ds.textPrimary
            visible: label !== ""
        }
        
        // Input container
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "transparent"
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 0
                spacing: ds.space2
                
                // Left icon
                Text {
                    Layout.leftMargin: paddingHorizontal
                    text: leftIcon
                    font.pixelSize: ds.iconMd
                    color: ds.textSecondary
                    visible: leftIcon !== ""
                }
                
                // Text input
                Item {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    
                    // Use TextField for single-line inputs (including password)
                    TextField {
                        id: textField
                        anchors.fill: parent
                        anchors.topMargin: ds.space2
                        anchors.bottomMargin: ds.space2
                        visible: !multiline
                        
                        text: root.text
                        placeholderText: root.placeholderText
                        font.pixelSize: fontSize
                        color: disabled ? ds.textSecondary : ds.textPrimary
                        selectedTextColor: ds.textPrimary
                        selectionColor: ds.accent
                        placeholderTextColor: ds.textSecondary
                        readOnly: root.readOnly || disabled
                        enabled: !disabled
                        
                        // Password handling
                        echoMode: inputType === "password" ? TextInput.Password : TextInput.Normal
                        
                        background: Rectangle {
                            color: "transparent"
                        }
                        
                        // Input validation
                        onTextChanged: {
                            let newText = text
                            
                            // Number validation
                            if (inputType === "number") {
                                newText = text.replace(/[^0-9]/g, "")
                            }
                            
                            // Length validation
                            if (maxLength > 0 && newText.length > maxLength) {
                                newText = newText.substring(0, maxLength)
                            }
                            
                            if (newText !== text) {
                                text = newText
                            }
                            root.text = newText
                        }
                    }
                    
                    // Use ScrollView + TextArea for multiline inputs
                    ScrollView {
                        anchors.fill: parent
                        anchors.topMargin: multiline ? ds.space2 : 0
                        anchors.bottomMargin: multiline ? ds.space2 : 0
                        visible: multiline
                        
                        TextArea {
                            id: textAreaField
                            text: root.text
                            placeholderText: root.placeholderText
                            font.pixelSize: fontSize
                            color: disabled ? ds.textSecondary : ds.textPrimary
                            selectedTextColor: ds.textPrimary
                            selectionColor: ds.accent
                            placeholderTextColor: ds.textSecondary
                            readOnly: root.readOnly || disabled
                            enabled: !disabled
                            wrapMode: TextArea.Wrap
                            
                            background: Rectangle {
                                color: "transparent"
                            }
                            
                            // Input validation
                            onTextChanged: {
                                let newText = text
                                
                                // Length validation
                                if (maxLength > 0 && newText.length > maxLength) {
                                    newText = newText.substring(0, maxLength)
                                }
                                
                                if (newText !== text) {
                                    text = newText
                                }
                                root.text = newText
                            }
                        }
                    }
                }
                
                // Clear button
                Rectangle {
                    Layout.preferredWidth: ds.iconMd
                    Layout.preferredHeight: ds.iconMd
                    radius: ds.iconMd / 2
                    color: clearMouseArea.containsMouse ? ds.hover : "transparent"
                    visible: clearable && text !== "" && !disabled
                    
                    Text {
                        anchors.centerIn: parent
                        text: "×"
                        font.pixelSize: ds.iconMd
                        color: ds.textSecondary
                    }
                    
                    MouseArea {
                        id: clearMouseArea
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        
                        onClicked: {
                            root.text = ""
                            getCurrentField().text = ""
                            getCurrentField().forceActiveFocus()
                        }
                    }
                }
                
                // Right icon
                Text {
                    Layout.rightMargin: paddingHorizontal
                    text: rightIcon
                    font.pixelSize: ds.iconMd
                    color: ds.textSecondary
                    visible: rightIcon !== ""
                }
            }
        }
    }
    
    // Helper/Error text
    Text {
        anchors.top: parent.bottom
        anchors.topMargin: ds.space1
        anchors.left: parent.left
        anchors.leftMargin: ds.space1
        anchors.right: showCharacterCount ? characterCount.left : parent.right
        anchors.rightMargin: showCharacterCount ? ds.space2 : ds.space1
        
        text: hasError ? errorText : helperText
        font.pixelSize: ds.text_xs
        color: hasError ? ds.danger : ds.textSecondary
        visible: text !== ""
        wrapMode: Text.WordWrap
    }
    
    // Character count
    Text {
        id: characterCount
        anchors.top: parent.bottom
        anchors.topMargin: ds.space1
        anchors.right: parent.right
        anchors.rightMargin: ds.space1
        
        text: maxLength > 0 ? root.text.length + "/" + maxLength : root.text.length
        font.pixelSize: ds.text_xs
        color: (maxLength > 0 && root.text.length > maxLength * 0.8) ? ds.warning : ds.textSecondary
        visible: showCharacterCount
    }
    
    // ===== ANIMATIONS =====
    Behavior on border.color {
        ColorAnimation {
            duration: ds.animationFast
            easing.type: ds.easingOut
        }
    }
    
    Behavior on color {
        ColorAnimation {
            duration: ds.animationFast
            easing.type: ds.easingOut
        }
    }
    
    // ===== INTERACTION =====
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        acceptedButtons: Qt.NoButton
        
        onPressed: {
            mouse.accepted = false
            if (!disabled) {
                getCurrentField().forceActiveFocus()
            }
        }
    }
    
    // ===== SIGNALS =====
    signal inputTextChanged(string text)
    signal editingFinished()
    signal accepted()
    
    // Connect internal signals for TextField
    Connections {
        target: textField
        function onTextChanged() { root.inputTextChanged(textField.text) }
        function onEditingFinished() { root.editingFinished() }
        function onAccepted() { root.accepted() }
    }
    
    // Connect internal signals for TextArea
    Connections {
        target: textAreaField
        function onTextChanged() { root.inputTextChanged(textAreaField.text) }
        function onEditingFinished() { root.editingFinished() }
    }
    
    // ===== ACCESSIBILITY =====
    Accessible.role: Accessible.EditableText
    Accessible.name: label !== "" ? label : placeholderText
    Accessible.description: helperText
    
    // ===== HELPER METHODS =====
    function getCurrentField() {
        return multiline ? textAreaField : textField
    }
    
    // ===== PUBLIC METHODS =====
    function forceActiveFocus() {
        getCurrentField().forceActiveFocus()
    }
    
    function selectAll() {
        getCurrentField().selectAll()
    }
    
    function clear() {
        text = ""
        getCurrentField().text = ""
    }
}