import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

/**
 * Notification Center - Item 12 do FRONTEND_MAP_MODERN.md
 * Central de notificações com real-time updates e configurações
 */
Rectangle {
    id: root
    
    // ===== DESIGN SYSTEM =====
    DesignSystem { id: ds }
    
    // ===== PUBLIC PROPERTIES =====
    property var notifications: []
    property int unreadCount: 0
    
    property var notificationSettings: {
        "uploads_completed": true,
        "critical_errors": true,
        "github_updates": true,
        "cdn_warnings": false,
        "statistics": false,
        "push_notifications": false
    }
    
    // ===== LAYOUT =====
    color: ds.bgPrimary
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: ds.space6
        spacing: ds.space6
        
        // ===== HEADER =====
        RowLayout {
            Layout.fillWidth: true
            spacing: ds.space4
            
            Text {
                text: "🔔 Notificações"
                font.pixelSize: ds.text_2xl
                font.weight: ds.fontBold
                color: ds.textPrimary
            }
            
            Rectangle {
                visible: getUnreadCount() > 0
                width: countText.implicitWidth + ds.space3
                height: ds.space5
                radius: ds.radius_full
                color: ds.danger
                
                Text {
                    id: countText
                    anchors.centerIn: parent
                    text: getUnreadCount()
                    font.pixelSize: ds.text_xs
                    font.weight: ds.fontBold
                    color: ds.textPrimary
                }
            }
            
            Item { Layout.fillWidth: true }
            
            ModernButton {
                text: "Marcar Todas"
                icon: "🔕"
                variant: "ghost"
                size: "sm"
                enabled: getUnreadCount() > 0
                
                onClicked: {
                    markAllAsRead()
                }
            }
        }
        
        // ===== NOTIFICATIONS LIST =====
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            
            ColumnLayout {
                width: parent.width
                spacing: ds.space3
                
                Repeater {
                    model: notifications
                    
                    NotificationItem {
                        Layout.fillWidth: true
                        notification: modelData
                        
                        onActionClicked: function(action) {
                            handleNotificationAction(modelData.id, action)
                        }
                        
                        onMarkAsRead: {
                            markNotificationAsRead(modelData.id)
                        }
                        
                        onDismiss: {
                            dismissNotification(modelData.id)
                        }
                    }
                }
                
                // Empty state
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 200
                    color: "transparent"
                    visible: notifications.length === 0
                    
                    ColumnLayout {
                        anchors.centerIn: parent
                        spacing: ds.space4
                        
                        Text {
                            text: "🔕"
                            font.pixelSize: ds.text_4xl
                            Layout.alignment: Qt.AlignHCenter
                        }
                        
                        Text {
                            text: "Nenhuma notificação"
                            font.pixelSize: ds.text_lg
                            color: ds.textSecondary
                            Layout.alignment: Qt.AlignHCenter
                        }
                    }
                }
            }
        }
        
        // ===== SETTINGS SECTION =====
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 200
            radius: ds.radius_lg
            color: ds.bgCard
            border.color: ds.border
            border.width: 1
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: ds.space6
                spacing: ds.space4
                
                Text {
                    text: "⚙️ Configurações de Notificação"
                    font.pixelSize: ds.text_lg
                    font.weight: ds.fontMedium
                    color: ds.textPrimary
                }
                
                GridLayout {
                    Layout.fillWidth: true
                    columns: parent.width <= ds.mobile ? 1 : 2
                    columnSpacing: ds.space6
                    rowSpacing: ds.space3
                    
                    CheckBox {
                        text: "Uploads concluídos"
                        checked: notificationSettings.uploads_completed
                        font.pixelSize: ds.text_sm
                        
                        onCheckedChanged: {
                            notificationSettings.uploads_completed = checked
                            saveNotificationSettings()
                        }
                    }
                    
                    CheckBox {
                        text: "Erros críticos"
                        checked: notificationSettings.critical_errors
                        font.pixelSize: ds.text_sm
                        
                        onCheckedChanged: {
                            notificationSettings.critical_errors = checked
                            saveNotificationSettings()
                        }
                    }
                    
                    CheckBox {
                        text: "Updates do GitHub"
                        checked: notificationSettings.github_updates
                        font.pixelSize: ds.text_sm
                        
                        onCheckedChanged: {
                            notificationSettings.github_updates = checked
                            saveNotificationSettings()
                        }
                    }
                    
                    CheckBox {
                        text: "Avisos de CDN"
                        checked: notificationSettings.cdn_warnings
                        font.pixelSize: ds.text_sm
                        
                        onCheckedChanged: {
                            notificationSettings.cdn_warnings = checked
                            saveNotificationSettings()
                        }
                    }
                    
                    CheckBox {
                        text: "Estatísticas"
                        checked: notificationSettings.statistics
                        font.pixelSize: ds.text_sm
                        
                        onCheckedChanged: {
                            notificationSettings.statistics = checked
                            saveNotificationSettings()
                        }
                    }
                    
                    CheckBox {
                        text: "Notificações push"
                        checked: notificationSettings.push_notifications
                        font.pixelSize: ds.text_sm
                        
                        onCheckedChanged: {
                            notificationSettings.push_notifications = checked
                            saveNotificationSettings()
                        }
                    }
                }
            }
        }
    }
    
    // ===== NOTIFICATION ITEM COMPONENT =====
    component NotificationItem: Rectangle {
        property var notification
        
        signal actionClicked(string action)
        signal markAsRead()
        signal dismiss()
        
        height: contentColumn.implicitHeight + ds.space6
        radius: ds.radius_md
        color: notification.unread ? ds.bgCard : ds.bgSurface
        border.color: notification.unread ? ds.accent : ds.border
        border.width: notification.unread ? 2 : 1
        
        // Unread indicator
        Rectangle {
            visible: notification.unread
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            width: 4
            color: getNotificationColor(notification.type)
            radius: ds.radius_sm
        }
        
        ColumnLayout {
            id: contentColumn
            anchors.fill: parent
            anchors.margins: ds.space4
            anchors.leftMargin: notification.unread ? ds.space6 : ds.space4
            spacing: ds.space3
            
            // Header
            RowLayout {
                Layout.fillWidth: true
                spacing: ds.space3
                
                Text {
                    text: notification.icon
                    font.pixelSize: ds.text_base
                }
                
                Text {
                    text: notification.title
                    font.pixelSize: ds.text_sm
                    font.weight: ds.fontBold
                    color: ds.textPrimary
                }
                
                Item { Layout.fillWidth: true }
                
                Text {
                    text: notification.timestamp
                    font.pixelSize: ds.text_xs
                    color: ds.textSecondary
                }
                
                ModernButton {
                    icon: "✕"
                    variant: "ghost"
                    size: "sm"
                    iconOnly: true
                    
                    onClicked: {
                        dismiss()
                    }
                }
            }
            
            // Message
            Text {
                Layout.fillWidth: true
                text: notification.message
                font.pixelSize: ds.text_base
                color: ds.textPrimary
                wrapMode: Text.WordWrap
            }
            
            // Details
            Text {
                Layout.fillWidth: true
                text: notification.details
                font.pixelSize: ds.text_sm
                color: ds.textSecondary
                wrapMode: Text.WordWrap
                visible: notification.details !== ""
            }
            
            // Actions
            RowLayout {
                Layout.fillWidth: true
                spacing: ds.space3
                visible: notification.actions.length > 0
                
                Repeater {
                    model: notification.actions
                    
                    ModernButton {
                        text: modelData
                        variant: index === 0 ? "primary" : "secondary"
                        size: "sm"
                        
                        onClicked: {
                            actionClicked(modelData)
                        }
                    }
                }
                
                Item { Layout.fillWidth: true }
                
                ModernButton {
                    text: "Marcar como lida"
                    variant: "ghost"
                    size: "sm"
                    visible: notification.unread
                    
                    onClicked: {
                        markAsRead()
                    }
                }
            }
        }
        
        MouseArea {
            anchors.fill: parent
            acceptedButtons: Qt.NoButton
            hoverEnabled: true
            
            onEntered: {
                parent.color = Qt.lighter(parent.color, 1.05)
            }
            
            onExited: {
                parent.color = notification.unread ? ds.bgCard : ds.bgSurface
            }
        }
    }
    
    // ===== FUNCTIONS =====
    function getUnreadCount() {
        var count = 0
        for (var i = 0; i < notifications.length; i++) {
            if (notifications[i].unread) count++
        }
        return count
    }
    
    function getNotificationColor(type) {
        switch (type) {
            case "success": return ds.success
            case "warning": return ds.warning
            case "error": return ds.danger
            default: return ds.accent
        }
    }
    
    
    function markNotificationAsRead(notificationId) {
        for (var i = 0; i < notifications.length; i++) {
            if (notifications[i].id === notificationId) {
                notifications[i].unread = false
                break
            }
        }
        notifications = notifications.slice() // Trigger property change
        console.log("Notification marked as read:", notificationId)
    }
    
    function dismissNotification(notificationId) {
        for (var i = 0; i < notifications.length; i++) {
            if (notifications[i].id === notificationId) {
                notifications.splice(i, 1)
                break
            }
        }
        notifications = notifications.slice() // Trigger property change
        console.log("Notification dismissed:", notificationId)
    }
    
    function handleNotificationAction(notificationId, action) {
        console.log("Notification action:", notificationId, action)
        
        switch (action) {
            case "Corrigir":
                // Open settings to fix API key
                break
            case "Tentar novamente":
                // Retry upload
                break
            case "Ver detalhes":
                // Show detailed info
                break
        }
    }
    
    function saveNotificationSettings() {
        // Save settings to backend
        console.log("Notification settings saved:", JSON.stringify(notificationSettings))
    }
    
    function addNotification(type, title, message, details = "", actions = []) {
        var newNotification = {
            id: "notif_" + Date.now(),
            type: type,
            icon: getNotificationIcon(type),
            title: title,
            message: message,
            details: details,
            timestamp: "agora",
            unread: true,
            actions: actions
        }
        
        notifications.unshift(newNotification)
        notifications = notifications.slice() // Trigger property change
    }
    
    function getNotificationIcon(type) {
        switch (type) {
            case "success": return "🟢"
            case "warning": return "🟡"
            case "error": return "🔴"
            default: return "🔵"
        }
    }
    
    function loadNotifications() {
        console.log("Loading notifications from backend...")
        
        if (backend.getNotifications) {
            notifications = backend.getNotifications()
        } else {
            // Generate demo notifications
            generateDemoNotifications()
        }
        
        updateUnreadCount()
    }
    
    function generateDemoNotifications() {
        notifications = [
            {
                id: "notif_1",
                type: "success",
                icon: "🟢",
                title: "UPLOAD CONCLUÍDO",
                message: "Upload finalizado com sucesso",
                details: "📁 Todas as imagens processadas • 🔗 Links gerados",
                timestamp: "2 min",
                unread: true,
                actions: []
            },
            {
                id: "notif_2",
                type: "warning",
                icon: "🟡",
                title: "AVISO CDN",
                message: "Verificação de CDN em andamento",
                details: "🔄 Testando conectividade...",
                timestamp: "15 min",
                unread: true,
                actions: ["Ver detalhes"]
            },
            {
                id: "notif_3",
                type: "success",
                icon: "🟢",
                title: "INDEXADOR ATUALIZADO",
                message: "Índice JSON regenerado",
                details: "📤 Sincronizado com GitHub",
                timestamp: "1 hora",
                unread: false,
                actions: []
            }
        ]
    }
    
    function updateUnreadCount() {
        unreadCount = 0
        for (var i = 0; i < notifications.length; i++) {
            if (notifications[i].unread) {
                unreadCount++
            }
        }
    }
    
    function markAllAsRead() {
        for (var i = 0; i < notifications.length; i++) {
            notifications[i].unread = false
        }
        notifications = notifications.slice() // Trigger property change
        updateUnreadCount()
    }
    
    function clearAllNotifications() {
        notifications = []
        unreadCount = 0
    }
    
    // ===== INITIALIZATION =====
    Component.onCompleted: {
        loadNotifications()
    }
    
}