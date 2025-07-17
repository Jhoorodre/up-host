import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

/**
 * IndexadorDialog - Hub central do sistema indexador
 * Baseado na Seção 9 do FRONTEND_MAP_MODERN.md
 */
Dialog {
    id: root
    
    // ===== PROPERTIES =====
    property string groupName: "Meu Grupo de Scanlation"
    property int totalWorks: 4
    property int totalChapters: 471
    property real groupRating: 4.8
    property string cdnStatus: "ativo"
    property string version: "v2.1"
    
    // ===== DIALOG SETUP =====
    width: Math.min(window.width * 0.95, 1200)
    height: Math.min(window.height * 0.95, 800)
    anchors.centerIn: parent
    modal: true
    focus: true
    
    // ===== DESIGN SYSTEM =====
    DesignSystem { id: ds }
    
    // ===== DIALOG BACKGROUND =====
    background: Rectangle {
        color: ds.bgPrimary
        radius: ds.radius_lg
    }
    
    // ===== BACKEND CONNECTIONS =====
    Connections {
        target: backend
        
        function onIndexGenerationStarted() {
            console.log("Index generation started")
            isGenerating = true
        }
        
        function onIndexGenerationFinished() {
            console.log("Index generation finished")
            isGenerating = false
        }
        
        function onGithubSyncStarted() {
            console.log("GitHub sync started")
            isSyncing = true
        }
        
        function onGithubSyncFinished() {
            console.log("GitHub sync finished")
            isSyncing = false
        }
        
        function onSeriesStatusChanged(seriesName, status) {
            console.log("Series status changed:", seriesName, status)
            updateSeriesStatus(seriesName, status)
        }
        
        function onCdnValidationResult(url, isValid) {
            console.log("CDN validation result:", url, isValid)
            updateCdnStatus(url, isValid)
        }
    }
    
    // ===== STATE MANAGEMENT =====
    property bool isGenerating: false
    property bool isSyncing: false
    property bool isValidating: false
    property var seriesData: [
        {"name": "Tower of God", "chapters": 471, "cdnStatus": "ativo", "lastUpdate": "Hoje"},
        {"name": "Solo Leveling", "chapters": 179, "cdnStatus": "ativo", "lastUpdate": "Ontem"},
        {"name": "Naruto", "chapters": 720, "cdnStatus": "falhou", "lastUpdate": "2 dias"},
        {"name": "One Piece", "chapters": 1100, "cdnStatus": "ativo", "lastUpdate": "Hoje"}
    ]
    
    // ===== MAIN CONTENT =====
    contentItem: ColumnLayout {
        anchors.fill: parent
        anchors.margins: ds.space8
        spacing: ds.space6
        
        // ===== HEADER =====
        RowLayout {
            Layout.fillWidth: true
            spacing: ds.space4
            
            Text {
                text: "📋"
                font.pixelSize: ds.text_2xl
            }
            
            Text {
                text: "INDEXADOR HUB"
                font.pixelSize: ds.text_xl
                font.weight: ds.fontBold
                color: ds.textPrimary
            }
            
            Item { Layout.fillWidth: true }
            
            ModernButton {
                text: "🔄 Sincronizar"
                variant: "primary"
                size: "sm"
                enabled: !isSyncing
                loading: isSyncing
                
                onClicked: {
                    syncWithGitHub()
                }
            }
            
            ModernButton {
                text: "✕"
                variant: "ghost"
                size: "sm"
                iconOnly: true
                
                onClicked: {
                    root.close()
                }
            }
        }
        
        // ===== GROUP INFO CARD =====
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 120
            radius: ds.radius_lg
            color: ds.bgCard
            border.color: ds.border
            border.width: 1
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: ds.space6
                spacing: ds.space3
                
                // Group name and info
                RowLayout {
                    Layout.fillWidth: true
                    spacing: ds.space3
                    
                    Text {
                        text: "🏷️"
                        font.pixelSize: ds.text_lg
                    }
                    
                    Text {
                        text: groupName.toUpperCase()
                        font.pixelSize: ds.text_lg
                        font.weight: ds.fontBold
                        color: ds.textPrimary
                    }
                    
                    Item { Layout.fillWidth: true }
                    
                    ModernButton {
                        text: "⚙️ Configurar"
                        variant: "ghost"
                        size: "sm"
                        
                        onClicked: {
                            groupConfigDialog.open()
                        }
                    }
                }
                
                // Group stats
                Text {
                    text: groupName + " • " + totalWorks + " obras ativas • " + version
                    font.pixelSize: ds.text_base
                    color: ds.textSecondary
                }
                
                // Detailed stats
                RowLayout {
                    Layout.fillWidth: true
                    spacing: ds.space6
                    
                    Text {
                        text: "📊 " + totalChapters + " capítulos"
                        font.pixelSize: ds.text_sm
                        color: ds.textSecondary
                    }
                    
                    Text {
                        text: "⭐ " + groupRating + " rating"
                        font.pixelSize: ds.text_sm
                        color: ds.textSecondary
                    }
                    
                    Text {
                        text: "🌐 CDN " + cdnStatus
                        font.pixelSize: ds.text_sm
                        color: cdnStatus === "ativo" ? ds.success : ds.danger
                    }
                    
                    Item { Layout.fillWidth: true }
                }
            }
        }
        
        // ===== QUICK ACTIONS =====
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 120
            radius: ds.radius_lg
            color: ds.bgCard
            border.color: ds.border
            border.width: 1
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: ds.space6
                spacing: ds.space4
                
                Text {
                    text: "🎯 AÇÕES RÁPIDAS"
                    font.pixelSize: ds.text_base
                    font.weight: ds.fontBold
                    color: ds.textPrimary
                }
                
                GridLayout {
                    Layout.fillWidth: true
                    columns: 4
                    columnSpacing: ds.space4
                    rowSpacing: ds.space4
                    
                    // Generate Index
                    QuickActionCard {
                        title: "GERAR"
                        subtitle: "Local"
                        icon: "🔄"
                        color: ds.accent
                        enabled: !isGenerating
                        loading: isGenerating
                        
                        onClicked: {
                            generateIndex()
                        }
                    }
                    
                    // GitHub Upload
                    QuickActionCard {
                        title: "GITHUB"
                        subtitle: "Upload"
                        icon: "📤"
                        color: ds.success
                        enabled: !isSyncing
                        loading: isSyncing
                        
                        onClicked: {
                            syncWithGitHub()
                        }
                    }
                    
                    // Validate CDNs
                    QuickActionCard {
                        title: "VALIDAR"
                        subtitle: "CDNs"
                        icon: "🔍"
                        color: ds.warning
                        enabled: !isValidating
                        loading: isValidating
                        
                        onClicked: {
                            validateCdns()
                        }
                    }
                    
                    // Copy JSON
                    QuickActionCard {
                        title: "COPIAR"
                        subtitle: "JSON"
                        icon: "📋"
                        color: ds.brandSecondary
                        
                        onClicked: {
                            copyJsonToClipboard()
                        }
                    }
                }
            }
        }
        
        // ===== SERIES STATUS =====
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
                
                Text {
                    text: "📊 STATUS DAS SÉRIES"
                    font.pixelSize: ds.text_base
                    font.weight: ds.fontBold
                    color: ds.textPrimary
                }
                
                ScrollView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    
                    ColumnLayout {
                        width: parent.width
                        spacing: ds.space2
                        
                        Repeater {
                            model: seriesData
                            
                            SeriesStatusItem {
                                Layout.fillWidth: true
                                seriesName: modelData.name
                                chapterCount: modelData.chapters
                                cdnStatus: modelData.cdnStatus
                                lastUpdate: modelData.lastUpdate
                                
                                onEditClicked: {
                                    console.log("Edit series:", modelData.name)
                                }
                                
                                onRefreshClicked: {
                                    console.log("Refresh series:", modelData.name)
                                    refreshSeries(modelData.name)
                                }
                            }
                        }
                    }
                }
            }
        }
        
        // ===== DISTRIBUTION LINKS =====
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 120
            radius: ds.radius_lg
            color: ds.bgCard
            border.color: ds.border
            border.width: 1
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: ds.space6
                spacing: ds.space4
                
                Text {
                    text: "🔗 LINKS DE DISTRIBUIÇÃO"
                    font.pixelSize: ds.text_base
                    font.weight: ds.fontBold
                    color: ds.textPrimary
                }
                
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: ds.space2
                    
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: ds.space3
                        
                        Text {
                            text: "CDN JSDelivr:"
                            font.pixelSize: ds.text_sm
                            color: ds.textSecondary
                            Layout.preferredWidth: 100
                        }
                        
                        ModernInput {
                            Layout.fillWidth: true
                            text: "https://cdn.jsdelivr.net/gh/user/repo@latest/"
                            size: "sm"
                            readOnly: true
                        }
                        
                        ModernButton {
                            text: "📋"
                            variant: "ghost"
                            size: "sm"
                            iconOnly: true
                            
                            onClicked: {
                                copyToClipboard("https://cdn.jsdelivr.net/gh/user/repo@latest/")
                            }
                        }
                    }
                    
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: ds.space3
                        
                        Text {
                            text: "GitHub Raw:"
                            font.pixelSize: ds.text_sm
                            color: ds.textSecondary
                            Layout.preferredWidth: 100
                        }
                        
                        ModernInput {
                            Layout.fillWidth: true
                            text: "https://raw.githubusercontent.com/user/repo/main/"
                            size: "sm"
                            readOnly: true
                        }
                        
                        ModernButton {
                            text: "📋"
                            variant: "ghost"
                            size: "sm"
                            iconOnly: true
                            
                            onClicked: {
                                copyToClipboard("https://raw.githubusercontent.com/user/repo/main/")
                            }
                        }
                    }
                }
                
                RowLayout {
                    Layout.fillWidth: true
                    spacing: ds.space3
                    
                    ModernButton {
                        text: "📋 Copiar Links"
                        variant: "secondary"
                        size: "sm"
                        
                        onClicked: {
                            copyAllLinks()
                        }
                    }
                    
                    ModernButton {
                        text: "🧪 Testar URLs"
                        variant: "secondary"
                        size: "sm"
                        
                        onClicked: {
                            testAllUrls()
                        }
                    }
                    
                    ModernButton {
                        text: "📤 Compartilhar"
                        variant: "secondary"
                        size: "sm"
                        
                        onClicked: {
                            shareLinks()
                        }
                    }
                }
            }
        }
    }
    
    // ===== QUICK ACTION CARD COMPONENT =====
    component QuickActionCard: Rectangle {
        property string title: ""
        property string subtitle: ""
        property string icon: ""
        property color color: ds.accent
        property bool enabled: true
        property bool loading: false
        
        signal clicked()
        
        Layout.fillWidth: true
        Layout.preferredHeight: 70
        radius: ds.radius_md
        color: enabled ? (mouseArea.containsMouse ? Qt.lighter(parent.color, 1.1) : parent.color) : ds.bgDisabled
        border.color: parent.color
        border.width: 2
        opacity: enabled ? 1.0 : 0.6
        
        Behavior on color {
            ColorAnimation {
                duration: ds.animationFast
                easing.type: ds.easingOut
            }
        }
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: ds.space3
            spacing: ds.space1
            
            Text {
                text: loading ? "🔄" : icon
                font.pixelSize: ds.text_lg
                Layout.alignment: Qt.AlignHCenter
                
                RotationAnimation on rotation {
                    running: loading
                    duration: 1000
                    loops: Animation.Infinite
                    from: 0
                    to: 360
                }
            }
            
            Text {
                text: title
                font.pixelSize: ds.text_sm
                font.weight: ds.fontBold
                color: ds.textPrimary
                Layout.alignment: Qt.AlignHCenter
                horizontalAlignment: Text.AlignHCenter
            }
            
            Text {
                text: subtitle
                font.pixelSize: ds.text_xs
                color: ds.textSecondary
                Layout.alignment: Qt.AlignHCenter
                horizontalAlignment: Text.AlignHCenter
            }
        }
        
        MouseArea {
            id: mouseArea
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: enabled ? Qt.PointingHandCursor : Qt.ForbiddenCursor
            enabled: parent.enabled
            
            onClicked: {
                if (parent.enabled) {
                    parent.clicked()
                }
            }
        }
    }
    
    // ===== SERIES STATUS ITEM COMPONENT =====
    component SeriesStatusItem: Rectangle {
        property string seriesName: ""
        property int chapterCount: 0
        property string cdnStatus: "ativo"
        property string lastUpdate: "Hoje"
        
        signal editClicked()
        signal refreshClicked()
        
        Layout.fillWidth: true
        height: ds.space12
        radius: ds.radius_sm
        color: mouseArea.containsMouse ? ds.hover : "transparent"
        border.color: ds.border
        border.width: 1
        
        RowLayout {
            anchors.fill: parent
            anchors.margins: ds.space3
            spacing: ds.space4
            
            // Status icon
            Text {
                text: {
                    switch (cdnStatus) {
                        case "ativo": return "✅"
                        case "falhou": return "⚠️"
                        case "processando": return "🔄"
                        default: return "❓"
                    }
                }
                font.pixelSize: ds.text_base
                color: {
                    switch (cdnStatus) {
                        case "ativo": return ds.success
                        case "falhou": return ds.danger
                        case "processando": return ds.warning
                        default: return ds.textSecondary
                    }
                }
            }
            
            // Series info
            ColumnLayout {
                Layout.fillWidth: true
                spacing: ds.space1
                
                Text {
                    text: seriesName
                    font.pixelSize: ds.text_base
                    font.weight: ds.fontMedium
                    color: ds.textPrimary
                }
                
                Text {
                    text: chapterCount + " caps • CDN " + cdnStatus + " • " + lastUpdate
                    font.pixelSize: ds.text_sm
                    color: ds.textSecondary
                }
            }
            
            // Action buttons
            RowLayout {
                spacing: ds.space2
                
                ModernButton {
                    text: "✏️"
                    variant: "ghost"
                    size: "sm"
                    iconOnly: true
                    
                    onClicked: {
                        editClicked()
                    }
                }
                
                ModernButton {
                    text: "🔄"
                    variant: "ghost"
                    size: "sm"
                    iconOnly: true
                    
                    onClicked: {
                        refreshClicked()
                    }
                }
            }
        }
        
        MouseArea {
            id: mouseArea
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
        }
    }
    
    // ===== GROUP CONFIG DIALOG =====
    Dialog {
        id: groupConfigDialog
        width: Math.min(window.width * 0.8, 600)
        height: Math.min(window.height * 0.8, 500)
        anchors.centerIn: parent
        
        modal: true
        focus: true
        
        background: Rectangle {
            color: ds.bgSurface
            radius: ds.radius_lg
        }
        
        contentItem: ColumnLayout {
            anchors.fill: parent
            anchors.margins: ds.space6
            spacing: ds.space6
            
            // Header
            RowLayout {
                Layout.fillWidth: true
                spacing: ds.space3
                
                Text {
                    text: "🏷️"
                    font.pixelSize: ds.text_2xl
                }
                
                Text {
                    text: "CONFIGURAÇÃO DO GRUPO"
                    font.pixelSize: ds.text_xl
                    font.weight: ds.fontBold
                    color: ds.textPrimary
                    Layout.fillWidth: true
                }
                
                ModernButton {
                    text: "✕"
                    variant: "ghost"
                    size: "sm"
                    iconOnly: true
                    
                    onClicked: {
                        groupConfigDialog.close()
                    }
                }
            }
            
            // Group configuration form
            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                
                ColumnLayout {
                    width: parent.width
                    spacing: ds.space4
                    
                    // Basic info
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: ds.space3
                        
                        Text {
                            text: "📋 INFORMAÇÕES BÁSICAS"
                            font.pixelSize: ds.text_base
                            font.weight: ds.fontBold
                            color: ds.textPrimary
                        }
                        
                        GridLayout {
                            Layout.fillWidth: true
                            columns: 2
                            columnSpacing: ds.space4
                            rowSpacing: ds.space3
                            
                            Text {
                                text: "Nome do Grupo:"
                                font.pixelSize: ds.text_sm
                                color: ds.textSecondary
                            }
                            
                            ModernInput {
                                Layout.fillWidth: true
                                text: groupName
                                placeholderText: "Nome do seu grupo"
                                size: "lg"
                                
                                onTextChanged: {
                                    groupName = text
                                }
                            }
                            
                            Text {
                                text: "Descrição:"
                                font.pixelSize: ds.text_sm
                                color: ds.textSecondary
                            }
                            
                            ModernInput {
                                Layout.fillWidth: true
                                placeholderText: "Descrição do grupo"
                                size: "lg"
                            }
                            
                            Text {
                                text: "Website:"
                                font.pixelSize: ds.text_sm
                                color: ds.textSecondary
                            }
                            
                            ModernInput {
                                Layout.fillWidth: true
                                placeholderText: "https://seusite.com"
                                size: "lg"
                            }
                        }
                    }
                }
            }
            
            // Save button
            RowLayout {
                Layout.fillWidth: true
                spacing: ds.space4
                
                ModernButton {
                    text: "Cancelar"
                    variant: "secondary"
                    size: "lg"
                    Layout.fillWidth: true
                    
                    onClicked: {
                        groupConfigDialog.close()
                    }
                }
                
                ModernButton {
                    text: "💾 Salvar"
                    variant: "primary"
                    size: "lg"
                    Layout.fillWidth: true
                    
                    onClicked: {
                        saveGroupConfig()
                        groupConfigDialog.close()
                    }
                }
            }
        }
    }
    
    // ===== FUNCTIONS =====
    function generateIndex() {
        console.log("Generating index...")
        if (backend.generateIndex) {
            backend.generateIndex()
        }
    }
    
    function syncWithGitHub() {
        console.log("Syncing with GitHub...")
        if (backend.syncWithGitHub) {
            backend.syncWithGitHub()
        }
    }
    
    function validateCdns() {
        console.log("Validating CDNs...")
        isValidating = true
        
        if (backend.validateCdns) {
            backend.validateCdns()
        }
        
        // Simulate validation
        Timer {
            interval: 2000
            running: true
            onTriggered: {
                isValidating = false
            }
        }
    }
    
    function copyJsonToClipboard() {
        console.log("Copying JSON to clipboard...")
        if (backend.copyJsonToClipboard) {
            backend.copyJsonToClipboard()
        }
    }
    
    function copyToClipboard(text) {
        console.log("Copying to clipboard:", text)
        if (backend.copyToClipboard) {
            backend.copyToClipboard(text)
        }
    }
    
    function copyAllLinks() {
        console.log("Copying all links...")
        var links = "CDN JSDelivr: https://cdn.jsdelivr.net/gh/user/repo@latest/\nGitHub Raw: https://raw.githubusercontent.com/user/repo/main/"
        copyToClipboard(links)
    }
    
    function testAllUrls() {
        console.log("Testing all URLs...")
        if (backend.testAllUrls) {
            backend.testAllUrls()
        }
    }
    
    function shareLinks() {
        console.log("Sharing links...")
        if (backend.shareLinks) {
            backend.shareLinks()
        }
    }
    
    function refreshSeries(seriesName) {
        console.log("Refreshing series:", seriesName)
        if (backend.refreshSeries) {
            backend.refreshSeries(seriesName)
        }
    }
    
    function updateSeriesStatus(seriesName, status) {
        console.log("Updating series status:", seriesName, status)
        // Update seriesData array
        for (var i = 0; i < seriesData.length; i++) {
            if (seriesData[i].name === seriesName) {
                seriesData[i].cdnStatus = status
                seriesData = seriesData.slice() // Trigger property change
                break
            }
        }
    }
    
    function updateCdnStatus(url, isValid) {
        console.log("Updating CDN status:", url, isValid)
        cdnStatus = isValid ? "ativo" : "falhou"
    }
    
    function saveGroupConfig() {
        console.log("Saving group config...")
        if (backend.saveGroupConfig) {
            backend.saveGroupConfig({
                name: groupName,
                description: "",
                website: ""
            })
        }
    }
    
    // ===== INITIALIZATION =====
    Component.onCompleted: {
        if (backend.loadIndexadorData) {
            backend.loadIndexadorData()
        }
    }
}
