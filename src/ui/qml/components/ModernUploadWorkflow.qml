import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

/**
 * ModernUploadWorkflow - Interface de upload completa com workflow steps
 * Baseado exatamente no Item 6 do FRONTEND_MAP_MODERN.md
 */
Rectangle {
    id: root
    
    // ===== PUBLIC PROPERTIES =====
    property int currentStep: 1
    property int totalSteps: 5
    property string selectedHost: "Catbox"
    property var selectedChapters: []
    property bool isProcessing: false
    property real uploadProgress: 0.0
    property var currentManga: null
    property var hostSettings: {
        "workers": 5,
        "rate_limit": 2,
        "quality": 3,
        "sync_mode": "replace_all"
    }
    
    // ===== JOB TRACKING =====
    property var activeJobs: []
    property var completedJobs: []
    property var failedJobs: []
    
    // ===== ERROR HANDLING =====
    property string errorMessage: ""
    property string errorDetails: ""
    property string warningMessage: ""
    property bool hasError: false
    property bool hasWarning: false
    
    // ===== VALIDATION =====
    property bool isValid: false
    property var validationErrors: []
    
    // ===== DESIGN SYSTEM =====
    DesignSystem { id: ds }
    
    // ===== SIGNALS =====
    signal cancelled()
    signal uploadStarted()
    signal uploadCompleted()
    
    // ===== BACKEND CONNECTIONS =====
    Connections {
        target: backend
        
        function onProcessingStarted() {
            console.log("Upload processing started")
            isProcessing = true
            clearErrors()
        }
        
        function onProcessingFinished() {
            console.log("Upload processing finished")
            isProcessing = false
            uploadProgress = 1.0
            uploadCompleted()
        }
        
        function onProgressChanged(progress) {
            console.log("Upload progress:", progress)
            uploadProgress = progress
        }
        
        function onJobStatusChanged(jobId, status, progress, message) {
            console.log("Job status changed:", jobId, status, progress, message)
            updateJobStatus(jobId, status, progress, message)
        }
        
        function onJobCompleted(jobId, result) {
            console.log("Job completed:", jobId, result)
            updateJobResult(jobId, result)
        }
        
        function onJobFailed(jobId, error) {
            console.log("Job failed:", jobId, error)
            updateJobError(jobId, error)
        }
        
        function onError(message, details) {
            console.log("Upload error:", message, "Details:", details)
            isProcessing = false
            hasError = true
            errorMessage = message || "Erro desconhecido durante o upload"
            errorDetails = details || ""
            
            // Specific error handling
            if (message.includes("API")) {
                errorMessage = "Erro de API: " + message
            } else if (message.includes("network") || message.includes("connection")) {
                errorMessage = "Erro de conexão: Verifique sua internet"
            } else if (message.includes("permission") || message.includes("auth")) {
                errorMessage = "Erro de autenticação: Verifique suas credenciais"
            } else if (message.includes("file") || message.includes("chapter")) {
                errorMessage = "Erro de arquivo: " + message
            }
        }
        
        function onWarning(message) {
            console.log("Upload warning:", message)
            hasWarning = true
            warningMessage = message
        }
        
        function onValidationFailed(errors) {
            console.log("Validation failed:", errors)
            isValid = false
            validationErrors = errors || []
        }
        
        function onValidationPassed() {
            console.log("Validation passed")
            isValid = true
            validationErrors = []
            clearErrors()
        }
        
        function onHostConfigurationChanged(hostName, config) {
            console.log("Host configuration changed:", hostName, config)
            if (hostName === selectedHost) {
                loadHostSettings(hostName)
            }
        }
    }
    
    // ===== LAYOUT =====
    color: ds.bgPrimary
    radius: ds.radius_lg
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: ds.space8
        spacing: ds.space8
        
        // ===== HEADER =====
        RowLayout {
            Layout.fillWidth: true
            spacing: ds.space4
            
            Text {
                text: "📤"
                font.pixelSize: ds.text_2xl
            }
            
            Text {
                text: "UPLOAD WORKFLOW"
                font.pixelSize: ds.text_xl
                font.weight: ds.fontBold
                color: ds.textPrimary
            }
            
            Item { Layout.fillWidth: true }
            
            ModernButton {
                text: "Cancelar"
                icon: "❌"
                variant: "danger"
                size: "sm"
                
                onClicked: {
                    root.cancelled()
                }
            }
        }
        
        // ===== PROGRESS STEPS =====
        Rectangle {
            Layout.fillWidth: true
            height: ds.space16
            radius: ds.radius_lg
            color: ds.bgCard
            border.color: ds.border
            border.width: 1
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: ds.space6
                spacing: ds.space4
                
                // Step 1: Manga Selection
                StepIndicator {
                    stepNumber: 1
                    stepTitle: "Manga Selection"
                    isActive: currentStep === 1
                    isCompleted: currentStep > 1
                    Layout.fillWidth: true
                }
                
                StepConnector { isCompleted: currentStep > 1 }
                
                // Step 2: Chapter Selection
                StepIndicator {
                    stepNumber: 2
                    stepTitle: "Chapter Selection"
                    isActive: currentStep === 2
                    isCompleted: currentStep > 2
                    Layout.fillWidth: true
                }
                
                StepConnector { isCompleted: currentStep > 2 }
                
                // Step 3: Host & Settings
                StepIndicator {
                    stepNumber: 3
                    stepTitle: "Host & Settings"
                    isActive: currentStep === 3
                    isCompleted: currentStep > 3
                    Layout.fillWidth: true
                }
                
                StepConnector { isCompleted: currentStep > 3 }
                
                // Step 4: Metadata
                StepIndicator {
                    stepNumber: 4
                    stepTitle: "Metadata"
                    isActive: currentStep === 4
                    isCompleted: currentStep > 4
                    Layout.fillWidth: true
                }
                
                StepConnector { isCompleted: currentStep > 4 }
                
                // Step 5: Upload & Generate
                StepIndicator {
                    stepNumber: 5
                    stepTitle: "Upload & Generate"
                    isActive: currentStep === 5
                    isCompleted: false
                    Layout.fillWidth: true
                }
            }
        }
        
        // ===== MAIN CONTENT AREA =====
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: ds.radius_lg
            color: ds.bgCard
            border.color: ds.border
            border.width: 1
            
            StackLayout {
                anchors.fill: parent
                anchors.margins: ds.space6
                currentIndex: currentStep - 1
                
                // ===== STEP 1: MANGA SELECTION =====
                ColumnLayout {
                    spacing: ds.space6
                    
                    Text {
                        text: "📚 SELEÇÃO DE MANGÁ"
                        font.pixelSize: ds.text_xl
                        font.weight: ds.fontBold
                        color: ds.textPrimary
                        Layout.alignment: Qt.AlignHCenter
                    }
                    
                    // Manga info card
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 120
                        radius: ds.radius_md
                        color: ds.bgSurface
                        border.color: ds.border
                        border.width: 1
                        
                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: ds.space4
                            spacing: ds.space4
                            
                            // Cover placeholder
                            Rectangle {
                                Layout.preferredWidth: 80
                                Layout.preferredHeight: 100
                                radius: ds.radius_sm
                                color: ds.accent
                                
                                Text {
                                    anchors.centerIn: parent
                                    text: currentManga ? currentManga.title.charAt(0).toUpperCase() : "?"
                                    font.pixelSize: ds.text_2xl
                                    font.weight: ds.fontBold
                                    color: ds.textPrimary
                                }
                            }
                            
                            ColumnLayout {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                spacing: ds.space2
                                
                                Text {
                                    text: currentManga ? currentManga.title : "Nenhum mangá selecionado"
                                    font.pixelSize: ds.text_lg
                                    font.weight: ds.fontBold
                                    color: ds.textPrimary
                                }
                                
                                Text {
                                    text: "📁 " + (currentManga ? currentManga.path : "")
                                    font.pixelSize: ds.text_sm
                                    color: ds.textSecondary
                                    elide: Text.ElideMiddle
                                    Layout.fillWidth: true
                                }
                                
                                Text {
                                    text: "📑 " + chapterModel.rowCount() + " capítulos disponíveis"
                                    font.pixelSize: ds.text_sm
                                    color: ds.textSecondary
                                }
                                
                                Item { Layout.fillHeight: true }
                            }
                            
                            Text {
                                text: "✅"
                                font.pixelSize: ds.text_2xl
                                color: ds.success
                            }
                        }
                    }
                    
                    Text {
                        text: "✅ Mangá selecionado. Prossiga para a seleção de capítulos."
                        font.pixelSize: ds.text_base
                        color: ds.success
                        Layout.alignment: Qt.AlignHCenter
                    }
                    
                    Item { Layout.fillHeight: true }
                }
                
                // ===== STEP 2: CHAPTER SELECTION =====
                ColumnLayout {
                    spacing: ds.space6
                    
                    Text {
                        text: "📑 SELEÇÃO DE CAPÍTULOS"
                        font.pixelSize: ds.text_xl
                        font.weight: ds.fontBold
                        color: ds.textPrimary
                        Layout.alignment: Qt.AlignHCenter
                    }
                    
                    // Chapter selection summary
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 80
                        radius: ds.radius_md
                        color: ds.bgSurface
                        border.color: ds.border
                        border.width: 1
                        
                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: ds.space4
                            spacing: ds.space4
                            
                            Text {
                                text: "📊"
                                font.pixelSize: ds.text_2xl
                            }
                            
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: ds.space1
                                
                                Text {
                                    text: "Capítulos selecionados para upload"
                                    font.pixelSize: ds.text_base
                                    font.weight: ds.fontMedium
                                    color: ds.textPrimary
                                }
                                
                                Text {
                                    text: getSelectedChapterCount() + " de " + chapterModel.rowCount() + " capítulos selecionados"
                                    font.pixelSize: ds.text_sm
                                    color: ds.textSecondary
                                }
                                
                                Text {
                                    text: "~" + getEstimatedSize() + " de dados para upload"
                                    font.pixelSize: ds.text_sm
                                    color: ds.textSecondary
                                }
                            }
                            
                            ModernButton {
                                text: "Ajustar Seleção"
                                icon: "✏️"
                                variant: "ghost"
                                size: "sm"
                                
                                onClicked: {
                                    // TODO: Open chapter selection dialog
                                    console.log("Open chapter selection")
                                }
                            }
                        }
                    }
                    
                    // Chapter validation
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: getChapterValidationHeight()
                        radius: ds.radius_md
                        color: getChapterValidationColor()
                        border.color: getChapterValidationBorderColor()
                        border.width: 1
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: ds.space4
                            spacing: ds.space2
                            
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: ds.space3
                                
                                Text {
                                    text: getChapterValidationIcon()
                                    font.pixelSize: ds.text_lg
                                }
                                
                                Text {
                                    text: getChapterValidationTitle()
                                    font.pixelSize: ds.text_base
                                    font.weight: ds.fontMedium
                                    color: ds.textPrimary
                                    Layout.fillWidth: true
                                }
                            }
                            
                            Text {
                                text: getChapterValidationMessage()
                                font.pixelSize: ds.text_sm
                                color: ds.textSecondary
                                Layout.fillWidth: true
                                wrapMode: Text.WordWrap
                                visible: getChapterValidationMessage().length > 0
                            }
                            
                            // Chapter validation details
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: ds.space4
                                visible: getSelectedChapterCount() > 0
                                
                                Text {
                                    text: "📊 " + getSelectedChapterCount() + " capítulos"
                                    font.pixelSize: ds.text_sm
                                    color: ds.textSecondary
                                }
                                
                                Text {
                                    text: "💾 ~" + getEstimatedSize()
                                    font.pixelSize: ds.text_sm
                                    color: ds.textSecondary
                                }
                                
                                Text {
                                    text: "⏱️ ~" + getEstimatedTime()
                                    font.pixelSize: ds.text_sm
                                    color: ds.textSecondary
                                }
                            }
                        }
                    }
                    
                    Item { Layout.fillHeight: true }
                }
                
                // ===== STEP 3: HOST & SETTINGS =====
                ColumnLayout {
                    spacing: ds.space6
                    
                    Text {
                        text: "🎯 HOST DE UPLOAD"
                        font.pixelSize: ds.text_xl
                        font.weight: ds.fontBold
                        color: ds.textPrimary
                        Layout.alignment: Qt.AlignHCenter
                    }
                    
                    // Host Selection Grid (exatamente como no MD)
                    GridLayout {
                        Layout.fillWidth: true
                        Layout.alignment: Qt.AlignHCenter
                        columns: {
                            if (parent.width <= 400) return 2
                            if (parent.width <= ds.mobile) return 3
                            if (parent.width <= ds.tablet) return 4
                            if (parent.width <= ds.desktop) return 6
                            return 8
                        }
                        columnSpacing: ds.space3
                        rowSpacing: ds.space4
                        
                        Repeater {
                            model: hostModel
                            
                            HostCard {
                                hostName: model.name
                                hostIcon: getHostIcon(model.name)
                                selected: selectedHost === model.name
                                enabled: model.enabled
                                status: model.status || "Ativo"
                                
                                onClicked: {
                                    if (model.enabled) {
                                        selectedHost = model.name
                                        // Load host-specific settings
                                        loadHostSettings(model.name)
                                    }
                                }
                                
                                onConfigClicked: {
                                    openHostConfig(model.name)
                                }
                            }
                        }
                    }
                    
                    // Host-Specific Configuration
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 120
                        radius: ds.radius_md
                        color: ds.bgSurface
                        border.color: ds.border
                        border.width: 1
                        visible: selectedHost
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: ds.space4
                            spacing: ds.space3
                            
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: ds.space3
                                
                                Text {
                                    text: "🔧 CONFIGURAÇÕES DO " + selectedHost.toUpperCase()
                                    font.pixelSize: ds.text_base
                                    font.weight: ds.fontBold
                                    color: ds.textPrimary
                                }
                                
                                Item { Layout.fillWidth: true }
                                
                                ModernButton {
                                    text: "Configurar"
                                    icon: "⚙️"
                                    variant: "ghost"
                                    size: "sm"
                                    
                                    onClicked: {
                                        openHostConfig(selectedHost)
                                    }
                                }
                            }
                            
                            // Host-specific settings preview
                            GridLayout {
                                Layout.fillWidth: true
                                columns: 3
                                columnSpacing: ds.space4
                                rowSpacing: ds.space2
                                
                                Text {
                                    text: "Status:"
                                    font.pixelSize: ds.text_sm
                                    color: ds.textSecondary
                                }
                                
                                Text {
                                    text: getHostStatus(selectedHost)
                                    font.pixelSize: ds.text_sm
                                    color: getHostStatusColor(selectedHost)
                                    font.weight: ds.fontMedium
                                }
                                
                                Rectangle {
                                    width: ds.space2
                                    height: ds.space2
                                    radius: ds.space1
                                    color: getHostStatusColor(selectedHost)
                                }
                                
                                Text {
                                    text: "API Key:"
                                    font.pixelSize: ds.text_sm
                                    color: ds.textSecondary
                                }
                                
                                Text {
                                    text: getHostApiStatus(selectedHost)
                                    font.pixelSize: ds.text_sm
                                    color: ds.textSecondary
                                }
                                
                                Item {}
                                
                                Text {
                                    text: "Rate Limit:"
                                    font.pixelSize: ds.text_sm
                                    color: ds.textSecondary
                                }
                                
                                Text {
                                    text: hostSettings.rate_limit + "s"
                                    font.pixelSize: ds.text_sm
                                    color: ds.textSecondary
                                }
                                
                                Item {}
                            }
                        }
                    }
                    
                    // Advanced Settings
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: ds.space4
                        
                        Text {
                            text: "⚙️ CONFIGURAÇÕES AVANÇADAS"
                            font.pixelSize: ds.text_lg
                            font.weight: ds.fontBold
                            color: ds.textPrimary
                        }
                        
                        // Workers Setting
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: ds.space4
                            
                            Text {
                                text: "Workers:"
                                font.pixelSize: ds.text_base
                                color: ds.textPrimary
                                Layout.preferredWidth: 80
                            }
                            
                            Row {
                                spacing: ds.space1
                                Repeater {
                                    model: 5
                                    Rectangle {
                                        width: ds.space4
                                        height: ds.space4
                                        radius: ds.space4 / 2
                                        color: index < hostSettings.workers ? ds.accent : ds.border
                                        
                                        MouseArea {
                                            anchors.fill: parent
                                            onClicked: hostSettings.workers = index + 1
                                        }
                                    }
                                }
                            }
                            
                            Text {
                                text: hostSettings.workers.toString()
                                font.pixelSize: ds.text_sm
                                color: ds.textSecondary
                            }
                            
                            Item { Layout.fillWidth: true }
                            
                            Text {
                                text: "Rate Limit:"
                                font.pixelSize: ds.text_base
                                color: ds.textPrimary
                                Layout.preferredWidth: 80
                            }
                            
                            Row {
                                spacing: ds.space1
                                Repeater {
                                    model: 5
                                    Rectangle {
                                        width: ds.space4
                                        height: ds.space4
                                        radius: ds.space4 / 2
                                        color: index < hostSettings.rate_limit ? ds.warning : ds.border
                                        
                                        MouseArea {
                                            anchors.fill: parent
                                            onClicked: hostSettings.rate_limit = index + 1
                                        }
                                    }
                                }
                            }
                            
                            Text {
                                text: hostSettings.rate_limit + "s"
                                font.pixelSize: ds.text_sm
                                color: ds.textSecondary
                            }
                            
                            Item { Layout.fillWidth: true }
                            
                            Text {
                                text: "Quality:"
                                font.pixelSize: ds.text_base
                                color: ds.textPrimary
                                Layout.preferredWidth: 80
                            }
                            
                            Row {
                                spacing: ds.space1
                                Repeater {
                                    model: 5
                                    Rectangle {
                                        width: ds.space4
                                        height: ds.space4
                                        radius: ds.space4 / 2
                                        color: index < hostSettings.quality ? ds.success : ds.border
                                        
                                        MouseArea {
                                            anchors.fill: parent
                                            onClicked: hostSettings.quality = index + 1
                                        }
                                    }
                                }
                            }
                        }
                    }
                    
                    // Sync Mode
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: ds.space3
                        
                        Text {
                            text: "🔄 MODO DE SINCRONIZAÇÃO"
                            font.pixelSize: ds.text_lg
                            font.weight: ds.fontBold
                            color: ds.textPrimary
                        }
                        
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: ds.space6
                            
                            RadioButton {
                                text: "Adicionar novos"
                                checked: hostSettings.sync_mode === "add_new"
                                font.pixelSize: ds.text_sm
                                onCheckedChanged: if (checked) hostSettings.sync_mode = "add_new"
                            }
                            
                            RadioButton {
                                text: "Substituir todos"
                                checked: hostSettings.sync_mode === "replace_all"
                                font.pixelSize: ds.text_sm
                                onCheckedChanged: if (checked) hostSettings.sync_mode = "replace_all"
                            }
                            
                            RadioButton {
                                text: "Inteligente"
                                checked: hostSettings.sync_mode === "smart"
                                font.pixelSize: ds.text_sm
                                onCheckedChanged: if (checked) hostSettings.sync_mode = "smart"
                            }
                        }
                    }
                    
                    Item { Layout.fillHeight: true }
                }
                
                // ===== STEP 4: METADATA =====
                ColumnLayout {
                    spacing: ds.space6
                    
                    Text {
                        text: "📝 METADADOS"
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
                            spacing: ds.space4
                            
                            // Manga metadata
                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 180
                                radius: ds.radius_md
                                color: ds.bgSurface
                                border.color: ds.border
                                border.width: 1
                                
                                ColumnLayout {
                                    anchors.fill: parent
                                    anchors.margins: ds.space4
                                    spacing: ds.space3
                                    
                                    Text {
                                        text: "📚 Informações do Mangá"
                                        font.pixelSize: ds.text_base
                                        font.weight: ds.fontMedium
                                        color: ds.textPrimary
                                    }
                                    
                                    GridLayout {
                                        Layout.fillWidth: true
                                        columns: 2
                                        columnSpacing: ds.space4
                                        rowSpacing: ds.space3
                                        
                                        Text {
                                            text: "Título:"
                                            font.pixelSize: ds.text_sm
                                            color: ds.textSecondary
                                        }
                                        
                                        ModernInput {
                                            Layout.fillWidth: true
                                            placeholderText: "Título do mangá"
                                            text: currentManga ? currentManga.title : ""
                                        }
                                        
                                        Text {
                                            text: "Autor:"
                                            font.pixelSize: ds.text_sm
                                            color: ds.textSecondary
                                        }
                                        
                                        ModernInput {
                                            Layout.fillWidth: true
                                            placeholderText: "Nome do autor"
                                        }
                                        
                                        Text {
                                            text: "Artista:"
                                            font.pixelSize: ds.text_sm
                                            color: ds.textSecondary
                                        }
                                        
                                        ModernInput {
                                            Layout.fillWidth: true
                                            placeholderText: "Nome do artista"
                                        }
                                        
                                        Text {
                                            text: "Grupo:"
                                            font.pixelSize: ds.text_sm
                                            color: ds.textSecondary
                                        }
                                        
                                        ModernInput {
                                            Layout.fillWidth: true
                                            placeholderText: "Grupo de scanlation"
                                        }
                                    }
                                }
                            }
                            
                            // Upload settings
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
                                        text: "⚙️ Configurações de Upload"
                                        font.pixelSize: ds.text_base
                                        font.weight: ds.fontMedium
                                        color: ds.textPrimary
                                    }
                                    
                                    RowLayout {
                                        Layout.fillWidth: true
                                        spacing: ds.space4
                                        
                                        CheckDelegate {
                                            text: "Gerar JSON automaticamente"
                                            checked: true
                                        }
                                        
                                        CheckDelegate {
                                            text: "Fazer upload para GitHub"
                                            checked: true
                                        }
                                    }
                                    
                                    RowLayout {
                                        Layout.fillWidth: true
                                        spacing: ds.space4
                                        
                                        CheckDelegate {
                                            text: "Otimizar imagens"
                                            checked: false
                                        }
                                        
                                        CheckDelegate {
                                            text: "Criar backup local"
                                            checked: true
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                
                // ===== STEP 5: UPLOAD & GENERATE =====
                ColumnLayout {
                    spacing: ds.space6
                    
                    Text {
                        text: "🚀 UPLOAD & GERAR"
                        font.pixelSize: ds.text_xl
                        font.weight: ds.fontBold
                        color: ds.textPrimary
                        Layout.alignment: Qt.AlignHCenter
                    }
                    
                    // Upload summary
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
                                text: "📋 Resumo do Upload"
                                font.pixelSize: ds.text_base
                                font.weight: ds.fontMedium
                                color: ds.textPrimary
                            }
                            
                            GridLayout {
                                Layout.fillWidth: true
                                columns: 2
                                columnSpacing: ds.space4
                                rowSpacing: ds.space2
                                
                                Text {
                                    text: "Host selecionado:"
                                    font.pixelSize: ds.text_sm
                                    color: ds.textSecondary
                                }
                                
                                Text {
                                    text: selectedHost
                                    font.pixelSize: ds.text_sm
                                    color: ds.accent
                                    font.weight: ds.fontMedium
                                }
                                
                                Text {
                                    text: "Capítulos:"
                                    font.pixelSize: ds.text_sm
                                    color: ds.textSecondary
                                }
                                
                                Text {
                                    text: getSelectedChapterCount() + " selecionados"
                                    font.pixelSize: ds.text_sm
                                    color: ds.textSecondary
                                }
                                
                                Text {
                                    text: "Tamanho estimado:"
                                    font.pixelSize: ds.text_sm
                                    color: ds.textSecondary
                                }
                                
                                Text {
                                    text: getEstimatedSize()
                                    font.pixelSize: ds.text_sm
                                    color: ds.textSecondary
                                }
                            }
                        }
                    }
                    
                    Text {
                        text: isProcessing ? 
                              "🔄 Upload em andamento..." :
                              "✅ Tudo pronto! Clique em 'Iniciar Upload' para começar."
                        font.pixelSize: ds.text_base
                        color: isProcessing ? ds.warning : ds.success
                        Layout.alignment: Qt.AlignHCenter
                        horizontalAlignment: Text.AlignHCenter
                    }
                    
                    // ===== JOB PROGRESS DETAILS =====
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        radius: ds.radius_md
                        color: ds.bgSurface
                        border.color: ds.border
                        border.width: 1
                        visible: isProcessing && (activeJobs.length > 0 || completedJobs.length > 0)
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: ds.space4
                            spacing: ds.space3
                            
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: ds.space3
                                
                                Text {
                                    text: "📊 Status dos Jobs"
                                    font.pixelSize: ds.text_base
                                    font.weight: ds.fontMedium
                                    color: ds.textPrimary
                                }
                                
                                Item { Layout.fillWidth: true }
                                
                                Text {
                                    text: completedJobs.length + "/" + (activeJobs.length + completedJobs.length + failedJobs.length)
                                    font.pixelSize: ds.text_sm
                                    color: ds.textSecondary
                                }
                            }
                            
                            ScrollView {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                
                                ColumnLayout {
                                    width: parent.width
                                    spacing: ds.space2
                                    
                                    // Active Jobs
                                    Repeater {
                                        model: activeJobs
                                        
                                        JobProgressItem {
                                            Layout.fillWidth: true
                                            jobId: modelData.id
                                            jobName: modelData.name
                                            jobStatus: modelData.status
                                            jobProgress: modelData.progress
                                            jobMessage: modelData.message
                                            isActive: true
                                        }
                                    }
                                    
                                    // Completed Jobs
                                    Repeater {
                                        model: completedJobs
                                        
                                        JobProgressItem {
                                            Layout.fillWidth: true
                                            jobId: modelData.id
                                            jobName: modelData.name
                                            jobStatus: "completed"
                                            jobProgress: 1.0
                                            jobMessage: modelData.result || "Concluído"
                                            isActive: false
                                        }
                                    }
                                    
                                    // Failed Jobs
                                    Repeater {
                                        model: failedJobs
                                        
                                        JobProgressItem {
                                            Layout.fillWidth: true
                                            jobId: modelData.id
                                            jobName: modelData.name
                                            jobStatus: "failed"
                                            jobProgress: 0.0
                                            jobMessage: modelData.error || "Falha no upload"
                                            isActive: false
                                        }
                                    }
                                }
                            }
                        }
                    }
                    
                    Item { Layout.fillHeight: true; visible: !isProcessing }
                }
            }
        }
        
        // ===== ERROR/WARNING NOTIFICATIONS =====
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: getNotificationHeight()
            radius: ds.radius_md
            color: hasError ? ds.dangerBg : (hasWarning ? ds.warningBg : "transparent")
            border.color: hasError ? ds.danger : (hasWarning ? ds.warning : "transparent")
            border.width: 1
            visible: hasError || hasWarning
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: ds.space4
                spacing: ds.space3
                
                RowLayout {
                    Layout.fillWidth: true
                    spacing: ds.space3
                    
                    Text {
                        text: hasError ? "❌" : "⚠️"
                        font.pixelSize: ds.text_lg
                    }
                    
                    Text {
                        text: hasError ? "ERRO" : "AVISO"
                        font.pixelSize: ds.text_base
                        font.weight: ds.fontBold
                        color: hasError ? ds.danger : ds.warning
                    }
                    
                    Item { Layout.fillWidth: true }
                    
                    ModernButton {
                        text: "✕"
                        variant: "ghost"
                        size: "sm"
                        iconOnly: true
                        
                        onClicked: {
                            clearErrors()
                        }
                    }
                }
                
                Text {
                    text: hasError ? errorMessage : warningMessage
                    font.pixelSize: ds.text_sm
                    color: ds.textPrimary
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                }
                
                Text {
                    text: errorDetails
                    font.pixelSize: ds.text_xs
                    color: ds.textSecondary
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                    visible: hasError && errorDetails.length > 0
                }
                
                // Action buttons for errors
                RowLayout {
                    Layout.fillWidth: true
                    spacing: ds.space3
                    visible: hasError
                    
                    ModernButton {
                        text: "Tentar Novamente"
                        icon: "🔄"
                        variant: "secondary"
                        size: "sm"
                        
                        onClicked: {
                            retryUpload()
                        }
                    }
                    
                    ModernButton {
                        text: "Reportar Erro"
                        icon: "📝"
                        variant: "ghost"
                        size: "sm"
                        
                        onClicked: {
                            reportError()
                        }
                    }
                }
            }
        }
        
        // ===== UPLOAD PROGRESS =====
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: ds.space12
            radius: ds.radius_md
            color: ds.bgCard
            border.color: ds.border
            border.width: 1
            visible: isProcessing
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: ds.space4
                spacing: ds.space2
                
                RowLayout {
                    Layout.fillWidth: true
                    
                    Text {
                        text: "🔄 Fazendo upload..."
                        font.pixelSize: ds.text_base
                        color: ds.textPrimary
                    }
                    
                    Item { Layout.fillWidth: true }
                    
                    Text {
                        text: Math.round(uploadProgress * 100) + "%"
                        font.pixelSize: ds.text_base
                        color: ds.accent
                    }
                }
                
                // Progress bar
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: ds.space1
                    radius: ds.space1 / 2
                    color: ds.bgSurface
                    
                    Rectangle {
                        anchors.left: parent.left
                        anchors.verticalCenter: parent.verticalCenter
                        width: parent.width * uploadProgress
                        height: parent.height
                        radius: parent.radius
                        color: ds.accent
                        
                        Behavior on width {
                            NumberAnimation { duration: 200 }
                        }
                    }
                }
            }
        }
        
        // ===== BOTTOM NAVIGATION =====
        RowLayout {
            Layout.fillWidth: true
            spacing: ds.space4
            
            ModernButton {
                text: "← Anterior"
                variant: "secondary"
                size: "lg"
                enabled: currentStep > 1 && !isProcessing
                
                onClicked: {
                    if (currentStep > 1) currentStep--
                }
            }
            
            Item { Layout.fillWidth: true }
            
            Text {
                text: isProcessing ? "Processando..." : "Passo " + currentStep + " de " + totalSteps
                font.pixelSize: ds.text_sm
                color: ds.textSecondary
            }
            
            Item { Layout.fillWidth: true }
            
            ModernButton {
                text: currentStep === totalSteps ? "Iniciar Upload" : "Próximo →"
                variant: "primary"
                size: "lg"
                enabled: !isProcessing && canProceed()
                
                onClicked: {
                    if (currentStep < totalSteps) {
                        if (validateCurrentStep()) {
                            currentStep++
                            // Save step configuration
                            saveStepConfiguration()
                        }
                    } else {
                        if (validateAllSteps()) {
                            startUploadProcess()
                        }
                    }
                }
            }
        }
    }
    
    // ===== STEP INDICATOR COMPONENT =====
    component StepIndicator: ColumnLayout {
        property int stepNumber: 1
        property string stepTitle: ""
        property bool isActive: false
        property bool isCompleted: false
        
        spacing: ds.space2
        
        Rectangle {
            width: ds.space8
            height: ds.space8
            radius: ds.space8 / 2
            color: {
                if (isCompleted) return ds.success
                if (isActive) return ds.accent
                return ds.border
            }
            Layout.alignment: Qt.AlignHCenter
            
            Behavior on color {
                ColorAnimation { duration: ds.animationFast }
            }
            
            Text {
                anchors.centerIn: parent
                text: isCompleted ? "✅" : stepNumber.toString()
                font.pixelSize: ds.text_sm
                font.weight: ds.fontBold
                color: (isCompleted || isActive) ? ds.textPrimary : ds.textSecondary
            }
        }
        
        Text {
            text: stepTitle
            font.pixelSize: ds.text_xs
            color: isActive ? ds.textPrimary : ds.textSecondary
            Layout.alignment: Qt.AlignHCenter
            horizontalAlignment: Text.AlignHCenter
        }
    }
    
    // ===== STEP CONNECTOR COMPONENT =====
    component StepConnector: Rectangle {
        property bool isCompleted: false
        
        width: ds.space8
        height: 3
        color: isCompleted ? ds.success : ds.border
        Layout.alignment: Qt.AlignVCenter
        
        Behavior on color {
            ColorAnimation { duration: ds.animationFast }
        }
    }
    
    // ===== HELPER FUNCTIONS =====
    function getSelectedChapterCount() {
        var count = 0
        for (var i = 0; i < chapterModel.rowCount(); i++) {
            var index = chapterModel.index(i, 0)
            var item = chapterModel.data(index, Qt.UserRole + 4) // SelectedRole
            if (item) {
                count++
            }
        }
        return count
    }
    
    function getEstimatedSize() {
        var selectedCount = getSelectedChapterCount()
        var estimatedMB = Math.round(selectedCount * 15) // ~15MB per chapter average
        return estimatedMB > 1000 ? (estimatedMB / 1000).toFixed(1) + "GB" : estimatedMB + "MB"
    }
    
    function getEstimatedTime() {
        var selectedCount = getSelectedChapterCount()
        var baseTimePerChapter = 30 // seconds
        var totalSeconds = selectedCount * baseTimePerChapter * hostSettings.rate_limit
        
        if (totalSeconds < 60) return totalSeconds + "s"
        if (totalSeconds < 3600) return Math.round(totalSeconds / 60) + "min"
        return Math.round(totalSeconds / 3600) + "h"
    }
    
    // ===== VALIDATION FUNCTIONS =====
    function canProceed() {
        switch (currentStep) {
            case 1: return currentManga !== null
            case 2: return getSelectedChapterCount() > 0
            case 3: return selectedHost !== "" && getHostStatus(selectedHost) === "Ativo"
            case 4: return true // Metadata is optional
            case 5: return !hasError
            default: return false
        }
    }
    
    function validateCurrentStep() {
        clearErrors()
        
        switch (currentStep) {
            case 1:
                if (!currentManga) {
                    showError("Nenhum mangá selecionado", "Selecione um mangá antes de continuar.")
                    return false
                }
                return true
                
            case 2:
                if (getSelectedChapterCount() === 0) {
                    showError("Nenhum capítulo selecionado", "Selecione pelo menos um capítulo para upload.")
                    return false
                }
                return true
                
            case 3:
                if (!selectedHost) {
                    showError("Nenhum host selecionado", "Selecione um host de upload.")
                    return false
                }
                if (getHostStatus(selectedHost) !== "Ativo") {
                    showError("Host não disponível", "O host " + selectedHost + " não está configurado corretamente.")
                    return false
                }
                return true
                
            case 4:
                // Metadata validation (optional but can show warnings)
                return true
                
            case 5:
                return validateAllSteps()
                
            default:
                return true
        }
    }
    
    function validateAllSteps() {
        if (!currentManga) {
            showError("Validação falhou", "Nenhum mangá selecionado.")
            return false
        }
        
        if (getSelectedChapterCount() === 0) {
            showError("Validação falhou", "Nenhum capítulo selecionado.")
            return false
        }
        
        if (!selectedHost) {
            showError("Validação falhou", "Nenhum host selecionado.")
            return false
        }
        
        if (getHostStatus(selectedHost) !== "Ativo") {
            showError("Validação falhou", "Host não está disponível.")
            return false
        }
        
        return true
    }
    
    // ===== CHAPTER VALIDATION FUNCTIONS =====
    function getChapterValidationHeight() {
        if (getSelectedChapterCount() === 0) return 80
        return 120
    }
    
    function getChapterValidationColor() {
        if (getSelectedChapterCount() === 0) return ds.warningBg
        return ds.successBg
    }
    
    function getChapterValidationBorderColor() {
        if (getSelectedChapterCount() === 0) return ds.warning
        return ds.success
    }
    
    function getChapterValidationIcon() {
        if (getSelectedChapterCount() === 0) return "⚠️"
        return "✅"
    }
    
    function getChapterValidationTitle() {
        if (getSelectedChapterCount() === 0) return "Nenhum capítulo selecionado"
        return getSelectedChapterCount() + " capítulos prontos para upload"
    }
    
    function getChapterValidationMessage() {
        if (getSelectedChapterCount() === 0) {
            return "Volte à etapa anterior para selecionar os capítulos que deseja fazer upload."
        }
        return "Capítulos validados e prontos para processamento."
    }
    
    // ===== HOST FUNCTIONS =====
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
    
    function getHostStatus(hostName) {
        // Get status from hostModel
        for (var i = 0; i < hostModel.rowCount(); i++) {
            var index = hostModel.index(i, 0)
            var item = hostModel.data(index, Qt.UserRole)
            if (item && item.name === hostName) {
                return item.enabled ? "Ativo" : "Inativo"
            }
        }
        return "Desconhecido"
    }
    
    function getHostStatusColor(hostName) {
        var status = getHostStatus(hostName)
        switch(status) {
            case "Ativo": return ds.success
            case "Inativo": return ds.danger
            default: return ds.warning
        }
    }
    
    function getHostApiStatus(hostName) {
        // Check if host requires API key and if it's configured
        var requiresApi = ["Imgur", "ImgBB", "Lensdump", "ImgHippo", "ImgPile"]
        if (requiresApi.includes(hostName)) {
            return backend.hasApiKey(hostName) ? "Configurada" : "Não configurada"
        }
        return "Não requerida"
    }
    
    function loadHostSettings(hostName) {
        if (backend.getHostSettings) {
            var settings = backend.getHostSettings(hostName)
            if (settings) {
                hostSettings = settings
            }
        }
    }
    
    function openHostConfig(hostName) {
        console.log("Opening host configuration for:", hostName)
        if (backend.openHostConfiguration) {
            backend.openHostConfiguration(hostName)
        }
    }
    
    // ===== ERROR HANDLING FUNCTIONS =====
    function showError(message, details) {
        hasError = true
        errorMessage = message
        errorDetails = details || ""
        hasWarning = false
    }
    
    function showWarning(message) {
        hasWarning = true
        warningMessage = message
        hasError = false
    }
    
    function clearErrors() {
        hasError = false
        hasWarning = false
        errorMessage = ""
        errorDetails = ""
        warningMessage = ""
    }
    
    function getNotificationHeight() {
        if (!hasError && !hasWarning) return 0
        if (hasError && errorDetails.length > 0) return 140
        return 100
    }
    
    function retryUpload() {
        clearErrors()
        if (validateAllSteps()) {
            startUploadProcess()
        }
    }
    
    function reportError() {
        console.log("Reporting error:", errorMessage, errorDetails)
        // TODO: Implement error reporting
        if (backend.reportError) {
            backend.reportError(errorMessage, errorDetails)
        }
    }
    
    // ===== JOB MANAGEMENT FUNCTIONS =====
    function updateJobStatus(jobId, status, progress, message) {
        // Update active jobs
        for (var i = 0; i < activeJobs.length; i++) {
            if (activeJobs[i].id === jobId) {
                activeJobs[i].status = status
                activeJobs[i].progress = progress
                activeJobs[i].message = message
                activeJobs = activeJobs.slice() // Trigger property change
                return
            }
        }
        
        // If not found in active jobs, add new job
        if (status !== "completed" && status !== "failed") {
            activeJobs.push({
                id: jobId,
                name: jobId, // Use jobId as name for now
                status: status,
                progress: progress,
                message: message
            })
            activeJobs = activeJobs.slice() // Trigger property change
        }
    }
    
    function updateJobResult(jobId, result) {
        // Move from active to completed
        for (var i = 0; i < activeJobs.length; i++) {
            if (activeJobs[i].id === jobId) {
                var job = activeJobs[i]
                job.result = result
                completedJobs.push(job)
                activeJobs.splice(i, 1)
                
                // Trigger property changes
                activeJobs = activeJobs.slice()
                completedJobs = completedJobs.slice()
                break
            }
        }
    }
    
    function updateJobError(jobId, error) {
        // Move from active to failed
        for (var i = 0; i < activeJobs.length; i++) {
            if (activeJobs[i].id === jobId) {
                var job = activeJobs[i]
                job.error = error
                failedJobs.push(job)
                activeJobs.splice(i, 1)
                
                // Trigger property changes
                activeJobs = activeJobs.slice()
                failedJobs = failedJobs.slice()
                break
            }
        }
    }
    
    function clearJobHistory() {
        activeJobs = []
        completedJobs = []
        failedJobs = []
    }
    
    // ===== UPLOAD FUNCTIONS =====
    function startUploadProcess() {
        clearErrors()
        clearJobHistory()
        isProcessing = true
        uploadProgress = 0.0
        uploadStarted()
        
        // Get selected chapters
        var selectedChapterNames = []
        for (var i = 0; i < chapterModel.rowCount(); i++) {
            var index = chapterModel.index(i, 0)
            var item = chapterModel.data(index, Qt.UserRole)
            if (item && item.selected) {
                selectedChapterNames.push(item.name)
            }
        }
        
        if (selectedChapterNames.length > 0) {
            console.log("Starting upload for chapters:", selectedChapterNames)
            backend.startUpload(selectedChapterNames, selectedHost, hostSettings)
        } else {
            showError("Erro de validação", "Nenhum capítulo selecionado para upload.")
            isProcessing = false
        }
    }
    
    function uploadSingleChapter(chapterName) {
        console.log("Starting single chapter upload:", chapterName)
        clearErrors()
        
        if (!selectedHost || getHostStatus(selectedHost) !== "Ativo") {
            showError("Host não configurado", "Configure um host antes de fazer upload.")
            return
        }
        
        isProcessing = true
        uploadProgress = 0.0
        
        if (backend.uploadSingleChapter) {
            backend.uploadSingleChapter(chapterName, selectedHost, hostSettings)
        }
    }
    
    // ===== CONFIGURATION PERSISTENCE =====
    function saveStepConfiguration() {
        var config = {
            "step": currentStep,
            "selectedHost": selectedHost,
            "hostSettings": hostSettings,
            "selectedChapters": getSelectedChapterNames(),
            "timestamp": new Date().toISOString()
        }
        
        if (backend.saveUploadConfig) {
            backend.saveUploadConfig(config)
        }
        
        console.log("Saved step configuration:", config)
    }
    
    function loadUploadConfiguration() {
        if (backend.loadUploadConfig) {
            var config = backend.loadUploadConfig()
            if (config) {
                selectedHost = config.selectedHost || "Catbox"
                hostSettings = config.hostSettings || hostSettings
                console.log("Loaded upload configuration:", config)
            }
        }
    }
    
    function getSelectedChapterNames() {
        var names = []
        for (var i = 0; i < chapterModel.rowCount(); i++) {
            var index = chapterModel.index(i, 0)
            var item = chapterModel.data(index, Qt.UserRole)
            if (item && item.selected) {
                names.push(item.name)
            }
        }
        return names
    }
    
    // ===== COMPONENT INITIALIZATION =====
    Component.onCompleted: {
        loadUploadConfiguration()
        if (selectedHost) {
            loadHostSettings(selectedHost)
        }
    }
    
    // ===== JOB PROGRESS ITEM COMPONENT =====
    component JobProgressItem: Rectangle {
        property string jobId: ""
        property string jobName: ""
        property string jobStatus: "pending"
        property real jobProgress: 0.0
        property string jobMessage: ""
        property bool isActive: false
        
        Layout.fillWidth: true
        height: ds.space12
        radius: ds.radius_sm
        color: ds.bgCard
        border.color: ds.border
        border.width: 1
        
        RowLayout {
            anchors.fill: parent
            anchors.margins: ds.space3
            spacing: ds.space3
            
            // Status icon
            Text {
                text: {
                    switch (jobStatus) {
                        case "pending": return "⏳"
                        case "uploading": return "📤"
                        case "processing": return "🔄"
                        case "completed": return "✅"
                        case "failed": return "❌"
                        default: return "❓"
                    }
                }
                font.pixelSize: ds.text_base
                color: {
                    switch (jobStatus) {
                        case "completed": return ds.success
                        case "failed": return ds.danger
                        case "uploading": 
                        case "processing": return ds.warning
                        default: return ds.textSecondary
                    }
                }
            }
            
            // Job info
            ColumnLayout {
                Layout.fillWidth: true
                spacing: ds.space1
                
                Text {
                    text: jobName
                    font.pixelSize: ds.text_sm
                    font.weight: ds.fontMedium
                    color: ds.textPrimary
                    elide: Text.ElideRight
                    Layout.fillWidth: true
                }
                
                Text {
                    text: jobMessage
                    font.pixelSize: ds.text_xs
                    color: ds.textSecondary
                    elide: Text.ElideRight
                    Layout.fillWidth: true
                    visible: jobMessage.length > 0
                }
            }
            
            // Progress indicator
            ColumnLayout {
                Layout.preferredWidth: 60
                spacing: ds.space1
                
                Text {
                    text: Math.round(jobProgress * 100) + "%"
                    font.pixelSize: ds.text_xs
                    color: ds.textSecondary
                    Layout.alignment: Qt.AlignRight
                    visible: isActive
                }
                
                Rectangle {
                    Layout.fillWidth: true
                    height: 3
                    radius: 1.5
                    color: ds.bgSurface
                    visible: isActive
                    
                    Rectangle {
                        anchors.left: parent.left
                        anchors.verticalCenter: parent.verticalCenter
                        width: parent.width * jobProgress
                        height: parent.height
                        radius: parent.radius
                        color: {
                            switch (jobStatus) {
                                case "completed": return ds.success
                                case "failed": return ds.danger
                                default: return ds.accent
                            }
                        }
                        
                        Behavior on width {
                            NumberAnimation { duration: 300 }
                        }
                    }
                }
            }
        }
    }
    
    // ===== HOST CARD COMPONENT =====
    component HostCard: Rectangle {
        property string hostName: ""
        property string hostIcon: ""
        property bool selected: false
        property bool enabled: true
        property string status: "Ativo"
        
        signal clicked()
        signal configClicked()
        
        width: 60
        height: 60
        radius: ds.radius_md
        color: {
            if (!enabled) return ds.bgDisabled
            if (selected) return ds.accent
            if (mouseArea.containsMouse) return ds.hover
            return ds.bgSurface
        }
        border.color: {
            if (!enabled) return ds.borderDisabled
            if (selected) return ds.accent
            return ds.border
        }
        border.width: selected ? 3 : 1
        opacity: enabled ? 1.0 : 0.6
        
        Behavior on color {
            ColorAnimation { duration: ds.animationFast }
        }
        
        Behavior on border.color {
            ColorAnimation { duration: ds.animationFast }
        }
        
        ColumnLayout {
            anchors.centerIn: parent
            spacing: ds.space1
            
            Text {
                text: hostIcon
                font.pixelSize: ds.text_lg
                font.weight: ds.fontBold
                color: selected ? ds.textPrimary : ds.textSecondary
                Layout.alignment: Qt.AlignHCenter
            }
            
            Rectangle {
                visible: selected
                width: ds.space2
                height: ds.space2
                radius: ds.space2 / 2
                color: selected ? ds.textPrimary : "transparent"
                Layout.alignment: Qt.AlignHCenter
            }
        }
        
        Text {
            anchors.bottom: parent.bottom
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottomMargin: -ds.space5
            text: hostName
            font.pixelSize: ds.text_xs
            color: ds.textSecondary
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
            
            onPressAndHold: {
                if (parent.enabled) {
                    parent.configClicked()
                }
            }
        }
    }
}