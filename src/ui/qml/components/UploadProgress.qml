import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls.Material 2.15

Item {
    id: root
    
    property alias value: progressBar.value
    property alias text: statusLabel.text
    property alias subText: subStatusLabel.text
    property bool showPercentage: true
    
    height: 80
    
    ColumnLayout {
        anchors.fill: parent
        spacing: 8
        
        RowLayout {
            Layout.fillWidth: true
            
            Label {
                id: statusLabel
                font.pixelSize: 14
                font.bold: true
            }
            
            Item { Layout.fillWidth: true }
            
            Label {
                text: showPercentage ? Math.round(progressBar.value * 100) + "%" : ""
                font.pixelSize: 14
                font.bold: true
                color: Material.accent
            }
        }
        
        ProgressBar {
            id: progressBar
            Layout.fillWidth: true
            height: 8
            
            background: Rectangle {
                radius: 4
                color: Material.color(Material.Grey, Material.Shade800)
            }
            
            contentItem: Item {
                Rectangle {
                    width: progressBar.visualPosition * parent.width
                    height: parent.height
                    radius: 4
                    color: Material.accent
                    
                    Behavior on width {
                        NumberAnimation { duration: 250; easing.type: Easing.OutCubic }
                    }
                }
            }
        }
        
        Label {
            id: subStatusLabel
            font.pixelSize: 12
            opacity: 0.7
        }
    }
}