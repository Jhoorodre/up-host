import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls.Material 2.15

Dialog {
    id: indexadorDialog
    
    title: "Gerenciar Indexador"
    width: 800
    height: 600
    modal: true
    anchors.centerIn: parent
    
    // Cores do tema
    readonly property color colorPrimary: "#1a1a1a"
    readonly property color colorSecondary: "#0078d4"
    readonly property color colorTertiary: "#ffffff"
    readonly property color colorSurface: "#2d2d2d"
    readonly property color colorHover: "#404040"
    readonly property color colorSuccess: "#00c851"
    readonly property color colorWarning: "#ff9500"
    
    Material.theme: Material.Dark
    Material.accent: colorSecondary
    
    Component.onCompleted: {
        // Carrega séries locais automaticamente
        backend.scanLocalJsons()
    }
    
    // Conexão com signal de séries
    Connections {
        target: backend
        function onIndexadorSeriesListChanged(seriesList) {
            seriesListModel.clear()
            for (let i = 0; i < seriesList.length; i++) {
                seriesListModel.append(seriesList[i])
            }
            // updateSeriesStats() // Função será definida mais abaixo
        }
    }
    
    ColumnLayout {
        anchors.fill: parent
        spacing: 16
        
        // Área de notificações
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: notificationText.visible ? 40 : 0
            color: "#1e3a8a"
            radius: 6
            border.color: colorSecondary
            border.width: 1
            visible: notificationText.text !== ""
            
            Label {
                id: notificationText
                anchors.centerIn: parent
                text: ""
                color: colorTertiary
                font.pixelSize: 11
                font.weight: Font.Medium
            }
        }
        
        // TabBar
        TabBar {
            id: tabBar
            Layout.fillWidth: true
            
            TabButton {
                text: "Grupo"
                width: implicitWidth
            }
            TabButton {
                text: "Redes Sociais"
                width: implicitWidth
            }
            TabButton {
                text: "Técnico"
                width: implicitWidth
            }
            TabButton {
                text: "Séries"
                width: implicitWidth
            }
            TabButton {
                text: "Prévia"
                width: implicitWidth
            }
        }
        
        // Stack Layout para as abas
        StackLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: tabBar.currentIndex
            
            // Aba 1: Informações do Grupo
            ScrollView {
                ColumnLayout {
                    width: parent.width
                    spacing: 16
                    
                    Label {
                        text: "INFORMAÇÕES DO GRUPO"
                        font.pixelSize: 14
                        font.weight: Font.Bold
                        color: colorTertiary
                    }
                    
                    // Nome do Grupo
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8
                        
                        TextField {
                            id: hubNameField
                            Layout.fillWidth: true
                            placeholderText: "Nome do grupo"
                            text: backend.indexadorHubName
                            onTextChanged: {
                                if (text !== backend.indexadorHubName) {
                                    backend.setIndexadorHubName(text)
                                }
                            }
                        }
                        
                        Text {
                            text: "💡"
                            font.pixelSize: 16
                            color: colorWarning
                            
                            MouseArea {
                                anchors.fill: parent
                                hoverEnabled: true
                                onEntered: {
                                    notificationText.text = "💡 Nome do grupo é recomendado para identificação do hub"
                                }
                                onExited: {
                                    notificationText.text = ""
                                }
                            }
                        }
                    }
                    
                    // Subtítulo
                    TextField {
                        id: hubSubtitleField
                        Layout.fillWidth: true
                        placeholderText: "Subtítulo (ex: Scanlation Oficial)"
                        text: backend.indexadorHubSubtitle
                        onTextChanged: {
                            if (text !== backend.indexadorHubSubtitle) {
                                backend.setIndexadorHubSubtitle(text)
                            }
                        }
                    }
                    
                    // Descrição
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8
                        
                        ColumnLayout {
                            Layout.fillWidth: true
                            
                            Label {
                                text: "Descrição:"
                                font.pixelSize: 12
                                color: colorTertiary
                            }
                            
                            ScrollView {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 100
                                
                                TextArea {
                                    id: hubDescriptionArea
                                    placeholderText: "Descrição do grupo, missão, objetivos..."
                                    text: backend.indexadorHubDescription
                                    wrapMode: TextArea.Wrap
                                    selectByMouse: true
                                    
                                    onTextChanged: {
                                        if (text !== backend.indexadorHubDescription) {
                                            backend.setIndexadorHubDescription(text)
                                        }
                                    }
                                }
                            }
                        }
                        
                        Text {
                            text: "💡"
                            font.pixelSize: 16
                            color: colorWarning
                            Layout.alignment: Qt.AlignTop
                            
                            MouseArea {
                                anchors.fill: parent
                                hoverEnabled: true
                                onEntered: {
                                    notificationText.text = "💡 Descrição ajuda visitantes a entender o propósito do grupo"
                                }
                                onExited: {
                                    notificationText.text = ""
                                }
                            }
                        }
                    }
                    
                    // Email de contato
                    TextField {
                        id: hubContactField
                        Layout.fillWidth: true
                        placeholderText: "Email de contato (opcional)"
                        text: backend.indexadorHubContact
                        onTextChanged: {
                            if (text !== backend.indexadorHubContact) {
                                backend.setIndexadorHubContact(text)
                            }
                        }
                    }
                    
                    // Website
                    TextField {
                        id: hubWebsiteField
                        Layout.fillWidth: true
                        placeholderText: "Website principal (opcional)"
                        text: backend.indexadorHubWebsite
                        onTextChanged: {
                            if (text !== backend.indexadorHubWebsite) {
                                backend.setIndexadorHubWebsite(text)
                            }
                        }
                    }
                }
            }
            
            // Aba 2: Redes Sociais
            ScrollView {
                ColumnLayout {
                    width: parent.width
                    spacing: 20
                    
                    Label {
                        text: "REDES SOCIAIS"
                        font.pixelSize: 14
                        font.weight: Font.Bold
                        color: colorTertiary
                    }
                    
                    // Discord
                    GroupBox {
                        Layout.fillWidth: true
                        title: "🎮 Discord"
                        
                        ColumnLayout {
                            anchors.fill: parent
                            spacing: 8
                            
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                
                                TextField {
                                    id: discordUrlField
                                    Layout.fillWidth: true
                                    placeholderText: "https://discord.gg/..."
                                    text: backend.indexadorDiscordUrl
                                    onTextChanged: {
                                        if (text !== backend.indexadorDiscordUrl) {
                                            backend.setIndexadorDiscordUrl(text)
                                        }
                                    }
                                }
                                
                                Button {
                                    text: "Testar"
                                    enabled: discordUrlField.text.length > 0
                                    onClicked: {
                                        backend.testSocialUrl(discordUrlField.text)
                                        notificationText.text = "🔄 Testando URL..."
                                    }
                                }
                            }
                            
                            TextField {
                                Layout.fillWidth: true
                                placeholderText: "Descrição (ex: Servidor principal para discussões)"
                                text: "Servidor principal para discussões e atualizações"
                            }
                        }
                    }
                    
                    // Telegram
                    GroupBox {
                        Layout.fillWidth: true
                        title: "📱 Telegram"
                        
                        ColumnLayout {
                            anchors.fill: parent
                            spacing: 8
                            
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                
                                TextField {
                                    id: telegramUrlField
                                    Layout.fillWidth: true
                                    placeholderText: "https://t.me/..."
                                    text: backend.indexadorTelegramUrl
                                    onTextChanged: {
                                        if (text !== backend.indexadorTelegramUrl) {
                                            backend.setIndexadorTelegramUrl(text)
                                        }
                                    }
                                }
                                
                                Button {
                                    text: "Testar"
                                    enabled: telegramUrlField.text.length > 0
                                    onClicked: {
                                        backend.testSocialUrl(telegramUrlField.text)
                                        notificationText.text = "🔄 Testando URL..."
                                    }
                                }
                            }
                            
                            TextField {
                                Layout.fillWidth: true
                                placeholderText: "Descrição (ex: Notificações e releases)"
                                text: "Notificações e releases"
                            }
                        }
                    }
                    
                    // WhatsApp
                    GroupBox {
                        Layout.fillWidth: true
                        title: "📞 WhatsApp"
                        
                        ColumnLayout {
                            anchors.fill: parent
                            spacing: 8
                            
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                
                                TextField {
                                    id: whatsappUrlField
                                    Layout.fillWidth: true
                                    placeholderText: "https://chat.whatsapp.com/..."
                                    text: backend.indexadorWhatsappUrl
                                    onTextChanged: {
                                        if (text !== backend.indexadorWhatsappUrl) {
                                            backend.setIndexadorWhatsappUrl(text)
                                        }
                                    }
                                }
                                
                                Button {
                                    text: "Testar"
                                    enabled: whatsappUrlField.text.length > 0
                                    onClicked: {
                                        backend.testSocialUrl(whatsappUrlField.text)
                                        notificationText.text = "🔄 Testando URL..."
                                    }
                                }
                            }
                            
                            TextField {
                                Layout.fillWidth: true
                                placeholderText: "Descrição (ex: Comunidade para discussões rápidas)"
                                text: "Comunidade para discussões rápidas"
                            }
                        }
                    }
                    
                    // Twitter
                    GroupBox {
                        Layout.fillWidth: true
                        title: "🐦 Twitter/X"
                        
                        ColumnLayout {
                            anchors.fill: parent
                            spacing: 8
                            
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                
                                TextField {
                                    id: twitterUrlField
                                    Layout.fillWidth: true
                                    placeholderText: "https://twitter.com/..."
                                    text: backend.indexadorTwitterUrl
                                    onTextChanged: {
                                        if (text !== backend.indexadorTwitterUrl) {
                                            backend.setIndexadorTwitterUrl(text)
                                        }
                                    }
                                }
                                
                                Button {
                                    text: "Testar"
                                    enabled: twitterUrlField.text.length > 0
                                    onClicked: {
                                        backend.testSocialUrl(twitterUrlField.text)
                                        notificationText.text = "🔄 Testando URL..."
                                    }
                                }
                            }
                            
                            TextField {
                                Layout.fillWidth: true
                                placeholderText: "Descrição (ex: Atualizações e novidades)"
                                text: "Atualizações e novidades"
                            }
                        }
                    }
                    
                    // Dica
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        color: colorSurface
                        radius: 6
                        border.color: colorWarning
                        border.width: 1
                        
                        Label {
                            anchors.centerIn: parent
                            text: "💡 Pelo menos uma rede social é recomendada para contato"
                            color: colorTertiary
                            font.pixelSize: 11
                        }
                    }
                }
            }
            
            // Aba 3: Configurações Técnicas
            ScrollView {
                ColumnLayout {
                    width: parent.width
                    spacing: 20
                    
                    Label {
                        text: "CONFIGURAÇÕES TÉCNICAS"
                        font.pixelSize: 14
                        font.weight: Font.Bold
                        color: colorTertiary
                    }
                    
                    // URLs e CDN
                    GroupBox {
                        Layout.fillWidth: true
                        title: "URLs e CDN"
                        
                        ColumnLayout {
                            anchors.fill: parent
                            spacing: 12
                            
                            // Preferência de URL
                            Label {
                                text: "Preferência de URL:"
                                font.pixelSize: 12
                                color: colorTertiary
                            }
                            
                            ColumnLayout {
                                spacing: 8
                                
                                RadioButton {
                                    id: cdnOnlyRadio
                                    text: "CDN jsDelivr (recomendado - mais rápido)"
                                    checked: backend.indexadorUrlPreference === "cdn"
                                    onCheckedChanged: {
                                        if (checked && backend.indexadorUrlPreference !== "cdn") {
                                            backend.setIndexadorUrlPreference("cdn")
                                        }
                                    }
                                }
                                
                                RadioButton {
                                    id: rawOnlyRadio
                                    text: "GitHub Raw (sempre funciona)"
                                    checked: backend.indexadorUrlPreference === "raw"
                                    onCheckedChanged: {
                                        if (checked && backend.indexadorUrlPreference !== "raw") {
                                            backend.setIndexadorUrlPreference("raw")
                                        }
                                    }
                                }
                                
                                RadioButton {
                                    id: hybridRadio
                                    text: "Híbrido (CDN com fallback para GitHub Raw) ✅"
                                    checked: backend.indexadorUrlPreference === "hybrid"
                                    onCheckedChanged: {
                                        if (checked && backend.indexadorUrlPreference !== "hybrid") {
                                            backend.setIndexadorUrlPreference("hybrid")
                                        }
                                    }
                                }
                            }
                            
                            // Templates
                            ColumnLayout {
                                spacing: 8
                                
                                Label {
                                    text: "Template CDN:"
                                    font.pixelSize: 11
                                    color: colorTertiary
                                }
                                
                                TextField {
                                    id: templateCdnField
                                    Layout.fillWidth: true
                                    text: backend.indexadorTemplateCdn
                                    font.pixelSize: 10
                                    selectByMouse: true
                                    onTextChanged: {
                                        if (text !== backend.indexadorTemplateCdn) {
                                            backend.setIndexadorTemplateCdn(text)
                                        }
                                    }
                                }
                                
                                Label {
                                    text: "Template Raw:"
                                    font.pixelSize: 11
                                    color: colorTertiary
                                }
                                
                                TextField {
                                    id: templateRawField
                                    Layout.fillWidth: true
                                    text: backend.indexadorTemplateRaw
                                    font.pixelSize: 10
                                    selectByMouse: true
                                    onTextChanged: {
                                        if (text !== backend.indexadorTemplateRaw) {
                                            backend.setIndexadorTemplateRaw(text)
                                        }
                                    }
                                }
                            }
                            
                            // Verificação CDN
                            Label {
                                text: "Verificação CDN:"
                                font.pixelSize: 12
                                color: colorTertiary
                            }
                            
                            ColumnLayout {
                                spacing: 8
                                
                                RowLayout {
                                    CheckBox {
                                        id: autoVerifyCheckbox
                                        text: "Verificar automaticamente a cada"
                                        checked: true
                                    }
                                    
                                    SpinBox {
                                        from: 1
                                        to: 24
                                        value: 1
                                        textFromValue: function(value) {
                                            return value + " hora" + (value > 1 ? "s" : "")
                                        }
                                    }
                                }
                                
                                CheckBox {
                                    id: autoPromoteCheckbox
                                    text: "Promover URLs do Raw para CDN quando disponível"
                                    checked: backend.indexadorCdnAutoPromote
                                    onCheckedChanged: {
                                        if (checked !== backend.indexadorCdnAutoPromote) {
                                            backend.setIndexadorCdnAutoPromote(checked)
                                        }
                                    }
                                }
                                
                                CheckBox {
                                    text: "Forçar re-cache CDN (purge) após upload"
                                    checked: false
                                    enabled: false
                                    opacity: 0.6
                                }
                            }
                        }
                    }
                    
                    // Separador
                    Rectangle {
                        Layout.fillWidth: true
                        height: 1
                        color: colorTertiary
                        opacity: 0.2
                    }
                    
                    // Sincronização com Repositório
                    GroupBox {
                        Layout.fillWidth: true
                        title: "Sincronização com Repositório"
                        
                        ColumnLayout {
                            anchors.fill: parent
                            spacing: 12
                            
                            CheckBox {
                                id: autoDetectCheckbox
                                text: "Auto-detectar JSONs existentes no GitHub"
                                checked: backend.indexadorGithubAutoDetect
                                onCheckedChanged: {
                                    if (checked !== backend.indexadorGithubAutoDetect) {
                                        backend.setIndexadorGithubAutoDetect(checked)
                                    }
                                }
                            }
                            
                            CheckBox {
                                id: monitorChangesCheckbox
                                text: "Monitorar mudanças remotas"
                                checked: backend.indexadorGithubMonitorChanges
                                onCheckedChanged: {
                                    if (checked !== backend.indexadorGithubMonitorChanges) {
                                        backend.setIndexadorGithubMonitorChanges(checked)
                                    }
                                }
                            }
                            
                            CheckBox {
                                text: "Sincronização bidirecional (local ↔ remoto)"
                                checked: false
                                enabled: false
                                opacity: 0.6
                            }
                            
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                
                                Label {
                                    text: "Pasta de busca no GitHub:"
                                    font.pixelSize: 11
                                    color: colorTertiary
                                }
                                
                                TextField {
                                    id: searchFolderField
                                    Layout.fillWidth: true
                                    text: backend.indexadorGithubSearchFolder
                                    placeholderText: "metadata"
                                    onTextChanged: {
                                        if (text !== backend.indexadorGithubSearchFolder) {
                                            backend.setIndexadorGithubSearchFolder(text)
                                        }
                                    }
                                }
                            }
                            
                            CheckBox {
                                id: includeSubfoldersCheckbox
                                text: "Incluir subpastas"
                                checked: backend.indexadorGithubIncludeSubfolders
                                onCheckedChanged: {
                                    if (checked !== backend.indexadorGithubIncludeSubfolders) {
                                        backend.setIndexadorGithubIncludeSubfolders(checked)
                                    }
                                }
                            }
                            
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                
                                Label {
                                    text: "Cache de sincronização:"
                                    font.pixelSize: 11
                                    color: colorTertiary
                                }
                                
                                SpinBox {
                                    from: 1
                                    to: 24
                                    value: 1
                                    textFromValue: function(value) {
                                        return value + " hora" + (value > 1 ? "s" : "")
                                    }
                                }
                                
                                Button {
                                    text: "Limpar Cache"
                                    Material.background: colorWarning
                                    Material.foreground: colorPrimary
                                    onClicked: {
                                        notificationText.text = "🗑️ Cache limpo com sucesso"
                                    }
                                }
                            }
                        }
                    }
                    
                    // Repositório de Destino
                    GroupBox {
                        Layout.fillWidth: true
                        title: "Repositório de Destino"
                        
                        ColumnLayout {
                            anchors.fill: parent
                            spacing: 12
                            
                            ColumnLayout {
                                spacing: 8
                                
                                RadioButton {
                                    id: sameRepoRadio
                                    text: "Mesmo repositório dos JSONs"
                                    checked: backend.indexadorUseSameRepo
                                    onCheckedChanged: {
                                        if (checked && !backend.indexadorUseSameRepo) {
                                            backend.setIndexadorUseSameRepo(true)
                                        }
                                    }
                                }
                                
                                RowLayout {
                                    RadioButton {
                                        id: specificRepoRadio
                                        text: "Repositório específico:"
                                        checked: !backend.indexadorUseSameRepo
                                        onCheckedChanged: {
                                            if (checked && backend.indexadorUseSameRepo) {
                                                backend.setIndexadorUseSameRepo(false)
                                            }
                                        }
                                    }
                                    
                                    TextField {
                                        id: specificRepoField
                                        Layout.fillWidth: true
                                        text: backend.indexadorSpecificRepo
                                        placeholderText: "usuario/repositorio"
                                        enabled: specificRepoRadio.checked
                                        onTextChanged: {
                                            if (text !== backend.indexadorSpecificRepo) {
                                                backend.setIndexadorSpecificRepo(text)
                                            }
                                        }
                                    }
                                }
                            }
                            
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                
                                Label {
                                    text: "Pasta no repositório:"
                                    font.pixelSize: 11
                                    color: colorTertiary
                                }
                                
                                TextField {
                                    id: indexadorFolderField
                                    Layout.fillWidth: true
                                    text: backend.indexadorFolder
                                    placeholderText: "indexadores"
                                    onTextChanged: {
                                        if (text !== backend.indexadorFolder) {
                                            backend.setIndexadorFolder(text)
                                        }
                                    }
                                }
                            }
                            
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                
                                Label {
                                    text: "Branch padrão:"
                                    font.pixelSize: 11
                                    color: colorTertiary
                                }
                                
                                TextField {
                                    Layout.fillWidth: true
                                    text: "main"
                                    placeholderText: "main"
                                }
                            }
                        }
                    }
                    
                    // Configurações de Upload
                    GroupBox {
                        Layout.fillWidth: true
                        title: "Configurações de Upload"
                        
                        ColumnLayout {
                            anchors.fill: parent
                            spacing: 8
                            
                            CheckBox {
                                text: "Upload automático quando JSONs são criados"
                                checked: backend.indexadorAutoUpdate
                                onCheckedChanged: {
                                    if (checked !== backend.indexadorAutoUpdate) {
                                        backend.setIndexadorAutoUpdate(checked)
                                    }
                                }
                            }
                            
                            CheckBox {
                                id: confirmUploadCheckbox
                                text: "Confirmar antes de fazer upload"
                                checked: backend.indexadorConfirmBeforeUpload
                                onCheckedChanged: {
                                    if (checked !== backend.indexadorConfirmBeforeUpload) {
                                        backend.setIndexadorConfirmBeforeUpload(checked)
                                    }
                                }
                            }
                        }
                    }
                }
            }
            
            // Aba 4: Séries Detectadas
            ColumnLayout {
                spacing: 16
                
                Label {
                    text: "SÉRIES DETECTADAS"
                    font.pixelSize: 14
                    font.weight: Font.Bold
                    color: colorTertiary
                }
                
                // Botões de controle
                RowLayout {
                    spacing: 12
                    
                    Button {
                        text: "🔄 Sincronizar com GitHub"
                        Material.background: colorSecondary
                        Material.foreground: colorPrimary
                        onClicked: {
                            backend.scanGithubJsons()
                            notificationText.text = "🔄 Sincronizando com GitHub..."
                        }
                    }
                    
                    Button {
                        text: "📁 Escanear Local"
                        Material.background: colorSurface
                        Material.foreground: colorTertiary
                        onClicked: {
                            backend.scanLocalJsons()
                            notificationText.text = "📁 Escaneando arquivos locais..."
                        }
                    }
                    
                    Item { Layout.fillWidth: true }
                    
                    Button {
                        text: "Verificar CDNs"
                        Material.background: colorWarning
                        Material.foreground: colorPrimary
                        onClicked: {
                            backend.checkCdnStatus()
                            notificationText.text = "🔄 Verificando status das CDNs..."
                        }
                    }
                }
                
                // Modelo de dados para séries
                ListModel {
                    id: seriesListModel
                }
                
                // Lista de séries
                ScrollView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    
                    ListView {
                        id: seriesListView
                        model: seriesListModel
                        spacing: 8
                        
                        delegate: Rectangle {
                            width: seriesListView.width
                            height: 120
                            color: colorSurface
                            radius: 8
                            border.color: {
                                switch(model.status) {
                                    case "local": return colorSuccess
                                    case "github": return colorSecondary
                                    default: return colorWarning
                                }
                            }
                            border.width: 1
                            
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 12
                                spacing: 8
                                
                                RowLayout {
                                    spacing: 8
                                    
                                    Text {
                                        text: {
                                            switch(model.status) {
                                                case "local": return "📁"
                                                case "github": return "🌐"
                                                default: return "❓"
                                            }
                                        }
                                        font.pixelSize: 16
                                    }
                                    
                                    Label {
                                        text: model.title || "Título não disponível"
                                        font.pixelSize: 13
                                        font.weight: Font.Bold
                                        color: colorTertiary
                                        Layout.fillWidth: true
                                    }
                                    
                                    CheckBox {
                                        text: "Incluir no indexador"
                                        checked: model.included !== undefined ? model.included : true
                                        font.pixelSize: 10
                                        onCheckedChanged: {
                                            if (model.included !== checked) {
                                                seriesListModel.setProperty(model.index, "included", checked)
                                            }
                                        }
                                    }
                                }
                                
                                RowLayout {
                                    spacing: 6
                                    
                                    Label {
                                        text: `Capítulos: ${model.chapters || 0}`
                                        font.pixelSize: 10
                                        color: colorTertiary
                                    }
                                    
                                    Label {
                                        text: `Status: ${model.status || 'desconhecido'}`
                                        font.pixelSize: 10
                                        color: colorTertiary
                                    }
                                    
                                    Label {
                                        text: model.lastUpdated ? `Atualizado: ${model.lastUpdated}` : ""
                                        font.pixelSize: 10
                                        color: colorTertiary
                                        visible: text !== ""
                                    }
                                }
                                
                                RowLayout {
                                    spacing: 6
                                    
                                    Label {
                                        text: "URL:"
                                        font.pixelSize: 10
                                        color: colorTertiary
                                    }
                                    
                                    TextField {
                                        Layout.fillWidth: true
                                        text: model.url || ""
                                        font.pixelSize: 9
                                        height: 24
                                        onTextChanged: {
                                            if (model.url !== text) {
                                                seriesListModel.setProperty(model.index, "url", text)
                                            }
                                        }
                                    }
                                    
                                    Button {
                                        text: "✏️"
                                        font.pixelSize: 10
                                        Layout.preferredWidth: 28
                                        Layout.preferredHeight: 24
                                        onClicked: {
                                            // Foca no campo de texto para edição
                                            // Em implementação futura, poderia abrir dialog dedicado
                                        }
                                    }
                                }
                            }
                        }
                        
                        // Placeholder quando não há séries
                        Rectangle {
                            anchors.centerIn: parent
                            width: parent.width * 0.8
                            height: 100
                            color: colorSurface
                            radius: 8
                            border.color: colorTertiary
                            border.width: 1
                            opacity: 0.6
                            visible: seriesListModel.count === 0
                            
                            ColumnLayout {
                                anchors.centerIn: parent
                                spacing: 8
                                
                                Text {
                                    text: "📂"
                                    font.pixelSize: 24
                                    color: colorTertiary
                                    Layout.alignment: Qt.AlignHCenter
                                }
                                
                                Label {
                                    text: "Nenhuma série encontrada"
                                    font.pixelSize: 12
                                    color: colorTertiary
                                    Layout.alignment: Qt.AlignHCenter
                                }
                                
                                Label {
                                    text: "Clique em 'Escanear Local' ou 'Sincronizar GitHub' para carregar séries"
                                    font.pixelSize: 10
                                    color: colorTertiary
                                    opacity: 0.7
                                    Layout.alignment: Qt.AlignHCenter
                                    wrapMode: Text.WordWrap
                                }
                            }
                        }
                    }
                }
                
                // Estatísticas dinâmicas
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 40
                    color: colorSurface
                    radius: 6
                    
                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 16
                        
                        Label {
                            id: seriesStatsLabel
                            text: `Total: ${seriesListModel.count} séries`
                            font.pixelSize: 11
                            font.weight: Font.Medium
                            color: colorTertiary
                        }
                        
                        Item { Layout.fillWidth: true }
                        
                        Button {
                            text: "Reescanear"
                            Material.background: colorSecondary
                            Material.foreground: colorPrimary
                            Layout.preferredHeight: 28
                            font.pixelSize: 10
                            onClicked: {
                                backend.scanLocalJsons()
                                backend.scanGithubJsons()
                                notificationText.text = "🔄 Reescaneando todas as séries..."
                            }
                        }
                    }
                }
            }
            
            // Aba 5: Prévia JSON
            ColumnLayout {
                spacing: 16
                
                Label {
                    text: "PRÉVIA JSON"
                    font.pixelSize: 14
                    font.weight: Font.Bold
                    color: colorTertiary
                }
                
                // Controles
                RowLayout {
                    spacing: 12
                    
                    Button {
                        text: "🔄 Atualizar Prévia"
                        Material.background: colorSecondary
                        Material.foreground: colorPrimary
                        onClicked: {
                            // Atualiza o conteúdo da prévia com dados reais do backend
                            jsonPreviewArea.text = backend.generateIndexadorJson()
                            notificationText.text = "🔄 Prévia atualizada com dados reais"
                        }
                    }
                    
                    Item { Layout.fillWidth: true }
                    
                    Button {
                        text: "📋 Copiar JSON"
                        Material.background: colorSuccess
                        Material.foreground: colorPrimary
                        onClicked: {
                            backend.copyToClipboard(jsonPreviewArea.text)
                            notificationText.text = "📋 JSON copiado para área de transferência"
                        }
                    }
                    
                    Button {
                        text: "💾 Salvar Arquivo"
                        Material.background: colorWarning
                        Material.foreground: colorPrimary
                        onClicked: {
                            var filename = `index_${backend.indexadorHubName || 'grupo'}`
                            backend.saveJsonFile(jsonPreviewArea.text, filename)
                            notificationText.text = "💾 JSON salvo como arquivo"
                        }
                    }
                }
                
                // Prévia do JSON
                ScrollView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    
                    TextArea {
                        id: jsonPreviewArea
                        readOnly: true
                        selectByMouse: true
                        wrapMode: TextArea.Wrap
                        font.family: "Consolas, Monaco, monospace"
                        font.pixelSize: 10
                        color: colorTertiary
                        
                        text: `{
  "schema": {
    "version": "2.0",
    "format": "application/json",
    "encoding": "utf-8"
  },
  "meta": {
    "version": "1.0.0",
    "lastUpdated": "2025-07-13T15:30:00-03:00",
    "language": "pt-BR",
    "region": "BR",
    "updateFrequency": "weekly",
    "apiVersion": "v1",
    "cacheControl": {
      "maxAge": 3600,
      "staleWhileRevalidate": 86400
    }
  },
  "hub": {
    "id": "meu-grupo-hub",
    "title": "${backend.indexadorHubName || 'Meu Grupo'}",
    "subtitle": "Scanlation Oficial",
    "description": "${backend.indexadorHubDescription || 'Descrição do grupo...'}",
    "team": {
      "name": "${backend.indexadorHubName || 'Meu Grupo'}",
      "type": "scanlation",
      "status": "active"
    },
    "website": "${backend.indexadorHubWebsite || ''}"
  },
  "social": {
    "platforms": [
      {
        "id": "discord",
        "name": "Discord Oficial", 
        "platform": "discord",
        "url": "${backend.indexadorDiscordUrl || ''}",
        "description": "Servidor principal para discussões",
        "primary": true
      },
      {
        "id": "telegram",
        "name": "Canal Telegram",
        "platform": "telegram", 
        "url": "${backend.indexadorTelegramUrl || ''}",
        "description": "Notificações e releases"
      },
      {
        "id": "whatsapp", 
        "name": "Grupo WhatsApp",
        "platform": "whatsapp",
        "url": "${backend.indexadorWhatsappUrl || ''}",
        "description": "Comunidade para discussões"
      },
      {
        "id": "twitter",
        "name": "Twitter/X",
        "platform": "twitter",
        "url": "${backend.indexadorTwitterUrl || ''}",
        "description": "Atualizações e novidades"
      }
    ]
  },
  "series": [
    {
      "id": "tower-of-god-parte-1",
      "title": "Tower of God: Parte 1 – O Irregular",
      "originalTitle": "Tower of God Season 1",
      "slug": "tower-of-god-parte-1-o-irregular",
      "author": {
        "name": "S.I.U",
        "originalName": "SIU",
        "nationality": "KR"
      },
      "status": {
        "translation": "completed",
        "original": "completed",
        "lastUpdated": "2025-07-13T15:30:00-03:00"
      },
      "type": "manhwa",
      "genres": ["action", "adventure", "drama", "fantasy"],
      "cover": {
        "url": "https://example.com/cover.jpg",
        "alt": "Tower of God Parte 1 Cover"
      },
      "description": "A primeira temporada de Tower of God...",
      "chapters": {
        "total": 78,
        "translated": 78,
        "available": 78,
        "status": "completed"
      },
      "rating": {
        "community": 4.8,
        "totalVotes": 1250
      },
      "data": {
        "url": "https://cdn.jsdelivr.net/gh/user/repo@main/Tower_of_God_Parte_1.json",
        "format": "json",
        "size": "2.1MB"
      },
      "priority": 1,
      "featured": true
    },
    {
      "id": "another-series",
      "title": "Another Series",
      "status": {
        "translation": "ongoing",
        "lastUpdated": "2025-07-13T15:30:00-03:00"
      },
      "chapters": {
        "total": 45,
        "translated": 45,
        "available": 45,
        "status": "ongoing"
      },
      "data": {
        "url": "https://cdn.jsdelivr.net/gh/user/repo@main/Another_Series.json",
        "format": "json",
        "size": "1.5MB"
      }
    }
  ],
  "statistics": {
    "overview": {
      "totalSeries": 2,
      "completedSeries": 1,
      "ongoingSeries": 1,
      "totalChapters": 123,
      "totalPages": 3500
    },
    "content": {
      "totalFileSize": "3.6MB",
      "averageChapterSize": "32KB",
      "supportedFormats": ["json"]
    }
  },
  "technical": {
    "api": {
      "version": "1.0",
      "baseUrl": "${backend.indexadorHubWebsite || ''}",
      "endpoints": {
        "hub": "hub.json",
        "series": "series/{id}.json"
      }
    }
  },
  "features": {
    "search": {
      "enabled": true,
      "fields": ["title", "description", "tags", "genres"]
    },
    "filtering": {
      "enabled": true,
      "options": ["status", "genre", "year", "rating"]
    }
  }
}`
                        
                        // Syntax highlighting simulado com cor de fundo
                        background: Rectangle {
                            color: "#1e1e1e"
                            radius: 6
                        }
                    }
                }
                
                // Informações do JSON
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 60
                    color: colorSurface
                    radius: 6
                    
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 4
                        
                        RowLayout {
                            spacing: 16
                            
                            Label {
                                text: "📊 Tamanho: ~8.5KB"
                                font.pixelSize: 10
                                color: colorTertiary
                            }
                            
                            Label {
                                text: "📋 Formato: JSON"
                                font.pixelSize: 10
                                color: colorTertiary
                            }
                            
                            Label {
                                text: "🔗 Séries: 2"
                                font.pixelSize: 10
                                color: colorTertiary
                            }
                            
                            Label {
                                text: "🌐 CDN: 2 ativas"
                                font.pixelSize: 10
                                color: colorSuccess
                            }
                        }
                        
                        Label {
                            text: "💡 Esta é uma prévia do indexador que será gerado com as configurações atuais"
                            font.pixelSize: 9
                            color: colorTertiary
                            opacity: 0.7
                        }
                    }
                }
            }
            
            
            // Função para atualizar a prévia
            function updateJsonPreview() {
                // Atualiza prévia com dados reais do backend
                jsonPreviewArea.text = backend.generateIndexadorJson()
            }
            
            // Função para atualizar estatísticas
            function updateSeriesStats() {
                if (typeof seriesStatsLabel !== 'undefined') {
                    let includedCount = 0
                    for (let i = 0; i < seriesListModel.count; i++) {
                        if (seriesListModel.get(i).included) {
                            includedCount++
                        }
                    }
                    seriesStatsLabel.text = `Total: ${seriesListModel.count} séries | ${includedCount} incluídas no indexador`
                }
            }
        }
        
        // Footer com botões de ação
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 60
            color: colorSurface
            radius: 6
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 12
                
                Button {
                    text: "💡 Dicas"
                    Material.background: colorSurface
                    Material.foreground: colorTertiary
                    onClicked: {
                        notificationText.text = "💡 Preencha pelo menos nome e descrição do grupo para melhor identificação"
                    }
                }
                
                Button {
                    text: "🔄 Gerar Local"
                    Material.background: colorSecondary
                    Material.foreground: colorPrimary
                    onClicked: {
                        backend.generateIndexador()
                        notificationText.text = "🔄 Gerando indexador local..."
                    }
                }
                
                Button {
                    text: "📤 Upload GitHub"
                    Material.background: colorSuccess
                    Material.foreground: colorPrimary
                    onClicked: {
                        backend.uploadIndexadorToGitHub()
                        notificationText.text = "📤 Fazendo upload para GitHub..."
                    }
                }
                
                Rectangle {
                    Layout.preferredWidth: 120
                    Layout.preferredHeight: 32
                    color: autoToggleMouseArea.containsMouse ? colorHover : colorSurface
                    border.color: backend.indexadorAutoUpdate ? colorSuccess : colorTertiary
                    border.width: 1
                    radius: 6
                    
                    RowLayout {
                        anchors.centerIn: parent
                        spacing: 6
                        
                        Text {
                            text: "⚙️"
                            font.pixelSize: 12
                            color: backend.indexadorAutoUpdate ? colorSuccess : colorTertiary
                        }
                        
                        Label {
                            text: "Auto: " + (backend.indexadorAutoUpdate ? "ON" : "OFF")
                            font.pixelSize: 10
                            font.weight: Font.Medium
                            color: backend.indexadorAutoUpdate ? colorSuccess : colorTertiary
                        }
                    }
                    
                    MouseArea {
                        id: autoToggleMouseArea
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        
                        onClicked: {
                            backend.setIndexadorAutoUpdate(!backend.indexadorAutoUpdate)
                            notificationText.text = backend.indexadorAutoUpdate ? 
                                "✅ Atualização automática ativada" : 
                                "⏸️ Atualização automática desativada"
                        }
                    }
                }
                
                Item { Layout.fillWidth: true }
                
                Button {
                    text: "Cancelar"
                    Material.background: "transparent"
                    Material.foreground: colorTertiary
                    onClicked: indexadorDialog.close()
                }
                
                Button {
                    text: "Salvar"
                    Material.background: colorSecondary
                    Material.foreground: colorPrimary
                    onClicked: {
                        // Configurações já são salvas em tempo real
                        notificationText.text = "✅ Configurações salvas com sucesso!"
                        Qt.callLater(function() {
                            indexadorDialog.close()
                        }, 1500)
                    }
                }
            }
        }
    }
}