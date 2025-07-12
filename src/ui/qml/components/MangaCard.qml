import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls.Material 2.15

Rectangle {
    id: root
    
    property alias title: titleLabel.text
    property alias chapterCount: countLabel.text
    property bool selected: false
    property string firstLetter: title.charAt(0).toUpperCase()
    
    signal clicked()
    
    height: 70
    radius: 8
    color: mouseArea.containsPress ? Material.color(Material.Grey, Material.Shade800) : 
           (selected || mouseArea.containsMouse) ? Material.color(Material.Grey, Material.Shade900) : 
           "transparent"
    
    border.width: selected ? 2 : 0
    border.color: Material.accent
    
    Behavior on color { ColorAnimation { duration: 150 } }
    
    RowLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 12
        
        // Avatar
        Rectangle {
            width: 46
            height: 46
            radius: 8
            color: Material.accent
            
            Label {
                anchors.centerIn: parent
                text: root.firstLetter
                font.pixelSize: 20
                font.bold: true
                color: "white"
            }
        }
        
        // Text content
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 2
            
            Label {
                id: titleLabel
                Layout.fillWidth: true
                font.pixelSize: 14
                font.bold: true
                elide: Text.ElideRight
            }
            
            Label {
                id: countLabel
                font.pixelSize: 12
                opacity: 0.7
            }
        }
        
        // Selection indicator
        Rectangle {
            width: 4
            height: parent.height - 24
            radius: 2
            color: Material.accent
            visible: selected
        }
    }
    
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        onClicked: root.clicked()
    }
}