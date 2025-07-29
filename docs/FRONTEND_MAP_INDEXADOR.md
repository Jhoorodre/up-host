# MAPA VISUAL COMPLETO DO FRONTEND

Documentação visual completa da interface QML do Manga Uploader Pro - mapeando todas as seções, componentes e interações.

## Estrutura Geral da Aplicação

```
ApplicationWindow (1200x800)
├── Header (48px)
├── Main Content (RowLayout)
│   ├── Sidebar - Biblioteca (320px)
│   └── Main Area (880px)
│       ├── Welcome Screen
│       └── Manga Details + Actions Panel
├── Settings Drawer (450px)
└── Dialogs
    ├── Metadata Dialog
    ├── Folder Dialogs
    └── Progress/Status Dialogs
```

## 1. HEADER (48px altura)

```
┌─── HEADER BAR ─────────────────────────────────────────────────────────────┐
│ [MANGA UPLOADER]                              [HOST:🟧C Catbox▼] [⚙AJUSTES] │
└───────────────────────────────────────────────────────────────────────────┘
```

### Componentes:
- **Logo/Título**: "MANGA UPLOADER" (esquerda)
- **Host Selector**: Dropdown com hosts disponíveis + indicador visual
- **Settings Button**: Botão com ícone rotativo para abrir drawer

### Estados Dinâmicos:
```
Host Selector Estados:
┌─ Catbox Selecionado ─┐  ┌─ Imgur Selecionado ──┐
│ 🟧 C HOST: Catbox ▼  │  │ 🟩 I HOST: Imgur ▼   │
└──────────────────────┘  └───────────────────────┘

Settings Button:
Normal: [⚙ AJUSTES]    Hover: [⚙ AJUSTES] (ícone gira)
```

## 2. SIDEBAR - BIBLIOTECA (320px largura)

```
┌─── BIBLIOTECA ─────────────────────────┐
│ BIBLIOTECA                             │
│ ┌─────────────────────────────────────┐ │
│ │ 🔍 Buscar...                        │ │
│ └─────────────────────────────────────┘ │
│                                       │
│ ┌─────────────────────────────────────┐ │
│ │ [📖] Naruto          450 caps       │ │
│ │      🔵                             │ │
│ │                                     │ │
│ │ [📖] One Piece       1000+ caps     │ │
│ │      🔵                             │ │
│ │                                     │ │
│ │ [📖] Bleach          686 caps       │ │
│ │      🔵                             │ │
│ └─────────────────────────────────────┘ │
└───────────────────────────────────────┘
```

### Componentes do Item de Manga:
```
┌─ Card Individual (104px altura) ──────────────────────────┐
│ ┌─Cover─┐  Título do Manga              🔵               │
│ │ [📖]  │  450 caps                     Status           │  
│ │ 60x80 │                                                │
│ └───────┘                                                │
└──────────────────────────────────────────────────────────┘

Cover States:
┌─ Com Imagem ─┐  ┌─ Loading ────┐  ┌─ Erro ──┐  ┌─ Placeholder ─┐
│ [IMAGE]      │  │ [🔄 Loading] │  │ [⚠ !]   │  │ [N]           │
│              │  │              │  │          │  │ (primeira     │
│              │  │              │  │          │  │  letra)       │
└──────────────┘  └──────────────┘  └─────────┘  └───────────────┘
```

## 3. MAIN AREA (880px largura)

### 3.1 Welcome Screen (estado inicial)

