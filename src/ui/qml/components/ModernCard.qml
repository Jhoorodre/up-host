import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Qt5Compat.GraphicalEffects

/**
 * ModernCard - Componente de card moderno com hover animations
 * Baseado no FRONTEND_MAP_MODERN.md
 */
Rectangle {
    id: root
    
    // ===== PUBLIC PROPERTIES =====
    property string title: ""
    property string subtitle: ""
    property string coverUrl: ""
    property string status: ""
    property int chapterCount: 0
    property real progress: 0.0  // 0.0 to 1.0
    property bool hovered: false
    property bool selected: false
    property bool hasActions: true
    property var actions: []  // Array de ações: [{icon: "📤", text: "Upload", action: function(){}}, ...]
    
    // ===== DESIGN SYSTEM =====
    DesignSystem { id: ds }
    
    // ===== LAYOUT PROPERTIES =====
    width: ds.cardMinWidth
    height: ds.cardHeight
    radius: ds.radius_lg
    color: selected ? ds.hover : ds.bgCard
    border.color: selected ? ds.accent : "transparent"
    border.width: selected ? 2 : 0
    
    // ===== HOVER ANIMATIONS =====
    transform: Scale {
        origin.x: width / 2
        origin.y: height / 2
        xScale: hovered ? 1.02 : 1.0
        yScale: hovered ? 1.02 : 1.0
        
        Behavior on xScale {
            NumberAnimation { 
                duration: ds.animationMedium
                easing.type: ds.easingOut
            }
        }
        
        Behavior on yScale {
            NumberAnimation { 
                duration: ds.animationMedium
                easing.type: ds.easingOut
            }
        }
    }
    
    // ===== DROP SHADOW =====
    layer.enabled: true
    layer.effect: DropShadow {
        horizontalOffset: 0
        verticalOffset: hovered ? 8 : 4
        radius: hovered ? 16 : 12
        samples: 25
        color: "#40000000"
        transparentBorder: true
        
        Behavior on verticalOffset {
            NumberAnimation { 
                duration: ds.animationMedium
                easing.type: ds.easingOut
            }
        }
        
        Behavior on radius {
            NumberAnimation { 
                duration: ds.animationMedium
                easing.type: ds.easingOut
            }
        }
    }
    
    // ===== CONTENT LAYOUT =====
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 0
        spacing: 0
        
        // ===== COVER IMAGE AREA =====
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 240
            radius: ds.radius_lg
            color: ds.bgSurface
            clip: true
            
            // Clip only top corners
            Rectangle {
                anchors.fill: parent
                anchors.bottomMargin: ds.radius_lg
                color: parent.color
            }
            
            Rectangle {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                height: ds.radius_lg
                color: parent.color
            }
            
            // Cover image
            Image {
                id: coverImage
                anchors.fill: parent
                source: coverUrl || ""
                fillMode: Image.PreserveAspectCrop
                visible: coverUrl !== ""
                smooth: true
                cache: true
                asynchronous: true
                
                onStatusChanged: {
                    if (status === Image.Error) {
                        fallbackCover.visible = true
                    }
                }
            }
            
            // Fallback cover (generated)
            Rectangle {
                id: fallbackCover
                anchors.fill: parent
                visible: coverUrl === "" || coverImage.status === Image.Error
                
                gradient: Gradient {
                    GradientStop { position: 0.0; color: ds.accent }
                    GradientStop { position: 1.0; color: ds.accentHover }
                }
                
                Text {
                    anchors.centerIn: parent
                    text: title !== "" ? title.charAt(0).toUpperCase() : "?"
                    font.pixelSize: ds.text_4xl
                    font.weight: ds.fontBold
                    color: ds.textPrimary
                }
            }
            
            // Loading indicator
            Rectangle {
                anchors.fill: parent
                color: ds.bgPrimary
                opacity: 0.8
                visible: coverImage.status === Image.Loading
                
                Rectangle {
                    anchors.centerIn: parent
                    width: ds.iconLg
                    height: ds.iconLg
                    radius: ds.iconLg / 2
                    color: ds.accent
                    
                    SequentialAnimation on rotation {
                        running: parent.visible
                        loops: Animation.Infinite
                        NumberAnimation { from: 0; to: 360; duration: 1000 }
                    }
                }
            }
            
            // Status badge
            Rectangle {
                anchors.top: parent.top
                anchors.right: parent.right
                anchors.margins: ds.space3
                width: ds.space3
                height: ds.space3
                radius: ds.space3 / 2
                color: {
                    switch(status.toLowerCase()) {
                        case "completed": 
                        case "completo": return ds.success
                        case "ongoing": 
                        case "em andamento": return ds.accent
                        case "paused": 
                        case "pausado": return ds.warning
                        case "cancelled": 
                        case "cancelado": return ds.danger
                        default: return ds.textSecondary
                    }
                }
                visible: status !== ""
            }
        }
        
        // ===== CONTENT INFO =====
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "transparent"
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: ds.space4
                spacing: ds.space2
                
                // Title
                Text {
                    Layout.fillWidth: true
                    text: title
                    font.pixelSize: ds.text_lg
                    font.weight: ds.fontMedium
                    color: ds.textPrimary
                    elide: Text.ElideRight
                    maximumLineCount: 2
                    wrapMode: Text.WordWrap
                }
                
                // Subtitle/Status info
                Text {
                    Layout.fillWidth: true
                    text: chapterCount > 0 ? chapterCount + " caps • " + status : status
                    font.pixelSize: ds.text_sm
                    color: ds.textSecondary
                    elide: Text.ElideRight
                }
                
                // Progress bar
                Rectangle {
                    Layout.fillWidth: true
                    height: 4
                    radius: 2
                    color: ds.bgSurface
                    visible: progress > 0
                    
                    Rectangle {
                        width: parent.width * progress
                        height: parent.height
                        radius: parent.radius
                        color: ds.accent
                        
                        Behavior on width {
                            NumberAnimation { 
                                duration: ds.animationMedium
                                easing.type: ds.easingOut
                            }
                        }
                    }
                }
                
                // Progress text
                Text {
                    Layout.fillWidth: true
                    text: progress > 0 ? Math.round(progress * 100) + "%" : ""
                    font.pixelSize: ds.text_xs
                    color: ds.textSecondary
                    visible: progress > 0
                    horizontalAlignment: Text.AlignRight
                }
                
                Item { Layout.fillHeight: true }
                
                // Actions row
                Row {
                    Layout.fillWidth: true
                    spacing: ds.space2
                    visible: hasActions && actions.length > 0
                    
                    Repeater {
                        model: actions
                        
                        Rectangle {
                            width: ds.space10
                            height: ds.space8
                            radius: ds.radius_sm
                            color: actionMouseArea.containsMouse ? ds.accent : "transparent"
                            border.color: ds.border
                            border.width: 1
                            
                            Text {
                                anchors.centerIn: parent
                                text: modelData.icon || "⚙"
                                font.pixelSize: ds.text_sm
                                color: parent.color === "transparent" ? ds.textSecondary : ds.textPrimary
                            }
                            
                            MouseArea {
                                id: actionMouseArea
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                
                                onClicked: {
                                    if (modelData.action) {
                                        modelData.action()
                                    }
                                }
                            }
                            
                            // Tooltip for action
                            Rectangle {
                                visible: modelData.text && actionMouseArea.containsMouse
                                color: ds.bgCard
                                border.color: ds.border
                                border.width: 1
                                radius: ds.radius_sm
                                width: actionTooltip.implicitWidth + ds.space2 * 2
                                height: actionTooltip.implicitHeight + ds.space1 * 2
                                
                                anchors.bottom: parent.top
                                anchors.bottomMargin: ds.space1
                                anchors.horizontalCenter: parent.horizontalCenter
                                
                                z: ds.zIndexTooltip
                                
                                Text {
                                    id: actionTooltip
                                    text: modelData.text || ""
                                    color: ds.textPrimary
                                    font.pixelSize: ds.text_xs
                                    anchors.centerIn: parent
                                }
                            }
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
        acceptedButtons: Qt.LeftButton | Qt.RightButton
        
        onEntered: root.hovered = true
        onExited: root.hovered = false
        
        onClicked: {
            if (mouse.button === Qt.LeftButton) {
                root.clicked()
            } else if (mouse.button === Qt.RightButton) {
                root.rightClicked()
            }
        }
        
        onDoubleClicked: root.doubleClicked()
    }
    
    // ===== SIGNALS =====
    signal clicked()
    signal rightClicked()
    signal doubleClicked()
    
    // ===== ACCESSIBILITY =====
    Accessible.role: Accessible.Button
    Accessible.name: title
    Accessible.description: subtitle
    
    // ===== FOCUS HANDLING =====
    Keys.onSpacePressed: clicked()
    Keys.onEnterPressed: clicked()
    Keys.onReturnPressed: clicked()
}