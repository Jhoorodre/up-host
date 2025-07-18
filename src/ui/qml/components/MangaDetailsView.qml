import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

/**
 * MangaDetailsView - Tela de detalhes do mangá com lista de capítulos
 * Baseado no FRONTEND_MAP_MODERN.md
 */
Rectangle {
    id: root
    
    // ===== PUBLIC PROPERTIES =====
    property var mangaData: null
    property bool isLoading: false
    
    // ===== DESIGN SYSTEM =====
    DesignSystem { id: ds }
    
    // ===== LAYOUT =====
    color: "transparent"
    
    ColumnLayout {
        anchors.fill: parent
        spacing: ds.space6
        
        // ===== HEADER COM NAVEGAÇÃO =====
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: ds.space12
            radius: ds.radius_lg
            color: ds.bgCard
            border.color: ds.border
            border.width: 1
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: ds.space4
                spacing: ds.space4
                
                // Botão Voltar
                ModernButton {
                    text: "Voltar"
                    icon: "◀"
                    variant: "ghost"
                    size: "sm"
                    
                    onClicked: {
                        root.backClicked()
                    }
                }
                
                // Título do mangá
                Text {
                    text: mangaData ? mangaData.title : "Carregando..."
                    font.pixelSize: ds.text_2xl
                    font.weight: ds.fontBold
                    color: ds.textPrimary
                    Layout.fillWidth: true
                    elide: Text.ElideRight
                }
                
                // Informações rápidas
                Rectangle {
                    Layout.preferredWidth: 200
                    Layout.preferredHeight: ds.space8
                    radius: ds.radius_md
                    color: ds.bgSurface
                    border.color: ds.border
                    border.width: 1
                    
                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: ds.space2
                        spacing: ds.space3
                        
                        Text {
                            text: "📑"
                            font.pixelSize: ds.text_sm
                        }
                        
                        Text {
                            text: chapterModel.rowCount() + " capítulos"
                            font.pixelSize: ds.text_sm
                            color: ds.textSecondary
                            Layout.fillWidth: true
                        }
                        
                        // Status badge
                        Rectangle {
                            width: ds.space2
                            height: ds.space2
                            radius: ds.space1
                            color: ds.success
                        }
                    }
                }
                
                // Botão upload principal
                ModernButton {
                    text: "Upload Selecionados"
                    icon: "📤"
                    variant: "primary"
                    size: "sm"
                    enabled: mangaData && chapterModel.rowCount() > 0
                    
                    onClicked: {
                        root.uploadChaptersClicked()
                    }
                }
            }
        }
        
        // ===== INFORMAÇÕES DO MANGÁ =====
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 180
            radius: ds.radius_lg
            color: ds.bgCard
            border.color: ds.border
            border.width: 1
            visible: mangaData
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: ds.space6
                spacing: ds.space6
                
                // Cover Image
                Rectangle {
                    Layout.preferredWidth: 120
                    Layout.preferredHeight: 160
                    radius: ds.radius_md
                    color: ds.bgSurface
                    border.color: ds.border
                    border.width: 1
                    clip: true
                    
                    Image {
                        anchors.fill: parent
                        anchors.margins: 1
                        source: mangaData ? mangaData.coverUrl || "" : ""
                        fillMode: Image.PreserveAspectCrop
                        visible: mangaData && mangaData.coverUrl && mangaData.coverUrl !== ""
                        smooth: true
                        cache: true
                        asynchronous: true
                    }
                    
                    // Fallback cover
                    Rectangle {
                        anchors.fill: parent
                        visible: !mangaData || !mangaData.coverUrl
                        
                        gradient: Gradient {
                            GradientStop { position: 0.0; color: ds.accent }
                            GradientStop { position: 1.0; color: ds.accentHover }
                        }
                        
                        Text {
                            anchors.centerIn: parent
                            text: mangaData ? mangaData.title.charAt(0).toUpperCase() : "?"
                            font.pixelSize: ds.text_3xl
                            font.weight: ds.fontBold
                            color: ds.textPrimary
                        }
                    }
                }
                
                // Manga Info
                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    spacing: ds.space3
                    
                    // Title
                    Text {
                        text: mangaData ? mangaData.title : "Carregando..."
                        font.pixelSize: ds.text_xl
                        font.weight: ds.fontBold
                        color: ds.textPrimary
                        Layout.fillWidth: true
                        wrapMode: Text.WordWrap
                        maximumLineCount: 2
                        elide: Text.ElideRight
                    }
                    
                    // Metadata grid
                    GridLayout {
                        Layout.fillWidth: true
                        columns: 2
                        columnSpacing: ds.space4
                        rowSpacing: ds.space2
                        
                        Text {
                            text: "📁 Pasta:"
                            font.pixelSize: ds.text_sm
                            color: ds.textSecondary
                        }
                        
                        Text {
                            text: mangaData ? mangaData.path : ""
                            font.pixelSize: ds.text_sm
                            color: ds.textSecondary
                            Layout.fillWidth: true
                            elide: Text.ElideMiddle
                        }
                        
                        Text {
                            text: "📊 Status:"
                            font.pixelSize: ds.text_sm
                            color: ds.textSecondary
                        }
                        
                        Text {
                            text: "Em andamento"
                            font.pixelSize: ds.text_sm
                            color: ds.success
                        }
                        
                        Text {
                            text: "📅 Última atualização:"
                            font.pixelSize: ds.text_sm
                            color: ds.textSecondary
                        }
                        
                        Text {
                            text: "Hoje"
                            font.pixelSize: ds.text_sm
                            color: ds.textSecondary
                        }
                    }
                    
                    Item { Layout.fillHeight: true }
                    
                    // Quick stats
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: ds.space4
                        
                        Rectangle {
                            Layout.preferredWidth: 80
                            Layout.preferredHeight: ds.space6
                            radius: ds.radius_sm
                            color: ds.bgSurface
                            border.color: ds.border
                            border.width: 1
                            
                            Text {
                                anchors.centerIn: parent
                                text: chapterModel.rowCount() + " caps"
                                font.pixelSize: ds.text_xs
                                color: ds.textSecondary
                            }
                        }
                        
                        Rectangle {
                            Layout.preferredWidth: 80
                            Layout.preferredHeight: ds.space6
                            radius: ds.radius_sm
                            color: ds.bgSurface
                            border.color: ds.border
                            border.width: 1
                            
                            Text {
                                anchors.centerIn: parent
                                text: "~2.5GB"
                                font.pixelSize: ds.text_xs
                                color: ds.textSecondary
                            }
                        }
                        
                        Item { Layout.fillWidth: true }
                    }
                }
            }
        }
        
        // ===== LISTA DE CAPÍTULOS =====
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
                
                // Header da lista
                RowLayout {
                    Layout.fillWidth: true
                    
                    Text {
                        text: "📑 Lista de Capítulos"
                        font.pixelSize: ds.text_lg
                        font.weight: ds.fontMedium
                        color: ds.textPrimary
                    }
                    
                    Item { Layout.fillWidth: true }
                    
                    // Filtros rápidos
                    ModernButton {
                        text: "Todos"
                        variant: "ghost"
                        size: "sm"
                        
                        onClicked: {
                            // TODO: Selecionar todos os capítulos
                            console.log("Select all chapters")
                        }
                    }
                    
                    ModernButton {
                        text: "Nenhum"
                        variant: "ghost"
                        size: "sm"
                        
                        onClicked: {
                            // TODO: Desselecionar todos os capítulos
                            console.log("Deselect all chapters")
                        }
                    }
                    
                    ModernButton {
                        text: "Inverter"
                        variant: "ghost"
                        size: "sm"
                        
                        onClicked: {
                            // TODO: Inverter seleção
                            console.log("Invert selection")
                        }
                    }
                }
                
                // Lista de capítulos
                ModernChapterList {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    
                    model: chapterModel
                    
                    onChapterClicked: function(name) {
                        console.log("Chapter clicked:", name)
                    }
                    
                    onChapterUploadClicked: function(name) {
                        console.log("Upload single chapter:", name)
                        // Open single chapter upload dialog
                        singleChapterUploadDialog.chapterName = name
                        singleChapterUploadDialog.open()
                    }
                    
                    onChapterEditClicked: function(name) {
                        console.log("Edit chapter:", name)
                        // Open chapter metadata editor
                        root.chapterEditRequested(name)
                    }
                    
                    onUploadSelected: {
                        console.log("Upload selected chapters")
                        root.uploadChaptersClicked()
                    }
                    
                    onProcessSelected: {
                        console.log("Process selected chapters")
                        root.uploadChaptersClicked()
                    }
                    
                    onAllSelected: {
                        console.log("All chapters selected")
                    }
                    
                    onAllUnselected: {
                        console.log("All chapters unselected")
                    }
                    
                    onOrderInverted: function(inverted) {
                        console.log("Order inverted:", inverted)
                    }
                }
            }
        }
    }
    
    // ===== LOADING OVERLAY =====
    Rectangle {
        anchors.fill: parent
        color: Qt.rgba(ds.bgPrimary.r, ds.bgPrimary.g, ds.bgPrimary.b, 0.8)
        visible: isLoading
        
        ColumnLayout {
            anchors.centerIn: parent
            spacing: ds.space4
            
            Rectangle {
                Layout.preferredWidth: ds.space12
                Layout.preferredHeight: ds.space12
                radius: ds.space6
                color: ds.accent
                Layout.alignment: Qt.AlignHCenter
                
                RotationAnimation on rotation {
                    running: isLoading
                    duration: 1000
                    loops: Animation.Infinite
                    from: 0
                    to: 360
                }
            }
            
            Text {
                text: "Carregando capítulos..."
                font.pixelSize: ds.text_base
                color: ds.textPrimary
                Layout.alignment: Qt.AlignHCenter
            }
        }
    }
    
    // ===== SINGLE CHAPTER UPLOAD DIALOG =====
    Dialog {
        id: singleChapterUploadDialog
        width: Math.min(window.width * 0.8, 600)
        height: Math.min(window.height * 0.7, 500)
        anchors.centerIn: parent
        
        property string chapterName: ""
        
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
                spacing: ds.space4
                
                Text {
                    text: "📤"
                    font.pixelSize: ds.text_2xl
                }
                
                Text {
                    text: "UPLOAD DE CAPÍTULO"
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
                        singleChapterUploadDialog.close()
                    }
                }
            }
            
            // Chapter info
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 80
                radius: ds.radius_md
                color: ds.bgCard
                border.color: ds.border
                border.width: 1
                
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: ds.space4
                    spacing: ds.space4
                    
                    Text {
                        text: "📑"
                        font.pixelSize: ds.text_xl
                    }
                    
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: ds.space1
                        
                        Text {
                            text: singleChapterUploadDialog.chapterName
                            font.pixelSize: ds.text_lg
                            font.weight: ds.fontBold
                            color: ds.textPrimary
                        }
                        
                        Text {
                            text: "De: " + (mangaData ? mangaData.title : "")
                            font.pixelSize: ds.text_sm
                            color: ds.textSecondary
                        }
                    }
                }
            }
            
            // Host selection
            ColumnLayout {
                Layout.fillWidth: true
                spacing: ds.space3
                
                Text {
                    text: "🌐 Host de Upload"
                    font.pixelSize: ds.text_base
                    font.weight: ds.fontMedium
                    color: ds.textPrimary
                }
                
                ModernDropdown {
                    id: hostDropdown
                    Layout.fillWidth: true
                    model: ["Catbox", "Imgur", "ImgBB", "Gofile", "Pixeldrain", "Lensdump", "ImageChest", "Imgbox", "ImgHippo", "ImgPile"]
                    currentIndex: 0
                    size: "lg"
                }
            }
            
            // Quick settings
            ColumnLayout {
                Layout.fillWidth: true
                spacing: ds.space3
                
                Text {
                    text: "⚙️ Configurações Rápidas"
                    font.pixelSize: ds.text_base
                    font.weight: ds.fontMedium
                    color: ds.textPrimary
                }
                
                RowLayout {
                    Layout.fillWidth: true
                    spacing: ds.space4
                    
                    CheckBox {
                        text: "Otimizar imagens"
                        checked: false
                        font.pixelSize: ds.text_sm
                    }
                    
                    CheckBox {
                        text: "Gerar JSON"
                        checked: true
                        font.pixelSize: ds.text_sm
                    }
                    
                    CheckBox {
                        text: "Backup local"
                        checked: true
                        font.pixelSize: ds.text_sm
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
                        singleChapterUploadDialog.close()
                    }
                }
                
                ModernButton {
                    text: "Iniciar Upload"
                    icon: "📤"
                    variant: "primary"
                    size: "lg"
                    Layout.fillWidth: true
                    
                    onClicked: {
                        var selectedHost = hostDropdown.model[hostDropdown.currentIndex]
                        console.log("Starting single chapter upload:", singleChapterUploadDialog.chapterName, "to", selectedHost)
                        
                        // Call backend upload function
                        if (backend.uploadSingleChapter) {
                            backend.uploadSingleChapter(singleChapterUploadDialog.chapterName, selectedHost)
                        }
                        
                        singleChapterUploadDialog.close()
                        root.uploadSingleChapter(singleChapterUploadDialog.chapterName)
                    }
                }
            }
        }
    }
    
    // ===== SIGNALS =====
    signal backClicked()
    signal uploadChaptersClicked()
    signal uploadSingleChapter(string chapterName)
    signal editChapter(string chapterName)
    signal chapterEditRequested(string chapterName)
}