```
┌─── MAIN CONTENT ─────────────────────────────────────────────────────┐
│                                                                     │
│                        ┌─────────────┐                              │
│                        │    MANGA    │                              │
│                        │  (120x120)  │                              │
│                        └─────────────┘                              │
│                                                                     │
│                  Selecione um mangá da biblioteca                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Manga Details Screen

```
┌─── MANGA DETAILS ───────────────────────────────────────────────────────────┐
│ ┌─────────────────────────────────────────────────────────┐ ┌─── AÇÕES ───┐ │
│ │ ┌─Cover──┐ Título do Manga                               │ │             │ │
│ │ │        │ Descrição aqui...                            │ │ [⬆ UPLOAD]  │ │
│ │ │120x160 │                                              │ │             │ │
│ │ │   🔵   │ ARTISTA: Nome • AUTOR: Nome • STATUS: Status │ │ [✎ EDITAR]  │ │
│ │ └────────┘ 450 CAPÍTULOS • METADADOS                   │ │             │ │
│ │                                                         │ │ [⚡ GITHUB] │ │
│ │ CAPÍTULOS                                               │ │             │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │             │ │
│ │ │ [✓ Todos] [✕ Nenhum]                                │ │ │             │ │
│ │ │ [⇅ Inverter Ordem]                                  │ │ │             │ │
│ │ └─────────────────────────────────────────────────────┘ │ │             │ │
│ │                                                         │ │             │ │
│ │ ┌─ LISTA DE CAPÍTULOS ─────────────────────────────────┐ │ │             │ │
│ │ │ ◯ Cap. 001 - Início                      25 img     │ │ │             │ │
│ │ │ ● Cap. 002 - Aventura                    30 img     │ │ │             │ │
│ │ │ ◯ Cap. 003 - Batalha                     28 img     │ │ │             │ │
│ │ │ ● Cap. 004 - Final                       35 img     │ │ │             │ │
│ │ │ ...                                                  │ │ │             │ │
│ │ └─────────────────────────────────────────────────────┘ │ │             │ │
│ │                                                         │ │             │ │
│ │ ▓▓▓▓▓▓░░░░ 60% Complete                                │ │             │ │
│ └─────────────────────────────────────────────────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Breakdown dos Controles de Capítulos:

```
┌─── CONTROLES DE BATCH ────────────────────────────┐
│ ┌─[✓ Todos]─┐  ┌─[✕ Nenhum]──┐                   │
│ │   Hover:   │  │   Hover:    │                   │
│ │   Azul     │  │   Vermelho  │                   │
│ └───────────-┘  └─────────────┘                   │
│                                                   │
│ ┌─[⇅ Inverter Ordem]─────────────────────────────┐ │
│ │              Hover: Laranja                    │ │
│ └───────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────┘
```

### Lista de Capítulos - Estados:

```
┌─ Item Normal ─────────────────────────────┐  ┌─ Item Selecionado ────────────────────┐
│ ◯ Cap. 001 - Início            25 img    │  │ ● Cap. 002 - Aventura        30 img  │
│   (background: transparente)              │  │   (background: colorSurface)          │
└───────────────────────────────────────────┘  └───────────────────────────────────────┘
```

## 4. ACTIONS PANEL (140px largura)

```
┌─── AÇÕES ──────────┐
│      AÇÕES         │
│                    │
│ ┌────────────────┐ │
│ │ ⬆  UPLOAD      │ │ <- Estado normal/hover/disabled
│ │                │ │
│ └────────────────┘ │
│                    │
│ ┌────────────────┐ │
│ │ ✎  EDITAR      │ │ <- Estado normal/hover/disabled  
│ │                │ │
│ └────────────────┘ │
│                    │
│ ┌────────────────┐ │
│ │ ⚡ GITHUB      │ │ <- Condicional (só aparece se configurado)
│ │                │ │
│ └────────────────┘ │
│                    │
│                    │
└────────────────────┘
```

### Estados dos Botões de Ação:

