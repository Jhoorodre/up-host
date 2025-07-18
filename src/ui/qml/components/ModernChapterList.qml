import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

/**
 * ModernChapterList - Lista moderna de capítulos com seleção múltipla
 * Baseado no FRONTEND_MAP_MODERN.md
 */
Rectangle {
    id: root
    
    // ===== PUBLIC PROPERTIES =====
    property alias model: chapterListView.model
    property int selectedCount: 0
    property bool showControls: true
    property bool invertedOrder: false
    
    // ===== DESIGN SYSTEM =====
    DesignSystem { id: ds }
    
    // ===== LAYOUT =====
    color: "transparent"
    
    ColumnLayout {
        anchors.fill: parent
        spacing: ds.space4
        
        // ===== HEADER =====
        RowLayout {
            Layout.fillWidth: true
            spacing: ds.space4
            
            // Title with count
            Text {
                text: "📑 CAPÍTULOS (" + (chapterListView.count || 0) + ")"
                font.pixelSize: ds.text_base
                font.weight: ds.fontMedium
                font.letterSpacing: 0.5
                color: ds.textPrimary
            }
            
            Item { Layout.fillWidth: true }
            
            // Selection counter
            Rectangle {
                visible: selectedCount > 0
                Layout.preferredHeight: ds.space6
                radius: ds.radius_full
                color: ds.accent
                width: counterText.implicitWidth + ds.space4
                
                Text {
                    id: counterText
                    anchors.centerIn: parent
                    text: selectedCount + " selecionados"
                    font.pixelSize: ds.text_xs
                    font.weight: ds.fontMedium
                    color: ds.textPrimary
                }
            }
        }
        
        // ===== CONTROL BUTTONS =====
        RowLayout {
            Layout.fillWidth: true
            spacing: ds.space3
            visible: showControls
            
            // Select All
            ModernButton {
                text: "Selecionar Todos"
                icon: "✓"
                variant: "ghost"
                size: "sm"
                
                onClicked: {
                    selectAllChapters()
                }
            }
            
            // Unselect All
            ModernButton {
                text: "Desmarcar Todos"
                icon: "✕"
                variant: "ghost"
                size: "sm"
                
                onClicked: {
                    unselectAllChapters()
                }
            }
            
            // Invert Order
            ModernButton {
                text: "Inverter Ordem"
                icon: "⇅"
                variant: "ghost"
                size: "sm"
                
                onClicked: {
                    invertedOrder = !invertedOrder
                    orderInverted(invertedOrder)
                }
            }
            
            Item { Layout.fillWidth: true }
            
            // Batch actions (visible when items selected)
            RowLayout {
                spacing: ds.space2
                visible: selectedCount > 0
                
                ModernButton {
                    text: "Upload Selecionados"
                    icon: "📤"
                    variant: "primary"
                    size: "sm"
                    
                    onClicked: {
                        uploadSelected()
                    }
                }
                
                ModernButton {
                    text: "Remover Selecionados"
                    icon: "🗑️"
                    variant: "danger"
                    size: "sm"
                    
                    onClicked: {
                        removeSelected()
                    }
                }
            }
        }
        
        // ===== CHAPTER LIST =====
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            
            ListView {
                id: chapterListView
                spacing: ds.space1
                
                delegate: ChapterItem {
                    width: chapterListView.width
                    chapterName: model.name || ""
                    imageCount: model.imageCount || 0
                    isSelected: model.selected || false
                    chapterStatus: model.status || ""
                    lastModified: model.lastModified || ""
                    
                    onSelectionChanged: {
                        model.selected = selected
                        updateSelectedCount()
                    }
                    
                    onChapterClicked: {
                        root.chapterClicked(model.name)
                    }
                    
                    onUploadClicked: {
                        root.chapterUploadClicked(model.name)
                    }
                    
                    onEditClicked: {
                        root.chapterEditClicked(model.name)
                    }
                }
            }
        }
        
        // ===== FOOTER INFO =====
        Rectangle {
            Layout.fillWidth: true
            height: ds.space8
            radius: ds.radius_md
            color: ds.bgCard
            border.color: ds.border
            border.width: 1
            visible: selectedCount > 0
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: ds.space3
                spacing: ds.space4
                
                Text {
                    text: "📊"
                    font.pixelSize: ds.iconMd
                }
                
                Text {
                    text: "Selecionados: " + selectedCount + " capítulos"
                    font.pixelSize: ds.text_sm
                    color: ds.textPrimary
                }
                
                Text {
                    text: "•"
                    font.pixelSize: ds.text_sm
                    color: ds.textSecondary
                }
                
                Text {
                    text: getTotalImages() + " imagens"
                    font.pixelSize: ds.text_sm
                    color: ds.textSecondary
                }
                
                Text {
                    text: "•"
                    font.pixelSize: ds.text_sm
                    color: ds.textSecondary
                }
                
                Text {
                    text: "~" + getEstimatedSize()
                    font.pixelSize: ds.text_sm
                    color: ds.textSecondary
                }
                
                Item { Layout.fillWidth: true }
                
                ModernButton {
                    text: "Processar"
                    icon: "⚡"
                    variant: "primary"
                    size: "sm"
                    
                    onClicked: {
                        processSelected()
                    }
                }
            }
        }
    }
    
    // ===== CHAPTER ITEM COMPONENT =====
    component ChapterItem: Rectangle {
        id: chapterItem
        
        property string chapterName: ""
        property int imageCount: 0
        property bool isSelected: false
        property string chapterStatus: ""
        property string lastModified: ""
        
        signal selectionChanged(bool selected)
        signal chapterClicked(string name)
        signal uploadClicked(string name)
        signal editClicked(string name)
        
        height: ds.space12
        radius: ds.radius_sm
        color: mouseArea.containsMouse ? ds.hover : (isSelected ? ds.bgCard : "transparent")
        border.color: isSelected ? ds.accent : "transparent"
        border.width: isSelected ? 1 : 0
        
        Behavior on color {
            ColorAnimation {
                duration: ds.animationFast
                easing.type: ds.easingOut
            }
        }
        
        Behavior on border.color {
            ColorAnimation {
                duration: ds.animationFast
                easing.type: ds.easingOut
            }
        }
        
        RowLayout {
            anchors.fill: parent
            anchors.margins: ds.space3
            spacing: ds.space3
            
            // Selection checkbox
            Rectangle {
                width: ds.iconMd
                height: ds.iconMd
                radius: ds.radius_sm
                color: isSelected ? ds.accent : "transparent"
                border.color: isSelected ? ds.accent : ds.border
                border.width: 1
                
                Text {
                    anchors.centerIn: parent
                    text: "✓"
                    font.pixelSize: ds.text_xs
                    color: ds.textPrimary
                    visible: isSelected
                }
                
                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        isSelected = !isSelected
                        selectionChanged(isSelected)
                    }
                }
            }
            
            // Chapter info
            ColumnLayout {
                Layout.fillWidth: true
                spacing: ds.space1
                
                Text {
                    text: chapterName
                    font.pixelSize: ds.text_sm
                    font.weight: ds.fontMedium
                    color: ds.textPrimary
                    elide: Text.ElideRight
                    Layout.fillWidth: true
                }
                
                RowLayout {
                    spacing: ds.space3
                    
                    Text {
                        text: "🖼️ " + imageCount + " imgs"
                        font.pixelSize: ds.text_xs
                        color: ds.textSecondary
                    }
                    
                    Text {
                        text: "📅 " + (lastModified || "Hoje")
                        font.pixelSize: ds.text_xs
                        color: ds.textSecondary
                    }
                    
                    // Status badge
                    Rectangle {
                        visible: chapterStatus !== ""
                        width: statusText.implicitWidth + ds.space2
                        height: ds.space4
                        radius: ds.radius_sm
                        color: getStatusColor(chapterStatus)
                        
                        Text {
                            id: statusText
                            anchors.centerIn: parent
                            text: getStatusText(chapterStatus)
                            font.pixelSize: ds.text_xs
                            color: ds.textPrimary
                        }
                    }
                }
            }
            
            // Quick actions
            RowLayout {
                spacing: ds.space2
                opacity: mouseArea.containsMouse ? 1.0 : 0.5
                
                Behavior on opacity {
                    NumberAnimation {
                        duration: ds.animationFast
                        easing.type: ds.easingOut
                    }
                }
                
                ModernButton {
                    text: "Upload"
                    icon: "📤"
                    variant: "ghost"
                    size: "sm"
                    iconOnly: true
                    
                    onClicked: {
                        chapterItem.uploadClicked(chapterName)
                    }
                }
                
                ModernButton {
                    text: "Editar"
                    icon: "✏️"
                    variant: "ghost"
                    size: "sm"
                    iconOnly: true
                    
                    onClicked: {
                        chapterItem.editClicked(chapterName)
                    }
                }
            }
        }
        
        MouseArea {
            id: mouseArea
            anchors.fill: parent
            hoverEnabled: true
            acceptedButtons: Qt.LeftButton | Qt.RightButton
            
            onClicked: function(mouse) {
                if (mouse.button === Qt.LeftButton) {
                    chapterItem.chapterClicked(chapterName)
                }
            }
            
            onDoubleClicked: {
                isSelected = !isSelected
                selectionChanged(isSelected)
            }
        }
        
        function getStatusColor(status) {
            switch(status.toLowerCase()) {
                case "uploaded": return ds.success
                case "processing": return ds.warning
                case "error": return ds.danger
                default: return ds.textSecondary
            }
        }
        
        function getStatusText(status) {
            switch(status.toLowerCase()) {
                case "uploaded": return "✅"
                case "processing": return "⏳"
                case "error": return "❌"
                default: return "📄"
            }
        }
    }
    
    // ===== METHODS =====
    function selectAllChapters() {
        for (var i = 0; i < chapterListView.count; i++) {
            var item = chapterListView.model.get ? chapterListView.model.get(i) : chapterListView.model[i]
            if (item) {
                item.selected = true
            }
        }
        updateSelectedCount()
        allSelected()
    }
    
    function unselectAllChapters() {
        for (var i = 0; i < chapterListView.count; i++) {
            var item = chapterListView.model.get ? chapterListView.model.get(i) : chapterListView.model[i]
            if (item) {
                item.selected = false
            }
        }
        updateSelectedCount()
        allUnselected()
    }
    
    function updateSelectedCount() {
        var count = 0
        for (var i = 0; i < chapterListView.count; i++) {
            var item = chapterListView.model.get ? chapterListView.model.get(i) : chapterListView.model[i]
            if (item && item.selected) {
                count++
            }
        }
        selectedCount = count
    }
    
    function getTotalImages() {
        var total = 0
        for (var i = 0; i < chapterListView.count; i++) {
            var item = chapterListView.model.get ? chapterListView.model.get(i) : chapterListView.model[i]
            if (item && item.selected) {
                total += item.imageCount || 0
            }
        }
        return total
    }
    
    function getEstimatedSize() {
        var totalImages = getTotalImages()
        var estimatedMB = Math.round(totalImages * 1.5) // ~1.5MB per image
        return estimatedMB > 1000 ? (estimatedMB / 1000).toFixed(1) + "GB" : estimatedMB + "MB"
    }
    
    // ===== SIGNALS =====
    signal chapterClicked(string name)
    signal chapterUploadClicked(string name)
    signal chapterEditClicked(string name)
    signal allSelected()
    signal allUnselected()
    signal orderInverted(bool inverted)
    signal uploadSelected()
    signal removeSelected()
    signal processSelected()
}