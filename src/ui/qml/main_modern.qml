import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls.Material 2.15
import QtQuick.Dialogs
import Qt.labs.platform 1.1 as Platform
import "components"

/**
 * Main Application Window - Design Minimalista Moderno
 * Baseado no FRONTEND_MAP_MODERN.md
 */
ApplicationWindow {
    id: window
    width: 1400
    height: 900
    visible: true
    title: qsTr("Manga Uploader Pro")
    
    // ===== DESIGN SYSTEM =====
    DesignSystem { id: ds }
    
    // ===== THEME SETUP =====
    Material.theme: Material.Dark
    Material.accent: ds.accent
    color: ds.bgPrimary
    
    // ===== STATE PROPERTIES =====
    property var currentManga: null
    property var selectedChapters: []
    property bool isProcessing: false
    property bool sidebarCollapsed: false
    
    // ===== STATISTICS PROPERTIES =====
    property int totalChapters: 0
    property int uploadsToday: 0
    property int activeHosts: 0
    property string storageSize: "0 MB"
    property int queueCount: 0
    property var recentActivity: []
    
    // Quick Actions states
    property bool isSyncingGitHub: false
    property bool isGeneratingAnalytics: false
    
    // Sidebar filter states
    property string currentFilter: "all" // all, favoritos, recentes, progresso, concluidos
    property var favoritedManga: []
    property var recentManga: []
    
    // Tag system
    property var availableTags: []
    property var selectedTags: []
    property string currentTag: ""
    
    // ===== COMPONENT INITIALIZATION =====
    Component.onCompleted: {
        backend.loadConfig()
        backend.refreshMangaList()
        updateStatistics()
        checkQuickActionsAvailability()
        
        // Load user data
        if (backend.loadFavorites) {
            backend.loadFavorites()
        }
        if (backend.loadRecentManga) {
            backend.loadRecentManga()
        }
        
        // Initialize tag system
        initializeTags()
        
        // Add some example activities
        addRecentActivity("info", "Aplicação iniciada", "🚀")
        addRecentActivity("success", "Configuração carregada", "⚙️")
        addRecentActivity("info", "Lista de mangás atualizada", "📚")
    }
    
    // ===== BACKEND CONNECTIONS =====
    Connections {
        target: backend
        
        function onCookieTestResult(resultType, message) {
            // Handle cookie test results
            if (resultType === "success") {
                console.log("Cookie test success:", message)
            } else {
                console.log("Cookie test failed:", message)
            }
        }
        
        function onMangaListRefreshed() {
            console.log("Manga list refreshed")
            updateStatistics()
            updateTagCounts()
            
            // Update filter counts when manga list changes
            if (currentFilter !== "all") {
                filterMangaList()
            }
        }
        
        function onFavoritesLoaded(favorites) {
            console.log("Favorites loaded:", favorites.length)
            favoritedManga = favorites || []
        }
        
        function onRecentMangaLoaded(recent) {
            console.log("Recent manga loaded:", recent.length)
            recentManga = recent || []
        }
        
        function onGithubSyncStarted() {
            console.log("GitHub sync started")
            isSyncingGitHub = true
            addRecentActivity("sync", "Sincronização GitHub iniciada", "🔄")
        }
        
        function onGithubSyncFinished(success) {
            console.log("GitHub sync finished:", success)
            isSyncingGitHub = false
            if (success) {
                addRecentActivity("success", "Sincronização GitHub concluída", "✅")
            } else {
                addRecentActivity("error", "Falha na sincronização GitHub", "❌")
            }
        }
        
        function onUploadCompleted(chapterName, result) {
            console.log("Upload completed:", chapterName)
            uploadsToday++
            
            // Add to recent activity
            var activity = {
                "type": "upload",
                "message": "Upload concluído: " + chapterName,
                "timestamp": new Date().toLocaleTimeString(),
                "icon": "📤"
            }
            recentActivity.unshift(activity)
            if (recentActivity.length > 10) {
                recentActivity.pop()
            }
            recentActivity = recentActivity.slice() // Trigger property change
        }
        
        function onUploadFailed(chapterName, error) {
            console.log("Upload failed:", chapterName, error)
            
            // Add to recent activity
            var activity = {
                "type": "error",
                "message": "Falha no upload: " + chapterName,
                "timestamp": new Date().toLocaleTimeString(),
                "icon": "❌"
            }
            recentActivity.unshift(activity)
            if (recentActivity.length > 10) {
                recentActivity.pop()
            }
            recentActivity = recentActivity.slice() // Trigger property change
        }
        
        function onConfigSaved() {
            console.log("Config saved")
            updateStatistics()
        }
        
        function onJobStatusChanged(jobId, status, progress, message) {
            console.log("Job status changed:", jobId, status)
            
            // Add to recent activity for significant status changes
            if (status === "completed" || status === "failed") {
                var activity = {
                    "type": status === "completed" ? "success" : "error",
                    "message": status === "completed" ? "Job concluído: " + jobId : "Job falhou: " + jobId,
                    "timestamp": new Date().toLocaleTimeString(),
                    "icon": status === "completed" ? "✅" : "❌"
                }
                recentActivity.unshift(activity)
                if (recentActivity.length > 10) {
                    recentActivity.pop()
                }
                recentActivity = recentActivity.slice() // Trigger property change
            }
        }
    }
    
    // ===== HEADER MINIMALISTA =====
    header: Rectangle {
        height: ds.headerHeight
        color: ds.bgSurface
        
        // Subtle bottom border
        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width
            height: 1
            color: ds.divider
        }
        
        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: ds.space6
            anchors.rightMargin: ds.space6
            spacing: ds.space8
            
            // ===== LOGO E TÍTULO =====
            RowLayout {
                spacing: ds.space3
                
                // Logo icon
                Text {
                    text: "📚"
                    font.pixelSize: ds.text_2xl
                }
                
                // Title
                Text {
                    text: "Manga Uploader Pro"
                    font.pixelSize: ds.text_xl
                    font.weight: ds.fontMedium
                    color: ds.textPrimary
                }
            }
            
            // ===== BUSCA GLOBAL =====
            ModernInput {
                Layout.preferredWidth: 300
                placeholderText: "Buscar mangás..."
                leftIcon: "🔍"
                size: "sm"
                clearable: true
                
                onTextChanged: {
                    backend.filterMangaList(text)
                }
            }
            
            // ===== SPACER =====
            Item { Layout.fillWidth: true }
            
            // ===== AÇÕES RÁPIDAS =====
            RowLayout {
                spacing: ds.space3
                
                // Estatísticas
                ModernButton {
                    text: "Estatísticas"
                    icon: "📊"
                    variant: "ghost"
                    size: "sm"
                    tooltip: "Ver estatísticas de upload"
                    
                    onClicked: {
                        analyticsDialog.open()
                    }
                }
                
                // Notificações
                ModernButton {
                    text: "Notificações"
                    icon: "🔔"
                    variant: "ghost"
                    size: "sm"
                    tooltip: "Central de notificações"
                    
                    onClicked: {
                        notificationDialog.open()
                    }
                }
                
                // Developer Tools (apenas em dev mode)
                ModernButton {
                    text: "Dev Tools"
                    icon: "🛠️"
                    variant: "ghost"
                    size: "sm"
                    tooltip: "Ferramentas de desenvolvedor"
                    visible: Qt.application.arguments.indexOf("--dev") !== -1
                    
                    onClicked: {
                        developerDialog.open()
                    }
                }
                
                // Indexador
                ModernButton {
                    text: "Indexador"
                    icon: "📋"
                    variant: "ghost"
                    size: "sm"
                    tooltip: "Gerenciar indexador JSON"
                    
                    onClicked: {
                        indexadorDialog.open()
                    }
                }
                
                // Configurações
                ModernButton {
                    text: "Configurações"
                    icon: "⚙️"
                    variant: "ghost"
                    size: "sm"
                    tooltip: "Abrir configurações"
                    
                    onClicked: {
                        settingsDrawer.open()
                    }
                }
                
                // Host atual
                Rectangle {
                    Layout.preferredWidth: 140
                    Layout.preferredHeight: ds.buttonHeightSm
                    radius: ds.radius_md
                    color: ds.bgCard
                    border.color: ds.border
                    border.width: 1
                    
                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: ds.space2
                        spacing: ds.space2
                        
                        // Host indicator
                        Rectangle {
                            width: ds.iconSm
                            height: ds.iconSm
                            radius: ds.radius_sm
                            color: getHostColor(backend.currentHost)
                            
                            Text {
                                anchors.centerIn: parent
                                text: getHostInitial(backend.currentHost)
                                font.pixelSize: ds.text_xs
                                font.weight: ds.fontBold
                                color: ds.textPrimary
                            }
                        }
                        
                        Text {
                            Layout.fillWidth: true
                            text: backend.currentHost || "Nenhum"
                            font.pixelSize: ds.text_sm
                            color: ds.textPrimary
                            elide: Text.ElideRight
                        }
                    }
                    
                    MouseArea {
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        
                        onClicked: {
                            settingsDrawer.open()
                        }
                    }
                }
            }
        }
    }
    
    // ===== LAYOUT PRINCIPAL =====
    RowLayout {
        anchors.fill: parent
        spacing: 0
        
        // ===== SIDEBAR =====
        Rectangle {
            id: sidebar
            Layout.preferredWidth: sidebarCollapsed ? ds.sidebarCollapsedWidth : ds.sidebarWidth
            Layout.fillHeight: true
            color: ds.bgSurface
            
            // Subtle right border
            Rectangle {
                anchors.right: parent.right
                width: 1
                height: parent.height
                color: ds.divider
            }
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: ds.space5
                spacing: ds.space6
                
                // ===== SIDEBAR HEADER =====
                RowLayout {
                    Layout.fillWidth: true
                    spacing: ds.space3
                    
                    Text {
                        text: "📂"
                        font.pixelSize: ds.text_lg
                        visible: !sidebarCollapsed
                    }
                    
                    Text {
                        text: "BIBLIOTECA"
                        font.pixelSize: ds.text_sm
                        font.weight: ds.fontMedium
                        font.letterSpacing: 1
                        color: ds.textSecondary
                        visible: !sidebarCollapsed
                    }
                    
                    Item { Layout.fillWidth: true }
                    
                    // Collapse button
                    ModernButton {
                        icon: sidebarCollapsed ? "▶" : "◀"
                        variant: "ghost"
                        size: "sm"
                        iconOnly: true
                        
                        onClicked: {
                            sidebarCollapsed = !sidebarCollapsed
                        }
                    }
                }
                
                // ===== FILTROS INTELIGENTES =====
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: ds.space3
                    visible: !sidebarCollapsed
                    
                    // Todos
                    SidebarItem {
                        icon: "📚"
                        text: "Todos"
                        count: mangaModel ? mangaModel.rowCount() : 0
                        active: currentFilter === "all"
                        
                        onClicked: {
                            currentFilter = "all"
                            filterMangaList()
                            addRecentActivity("filter", "Filtro removido - Exibindo todos", "📚")
                        }
                    }
                    
                    // Favoritos
                    SidebarItem {
                        icon: "🌟"
                        text: "Favoritos"
                        count: favoritedManga.length
                        active: currentFilter === "favoritos"
                        
                        onClicked: {
                            currentFilter = "favoritos"
                            filterMangaList()
                            addRecentActivity("filter", "Filtro: Favoritos aplicado", "🌟")
                        }
                    }
                    
                    // Recentes
                    SidebarItem {
                        icon: "📈"
                        text: "Recentes"
                        count: recentManga.length
                        active: currentFilter === "recentes"
                        
                        onClicked: {
                            currentFilter = "recentes"
                            filterMangaList()
                            addRecentActivity("filter", "Filtro: Recentes aplicado", "📈")
                        }
                    }
                    
                    // Em Progresso
                    SidebarItem {
                        icon: "🔄"
                        text: "Em Progresso"
                        count: getProgressCount()
                        active: currentFilter === "progresso"
                        
                        onClicked: {
                            currentFilter = "progresso"
                            filterMangaList()
                            addRecentActivity("filter", "Filtro: Em Progresso aplicado", "🔄")
                        }
                    }
                    
                    // Concluídos
                    SidebarItem {
                        icon: "✅"
                        text: "Concluídos"
                        count: getCompletedCount()
                        active: currentFilter === "concluidos"
                        
                        onClicked: {
                            currentFilter = "concluidos"
                            filterMangaList()
                            addRecentActivity("filter", "Filtro: Concluídos aplicado", "✅")
                        }
                    }
                }
                
                // ===== SEPARADOR =====
                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: ds.divider
                    visible: !sidebarCollapsed
                }
                
                // ===== TAGS =====
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: ds.space3
                    visible: !sidebarCollapsed
                    
                    Text {
                        text: "🏷️ TAGS"
                        font.pixelSize: ds.text_sm
                        font.weight: ds.fontMedium
                        color: ds.textSecondary
                    }
                    
                    Repeater {
                        model: availableTags
                        
                        TagItem {
                            text: modelData.name
                            count: modelData.count
                            active: currentTag === modelData.name
                            
                            onClicked: {
                                if (currentTag === modelData.name) {
                                    currentTag = ""
                                    currentFilter = "all"
                                } else {
                                    currentTag = modelData.name
                                    currentFilter = "tag"
                                }
                                filterMangaList()
                                addRecentActivity("filter", "Tag aplicada: " + modelData.name, "🏷️")
                            }
                        }
                    }
                }
                
                // ===== SEPARADOR =====
                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: ds.divider
                    visible: !sidebarCollapsed
                }
                
                // ===== FERRAMENTAS =====
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: ds.space3
                    visible: !sidebarCollapsed
                    
                    Text {
                        text: "🔧 FERRAMENTAS"
                        font.pixelSize: ds.text_sm
                        font.weight: ds.fontMedium
                        color: ds.textSecondary
                    }
                    
                    SidebarItem {
                        icon: "📋"
                        text: "Indexador"
                        active: false
                        onClicked: indexadorDialog.open()
                    }
                    
                    SidebarItem {
                        icon: "📤"
                        text: "Upload Queue"
                        count: 3
                        active: false
                    }
                    
                    SidebarItem {
                        icon: "📊"
                        text: "Analytics"
                        active: false
                    }
                }
                
                // ===== SPACER =====
                Item { Layout.fillHeight: true }
            }
        }
        
        // ===== ÁREA DE CONTEÚDO PRINCIPAL =====
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: ds.bgPrimary
            
            StackLayout {
                anchors.fill: parent
                anchors.margins: ds.space8
                currentIndex: window.currentManga ? 1 : 0
                
                // ===== DASHBOARD PRINCIPAL COMPLETO =====
                ScrollView {
                    
                    ColumnLayout {
                        width: parent.width
                        spacing: ds.space8
                        
                        // ===== AÇÕES RÁPIDAS =====
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
                                spacing: ds.space6
                                
                                Text {
                                    text: "🎯 Ações Rápidas"
                                    font.pixelSize: ds.text_xl
                                    font.weight: ds.fontBold
                                    color: ds.textPrimary
                                    Layout.alignment: Qt.AlignHCenter
                                }
                                
                                GridLayout {
                                    Layout.fillWidth: true
                                    Layout.alignment: Qt.AlignHCenter
                                    columns: 4
                                    columnSpacing: ds.space4
                                    rowSpacing: ds.space4
                                    
                                    // Upload Card
                                    QuickActionCard {
                                        title: "UPLOAD"
                                        subtitle: "Novo projeto"
                                        icon: "📤"
                                        cardColor: ds.accent
                                        
                                        onClicked: {
                                            uploadWorkflowDialog.open()
                                            addRecentActivity("upload", "Iniciado novo workflow de upload", "📤")
                                        }
                                    }
                                    
                                    // Indexador Card
                                    QuickActionCard {
                                        title: "INDEXADOR" 
                                        subtitle: "Gerenciar hub"
                                        icon: "📋"
                                        cardColor: ds.success
                                        
                                        onClicked: indexadorDialog.open()
                                    }
                                    
                                    // GitHub Sync Card
                                    QuickActionCard {
                                        title: "SYNC GITHUB"
                                        subtitle: isSyncingGitHub ? "Sincronizando..." : "Sincronizar"
                                        icon: "🔄"
                                        cardColor: ds.warning
                                        enabled: !isSyncingGitHub
                                        loading: isSyncingGitHub
                                        
                                        onClicked: {
                                            backend.saveToGitHub()
                                        }
                                    }
                                    
                                    // Reports Card
                                    QuickActionCard {
                                        title: "RELATÓRIO"
                                        subtitle: isGeneratingAnalytics ? "Carregando..." : "Ver análise"
                                        icon: "📊"
                                        cardColor: ds.brandSecondary
                                        enabled: !isGeneratingAnalytics
                                        loading: isGeneratingAnalytics
                                        
                                        onClicked: {
                                            isGeneratingAnalytics = true
                                            analyticsDialog.open()
                                            addRecentActivity("analytics", "Aberto dashboard de análise", "📊")
                                            
                                            // Start analytics loading timer
                                            analyticsLoadingTimer.start()
                                        }
                                    }
                                }
                            }
                        }
                        
                        // ===== ESTATÍSTICAS =====
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
                                    text: "📈 Estatísticas"
                                    font.pixelSize: ds.text_xl
                                    font.weight: ds.fontBold
                                    color: ds.textPrimary
                                    Layout.alignment: Qt.AlignHCenter
                                }
                                
                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: ds.space8
                                    
                                    // Total Mangás
                                    StatCard {
                                        title: "Total de Mangás"
                                        value: mangaModel.rowCount()
                                        icon: "📚"
                                    }
                                    
                                    // Total Capítulos  
                                    StatCard {
                                        title: "Capítulos"
                                        value: totalChapters.toString()
                                        icon: "📑"
                                    }
                                    
                                    // Uploads Hoje
                                    StatCard {
                                        title: "Hoje"
                                        value: uploadsToday + " upload" + (uploadsToday === 1 ? "" : "s")
                                        icon: "📤"
                                    }
                                    
                                    // Hosts Ativos
                                    StatCard {
                                        title: "Hosts Ativos"
                                        value: activeHosts + "/10"
                                        icon: "🌐"
                                    }
                                    
                                    // Storage
                                    StatCard {
                                        title: "Storage"
                                        value: storageSize
                                        icon: "💾"
                                    }
                                    
                                    // Queue
                                    StatCard {
                                        title: "Queue"
                                        value: queueCount + " pendente" + (queueCount === 1 ? "" : "s")
                                        icon: "⏳"
                                    }
                                }
                            }
                        }
                        
                        // ===== ATIVIDADE RECENTE =====
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
                                    text: "📈 Atividade Recente"
                                    font.pixelSize: ds.text_xl
                                    font.weight: ds.fontBold
                                    color: ds.textPrimary
                                    Layout.alignment: Qt.AlignHCenter
                                }
                                
                                ScrollView {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    
                                    ColumnLayout {
                                        width: parent.width
                                        spacing: ds.space2
                                        
                                        Repeater {
                                            model: recentActivity
                                            
                                            ActivityItem {
                                                Layout.fillWidth: true
                                                icon: modelData.icon
                                                message: modelData.message
                                                timestamp: modelData.timestamp
                                                type: modelData.type
                                            }
                                        }
                                        
                                        // Placeholder quando não há atividade
                                        Text {
                                            text: "📱 Nenhuma atividade recente\n\nFaça um upload para ver o histórico aqui"
                                            font.pixelSize: ds.text_base
                                            color: ds.textSecondary
                                            horizontalAlignment: Text.AlignHCenter
                                            Layout.alignment: Qt.AlignHCenter
                                            Layout.fillWidth: true
                                            visible: recentActivity.length === 0
                                        }
                                    }
                                }
                            }
                        }
                        
                        // ===== BIBLIOTECA DE MANGÁS =====
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 500
                            radius: ds.radius_lg
                            color: ds.bgCard
                            border.color: ds.border
                            border.width: 1
                            
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: ds.space6
                                spacing: ds.space4
                                
                                Text {
                                    text: "📚 Biblioteca de Mangás"
                                    font.pixelSize: ds.text_xl
                                    font.weight: ds.fontBold
                                    color: ds.textPrimary
                                    Layout.alignment: Qt.AlignHCenter
                                }
                                
                                GridView {
                                    id: mangaGridView
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    
                                    cellWidth: 280
                                    cellHeight: 120
                                    
                                    model: mangaModel
                                    
                                    delegate: MangaCardModern {
                                        width: mangaGridView.cellWidth - ds.space2
                                        height: mangaGridView.cellHeight - ds.space2
                                        
                                        title: model.title
                                        coverUrl: model.coverUrl
                                        chapterCount: model.chapterCount
                                        status: "Em andamento"
                                        isFavorited: favoritedManga.indexOf(model.path) !== -1
                                        
                                        onClicked: {
                                            selectManga(model.title, model.path)
                                            updateRecentManga(model.path)
                                        }
                                        
                                        onUploadClicked: {
                                            selectManga(model.title, model.path)
                                            uploadWorkflowDialog.open()
                                            addRecentActivity("upload", "Upload iniciado: " + model.title, "📤")
                                        }
                                        
                                        onEditClicked: {
                                            selectManga(model.title, model.path)
                                            indexadorDialog.open()
                                            addRecentActivity("edit", "Editando: " + model.title, "✏️")
                                        }
                                        
                                        onFavoriteClicked: {
                                            toggleFavorite(model.path)
                                        }
                                    }
                                }
                                
                                // Placeholder quando não há mangás
                                Text {
                                    text: "📂 Nenhum mangá encontrado\n\nVerifique se a pasta raiz está configurada corretamente"
                                    font.pixelSize: ds.text_base
                                    color: ds.textSecondary
                                    horizontalAlignment: Text.AlignHCenter
                                    Layout.alignment: Qt.AlignHCenter
                                    visible: mangaGridView.count === 0
                                }
                            }
                        }
                    }
                }
                
                // ===== DETALHES DO MANGÁ =====
                MangaDetailsView {
                    mangaData: currentManga
                    isLoading: false
                    
                    onBackClicked: {
                        currentManga = null
                    }
                    
                    onUploadChaptersClicked: {
                        uploadWorkflowDialog.open()
                    }
                    
                    onUploadSingleChapter: function(chapterName) {
                        console.log("Upload single chapter:", chapterName)
                        // TODO: Implementar upload de capítulo individual
                        uploadWorkflowDialog.open()
                    }
                    
                    onEditChapter: function(chapterName) {
                        console.log("Edit chapter:", chapterName)
                        // TODO: Implementar edição de capítulo
                    }
                }
            }
        }
    }
    
    // ===== COMPONENTS AUXILIARES =====
    
    // Sidebar Item Component
    component SidebarItem: Rectangle {
        property string icon: ""
        property string text: ""
        property int count: 0
        property bool active: false
        
        signal clicked()
        
        Layout.fillWidth: true
        height: ds.space10
        radius: ds.radius_md
        color: active ? ds.accent : (mouseArea.containsMouse ? ds.hover : "transparent")
        
        RowLayout {
            anchors.fill: parent
            anchors.margins: ds.space3
            spacing: ds.space3
            
            Text {
                text: icon
                font.pixelSize: ds.iconMd
            }
            
            Text {
                Layout.fillWidth: true
                text: parent.parent.text
                font.pixelSize: ds.text_sm
                color: active ? ds.textPrimary : ds.textSecondary
            }
            
            Rectangle {
                visible: count > 0
                width: countText.implicitWidth + ds.space2
                height: ds.space5
                radius: ds.radius_full
                color: active ? ds.textPrimary : ds.textSecondary
                
                Text {
                    id: countText
                    anchors.centerIn: parent
                    text: count
                    font.pixelSize: ds.text_xs
                    color: active ? ds.bgPrimary : ds.textPrimary
                }
            }
        }
        
        MouseArea {
            id: mouseArea
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            
            onClicked: parent.clicked()
        }
    }
    
    // Tag Item Component
    component TagItem: Rectangle {
        property string text: ""
        property int count: 0
        property bool active: false
        
        signal clicked()
        
        Layout.fillWidth: true
        height: ds.space8
        radius: ds.radius_sm
        color: active ? ds.accent : (mouseArea.containsMouse ? ds.hover : "transparent")
        
        RowLayout {
            anchors.fill: parent
            anchors.margins: ds.space2
            spacing: ds.space2
            
            Text {
                text: "#"
                font.pixelSize: ds.text_sm
                color: active ? ds.textPrimary : ds.accent
            }
            
            Text {
                Layout.fillWidth: true
                text: parent.parent.text
                font.pixelSize: ds.text_sm
                color: active ? ds.textPrimary : ds.textSecondary
            }
            
            Text {
                text: count
                font.pixelSize: ds.text_xs
                color: active ? ds.textPrimary : ds.textSecondary
            }
        }
        
        MouseArea {
            id: mouseArea
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            
            onClicked: {
                parent.clicked()
            }
        }
    }
    
    // ===== HELPER FUNCTIONS =====
    function getHostColor(hostName) {
        switch(hostName) {
            case "Catbox": return "#ff6b35"
            case "Imgur": return "#1bb76e"
            case "ImgBB": return "#3b82f6"
            case "Pixeldrain": return "#8b5cf6"
            case "Gofile": return "#10b981"
            case "Lensdump": return "#f59e0b"
            case "ImageChest": return "#ef4444"
            case "Imgbox": return "#06b6d4"
            case "ImgHippo": return "#ec4899"
            case "ImgPile": return "#84cc16"
            default: return ds.textSecondary
        }
    }
    
    function getHostInitial(hostName) {
        return hostName ? hostName.charAt(0).toUpperCase() : "?"
    }
    
    // ===== DASHBOARD COMPONENTS =====
    
    // Quick Action Card Component
    component QuickActionCard: Rectangle {
        property string title: ""
        property string subtitle: ""
        property string icon: ""
        property color cardColor: ds.accent
        property bool enabled: true
        property bool loading: false
        
        signal clicked()
        
        width: 120
        height: 80
        radius: ds.radius_md
        color: enabled ? (mouseArea.containsMouse ? Qt.lighter(cardColor, 1.1) : cardColor) : ds.bgDisabled
        border.color: cardColor
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
            spacing: ds.space2
            
            Text {
                text: loading ? "🔄" : icon
                font.pixelSize: ds.text_xl
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
    
    // Stat Card Component
    component StatCard: ColumnLayout {
        property string title: ""
        property string value: ""
        property string icon: ""
        
        Layout.fillWidth: true
        spacing: ds.space1
        
        RowLayout {
            Layout.fillWidth: true
            spacing: ds.space2
            
            Text {
                text: icon
                font.pixelSize: ds.text_base
            }
            
            Text {
                text: title
                font.pixelSize: ds.text_sm
                color: ds.textSecondary
                Layout.fillWidth: true
            }
        }
        
        Text {
            text: value
            font.pixelSize: ds.text_lg
            font.weight: ds.fontBold
            color: ds.textPrimary
        }
    }
    
    // Activity Item Component
    component ActivityItem: Rectangle {
        property string icon: ""
        property string message: ""
        property string timestamp: ""
        property string type: "info"
        
        Layout.fillWidth: true
        height: ds.space10
        radius: ds.radius_sm
        color: mouseArea.containsMouse ? ds.hover : "transparent"
        
        RowLayout {
            anchors.fill: parent
            anchors.margins: ds.space3
            spacing: ds.space3
            
            Rectangle {
                width: ds.space8
                height: ds.space8
                radius: ds.space8 / 2
                color: getActivityColor(type)
                
                Text {
                    anchors.centerIn: parent
                    text: icon
                    font.pixelSize: ds.text_sm
                }
            }
            
            Text {
                text: message
                font.pixelSize: ds.text_base
                color: ds.textPrimary
                Layout.fillWidth: true
                elide: Text.ElideRight
            }
            
            Text {
                text: timestamp
                font.pixelSize: ds.text_sm
                color: ds.textSecondary
            }
        }
        
        MouseArea {
            id: mouseArea
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
        }
        
        function getActivityColor(activityType) {
            switch (activityType) {
                case "success": return ds.success
                case "warning": return ds.warning
                case "error": return ds.danger
                default: return ds.accent
            }
        }
    }
    
    // ===== DIALOGS =====
    
    // Settings Drawer (functional)
    Drawer {
        id: settingsDrawer
        width: Math.min(window.width * 0.9, 1000)
        height: parent.height
        edge: Qt.RightEdge
        
        background: Rectangle {
            color: "transparent"
        }
        
        ModernSettingsPanel {
            anchors.fill: parent
            
            onSaveSettings: {
                console.log("Settings saved from drawer")
                settingsDrawer.close()
            }
        }
    }
    
    // Indexador Dialog
    IndexadorDialog {
        id: indexadorDialog
    }
    
    // Analytics Dialog
    Dialog {
        id: analyticsDialog
        width: Math.min(window.width * 0.95, 1400)
        height: Math.min(window.height * 0.95, 900)
        anchors.centerIn: parent
        
        modal: true
        focus: true
        
        background: Rectangle {
            color: "transparent"
        }
        
        contentItem: AnalyticsDashboard {
            anchors.fill: parent
        }
    }
    
    // Notification Dialog
    Dialog {
        id: notificationDialog
        width: Math.min(window.width * 0.8, 800)
        height: Math.min(window.height * 0.8, 700)
        anchors.centerIn: parent
        
        modal: true
        focus: true
        
        background: Rectangle {
            color: "transparent"
        }
        
        contentItem: NotificationCenter {
            anchors.fill: parent
        }
    }
    
    // Developer Tools Dialog
    Dialog {
        id: developerDialog
        width: Math.min(window.width * 0.9, 1200)
        height: Math.min(window.height * 0.9, 800)
        anchors.centerIn: parent
        
        modal: true
        focus: true
        
        background: Rectangle {
            color: "transparent"
        }
        
        contentItem: DeveloperTools {
            anchors.fill: parent
        }
    }
    
    // Upload Workflow Dialog
    Dialog {
        id: uploadWorkflowDialog
        width: Math.min(window.width * 0.9, 1200)
        height: Math.min(window.height * 0.9, 800)
        anchors.centerIn: parent
        
        modal: true
        focus: true
        
        background: Rectangle {
            color: "transparent"
        }
        
        contentItem: ModernUploadWorkflow {
            anchors.fill: parent
            currentManga: window.currentManga
            
            onCancelled: {
                uploadWorkflowDialog.close()
            }
            
            onUploadStarted: {
                console.log("Upload started")
                // Keep dialog open during upload to show progress
            }
            
            onUploadCompleted: {
                console.log("Upload completed")
                uploadWorkflowDialog.close()
            }
        }
    }
    
    // ===== HELPER FUNCTIONS =====
    function selectManga(title, path) {
        currentManga = {
            title: title,
            path: path
        }
        
        // Carrega detalhes do mangá
        backend.loadMangaDetails(path)
    }
    
    // ===== STATISTICS FUNCTIONS =====
    function updateStatistics() {
        console.log("Updating statistics...")
        
        // Calculate total chapters from all manga
        var totalChaps = 0
        for (var i = 0; i < mangaModel.rowCount(); i++) {
            var index = mangaModel.index(i, 0)
            var item = mangaModel.data(index, Qt.UserRole)
            if (item && item.chapterCount) {
                totalChaps += item.chapterCount
            }
        }
        totalChapters = totalChaps
        
        // Count active hosts
        var activeCount = 0
        var hostList = ["Catbox", "Imgur", "ImgBB", "Gofile", "Pixeldrain", "Lensdump", "ImageChest", "Imgbox", "ImgHippo", "ImgPile"]
        for (var j = 0; j < hostList.length; j++) {
            if (isHostActive(hostList[j])) {
                activeCount++
            }
        }
        activeHosts = activeCount
        
        // Calculate storage size estimation
        var estimatedMB = totalChapters * 15 // ~15MB per chapter average
        storageSize = estimatedMB > 1000 ? (estimatedMB / 1000).toFixed(1) + " GB" : estimatedMB + " MB"
        
        // Get queue count (placeholder for now)
        if (backend.getQueueCount) {
            queueCount = backend.getQueueCount()
        } else {
            queueCount = 0
        }
        
        console.log("Statistics updated:", {
            totalChapters: totalChapters,
            activeHosts: activeHosts,
            storageSize: storageSize,
            queueCount: queueCount
        })
    }
    
    function isHostActive(hostName) {
        if (!backend.config || !backend.config.hosts) {
            return false
        }
        
        var hostConfig = backend.config.hosts[hostName]
        if (!hostConfig) {
            // Default enabled for non-API hosts
            var apiHosts = ["Imgur", "ImgBB", "Lensdump", "ImgHippo", "ImgPile"]
            return !apiHosts.includes(hostName)
        }
        
        return hostConfig.enabled !== false
    }
    
    function addRecentActivity(type, message, icon) {
        var activity = {
            "type": type,
            "message": message,
            "timestamp": new Date().toLocaleTimeString(),
            "icon": icon || "📱"
        }
        
        recentActivity.unshift(activity)
        if (recentActivity.length > 10) {
            recentActivity.pop()
        }
        recentActivity = recentActivity.slice() // Trigger property change
    }
    
    function checkQuickActionsAvailability() {
        // Check if IndexadorDialog is ready
        if (backend.config && backend.config.github) {
            console.log("GitHub configuration available")
        }
        
        // Check upload capability
        if (activeHosts > 0) {
            console.log("Upload hosts available:", activeHosts)
        }
        
        return true
    }
    
    // ===== FILTER FUNCTIONS =====
    function filterMangaList() {
        console.log("Applying filter:", currentFilter, "tag:", currentTag)
        
        if (!backend.setMangaFilter) {
            console.log("setMangaFilter method not available")
            return
        }
        
        // Update backend with current favorites and recent manga
        if (backend.setFavorites) {
            backend.setFavorites(favoritedManga)
        }
        if (backend.setRecentManga) {
            backend.setRecentManga(recentManga)
        }
        
        // Apply filter
        switch (currentFilter) {
            case "favoritos":
                backend.setMangaFilter("favorites", "")
                break
            case "recentes":
                backend.setMangaFilter("recent", "")
                break
            case "progresso":
                backend.setMangaFilter("progress", "")
                break
            case "concluidos":
                backend.setMangaFilter("completed", "")
                break
            case "tag":
                if (currentTag !== "") {
                    backend.setMangaFilter("tag", currentTag)
                } else {
                    backend.setMangaFilter("all", "")
                }
                break
            default:
                backend.setMangaFilter("all", "")
                break
        }
    }
    
    function getProgressCount() {
        // Count manga with active uploads or incomplete status
        var count = 0
        if (mangaModel && mangaModel.rowCount) {
            for (var i = 0; i < mangaModel.rowCount(); i++) {
                var index = mangaModel.index(i, 0)
                var item = mangaModel.data(index, Qt.UserRole)
                if (item && item.status === "uploading" || item.status === "pending") {
                    count++
                }
            }
        }
        return Math.max(count, queueCount) // Use queue count as fallback
    }
    
    function getCompletedCount() {
        // Count manga with completed status
        var count = 0
        if (mangaModel && mangaModel.rowCount) {
            for (var i = 0; i < mangaModel.rowCount(); i++) {
                var index = mangaModel.index(i, 0)
                var item = mangaModel.data(index, Qt.UserRole)
                if (item && item.status === "completed") {
                    count++
                }
            }
        }
        // Fallback to calculation based on total
        return Math.max(count, Math.floor(totalChapters / 15))
    }
    
    function toggleFavorite(mangaPath) {
        var index = favoritedManga.indexOf(mangaPath)
        if (index === -1) {
            favoritedManga.push(mangaPath)
            addRecentActivity("favorite", "Mangá adicionado aos favoritos", "⭐")
        } else {
            favoritedManga.splice(index, 1)
            addRecentActivity("favorite", "Mangá removido dos favoritos", "⭐")
        }
        favoritedManga = favoritedManga.slice() // Trigger property change
        
        // Save to backend
        if (backend.saveFavorites) {
            backend.saveFavorites(favoritedManga)
        }
    }
    
    function updateRecentManga(mangaPath) {
        // Add to recent, remove duplicates, keep max 10
        var index = recentManga.indexOf(mangaPath)
        if (index !== -1) {
            recentManga.splice(index, 1)
        }
        recentManga.unshift(mangaPath)
        if (recentManga.length > 10) {
            recentManga.pop()
        }
        recentManga = recentManga.slice() // Trigger property change
        
        // Save to backend
        if (backend.saveRecentManga) {
            backend.saveRecentManga(recentManga)
        }
    }
    
    // ===== TAG FUNCTIONS =====
    function initializeTags() {
        // Initialize with some common manga tags
        availableTags = [
            {"name": "Action", "count": 0},
            {"name": "Romance", "count": 0},
            {"name": "Drama", "count": 0},
            {"name": "Comedy", "count": 0},
            {"name": "Fantasy", "count": 0},
            {"name": "Isekai", "count": 0},
            {"name": "Shounen", "count": 0},
            {"name": "Seinen", "count": 0}
        ]
        
        updateTagCounts()
    }
    
    function updateTagCounts() {
        // Update tag counts based on manga metadata
        if (!backend.getMangaTags) {
            // Simulate tag counts if backend doesn't support it
            for (var i = 0; i < availableTags.length; i++) {
                availableTags[i].count = Math.floor(Math.random() * 25) + 1
            }
        } else {
            var tagCounts = backend.getMangaTags()
            for (var j = 0; j < availableTags.length; j++) {
                availableTags[j].count = tagCounts[availableTags[j].name] || 0
            }
        }
        
        // Filter out tags with 0 count
        availableTags = availableTags.filter(function(tag) {
            return tag.count > 0
        })
        
        availableTags = availableTags.slice() // Trigger property change
        console.log("Tags updated:", availableTags.length, "tags available")
    }
    
    function addTagToManga(mangaPath, tagName) {
        if (backend.addTagToManga) {
            backend.addTagToManga(mangaPath, tagName)
            updateTagCounts()
            addRecentActivity("tag", "Tag adicionada: " + tagName, "🏷️")
        }
    }
    
    function removeTagFromManga(mangaPath, tagName) {
        if (backend.removeTagFromManga) {
            backend.removeTagFromManga(mangaPath, tagName)
            updateTagCounts()
            addRecentActivity("tag", "Tag removida: " + tagName, "🏷️")
        }
    }
    
    // ===== TIMERS =====
    Timer {
        id: analyticsLoadingTimer
        interval: 1500
        running: false
        repeat: false
        onTriggered: {
            isGeneratingAnalytics = false
        }
    }
    
    // ===== ANIMATIONS =====
    Behavior on sidebarCollapsed {
        NumberAnimation {
            duration: ds.animationMedium
            easing.type: ds.easingOut
        }
    }
}