```
Upload Button States:
┌─ Normal ─────────┐  ┌─ Hover ──────────┐  ┌─ Processing ─────┐  ┌─ Disabled ───────┐
│ ⬆  UPLOAD       │  │ ⬆  UPLOAD       │  │ ⟳  PROCESSANDO… │  │ ⬆  UPLOAD       │
│ (azul/branco)   │  │ (invertido)     │  │ (ícone girando) │  │ (acinzentado)   │
└─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘

Edit Button States:
┌─ Normal ─────────┐  ┌─ Hover ──────────┐  ┌─ Disabled ───────┐
│ ✎  EDITAR       │  │ ✎  EDITAR       │  │ ✎  EDITAR       │
│ (laranja/branco)│  │ (invertido)     │  │ (acinzentado)   │
└─────────────────┘  └─────────────────┘  └─────────────────┘

GitHub Button States:
┌─ Normal ─────────┐  ┌─ Hover ──────────┐  ┌─ Hidden ─────────┐
│ ⚡ GITHUB       │  │ ⚡ GITHUB       │  │ (não aparece se  │
│ (verde/branco)  │  │ (invertido)     │  │  não configurado)│
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

## 5. SETTINGS DRAWER (450px largura)

```
┌─── CONFIGURAÇÕES ─────────────────────────────────────────────────────────────────────┐
│ CONFIGURAÇÕES                                                              [×]        │
│ ────────────────────────────────────────────────────────────────────────────────────│
│                                                                                      │
│ DIRETÓRIOS                                                                           │
│ ────────────────────────────────────────────────────────────────────────────────────│
│ Pasta raiz dos mangás                                                                │
│ ┌──────────────────────────────────────────────────────────────────┐ ┌─────────────┐ │
│ │ C:\Manga                                                         │ │    ...      │ │
│ └──────────────────────────────────────────────────────────────────┘ └─────────────┘ │
│                                                                                      │
│ Pasta de saída dos metadados                                                         │
│ ┌──────────────────────────────────────────────────────────────────┐ ┌─────────────┐ │
│ │ C:\Manga_Output                                                  │ │    ...      │ │
│ └──────────────────────────────────────────────────────────────────┘ └─────────────┘ │
│                                                                                      │
│ HOST DE UPLOAD                                                                       │
│ ────────────────────────────────────────────────────────────────────────────────────│
│ Host ativo                                                                           │
│ ┌──────────────────────────────────────────────────────────────────────────────────┐ │
│ │ Catbox                                                                      ▼    │ │
│ └──────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                      │
│ ┌─ Catbox Settings (conditional) ────────────────────────────────────────────────┐   │
│ │ Catbox Userhash (opcional)                                                     │   │
│ │ ┌────────────────────────────────────────────────────────────────────────────┐ │   │
│ │ │ Se tiver userhash...                                                       │ │   │
│ │ └────────────────────────────────────────────────────────────────────────────┘ │   │
│ └────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│ ┌─ Imgur Settings (conditional) ─────────────────────────────────────────────────┐   │
│ │ Imgur Client ID                                                                │   │
│ │ ┌────────────────────────────────────────────────────────────────────────────┐ │   │
│ │ │ Client ID do Imgur                                                         │ │   │
│ │ └────────────────────────────────────────────────────────────────────────────┘ │   │
│ │ Imgur Access Token                                                             │   │
│ │ ┌────────────────────────────────────────────────────────────────────────────┐ │   │
│ │ │ Access Token do Imgur                                                      │ │   │
│ │ └────────────────────────────────────────────────────────────────────────────┘ │   │
│ └────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│ ┌─ Performance Settings ─────────────────────────────────────────────────────────┐   │
│ │ Workers simultâneos          Rate limit (segundos)                             │   │
│ │ ┌──────────────────────────┐  ┌─────────────────────────────────────────────┐ │   │
│ │ │ 5                    ▲▼  │  │ 1                                       ▲▼ │ │   │
│ │ └──────────────────────────┘  └─────────────────────────────────────────────┘ │   │
│ └────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│ GITHUB (OPCIONAL)                                                                    │
│ ────────────────────────────────────────────────────────────────────────────────────│
│ Token de acesso                                                                      │
│ ┌──────────────────────────────────────────────────────────────────────────────────┐ │
│ │ ••••••••••••••••••••••••••••••••••••••••••••                                   │ │
│ └──────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                      │
│ Repositório (usuário/repo)                                                           │
│ ┌──────────────────────────────────────────────────────────────────────────────────┐ │  
│ │ usuario/repositorio                                                              │ │
│ └──────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                      │
│ Branch                                                                               │
│ ┌──────────────────────────────────────────────────────────────────────────────────┐ │
│ │ main                                                                             │ │
│ └──────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                      │
│ Pasta no repositório                                                                 │
│ ┌──────────────────────────────────────────────────────────────────────────────┐ ┌─┐ │
│ │ 🏠 (raiz)                                                                 ▼  │ │🔄│ │
│ └──────────────────────────────────────────────────────────────────────────────┘ └─┘ │
│                                                                                      │
│ MODO DE ATUALIZAÇÃO JSON                                                             │
│ ────────────────────────────────────────────────────────────────────────────────────│
│ Modo de atualização                                                                  │
│ ┌──────────────────────────────────────────────────────────────────────────────────┐ │
│ │ Adicionar novos (preserva existentes)                                       ▼   │ │
│ └──────────────────────────────────────────────────────────────────────────────────┘ │
│ Mantém capítulos existentes • Adiciona novos • Atualiza duplicados                  │
│                                                                                      │
│ ┌─ SALVAR CONFIGURAÇÕES ─────────────────────────────────────────────────────────────┐ │
│ │                              SALVAR CONFIGURAÇÕES                                 │ │
│ └────────────────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

