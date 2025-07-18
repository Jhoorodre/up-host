import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Shapes 1.15

/**
 * Analytics Dashboard - Item 11 do FRONTEND_MAP_MODERN.md
 * Dashboard completo com gráficos, métricas e relatórios
 */
Rectangle {
    id: root
    
    // ===== DESIGN SYSTEM =====
    DesignSystem { id: ds }
    
    // ===== PUBLIC PROPERTIES =====
    property var uploadData: []
    property int totalUploads: 0
    property string totalStorage: "0 MB"
    property string avgTime: "0h"
    property string successRate: "0%"
    property int activeManga: 0
    property int completedJobs: 0
    property int failedJobs: 0
    
    // ===== LAYOUT =====
    color: ds.bgPrimary
    
    ScrollView {
        anchors.fill: parent
        anchors.margins: ds.space8
        
        ColumnLayout {
            width: parent.width
            spacing: ds.space8
            
            // ===== HEADER =====
            RowLayout {
                Layout.fillWidth: true
                spacing: ds.space4
                
                Text {
                    text: "📊 Analytics & Relatórios"
                    font.pixelSize: ds.text_3xl
                    font.weight: ds.fontBold
                    color: ds.textPrimary
                }
                
                Item { Layout.fillWidth: true }
                
                ModernDropdown {
                    model: ["Últimos 7 dias", "Últimos 30 dias", "Últimos 90 dias", "Este ano"]
                    currentIndex: 1
                    size: "md"
                }
            }
            
            // ===== METRICS CARDS =====
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
                
                // Upload Count Card
                MetricCard {
                    title: "UPLOADS"
                    value: totalUploads.toLocaleString()
                    change: "+12%"
                    changePositive: true
                    icon: "📤"
                    subtitle: "esta semana"
                }
                
                // Storage Card
                MetricCard {
                    title: "STORAGE"
                    value: totalStorage
                    change: "+2.1 GB"
                    changePositive: true
                    icon: "📁"
                    subtitle: "total usado"
                }
                
                // Time Card
                MetricCard {
                    title: "TEMPO"
                    value: avgTime
                    change: "-15 min"
                    changePositive: true
                    icon: "⏱️"
                    subtitle: "tempo médio"
                }
                
                // Success Rate Card
                MetricCard {
                    title: "SUCESSO"
                    value: successRate
                    change: "+0.8%"
                    changePositive: true
                    icon: "✅"
                    subtitle: "taxa de sucesso"
                }
            }
            
            // ===== UPLOAD CHART =====
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 320
                radius: ds.radius_lg
                color: ds.bgCard
                border.color: ds.border
                border.width: 1
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: ds.space6
                    spacing: ds.space4
                    
                    Text {
                        text: "📈 Uploads por Dia (Últimos 30 dias)"
                        font.pixelSize: ds.text_xl
                        font.weight: ds.fontMedium
                        color: ds.textPrimary
                    }
                    
                    // Chart Area
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        color: "transparent"
                        
                        Canvas {
                            id: chartCanvas
                            anchors.fill: parent
                            anchors.margins: ds.space4
                            
                            onPaint: {
                                var ctx = getContext("2d")
                                ctx.clearRect(0, 0, width, height)
                                
                                if (uploadData.length === 0) return
                                
                                // Chart styling
                                ctx.strokeStyle = ds.accent
                                ctx.fillStyle = ds.accent + "40"
                                ctx.lineWidth = 3
                                ctx.lineCap = "round"
                                ctx.lineJoin = "round"
                                
                                // Calculate dimensions
                                var maxValue = Math.max(...uploadData)
                                var stepX = width / (uploadData.length - 1)
                                var stepY = height / maxValue
                                
                                // Draw area under curve
                                ctx.beginPath()
                                ctx.moveTo(0, height)
                                
                                for (var i = 0; i < uploadData.length; i++) {
                                    var x = i * stepX
                                    var y = height - (uploadData[i] * stepY)
                                    
                                    if (i === 0) {
                                        ctx.lineTo(x, y)
                                    } else {
                                        // Smooth curve
                                        var prevX = (i - 1) * stepX
                                        var prevY = height - (uploadData[i - 1] * stepY)
                                        var cpX = prevX + stepX / 2
                                        ctx.quadraticCurveTo(cpX, prevY, x, y)
                                    }
                                }
                                
                                ctx.lineTo(width, height)
                                ctx.closePath()
                                ctx.fill()
                                
                                // Draw line
                                ctx.beginPath()
                                ctx.moveTo(0, height - (uploadData[0] * stepY))
                                
                                for (var j = 1; j < uploadData.length; j++) {
                                    var x2 = j * stepX
                                    var y2 = height - (uploadData[j] * stepY)
                                    var prevX2 = (j - 1) * stepX
                                    var prevY2 = height - (uploadData[j - 1] * stepY)
                                    var cpX2 = prevX2 + stepX / 2
                                    ctx.quadraticCurveTo(cpX2, prevY2, x2, y2)
                                }
                                
                                ctx.stroke()
                                
                                // Draw data points
                                ctx.fillStyle = ds.accent
                                for (var k = 0; k < uploadData.length; k++) {
                                    var x3 = k * stepX
                                    var y3 = height - (uploadData[k] * stepY)
                                    ctx.beginPath()
                                    ctx.arc(x3, y3, 4, 0, 2 * Math.PI)
                                    ctx.fill()
                                }
                            }
                            
                            Component.onCompleted: requestPaint()
                        }
                        
                        // X-axis labels
                        Row {
                            anchors.bottom: parent.bottom
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.margins: ds.space4
                            
                            Repeater {
                                model: 6
                                
                                Text {
                                    width: (parent.width - ds.space8) / 5
                                    text: (index * 6 + 1).toString()
                                    font.pixelSize: ds.text_xs
                                    color: ds.textSecondary
                                    horizontalAlignment: Text.AlignHCenter
                                }
                            }
                        }
                    }
                }
            }
            
            // ===== BOTTOM SECTION =====
            GridLayout {
                Layout.fillWidth: true
                columns: parent.width <= ds.tablet ? 1 : 2
                columnSpacing: ds.space6
                rowSpacing: ds.space6
                
                // ===== TOP HOSTS =====
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 280
                    radius: ds.radius_lg
                    color: ds.bgCard
                    border.color: ds.border
                    border.width: 1
                    
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: ds.space6
                        spacing: ds.space4
                        
                        Text {
                            text: "🏆 Top Hosts"
                            font.pixelSize: ds.text_xl
                            font.weight: ds.fontMedium
                            color: ds.textPrimary
                        }
                        
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: ds.space3
                            
                            TopHostItem {
                                position: 1
                                hostName: "Catbox"
                                uploadCount: 342
                                hostColor: "#ff6b35"
                            }
                            
                            TopHostItem {
                                position: 2
                                hostName: "Imgur"
                                uploadCount: 289
                                hostColor: "#1bb76e"
                            }
                            
                            TopHostItem {
                                position: 3
                                hostName: "ImgBox"
                                uploadCount: 234
                                hostColor: "#06b6d4"
                            }
                            
                            TopHostItem {
                                position: 4
                                hostName: "Pixeldrain"
                                uploadCount: 189
                                hostColor: "#8b5cf6"
                            }
                        }
                        
                        Item { Layout.fillHeight: true }
                    }
                }
                
                // ===== TOP MANGÁS =====
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 280
                    radius: ds.radius_lg
                    color: ds.bgCard
                    border.color: ds.border
                    border.width: 1
                    
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: ds.space6
                        spacing: ds.space4
                        
                        Text {
                            text: "🔥 Mangás Mais Ativos"
                            font.pixelSize: ds.text_xl
                            font.weight: ds.fontMedium
                            color: ds.textPrimary
                        }
                        
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: ds.space3
                            
                            TopMangaItem {
                                position: 1
                                mangaName: "Tower of God"
                                chapterCount: 23
                            }
                            
                            TopMangaItem {
                                position: 2
                                mangaName: "One Piece"
                                chapterCount: 18
                            }
                            
                            TopMangaItem {
                                position: 3
                                mangaName: "Naruto"
                                chapterCount: 15
                            }
                            
                            TopMangaItem {
                                position: 4
                                mangaName: "Solo Leveling"
                                chapterCount: 12
                            }
                        }
                        
                        Item { Layout.fillHeight: true }
                    }
                }
            }
            
            // ===== ACTION BUTTONS =====
            RowLayout {
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignHCenter
                spacing: ds.space4
                
                ModernButton {
                    text: "Exportar CSV"
                    icon: "📥"
                    variant: "secondary"
                    size: "lg"
                    
                    onClicked: {
                        // TODO: Implement CSV export
                        console.log("Export CSV clicked")
                    }
                }
                
                ModernButton {
                    text: "Relatório Detalhado"
                    icon: "📊"
                    variant: "primary"
                    size: "lg"
                    
                    onClicked: {
                        // TODO: Open detailed report
                        console.log("Detailed report clicked")
                    }
                }
                
                ModernButton {
                    text: "Atualizar"
                    icon: "🔄"
                    variant: "ghost"
                    size: "lg"
                    
                    onClicked: {
                        chartCanvas.requestPaint()
                        console.log("Refresh clicked")
                    }
                }
            }
        }
    }
    
    // ===== METRIC CARD COMPONENT =====
    component MetricCard: Rectangle {
        property string title: ""
        property string value: ""
        property string change: ""
        property bool changePositive: true
        property string icon: ""
        property string subtitle: ""
        
        Layout.fillWidth: true
        Layout.preferredHeight: 120
        radius: ds.radius_md
        color: ds.bgCard
        border.color: ds.border
        border.width: 1
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: ds.space4
            spacing: ds.space2
            
            RowLayout {
                Layout.fillWidth: true
                spacing: ds.space2
                
                Text {
                    text: icon
                    font.pixelSize: ds.text_lg
                }
                
                Text {
                    text: title
                    font.pixelSize: ds.text_sm
                    font.weight: ds.fontMedium
                    color: ds.textSecondary
                }
                
                Item { Layout.fillWidth: true }
                
                Text {
                    text: (changePositive ? "↗️" : "↘️") + " " + change
                    font.pixelSize: ds.text_xs
                    color: changePositive ? ds.success : ds.danger
                }
            }
            
            Text {
                text: value
                font.pixelSize: ds.text_2xl
                font.weight: ds.fontBold
                color: ds.textPrimary
            }
            
            Text {
                text: subtitle
                font.pixelSize: ds.text_xs
                color: ds.textSecondary
            }
            
            Item { Layout.fillHeight: true }
        }
    }
    
    // ===== TOP HOST ITEM COMPONENT =====
    component TopHostItem: Rectangle {
        property int position: 1
        property string hostName: ""
        property int uploadCount: 0
        property string hostColor: ""
        
        Layout.fillWidth: true
        height: ds.space10
        radius: ds.radius_sm
        color: mouseArea.containsMouse ? ds.hover : "transparent"
        
        RowLayout {
            anchors.fill: parent
            anchors.margins: ds.space3
            spacing: ds.space3
            
            Text {
                text: position + "."
                font.pixelSize: ds.text_base
                font.weight: ds.fontBold
                color: ds.textPrimary
                Layout.preferredWidth: ds.space5
            }
            
            Rectangle {
                width: ds.space4
                height: ds.space4
                radius: ds.space4 / 2
                color: hostColor
            }
            
            Text {
                text: hostName
                font.pixelSize: ds.text_base
                color: ds.textPrimary
                Layout.fillWidth: true
            }
            
            Text {
                text: uploadCount + " uploads"
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
    }
    
    // ===== TOP MANGA ITEM COMPONENT =====
    component TopMangaItem: Rectangle {
        property int position: 1
        property string mangaName: ""
        property int chapterCount: 0
        
        Layout.fillWidth: true
        height: ds.space10
        radius: ds.radius_sm
        color: mouseArea.containsMouse ? ds.hover : "transparent"
        
        RowLayout {
            anchors.fill: parent
            anchors.margins: ds.space3
            spacing: ds.space3
            
            Text {
                text: position + "."
                font.pixelSize: ds.text_base
                font.weight: ds.fontBold
                color: ds.textPrimary
                Layout.preferredWidth: ds.space5
            }
            
            Text {
                text: "📚"
                font.pixelSize: ds.text_base
            }
            
            Text {
                text: mangaName
                font.pixelSize: ds.text_base
                color: ds.textPrimary
                Layout.fillWidth: true
                elide: Text.ElideRight
            }
            
            Text {
                text: chapterCount + " caps"
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
    }
    
    // ===== FUNCTIONS =====
    function updateAnalytics() {
        console.log("Updating analytics data...")
        
        if (backend.getAnalyticsData) {
            var data = backend.getAnalyticsData()
            totalUploads = data.totalUploads || 0
            totalStorage = data.totalStorage || "0 MB"
            avgTime = data.avgTime || "0h"
            successRate = data.successRate || "0%"
            activeManga = data.activeManga || 0
            completedJobs = data.completedJobs || 0
            failedJobs = data.failedJobs || 0
            uploadData = data.uploadData || []
        } else {
            // Generate demo data if backend not available
            generateDemoData()
        }
    }
    
    function generateDemoData() {
        console.log("Generating demo analytics data...")
        
        // Generate realistic upload data for last 30 days
        uploadData = []
        for (var i = 0; i < 30; i++) {
            var baseValue = 50 + (Math.sin(i * 0.2) * 20)
            var randomVariation = (Math.random() - 0.5) * 40
            uploadData.push(Math.max(0, Math.floor(baseValue + randomVariation)))
        }
        
        // Calculate totals from generated data
        totalUploads = uploadData.reduce(function(sum, val) { return sum + val }, 0)
        totalStorage = (totalUploads * 0.012).toFixed(1) + " GB" // ~12MB per upload
        avgTime = (Math.random() * 3 + 1).toFixed(1) + "h"
        
        var success = Math.floor(85 + Math.random() * 12) // 85-97%
        successRate = success.toFixed(1) + "%"
        
        activeManga = Math.floor(Math.random() * 20) + 5
        completedJobs = Math.floor(totalUploads * 0.8)
        failedJobs = totalUploads - completedJobs
        
        console.log("Demo data generated:", {
            totalUploads: totalUploads,
            totalStorage: totalStorage,
            successRate: successRate
        })
    }
    
    // ===== INITIALIZATION =====
    Component.onCompleted: {
        updateAnalytics()
    }
}