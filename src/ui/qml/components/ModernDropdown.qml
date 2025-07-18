import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

/**
 * ModernDropdown - Componente de dropdown moderno
 * Baseado no FRONTEND_MAP_MODERN.md
 */
Rectangle {
    id: root
    
    // ===== PUBLIC PROPERTIES =====
    property string label: ""
    property string placeholder: "Selecione uma opção"
    property var model: []
    property string textRole: "text"
    property string valueRole: "value"
    property int currentIndex: -1
    property var currentValue: null
    property string currentText: ""
    property bool disabled: false
    property string size: "md"
    property string variant: "outlined"
    property string leftIcon: ""
    property bool searchable: false
    property string searchPlaceholder: "Buscar..."
    property bool clearable: false
    
    // ===== DESIGN SYSTEM =====
    DesignSystem { id: ds }
    
    // ===== COMPUTED PROPERTIES =====
    readonly property int dropdownHeight: {
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
    
    readonly property color borderColor: {
        if (disabled) return ds.border
        if (dropdown.activeFocus || dropdownPopup.visible) return ds.accent
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
    height: label !== "" ? dropdownHeight + ds.space6 : dropdownHeight
    radius: ds.radius_md
    color: backgroundColor
    border.color: borderColor
    border.width: 1
    
    // ===== INTERNAL PROPERTIES =====
    property string searchText: ""
    property var filteredModel: getFilteredModel()
    
    function getFilteredModel() {
        if (!searchable || searchText === "") {
            return model
        }
        
        var filtered = []
        for (var i = 0; i < model.length; i++) {
            var item = model[i]
            var text = typeof item === "string" ? item : item[textRole] || ""
            if (text.toLowerCase().includes(searchText.toLowerCase())) {
                filtered.push(item)
            }
        }
        return filtered
    }
    
    // ===== CONTENT LAYOUT =====
    ColumnLayout {
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
            color: ds.textPrimary
            visible: label !== ""
        }
        
        // Dropdown container
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
                    Layout.leftMargin: ds.space3
                    text: leftIcon
                    font.pixelSize: ds.iconMd
                    color: ds.textSecondary
                    visible: leftIcon !== ""
                }
                
                // Selected text
                Text {
                    Layout.fillWidth: true
                    Layout.leftMargin: leftIcon !== "" ? 0 : ds.space3
                    text: currentText !== "" ? currentText : placeholder
                    font.pixelSize: fontSize
                    color: currentText !== "" ? (disabled ? ds.textSecondary : ds.textPrimary) : ds.textSecondary
                    elide: Text.ElideRight
                    verticalAlignment: Text.AlignVCenter
                }
                
                // Clear button
                Rectangle {
                    Layout.preferredWidth: ds.iconMd
                    Layout.preferredHeight: ds.iconMd
                    radius: ds.iconMd / 2
                    color: clearMouseArea.containsMouse ? ds.hover : "transparent"
                    visible: clearable && currentIndex >= 0 && !disabled
                    
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
                            currentIndex = -1
                            currentValue = null
                            currentText = ""
                            selectionChanged()
                        }
                    }
                }
                
                // Dropdown arrow
                Text {
                    Layout.rightMargin: ds.space3
                    text: dropdownPopup.visible ? "▲" : "▼"
                    font.pixelSize: ds.text_sm
                    color: ds.textSecondary
                    
                    Behavior on rotation {
                        NumberAnimation {
                            duration: ds.animationFast
                            easing.type: ds.easingOut
                        }
                    }
                }
            }
        }
    }
    
    // ===== INTERACTION =====
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        enabled: !disabled
        cursorShape: Qt.PointingHandCursor
        
        onClicked: {
            dropdown.forceActiveFocus()
            dropdownPopup.visible = !dropdownPopup.visible
        }
    }
    
    // ===== FOCUS ITEM =====
    FocusScope {
        id: dropdown
        anchors.fill: parent
        
        Keys.onSpacePressed: {
            dropdownPopup.visible = !dropdownPopup.visible
        }
        
        Keys.onEnterPressed: {
            dropdownPopup.visible = !dropdownPopup.visible
        }
        
        Keys.onEscapePressed: {
            dropdownPopup.visible = false
        }
        
        Keys.onUpPressed: {
            if (currentIndex > 0) {
                setCurrentIndex(currentIndex - 1)
            }
        }
        
        Keys.onDownPressed: {
            if (currentIndex < model.length - 1) {
                setCurrentIndex(currentIndex + 1)
            }
        }
    }
    
    // ===== POPUP =====
    Rectangle {
        id: dropdownPopup
        visible: false
        width: root.width
        height: Math.min(300, contentColumn.implicitHeight)
        anchors.top: root.bottom
        anchors.topMargin: ds.space1
        anchors.left: root.left
        
        color: ds.bgCard
        border.color: ds.border
        border.width: 1
        radius: ds.radius_md
        z: ds.zIndexDropdown
        
        ColumnLayout {
            id: contentColumn
            anchors.fill: parent
            anchors.margins: ds.space2
            spacing: ds.space1
            
            // Search input
            ModernInput {
                Layout.fillWidth: true
                placeholderText: searchPlaceholder
                size: root.size
                visible: searchable
                
                onInputTextChanged: {
                    searchText = text
                    filteredModel = getFilteredModel()
                }
            }
            
            // Options list
            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                
                ListView {
                    id: optionsList
                    model: filteredModel
                    delegate: optionDelegate
                    
                    highlight: Rectangle {
                        color: ds.accent
                        radius: ds.radius_sm
                    }
                    highlightFollowsCurrentItem: true
                    
                    Component.onCompleted: {
                        if (currentIndex >= 0 && currentIndex < count) {
                            currentIndex = root.currentIndex
                        }
                    }
                }
            }
        }
    }
    
    // ===== OPTION DELEGATE =====
    Component {
        id: optionDelegate
        
        Rectangle {
            width: optionsList.width
            height: ds.inputHeightSm
            color: optionMouseArea.containsMouse ? ds.hover : "transparent"
            radius: ds.radius_sm
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: ds.space2
                spacing: ds.space2
                
                Text {
                    Layout.fillWidth: true
                    text: typeof modelData === "string" ? modelData : modelData[textRole] || ""
                    font.pixelSize: fontSize
                    color: ds.textPrimary
                    elide: Text.ElideRight
                }
                
                // Selected indicator
                Text {
                    text: "✓"
                    font.pixelSize: ds.text_sm
                    color: ds.accent
                    visible: index === root.currentIndex
                }
            }
            
            MouseArea {
                id: optionMouseArea
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                
                onClicked: {
                    setCurrentIndex(index)
                    dropdownPopup.visible = false
                }
            }
        }
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
    
    // ===== METHODS =====
    function setCurrentIndex(index) {
        if (index >= 0 && index < model.length) {
            currentIndex = index
            var item = model[index]
            currentValue = typeof item === "string" ? item : item[valueRole]
            currentText = typeof item === "string" ? item : item[textRole] || ""
            selectionChanged()
        }
    }
    
    function getCurrentItem() {
        if (currentIndex >= 0 && currentIndex < model.length) {
            return model[currentIndex]
        }
        return null
    }
    
    // ===== SIGNALS =====
    signal selectionChanged()
    
    // ===== ACCESSIBILITY =====
    Accessible.role: Accessible.ComboBox
    Accessible.name: label !== "" ? label : placeholder
    Accessible.description: currentText
    
    // ===== CLOSE POPUP ON OUTSIDE CLICK =====
    MouseArea {
        anchors.fill: parent
        enabled: dropdownPopup.visible
        onClicked: {
            if (!root.contains(Qt.point(mouse.x, mouse.y))) {
                dropdownPopup.visible = false
            }
        }
        z: ds.zIndexDropdown - 1
    }
}