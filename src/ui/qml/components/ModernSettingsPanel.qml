import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs

/**
 * ModernSettingsPanel - Painel de configurações categorizado
 * Baseado no FRONTEND_MAP_MODERN.md
 */
Rectangle {
    id: root
    
    // ===== PUBLIC PROPERTIES =====
    property int currentCategory: 0
    property bool showAdvancedIndexador: false
    property var categories: [
        "📁 Diretórios",
        "🌐 Hosts", 
        "🔧 GitHub",
        "📋 Indexador",
        "🎨 Interface",
        "🔔 Notificações"
    ]
    
    // ===== BACKEND CONNECTIONS =====
    Connections {
        target: backend
        
        function onConfigLoaded() {
            console.log("Config loaded in settings panel")
            refreshSettings()
        }
        
        function onConfigSaved() {
            console.log("Config saved successfully")
            // Show success notification
        }
        
        function onError(message) {
            console.log("Settings error:", message)
            // Show error notification
        }
    }
    
    // ===== COMPONENT INITIALIZATION =====
    Component.onCompleted: {
        refreshSettings()
    }
    
    // ===== DESIGN SYSTEM =====
    DesignSystem { id: ds }
    
    // ===== LAYOUT =====
    color: ds.bgPrimary
    
    RowLayout {
        anchors.fill: parent
        anchors.margins: ds.space8
        spacing: 0
        
        // ===== SIDEBAR CATEGORIES =====
        Rectangle {
            Layout.preferredWidth: parent.width <= ds.mobile ? Math.max(160, parent.width * 0.4) : 200
            Layout.fillHeight: true
            color: ds.bgSurface
            radius: ds.radius_lg
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: ds.space4
                spacing: ds.space2
                
                Text {
                    text: "⚙️ CONFIGURAÇÕES"
                    font.pixelSize: ds.text_lg
                    font.weight: ds.fontBold
                    color: ds.textPrimary
                    Layout.alignment: Qt.AlignHCenter
                    Layout.bottomMargin: ds.space4
                }
                
                Repeater {
                    model: categories
                    
                    Rectangle {
                        Layout.fillWidth: true
                        height: ds.space10
                        radius: ds.radius_md
                        color: currentCategory === index ? ds.accent : (categoryMouseArea.containsMouse ? ds.hover : "transparent")
                        
                        Behavior on color {
                            ColorAnimation {
                                duration: ds.animationFast
                                easing.type: ds.easingOut
                            }
                        }
                        
                        Text {
                            anchors.left: parent.left
                            anchors.leftMargin: ds.space3
                            anchors.verticalCenter: parent.verticalCenter
                            text: modelData
                            font.pixelSize: ds.text_sm
                            font.weight: ds.fontMedium
                            color: currentCategory === index ? ds.textPrimary : ds.textSecondary
                            
                            Behavior on color {
                                ColorAnimation {
                                    duration: ds.animationFast
                                    easing.type: ds.easingOut
                                }
                            }
                        }
                        
                        MouseArea {
                            id: categoryMouseArea
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            
                            onClicked: {
                                currentCategory = index
                            }
                        }
                    }
                }
                
                Item { Layout.fillHeight: true }
                
                ModernButton {
                    text: "Salvar"
                    icon: "💾"
                    variant: "primary"
                    size: "lg"
                    Layout.fillWidth: true
                    
                    onClicked: {
                        backend.saveConfig()
                        root.saveSettings()
                    }
                }
            }
        }
        
        // ===== CONTENT AREA =====
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.leftMargin: ds.space4
            color: ds.bgCard
            radius: ds.radius_lg
            border.color: ds.border
            border.width: 1
            
            StackLayout {
                anchors.fill: parent
                anchors.margins: ds.space6
                currentIndex: currentCategory
                
                // ===== DIRECTORIES SETTINGS =====
                Item {
                    ColumnLayout {
                        anchors.fill: parent
                        spacing: ds.space6
                        
                        Text {
                            text: "📁 Configuração de Diretórios"
                            font.pixelSize: ds.text_2xl
                            font.weight: ds.fontBold
                            color: ds.textPrimary
                        }
                        
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: ds.space4
                            
                            // Manga Root Folder
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: ds.space2
                                
                                Text {
                                    text: "Pasta Raiz dos Mangás"
                                    font.pixelSize: ds.text_base
                                    font.weight: ds.fontMedium
                                    color: ds.textPrimary
                                }
                                
                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: ds.space3
                                    
                                    ModernInput {
                                        id: mangaRootInput
                                        Layout.fillWidth: true
                                        placeholderText: "C:\\Users\\User\\Documents\\Manga"
                                        text: backend.config ? backend.config.mangaRootPath : ""
                                        size: "lg"
                                        
                                        onTextChanged: {
                                            if (backend.config) {
                                                backend.config.mangaRootPath = text
                                            }
                                        }
                                    }
                                    
                                    ModernButton {
                                        text: "Procurar"
                                        icon: "📂"
                                        variant: "secondary"
                                        size: "lg"
                                        
                                        onClicked: {
                                            folderDialog.title = "Selecionar Pasta Raiz dos Mangás"
                                            folderDialog.currentFolder = "file:///" + mangaRootInput.text
                                            folderDialog.open()
                                        }
                                    }
                                }
                            }
                            
                            // Output Folder
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: ds.space2
                                
                                Text {
                                    text: "Pasta de Saída (Metadados)"
                                    font.pixelSize: ds.text_base
                                    font.weight: ds.fontMedium
                                    color: ds.textPrimary
                                }
                                
                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: ds.space3
                                    
                                    ModernInput {
                                        id: outputFolderInput
                                        Layout.fillWidth: true
                                        placeholderText: "C:\\Users\\User\\Documents\\Manga_Output"
                                        text: backend.config ? backend.config.outputPath : ""
                                        size: "lg"
                                        
                                        onTextChanged: {
                                            if (backend.config) {
                                                backend.config.outputPath = text
                                            }
                                        }
                                    }
                                    
                                    ModernButton {
                                        text: "Procurar"
                                        icon: "📂"
                                        variant: "secondary"
                                        size: "lg"
                                        
                                        onClicked: {
                                            folderDialog.title = "Selecionar Pasta de Saída"
                                            folderDialog.currentFolder = "file:///" + outputFolderInput.text
                                            folderDialog.open()
                                        }
                                    }
                                }
                            }
                            
                            // Options
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: ds.space3
                                
                                Text {
                                    text: "Opções"
                                    font.pixelSize: ds.text_base
                                    font.weight: ds.fontMedium
                                    color: ds.textPrimary
                                }
                                
                                CheckBox {
                                    id: createSubfoldersCheck
                                    text: "Criar subpastas por mangá"
                                    checked: backend.config ? backend.config.createSubfolders !== false : true
                                    font.pixelSize: ds.text_sm
                                    
                                    onCheckedChanged: {
                                        if (backend.config) {
                                            backend.config.createSubfolders = checked
                                        }
                                    }
                                }
                                
                                CheckBox {
                                    id: autoBackupCheck
                                    text: "Backup automático de JSONs"
                                    checked: backend.config ? backend.config.autoBackupJsons !== false : true
                                    font.pixelSize: ds.text_sm
                                    
                                    onCheckedChanged: {
                                        if (backend.config) {
                                            backend.config.autoBackupJsons = checked
                                        }
                                    }
                                }
                                
                                CheckBox {
                                    id: autoCleanCheck
                                    text: "Limpeza automática de temporários"
                                    checked: backend.config ? backend.config.autoCleanTemp === true : false
                                    font.pixelSize: ds.text_sm
                                    
                                    onCheckedChanged: {
                                        if (backend.config) {
                                            backend.config.autoCleanTemp = checked
                                        }
                                    }
                                }
                                
                                CheckBox {
                                    id: watchChangesCheck
                                    text: "Monitorar mudanças nos diretórios"
                                    checked: backend.config ? backend.config.watchChanges === true : false
                                    font.pixelSize: ds.text_sm
                                    
                                    onCheckedChanged: {
                                        if (backend.config) {
                                            backend.config.watchChanges = checked
                                        }
                                    }
                                }
                            }
                        }
                        
                        // Directory Status and Validation
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 100
                            radius: ds.radius_md
                            color: ds.bgSurface
                            border.color: ds.border
                            border.width: 1
                            
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: ds.space4
                                spacing: ds.space2
                                
                                Text {
                                    text: "📊 Status dos Diretórios"
                                    font.pixelSize: ds.text_base
                                    font.weight: ds.fontMedium
                                    color: ds.textPrimary
                                }
                                
                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: ds.space4
                                    
                                    // Manga folder status
                                    RowLayout {
                                        spacing: ds.space2
                                        
                                        Rectangle {
                                            width: ds.space3
                                            height: ds.space3
                                            radius: ds.space3 / 2
                                            color: getMangaFolderStatus() === "valid" ? ds.success : ds.danger
                                        }
                                        
                                        Text {
                                            text: "Pasta Mangás: " + getMangaFolderStatus()
                                            font.pixelSize: ds.text_sm
                                            color: ds.textSecondary
                                        }
                                    }
                                    
                                    // Output folder status
                                    RowLayout {
                                        spacing: ds.space2
                                        
                                        Rectangle {
                                            width: ds.space3
                                            height: ds.space3
                                            radius: ds.space3 / 2
                                            color: getOutputFolderStatus() === "valid" ? ds.success : ds.warning
                                        }
                                        
                                        Text {
                                            text: "Pasta Saída: " + getOutputFolderStatus()
                                            font.pixelSize: ds.text_sm
                                            color: ds.textSecondary
                                        }
                                    }
                                }
                                
                                // Quick action buttons
                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: ds.space3
                                    
                                    ModernButton {
                                        text: "Validar Caminhos"
                                        icon: "✅"
                                        variant: "ghost"
                                        size: "sm"
                                        
                                        onClicked: {
                                            validateDirectories()
                                        }
                                    }
                                    
                                    ModernButton {
                                        text: "Aplicar Configurações"
                                        icon: "💾"
                                        variant: "secondary"
                                        size: "sm"
                                        
                                        onClicked: {
                                            applyDirectorySettings()
                                        }
                                    }
                                }
                            }
                        }
                        
                        Item { Layout.fillHeight: true }
                    }
                }
                
                // ===== HOSTS SETTINGS =====
                Item {
                    ColumnLayout {
                        anchors.fill: parent
                        spacing: ds.space6
                        
                        Text {
                            text: "🌐 Configuração de Hosts"
                            font.pixelSize: ds.text_2xl
                            font.weight: ds.fontBold
                            color: ds.textPrimary
                        }
                        
                        // Host Cards Grid
                        GridLayout {
                            Layout.fillWidth: true
                            columns: {
                            if (parent.width <= ds.mobile) return 1
                            if (parent.width <= ds.tablet) return 2
                            if (parent.width <= ds.desktop) return 3
                            return 4
                        }
                            columnSpacing: ds.space4
                            rowSpacing: ds.space4
                            
                            // Interactive Host Configuration Cards
                            Repeater {
                                model: [
                                    {"name": "Catbox", "requiresApi": false, "enabled": true, "uploads": 142, "status": "Ativo"},
                                    {"name": "Imgur", "requiresApi": true, "enabled": false, "uploads": 23, "status": "Sem Token"},
                                    {"name": "ImgBB", "requiresApi": true, "enabled": false, "uploads": 0, "status": "Desabilitado"},
                                    {"name": "Gofile", "requiresApi": false, "enabled": true, "uploads": 89, "status": "Ativo"},
                                    {"name": "Pixeldrain", "requiresApi": false, "enabled": true, "uploads": 34, "status": "Ativo"},
                                    {"name": "Lensdump", "requiresApi": true, "enabled": false, "uploads": 67, "status": "Sem Token"},
                                    {"name": "ImageChest", "requiresApi": false, "enabled": true, "uploads": 12, "status": "Ativo"},
                                    {"name": "Imgbox", "requiresApi": false, "enabled": true, "uploads": 56, "status": "Ativo"},
                                    {"name": "ImgHippo", "requiresApi": true, "enabled": false, "uploads": 8, "status": "Sem Token"},
                                    {"name": "ImgPile", "requiresApi": true, "enabled": false, "uploads": 3, "status": "Sem Token"}
                                ]
                                
                                InteractiveHostCard {
                                    hostName: modelData.name
                                    hostIcon: getHostIcon(modelData.name)
                                    hostColor: getHostColor(modelData.name)
                                    isActive: getHostEnabledStatus(modelData.name)
                                    uploadCount: modelData.uploads
                                    requiresApiKey: modelData.requiresApi
                                    status: getHostConfigStatus(modelData.name)
                                    
                                    onConfigClicked: {
                                        openHostConfigDialog(modelData.name)
                                    }
                                    
                                    onToggleEnabled: {
                                        toggleHost(modelData.name, enabled)
                                    }
                                }
                            }
                        }
                        
                        // Statistics
                        Rectangle {
                            Layout.fillWidth: true
                            height: ds.space12
                            radius: ds.radius_md
                            color: ds.bgSurface
                            border.color: ds.border
                            border.width: 1
                            
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: ds.space4
                                spacing: ds.space2
                                
                                Text {
                                    text: "📊 Estatísticas Globais"
                                    font.pixelSize: ds.text_lg
                                    font.weight: ds.fontMedium
                                    color: ds.textPrimary
                                }
                                
                                Text {
                                    text: "Total de uploads: 646 • Hosts ativos: 8/10 • Taxa de sucesso: 97%"
                                    font.pixelSize: ds.text_sm
                                    color: ds.textSecondary
                                }
                            }
                        }
                        
                        Item { Layout.fillHeight: true }
                    }
                }
                
                // ===== GITHUB SETTINGS =====
                Item {
                    ColumnLayout {
                        anchors.fill: parent
                        spacing: ds.space6
                        
                        Text {
                            text: "🔧 Configuração do GitHub"
                            font.pixelSize: ds.text_2xl
                            font.weight: ds.fontBold
                            color: ds.textPrimary
                        }
                        
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: ds.space4
                            
                            // Repository URL
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: ds.space2
                                
                                Text {
                                    text: "URL do Repositório"
                                    font.pixelSize: ds.text_base
                                    font.weight: ds.fontMedium
                                    color: ds.textPrimary
                                }
                                
                                ModernInput {
                                    id: githubRepoInput
                                    Layout.fillWidth: true
                                    placeholderText: "https://github.com/username/repo"
                                    text: backend.config ? backend.config.githubRepo : ""
                                    size: "lg"
                                    
                                    onTextChanged: {
                                        if (backend.config) {
                                            backend.config.githubRepo = text
                                        }
                                    }
                                }
                            }
                            
                            // Access Token
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: ds.space2
                                
                                Text {
                                    text: "Token de Acesso"
                                    font.pixelSize: ds.text_base
                                    font.weight: ds.fontMedium
                                    color: ds.textPrimary
                                }
                                
                                ModernInput {
                                    id: githubTokenInput
                                    Layout.fillWidth: true
                                    placeholderText: "ghp_xxxxxxxxxxxxxxxxxxxx"
                                    text: backend.config ? backend.config.githubToken : ""
                                    size: "lg"
                                    echoMode: TextInput.Password
                                    
                                    onTextChanged: {
                                        if (backend.config) {
                                            backend.config.githubToken = text
                                        }
                                    }
                                }
                            }
                            
                            // Test Connection
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: ds.space3
                                
                                ModernButton {
                                    text: "Testar Conexão"
                                    icon: "🧪"
                                    variant: "secondary"
                                    size: "lg"
                                    
                                    onClicked: {
                                        backend.testGitHubConnection()
                                    }
                                }
                                
                                Rectangle {
                                    width: ds.space3
                                    height: ds.space3
                                    radius: ds.space3 / 2
                                    color: ds.success
                                }
                                
                                Text {
                                    text: "Conexão estabelecida"
                                    font.pixelSize: ds.text_sm
                                    color: ds.success
                                }
                            }
                        }
                        
                        Item { Layout.fillHeight: true }
                    }
                }
                
                // ===== INDEXADOR SETTINGS =====
                Item {
                    ColumnLayout {
                        anchors.fill: parent
                        spacing: ds.space6
                        
                        Text {
                            text: "📋 Configuração do Indexador"
                            font.pixelSize: ds.text_2xl
                            font.weight: ds.fontBold
                            color: ds.textPrimary
                        }
                        
                        // Quick Settings Overview
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 120
                            radius: ds.radius_md
                            color: ds.bgSurface
                            border.color: ds.border
                            border.width: 1
                            
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: ds.space4
                                spacing: ds.space3
                                
                                Text {
                                    text: "📋 Resumo do Indexador"
                                    font.pixelSize: ds.text_lg
                                    font.weight: ds.fontMedium
                                    color: ds.textPrimary
                                }
                                
                                GridLayout {
                                    Layout.fillWidth: true
                                    columns: parent.width <= ds.mobile ? 1 : 2
                                    columnSpacing: ds.space6
                                    rowSpacing: ds.space2
                                    
                                    Text {
                                        text: "👥 Grupo: Meu Scan Group"
                                        font.pixelSize: ds.text_sm
                                        color: ds.textSecondary
                                    }
                                    
                                    Text {
                                        text: "🌐 CDN: JSDelivr Configurado"
                                        font.pixelSize: ds.text_sm
                                        color: ds.success
                                    }
                                    
                                    Text {
                                        text: "📚 Séries: 12 mangás indexados"
                                        font.pixelSize: ds.text_sm
                                        color: ds.textSecondary
                                    }
                                    
                                    Text {
                                        text: "🔄 Auto-indexação: Ativada"
                                        font.pixelSize: ds.text_sm
                                        color: ds.success
                                    }
                                }
                            }
                        }
                        
                        // Essential Options
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: ds.space3
                            
                            Text {
                                text: "⚙️ Configurações Essenciais"
                                font.pixelSize: ds.text_base
                                font.weight: ds.fontMedium
                                color: ds.textPrimary
                            }
                            
                            CheckBox {
                                text: "Atualizar index.json automaticamente após upload"
                                checked: true
                                font.pixelSize: ds.text_sm
                            }
                            
                            CheckBox {
                                text: "Gerar reader.json para cada mangá"
                                checked: true
                                font.pixelSize: ds.text_sm
                            }
                            
                            CheckBox {
                                text: "Commit automático no GitHub"
                                checked: false
                                font.pixelSize: ds.text_sm
                            }
                        }
                        
                        // Expandable Advanced Configuration
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: ds.space4
                            
                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredHeight: showAdvancedIndexador ? 600 : 60
                                radius: ds.radius_md
                                color: ds.bgSurface
                                border.color: ds.border
                                border.width: 1
                                clip: true
                                
                                Behavior on Layout.preferredHeight {
                                    NumberAnimation {
                                        duration: ds.animationNormal
                                        easing.type: ds.easingOut
                                    }
                                }
                                
                                ColumnLayout {
                                    anchors.fill: parent
                                    anchors.margins: ds.space4
                                    spacing: ds.space4
                                    
                                    // Header with toggle
                                    RowLayout {
                                        Layout.fillWidth: true
                                        spacing: ds.space3
                                        
                                        Text {
                                            text: "🔧 Configuração Avançada do Indexador"
                                            font.pixelSize: ds.text_base
                                            font.weight: ds.fontMedium
                                            color: ds.textPrimary
                                            Layout.fillWidth: true
                                        }
                                        
                                        ModernButton {
                                            text: showAdvancedIndexador ? "🔼 Recolher" : "🔽 Expandir"
                                            variant: "ghost"
                                            size: "sm"
                                            
                                            onClicked: {
                                                showAdvancedIndexador = !showAdvancedIndexador
                                            }
                                        }
                                    }
                                    
                                    // Advanced Settings (embedded content)
                                    ScrollView {
                                        Layout.fillWidth: true
                                        Layout.fillHeight: true
                                        visible: showAdvancedIndexador
                                        
                                        ColumnLayout {
                                            width: parent.width - 20
                                            spacing: ds.space4
                                            
                                            Text {
                                                text: "⚙️ Configurações Avançadas do Indexador"
                                                font.pixelSize: ds.text_lg
                                                font.weight: ds.fontBold
                                                color: ds.textPrimary
                                            }
                                            
                                            // Group Configuration
                                            ColumnLayout {
                                                Layout.fillWidth: true
                                                spacing: ds.space2
                                                
                                                Text {
                                                    text: "Nome do Grupo"
                                                    font.pixelSize: ds.text_base
                                                    font.weight: ds.fontMedium
                                                    color: ds.textPrimary
                                                }
                                                
                                                ModernInput {
                                                    Layout.fillWidth: true
                                                    placeholderText: "Meu Scan Group"
                                                    size: "lg"
                                                }
                                            }
                                            
                                            // CDN Configuration
                                            ColumnLayout {
                                                Layout.fillWidth: true
                                                spacing: ds.space2
                                                
                                                Text {
                                                    text: "Base URL do CDN"
                                                    font.pixelSize: ds.text_base
                                                    font.weight: ds.fontMedium
                                                    color: ds.textPrimary
                                                }
                                                
                                                ModernInput {
                                                    Layout.fillWidth: true
                                                    placeholderText: "https://cdn.jsdelivr.net/gh/user/repo@main/"
                                                    size: "lg"
                                                }
                                            }
                                            
                                            // Auto-indexing options
                                            ColumnLayout {
                                                Layout.fillWidth: true
                                                spacing: ds.space3
                                                
                                                Text {
                                                    text: "Opções de Auto-indexação"
                                                    font.pixelSize: ds.text_base
                                                    font.weight: ds.fontMedium
                                                    color: ds.textPrimary
                                                }
                                                
                                                CheckBox {
                                                    text: "Atualizar metadados de capítulos automaticamente"
                                                    checked: true
                                                    font.pixelSize: ds.text_sm
                                                }
                                                
                                                CheckBox {
                                                    text: "Incluir estatísticas de upload nos JSONs"
                                                    checked: false
                                                    font.pixelSize: ds.text_sm
                                                }
                                                
                                                CheckBox {
                                                    text: "Gerar thumbnails automáticos"
                                                    checked: true
                                                    font.pixelSize: ds.text_sm
                                                }
                                            }
                                            
                                            Item { Layout.fillHeight: true }
                                        }
                                    }
                                }
                            }
                            
                            // Quick Actions
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: ds.space3
                                
                                ModernButton {
                                    text: "Regenerar Índices"
                                    icon: "🔄"
                                    variant: "secondary"
                                    size: "md"
                                    
                                    onClicked: {
                                        backend.regenerateIndexes()
                                    }
                                }
                                
                                ModernButton {
                                    text: "Validar JSONs"
                                    icon: "✅"
                                    variant: "ghost"
                                    size: "md"
                                    
                                    onClicked: {
                                        backend.validateJsonFiles()
                                    }
                                }
                                
                                ModernButton {
                                    text: "Exportar Configuração"
                                    icon: "📥"
                                    variant: "ghost"
                                    size: "md"
                                    
                                    onClicked: {
                                        exportConfigDialog.open()
                                    }
                                }
                            }
                        }
                        
                        Item { Layout.fillHeight: true }
                    }
                }
                
                // ===== INTERFACE SETTINGS =====
                Item {
                    ColumnLayout {
                        anchors.fill: parent
                        spacing: ds.space6
                        
                        Text {
                            text: "🎨 Configuração da Interface"
                            font.pixelSize: ds.text_2xl
                            font.weight: ds.fontBold
                            color: ds.textPrimary
                        }
                        
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: ds.space4
                            
                            // Theme Selection
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: ds.space2
                                
                                Text {
                                    text: "Tema"
                                    font.pixelSize: ds.text_base
                                    font.weight: ds.fontMedium
                                    color: ds.textPrimary
                                }
                                
                                RowLayout {
                                    spacing: ds.space3
                                    
                                    RadioButton {
                                        text: "Escuro"
                                        checked: true
                                        font.pixelSize: ds.text_sm
                                        }
                                    
                                    RadioButton {
                                        text: "Claro"
                                        font.pixelSize: ds.text_sm
                                        }
                                    
                                    RadioButton {
                                        text: "Sistema"
                                        font.pixelSize: ds.text_sm
                                        }
                                }
                            }
                            
                            // Language Selection
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: ds.space2
                                
                                Text {
                                    text: "Idioma"
                                    font.pixelSize: ds.text_base
                                    font.weight: ds.fontMedium
                                    color: ds.textPrimary
                                }
                                
                                ModernDropdown {
                                    Layout.preferredWidth: 200
                                    model: ["Português (Brasil)", "English", "Español"]
                                    currentIndex: 0
                                    size: "lg"
                                }
                            }
                        }
                        
                        Item { Layout.fillHeight: true }
                    }
                }
                
                // ===== NOTIFICATIONS SETTINGS =====
                Item {
                    ColumnLayout {
                        anchors.fill: parent
                        spacing: ds.space6
                        
                        Text {
                            text: "🔔 Configuração de Notificações"
                            font.pixelSize: ds.text_2xl
                            font.weight: ds.fontBold
                            color: ds.textPrimary
                        }
                        
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: ds.space4
                            
                            Text {
                                text: "Tipos de Notificação"
                                font.pixelSize: ds.text_base
                                font.weight: ds.fontMedium
                                color: ds.textPrimary
                            }
                            
                            CheckBox {
                                text: "Uploads concluídos"
                                checked: true
                                font.pixelSize: ds.text_sm
                            }
                            
                            CheckBox {
                                text: "Erros críticos"
                                checked: true
                                font.pixelSize: ds.text_sm
                            }
                            
                            CheckBox {
                                text: "Updates do GitHub"
                                checked: true
                                font.pixelSize: ds.text_sm
                            }
                            
                            CheckBox {
                                text: "Avisos de CDN"
                                checked: false
                                font.pixelSize: ds.text_sm
                            }
                            
                            CheckBox {
                                text: "Estatísticas"
                                checked: false
                                font.pixelSize: ds.text_sm
                            }
                            
                            CheckBox {
                                text: "Notificações push"
                                checked: false
                                font.pixelSize: ds.text_sm
                            }
                        }
                        
                        Item { Layout.fillHeight: true }
                    }
                }
            }
        }
    }
    
    // ===== INTERACTIVE HOST CARD COMPONENT =====
    component InteractiveHostCard: Rectangle {
        property string hostName: ""
        property string hostIcon: ""
        property string hostColor: ""
        property bool isActive: false
        property int uploadCount: 0
        property string status: ""
        property bool requiresApiKey: false
        
        signal configClicked()
        signal toggleEnabled(bool enabled)
        
        width: 200
        height: 140
        radius: ds.radius_md
        color: ds.bgSurface
        border.color: isActive ? hostColor : ds.border
        border.width: isActive ? 2 : 1
        
        // Hover effect
        MouseArea {
            id: hoverArea
            anchors.fill: parent
            hoverEnabled: true
            
            Rectangle {
                anchors.fill: parent
                radius: parent.parent.radius
                color: Qt.rgba(1, 1, 1, 0.1)
                visible: hoverArea.containsMouse
            }
        }
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: ds.space3
            spacing: ds.space2
            
            // Header with toggle
            RowLayout {
                Layout.fillWidth: true
                spacing: ds.space2
                
                // Status indicator
                Rectangle {
                    width: ds.space4
                    height: ds.space4
                    radius: ds.space4 / 2
                    color: {
                        if (isActive) return ds.success
                        if (status === "Sem Token") return ds.warning
                        return ds.danger
                    }
                }
                
                Text {
                    text: hostName
                    font.pixelSize: ds.text_base
                    font.weight: ds.fontBold
                    color: ds.textPrimary
                }
                
                Item { Layout.fillWidth: true }
                
                // Host icon with color
                Text {
                    text: hostIcon
                    font.pixelSize: ds.text_lg
                    color: hostColor
                }
            }
            
            // Status and API key requirement
            RowLayout {
                Layout.fillWidth: true
                spacing: ds.space2
                
                Text {
                    text: status
                    font.pixelSize: ds.text_sm
                    color: {
                        if (isActive) return ds.success
                        if (status === "Sem Token") return ds.warning
                        return ds.danger
                    }
                    font.weight: ds.fontMedium
                }
                
                Item { Layout.fillWidth: true }
                
                Text {
                    text: requiresApiKey ? "🔑 API" : "🆓 Grátis"
                    font.pixelSize: ds.text_xs
                    color: ds.textSecondary
                }
            }
            
            // Upload count
            Text {
                text: uploadCount + " uploads realizados"
                font.pixelSize: ds.text_sm
                color: ds.textSecondary
            }
            
            Item { Layout.fillHeight: true }
            
            // Action buttons
            RowLayout {
                Layout.fillWidth: true
                spacing: ds.space2
                
                // Toggle button
                ModernButton {
                    text: isActive ? "Desativar" : "Ativar"
                    icon: isActive ? "⏸️" : "▶️"
                    variant: isActive ? "danger" : "success"
                    size: "sm"
                    Layout.fillWidth: true
                    
                    onClicked: {
                        toggleEnabled(!isActive)
                    }
                }
                
                // Config button
                ModernButton {
                    text: "Config"
                    icon: "⚙️"
                    variant: "ghost"
                    size: "sm"
                    iconOnly: true
                    
                    onClicked: {
                        configClicked()
                    }
                }
            }
        }
    }
    
    // ===== DIALOGS =====
    FolderDialog {
        id: folderDialog
        title: "Selecionar Pasta"
        
        onAccepted: {
            var path = folderDialog.selectedFolder.toString()
            if (path.startsWith("file:///")) {
                path = path.substring(8) // Remove file:/// prefix
            }
            
            if (folderDialog.title.includes("Raiz")) {
                mangaRootInput.text = path
            } else {
                outputFolderInput.text = path
            }
        }
    }
    
    // ===== HOST CONFIGURATION DIALOG =====
    Dialog {
        id: hostConfigDialog
        width: Math.min(window.width * 0.8, 500)
        height: Math.min(window.height * 0.7, 400)
        anchors.centerIn: parent
        
        property string hostName: ""
        property bool requiresApiKey: false
        
        // Access to dialog components
        property alias apiKeyInput: apiKeyInput
        property alias rateLimitSpinBox: rateLimitSpinBox  
        property alias workersSpinBox: workersSpinBox
        
        modal: true
        focus: true
        
        background: Rectangle {
            color: ds.bgSurface
            radius: ds.radius_lg
        }
        
        contentItem: ColumnLayout {
            anchors.fill: parent
            anchors.margins: ds.space6
            spacing: ds.space4
            
            // Header
            RowLayout {
                Layout.fillWidth: true
                spacing: ds.space3
                
                Text {
                    text: getHostIcon(hostConfigDialog.hostName)
                    font.pixelSize: ds.text_2xl
                    color: getHostColor(hostConfigDialog.hostName)
                }
                
                Text {
                    text: "CONFIGURAR " + hostConfigDialog.hostName.toUpperCase()
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
                        hostConfigDialog.close()
                    }
                }
            }
            
            // Configuration options
            ColumnLayout {
                Layout.fillWidth: true
                spacing: ds.space4
                
                // API Key configuration (if required)
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: ds.space2
                    visible: hostConfigDialog.requiresApiKey
                    
                    Text {
                        text: "🔑 Chave da API"
                        font.pixelSize: ds.text_base
                        font.weight: ds.fontMedium
                        color: ds.textPrimary
                    }
                    
                    ModernInput {
                        id: apiKeyInput
                        Layout.fillWidth: true
                        placeholderText: "Cole sua chave da API aqui..."
                        echoMode: TextInput.Password
                        size: "lg"
                        
                        // Visual feedback for API key validation
                        property bool hasValidKey: text.trim().length > 0
                        
                        Rectangle {
                            anchors.right: parent.right
                            anchors.rightMargin: ds.space2
                            anchors.verticalCenter: parent.verticalCenter
                            width: ds.space4
                            height: ds.space4
                            radius: ds.space2
                            color: parent.hasValidKey ? ds.success : ds.warning
                            visible: parent.text.length > 0
                            
                            Text {
                                anchors.centerIn: parent
                                text: parent.parent.hasValidKey ? "✓" : "!"
                                font.pixelSize: ds.text_xs
                                color: ds.textPrimary
                                font.weight: ds.fontBold
                            }
                        }
                    }
                    
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: ds.space3
                        
                        Text {
                            text: "⚠️ Mantenha sua chave da API segura. Ela será criptografada localmente."
                            font.pixelSize: ds.text_xs
                            color: ds.warning
                            Layout.fillWidth: true
                            wrapMode: Text.WordWrap
                        }
                        
                        ModernButton {
                            text: apiKeyInput.echoMode === TextInput.Password ? "👁️ Mostrar" : "🙈 Ocultar"
                            variant: "ghost"
                            size: "sm"
                            
                            onClicked: {
                                apiKeyInput.echoMode = apiKeyInput.echoMode === TextInput.Password ? 
                                                     TextInput.Normal : TextInput.Password
                            }
                        }
                    }
                }
                
                // Rate limiting
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: ds.space2
                    
                    Text {
                        text: "⏱️ Rate Limiting"
                        font.pixelSize: ds.text_base
                        font.weight: ds.fontMedium
                        color: ds.textPrimary
                    }
                    
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: ds.space3
                        
                        Text {
                            text: "Delay entre uploads:"
                            font.pixelSize: ds.text_sm
                            color: ds.textSecondary
                        }
                        
                        SpinBox {
                            id: rateLimitSpinBox
                            from: 1
                            to: 10
                            value: 2
                            suffix: "s"
                        }
                    }
                }
                
                // Workers
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: ds.space2
                    
                    Text {
                        text: "👥 Workers Simultâneos"
                        font.pixelSize: ds.text_base
                        font.weight: ds.fontMedium
                        color: ds.textPrimary
                    }
                    
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: ds.space3
                        
                        Text {
                            text: "Uploads paralelos:"
                            font.pixelSize: ds.text_sm
                            color: ds.textSecondary
                        }
                        
                        SpinBox {
                            id: workersSpinBox
                            from: 1
                            to: 10
                            value: 3
                        }
                    }
                }
                
                // Test connection
                RowLayout {
                    Layout.fillWidth: true
                    spacing: ds.space3
                    
                    ModernButton {
                        text: "Testar Conexão"
                        icon: "🧪"
                        variant: "secondary"
                        size: "md"
                        
                        onClicked: {
                            testHostConnection()
                        }
                    }
                    
                    Rectangle {
                        width: ds.space3
                        height: ds.space3
                        radius: ds.space3 / 2
                        color: ds.success
                        visible: false // TODO: Show based on test result
                    }
                    
                    Text {
                        text: "Conexão OK"
                        font.pixelSize: ds.text_sm
                        color: ds.success
                        visible: false // TODO: Show based on test result
                    }
                }
            }
            
            Item { Layout.fillHeight: true }
            
            // Action buttons
            RowLayout {
                Layout.fillWidth: true
                spacing: ds.space4
                
                ModernButton {
                    text: "Cancelar"
                    variant: "secondary"
                    size: "lg"
                    Layout.fillWidth: true
                    
                    onClicked: {
                        hostConfigDialog.close()
                    }
                }
                
                ModernButton {
                    text: "Salvar"
                    icon: "💾"
                    variant: "primary"
                    size: "lg"
                    Layout.fillWidth: true
                    
                    onClicked: {
                        saveHostConfiguration()
                    }
                }
            }
        }
        
        function testHostConnection() {
            console.log("Testing connection for:", hostConfigDialog.hostName)
            
            var config = {
                "apiKey": apiKeyInput.text,
                "rateLimit": rateLimitSpinBox.value,
                "workers": workersSpinBox.value
            }
            
            if (backend.testHostConnection) {
                backend.testHostConnection(hostConfigDialog.hostName, config)
            }
        }
        
        function saveHostConfiguration() {
            console.log("Saving configuration for:", hostConfigDialog.hostName)
            
            // Prepare host configuration
            var hostConfig = {
                "enabled": true,
                "rate_limit": rateLimitSpinBox.value,
                "max_workers": workersSpinBox.value
            }
            
            // Add API key if required
            if (hostConfigDialog.requiresApiKey) {
                hostConfig.api_key = apiKeyInput.text.trim()
            }
            
            // Save to backend config
            if (!backend.config.hosts) {
                backend.config.hosts = {}
            }
            backend.config.hosts[hostConfigDialog.hostName] = hostConfig
            
            // Call backend save
            backend.saveConfig()
            
            console.log("Host configuration saved:", hostConfigDialog.hostName, hostConfig)
            hostConfigDialog.close()
        }
    }
    
    // ===== ADDITIONAL DIALOGS =====
    FileDialog {
        id: exportConfigDialog
        title: "Exportar Configuração"
        fileMode: FileDialog.SaveFile
        nameFilters: ["JSON files (*.json)", "All files (*)"]
        
        onAccepted: {
            backend.exportConfiguration(selectedFile)
        }
    }
    
    // ===== HELPER FUNCTIONS =====
    function refreshSettings() {
        // Force refresh of all input bindings
        if (backend.config) {
            mangaRootInput.text = backend.config.mangaRootPath || ""
            outputFolderInput.text = backend.config.outputPath || ""
            githubRepoInput.text = backend.config.githubRepo || ""
            githubTokenInput.text = backend.config.githubToken || ""
        }
    }
    
    function getHostIcon(hostName) {
        switch(hostName) {
            case "Catbox": return "C"
            case "Imgur": return "I"
            case "ImgBB": return "📦"
            case "Gofile": return "G"
            case "Pixeldrain": return "P"
            case "Lensdump": return "L"
            case "ImageChest": return "📷"
            case "Imgbox": return "📁"
            case "ImgHippo": return "🦛"
            case "ImgPile": return "📚"
            default: return "?"
        }
    }
    
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
    
    function openHostConfig(hostName) {
        console.log("Opening config for host:", hostName)
        // TODO: Open host-specific configuration dialog
        backend.openHostConfiguration(hostName)
    }
    
    // ===== DIRECTORY VALIDATION FUNCTIONS =====
    function getMangaFolderStatus() {
        var path = mangaRootInput.text
        if (!path || path.trim() === "") return "não configurado"
        
        // Call backend to validate path
        if (backend.validatePath) {
            return backend.validatePath(path) ? "válido" : "inválido"
        }
        return "não verificado"
    }
    
    function getOutputFolderStatus() {
        var path = outputFolderInput.text
        if (!path || path.trim() === "") return "não configurado"
        
        // Call backend to validate path
        if (backend.validatePath) {
            return backend.validatePath(path) ? "válido" : "inválido"
        }
        return "não verificado"
    }
    
    function validateDirectories() {
        console.log("Validating directories...")
        
        var mangaPath = mangaRootInput.text
        var outputPath = outputFolderInput.text
        
        if (backend.validateDirectories) {
            var result = backend.validateDirectories(mangaPath, outputPath)
            console.log("Directory validation result:", result)
        }
        
        // Refresh the UI to show updated status
        refreshSettings()
    }
    
    function applyDirectorySettings() {
        console.log("Applying directory settings...")
        
        // Save current configuration
        backend.saveConfig()
        
        // Refresh manga list with new root path
        if (backend.refreshMangaList) {
            backend.refreshMangaList()
        }
        
        console.log("Directory settings applied successfully")
    }
    
    // ===== HOST CONFIGURATION FUNCTIONS =====
    function openHostConfigDialog(hostName) {
        console.log("Opening host configuration dialog for:", hostName)
        
        // Set the host configuration dialog properties
        hostConfigDialog.hostName = hostName
        hostConfigDialog.requiresApiKey = getHostRequiresApi(hostName)
        
        // Load current host configuration from backend
        loadHostConfiguration(hostName)
        
        hostConfigDialog.open()
    }
    
    function toggleHost(hostName, enabled) {
        console.log("Toggling host:", hostName, "enabled:", enabled)
        
        // Ensure hosts config exists
        if (!backend.config.hosts) {
            backend.config.hosts = {}
        }
        
        // Create host config if it doesn't exist
        if (!backend.config.hosts[hostName]) {
            backend.config.hosts[hostName] = {
                "enabled": enabled,
                "rate_limit": 2,
                "max_workers": 3
            }
        } else {
            // Update enabled status
            backend.config.hosts[hostName].enabled = enabled
        }
        
        // Save configuration
        backend.saveConfig()
        
        console.log("Host", hostName, enabled ? "enabled" : "disabled")
    }
    
    function getHostRequiresApi(hostName) {
        var apiHosts = ["Imgur", "ImgBB", "Lensdump", "ImgHippo", "ImgPile"]
        return apiHosts.includes(hostName)
    }
    
    function getHostEnabledStatus(hostName) {
        if (backend.config && backend.config.hosts && backend.config.hosts[hostName]) {
            return backend.config.hosts[hostName].enabled !== false
        }
        // Default enabled status for hosts that don't require API
        return !getHostRequiresApi(hostName)
    }
    
    function getHostConfigStatus(hostName) {
        if (!getHostRequiresApi(hostName)) {
            return getHostEnabledStatus(hostName) ? "Ativo" : "Desabilitado"
        }
        
        // For API hosts, check if API key is configured
        if (backend.config && backend.config.hosts && backend.config.hosts[hostName]) {
            var hostConfig = backend.config.hosts[hostName]
            if (hostConfig.api_key && hostConfig.api_key.trim() !== "") {
                return hostConfig.enabled !== false ? "Ativo" : "Configurado (Inativo)"
            }
        }
        
        return "Sem Token"
    }
    
    function loadHostConfiguration(hostName) {
        console.log("Loading configuration for host:", hostName)
        
        // Get current host config from backend
        var hostConfig = {}
        if (backend.config && backend.config.hosts && backend.config.hosts[hostName]) {
            hostConfig = backend.config.hosts[hostName]
        }
        
        // Populate dialog fields with current values
        if (hostConfigDialog.apiKeyInput) {
            hostConfigDialog.apiKeyInput.text = hostConfig.api_key || ""
        }
        if (hostConfigDialog.rateLimitSpinBox) {
            hostConfigDialog.rateLimitSpinBox.value = hostConfig.rate_limit || 2
        }
        if (hostConfigDialog.workersSpinBox) {
            hostConfigDialog.workersSpinBox.value = hostConfig.max_workers || 3
        }
    }
    
    // ===== SIGNALS =====
    signal saveSettings()
    signal openIndexadorDialog()
}