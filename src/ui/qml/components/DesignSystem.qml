import QtQuick 2.15

/**
 * Design System - Tokens para o novo design minimalista moderno
 * Baseado no FRONTEND_MAP_MODERN.md
 */
QtObject {
    id: designSystem

    // ===== COLOR PALETTE - MINIMALISTA MODERNO =====
    readonly property color bgPrimary: "#0a0a0a"      // Preto profundo
    readonly property color bgSurface: "#161616"      // Cinza escuro suave  
    readonly property color bgCard: "#1e1e1e"         // Cards
    readonly property color accent: "#0ea5e9"         // Azul vibrante (Sky-500)
    readonly property color accentHover: "#0284c7"    // Azul hover (Sky-600)
    readonly property color textPrimary: "#fafafa"    // Branco quase puro
    readonly property color textSecondary: "#a1a1aa"  // Cinza claro
    readonly property color success: "#22c55e"        // Verde moderno
    readonly property color warning: "#f59e0b"        // Laranja
    readonly property color danger: "#ef4444"         // Vermelho
    
    // Estados e interações
    readonly property color hover: "#404040"          // Estados hover
    readonly property color pressed: "#2a2a2a"        // Estados pressed
    readonly property color disabled: "#525252"       // Elementos desabilitados
    readonly property color border: "#374151"         // Bordas padrão
    readonly property color divider: "#1f2937"        // Separadores
    
    // ===== SPACING SCALE (8pt grid) =====
    readonly property int space1: 4      // 0.25rem
    readonly property int space2: 8      // 0.5rem  
    readonly property int space3: 12     // 0.75rem
    readonly property int space4: 16     // 1rem
    readonly property int space5: 20     // 1.25rem
    readonly property int space6: 24     // 1.5rem
    readonly property int space8: 32     // 2rem
    readonly property int space10: 40    // 2.5rem
    readonly property int space12: 48    // 3rem
    readonly property int space16: 64    // 4rem
    readonly property int space20: 80    // 5rem
    readonly property int space24: 96    // 6rem
    
    // ===== TYPOGRAPHY SCALE =====
    readonly property int text_xs: 12    // 0.75rem
    readonly property int text_sm: 14    // 0.875rem
    readonly property int text_base: 16  // 1rem
    readonly property int text_lg: 18    // 1.125rem
    readonly property int text_xl: 20    // 1.25rem
    readonly property int text_2xl: 24   // 1.5rem
    readonly property int text_3xl: 30   // 1.875rem
    readonly property int text_4xl: 36   // 2.25rem
    
    // Font weights
    readonly property int fontLight: Font.Light
    readonly property int fontNormal: Font.Normal
    readonly property int fontMedium: Font.Medium
    readonly property int fontSemiBold: Font.DemiBold
    readonly property int fontBold: Font.Bold
    
    // ===== BORDER RADIUS SCALE =====
    readonly property int radius_sm: 4   // Small elements
    readonly property int radius_md: 8   // Standard cards
    readonly property int radius_lg: 12  // Large cards
    readonly property int radius_xl: 16  // Hero elements
    readonly property int radius_2xl: 24  // Very large elements
    readonly property int radius_full: 999 // Pills/badges
    
    // ===== SHADOW LEVELS =====
    readonly property string shadow_sm: "0 1px 2px rgba(0,0,0,0.05)"
    readonly property string shadow_md: "0 4px 6px rgba(0,0,0,0.1)"
    readonly property string shadow_lg: "0 10px 15px rgba(0,0,0,0.1)"
    readonly property string shadow_xl: "0 20px 25px rgba(0,0,0,0.15)"
    readonly property string shadow_2xl: "0 25px 50px rgba(0,0,0,0.25)"
    
    // ===== RESPONSIVE BREAKPOINTS =====
    readonly property int mobile: 640    // <= 640px
    readonly property int tablet: 768    // <= 768px  
    readonly property int desktop: 1024  // <= 1024px
    readonly property int wide: 1280     // <= 1280px
    readonly property int ultrawide: 1536 // > 1536px
    
    // ===== RESPONSIVE HELPERS =====
    function getResponsiveColumns(screenWidth, maxCols, minItemWidth) {
        // Helper function for responsive grid layouts with safety checks
        const minCols = 1
        const safeMinWidth = Math.max(minItemWidth, 120)
        if (screenWidth <= 320) return Math.max(minCols, Math.min(2, Math.floor(screenWidth / safeMinWidth)))
        if (screenWidth <= mobile) return Math.max(minCols, Math.min(2, Math.floor(screenWidth / safeMinWidth)))
        if (screenWidth <= tablet) return Math.max(2, Math.min(Math.ceil(maxCols/2), Math.floor(screenWidth / minItemWidth)))
        return Math.max(2, Math.min(maxCols, Math.floor(screenWidth / minItemWidth)))
    }
    
    function getResponsiveTextSize(baseSize, screenWidth) {
        // Responsive text scaling with better mobile support
        if (screenWidth <= 320) return Math.max(baseSize - 1, text_sm)  // Less aggressive reduction
        if (screenWidth <= mobile) return Math.max(baseSize - 2, text_xs)
        if (screenWidth <= tablet) return Math.max(baseSize - 1, text_sm) 
        return baseSize
    }
    
    // ===== COMPONENT SIZES =====
    readonly property int buttonHeightSm: 32
    readonly property int buttonHeightMd: 40
    readonly property int buttonHeightLg: 48
    
    readonly property int inputHeightSm: 32
    readonly property int inputHeightMd: 40
    readonly property int inputHeightLg: 48
    
    readonly property int cardMinWidth: 280
    readonly property int cardMaxWidth: 320
    readonly property int cardHeight: 380
    
    readonly property int sidebarWidth: 320
    readonly property int sidebarCollapsedWidth: 80
    
    readonly property int headerHeight: 64
    readonly property int footerHeight: 48
    
    // ===== ANIMATION DURATIONS =====
    readonly property int animationFast: 150
    readonly property int animationMedium: 300
    readonly property int animationSlow: 500
    
    // ===== Z-INDEX LAYERS =====
    readonly property int zIndexTooltip: 1000
    readonly property int zIndexModal: 900
    readonly property int zIndexDrawer: 800
    readonly property int zIndexDropdown: 700
    readonly property int zIndexHeader: 600
    readonly property int zIndexSidebar: 500
    
    // ===== HELPER FUNCTIONS =====
    function getTextColor(backgroundColor) {
        // Função para determinar cor de texto baseada no fundo
        var r = parseInt(backgroundColor.substr(1, 2), 16)
        var g = parseInt(backgroundColor.substr(3, 2), 16)
        var b = parseInt(backgroundColor.substr(5, 2), 16)
        var brightness = (r * 299 + g * 587 + b * 114) / 1000
        return brightness > 125 ? bgPrimary : textPrimary
    }
    
    function getHoverColor(baseColor) {
        // Retorna uma versão mais clara/escura para hover
        if (baseColor === bgPrimary) return hover
        if (baseColor === accent) return accentHover
        return Qt.lighter(baseColor, 1.1)
    }
    
    function getPressedColor(baseColor) {
        // Retorna uma versão mais escura para pressed
        if (baseColor === bgPrimary) return pressed
        return Qt.darker(baseColor, 1.1)
    }
    
    // ===== SEMANTIC COLORS =====
    readonly property color statusOnline: success
    readonly property color statusOffline: textSecondary
    readonly property color statusError: danger
    readonly property color statusWarning: warning
    readonly property color statusInfo: accent
    
    // ===== BRAND COLORS =====
    readonly property color brandPrimary: accent
    readonly property color brandSecondary: "#6366f1"
    readonly property color brandTertiary: "#8b5cf6"
    
    // ===== GRADIENT DEFINITIONS =====
    readonly property var gradientPrimary: [
        { position: 0.0, color: accent },
        { position: 1.0, color: accentHover }
    ]
    
    readonly property var gradientSuccess: [
        { position: 0.0, color: success },
        { position: 1.0, color: "#16a34a" }
    ]
    
    readonly property var gradientWarning: [
        { position: 0.0, color: warning },
        { position: 1.0, color: "#d97706" }
    ]
    
    readonly property var gradientDanger: [
        { position: 0.0, color: danger },
        { position: 1.0, color: "#dc2626" }
    ]
    
    // ===== ICON SIZES =====
    readonly property int iconXs: 12
    readonly property int iconSm: 16
    readonly property int iconMd: 20
    readonly property int iconLg: 24
    readonly property int iconXl: 32
    readonly property int icon2xl: 48
    
    // ===== TRANSITION EASINGS =====
    readonly property int easingInOut: Easing.InOutQuad
    readonly property int easingOut: Easing.OutQuad
    readonly property int easingIn: Easing.InQuad
    readonly property int easingBounce: Easing.OutBounce
    readonly property int easingBack: Easing.OutBack
    readonly property int easingElastic: Easing.OutElastic
    
    // ===== COMPONENT STATES =====
    readonly property var componentStates: ({
        "default": {
            backgroundColor: bgCard,
            borderColor: border,
            textColor: textPrimary
        },
        "hover": {
            backgroundColor: hover,
            borderColor: accent,
            textColor: textPrimary
        },
        "pressed": {
            backgroundColor: pressed,
            borderColor: accentHover,
            textColor: textPrimary
        },
        "disabled": {
            backgroundColor: disabled,
            borderColor: border,
            textColor: textSecondary
        },
        "success": {
            backgroundColor: success,
            borderColor: success,
            textColor: textPrimary
        },
        "warning": {
            backgroundColor: warning,
            borderColor: warning,
            textColor: bgPrimary
        },
        "danger": {
            backgroundColor: danger,
            borderColor: danger,
            textColor: textPrimary
        }
    })
}