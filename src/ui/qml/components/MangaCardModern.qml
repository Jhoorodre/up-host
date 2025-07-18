import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Qt5Compat.GraphicalEffects

/**
 * MangaCardModern - Card de manga para a sidebar com hover animations
 * Baseado no FRONTEND_MAP_MODERN.md
 */
Rectangle {
    id: root
    
    // ===== PUBLIC PROPERTIES =====
    property string title: ""
    property string coverUrl: ""
    property int chapterCount: 0
    property string status: ""
    property bool selected: false
    property bool hovered: false
    property bool isFavorited: false
    
    // ===== DESIGN SYSTEM =====
    DesignSystem { id: ds }
    
    // ===== LAYOUT PROPERTIES =====
    width: parent ? parent.width : ds.sidebarWidth
    height: 120
    radius: ds.radius_lg
    color: selected ? ds.accent : (hovered ? ds.hover : "transparent")
    
    // ===== HOVER ANIMATIONS =====
    transform: Scale {
        origin.x: width / 2
        origin.y: height / 2
        xScale: hovered ? 1.02 : 1.0
        yScale: hovered ? 1.02 : 1.0
        
        Behavior on xScale {
            NumberAnimation { 
                duration: ds.animationFast
                easing.type: ds.easingOut
            }
        }
        
        Behavior on yScale {
            NumberAnimation { 
                duration: ds.animationFast
                easing.type: ds.easingOut
            }
        }
    }
    
    // ===== SUBTLE GLOW EFFECT =====
    Rectangle {
        anchors.fill: parent
        radius: parent.radius
        color: "transparent"
        border.color: selected ? ds.accent : "transparent"
        border.width: selected ? 2 : 0
        opacity: selected ? 0.8 : 0.0
        
        Behavior on opacity {
            NumberAnimation { 
                duration: ds.animationFast
                easing.type: ds.easingOut
            }
        }
    }
    
    // ===== CONTENT LAYOUT =====
    RowLayout {
        anchors.fill: parent
        anchors.margins: ds.space3
        spacing: ds.space3
        
        // ===== COVER IMAGE =====
        Rectangle {
            Layout.preferredWidth: 70
            Layout.preferredHeight: 90
            radius: ds.radius_md
            color: ds.bgSurface
            border.color: ds.border
            border.width: 1
            clip: true
            
            Image {
                id: coverImage
                anchors.fill: parent
                anchors.margins: 1
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
                    font.pixelSize: ds.text_2xl
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
                    width: ds.iconMd
                    height: ds.iconMd
                    radius: ds.iconMd / 2
                    color: ds.accent
                    
                    SequentialAnimation on rotation {
                        running: parent && parent.visible && coverImage.status === Image.Loading
                        loops: Animation.Infinite
                        NumberAnimation { from: 0; to: 360; duration: 1000 }
                    }
                }
            }
            
            // Status badge
            Rectangle {
                anchors.top: parent.top
                anchors.right: parent.right
                anchors.margins: ds.space1
                width: ds.space2
                height: ds.space2
                radius: ds.space1
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
                opacity: 0.9
            }
        }
        
        // ===== CONTENT INFO =====
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: ds.space2
            
            // Title
            Text {
                Layout.fillWidth: true
                text: title
                font.pixelSize: ds.getResponsiveTextSize(ds.text_base, root.width)
                font.weight: ds.fontMedium
                color: selected ? ds.textPrimary : ds.textPrimary
                elide: Text.ElideRight
                maximumLineCount: 2
                wrapMode: Text.WordWrap
                
                Behavior on color {
                    ColorAnimation { 
                        duration: ds.animationFast
                        easing.type: ds.easingOut
                    }
                }
            }
            
            // Chapter count and status
            Text {
                Layout.fillWidth: true
                text: chapterCount > 0 ? chapterCount + " capítulos" : "Sem capítulos"
                font.pixelSize: ds.text_sm
                color: selected ? ds.textPrimary : ds.textSecondary
                elide: Text.ElideRight
                
                Behavior on color {
                    ColorAnimation { 
                        duration: ds.animationFast
                        easing.type: ds.easingOut
                    }
                }
            }
            
            // Status text
            Text {
                Layout.fillWidth: true
                text: status || "Desconhecido"
                font.pixelSize: ds.text_xs
                color: selected ? ds.textPrimary : ds.textSecondary
                elide: Text.ElideRight
                opacity: 0.8
                
                Behavior on color {
                    ColorAnimation { 
                        duration: ds.animationFast
                        easing.type: ds.easingOut
                    }
                }
            }
            
            Item { Layout.fillHeight: true }
            
            // Quick actions (visible on hover)
            RowLayout {
                Layout.fillWidth: true
                spacing: ds.space2
                opacity: hovered ? 1.0 : 0.0
                
                Behavior on opacity {
                    NumberAnimation { 
                        duration: ds.animationFast
                        easing.type: ds.easingOut
                    }
                }
                
                // Upload action
                Rectangle {
                    width: ds.space6
                    height: ds.space6
                    radius: ds.radius_sm
                    color: uploadMouseArea.containsMouse ? ds.accent : ds.bgCard
                    border.color: ds.border
                    border.width: 1
                    
                    Text {
                        anchors.centerIn: parent
                        text: "📤"
                        font.pixelSize: ds.text_xs
                        color: parent.color === ds.bgCard ? ds.textSecondary : ds.textPrimary
                    }
                    
                    MouseArea {
                        id: uploadMouseArea
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        
                        onClicked: {
                            root.uploadClicked()
                        }
                    }
                }
                
                // Edit action
                Rectangle {
                    width: ds.space6
                    height: ds.space6
                    radius: ds.radius_sm
                    color: editMouseArea.containsMouse ? ds.warning : ds.bgCard
                    border.color: ds.border
                    border.width: 1
                    
                    Text {
                        anchors.centerIn: parent
                        text: "✏️"
                        font.pixelSize: ds.text_xs
                        color: parent.color === ds.bgCard ? ds.textSecondary : ds.textPrimary
                    }
                    
                    MouseArea {
                        id: editMouseArea
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        
                        onClicked: {
                            root.editClicked()
                        }
                    }
                }
                
                // Favorite action
                Rectangle {
                    width: ds.space6
                    height: ds.space6
                    radius: ds.radius_sm
                    color: isFavorited ? ds.warning : (favoriteMouseArea.containsMouse ? ds.warning : ds.bgCard)
                    border.color: isFavorited ? ds.warning : ds.border
                    border.width: 1
                    
                    Text {
                        anchors.centerIn: parent
                        text: isFavorited ? "⭐" : "☆"
                        font.pixelSize: ds.text_xs
                        color: isFavorited ? ds.textPrimary : (parent.color === ds.bgCard ? ds.textSecondary : ds.textPrimary)
                    }
                    
                    MouseArea {
                        id: favoriteMouseArea
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        
                        onClicked: {
                            root.favoriteClicked()
                        }
                    }
                }
                
                Item { Layout.fillWidth: true }
            }
        }
        
        // ===== SELECTION INDICATOR =====
        Rectangle {
            width: 4
            height: 4
            radius: 2
            color: chapterCount > 0 ? ds.accent : ds.textSecondary
            opacity: chapterCount > 0 ? 1.0 : 0.3
            Layout.alignment: Qt.AlignVCenter
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
        
        onClicked: function(mouse) {
            if (mouse.button === Qt.LeftButton) {
                root.clicked()
            } else if (mouse.button === Qt.RightButton) {
                root.rightClicked()
            }
        }
        
        onDoubleClicked: root.doubleClicked()
    }
    
    // ===== RIPPLE EFFECT =====
    Rectangle {
        id: ripple
        anchors.fill: parent
        radius: parent.radius
        color: ds.accent
        opacity: 0.0
        
        NumberAnimation on opacity {
            id: rippleAnimation
            duration: ds.animationMedium
            easing.type: ds.easingOut
        }
        
        function trigger() {
            opacity = 0.2
            rippleAnimation.from = 0.2
            rippleAnimation.to = 0.0
            rippleAnimation.start()
        }
    }
    
    // ===== SIGNALS =====
    signal clicked()
    signal rightClicked()
    signal doubleClicked()
    signal uploadClicked()
    signal editClicked()
    signal favoriteClicked()
    
    // ===== ACCESSIBILITY =====
    Accessible.role: Accessible.Button
    Accessible.name: title
    Accessible.description: chapterCount + " capítulos, " + status
    
    // ===== FOCUS HANDLING =====
    Keys.onSpacePressed: {
        ripple.trigger()
        clicked()
    }
    
    Keys.onEnterPressed: {
        ripple.trigger()
        clicked()
    }
    
    Keys.onReturnPressed: {
        ripple.trigger()
        clicked()
    }
    
    // ===== ANIMATIONS =====
    Behavior on color {
        ColorAnimation {
            duration: ds.animationFast
            easing.type: ds.easingOut
        }
    }
}