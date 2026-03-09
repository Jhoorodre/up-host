import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls.Material 2.15
import Backend 1.0

Dialog {
    id: batchDialog
    modal: true
    anchors.centerIn: parent
    width: 800
    height: 600
    
    Material.theme: Material.Dark
    Material.background: "#1a1a1a"
    Material.primary: "#0078d4"
    Material.accent: "#0078d4"
    
    // Material Design Dark theme colors
    property color colorPrimary: "#1a1a1a"
    property color colorSurface: "#2d2d2d"
    property color colorSecondary: "#0078d4"  
    property color colorTertiary: "#ffffff"
    property color colorSuccess: "#107c10"
    property color colorWarning: "#ff8c00"
    property color colorError: "#d83b01"
    
    // State variables
    property var batchQueueStatus: null
    property var batchJobs: []
    property bool isProcessing: false
    property string selectedMode: "sequential"
    property bool autoProcessingEnabled: true
    property bool priorityEnabled: true
    
    // Refresh data when dialog opens
    onOpened: {
        refreshBatchData()
        refreshTimer.start()
    }
    
    onClosed: {
        refreshTimer.stop()
    }
    
    // Auto-refresh timer
    Timer {
        id: refreshTimer
        interval: 2000 // 2 seconds
        running: false
        repeat: true
        onTriggered: refreshBatchData()
    }
    
    function refreshBatchData() {
        batchQueueStatus = backend.getBatchQueueStatus()
        batchJobs = backend.getAllBatchJobs()
        
        if (batchQueueStatus) {
            isProcessing = (batchQueueStatus.activeJobs > 0) || ((batchQueueStatus.queuedJobs || 0) > 0)
        }
    }
    
    function formatDuration(seconds) {
        if (seconds < 60) {
            return Math.round(seconds) + "s"
        } else if (seconds < 3600) {
            return Math.round(seconds / 60) + "m"
        } else {
            return Math.round(seconds / 3600) + "h"
        }
    }
    
    function getStatusIcon(status) {
        switch (status) {
            case "pending": return "⏳"
            case "queued": return "🕒"
            case "running": return "▶️"
            case "completed": return "✅"
            case "failed": return "❌"
            case "cancelled": return "⏹️"
            case "paused": return "⏸️"
            default: return "❓"
        }
    }
    
    function getStatusColor(status) {
        switch (status) {
            case "pending": return colorWarning
            case "queued": return colorSecondary
            case "running": return colorSecondary
            case "completed": return colorSuccess
            case "failed": return colorError
            case "cancelled": return colorTertiary
            case "paused": return colorWarning
            default: return colorTertiary
        }
    }
    
    header: Rectangle {
        height: 60
        color: colorSurface
        
        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 24
            anchors.rightMargin: 16
            
            Rectangle {
                width: 32
                height: 32
                radius: 6
                color: colorSecondary
                
                Label {
                    anchors.centerIn: parent
                    text: "📦"
                    font.pixelSize: 16
                    color: "white"
                }
            }
            
            Label {
                text: "BATCH UPLOAD MANAGER"
                font.pixelSize: 18
                font.weight: Font.Medium
                font.letterSpacing: 1
                color: colorTertiary
                Layout.fillWidth: true
            }
            
            Rectangle {
                width: 80
                height: 24
                radius: 12
                color: isProcessing ? colorSuccess : colorSurface
                border.color: isProcessing ? colorSuccess : colorTertiary
                border.width: 1
                
                Label {
                    anchors.centerIn: parent
                    text: isProcessing ? "Active" : "Idle"
                    font.pixelSize: 10
                    font.weight: Font.Medium
                    font.letterSpacing: 0.5
                    color: isProcessing ? "white" : colorTertiary
                }
            }
            
            Button {
                text: "×"
                font.pixelSize: 18
                font.bold: true
                background: Rectangle { color: "transparent" }
                Material.foreground: colorTertiary
                onClicked: batchDialog.close()
            }
        }
    }
    
    contentItem: ColumnLayout {
        spacing: 0
        
        // Control Panel
        Rectangle {
            Layout.fillWidth: true
            height: 60
            color: colorPrimary
            border.color: colorTertiary
            border.width: 1
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 16
                
                // Mode Selection
                Label {
                    text: "Mode:"
                    font.pixelSize: 12
                    font.weight: Font.Medium
                    color: colorTertiary
                }
                
                ComboBox {
                    id: modeComboBox
                    model: ["Sequential", "Parallel", "Smart Priority"]
                    currentIndex: selectedMode === "sequential" ? 0 : selectedMode === "parallel" ? 1 : 2
                    
                    Material.accent: colorSecondary
                    Material.foreground: colorTertiary
                    
                    background: Rectangle {
                        radius: 4
                        color: colorSurface
                        border.color: colorTertiary
                        border.width: 1
                    }
                    
                    onCurrentIndexChanged: {
                        selectedMode = currentIndex === 0 ? "sequential" : currentIndex === 1 ? "parallel" : "smart"
                    }
                }
                
                Rectangle {
                    width: 1
                    height: parent.height - 8
                    color: colorTertiary
                    opacity: 0.2
                }
                
                // Auto Processing Toggle
                CheckBox {
                    id: autoCheckbox
                    text: "Auto"
                    checked: autoProcessingEnabled
                    Material.accent: colorSecondary
                    Material.foreground: colorTertiary
                    
                    onCheckedChanged: autoProcessingEnabled = checked
                }
                
                // Priority Toggle
                CheckBox {
                    id: priorityCheckbox
                    text: "Priority"
                    checked: priorityEnabled
                    Material.accent: colorSecondary
                    Material.foreground: colorTertiary
                    
                    onCheckedChanged: priorityEnabled = checked
                }
                
                Item { Layout.fillWidth: true }
            }
        }
        
        // Statistics Panel
        Rectangle {
            Layout.fillWidth: true
            height: 50
            color: colorSurface
            border.color: colorTertiary
            border.width: 1
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 24
                
                Label {
                    text: batchQueueStatus ? `Queue: ${batchQueueStatus.queueSize} jobs` : "Queue: 0 jobs"
                    font.pixelSize: 11
                    font.weight: Font.Medium
                    color: colorTertiary
                }
                
                Label {
                    text: batchQueueStatus ? `Active: ${batchQueueStatus.activeJobs}` : "Active: 0"
                    font.pixelSize: 11
                    font.weight: Font.Medium
                    color: colorSecondary
                }
                
                Label {
                    text: batchQueueStatus ? `Completed: ${batchQueueStatus.completedJobs || 0}` : "Completed: 0"
                    font.pixelSize: 11
                    font.weight: Font.Medium
                    color: colorSuccess
                }
                
                Label {
                    text: batchQueueStatus ? `Failed: ${batchQueueStatus.failedJobs || 0}` : "Failed: 0"
                    font.pixelSize: 11
                    font.weight: Font.Medium
                    color: colorError
                }
                
                Rectangle {
                    width: 1
                    height: parent.height - 8
                    color: colorTertiary
                    opacity: 0.2
                }
                
                Label {
                    text: batchQueueStatus ? `Success Rate: ${(batchQueueStatus.successRate * 100).toFixed(1)}%` : "Success Rate: 0.0%"
                    font.pixelSize: 11
                    font.weight: Font.Medium
                    color: colorTertiary
                }
                
                Label {
                    text: batchQueueStatus ? `Avg: ${formatDuration(batchQueueStatus.averageTimePerItem || 0)}/item` : "Avg: 0s/item"
                    font.pixelSize: 11
                    font.weight: Font.Medium
                    color: colorTertiary
                }
                
                Item { Layout.fillWidth: true }
            }
        }
        
        // Job List
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            
            background: Rectangle {
                color: colorPrimary
                border.color: colorTertiary
                border.width: 1
            }
            
            ListView {
                id: jobListView
                model: batchJobs
                spacing: 1
                
                delegate: Rectangle {
                    width: jobListView.width
                    height: 80
                    color: index % 2 === 0 ? colorPrimary : colorSurface
                    
                    property var job: modelData || {}
                    
                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 16
                        
                        // Status Icon
                        Rectangle {
                            width: 32
                            height: 32
                            radius: 16
                            color: getStatusColor(job.status || "pending")
                            
                            Label {
                                anchors.centerIn: parent
                                text: getStatusIcon(job.status || "pending")
                                font.pixelSize: 12
                                color: "white"
                            }
                        }
                        
                        // Job Info
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 4
                            
                            Label {
                                text: job.title || "Unnamed Job"
                                font.pixelSize: 14
                                font.weight: Font.Medium
                                color: colorTertiary
                                elide: Text.ElideRight
                                Layout.fillWidth: true
                            }
                            
                            Label {
                                text: job.description || ""
                                font.pixelSize: 11
                                color: colorTertiary
                                opacity: 0.7
                                elide: Text.ElideRight
                                Layout.fillWidth: true
                            }
                            
                            // Progress bar
                            ProgressBar {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 4
                                value: (job.totalProgress || 0) / 100.0
                                
                                background: Rectangle {
                                    radius: 2
                                    color: Qt.rgba(255, 255, 255, 0.1)
                                }
                                
                                contentItem: Rectangle {
                                    width: parent.visualPosition * parent.width
                                    height: parent.height
                                    radius: 2
                                    color: getStatusColor(job.status || "pending")
                                }
                            }
                        }
                        
                        // Job Stats
                        ColumnLayout {
                            spacing: 2
                            
                            Label {
                                text: `${Math.round(job.totalProgress || 0)}%`
                                font.pixelSize: 12
                                font.weight: Font.Medium
                                color: colorSecondary
                                Layout.alignment: Qt.AlignHCenter
                            }
                            
                            Label {
                                text: job.items ? `${job.items.length} items` : "0 items"
                                font.pixelSize: 10
                                color: colorTertiary
                                opacity: 0.7
                                Layout.alignment: Qt.AlignHCenter
                            }
                        }
                        
                        // Action Buttons
                        RowLayout {
                            spacing: 8
                            
                            Button {
                                text: job.status === "running" ? "⏸️" : job.status === "paused" ? "▶️" : "▶️"
                                font.pixelSize: 10
                                width: 32
                                height: 24
                                enabled: job.status === "running" || job.status === "paused" || job.status === "pending"
                                
                                Material.background: colorSurface
                                Material.foreground: colorTertiary
                                
                                onClicked: {
                                    if (job.status === "running") {
                                        backend.pauseBatchJob(job.jobId || job.job_id)
                                    } else {
                                        backend.resumeBatchJob(job.jobId || job.job_id)
                                    }
                                    refreshBatchData()
                                }
                            }
                            
                            Button {
                                text: "⏹️"
                                font.pixelSize: 10
                                width: 32
                                height: 24
                                enabled: job.status === "running" || job.status === "paused" || job.status === "pending" || job.status === "queued"
                                
                                Material.background: colorError
                                Material.foreground: "white"
                                
                                onClicked: {
                                    backend.cancelBatchJob(job.jobId || job.job_id)
                                    refreshBatchData()
                                }
                            }
                            
                            Button {
                                text: "🗑️"
                                font.pixelSize: 10
                                width: 32
                                height: 24
                                enabled: job.status === "completed" || job.status === "failed" || job.status === "cancelled"
                                
                                Material.background: colorTertiary
                                Material.foreground: colorPrimary
                                
                                onClicked: {
                                    backend.deleteBatchJob(job.jobId || job.job_id)
                                    refreshBatchData()
                                }
                            }
                        }
                    }
                }
                
                // Empty state
                Label {
                    anchors.centerIn: parent
                    text: "No batch jobs in queue"
                    font.pixelSize: 14
                    color: colorTertiary
                    opacity: 0.5
                    visible: batchJobs.length === 0
                }
            }
        }
        
        // Control Buttons
        Rectangle {
            Layout.fillWidth: true
            height: 60
            color: colorSurface
            border.color: colorTertiary
            border.width: 1
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 16
                
                Button {
                    text: "▶️ START"
                    font.pixelSize: 11
                    font.weight: Font.Medium
                    font.letterSpacing: 0.5
                    
                    Material.background: colorSuccess
                    Material.foreground: "white"
                    
                    enabled: !isProcessing && batchJobs.some(job => job.status === "pending")
                    
                    onClicked: {
                        backend.startAllBatchJobs()
                        refreshBatchData()
                    }
                }
                
                Button {
                    text: "⏸️ PAUSE"
                    font.pixelSize: 11
                    font.weight: Font.Medium
                    font.letterSpacing: 0.5
                    
                    Material.background: colorWarning
                    Material.foreground: "white"
                    
                    enabled: isProcessing
                    
                    onClicked: {
                        backend.pauseAllRunningBatchJobs()
                        refreshBatchData()
                    }
                }
                
                Button {
                    text: "🔄 RETRY"
                    font.pixelSize: 11
                    font.weight: Font.Medium
                    font.letterSpacing: 0.5
                    
                    Material.background: colorSecondary
                    Material.foreground: "white"
                    
                    enabled: batchJobs.some(job => job.status === "failed" || job.status === "cancelled")
                    
                    onClicked: {
                        backend.retryFailedBatchJobs()
                        refreshBatchData()
                    }
                }
                
                Button {
                    text: "🗑️ CLEAR"
                    font.pixelSize: 11
                    font.weight: Font.Medium
                    font.letterSpacing: 0.5
                    
                    Material.background: colorError
                    Material.foreground: "white"
                    
                    enabled: batchJobs.some(job => job.status === "completed" || job.status === "failed" || job.status === "cancelled")
                    
                    onClicked: {
                        backend.clearFinishedBatchJobs()
                        refreshBatchData()
                    }
                }
                
                Item { Layout.fillWidth: true }
                
                Button {
                    text: "📊 EXPORT"
                    font.pixelSize: 11
                    font.weight: Font.Medium
                    font.letterSpacing: 0.5
                    
                    Material.background: colorTertiary
                    Material.foreground: colorPrimary
                    
                    enabled: batchJobs.length > 0
                    
                    onClicked: {
                        // TODO: Implement export batch results
                        console.log("Export batch results")
                    }
                }
                
                Button {
                    text: "CLOSE"
                    font.pixelSize: 11
                    font.weight: Font.Medium
                    font.letterSpacing: 0.5
                    
                    Material.background: colorSurface
                    Material.foreground: colorTertiary
                    
                    onClicked: batchDialog.close()
                }
            }
        }
    }
}