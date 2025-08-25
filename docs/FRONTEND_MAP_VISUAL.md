# 🎨 Mapa Visual do Frontend - Manga Uploader Pro

Este documento apresenta um mapa visual detalhado dos componentes da interface QML da aplicação.

## 📱 Layout Principal da Interface

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         MANGA UPLOADER PRO (1200x800)                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 📋 HEADER BAR (48px altura)                                                    │
│ ┌─────────────┬─────────────────────────────────────────┬─────────────────────┐ │
│ │ MANGA       │                CENTRO                   │ [HOST: Catbox ▼]   │ │
│ │ UPLOADER    │                                         │ [⚙️ AJUSTES]        │ │
│ └─────────────┴─────────────────────────────────────────┴─────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 🗂️ CONTENT AREA (RowLayout - flex height)                                      │
│ ┌─────────────┬───────────────────────────────────────┬─────────────────────┐ │
│ │             │                                       │                     │ │
│ │ 📚 LIBRARY  │         📄 MANGA DETAILS              │  🎭 ACTIONS         │ │
│ │ PANEL       │                                       │  PANEL              │ │
│ │ (320px)     │              (flex)                   │  (140px)            │ │
│ │             │                                       │                     │ │
│ │ [🔍 Search] │  🖼️ MANGA INFO                        │  [⬆️ UPLOAD]        │ │
│ │             │  ┌─────────────────────────────────┐   │  [✏️ EDIT]          │ │
│ │ 📖 Manga 1  │  │ [Cover] Title: Naruto          │   │  [⚡ GITHUB]        │ │
│ │ 📖 Manga 2  │  │         Description...          │   │                     │ │
│ │ 📖 Manga 3  │  │         Artist: Kishimoto       │   │                     │ │
│ │ ...         │  └─────────────────────────────────┘   │                     │ │
│ │             │                                       │                     │ │
│ │             │  📋 CHAPTERS                          │                     │ │
│ │             │  [✓ Todos] [✕ Nenhum] [⇅ Inverter]   │                     │ │
│ │             │  ☐ Capítulo 1   (25 img)            │                     │ │
│ │             │  ☑ Capítulo 2   (24 img)            │                     │ │
│ │             │  ☐ Capítulo 3   (26 img)            │                     │ │
│ │             │                                       │                     │ │
│ │             │  ▓▓▓▓▓░░░░░ 50% [Progress Bar]       │                     │ │
│ └─────────────┴───────────────────────────────────────┴─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 🎨 Palette de Cores (Material Design Dark)

```
🎨 COLOR SYSTEM
├── 🌑 Primary (#1a1a1a)    ■■■ Background principal (70%)
├── 🔵 Secondary (#0078d4)  ■■■ Accent azul vibrante (20%)  
├── ⚪ Tertiary (#ffffff)   ■■■ Texto branco puro (10%)
├── 🔳 Surface (#2d2d2d)    ■■■ Superfícies elevadas
├── 🫧 Hover (#404040)      ■■■ Estados de hover
├── 🟢 Success (#00c851)    ■■■ Verde para sucessos
└── 🟠 Warning (#ff9500)    ■■■ Laranja para avisos
```

## 📚 Seção Biblioteca (320px)

```
┌─────────────────────────────────────┐
│ 📚 BIBLIOTECA                       │
├─────────────────────────────────────┤
│ 🔍 [Buscar...]                     │ ← TextField (32px altura)
├─────────────────────────────────────┤
│ 📖 ┌─────┐ Naruto              📊 │ │
│    │  N  │ 700 caps               │ │ ← MangaCard (104px altura)
│    │ 🖼  │                       │ │
│    └─────┘                        │ │
├─────────────────────────────────────┤
│ 📖 ┌─────┐ One Piece          📊 │ │
│    │  O  │ 1000+ caps             │ │
│    │ 🖼  │                       │ │
│    └─────┘                        │ │
├─────────────────────────────────────┤
│ 📖 ┌─────┐ Attack on Titan     📊 │ │
│    │  A  │ 139 caps               │ │
│    │ 🖼  │                       │ │
│    └─────┘                        │ │
└────────────┬────────────────────────┘
             │ ScrollView com ListView
             └─ spacing: 2px entre items
```

