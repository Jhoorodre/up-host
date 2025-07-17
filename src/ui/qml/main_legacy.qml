import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls.Material 2.15
import QtQuick.Dialogs
import Qt.labs.platform 1.1 as Platform
import "components"

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
    
    property var currentManga: null
    property var selectedChapters: []
    property bool isProcessing: false
    property bool indexadorButtonHovered: false
    
    Component.onCompleted: {
        backend.loadConfig()
        backend.refreshMangaList()
    }
    
    // Connect cookie test result signal
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
    }
    
    header: Rectangle {
        height: ds.headerHeight
        color: ds.bgSurface
        
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
                
                Text {
                    text: "📚"
                    font.pixelSize: ds.text_2xl
                }
                
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
                
                onInputTextChanged: {
                    backend.filterMangaList(text)
                }
            }
            
            Item { Layout.fillWidth: true }
            
            // ===== AÇÕES RÁPIDAS =====
            RowLayout {
                spacing: ds.space3
                
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
            
                // Host atual
                Rectangle {
                    Layout.preferredWidth: 160
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
                            color: getHostColor(backend.availableHosts && backend.selectedHostIndex >= 0 ? backend.availableHosts[backend.selectedHostIndex] : "")
                            
                            Text {
                                anchors.centerIn: parent
                                text: getHostInitial(backend.availableHosts && backend.selectedHostIndex >= 0 ? backend.availableHosts[backend.selectedHostIndex] : "")
                                font.pixelSize: ds.text_xs
                                font.weight: ds.fontBold
                                color: ds.textPrimary
                            }
                        }
                        
                        Text {
                            text: "HOST:"
                            font.pixelSize: ds.text_xs
                            font.weight: ds.fontMedium
                            color: ds.textSecondary
                        }
                        
                        ComboBox {
                            id: hostSelector
                            model: backend.availableHosts
                            enabled: !isProcessing
                            Layout.fillWidth: true
                            
                            Component.onCompleted: {
                                currentIndex = backend.selectedHostIndex
                            }
                            
                            Connections {
                                target: backend
                                function onSelectedHostIndexChanged() {
                                    if (hostSelector.currentIndex !== backend.selectedHostIndex) {
                                        hostSelector.currentIndex = backend.selectedHostIndex
                                    }
                                }
                            }
                            
                            onCurrentTextChanged: {
                                if (currentText && currentText !== "") {
                                    backend.setHost(currentText)
                                }
                            }
                            
                            background: Rectangle {
                                color: "transparent"
                            }
                            
                            contentItem: Text {
                                text: hostSelector.currentText
                                font.pixelSize: ds.text_sm
                                font.weight: ds.fontMedium
                                color: ds.textPrimary
                                verticalAlignment: Text.AlignVCenter
                            }
                        }
                    }
                }
            
                // Configurações
                ModernButton {
                    text: "Configurações"
                    icon: "⚙️"
                    variant: "ghost"
                    size: "sm"
                    tooltip: "Abrir configurações"
                    enabled: !isProcessing
                    
                    onClicked: {
                        settingsDrawer.open()
                    }
                }
            }
        }
    }
    
    RowLayout {
        anchors.fill: parent
        anchors.margins: 0
        spacing: 0
        
        // Manga Library Panel
        Rectangle {
            Layout.preferredWidth: ds.sidebarWidth
            Layout.fillHeight: true
            color: ds.bgSurface
            
            Rectangle {
                anchors.right: parent.right
                width: 1
                height: parent.height
                color: ds.divider
            }
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: ds.space5
                spacing: ds.space4
                
                RowLayout {
                    Layout.fillWidth: true
                    spacing: ds.space3
                    
                    Text {
                        text: "📂"
                        font.pixelSize: ds.text_lg
                    }
                    
                    Text {
                        text: "BIBLIOTECA"
                        font.pixelSize: ds.text_sm
                        font.weight: ds.fontMedium
                        font.letterSpacing: 1
                        color: ds.textSecondary
                    }
                }
                
                ModernInput {
                    Layout.fillWidth: true
                    placeholderText: "Buscar..."
                    leftIcon: "🔍"
                    size: "sm"
                    clearable: true
                    
                    onInputTextChanged: {
                        backend.filterMangaList(text)
                    }
                }
                
                ScrollView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    
                    ListView {
                        id: mangaListView
                        model: mangaModel
                        spacing: ds.space2
                        delegate: MangaCardModern {
                            title: model.title || "Sem título"
                            coverUrl: model.coverUrl || ""
                            chapterCount: model.chapterCount || 0
                            status: model.status || ""
                            selected: window.currentManga && window.currentManga.path === model.path
                            
                            onClicked: {
                                if (model.path) {
                                    window.currentManga = {
                                        title: model.title,
                                        path: model.path,
                                        chapterCount: model.chapterCount
                                    }
                                    backend.loadMangaDetails(model.path)
                                }
                            }
                            
                            onUploadClicked: {
                                if (model.path) {
                                    window.currentManga = {
                                        title: model.title,
                                        path: model.path,
                                        chapterCount: model.chapterCount
                                    }
                                    backend.loadMangaDetails(model.path)
                                    // TODO: Abrir diálogo de upload
                                }
                            }
                            
                            onEditClicked: {
                                if (model.path) {
                                    window.currentManga = {
                                        title: model.title,
                                        path: model.path,
                                        chapterCount: model.chapterCount
                                    }
                                    backend.loadMangaDetails(model.path)
                                    // TODO: Abrir diálogo de edição
                                }
                            }
                        }
                    }
                }
            }
        }
        
        // Main Content Area
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: ds.bgPrimary
            
            StackLayout {
                anchors.fill: parent
                anchors.margins: ds.space8
                currentIndex: window.currentManga ? 1 : 0
                
                // Dashboard Principal
                Item {
                    ColumnLayout {
                        anchors.centerIn: parent
                        spacing: ds.space8
                        width: Math.min(parent.width - ds.space16, 800)
                        
                        // Hero Section
                        ColumnLayout {
                            Layout.alignment: Qt.AlignHCenter
                            spacing: ds.space6
                            
                            Rectangle {
                                width: 120
                                height: 120
                                radius: ds.radius_xl
                                color: ds.bgCard
                                border.color: ds.border
                                border.width: 1
                                Layout.alignment: Qt.AlignHCenter
                                
                                Text {
                                    anchors.centerIn: parent
                                    text: "📚"
                                    font.pixelSize: ds.text_4xl
                                }
                            }
                            
                            Text {
                                text: "Manga Uploader Pro"
                                font.pixelSize: ds.text_3xl
                                font.weight: ds.fontBold
                                color: ds.textPrimary
                                Layout.alignment: Qt.AlignHCenter
                            }
                            
                            Text {
                                text: "Selecione um mangá na biblioteca ou configure um host para começar"
                                font.pixelSize: ds.text_lg
                                color: ds.textSecondary
                                Layout.alignment: Qt.AlignHCenter
                                horizontalAlignment: Text.AlignHCenter
                                Layout.maximumWidth: 400
                                wrapMode: Text.WordWrap
                            }
                        }
                        
                        // Quick Actions Grid
                        GridLayout {
                            Layout.alignment: Qt.AlignHCenter
                            columns: 2
                            columnSpacing: ds.space4
                            rowSpacing: ds.space4
                            
                            // Configure Host Card
                            ModernCard {
                                Layout.preferredWidth: 200
                                Layout.preferredHeight: 120
                                
                                ColumnLayout {
                                    anchors.fill: parent
                                    anchors.margins: ds.space4
                                    spacing: ds.space3
                                    
                                    RowLayout {
                                        spacing: ds.space3
                                        
                                        Text {
                                            text: "🌐"
                                            font.pixelSize: ds.text_xl
                                        }
                                        
                                        Text {
                                            text: "Configurar Host"
                                            font.pixelSize: ds.text_base
                                            font.weight: ds.fontMedium
                                            color: ds.textPrimary
                                        }
                                    }
                                    
                                    Text {
                                        text: "Configure provedores de upload como Catbox, Imgur, etc."
                                        font.pixelSize: ds.text_sm
                                        color: ds.textSecondary
                                        wrapMode: Text.WordWrap
                                        Layout.fillWidth: true
                                        Layout.fillHeight: true
                                    }
                                }
                                
                                onClicked: settingsDrawer.open()
                            }
                            
                            // View Indexador Card
                            ModernCard {
                                Layout.preferredWidth: 200
                                Layout.preferredHeight: 120
                                
                                ColumnLayout {
                                    anchors.fill: parent
                                    anchors.margins: ds.space4
                                    spacing: ds.space3
                                    
                                    RowLayout {
                                        spacing: ds.space3
                                        
                                        Text {
                                            text: "📋"
                                            font.pixelSize: ds.text_xl
                                        }
                                        
                                        Text {
                                            text: "Ver Indexador"
                                            font.pixelSize: ds.text_base
                                            font.weight: ds.fontMedium
                                            color: ds.textPrimary
                                        }
                                    }
                                    
                                    Text {
                                        text: "Visualize e gerencie séries no sistema indexador"
                                        font.pixelSize: ds.text_sm
                                        color: ds.textSecondary
                                        wrapMode: Text.WordWrap
                                        Layout.fillWidth: true
                                        Layout.fillHeight: true
                                    }
                                }
                                
                                onClicked: indexadorDialog.open()
                            }
                            
                            // Folder Browser Card
                            ModernCard {
                                Layout.preferredWidth: 200
                                Layout.preferredHeight: 120
                                
                                ColumnLayout {
                                    anchors.fill: parent
                                    anchors.margins: ds.space4
                                    spacing: ds.space3
                                    
                                    RowLayout {
                                        spacing: ds.space3
                                        
                                        Text {
                                            text: "📁"
                                            font.pixelSize: ds.text_xl
                                        }
                                        
                                        Text {
                                            text: "Explorar Pasta"
                                            font.pixelSize: ds.text_base
                                            font.weight: ds.fontMedium
                                            color: ds.textPrimary
                                        }
                                    }
                                    
                                    Text {
                                        text: "Abrir explorador de arquivos para selecionar pasta"
                                        font.pixelSize: ds.text_sm
                                        color: ds.textSecondary
                                        wrapMode: Text.WordWrap
                                        Layout.fillWidth: true
                                        Layout.fillHeight: true
                                    }
                                }
                                
                                onClicked: {
                                    folderDialog.open()
                                }
                            }
                            
                            // Refresh Library Card
                            ModernCard {
                                Layout.preferredWidth: 200
                                Layout.preferredHeight: 120
                                
                                ColumnLayout {
                                    anchors.fill: parent
                                    anchors.margins: ds.space4
                                    spacing: ds.space3
                                    
                                    RowLayout {
                                        spacing: ds.space3
                                        
                                        Text {
                                            text: "🔄"
                                            font.pixelSize: ds.text_xl
                                        }
                                        
                                        Text {
                                            text: "Atualizar Biblioteca"
                                            font.pixelSize: ds.text_base
                                            font.weight: ds.fontMedium
                                            color: ds.textPrimary
                                        }
                                    }
                                    
                                    Text {
                                        text: "Recarregar a lista de mangás da biblioteca"
                                        font.pixelSize: ds.text_sm
                                        color: ds.textSecondary
                                        wrapMode: Text.WordWrap
                                        Layout.fillWidth: true
                                        Layout.fillHeight: true
                                    }
                                }
                                
                                onClicked: {
                                    backend.refreshMangaList()
                                }
                            }
                        }
                        
                        // Status Section
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 80
                            radius: ds.radius_lg
                            color: ds.bgCard
                            border.color: ds.border
                            border.width: 1
                            Layout.alignment: Qt.AlignHCenter
                            Layout.maximumWidth: 600
                            
                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: ds.space4
                                spacing: ds.space6
                                
                                // Library Status
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: ds.space1
                                    
                                    Text {
                                        text: "📚 Biblioteca"
                                        font.pixelSize: ds.text_sm
                                        font.weight: ds.fontMedium
                                        color: ds.textSecondary
                                    }
                                    
                                    Text {
                                        text: (mangaListView.count || 0) + " mangás"
                                        font.pixelSize: ds.text_lg
                                        font.weight: ds.fontBold
                                        color: ds.textPrimary
                                    }
                                }
                                
                                Rectangle {
                                    width: 1
                                    height: parent.height * 0.6
                                    color: ds.divider
                                }
                                
                                // Host Status
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: ds.space1
                                    
                                    Text {
                                        text: "🌐 Host Ativo"
                                        font.pixelSize: ds.text_sm
                                        font.weight: ds.fontMedium
                                        color: ds.textSecondary
                                    }
                                    
                                    Text {
                                        text: backend.currentHost || "Não configurado"
                                        font.pixelSize: ds.text_lg
                                        font.weight: ds.fontBold
                                        color: backend.currentHost ? ds.success : ds.warning
                                    }
                                }
                                
                                Rectangle {
                                    width: 1
                                    height: parent.height * 0.6
                                    color: ds.divider
                                }
                                
                                // Upload Status
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: ds.space1
                                    
                                    Text {
                                        text: "⚡ Status"
                                        font.pixelSize: ds.text_sm
                                        font.weight: ds.fontMedium
                                        color: ds.textSecondary
                                    }
                                    
                                    Text {
                                        text: isProcessing ? "Processando" : "Pronto"
                                        font.pixelSize: ds.text_lg
                                        font.weight: ds.fontBold
                                        color: isProcessing ? ds.accent : ds.success
                                    }
                                }
                            }
                        }
                    }
                }
                
                // Manga Details
                RowLayout {
                    spacing: 0
                    
                    // Main Content Column
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 24
                        
                        // Manga Info Section
                        RowLayout {
                            spacing: 20
                            
                            // Cover
                            Rectangle {
                                width: 120
                                height: 160
                                radius: ds.radius_lg
                                color: ds.bgSurface
                                border.color: backend.currentMangaHasJson ? ds.accent : ds.border
                                border.width: 2
                                clip: true
                                
                                Image {
                                    anchors.fill: parent
                                    anchors.margins: 2
                                    source: backend.currentMangaCover || ""
                                    fillMode: Image.PreserveAspectCrop
                                    visible: backend.currentMangaCover !== ""
                                    smooth: true
                                    cache: true
                                    asynchronous: true
                                    horizontalAlignment: Image.AlignHCenter
                                    verticalAlignment: Image.AlignTop
                                    sourceSize.width: 240
                                    sourceSize.height: 320
                                    
                                    Rectangle {
                                        anchors.fill: parent
                                        color: ds.bgPrimary
                                        opacity: 0.8
                                        visible: parent.status === Image.Loading
                                        radius: ds.radius_sm
                                        
                                        Rectangle {
                                            anchors.centerIn: parent
                                            width: ds.iconLg
                                            height: ds.iconLg
                                            radius: ds.iconLg / 2
                                            color: ds.accent
                                            
                                            SequentialAnimation on rotation {
                                                running: true
                                                loops: Animation.Infinite
                                                NumberAnimation { from: 0; to: 360; duration: 1000 }
                                            }
                                        }
                                    }
                                }
                                
                                Rectangle {
                                    anchors.fill: parent
                                    color: ds.accent
                                    visible: backend.currentMangaCover === ""
                                    
                                    Text {
                                        anchors.centerIn: parent
                                        text: backend.currentMangaTitle ? backend.currentMangaTitle.charAt(0).toUpperCase() : "?"
                                        font.pixelSize: ds.text_3xl
                                        font.weight: ds.fontBold
                                        color: ds.textPrimary
                                    }
                                }
                                
                                // JSON Status Badge
                                Rectangle {
                                    anchors.bottom: parent.bottom
                                    anchors.right: parent.right
                                    anchors.margins: ds.space1
                                    width: ds.space3
                                    height: ds.space3
                                    radius: ds.space3 / 2
                                    color: backend.currentMangaHasJson ? ds.success : ds.textSecondary
                                    opacity: backend.currentMangaHasJson ? 1.0 : 0.3
                                }
                            }
                            
                            // Info Column
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                
                                Text {
                                    text: backend.currentMangaTitle || ""
                                    font.pixelSize: ds.text_xl
                                    font.weight: ds.fontMedium
                                    color: ds.textPrimary
                                    elide: Text.ElideRight
                                    Layout.fillWidth: true
                                }
                                
                                Text {
                                    text: backend.currentMangaDescription || ""
                                    font.pixelSize: ds.text_sm
                                    color: ds.textSecondary
                                    opacity: 0.8
                                    elide: Text.ElideRight
                                    maximumLineCount: 2
                                    wrapMode: Text.WordWrap
                                    Layout.fillWidth: true
                                    visible: backend.currentMangaDescription !== ""
                                }
                                
                                RowLayout {
                                    spacing: 16
                                    
                                    Text {
                                        text: "ARTISTA: " + (backend.currentMangaArtist || "—")
                                        font.pixelSize: ds.text_xs
                                        font.weight: ds.fontMedium
                                        font.letterSpacing: 0.5
                                        color: ds.textSecondary
                                        opacity: 0.7
                                    }
                                    
                                    Text {
                                        text: "AUTOR: " + (backend.currentMangaAuthor || "—")
                                        font.pixelSize: ds.text_xs
                                        font.weight: ds.fontMedium
                                        font.letterSpacing: 0.5
                                        color: ds.textSecondary
                                        opacity: 0.7
                                    }
                                    
                                    Text {
                                        text: "STATUS: " + (backend.currentMangaStatus || "—")
                                        font.pixelSize: ds.text_xs
                                        font.weight: ds.fontMedium
                                        font.letterSpacing: 0.5
                                        color: ds.textSecondary
                                        opacity: 0.7
                                    }
                                    
                                    Text {
                                        text: "GRUPO: " + (backend.currentMangaGroup || "—")
                                        font.pixelSize: ds.text_xs
                                        font.weight: ds.fontMedium
                                        font.letterSpacing: 0.5
                                        color: ds.textSecondary
                                        opacity: 0.7
                                    }
                                }
                                
                                Text {
                                    text: backend.currentMangaChapterCount + " CAPÍTULOS " + (backend.currentMangaHasJson ? "• METADADOS" : "• SEM METADADOS")
                                    font.pixelSize: ds.text_xs
                                    font.weight: ds.fontMedium
                                    font.letterSpacing: 0.5
                                    color: backend.currentMangaHasJson ? ds.success : ds.textSecondary
                                    opacity: backend.currentMangaHasJson ? 1.0 : 0.7
                                }
                            }
                        }
                        
                        // Chapters Section
                        ModernChapterList {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            model: chapterModel
                            
                            onAllSelected: {
                                backend.selectAllChapters()
                            }
                            
                            onAllUnselected: {
                                backend.unselectAllChapters()
                            }
                            
                            onOrderInverted: {
                                backend.toggleChapterOrder()
                            }
                            
                            onUploadSelected: {
                                uploadWorkflowDialog.open()
                            }
                            
                            onRemoveSelected: {
                                // TODO: Implementar remoção de capítulos selecionados
                                console.log("Remove selected chapters")
                            }
                            
                            onProcessSelected: {
                                uploadWorkflowDialog.open()
                            }
                            
                            onChapterClicked: {
                                // TODO: Implementar seleção de capítulo específico
                                console.log("Chapter clicked:", name)
                            }
                            
                            onChapterUploadClicked: {
                                uploadWorkflowDialog.open()
                            }
                            
                            onChapterEditClicked: {
                                // TODO: Implementar edição de capítulo específico
                                console.log("Chapter edit clicked:", name)
                            }
                        }
                        
                        // Progress Bar
                        Rectangle {
                            Layout.fillWidth: true
                            height: 4
                            radius: 2
                            color: ds.bgSurface
                            visible: isProcessing
                            
                            Rectangle {
                                width: parent.width * backend.uploadProgress
                                height: parent.height
                                radius: parent.radius
                                color: ds.accent
                                
                                Behavior on width {
                                    NumberAnimation {
                                        duration: ds.animationFast
                                        easing.type: ds.easingOut
                                    }
                                }
                            }
                        }
                    }
                    
                    // Vertical Actions Panel
                    Rectangle {
                        Layout.preferredWidth: 160
                        Layout.fillHeight: true
                        color: ds.bgSurface
                        
                        Rectangle {
                            anchors.left: parent.left
                            width: 1
                            height: parent.height
                            color: ds.divider
                        }
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: ds.space5
                            spacing: ds.space4
                            
                            Text {
                                text: "⚡ AÇÕES"
                                font.pixelSize: ds.text_sm
                                font.weight: ds.fontMedium
                                font.letterSpacing: 1
                                color: ds.textSecondary
                                Layout.alignment: Qt.AlignHCenter
                            }
                            
                            // Upload Button
                            ModernButton {
                                Layout.fillWidth: true
                                text: isProcessing ? "Processando..." : "Upload"
                                icon: isProcessing ? "⟳" : "📤"
                                variant: "primary"
                                size: "lg"
                                loading: isProcessing
                                enabled: !isProcessing && window.currentManga
                                tooltip: "Iniciar upload dos capítulos selecionados"
                                
                                onClicked: {
                                    metadataDialog.openForUpload()
                                }
                            }
                            
                            // Edit Button
                            ModernButton {
                                Layout.fillWidth: true
                                text: "Editar"
                                icon: "✏️"
                                variant: "secondary"
                                size: "lg"
                                enabled: !isProcessing && window.currentManga
                                tooltip: "Editar informações do mangá"
                                
                                onClicked: {
                                    metadataDialog.openForEdit()
                                }
                            }
                            
                            // GitHub Button
                            ModernButton {
                                Layout.fillWidth: true
                                text: "GitHub"
                                icon: "⚡"
                                variant: "success"
                                size: "lg"
                                enabled: !isProcessing && window.currentManga && backend.currentMangaHasJson
                                visible: backend.githubRepo !== ""
                                tooltip: "Salvar no repositório GitHub"
                                
                                onClicked: {
                                    backend.saveToGitHub()
                                }
                            }
                            
                            Item { Layout.fillHeight: true }
                        }
                    }
                }
            }
        }
    }
    
    // Settings Drawer
    Drawer {
        id: settingsDrawer
        width: 450
        height: parent.height
        edge: Qt.RightEdge
        
        Material.theme: Material.Dark
        Material.background: ds.bgPrimary
        
        ModernSettingsPanel {
            anchors.fill: parent
            
            onSaveSettings: {
                // Save configuration logic here
                console.log("Settings saved")
                settingsDrawer.close()
            }
        }
    }
    
    // Upload Workflow Dialog
    Dialog {
        id: uploadWorkflowDialog
        width: Math.min(window.width * 0.9, 1200)
        height: Math.min(window.height * 0.9, 800)
        x: (window.width - width) / 2
        y: (window.height - height) / 2
        
        modal: true
        focus: true
        closePolicy: Dialog.NoAutoClose
        
        background: Rectangle {
            color: "transparent"
        }
        
        contentItem: ModernUploadWorkflow {
            anchors.fill: parent
            
            onCancelled: {
                uploadWorkflowDialog.close()
            }
            
            onUploadStarted: {
                console.log("Upload started")
            }
            
            onUploadCompleted: {
                console.log("Upload completed")
                uploadWorkflowDialog.close()
            }
        }
    }
    
    // Dialogs
    Platform.FolderDialog {
        id: folderDialog
        title: "Selecione a pasta dos mangás"
        folder: backend.rootFolder ? "file:///" + backend.rootFolder : Platform.StandardPaths.homeFolder
        onAccepted: {
            rootFolderField.text = folder.toString()
        }
    }
    
    Platform.FolderDialog {
        id: outputFolderDialog
        title: "Selecione a pasta de saída dos metadados"
        folder: backend.outputFolder ? "file:///" + backend.outputFolder : Platform.StandardPaths.homeFolder
        onAccepted: {
            outputFolderField.text = folder.toString()
        }
    }
    
    
    Dialog {
        id: metadataDialog
        width: 480
        height: 600
        anchors.centerIn: parent
        
        Material.theme: Material.Dark
        Material.background: colorSurface
        
        property bool isEditMode: false
        title: isEditMode ? "Editar Metadados" : "Upload com Metadados"
        
        function openForUpload() {
            isEditMode = false
            if (window.currentManga) {
                // Carregar metadados existentes se disponível
                backend.loadExistingMetadata(window.currentManga.title)
            }
            open()
        }
        
        function openForEdit() {
            if (!window.currentManga) return
            isEditMode = true
            backend.loadExistingMetadata(window.currentManga.title)
            open()
        }
        
        Connections {
            target: backend
            function onMetadataLoaded(metadata) {
                console.log("onMetadataLoaded called - metadata:", JSON.stringify(metadata))
                console.log("Dialog visible:", metadataDialog.visible, "isEditMode:", metadataDialog.isEditMode)
                
                // Funciona tanto para upload quanto para editar
                titleField.text = metadata.title || ""
                descriptionField.text = metadata.description || ""
                artistField.text = metadata.artist || ""
                authorField.text = metadata.author || ""
                groupField.text = metadata.group || ""
                coverField.text = metadata.cover || ""
                
                var statusList = ["Em Andamento", "Completo", "Pausado", "Cancelado", "Hiato"]
                var statusIndex = statusList.indexOf(metadata.status || "Em Andamento")
                statusCombo.currentIndex = statusIndex >= 0 ? statusIndex : 0
                
                console.log("Fields updated - title:", titleField.text, "mode:", metadataDialog.isEditMode ? "edit" : "upload")
            }
        }
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 24
            spacing: 16
            
            Label {
                text: metadataDialog.isEditMode ? "EDITAR METADADOS" : "METADADOS PARA UPLOAD"
                font.pixelSize: 12
                font.weight: Font.Medium
                font.letterSpacing: 1
                color: colorTertiary
                opacity: 0.8
            }
            
            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: colorTertiary
                opacity: 0.1
            }
            
            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                
                ColumnLayout {
                    width: parent.width
                    spacing: 16
                    
                    Rectangle {
                        Layout.fillWidth: true
                        height: 32
                        color: colorPrimary
                        border.color: colorTertiary
                        border.width: 1
                        radius: 8
                        
                        TextField {
                            id: titleField
                            anchors.fill: parent
                            anchors.margins: 1
                            placeholderText: "Título"
                            color: colorTertiary
                            font.pixelSize: 12
                            background: Rectangle { color: "transparent" }
                            leftPadding: 8
                            rightPadding: 8
                        }
                    }
                    
                    Rectangle {
                        Layout.fillWidth: true
                        height: 80
                        color: colorPrimary
                        border.color: colorTertiary
                        border.width: 1
                        radius: 8
                        
                        ScrollView {
                            anchors.fill: parent
                            anchors.margins: 1
                            
                            TextArea {
                                id: descriptionField
                                placeholderText: "Descrição..."
                                color: colorTertiary
                                font.pixelSize: 12
                                background: Rectangle { color: "transparent" }
                                leftPadding: 8
                                rightPadding: 8
                                topPadding: 8
                                bottomPadding: 8
                                wrapMode: TextArea.Wrap
                            }
                        }
                    }
                    
                    Rectangle {
                        Layout.fillWidth: true
                        height: 32
                        color: colorPrimary
                        border.color: colorTertiary
                        border.width: 1
                        radius: 8
                        
                        TextField {
                            id: artistField
                            anchors.fill: parent
                            anchors.margins: 1
                            placeholderText: "Artista"
                            color: colorTertiary
                            font.pixelSize: 12
                            background: Rectangle { color: "transparent" }
                            leftPadding: 8
                            rightPadding: 8
                        }
                    }
                    
                    Rectangle {
                        Layout.fillWidth: true
                        height: 32
                        color: colorPrimary
                        border.color: colorTertiary
                        border.width: 1
                        radius: 8
                        
                        TextField {
                            id: authorField
                            anchors.fill: parent
                            anchors.margins: 1
                            placeholderText: "Autor"
                            color: colorTertiary
                            font.pixelSize: 12
                            background: Rectangle { color: "transparent" }
                            leftPadding: 8
                            rightPadding: 8
                        }
                    }
                    
                    Rectangle {
                        Layout.fillWidth: true
                        height: 32
                        color: colorPrimary
                        border.color: colorTertiary
                        border.width: 1
                        radius: 8
                        
                        TextField {
                            id: groupField
                            anchors.fill: parent
                            anchors.margins: 1
                            placeholderText: "Grupo de tradução (opcional)"
                            color: colorTertiary
                            font.pixelSize: 12
                            background: Rectangle { color: "transparent" }
                            leftPadding: 8
                            rightPadding: 8
                        }
                    }
                    
                    Rectangle {
                        Layout.fillWidth: true
                        height: 32
                        color: colorPrimary
                        border.color: colorTertiary
                        border.width: 1
                        radius: 8
                        
                        TextField {
                            id: coverField
                            anchors.fill: parent
                            anchors.margins: 1
                            placeholderText: "URL da capa"
                            color: colorTertiary
                            font.pixelSize: 12
                            background: Rectangle { color: "transparent" }
                            leftPadding: 8
                            rightPadding: 8
                        }
                    }
                    
                    Rectangle {
                        Layout.fillWidth: true
                        height: 32
                        color: colorPrimary
                        border.color: colorTertiary
                        border.width: 1
                        radius: 8
                        
                        ComboBox {
                            id: statusCombo
                            anchors.fill: parent
                            model: ["Em Andamento", "Completo", "Pausado", "Cancelado", "Hiato"]
                            currentIndex: 0
                            
                            background: Rectangle {
                                color: "transparent"
                            }
                            
                            contentItem: Text {
                                text: statusCombo.currentText
                                font.pixelSize: 12
                                color: colorTertiary
                                verticalAlignment: Text.AlignVCenter
                                leftPadding: 8
                            }
                        }
                    }
                }
            }
            
            RowLayout {
                spacing: 12
                
                Rectangle {
                    Layout.fillWidth: true
                    height: 36
                    radius: 8
                    color: cancelBtnHovered ? colorTertiary : "transparent"
                    border.color: colorTertiary
                    border.width: 1
                    
                    property bool cancelBtnHovered: false
                    
                    Label {
                        anchors.centerIn: parent
                        text: "CANCELAR"
                        font.pixelSize: 10
                        font.weight: Font.Medium
                        font.letterSpacing: 1
                        color: parent.cancelBtnHovered ? colorPrimary : colorTertiary
                    }
                    
                    MouseArea {
                        id: cancelBtn
                        anchors.fill: parent
                        hoverEnabled: true
                        onEntered: parent.cancelBtnHovered = true
                        onExited: parent.cancelBtnHovered = false
                        onClicked: metadataDialog.close()
                    }
                }
                
                Rectangle {
                    Layout.fillWidth: true
                    height: 36
                    radius: 8
                    color: okBtnHovered ? colorSecondary : "transparent"
                    border.color: colorSecondary
                    border.width: 1
                    
                    property bool okBtnHovered: false
                    
                    Label {
                        anchors.centerIn: parent
                        text: metadataDialog.isEditMode ? "SALVAR" : "UPLOAD"
                        font.pixelSize: 10
                        font.weight: Font.Medium
                        font.letterSpacing: 1
                        color: parent.okBtnHovered ? "white" : colorSecondary
                    }
                    
                    MouseArea {
                        id: okBtn
                        anchors.fill: parent
                        hoverEnabled: true
                        onEntered: parent.okBtnHovered = true
                        onExited: parent.okBtnHovered = false
                        onClicked: {
                            var metadata = {
                                title: backend.makeJsonSafe(titleField.text || ""),
                                description: backend.makeJsonSafe(descriptionField.text || ""),
                                artist: backend.makeJsonSafe(artistField.text || ""),
                                author: backend.makeJsonSafe(authorField.text || ""),
                                group: backend.makeJsonSafe(groupField.text || ""),
                                cover: coverField.text || "",
                                status: statusCombo.currentText || "Em Andamento"
                            }
                            
                            if (metadataDialog.isEditMode) {
                                backend.updateExistingMetadata(metadata)
                            } else {
                                backend.startUploadWithMetadata(metadata)
                            }
                            
                            metadataDialog.close()
                        }
                    }
                }
            }
        }
    }
    
    // Indexador Dialog
    IndexadorDialog {
        id: indexadorDialog
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
}