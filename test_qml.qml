import QtQuick 2.15
import QtQuick.Controls 2.15
import "src/ui/qml/components"

ApplicationWindow {
    visible: true
    width: 1200
    height: 800
    title: "Test Modern Components"
    
    DesignSystem { id: ds }
    
    color: ds.bgPrimary
    
    TabView {
        anchors.fill: parent
        anchors.margins: 20
        
        Tab {
            title: "Components"
            
            ScrollView {
                anchors.fill: parent
                
                Column {
                    anchors.centerIn: parent
                    spacing: 20
                    width: 400
                    
                    Text {
                        text: "Modern Components Test"
                        font.pixelSize: ds.text_2xl
                        font.weight: ds.fontBold
                        color: ds.textPrimary
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                    
                    ModernButton {
                        text: "Primary Button"
                        variant: "primary"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                    
                    ModernButton {
                        text: "Secondary Button"
                        variant: "secondary"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                    
                    ModernButton {
                        text: "Success Button"
                        variant: "success"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                    
                    ModernInput {
                        placeholderText: "Search..."
                        leftIcon: "🔍"
                        clearable: true
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                    
                    ModernDropdown {
                        model: ["Option 1", "Option 2", "Option 3"]
                        placeholder: "Select an option"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                    
                    ModernCard {
                        width: 300
                        height: 200
                        anchors.horizontalCenter: parent.horizontalCenter
                        
                        Text {
                            anchors.centerIn: parent
                            text: "Modern Card\nwith hover effect"
                            font.pixelSize: ds.text_lg
                            color: ds.textPrimary
                            horizontalAlignment: Text.AlignHCenter
                        }
                    }
                }
            }
        }
        
        Tab {
            title: "Upload Workflow"
            
            ModernUploadWorkflow {
                anchors.fill: parent
                
                onCancelled: {
                    console.log("Upload cancelled")
                }
                
                onUploadStarted: {
                    console.log("Upload started")
                }
                
                onUploadCompleted: {
                    console.log("Upload completed")
                }
            }
        }
        
        Tab {
            title: "Settings"
            
            ModernSettingsPanel {
                anchors.fill: parent
                
                onSaveSettings: {
                    console.log("Settings saved")
                }
            }
        }
    }
}