### 🃏 Componente MangaCard

```
MangaCard.qml (70px altura)
┌─────────────────────────────────────────────┐
│ ┌───────┐                              ┌─┐ │
│ │   N   │ Naruto                       │▌│ │ ← Indicador seleção
│ │ (46px)│ 700 caps                     └─┘ │
│ └───────┘                                  │
└─────────────────────────────────────────────┘
├─ Avatar com primeira letra (Material.accent)
├─ Title (14px, bold) + Count (12px, opacity 0.7)  
├─ Hover/Press states com ColorAnimation
└─ Border accent quando selected
```

## 📄 Seção Detalhes do Mangá (Centro - Flex)

```
┌─────────────────────────────────────────────────────────────┐
│ 🖼️ MANGA INFO (RowLayout)                                   │
│ ┌─────────┐ Title: Naruto                                   │
│ │  COVER  │ Description: Ninja adventures...               │
│ │ (120x   │ ARTISTA: Kishimoto  AUTOR: Kishimoto           │
│ │  160px) │ STATUS: Em Andamento  GRUPO: ScanGroup         │
│ │   🖼️    │ 700 CAPÍTULOS • METADADOS                      │
│ └─────────┘                                                 │
├─────────────────────────────────────────────────────────────┤
│ 📋 CAPÍTULOS                                                │
│ ┌──────────┬──────────┬─────────────────────┐               │
│ │ ✓ Todos  │✕ Nenhum │ ⇅ Inverter Ordem    │               │
│ └──────────┴──────────┴─────────────────────┘               │
│                                                             │
│ ☐ ┌─┐ Capítulo 1                    25 img                 │
│ ☑ │●│ Capítulo 2                    24 img                 │ ← Selected
│ ☐ └─┘ Capítulo 3                    26 img                 │
│ ☐     Capítulo 4                    23 img                 │
│ ...                                                         │
│                                                             │
│ ▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░░░ 45% [Upload Progress]     │
└─────────────────────────────────────────────────────────────┘
```

### 🖼️ Cover Display Logic

```
COVER LOADING STATES
├── 🖼️ Image.Ready    → Show cover image
├── ⏳ Image.Loading  → Blue spinning loader  
├── ❌ Image.Error    → Orange warning icon
└── 📷 No URL         → Letter avatar (title[0])
```

### 📋 Chapter List Item

```
Chapter Item (40px altura)
┌─────────────────────────────────────────────┐
│ ☑ Capítulo 2                        24 img │
│ ▲   ├─ Checkbox (16px radius)              │
│ │   ├─ Chapter name (12px)                 │
│ │   └─ Image count (10px, opacity 0.6)    │
│ └─ Selected state: colorSurface background │
└─────────────────────────────────────────────┘
```

## 🎭 Painel de Ações (140px)

```
┌─────────────────────┐
│ AÇÕES               │
├─────────────────────┤ ← Label (10px, centered)
│ ┌─────────────────┐ │
│ │ [⬆] UPLOAD     │ │ ← 48px altura
│ └─────────────────┘ │
├─────────────────────┤
│ ┌─────────────────┐ │
│ │ [✎] EDITAR     │ │ ← 48px altura  
│ └─────────────────┘ │
├─────────────────────┤
│ ┌─────────────────┐ │
│ │ [⚡] GITHUB     │ │ ← 48px altura (conditional)
│ └─────────────────┘ │
└─────────────────────┘

Button States:
├── Normal: colorSurface + border
├── Hover: background color changes
├── Disabled: opacity reduced
└── Processing: spinning icon
```

## ⚙️ Settings Drawer (450px width)

