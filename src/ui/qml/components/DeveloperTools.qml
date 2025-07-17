import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

/**
 * Developer Tools - Item 13 do FRONTEND_MAP_MODERN.md
 * Debug Panel com métricas de performance, logs e testes
 */
Rectangle {
    id: root
    
    // ===== DESIGN SYSTEM =====
    DesignSystem { id: ds }
    
    // ===== PUBLIC PROPERTIES =====
    property bool devMode: true
    property var performanceMetrics: {
        "qml_render_time": "16.7ms",
        "fps": "60 FPS",
        "memory_usage": "145MB",
        "memory_limit": "512MB",
        "http_connections": 8,
        "max_connections": 20,
        "upload_queue_size": 3
    }
    
    property var apiLogs: [
        {
            timestamp: "14:32:15",
            method: "POST",
            url: "catbox.moe/user/api.php",
            status: 200,
            duration: "1.2s",
            size: "2.3MB",
            type: "success"
        },
        {
            timestamp: "14:31:58",
            method: "GET", 
            url: "api.github.com/repos/user/repo",
            status: 200,
            duration: "0.8s",
            size: "45KB",
            type: "success"
        },
        {
            timestamp: "14:31:42",
            method: "POST",
            url: "imgur.com/api/upload",
            status: 429,
            duration: "2.1s",
            size: "-",
            type: "error",
            error: "Rate Limited"
        },
        {
            timestamp: "14:31:28",
            method: "GET",
            url: "cdn.jsdelivr.net/gh/user/repo",
            status: 200,
            duration: "0.3s",
            size: "128KB",
            type: "success"
        }
    ]
    
    property var debugSettings: {
        "detailed_logs": true,
        "network_timing": true,
        "qml_debugging": false,
        "auto_reload_qml": false,
        "mock_api_calls": false,
        "performance_overlay": false
    }
    
    // ===== LAYOUT =====
    color: ds.bgPrimary
    visible: devMode
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: ds.space6
        spacing: ds.space6
        
        // ===== HEADER =====
        RowLayout {
            Layout.fillWidth: true
            spacing: ds.space4
            
            Text {
                text: "🛠️ Developer Tools"
                font.pixelSize: ds.text_2xl
                font.weight: ds.fontBold
                color: ds.textPrimary
            }
            
            Rectangle {
                width: developerBadge.implicitWidth + ds.space4
                height: ds.space6
                radius: ds.radius_full
                color: ds.accent
                
                Text {
                    id: developerBadge
                    anchors.centerIn: parent
                    text: "👁️ DEV MODE"
                    font.pixelSize: ds.text_xs
                    font.weight: ds.fontBold
                    color: ds.textPrimary
                }
            }
            
            Item { Layout.fillWidth: true }
            
            ModernButton {
                text: "Toggle Dev Mode"
                icon: "🔧"
                variant: "secondary"
                size: "sm"
                
                onClicked: {
                    devMode = !devMode
                }
            }
        }
        
        // ===== PERFORMANCE METRICS =====
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 160
            radius: ds.radius_lg
            color: ds.bgCard
            border.color: ds.border
            border.width: 1
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: ds.space6
                spacing: ds.space4
                
                Text {
                    text: "📊 Performance Metrics"
                    font.pixelSize: ds.text_xl
                    font.weight: ds.fontMedium
                    color: ds.textPrimary
                }
                
                GridLayout {
                    Layout.fillWidth: true
                    columns: {
                        if (parent.width <= ds.mobile) return 1
                        if (parent.width <= ds.tablet) return 2
                        return 4
                    }
                    columnSpacing: ds.space6
                    rowSpacing: ds.space3
                    
                    // QML Render Performance
                    ColumnLayout {
                        spacing: ds.space1
                        
                        Text {
                            text: "QML Render Time:"
                            font.pixelSize: ds.text_sm
                            color: ds.textSecondary
                        }
                        
                        Text {
                            text: performanceMetrics.qml_render_time + " (" + performanceMetrics.fps + ")"
                            font.pixelSize: ds.text_base
                            font.weight: ds.fontBold
                            color: ds.success
                        }
                    }
                    
                    // Memory Usage
                    ColumnLayout {
                        spacing: ds.space1
                        
                        Text {
                            text: "Memory Usage:"
                            font.pixelSize: ds.text_sm
                            color: ds.textSecondary
                        }
                        
                        Text {
                            text: performanceMetrics.memory_usage + " / " + performanceMetrics.memory_limit
                            font.pixelSize: ds.text_base
                            font.weight: ds.fontBold
                            color: getMemoryColor()
                        }
                    }
                    
                    // HTTP Connections
                    ColumnLayout {
                        spacing: ds.space1
                        
                        Text {
                            text: "HTTP Connections:"
                            font.pixelSize: ds.text_sm
                            color: ds.textSecondary
                        }
                        
                        Text {
                            text: performanceMetrics.http_connections + "/" + performanceMetrics.max_connections
                            font.pixelSize: ds.text_base
                            font.weight: ds.fontBold
                            color: ds.textPrimary
                        }
                    }
                    
                    // Upload Queue
                    ColumnLayout {
                        spacing: ds.space1
                        
                        Text {
                            text: "Upload Queue Size:"
                            font.pixelSize: ds.text_sm
                            color: ds.textSecondary
                        }
                        
                        Text {
                            text: performanceMetrics.upload_queue_size + " jobs"
                            font.pixelSize: ds.text_base
                            font.weight: ds.fontBold
                            color: performanceMetrics.upload_queue_size > 0 ? ds.warning : ds.success
                        }
                    }
                }
            }
        }
        
        // ===== API LOGS =====
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: ds.radius_lg
            color: ds.bgCard
            border.color: ds.border
            border.width: 1
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: ds.space6
                spacing: ds.space4
                
                RowLayout {
                    Layout.fillWidth: true
                    spacing: ds.space4
                    
                    Text {
                        text: "🔍 API Logs (Últimas 10 requisições)"
                        font.pixelSize: ds.text_xl
                        font.weight: ds.fontMedium
                        color: ds.textPrimary
                    }
                    
                    Item { Layout.fillWidth: true }
                    
                    ModernButton {
                        text: "Limpar"
                        icon: "🗑️"
                        variant: "ghost"
                        size: "sm"
                        
                        onClicked: {
                            clearApiLogs()
                        }
                    }
                    
                    ModernButton {
                        text: "Atualizar"
                        icon: "🔄"
                        variant: "ghost"
                        size: "sm"
                        
                        onClicked: {
                            refreshApiLogs()
                        }
                    }
                }
                
                // Log Headers
                Rectangle {
                    Layout.fillWidth: true
                    height: ds.space8
                    color: ds.bgSurface
                    radius: ds.radius_sm
                    
                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: ds.space3
                        spacing: ds.space4
                        
                        Text {
                            text: "Time"
                            font.pixelSize: ds.text_sm
                            font.weight: ds.fontBold
                            color: ds.textSecondary
                            Layout.preferredWidth: 60
                        }
                        
                        Text {
                            text: "Status"
                            font.pixelSize: ds.text_sm
                            font.weight: ds.fontBold
                            color: ds.textSecondary
                            Layout.preferredWidth: 50
                        }
                        
                        Text {
                            text: "Method"
                            font.pixelSize: ds.text_sm
                            font.weight: ds.fontBold
                            color: ds.textSecondary
                            Layout.preferredWidth: 60
                        }
                        
                        Text {
                            text: "URL"
                            font.pixelSize: ds.text_sm
                            font.weight: ds.fontBold
                            color: ds.textSecondary
                            Layout.fillWidth: true
                        }
                        
                        Text {
                            text: "Duration"
                            font.pixelSize: ds.text_sm
                            font.weight: ds.fontBold
                            color: ds.textSecondary
                            Layout.preferredWidth: 60
                        }
                        
                        Text {
                            text: "Size"
                            font.pixelSize: ds.text_sm
                            font.weight: ds.fontBold
                            color: ds.textSecondary
                            Layout.preferredWidth: 60
                        }
                    }
                }
                
                // Log Entries
                ScrollView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    
                    ColumnLayout {
                        width: parent.width
                        spacing: ds.space1
                        
                        Repeater {
                            model: apiLogs
                            
                            Rectangle {
                                Layout.fillWidth: true
                                height: ds.space8
                                color: mouseArea.containsMouse ? ds.hover : "transparent"
                                radius: ds.radius_sm
                                
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: ds.space3
                                    spacing: ds.space4
                                    
                                    Text {
                                        text: modelData.timestamp
                                        font.pixelSize: ds.text_sm
                                        font.family: "Consolas, Monaco, monospace"
                                        color: ds.textSecondary
                                        Layout.preferredWidth: 60
                                    }
                                    
                                    Rectangle {
                                        width: statusText.implicitWidth + ds.space2
                                        height: ds.space4
                                        radius: ds.radius_sm
                                        color: getStatusColor(modelData.status)
                                        Layout.preferredWidth: 50
                                        
                                        Text {
                                            id: statusText
                                            anchors.centerIn: parent
                                            text: modelData.status
                                            font.pixelSize: ds.text_xs
                                            font.weight: ds.fontBold
                                            color: ds.textPrimary
                                        }
                                    }
                                    
                                    Text {
                                        text: modelData.method
                                        font.pixelSize: ds.text_sm
                                        font.family: "Consolas, Monaco, monospace"
                                        font.weight: ds.fontBold
                                        color: getMethodColor(modelData.method)
                                        Layout.preferredWidth: 60
                                    }
                                    
                                    Text {
                                        text: modelData.url + (modelData.error ? " - " + modelData.error : "")
                                        font.pixelSize: ds.text_sm
                                        font.family: "Consolas, Monaco, monospace"
                                        color: modelData.type === "error" ? ds.danger : ds.textPrimary
                                        elide: Text.ElideRight
                                        Layout.fillWidth: true
                                    }
                                    
                                    Text {
                                        text: modelData.duration
                                        font.pixelSize: ds.text_sm
                                        font.family: "Consolas, Monaco, monospace"
                                        color: getDurationColor(modelData.duration)
                                        Layout.preferredWidth: 60
                                    }
                                    
                                    Text {
                                        text: modelData.size
                                        font.pixelSize: ds.text_sm
                                        font.family: "Consolas, Monaco, monospace"
                                        color: ds.textSecondary
                                        Layout.preferredWidth: 60
                                    }
                                }
                                
                                MouseArea {
                                    id: mouseArea
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    
                                    onClicked: {
                                        showLogDetails(modelData)
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        // ===== QUICK TESTS & DEBUG SETTINGS =====
        GridLayout {
            Layout.fillWidth: true
            columns: parent.width <= ds.tablet ? 1 : 2
            columnSpacing: ds.space6
            rowSpacing: ds.space6
            
            // Quick Tests
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 160
                radius: ds.radius_lg
                color: ds.bgCard
                border.color: ds.border
                border.width: 1
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: ds.space6
                    spacing: ds.space4
                    
                    Text {
                        text: "🧪 Testes Rápidos"
                        font.pixelSize: ds.text_lg
                        font.weight: ds.fontMedium
                        color: ds.textPrimary
                    }
                    
                    GridLayout {
                        Layout.fillWidth: true
                        columns: 2
                        columnSpacing: ds.space3
                        rowSpacing: ds.space3
                        
                        ModernButton {
                            text: "Testar Hosts"
                            icon: "🌐"
                            variant: "secondary"
                            size: "sm"
                            Layout.fillWidth: true
                            
                            onClicked: testHosts()
                        }
                        
                        ModernButton {
                            text: "Validar JSONs"
                            icon: "📋"
                            variant: "secondary"
                            size: "sm"
                            Layout.fillWidth: true
                            
                            onClicked: validateJsons()
                        }
                        
                        ModernButton {
                            text: "Verificar CDNs"
                            icon: "🔗"
                            variant: "secondary"
                            size: "sm"
                            Layout.fillWidth: true
                            
                            onClicked: checkCdns()
                        }
                        
                        ModernButton {
                            text: "Upload de Teste"
                            icon: "📤"
                            variant: "secondary"
                            size: "sm"
                            Layout.fillWidth: true
                            
                            onClicked: testUpload()
                        }
                        
                        ModernButton {
                            text: "Reset Cache"
                            icon: "🔄"
                            variant: "warning"
                            size: "sm"
                            Layout.fillWidth: true
                            
                            onClicked: resetCache()
                        }
                        
                        ModernButton {
                            text: "Export Logs"
                            icon: "💾"
                            variant: "primary"
                            size: "sm"
                            Layout.fillWidth: true
                            
                            onClicked: exportLogs()
                        }
                    }
                }
            }
            
            // Debug Settings
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 160
                radius: ds.radius_lg
                color: ds.bgCard
                border.color: ds.border
                border.width: 1
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: ds.space6
                    spacing: ds.space4
                    
                    Text {
                        text: "⚙️ Configurações Debug"
                        font.pixelSize: ds.text_lg
                        font.weight: ds.fontMedium
                        color: ds.textPrimary
                    }
                    
                    GridLayout {
                        Layout.fillWidth: true
                        columns: 1
                        rowSpacing: ds.space2
                        
                        CheckBox {
                            text: "Logs detalhados"
                            checked: debugSettings.detailed_logs
                            font.pixelSize: ds.text_sm
                            
                            onCheckedChanged: {
                                debugSettings.detailed_logs = checked
                                saveDebugSettings()
                            }
                        }
                        
                        CheckBox {
                            text: "Network timing"
                            checked: debugSettings.network_timing
                            font.pixelSize: ds.text_sm
                            
                            onCheckedChanged: {
                                debugSettings.network_timing = checked
                                saveDebugSettings()
                            }
                        }
                        
                        CheckBox {
                            text: "QML debugging"
                            checked: debugSettings.qml_debugging
                            font.pixelSize: ds.text_sm
                            
                            onCheckedChanged: {
                                debugSettings.qml_debugging = checked
                                saveDebugSettings()
                            }
                        }
                        
                        CheckBox {
                            text: "Performance overlay"
                            checked: debugSettings.performance_overlay
                            font.pixelSize: ds.text_sm
                            
                            onCheckedChanged: {
                                debugSettings.performance_overlay = checked
                                saveDebugSettings()
                            }
                        }
                    }
                }
            }
        }
    }
    
    // ===== FUNCTIONS =====
    function getMemoryColor() {
        var usage = parseInt(performanceMetrics.memory_usage)
        var limit = parseInt(performanceMetrics.memory_limit)
        var percentage = usage / limit
        
        if (percentage > 0.8) return ds.danger
        if (percentage > 0.6) return ds.warning
        return ds.success
    }
    
    function getStatusColor(status) {
        if (status >= 200 && status < 300) return ds.success
        if (status >= 400 && status < 500) return ds.warning
        if (status >= 500) return ds.danger
        return ds.textSecondary
    }
    
    function getMethodColor(method) {
        switch (method) {
            case "GET": return ds.success
            case "POST": return ds.accent
            case "PUT": return ds.warning
            case "DELETE": return ds.danger
            default: return ds.textSecondary
        }
    }
    
    function getDurationColor(duration) {
        var time = parseFloat(duration)
        if (time > 3.0) return ds.danger
        if (time > 1.0) return ds.warning
        return ds.success
    }
    
    function clearApiLogs() {
        apiLogs = []
        console.log("API logs cleared")
    }
    
    function refreshApiLogs() {
        console.log("API logs refreshed")
        // TODO: Fetch fresh logs from backend
    }
    
    function showLogDetails(logEntry) {
        console.log("Show log details:", JSON.stringify(logEntry))
        // TODO: Open detailed log view
    }
    
    function testHosts() {
        console.log("Testing all hosts...")
        // TODO: Run host connectivity tests
    }
    
    function validateJsons() {
        console.log("Validating JSON files...")
        // TODO: Validate JSON structure
    }
    
    function checkCdns() {
        console.log("Checking CDN availability...")
        // TODO: Test CDN endpoints
    }
    
    function testUpload() {
        console.log("Running test upload...")
        // TODO: Perform test upload
    }
    
    function resetCache() {
        console.log("Resetting cache...")
        // TODO: Clear application cache
    }
    
    function exportLogs() {
        console.log("Exporting logs...")
        // TODO: Export logs to file
    }
    
    function saveDebugSettings() {
        console.log("Debug settings saved:", JSON.stringify(debugSettings))
        // TODO: Save settings to backend
    }
}