### Configurações por Host (condicionais):

```
┌─ Catbox (Simples) ──────────────────┐  ┌─ Imgur (OAuth) ─────────────────────┐
│ Userhash (opcional)                 │  │ Client ID                            │
│ ┌─────────────────────────────────┐ │  │ ┌──────────────────────────────────┐ │
│ │ [campo texto]                   │ │  │ │ [campo obrigatório]              │ │
│ └─────────────────────────────────┘ │  │ └──────────────────────────────────┘ │
└─────────────────────────────────────┘  │ Access Token                         │
                                         │ ┌──────────────────────────────────┐ │
┌─ ImgBB (API Key) ───────────────────┐  │ │ [campo obrigatório]              │ │
│ API Key                             │  │ └──────────────────────────────────┘ │
│ ┌─────────────────────────────────┐ │  └─────────────────────────────────────┘
│ │ [campo obrigatório]             │ │
│ └─────────────────────────────────┘ │  ┌─ Imgbox (Cookie) ───────────────────┐
└─────────────────────────────────────┘  │ Session Cookie (opcional)            │
                                         │ ┌──────────────────────────────────┐ │
┌─ Hosts sem config (Info apenas) ───┐  │ │ [campo wrap longo]               │ │
│ ✓ Gofile está pronto para uso       │  │ └──────────────────────────────────┘ │
│ Ótimo para múltiplos arquivos       │  │ [Testar Cookie] [resultado...]       │
│ ✅ Links diretos otimizados!        │  │ Como obter cookie: 1. Login...       │
└─────────────────────────────────────┘  └─────────────────────────────────────┘
```

## 6. METADATA DIALOG (480x600)

```
┌─── METADADOS PARA UPLOAD ──────────────────────────────────────────┐
│ METADADOS PARA UPLOAD                                              │
│ ──────────────────────────────────────────────────────────────────│
│                                                                    │
│ ┌────────────────────────────────────────────────────────────────┐ │
│ │ Título                                                         │ │
│ └────────────────────────────────────────────────────────────────┘ │
│                                                                    │
│ ┌────────────────────────────────────────────────────────────────┐ │
│ │ Descrição...                                                   │ │
│ │                                                                │ │
│ │                                                                │ │
│ └────────────────────────────────────────────────────────────────┘ │
│                                                                    │
│ ┌────────────────────────────────────────────────────────────────┐ │
│ │ Artista                                                        │ │
│ └────────────────────────────────────────────────────────────────┘ │
│                                                                    │
│ ┌────────────────────────────────────────────────────────────────┐ │
│ │ Autor                                                          │ │
│ └────────────────────────────────────────────────────────────────┘ │
│                                                                    │
│ ┌────────────────────────────────────────────────────────────────┐ │
│ │ Grupo de tradução (opcional)                                   │ │
│ └────────────────────────────────────────────────────────────────┘ │
│                                                                    │
│ ┌────────────────────────────────────────────────────────────────┐ │
│ │ URL da capa                                                    │ │
│ └────────────────────────────────────────────────────────────────┘ │
│                                                                    │
│ ┌────────────────────────────────────────────────────────────────┐ │
│ │ Em Andamento                                                ▼  │ │
│ └────────────────────────────────────────────────────────────────┘ │
│                                                                    │
│ ┌─────────────────────────────┐ ┌─────────────────────────────────┐ │
│ │          CANCELAR           │ │           UPLOAD                │ │
│ └─────────────────────────────┘ └─────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────┘
```

### Estados do Dialog:

```
┌─ Upload Mode ──────────────┐  ┌─ Edit Mode ────────────────┐
│ METADADOS PARA UPLOAD      │  │ EDITAR METADADOS           │
│                            │  │                            │
│ [CANCELAR] [UPLOAD]        │  │ [CANCELAR] [SALVAR]        │
└────────────────────────────┘  └────────────────────────────┘
```

