import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

/**
 * ModernButton - Componente base reutilizável para o novo design
 * Baseado no FRONTEND_MAP_MODERN.md com sistema de design minimalista
 */
Rectangle {
    id: root
    
    // ===== PUBLIC PROPERTIES =====
    property string text: ""
    property string variant: "primary" // primary, secondary, ghost, danger, success, warning
    property string size: "md"         // sm, md, lg
    property bool loading: false
    property bool disabled: false
    property string icon: ""           // Emoji ou ícone
    property bool iconOnly: false      // Se true, só mostra o ícone
    property real iconSize: ds.iconMd
    
    // ===== DESIGN SYSTEM =====
    DesignSystem { id: ds }
    
    // ===== RESPONSIVE PROPERTIES =====
    readonly property int minTouchTarget: 44
    
    // ===== COMPUTED PROPERTIES =====
    readonly property color bgColor: {
        if (disabled) return ds.disabled
        
        switch(variant) {
            case "primary": return mouseArea.pressed ? ds.getPressedColor(ds.accent) : 
                                  mouseArea.containsMouse ? ds.accentHover : ds.accent
            case "secondary": return mouseArea.pressed ? ds.getPressedColor(ds.bgSurface) : 
                                    mouseArea.containsMouse ? ds.hover : ds.bgSurface
            case "ghost": return mouseArea.pressed ? ds.pressed : 
                                mouseArea.containsMouse ? ds.hover : "transparent"
            case "danger": return mouseArea.pressed ? ds.getPressedColor(ds.danger) : 
                                 mouseArea.containsMouse ? Qt.darker(ds.danger, 1.1) : ds.danger
            case "success": return mouseArea.pressed ? ds.getPressedColor(ds.success) : 
                                  mouseArea.containsMouse ? Qt.darker(ds.success, 1.1) : ds.success
            case "warning": return mouseArea.pressed ? ds.getPressedColor(ds.warning) : 
                                  mouseArea.containsMouse ? Qt.darker(ds.warning, 1.1) : ds.warning
            default: return ds.accent
        }
    }
    
    readonly property color textColor: {
        if (disabled) return ds.textSecondary
        
        switch(variant) {
            case "primary": return ds.textPrimary
            case "secondary": return ds.textPrimary
            case "ghost": return mouseArea.containsMouse ? ds.textPrimary : ds.textSecondary
            case "danger": return ds.textPrimary
            case "success": return ds.textPrimary
            case "warning": return ds.bgPrimary
            default: return ds.textPrimary
        }
    }
    
    readonly property color borderColor: {
        if (disabled) return ds.border
        
        switch(variant) {
            case "primary": return "transparent"
            case "secondary": return ds.border
            case "ghost": return mouseArea.containsMouse ? ds.accent : ds.border
            case "danger": return "transparent"
            case "success": return "transparent"
            case "warning": return "transparent"
            default: return "transparent"
        }
    }
    
    readonly property int paddingHorizontal: {
        switch(size) {
            case "sm": return ds.space3
            case "lg": return ds.space5
            case "md":
            default: return ds.space4
        }
    }
    
    readonly property int paddingVertical: {
        switch(size) {
            case "sm": return ds.space2
            case "lg": return ds.space3
            case "md":
            default: return ds.space2
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
    
    readonly property int buttonHeight: {
        switch(size) {
            case "sm": return ds.buttonHeightSm
            case "lg": return ds.buttonHeightLg
            case "md":
            default: return ds.buttonHeightMd
        }
    }
    
    // ===== LAYOUT PROPERTIES =====
    width: Math.max(iconOnly ? buttonHeight : content.implicitWidth + paddingHorizontal * 2, 
                    parent && parent.width <= ds.mobile ? minTouchTarget : 0)
    height: Math.max(buttonHeight, parent && parent.width <= ds.mobile ? minTouchTarget : buttonHeight)
    radius: ds.radius_md
    color: bgColor
    border.color: borderColor
    border.width: variant === "ghost" || variant === "secondary" ? 1 : 0
    
    // ===== TRANSITIONS =====
    Behavior on color {
        ColorAnimation {
            duration: ds.animationFast
            easing.type: ds.easingOut
        }
    }
    
    Behavior on border.color {
        ColorAnimation {
            duration: ds.animationFast
            easing.type: ds.easingOut
        }
    }
    
    // ===== STATES =====
    states: [
        State {
            name: "hovered"
            when: mouseArea.containsMouse && !disabled && !loading
            PropertyChanges { 
                target: root
                scale: 1.02
            }
        },
        State {
            name: "pressed"  
            when: mouseArea.pressed && !disabled && !loading
            PropertyChanges { 
                target: root
                scale: 0.98
            }
        }
    ]
    
    transitions: [
        Transition {
            from: "*"
            to: "*"
            NumberAnimation { 
                properties: "scale"
                duration: ds.animationFast
                easing.type: ds.easingOut
            }
        }
    ]
    
    // ===== CONTENT LAYOUT =====
    Row {
        id: content
        anchors.centerIn: parent
        spacing: ds.space2
        
        // Loading spinner
        Rectangle {
            visible: loading
            width: ds.iconSm
            height: ds.iconSm
            radius: ds.iconSm / 2
            color: "transparent"
            border.color: textColor
            border.width: 2
            anchors.verticalCenter: parent.verticalCenter
            
            Rectangle {
                width: 2
                height: 2
                radius: 1
                color: textColor
                anchors.centerIn: parent
            }
            
            RotationAnimation {
                target: parent
                running: loading
                duration: 1000
                loops: Animation.Infinite
                from: 0
                to: 360
            }
        }
        
        // Icon
        Text {
            visible: icon !== "" && !loading
            text: icon
            font.pixelSize: iconSize
            color: textColor
            anchors.verticalCenter: parent.verticalCenter
        }
        
        // Text
        Text {
            visible: !iconOnly && !loading
            text: root.text
            color: textColor
            font.pixelSize: fontSize
            font.weight: ds.fontMedium
            anchors.verticalCenter: parent.verticalCenter
        }
    }
    
    // ===== INTERACTION =====
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        enabled: !disabled && !loading
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        
        onClicked: root.clicked()
    }
    
    // ===== SIGNALS =====
    signal clicked()
    
    // ===== ACCESSIBILITY =====
    Accessible.role: Accessible.Button
    Accessible.name: text
    Accessible.description: loading ? "Carregando..." : ""
    
    // ===== FOCUS HANDLING =====
    Keys.onSpacePressed: if (!disabled && !loading) clicked()
    Keys.onEnterPressed: if (!disabled && !loading) clicked()
    Keys.onReturnPressed: if (!disabled && !loading) clicked()
    
    // ===== TOOLTIP SUPPORT =====
    property string tooltip: ""
    
    Rectangle {
        id: tooltipRect
        visible: tooltip !== "" && mouseArea.containsMouse
        color: ds.bgCard
        border.color: ds.border
        border.width: 1
        radius: ds.radius_sm
        width: tooltipText.implicitWidth + ds.space3 * 2
        height: tooltipText.implicitHeight + ds.space2 * 2
        
        anchors.bottom: parent.top
        anchors.bottomMargin: ds.space2
        anchors.horizontalCenter: parent.horizontalCenter
        
        z: ds.zIndexTooltip
        
        Text {
            id: tooltipText
            text: tooltip
            color: ds.textPrimary
            font.pixelSize: ds.text_xs
            anchors.centerIn: parent
        }
        
        // Tooltip arrow
        Rectangle {
            width: 8
            height: 8
            color: ds.bgCard
            border.color: ds.border
            border.width: 1
            rotation: 45
            anchors.top: parent.bottom
            anchors.topMargin: -4
            anchors.horizontalCenter: parent.horizontalCenter
        }
    }
}