```
SETTINGS DRAWER (slide from right)
┌─────────────────────────────────────────────────┐
│ CONFIGURAÇÕES                            [×]    │
├─────────────────────────────────────────────────┤
│ 📁 DIRETÓRIOS                                   │
│ ┌─────────────────────────────────────────────┐ │
│ │ Pasta raiz: [/path/to/manga]      [...] │ │
│ │ Pasta saída: [/path/to/output]    [...] │ │
│ └─────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────│
│ 🌐 HOST DE UPLOAD                               │
│ ┌─────────────────────────────────────────────┐ │
│ │ Host ativo: [Catbox        ▼]              │ │
│ │                                             │ │
│ │ [Host-specific settings shown here]         │ │
│ │ - Catbox: Userhash field                   │ │
│ │ - Imgur: Client ID + Access Token          │ │
│ │ - ImgBB: API Key                           │ │
│ │ - etc...                                   │ │
│ │                                             │ │
│ │ Workers: [5] Rate Limit: [1]s              │ │
│ └─────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────│
│ 🐱 GITHUB (OPCIONAL)                            │
│ ┌─────────────────────────────────────────────┐ │
│ │ Token: [••••••••••••••••••••••••••••••••]  │ │
│ │ Repo: [user/repository]                     │ │
│ │ Branch: [main]                              │ │
│ │ Pasta: [metadata    ▼] [🔄 REFRESH]        │ │
│ └─────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────│
│ 📝 MODO DE ATUALIZAÇÃO JSON                     │
│ ┌─────────────────────────────────────────────┐ │
│ │ [Inteligente (recomendado) ▼]              │ │
│ │ Analisa títulos • Adiciona novos • etc     │ │
│ └─────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────│
│ [        SALVAR CONFIGURAÇÕES        ]          │
└─────────────────────────────────────────────────┘
```

## 📝 Metadata Dialog (480x600)

```
METADATA DIALOG (Modal - Center)
┌───────────────────────────────────────────────┐
│ Upload com Metadados                    [×]   │
├───────────────────────────────────────────────┤
│ METADADOS PARA UPLOAD                         │
├───────────────────────────────────────────────┤
│ ┌───────────────────────────────────────────┐ │
│ │ Título: [Naruto                        ] │ │
│ └───────────────────────────────────────────┘ │
│ ┌───────────────────────────────────────────┐ │
│ │ Descrição:                              │ │
│ │ [Text area for description...           │ │
│ │                                         │ │
│ │                                        ] │ │
│ └───────────────────────────────────────────┘ │
│ ┌───────────────────────────────────────────┐ │
│ │ Artista: [Masashi Kishimoto            ] │ │
│ └───────────────────────────────────────────┘ │
│ ┌───────────────────────────────────────────┐ │
│ │ Autor: [Masashi Kishimoto              ] │ │
│ └───────────────────────────────────────────┘ │
│ ┌───────────────────────────────────────────┐ │
│ │ Grupo: [Scan Group                     ] │ │
│ └───────────────────────────────────────────┘ │
│ ┌───────────────────────────────────────────┐ │
│ │ URL Capa: [https://cover-url.jpg       ] │ │
│ └───────────────────────────────────────────┘ │
│ ┌───────────────────────────────────────────┐ │
│ │ Status: [Em Andamento         ▼]       │ │
│ └───────────────────────────────────────────┘ │
├───────────────────────────────────────────────┤
│ [  CANCELAR  ]          [    UPLOAD    ]     │
└───────────────────────────────────────────────┘
```

## 🔄 Estados e Animações

### ⏳ Loading States

```
LOADING ANIMATIONS
├── 🔄 Spinning Icons
│   ├── Upload button: ⟳ rotation (1000ms)
│   ├── Settings icon: ⚙ rotation (2000ms) 
│   └── Cover loading: Blue circle (1000ms)
├── 📊 Progress Animations
│   ├── Progress bar: width animation (250ms, OutCubic)
│   └── Upload progress: real-time updates
└── 🎨 Color Transitions
    ├── Hover states: ColorAnimation (150ms)
    ├── Button states: background transitions
    └── Selection indicators: border animations
```