## 7. FLUXO DE INTERAÇÕES

### 7.1 Navegação Principal:

```
[Aplicação Inicia] → [Welcome Screen]
         ↓
[Usuário clica manga na biblioteca] → [Carrega Manga Details]
         ↓
[Mostra capítulos + controles] → [Usuário faz seleções]
         ↓  
[Clica UPLOAD] → [Abre Metadata Dialog] → [Upload inicia]
         ↓
[Progress bar ativa] → [Upload completo] → [Volta ao normal]
```

### 7.2 Configurações:

```
[Clica ⚙ AJUSTES] → [Drawer abre da direita]
         ↓
[Usuário configura] → [Clica SALVAR] → [Drawer fecha]
         ↓
[Configurações aplicadas] → [Interface atualizada]
```

### 7.3 Estados de Loading:

```
Estado Normal:
┌──────────────────────────┐
│ Lista normal de capítulos│
│ Botões enabled           │
│ Progress bar hidden      │
└──────────────────────────┘

Estado Loading/Processing:
┌──────────────────────────┐
│ Lista readonly           │
│ Botões disabled          │
│ ▓▓▓▓░░░░ Progress visible│
└──────────────────────────┘
```

## 8. RESPONSIVIDADE E ADAPTAÇÕES

### Tamanhos de Componentes:
- **Sidebar**: Fixa em 320px
- **Actions Panel**: Fixa em 140px  
- **Main Content**: Flexível (resto do espaço)
- **Settings Drawer**: Fixa em 450px
- **Header**: Fixa em 48px

### Breakpoints Visuais:
```
Mínimo: 800x600 (funcional)
Ideal:  1200x800 (design padrão)  
Máximo: Ilimitado (scales bem)
```

## 9. PALETA DE CORES E TEMAS

```
Cores Principais:
- colorPrimary:   #1a1a1a (fundo escuro)
- colorSecondary: #0078d4 (azul acentos)  
- colorTertiary:  #ffffff (texto branco)
- colorSurface:   #2d2d2d (superfícies)
- colorHover:     #404040 (hover states)
- colorSuccess:   #00c851 (verde sucessos)
- colorWarning:   #ff9500 (laranja avisos)
```

### Aplicação de Cores:
```
┌─ Hierarquia Visual ─────────────────────────────┐
│ Background: colorPrimary (#1a1a1a)             │
│ Cards/Panels: colorSurface (#2d2d2d)           │  
│ Text: colorTertiary (#ffffff)                  │
│ Accents: colorSecondary (#0078d4)              │
│ Actions: colorSuccess/colorWarning             │
└─────────────────────────────────────────────────┘
```

## 10. COMPONENTES ESPECIAIS

### 10.1 UploadProgress Component:
```
┌─ Progress Tracking ──────────────────────────────┐
│ ▓▓▓▓▓▓░░░░ 60% Complete                        │
│ Uploading chapter 12 of 20...                   │
│ [Estado dinâmico baseado em backend.progress]   │
└──────────────────────────────────────────────────┘
```

### 10.2 MangaCard Component:
```
┌─ Reutilizável ──────────────────────────────────┐
│ Usado na biblioteca                             │
│ Estados: normal, hover, selected, loading       │
│ Suporta: cover, placeholder, error states       │
└─────────────────────────────────────────────────┘
```

### 10.3 IndexadorDialog Component:
```
┌─ Futuro ────────────────────────────────────────┐
│ Dialog para gerenciar sistema de indexação     │
│ Não implementado no código atual               │  
│ Planejado para gerenciamento de séries         │
└─────────────────────────────────────────────────┘
```

---

## Resultado Visual Final

A interface oferece:
- **Layout profissional** com sidebar + main content + drawer
- **Navegação intuitiva** entre biblioteca e detalhes 
- **Controles batch** para seleção em massa
- **Configuração completa** de hosts e GitHub
- **Feedback visual** em tempo real
- **Design moderno** com Material Design dark theme
- **Funcionalidade completa** para upload de mangás

A aplicação mantém estado consistente entre todas as telas e oferece uma experiência fluída para gerenciar grandes coleções de mangás.