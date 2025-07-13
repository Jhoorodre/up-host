import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls.Material 2.15
import QtQuick.Dialogs
import Qt.labs.platform 1.1 as Platform

ApplicationWindow {
    id: window
    width: 1200
    height: 800
    visible: true
    title: qsTr("Manga Uploader Pro")
    
    // Custom Color Palette - Alta nitidez e contraste
    readonly property color colorPrimary: "#1a1a1a"      // 70% - Fundo escuro para contraste
    readonly property color colorSecondary: "#0078d4"    // 20% - Azul vibrante para acentos
    readonly property color colorTertiary: "#ffffff"     // 10% - Branco puro para texto (máxima nitidez)
    readonly property color colorSurface: "#2d2d2d"      // Superfícies ligeiramente mais claras
    readonly property color colorHover: "#404040"        // Estados hover sutis
    readonly property color colorSuccess: "#00c851"      // Verde para sucessos
    readonly property color colorWarning: "#ff9500"      // Laranja para avisos
    
    Material.theme: Material.Dark
    Material.accent: colorSecondary
    color: colorPrimary
    
    property var currentManga: null
    property var selectedChapters: []
    property bool isProcessing: false
    
    Component.onCompleted: {
        backend.loadConfig()
        backend.refreshMangaList()
    }
    
    // Connect cookie test result signal
    Connections {
        target: backend
        function onCookieTestResult(resultType, message) {
            testCookieResult.text = message
            if (resultType === "success") {
                testCookieResult.color = colorSuccess
            } else {
                testCookieResult.color = "#ff4444"
            }
        }
    }
    
    header: Rectangle {
        height: 48
        color: colorSurface
        
        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width
            height: 1
            color: colorTertiary
            opacity: 0.1
        }
        
        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 24
            anchors.rightMargin: 24
            
            Label {
                text: "MANGA UPLOADER"
                font.pixelSize: 14
                font.weight: Font.Medium
                font.letterSpacing: 1.2
                color: colorTertiary
            }
            
            Item { Layout.fillWidth: true }
            
            Rectangle {
                Layout.preferredWidth: 160
                Layout.preferredHeight: 32
                color: hostSelectorHovered ? colorSurface : "transparent"
                border.color: hostSelectorHovered ? colorSecondary : colorTertiary
                border.width: 1
                radius: 8
                
                property bool hostSelectorHovered: false
                
                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 8
                    anchors.rightMargin: 4
                    anchors.topMargin: 4
                    anchors.bottomMargin: 4
                    spacing: 6
                    
                    Rectangle {
                        width: 16
                        height: 16
                        radius: 3
                        color: hostSelector.currentText === "Catbox" ? "#ff6b35" : "#1bb76e"
                        Layout.alignment: Qt.AlignVCenter
                        
                        Label {
                            anchors.centerIn: parent
                            text: hostSelector.currentText === "Catbox" ? "C" : "I"
                            font.pixelSize: 8
                            font.weight: Font.Bold
                            color: "white"
                        }
                    }
                    
                    Label {
                        text: "HOST:"
                        font.pixelSize: 8
                        font.weight: Font.Medium
                        font.letterSpacing: 0.5
                        color: colorTertiary
                        opacity: 0.7
                        Layout.alignment: Qt.AlignVCenter
                    }
                    
                    ComboBox {
                        id: hostSelector
                        model: backend.availableHosts
                        enabled: !isProcessing
                        Layout.fillWidth: true
                        Layout.alignment: Qt.AlignVCenter
                        
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
                            font.pixelSize: 10
                            font.weight: Font.Medium
                            color: colorTertiary
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                }
                
                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    onEntered: parent.hostSelectorHovered = true
                    onExited: parent.hostSelectorHovered = false
                    enabled: false
                }
            }
            
            Rectangle {
                id: settingsButton
                Layout.preferredWidth: 80
                Layout.preferredHeight: 32
                color: settingsBtnHovered ? colorSecondary : colorSurface
                border.color: settingsBtnHovered ? colorSecondary : colorTertiary
                border.width: 1
                radius: 8
                
                property bool settingsBtnHovered: false
                
                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 8
                    anchors.rightMargin: 8
                    anchors.topMargin: 4
                    anchors.bottomMargin: 4
                    spacing: 6
                    
                    Rectangle {
                        width: 16
                        height: 16
                        radius: 3
                        color: settingsButton.settingsBtnHovered ? "white" : colorSecondary
                        Layout.alignment: Qt.AlignVCenter
                        
                        Label {
                            id: settingsIcon
                            anchors.centerIn: parent
                            text: "⚙"
                            font.pixelSize: 8
                            color: settingsButton.settingsBtnHovered ? colorSecondary : "white"
                            
                            RotationAnimation {
                                id: settingsRotation
                                target: settingsIcon
                                property: "rotation"
                                running: settingsButton.settingsBtnHovered
                                from: 0
                                to: 360
                                duration: 2000
                                loops: Animation.Infinite
                            }
                        }
                    }
                    
                    Label {
                        text: "AJUSTES"
                        font.pixelSize: 8
                        font.weight: Font.Medium
                        font.letterSpacing: 0.5
                        color: settingsButton.settingsBtnHovered ? "white" : colorTertiary
                        Layout.alignment: Qt.AlignVCenter
                        Layout.fillWidth: true
                    }
                }
                
                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    onEntered: settingsButton.settingsBtnHovered = true
                    onExited: settingsButton.settingsBtnHovered = false
                    onClicked: settingsDrawer.open()
                    enabled: !isProcessing
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
            Layout.preferredWidth: 320
            Layout.fillHeight: true
            color: colorSurface
            
            Rectangle {
                anchors.right: parent.right
                width: 1
                height: parent.height
                color: colorTertiary
                opacity: 0.1
            }
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 16
                
                Label {
                    text: "BIBLIOTECA"
                    font.pixelSize: 12
                    font.weight: Font.Medium
                    font.letterSpacing: 1
                    color: colorTertiary
                    opacity: 0.8
                }
                
                Rectangle {
                    Layout.fillWidth: true
                    height: 32
                    color: colorPrimary
                    border.color: colorTertiary
                    border.width: 1
                    radius: 8
                    
                    TextField {
                        id: searchField
                        anchors.fill: parent
                        anchors.margins: 1
                        placeholderText: "Buscar..."
                        placeholderTextColor: colorTertiary
                        color: colorTertiary
                        font.pixelSize: 12
                        background: Rectangle {
                            color: "transparent"
                        }
                        leftPadding: 12
                        rightPadding: 12
                        onTextChanged: backend.filterMangaList(text)
                    }
                }
                
                ScrollView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    
                    ListView {
                        id: mangaListView
                        model: mangaModel
                        spacing: 2
                        delegate: Rectangle {
                            width: parent ? parent.width : 320
                            height: 104
                            color: hovered ? colorHover : "transparent"
                            
                            property bool hovered: false
                            
                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 12
                                spacing: 12
                                
                                Rectangle {
                                    width: 60
                                    height: 80
                                    radius: 8
                                    color: colorSurface
                                    border.color: colorTertiary
                                    border.width: 1
                                    clip: true
                                    
                                    Image {
                                        anchors.fill: parent
                                        anchors.margins: 1
                                        source: model.coverUrl || ""
                                        fillMode: Image.PreserveAspectCrop
                                        visible: model.coverUrl !== undefined && model.coverUrl !== null && model.coverUrl !== ""
                                        smooth: true
                                        cache: true
                                        asynchronous: true
                                        horizontalAlignment: Image.AlignHCenter
                                        verticalAlignment: Image.AlignTop
                                        sourceSize.width: 120
                                        sourceSize.height: 160
                                        
                                        Component.onCompleted: {
                                            if (model.coverUrl && model.coverUrl !== "") {
                                                console.log("QML: Loading cover for", model.title, ":", model.coverUrl)
                                            }
                                        }
                                        
                                        onStatusChanged: {
                                            if (status === Image.Ready) {
                                                console.log("QML: Cover loaded successfully for", model.title)
                                            } else if (status === Image.Error) {
                                                console.log("QML: Cover failed to load for", model.title)
                                            } else if (status === Image.Loading) {
                                                console.log("QML: Loading cover for", model.title)
                                            }
                                        }
                                        
                                        Rectangle {
                                            anchors.fill: parent
                                            color: colorPrimary
                                            opacity: 0.8
                                            visible: parent.status === Image.Loading
                                            
                                            Rectangle {
                                                anchors.centerIn: parent
                                                width: 16
                                                height: 16
                                                radius: 8
                                                color: colorSecondary
                                                
                                                SequentialAnimation on rotation {
                                                    running: true
                                                    loops: Animation.Infinite
                                                    NumberAnimation { from: 0; to: 360; duration: 1000 }
                                                }
                                            }
                                        }
                                        
                                        Rectangle {
                                            anchors.fill: parent
                                            color: colorWarning
                                            opacity: 0.8
                                            visible: parent.status === Image.Error
                                            
                                            Label {
                                                anchors.centerIn: parent
                                                text: "!"
                                                font.pixelSize: 16
                                                color: "white"
                                            }
                                        }
                                    }
                                    
                                    Rectangle {
                                        anchors.fill: parent
                                        color: colorSecondary
                                        visible: model.coverUrl === undefined || model.coverUrl === null || model.coverUrl === ""
                                        
                                        Label {
                                            anchors.centerIn: parent
                                            text: model.title ? model.title.charAt(0).toUpperCase() : "?"
                                            font.pixelSize: 24
                                            font.weight: Font.Bold
                                            color: "white"
                                        }
                                    }
                                }
                                
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 2
                                    
                                    Label {
                                        text: model.title || "Sem título"
                                        font.pixelSize: 13
                                        font.weight: Font.Medium
                                        color: colorTertiary
                                        elide: Text.ElideRight
                                        Layout.fillWidth: true
                                    }
                                    
                                    Label {
                                        text: (model.chapterCount || 0) + " caps"
                                        font.pixelSize: 10
                                        color: colorTertiary
                                        opacity: 0.6
                                    }
                                }
                                
                                Rectangle {
                                    width: 4
                                    height: 4
                                    radius: 8
                                    color: (model.chapterCount || 0) > 0 ? colorSecondary : colorTertiary
                                    opacity: (model.chapterCount || 0) > 0 ? 1.0 : 0.3
                                }
                            }
                            
                            MouseArea {
                                anchors.fill: parent
                                hoverEnabled: true
                                onEntered: parent.hovered = true
                                onExited: parent.hovered = false
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
            color: colorPrimary
            
            StackLayout {
                anchors.fill: parent
                anchors.margins: 32
                currentIndex: window.currentManga ? 1 : 0
                
                // Welcome Screen
                Item {
                    ColumnLayout {
                        anchors.centerIn: parent
                        spacing: 24
                        
                        Rectangle {
                            width: 120
                            height: 120
                            radius: 8
                            color: colorSurface
                            border.color: colorTertiary
                            border.width: 1
                            Layout.alignment: Qt.AlignHCenter
                            
                            Label {
                                anchors.centerIn: parent
                                text: "MANGA"
                                font.pixelSize: 14
                                font.weight: Font.Medium
                                font.letterSpacing: 2
                                color: colorTertiary
                                opacity: 0.5
                            }
                        }
                        
                        Label {
                            text: "Selecione um mangá da biblioteca"
                            font.pixelSize: 14
                            color: colorTertiary
                            opacity: 0.7
                            Layout.alignment: Qt.AlignHCenter
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
                                radius: 8
                                color: colorSurface
                                border.color: backend.currentMangaHasJson ? colorSecondary : colorTertiary
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
                                        color: colorPrimary
                                        opacity: 0.8
                                        visible: parent.status === Image.Loading
                                        radius: 4
                                        
                                        Rectangle {
                                            anchors.centerIn: parent
                                            width: 20
                                            height: 20
                                            radius: 10
                                            color: colorSecondary
                                            
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
                                    color: colorSecondary
                                    visible: backend.currentMangaCover === ""
                                    
                                    Label {
                                        anchors.centerIn: parent
                                        text: backend.currentMangaTitle ? backend.currentMangaTitle.charAt(0).toUpperCase() : "?"
                                        font.pixelSize: 32
                                        font.weight: Font.Bold
                                        color: "white"
                                    }
                                }
                                
                                // JSON Status Badge
                                Rectangle {
                                    anchors.bottom: parent.bottom
                                    anchors.right: parent.right
                                    anchors.margins: 4
                                    width: 12
                                    height: 12
                                    radius: 8
                                    color: backend.currentMangaHasJson ? colorSecondary : colorTertiary
                                    opacity: backend.currentMangaHasJson ? 1.0 : 0.3
                                }
                            }
                            
                            // Info Column
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                
                                Label {
                                    text: backend.currentMangaTitle || ""
                                    font.pixelSize: 18
                                    font.weight: Font.Medium
                                    color: colorTertiary
                                    elide: Text.ElideRight
                                    Layout.fillWidth: true
                                }
                                
                                Label {
                                    text: backend.currentMangaDescription || ""
                                    font.pixelSize: 12
                                    color: colorTertiary
                                    opacity: 0.7
                                    elide: Text.ElideRight
                                    maximumLineCount: 2
                                    wrapMode: Text.WordWrap
                                    Layout.fillWidth: true
                                    visible: backend.currentMangaDescription !== ""
                                }
                                
                                RowLayout {
                                    spacing: 16
                                    
                                    Label {
                                        text: "ARTISTA: " + (backend.currentMangaArtist || "—")
                                        font.pixelSize: 9
                                        font.weight: Font.Medium
                                        font.letterSpacing: 0.5
                                        color: colorTertiary
                                        opacity: 0.6
                                    }
                                    
                                    Label {
                                        text: "AUTOR: " + (backend.currentMangaAuthor || "—")
                                        font.pixelSize: 9
                                        font.weight: Font.Medium  
                                        font.letterSpacing: 0.5
                                        color: colorTertiary
                                        opacity: 0.6
                                    }
                                    
                                    Label {
                                        text: "STATUS: " + (backend.currentMangaStatus || "—")
                                        font.pixelSize: 9
                                        font.weight: Font.Medium
                                        font.letterSpacing: 0.5
                                        color: colorTertiary
                                        opacity: 0.6
                                    }
                                }
                                
                                Label {
                                    text: backend.currentMangaChapterCount + " CAPÍTULOS " + (backend.currentMangaHasJson ? "• METADADOS" : "• SEM METADADOS")
                                    font.pixelSize: 9
                                    font.weight: Font.Medium
                                    font.letterSpacing: 0.5
                                    color: backend.currentMangaHasJson ? colorSecondary : colorTertiary
                                    opacity: backend.currentMangaHasJson ? 1.0 : 0.6
                                }
                            }
                        }
                        
                        // Chapters Section
                        ColumnLayout {
                            spacing: 12
                            
                            Label {
                                text: "CAPÍTULOS"
                                font.pixelSize: 12
                                font.weight: Font.Medium
                                font.letterSpacing: 1
                                color: colorTertiary
                                opacity: 0.8
                            }
                            
                            ScrollView {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                
                                ListView {
                                    id: chapterListView
                                    model: chapterModel
                                    spacing: 1
                                    delegate: Rectangle {
                                        width: parent ? parent.width : 400
                                        height: 40
                                        color: model.selected ? colorSurface : "transparent"
                                        
                                        RowLayout {
                                            anchors.fill: parent
                                            anchors.margins: 8
                                            spacing: 12
                                            
                                            Rectangle {
                                                width: 16
                                                height: 16
                                                radius: 8
                                                color: "transparent"
                                                border.color: colorTertiary
                                                border.width: 1
                                                
                                                Rectangle {
                                                    anchors.centerIn: parent
                                                    width: 8
                                                    height: 8
                                                    radius: 4
                                                    color: colorSecondary
                                                    visible: model.selected || false
                                                }
                                            }
                                            
                                            Label {
                                                text: model.name || ""
                                                font.pixelSize: 12
                                                color: colorTertiary
                                                Layout.fillWidth: true
                                            }
                                            
                                            Label {
                                                text: (model.imageCount || 0) + " img"
                                                font.pixelSize: 10
                                                color: colorTertiary
                                                opacity: 0.6
                                            }
                                        }
                                        
                                        MouseArea {
                                            anchors.fill: parent
                                            onClicked: {
                                                model.selected = !model.selected
                                            }
                                        }
                                    }
                                }
                            }
                        }
                        
                        // Progress Bar
                        Rectangle {
                            Layout.fillWidth: true
                            height: 2
                            color: colorSurface
                            visible: isProcessing
                            
                            Rectangle {
                                width: parent.width * backend.uploadProgress
                                height: parent.height
                                color: colorSecondary
                            }
                        }
                    }
                    
                    // Vertical Actions Panel
                    Rectangle {
                        Layout.preferredWidth: 140
                        Layout.fillHeight: true
                        color: colorSurface
                        
                        Rectangle {
                            anchors.left: parent.left
                            width: 1
                            height: parent.height
                            color: colorTertiary
                            opacity: 0.1
                        }
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 20
                            spacing: 16
                            
                            Label {
                                text: "AÇÕES"
                                font.pixelSize: 10
                                font.weight: Font.Medium
                                font.letterSpacing: 1
                                color: colorTertiary
                                opacity: 0.6
                                Layout.alignment: Qt.AlignHCenter
                            }
                            
                            // Upload Button
                            Rectangle {
                                Layout.fillWidth: true
                                height: 48
                                radius: 8
                                color: uploadBtnHovered ? colorSecondary : colorSurface
                                border.color: uploadBtnHovered ? colorSecondary : colorTertiary
                                border.width: 1
                                
                                property bool uploadBtnHovered: false
                                
                                RowLayout {
                                    anchors.centerIn: parent
                                    spacing: 8
                                    
                                    Rectangle {
                                        width: 24
                                        height: 24
                                        radius: 4
                                        color: parent.parent.uploadBtnHovered ? "white" : colorSecondary
                                        
                                        Label {
                                            anchors.centerIn: parent
                                            text: isProcessing ? "⟳" : "⬆"
                                            font.pixelSize: 12
                                            color: parent.parent.uploadBtnHovered ? colorSecondary : "white"
                                            
                                            SequentialAnimation on rotation {
                                                running: isProcessing
                                                loops: Animation.Infinite
                                                NumberAnimation { from: 0; to: 360; duration: 1000 }
                                            }
                                        }
                                    }
                                    
                                    Label {
                                        text: isProcessing ? "PROCESSANDO..." : "UPLOAD"
                                        font.pixelSize: 10
                                        font.weight: Font.Medium
                                        font.letterSpacing: 1
                                        color: parent.parent.uploadBtnHovered ? "white" : colorTertiary
                                    }
                                }
                                
                                MouseArea {
                                    id: uploadBtn
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    enabled: !isProcessing && window.currentManga
                                    onEntered: parent.uploadBtnHovered = true
                                    onExited: parent.uploadBtnHovered = false
                                    onClicked: metadataDialog.openForUpload()
                                }
                            }
                            
                            // Edit Button
                            Rectangle {
                                Layout.fillWidth: true
                                height: 48
                                radius: 8
                                color: editBtnHovered ? colorWarning : colorSurface
                                border.color: editBtnHovered ? colorWarning : colorTertiary
                                border.width: 1
                                
                                property bool editBtnHovered: false
                                
                                RowLayout {
                                    anchors.centerIn: parent
                                    spacing: 8
                                    
                                    Rectangle {
                                        width: 24
                                        height: 24
                                        radius: 4
                                        color: parent.parent.editBtnHovered ? "white" : colorWarning
                                        
                                        Label {
                                            anchors.centerIn: parent
                                            text: "✎"
                                            font.pixelSize: 12
                                            color: parent.parent.editBtnHovered ? colorWarning : "white"
                                        }
                                    }
                                    
                                    Label {
                                        text: "EDITAR"
                                        font.pixelSize: 10
                                        font.weight: Font.Medium
                                        font.letterSpacing: 1
                                        color: parent.parent.editBtnHovered ? "white" : colorTertiary
                                    }
                                }
                                
                                MouseArea {
                                    id: editBtn
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    enabled: !isProcessing && window.currentManga
                                    onEntered: parent.editBtnHovered = true
                                    onExited: parent.editBtnHovered = false
                                    onClicked: metadataDialog.openForEdit()
                                }
                            }
                            
                            // GitHub Button
                            Rectangle {
                                Layout.fillWidth: true
                                height: 48
                                radius: 8
                                color: githubBtnHovered ? colorSuccess : colorSurface
                                border.color: githubBtnHovered ? colorSuccess : colorTertiary
                                border.width: 1
                                visible: backend.githubRepo !== ""
                                
                                property bool githubBtnHovered: false
                                
                                RowLayout {
                                    anchors.centerIn: parent
                                    spacing: 8
                                    
                                    Rectangle {
                                        width: 24
                                        height: 24
                                        radius: 4
                                        color: parent.parent.githubBtnHovered ? "white" : colorSuccess
                                        
                                        Label {
                                            anchors.centerIn: parent
                                            text: "⚡"
                                            font.pixelSize: 12
                                            color: parent.parent.githubBtnHovered ? colorSuccess : "white"
                                        }
                                    }
                                    
                                    Label {
                                        text: "GITHUB"
                                        font.pixelSize: 10
                                        font.weight: Font.Medium
                                        font.letterSpacing: 1
                                        color: parent.parent.githubBtnHovered ? "white" : colorTertiary
                                    }
                                }
                                
                                MouseArea {
                                    id: githubBtn
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    enabled: !isProcessing && window.currentManga && backend.currentMangaHasJson
                                    onEntered: parent.githubBtnHovered = true
                                    onExited: parent.githubBtnHovered = false
                                    onClicked: backend.saveToGitHub()
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
        Material.background: colorSurface
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 24
            spacing: 24
            
            RowLayout {
                spacing: 12
                
                Label {
                    text: "CONFIGURAÇÕES"
                    font.pixelSize: 14
                    font.weight: Font.Medium
                    font.letterSpacing: 1.2
                    color: colorTertiary
                }
                
                Item { Layout.fillWidth: true }
                
                Rectangle {
                    width: 24
                    height: 24
                    radius: 8
                    color: closeBtnHovered ? colorHover : "transparent"
                    
                    property bool closeBtnHovered: false
                    
                    Label {
                        anchors.centerIn: parent
                        text: "×"
                        font.pixelSize: 16
                        color: colorTertiary
                    }
                    
                    MouseArea {
                        id: closeBtn
                        anchors.fill: parent
                        hoverEnabled: true
                        onEntered: parent.closeBtnHovered = true
                        onExited: parent.closeBtnHovered = false
                        onClicked: settingsDrawer.close()
                    }
                }
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
                    spacing: 20
                    
                    // Diretórios
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 12
                        
                        Label {
                            text: "DIRETÓRIOS"
                            font.pixelSize: 11
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
                        
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 16
                            
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                
                                Label {
                                    text: "Pasta raiz dos mangás"
                                    font.pixelSize: 12
                                    color: colorTertiary
                                    opacity: 0.8
                                }
                                
                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 8
                                    
                                    Rectangle {
                                        Layout.fillWidth: true
                                        height: 32
                                        color: colorPrimary
                                        border.color: colorTertiary
                                        border.width: 1
                                        radius: 8
                                        
                                        TextField {
                                            id: rootFolderField
                                            anchors.fill: parent
                                            anchors.margins: 1
                                            text: backend.rootFolder
                                            color: colorTertiary
                                            font.pixelSize: 11
                                            background: Rectangle { color: "transparent" }
                                            leftPadding: 8
                                            rightPadding: 8
                                        }
                                    }
                                    
                                    Rectangle {
                                        width: 60
                                        height: 32
                                        radius: 8
                                        color: folderBtnHovered ? colorTertiary : "transparent"
                                        border.color: colorTertiary
                                        border.width: 1
                                        
                                        property bool folderBtnHovered: false
                                        
                                        Label {
                                            anchors.centerIn: parent
                                            text: "..."
                                            font.pixelSize: 12
                                            color: parent.folderBtnHovered ? colorPrimary : colorTertiary
                                        }
                                        
                                        MouseArea {
                                            id: folderBtn
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            onEntered: parent.folderBtnHovered = true
                                            onExited: parent.folderBtnHovered = false
                                            onClicked: folderDialog.open()
                                        }
                                    }
                                }
                            }
                            
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                
                                Label {
                                    text: "Pasta de saída dos metadados"
                                    font.pixelSize: 12
                                    color: colorTertiary
                                    opacity: 0.8
                                }
                                
                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 8
                                    
                                    Rectangle {
                                        Layout.fillWidth: true
                                        height: 32
                                        color: colorPrimary
                                        border.color: colorTertiary
                                        border.width: 1
                                        radius: 8
                                        
                                        TextField {
                                            id: outputFolderField
                                            anchors.fill: parent
                                            anchors.margins: 1
                                            text: backend.outputFolder
                                            color: colorTertiary
                                            font.pixelSize: 11
                                            background: Rectangle { color: "transparent" }
                                            leftPadding: 8
                                            rightPadding: 8
                                        }
                                    }
                                    
                                    Rectangle {
                                        width: 60
                                        height: 32
                                        radius: 8
                                        color: outputFolderBtnHovered ? colorTertiary : "transparent"
                                        border.color: colorTertiary
                                        border.width: 1
                                        
                                        property bool outputFolderBtnHovered: false
                                        
                                        Label {
                                            anchors.centerIn: parent
                                            text: "..."
                                            font.pixelSize: 12
                                            color: parent.outputFolderBtnHovered ? colorPrimary : colorTertiary
                                        }
                                        
                                        MouseArea {
                                            id: outputFolderBtn
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            onEntered: parent.outputFolderBtnHovered = true
                                            onExited: parent.outputFolderBtnHovered = false
                                            onClicked: outputFolderDialog.open()
                                        }
                                    }
                                }
                            }
                        }
                    }
                    
                    // Host Settings
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 12
                        
                        Label {
                            text: "HOST DE UPLOAD"
                            font.pixelSize: 11
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
                        
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 16
                            
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                
                                Label {
                                    text: "Host ativo"
                                    font.pixelSize: 12
                                    color: colorTertiary
                                    opacity: 0.8
                                }
                                
                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 32
                                    color: colorPrimary
                                    border.color: colorTertiary
                                    border.width: 1
                                    radius: 8
                                    
                                    ComboBox {
                                        id: hostCombo
                                        anchors.fill: parent
                                        model: backend.availableHosts
                                        
                                        Component.onCompleted: {
                                            currentIndex = backend.selectedHostIndex
                                        }
                                        
                                        Connections {
                                            target: backend
                                            function onSelectedHostIndexChanged() {
                                                if (hostCombo.currentIndex !== backend.selectedHostIndex) {
                                                    hostCombo.currentIndex = backend.selectedHostIndex
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
                                            text: hostCombo.currentText
                                            font.pixelSize: 12
                                            color: colorTertiary
                                            verticalAlignment: Text.AlignVCenter
                                            leftPadding: 8
                                        }
                                    }
                                }
                            }
                            
                            // Catbox Settings
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                visible: hostCombo.currentText === "Catbox"
                                
                                Label {
                                    text: "Catbox Userhash (opcional)"
                                    font.pixelSize: 12
                                    color: colorTertiary
                                    opacity: 0.8
                                }
                                
                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 32
                                    color: colorPrimary
                                    border.color: colorTertiary
                                    border.width: 1
                                    radius: 8
                                    
                                    TextField {
                                        id: catboxUserhashField
                                        anchors.fill: parent
                                        anchors.margins: 1
                                        text: backend.catboxUserhash
                                        placeholderText: "Se tiver userhash..."
                                        color: colorTertiary
                                        font.pixelSize: 11
                                        background: Rectangle { color: "transparent" }
                                        leftPadding: 8
                                        rightPadding: 8
                                    }
                                }
                            }
                            
                            // Imgur Settings
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                visible: hostCombo.currentText === "Imgur"
                                
                                Label {
                                    text: "Imgur Client ID"
                                    font.pixelSize: 12
                                    color: colorTertiary
                                    opacity: 0.8
                                }
                                
                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 32
                                    color: colorPrimary
                                    border.color: colorTertiary
                                    border.width: 1
                                    radius: 8
                                    
                                    TextField {
                                        id: imgurClientIdField
                                        anchors.fill: parent
                                        anchors.margins: 1
                                        text: backend.imgurClientId
                                        placeholderText: "Client ID do Imgur"
                                        color: colorTertiary
                                        font.pixelSize: 11
                                        background: Rectangle { color: "transparent" }
                                        leftPadding: 8
                                        rightPadding: 8
                                    }
                                }
                                
                                Label {
                                    text: "Imgur Access Token"
                                    font.pixelSize: 12
                                    color: colorTertiary
                                    opacity: 0.8
                                }
                                
                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 32
                                    color: colorPrimary
                                    border.color: colorTertiary
                                    border.width: 1
                                    radius: 8
                                    
                                    TextField {
                                        id: imgurAccessTokenField
                                        anchors.fill: parent
                                        anchors.margins: 1
                                        text: backend.imgurAccessToken
                                        placeholderText: "Access Token do Imgur"
                                        color: colorTertiary
                                        font.pixelSize: 11
                                        background: Rectangle { color: "transparent" }
                                        leftPadding: 8
                                        rightPadding: 8
                                    }
                                }
                            }
                            
                            // ImgBB Settings
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                visible: hostCombo.currentText === "ImgBB"
                                
                                Label {
                                    text: "ImgBB API Key"
                                    font.pixelSize: 12
                                    color: colorTertiary
                                    opacity: 0.8
                                }
                                
                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 32
                                    color: colorPrimary
                                    border.color: colorTertiary
                                    border.width: 1
                                    radius: 8
                                    
                                    TextField {
                                        id: imgbbApiKeyField
                                        anchors.fill: parent
                                        anchors.margins: 1
                                        text: backend.imgbbApiKey
                                        placeholderText: "API Key do ImgBB"
                                        color: colorTertiary
                                        font.pixelSize: 11
                                        background: Rectangle { color: "transparent" }
                                        leftPadding: 8
                                        rightPadding: 8
                                    }
                                }
                            }
                            
                            // ImageChest Settings
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                visible: hostCombo.currentText === "ImageChest"
                                
                                Label {
                                    text: "ImageChest API Key"
                                    font.pixelSize: 12
                                    color: colorTertiary
                                    opacity: 0.8
                                }
                                
                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 32
                                    color: colorPrimary
                                    border.color: colorTertiary
                                    border.width: 1
                                    radius: 8
                                    
                                    TextField {
                                        id: imageChestApiKeyField
                                        anchors.fill: parent
                                        anchors.margins: 1
                                        text: backend.imageChestApiKey
                                        placeholderText: "API Key do ImageChest"
                                        color: colorTertiary
                                        font.pixelSize: 11
                                        background: Rectangle { color: "transparent" }
                                        leftPadding: 8
                                        rightPadding: 8
                                    }
                                }
                            }
                            
                            // Pixeldrain Settings
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                visible: hostCombo.currentText === "Pixeldrain"
                                
                                Label {
                                    text: "Pixeldrain API Key (opcional)"
                                    font.pixelSize: 12
                                    color: colorTertiary
                                    opacity: 0.8
                                }
                                
                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 32
                                    color: colorPrimary
                                    border.color: colorTertiary
                                    border.width: 1
                                    radius: 8
                                    
                                    TextField {
                                        id: pixeldrainApiKeyField
                                        anchors.fill: parent
                                        anchors.margins: 1
                                        text: backend.pixeldrainApiKey
                                        placeholderText: "API Key para recursos premium"
                                        color: colorTertiary
                                        font.pixelSize: 11
                                        background: Rectangle { color: "transparent" }
                                        leftPadding: 8
                                        rightPadding: 8
                                    }
                                }
                            }
                            
                            // Imgbox Settings
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                visible: hostCombo.currentText === "Imgbox"
                                
                                Label {
                                    text: "Session Cookie (opcional)"
                                    font.pixelSize: 12
                                    color: colorSecondary
                                }
                                
                                TextField {
                                    id: imgboxSessionCookieField
                                    Layout.fillWidth: true
                                    placeholderText: "Cole o cookie _imgbox_session para fazer upload na sua conta"
                                    text: backend.imgboxSessionCookie
                                    color: colorPrimary
                                    font.pixelSize: 12
                                    wrapMode: TextInput.Wrap
                                    selectByMouse: true
                                    
                                    background: Rectangle {
                                        color: colorSurface
                                        border.color: colorSecondary
                                        border.width: 1
                                        radius: 4
                                    }
                                }
                                
                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 8
                                    
                                    Button {
                                        id: testCookieBtn
                                        text: "Testar Cookie"
                                        enabled: imgboxSessionCookieField.text.length > 0
                                        font.pixelSize: 10
                                        
                                        background: Rectangle {
                                            color: testCookieBtn.enabled ? (testCookieBtn.hovered ? "#0078d4" : "#005a9e") : "#404040"
                                            border.color: testCookieBtn.enabled ? "#0078d4" : "#606060"
                                            border.width: 1
                                            radius: 4
                                        }
                                        
                                        contentItem: Text {
                                            text: testCookieBtn.text
                                            font: testCookieBtn.font
                                            color: testCookieBtn.enabled ? "white" : "#808080"
                                            horizontalAlignment: Text.AlignHCenter
                                            verticalAlignment: Text.AlignVCenter
                                        }
                                        
                                        onClicked: {
                                            testCookieResult.text = "Testando..."
                                            testCookieResult.color = colorTertiary
                                            backend.testImgboxCookie(imgboxSessionCookieField.text)
                                        }
                                    }
                                    
                                    Label {
                                        id: testCookieResult
                                        text: ""
                                        font.pixelSize: 10
                                        Layout.fillWidth: true
                                        wrapMode: Text.WordWrap
                                    }
                                }
                                
                                Label {
                                    text: "Para fazer upload na sua conta:\n1. Faça login no imgbox.com/upload\n2. Abra Dev Tools (F12) → Application → Cookies\n3. Copie o valor do cookie '_imgbox_session'"
                                    font.pixelSize: 10
                                    color: colorTertiary
                                    opacity: 0.7
                                    wrapMode: Text.WordWrap
                                    Layout.fillWidth: true
                                }
                            }
                            
                            // Info labels for hosts without configuration
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                visible: hostCombo.currentText === "Lensdump" || 
                                        hostCombo.currentText === "Gofile"
                                
                                Label {
                                    text: {
                                        if (hostCombo.currentText === "Lensdump") 
                                            return "✓ Lensdump está pronto para uso\nPreserva qualidade máxima de imagem"
                                        else if (hostCombo.currentText === "Gofile") 
                                            return "✓ Gofile está pronto para uso\nÓtimo para múltiplos arquivos\n✅ Links diretos otimizados!"
                                        else 
                                            return ""
                                    }
                                    font.pixelSize: 12
                                    color: colorTertiary
                                    opacity: 0.8
                                    wrapMode: Text.WordWrap
                                    Layout.fillWidth: true
                                }
                            }
                            
                            // Performance Settings
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 16
                                
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 8
                                    
                                    Label {
                                        text: "Workers simultâneos"
                                        font.pixelSize: 12
                                        color: colorTertiary
                                        opacity: 0.8
                                    }
                                    
                                    Rectangle {
                                        Layout.fillWidth: true
                                        height: 32
                                        color: colorPrimary
                                        border.color: colorTertiary
                                        border.width: 1
                                        radius: 8
                                        
                                        SpinBox {
                                            id: maxWorkersSpinBox
                                            anchors.fill: parent
                                            from: 1
                                            to: 20
                                            value: backend.maxWorkers
                                            
                                            background: Rectangle {
                                                color: "transparent"
                                            }
                                            
                                            contentItem: TextInput {
                                                text: maxWorkersSpinBox.textFromValue(maxWorkersSpinBox.value, maxWorkersSpinBox.locale)
                                                font.pixelSize: 11
                                                color: colorTertiary
                                                horizontalAlignment: Qt.AlignHCenter
                                                verticalAlignment: Qt.AlignVCenter
                                                readOnly: !maxWorkersSpinBox.editable
                                                validator: maxWorkersSpinBox.validator
                                                inputMethodHints: Qt.ImhFormattedNumbersOnly
                                            }
                                        }
                                    }
                                }
                                
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 8
                                    
                                    Label {
                                        text: "Rate limit (segundos)"
                                        font.pixelSize: 12
                                        color: colorTertiary
                                        opacity: 0.8
                                    }
                                    
                                    Rectangle {
                                        Layout.fillWidth: true
                                        height: 32
                                        color: colorPrimary
                                        border.color: colorTertiary
                                        border.width: 1
                                        radius: 8
                                        
                                        SpinBox {
                                            id: rateLimitSpinBox
                                            anchors.fill: parent
                                            from: 0
                                            to: 10
                                            value: backend.rateLimit
                                            
                                            background: Rectangle {
                                                color: "transparent"
                                            }
                                            
                                            contentItem: TextInput {
                                                text: rateLimitSpinBox.textFromValue(rateLimitSpinBox.value, rateLimitSpinBox.locale)
                                                font.pixelSize: 11
                                                color: colorTertiary
                                                horizontalAlignment: Qt.AlignHCenter
                                                verticalAlignment: Qt.AlignVCenter
                                                readOnly: !rateLimitSpinBox.editable
                                                validator: rateLimitSpinBox.validator
                                                inputMethodHints: Qt.ImhFormattedNumbersOnly
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                    
                    // GitHub Configuration
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 12
                        
                        Label {
                            text: "GITHUB (OPCIONAL)"
                            font.pixelSize: 11
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
                        
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 16
                            
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                
                                Label {
                                    text: "Token de acesso"
                                    font.pixelSize: 12
                                    color: colorTertiary
                                    opacity: 0.8
                                }
                                
                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 32
                                    color: colorPrimary
                                    border.color: colorTertiary
                                    border.width: 1
                                    radius: 8
                                    
                                    TextField {
                                        id: githubTokenField
                                        anchors.fill: parent
                                        anchors.margins: 1
                                        text: backend.githubToken
                                        echoMode: TextInput.Password
                                        color: colorTertiary
                                        font.pixelSize: 11
                                        background: Rectangle { color: "transparent" }
                                        leftPadding: 8
                                        rightPadding: 8
                                    }
                                }
                            }
                            
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                
                                Label {
                                    text: "Repositório (usuário/repo)"
                                    font.pixelSize: 12
                                    color: colorTertiary
                                    opacity: 0.8
                                }
                                
                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 32
                                    color: colorPrimary
                                    border.color: colorTertiary
                                    border.width: 1
                                    radius: 8
                                    
                                    TextField {
                                        id: githubRepoField
                                        anchors.fill: parent
                                        anchors.margins: 1
                                        text: backend.githubRepo
                                        placeholderText: "usuario/repositorio"
                                        color: colorTertiary
                                        font.pixelSize: 11
                                        background: Rectangle { color: "transparent" }
                                        leftPadding: 8
                                        rightPadding: 8
                                    }
                                }
                            }
                            
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                
                                Label {
                                    text: "Branch"
                                    font.pixelSize: 12
                                    color: colorTertiary
                                    opacity: 0.8
                                }
                                
                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 32
                                    color: colorPrimary
                                    border.color: colorTertiary
                                    border.width: 1
                                    radius: 8
                                    
                                    TextField {
                                        id: githubBranchField
                                        anchors.fill: parent
                                        anchors.margins: 1
                                        text: backend.githubBranch
                                        placeholderText: "main"
                                        color: colorTertiary
                                        font.pixelSize: 11
                                        background: Rectangle { color: "transparent" }
                                        leftPadding: 8
                                        rightPadding: 8
                                    }
                                }
                            }
                            
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                
                                Label {
                                    text: "Pasta no repositório"
                                    font.pixelSize: 12
                                    color: colorTertiary
                                    opacity: 0.8
                                }
                                
                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 8
                                    
                                    ComboBox {
                                        id: githubFolderCombo
                                        Layout.fillWidth: true
                                        Layout.preferredHeight: 32
                                        
                                        property string currentFolder: backend.githubFolder
                                        
                                        model: backend.githubFolders
                                        editable: true
                                        editText: backend.githubFolder
                                        
                                        Component.onCompleted: {
                                            backend.refreshGitHubFolders()
                                            var index = model.indexOf(backend.githubFolder)
                                            if (index >= 0) {
                                                currentIndex = index
                                            }
                                        }
                                        
                                        Connections {
                                            target: backend
                                            function onGithubFoldersChanged() {
                                                var currentFolder = backend.githubFolder
                                                var index = githubFolderCombo.model.indexOf(currentFolder)
                                                if (index >= 0) {
                                                    githubFolderCombo.currentIndex = index
                                                } else {
                                                    githubFolderCombo.editText = currentFolder
                                                }
                                            }
                                        }
                                        
                                        onAccepted: {
                                            currentFolder = editText
                                        }
                                        
                                        onCurrentTextChanged: {
                                            if (currentIndex >= 0 && currentText !== currentFolder) {
                                                currentFolder = currentText
                                            }
                                        }
                                        
                                        delegate: ItemDelegate {
                                            width: githubFolderCombo.width
                                            height: 32
                                            
                                            Rectangle {
                                                anchors.fill: parent
                                                color: parent.hovered ? colorHover : "transparent"
                                                radius: 4
                                                
                                                RowLayout {
                                                    anchors.fill: parent
                                                    anchors.leftMargin: 8
                                                    anchors.rightMargin: 8
                                                    spacing: 6
                                                    
                                                    Label {
                                                        text: modelData === "" ? "🏠" : "📁"
                                                        font.pixelSize: 12
                                                    }
                                                    
                                                    Label {
                                                        text: modelData === "" ? "(raiz)" : modelData
                                                        font.pixelSize: 11
                                                        color: colorTertiary
                                                        Layout.fillWidth: true
                                                    }
                                                }
                                            }
                                        }
                                        
                                        background: Rectangle {
                                            radius: 8
                                            color: colorSurface
                                            border.color: parent.activeFocus ? colorSecondary : colorTertiary
                                            border.width: 1
                                        }
                                        
                                        contentItem: RowLayout {
                                            spacing: 6
                                            
                                            Label {
                                                text: githubFolderCombo.editText === "" ? "🏠" : "📁"
                                                font.pixelSize: 12
                                                Layout.leftMargin: 8
                                            }
                                            
                                            Label {
                                                text: githubFolderCombo.editText === "" ? "(raiz)" : githubFolderCombo.editText
                                                font.pixelSize: 11
                                                color: colorTertiary
                                                Layout.fillWidth: true
                                            }
                                        }
                                    }
                                    
                                    Rectangle {
                                        width: 80
                                        height: 32
                                        radius: 8
                                        color: refreshBtnHovered ? colorSecondary : colorSurface
                                        border.color: refreshBtnHovered ? colorSecondary : colorTertiary
                                        border.width: 1
                                        
                                        property bool refreshBtnHovered: false
                                        
                                        RowLayout {
                                            anchors.centerIn: parent
                                            spacing: 4
                                            
                                            Label {
                                                text: "🔄"
                                                font.pixelSize: 10
                                            }
                                            
                                            Label {
                                                text: "REFRESH"
                                                font.pixelSize: 8
                                                font.weight: Font.Medium
                                                color: parent.parent.refreshBtnHovered ? "white" : colorTertiary
                                            }
                                        }
                                        
                                        MouseArea {
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            onEntered: parent.refreshBtnHovered = true
                                            onExited: parent.refreshBtnHovered = false
                                            onClicked: backend.refreshGitHubFolders()
                                        }
                                    }
                                }
                            }
                        }
                    }
                    
                    // JSON Update Mode
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 12
                        
                        Label {
                            text: "MODO DE ATUALIZAÇÃO JSON"
                            font.pixelSize: 11
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
                        
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 16
                            
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                
                                Label {
                                    text: "Modo de atualização"
                                    font.pixelSize: 12
                                    color: colorTertiary
                                    opacity: 0.8
                                }
                                
                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 32
                                    color: colorPrimary
                                    border.color: colorTertiary
                                    border.width: 1
                                    radius: 8
                                    
                                    ComboBox {
                                        id: jsonUpdateModeCombo
                                        anchors.fill: parent
                                        model: backend.availableUpdateModes
                                        textRole: "text"
                                        valueRole: "value"
                                        
                                        Component.onCompleted: {
                                            for (var i = 0; i < count; i++) {
                                                if (backend.availableUpdateModes[i].value === backend.jsonUpdateMode) {
                                                    currentIndex = i
                                                    break
                                                }
                                            }
                                        }
                                        
                                        background: Rectangle {
                                            color: "transparent"
                                        }
                                        
                                        contentItem: Text {
                                            text: jsonUpdateModeCombo.currentText
                                            font.pixelSize: 12
                                            color: colorTertiary
                                            verticalAlignment: Text.AlignVCenter
                                            leftPadding: 8
                                        }
                                    }
                                }
                                
                                Label {
                                    Layout.fillWidth: true
                                    text: {
                                        switch(jsonUpdateModeCombo.currentValue) {
                                        case "add": return "Mantém capítulos existentes • Adiciona novos • Atualiza duplicados"
                                        case "replace": return "Remove todos existentes • Substitui por novos • Use com cuidado!"
                                        case "smart": return "Analisa títulos • Adiciona apenas novos • Preserva ordem"
                                        default: return ""
                                        }
                                    }
                                    wrapMode: Text.WordWrap
                                    font.pixelSize: 10
                                    color: colorTertiary
                                    opacity: 0.7
                                }
                            }
                        }
                    }
                    
                    // Save Button
                    Rectangle {
                        Layout.fillWidth: true
                        height: 40
                        radius: 8
                        color: saveBtnHovered ? colorSecondary : "transparent"
                        border.color: colorSecondary
                        border.width: 1
                        
                        property bool saveBtnHovered: false
                        
                        Label {
                            anchors.centerIn: parent
                            text: "SALVAR CONFIGURAÇÕES"
                            font.pixelSize: 11
                            font.weight: Font.Medium
                            font.letterSpacing: 1
                            color: parent.saveBtnHovered ? "white" : colorSecondary
                        }
                        
                        MouseArea {
                            id: saveBtn
                            anchors.fill: parent
                            hoverEnabled: true
                            onEntered: parent.saveBtnHovered = true
                            onExited: parent.saveBtnHovered = false
                            onClicked: {
                                var config = {
                                    rootFolder: rootFolderField.text,
                                    outputFolder: outputFolderField.text,
                                    catboxUserhash: catboxUserhashField.text,
                                    imgurClientId: imgurClientIdField.text,
                                    imgurAccessToken: imgurAccessTokenField.text,
                                    imgbbApiKey: imgbbApiKeyField.text,
                                    imageChestApiKey: imageChestApiKeyField.text,
                                    pixeldrainApiKey: pixeldrainApiKeyField.text,
                                    imgboxSessionCookie: imgboxSessionCookieField.text,
                                    maxWorkers: maxWorkersSpinBox.value,
                                    rateLimit: rateLimitSpinBox.value,
                                    githubToken: githubTokenField.text,
                                    githubRepo: githubRepoField.text,
                                    githubBranch: githubBranchField.text,
                                    githubFolder: githubFolderCombo.currentFolder,
                                    jsonUpdateMode: jsonUpdateModeCombo.currentValue
                                }
                                backend.updateConfig(config)
                                settingsDrawer.close()
                            }
                        }
                    }
                    
                    Item { Layout.fillHeight: true }
                }
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
        height: 560
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
}