### 🎭 Interactive States

```
INTERACTION STATES
├── 👆 Hover Effects
│   ├── Manga cards: background color
│   ├── Buttons: background + border color  
│   ├── Host selector: border highlight
│   └── Settings items: surface elevation
├── 👇 Press States
│   ├── Buttons: darker background
│   ├── Cards: pressed indication
│   └── Interactive areas: visual feedback
├── ✅ Selected States
│   ├── Manga: border accent color
│   ├── Chapters: checkbox + background
│   └── Host: visual indicator
└── ❌ Disabled States
    ├── Buttons: reduced opacity
    ├── Fields: muted colors
    └── Icons: grayed out
```

## 📱 Responsive Behavior

```
LAYOUT RESPONSIVENESS
├── 🪟 Fixed Window Size: 1200x800
├── 📏 Fixed Panel Widths:
│   ├── Library: 320px
│   ├── Actions: 140px  
│   └── Settings: 450px
├── 🔄 Flexible Areas:
│   ├── Main content: flex width
│   ├── Chapter list: scroll when overflow
│   └── Manga list: scroll when overflow
└── 📱 Component Scaling:
    ├── Cards maintain aspect ratios
    ├── Text scales with font settings
    └── Icons remain crisp at all sizes
```

## 🧩 Component Hierarchy

```
QML COMPONENT TREE
main.qml (Root)
├── 📋 Header (Rectangle)
│   ├── 🏷️ App Title (Label)
│   ├── 🌐 Host Selector (ComboBox)
│   └── ⚙️ Settings Button (Rectangle + MouseArea)
├── 🗂️ Content (RowLayout)
│   ├── 📚 Library Panel (Rectangle)
│   │   ├── 🔍 Search Field (TextField)
│   │   └── 📖 Manga List (ListView → MangaCard delegates)
│   ├── 📄 Details Panel (ColumnLayout)
│   │   ├── 🖼️ Manga Info (RowLayout)
│   │   │   ├── Cover (Image/Rectangle)
│   │   │   └── Info Column (Labels)
│   │   ├── 📋 Chapters Section (ColumnLayout)
│   │   │   ├── Control Buttons (GridLayout)
│   │   │   └── Chapter List (ListView)
│   │   └── 📈 Progress Bar (Rectangle)
│   └── 🎭 Actions Panel (Rectangle)
│       └── Action Buttons (Rectangles + MouseAreas)
├── ⚙️ Settings Drawer (Drawer)
│   └── Settings Content (ScrollView)
├── 📝 Metadata Dialog (Dialog)
│   └── Form Fields (TextFields + ComboBox)
└── 🗂️ File Dialogs (Platform.FolderDialog)
```

## 📊 Métricas de Interface

```
UI METRICS
├── 📏 Dimensions:
│   ├── Window: 1200x800px
│   ├── Header: 48px height
│   ├── Manga Card: 104px height
│   ├── Chapter Item: 40px height
│   ├── Action Button: 48px height
│   └── Cover Image: 120x160px
├── 🎨 Typography:
│   ├── Headers: 12-14px, Font.Medium
│   ├── Body: 11-12px, normal weight
│   ├── Labels: 8-10px, Font.Medium
│   └── Letter spacing: 0.5-1.2px
├── 🎯 Spacing:
│   ├── Margins: 8-24px
│   ├── Padding: 4-12px  
│   ├── Item spacing: 2-16px
│   └── Border radius: 4-8px
└── 🎪 Animations:
    ├── Color transitions: 150ms
    ├── Progress: 250ms OutCubic
    ├── Rotations: 1000-2000ms
    └── Hover: instant feedback
```

Este mapa visual apresenta todos os componentes da interface QML, suas dimensões, estados e interações, fornecendo uma visão completa do frontend da aplicação.