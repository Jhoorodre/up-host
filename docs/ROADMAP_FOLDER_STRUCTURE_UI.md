# Roadmap: Melhorar Sistema de Navegação de Pastas

## Objetivo
Manter a interface atual mas implementar sistema de navegação mais flexível que detecta automaticamente diferentes estruturas de pastas, removendo a necessidade de configuração manual.

## Interface Atual (Manter) ✅

### **Layout Existente Detalhado (Corrigido):**
```
╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║  MANGA UPLOADER PRO                                                                                                           ║
╠═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                                               ║
║  [🌐 Host: Catbox           ▼]  [⚙️ Configurações]                                    [🔄 Refresh]  [📤 Upload Selecionados] ║
║                                                                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                                               ║
║  BIBLIOTECA (350px)                           │  ÁREA PRINCIPAL (850px)                                                     ║
║  ┌─────────────────────────────────────────┐  │  ┌─────────────────────────────────────────────────────────────────────┐   ║
║  │  BIBLIOTECA                             │  │  │                                                                     │   ║
║  │  ▔▔▔▔▔▔▔▔▔▔▔                             │  │  │           [Quando nenhum manga selecionado]                        │   ║
║  │                                         │  │  │                                                                     │   ║
║  │  ┌───────────────────────────────────┐   │  │  │  ┌─────────────────────────────────────────────────────────────┐   │   ║
║  │  │ 🔍 Buscar mangás...               │   │  │  │  │                    📖                                      │   │   ║
║  │  └───────────────────────────────────┘   │  │  │  │                   MANGA                                    │   │   ║
║  │                                         │  │  │  │                                                             │   │   ║
║  │  ┌─ Lista de Mangás ─────────────────┐   │  │  │  │            Selecione um mangá                               │   │   ║
║  │  │                                   │   │  │  │  │            da biblioteca                                   │   │   ║
║  │  │ 📖 ┌─ One Piece ──────────────┐   │   │  │  │  └─────────────────────────────────────────────────────────────┘   │   ║
║  │  │    │ [📸]  One Piece          │   │   │  │  │                                                                     │   ║
║  │  │    │ 📁 MangaPlus • 2 caps    │ ◄─┼───┼──┼─ SELECIONADO                                                           │   ║
║  │  │    └──────────────────────────┘   │   │  │  │                                                                     │   ║
║  │  │                                   │   │  │  │          [Quando manga selecionado - "One Piece"]                  │   ║
║  │  │ 📖 ┌─ Demon Slayer ──────────┐    │   │  │  │                                                                     │   ║
║  │  │    │ [📸]  Demon Slayer       │   │   │  │  │  ┌─────────────────────────────────────────────────────────────┐   │   ║
║  │  │    │ 📁 MangaPlus • 1 cap     │   │   │  │  │  │ 📖 ONE PIECE                                               │   │   ║
║  │  │    └──────────────────────────┘   │   │  │  │  │ ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔                                               │   │   ║
║  │  │                                   │   │  │  │  │                                                             │   │   ║
║  │  │ 📖 ┌─ Jujutsu Kaisen ────────┐    │   │  │  │  │ 🎯 2 capítulos encontrados                                 │   │   ║
║  │  │    │ [📸]  Jujutsu Kaisen     │   │   │  │  │  │ 📁 /home/user/Manga/MangaPlus/One Piece                    │   │   ║
║  │  │    │ 📁 TCB Scans • 2 caps    │   │   │  │  │  │                                                             │   │   ║
║  │  │    └──────────────────────────┘   │   │  │  │  │ ┌─ CAPÍTULOS DETECTADOS ─────────────────────────────────┐   │   │   ║
║  │  │                                   │   │  │  │  │ │                                                       │   │   │   ║
║  │  │ 📖 ┌─ Attack on Titan ───────┐    │   │  │  │  │ │ ☐ [MangaPlus] Capítulo 1090 (15 imagens)            │   │   │   ║
║  │  │    │ [📸]  Attack on Titan    │   │   │  │  │  │ │   📁 MangaPlus/One Piece/Capítulo 1090              │   │   │   ║
║  │  │    │ 📁 TCB Scans • 1 cap     │   │   │  │  │  │ │                                                       │   │   │   ║
║  │  │    └──────────────────────────┘   │   │  │  │  │ │ ☐ [MangaPlus] Capítulo 1089 (18 imagens)            │   │   │   ║
║  │  │                                   │   │  │  │  │ │   📁 MangaPlus/One Piece/Capítulo 1089              │   │   │   ║
║  │  │ 📖 ┌─ Naruto ────────────────┐    │   │  │  │  │ │                                                       │   │   │   ║
║  │  │    │ [📸]  Naruto             │   │   │  │  │  │ └───────────────────────────────────────────────────────┘   │   │   ║
║  │  │    │ 📁 Coleção • 2 caps      │   │   │  │  │  │                                                             │   │   ║
║  │  │    └──────────────────────────┘   │   │  │  │ ┌─ SELEÇÃO PARA UPLOAD ──────────────────────────────────┐   │   │   ║
║  │  │                                   │   │  │  │ │                                                       │   │   │   ║
║  │  │ [📄 Scroll para mais mangás...]   │   │  │  │ │ 🎯 2 capítulos selecionados (33 imagens)             │   │   │   ║
║  │  └───────────────────────────────────┘   │  │  │  │                                                       │   │   │   ║
║  │                                         │  │  │  │ • [MangaPlus] One Piece - Capítulo 1090              │   │   │   ║
║  └─────────────────────────────────────────┘  │  │  │ • [MangaPlus] One Piece - Capítulo 1089              │   │   │   ║
║                                               │  │  │ │                                                       │   │   │   ║
║                                               │  │  │ │ ┌─────────────────────────────────────────────────┐   │   │   │   ║
║                                               │  │  │ │ │          🚀 FAZER UPLOAD AGORA                 │   │   │   │   ║
║                                               │  │  │ │ └─────────────────────────────────────────────────┘   │   │   │   ║
║                                               │  │  │ │                                                       │   │   │   ║
║                                               │  │  │ │ ┌─────────────────────────────────────────────────┐   │   │   │   ║
║                                               │  │  │ │ │          🗑️ LIMPAR SELEÇÃO                     │   │   │   │   ║
║                                               │  │  │ │ └─────────────────────────────────────────────────┘   │   │   │   ║
║                                               │  │  │ └───────────────────────────────────────────────────────┘   │   │   ║
║                                               │  │  └─────────────────────────────────────────────────────────────┘   │   ║
║                                               │  └─────────────────────────────────────────────────────────────────────┘   ║
║                                               │                                                                             ║
╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
```

**MANTER:** Sidebar com lista de mangás + área principal de detalhes

### **Estados da Interface (Detalhado):**

#### **Estado 1: Nenhum Manga Selecionado**
```
╔═ ÁREA PRINCIPAL ═══════════════════════════════════════════════════════════════════╗
║                                                                                   ║
║                           ┌─────────────────────────────────────┐                 ║
║                           │                                     │                 ║
║                           │               📖                    │                 ║
║                           │              MANGA                  │                 ║
║                           │                                     │                 ║
║                           │        Selecione um mangá           │                 ║
║                           │        da biblioteca                │                 ║
║                           │                                     │                 ║
║                           └─────────────────────────────────────┘                 ║
║                                                                                   ║
╚═══════════════════════════════════════════════════════════════════════════════════╝
```

#### **Estado 2: Manga Selecionado - Estrutura Simples**
```
╔═ ÁREA PRINCIPAL - "Naruto" ═══════════════════════════════════════════════════════╗
║                                                                                   ║
║  📖 NARUTO                                                                        ║
║  ▔▔▔▔▔▔▔▔▔▔                                                                        ║
║                                                                                   ║
║  🎯 700 capítulos encontrados                                                     ║
║  📁 /home/user/Manga/Naruto                                                      ║
║                                                                                   ║
║  ┌─ CAPÍTULOS DETECTADOS (Estrutura: Manga/Capítulo) ────────────────────────┐   ║
║  │                                                                           │   ║
║  │ ☐ Capítulo 700 (23 imagens)                                             │   ║
║  │   📁 Naruto/Cap 700                                                      │   ║
║  │                                                                           │   ║
║  │ ☐ Capítulo 699 (21 imagens)                                             │   ║
║  │   📁 Naruto/Cap 699                                                      │   ║
║  │                                                                           │   ║
║  │ ☐ Capítulo 698 (19 imagens)                                             │   ║
║  │   📁 Naruto/Cap 698                                                      │   ║
║  │                                                                           │   ║
║  │ ... (mais 697 capítulos)                                                │   ║
║  └───────────────────────────────────────────────────────────────────────────┘   ║
║                                                                                   ║
╚═══════════════════════════════════════════════════════════════════════════════════╝
```

### **O que são Scan Groups? 🔍**

**Scan Groups** são equipes que digitalizam mangás. Cada grupo tem seu nome e muitas vezes o usuário organiza os mangás por grupo:

**Estrutura no Disco:**
```
📁 /home/user/Manga/
├── 📁 MangaPlus/              ← Nome do grupo de scan
│   ├── 📁 One Piece/
│   │   ├── 📁 Capítulo 1090/  ← Capítulo escaneado por MangaPlus
│   │   └── 📁 Capítulo 1089/
│   └── 📁 Naruto/
│       └── 📁 Capítulo 700/
├── 📁 TCB Scans/              ← Outro grupo de scan
│   ├── 📁 One Piece/
│   │   ├── 📁 Capítulo 1090/  ← Mesmo capítulo, scan diferente
│   │   └── 📁 Capítulo 1089/
│   └── 📁 Attack on Titan/
│       └── 📁 Capítulo 139/
└── 📁 VizMedia/               ← Scan oficial
    └── 📁 One Piece/
        └── 📁 Capítulo 1090/  ← Versão oficial
```

#### **Estado 3: Manga de um Scan Específico - "One Piece"**
```
╔═ ÁREA PRINCIPAL - "One Piece" ═══════════════════════════════════════════════════╗
║                                                                                  ║
║  📖 ONE PIECE                                                                    ║
║  ▔▔▔▔▔▔▔▔▔▔▔▔▔▔                                                                   ║
║                                                                                  ║
║  🎯 2 capítulos encontrados                                                     ║
║  📁 /home/user/Manga/MangaPlus/One Piece                                        ║
║                                                                                  ║
║  ┌─ CAPÍTULOS DETECTADOS (Scan: MangaPlus) ────────────────────────────────────┐ ║
║  │                                                                            │ ║
║  │ ☐ [MangaPlus] Capítulo 1090 (15 imagens)                                 │ ║
║  │   📁 MangaPlus/One Piece/Capítulo 1090                                    │ ║
║  │                                                                            │ ║
║  │ ☐ [MangaPlus] Capítulo 1089 (18 imagens)                                 │ ║
║  │   📁 MangaPlus/One Piece/Capítulo 1089                                    │ ║
║  │                                                                            │ ║
║  └────────────────────────────────────────────────────────────────────────────┘ ║
║                                                                                  ║
║  💡 Capítulos do grupo MangaPlus                                                ║
║                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════╝
```

#### **Estado 4: Manga Selecionado - Estrutura com Volumes**
```
╔═ ÁREA PRINCIPAL - "Attack on Titan" ═════════════════════════════════════════════╗
║                                                                                  ║
║  📖 ATTACK ON TITAN                                                              ║
║  ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔                                                             ║
║                                                                                  ║
║  🎯 139 capítulos encontrados organizados por volumes                           ║
║  📁 /home/user/Manga/Attack on Titan                                            ║
║                                                                                  ║
║  ┌─ CAPÍTULOS DETECTADOS (Estrutura: Manga/Volume/Capítulo) ──────────────────┐ ║
║  │                                                                            │ ║
║  │ ☐ [Volume 34] Capítulo 139 (29 imagens) - FINAL                          │ ║
║  │   📁 Attack on Titan/Volume 34/Cap 139                                    │ ║
║  │                                                                            │ ║
║  │ ☐ [Volume 34] Capítulo 138 (28 imagens)                                  │ ║
║  │   📁 Attack on Titan/Volume 34/Cap 138                                    │ ║
║  │                                                                            │ ║
║  │ ☐ [Volume 34] Capítulo 137 (27 imagens)                                  │ ║
║  │   📁 Attack on Titan/Volume 34/Cap 137                                    │ ║
║  │                                                                            │ ║
║  │ ☐ [Volume 33] Capítulo 136 (26 imagens)                                  │ ║
║  │   📁 Attack on Titan/Volume 33/Cap 136                                    │ ║
║  │                                                                            │ ║
║  │ ... (mais 135 capítulos em volumes anteriores)                            │ ║
║  └────────────────────────────────────────────────────────────────────────────┘ ║
║                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════╝
```

#### **Estado 5: Estrutura Mista Detectada**
```
╔═ ÁREA PRINCIPAL - "My Hero Academia" ════════════════════════════════════════════╗
║                                                                                  ║
║  📖 MY HERO ACADEMIA                                                             ║
║  ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔                                                            ║
║                                                                                  ║
║  🎯 380 capítulos encontrados - estrutura mista detectada                       ║
║  📁 /home/user/Manga/My Hero Academia                                           ║
║                                                                                  ║
║  ┌─ CAPÍTULOS DETECTADOS (Estrutura: Mista) ──────────────────────────────────┐ ║
║  │                                                                            │ ║
║  │ ☐ [Oficial] Capítulo 380 (22 imagens)                                    │ ║
║  │   📁 My Hero Academia/Oficial/Cap 380                                     │ ║
║  │                                                                            │ ║
║  │ ☐ Capítulo 379 (19 imagens)                                              │ ║
║  │   📁 My Hero Academia/Cap 379                                             │ ║
║  │                                                                            │ ║
║  │ ☐ [Volume 37] Capítulo 378 (20 imagens)                                  │ ║
║  │   📁 My Hero Academia/Volume 37/Cap 378                                   │ ║
║  │                                                                            │ ║
║  │ ☐ [Scan] Capítulo 377 (21 imagens)                                       │ ║
║  │   📁 My Hero Academia/Scan Groups/MHA Scan/Cap 377                        │ ║
║  │                                                                            │ ║
║  │ ... (mais 376 capítulos com estruturas variadas)                          │ ║
║  └────────────────────────────────────────────────────────────────────────────┘ ║
║                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════╝
```

## Problema Atual ❌

### **Limitação da Implementação:**
- Sistema atual só funciona com estrutura fixa: `Manga/Capítulo/`
- Usuários com outras organizações não conseguem usar o app
- Implementação com 5 estruturas diferentes é complexa demais

### **Estruturas Não Suportadas:**
```
❌ scan/NomeScan/Manga/Capítulo/
❌ Manga/Volume/Capítulo/
❌ Manga/imagens_diretas/
❌ Estruturas mistas
```

## Nova Solução ✅

### **Sistema de Detecção Automática:**
- **Escaneamento recursivo** inteligente que detecta qualquer estrutura
- **Zero configuração** do usuário
- **Mesmo visual** da interface atual
- **Funciona com qualquer organização** de pastas

### **Como Funcionará:**

#### **1. Detecção Automática de Estruturas:**
```python
def _scan_recursive(self, root_path: Path) -> List[Chapter]:
    """Detecta automaticamente qualquer estrutura de pastas"""
    chapters = []
    
    def find_chapters(path: Path, current_path: str = ""):
        for item in sorted(path.iterdir()):
            if item.is_dir():
                # Verifica se é uma pasta de capítulo (contém imagens)
                if self._has_manga_images(item):
                    chapter_name = current_path + item.name if current_path else item.name
                    chapters.append(Chapter(
                        name=chapter_name,
                        path=item,
                        images=[]
                    ))
                else:
                    # Continua navegando recursivamente
                    new_path = f"{current_path}{item.name}/" if current_path else f"{item.name}/"
                    find_chapters(item, new_path)
    
    find_chapters(root_path)
    return chapters

def _has_manga_images(self, path: Path) -> bool:
    """Verifica se pasta contém imagens de manga"""
    extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    return any(f.suffix.lower() in extensions for f in path.iterdir() if f.is_file())
```

#### **2. Interface Unchanged:**
- **Biblioteca (esquerda)** continua igual
- **Detalhes (direita)** continua igual  
- **Lista de capítulos** mostra estrutura detectada automaticamente

#### **3. Exemplo de Detecção:**

**Estrutura no disco (Como usuário organiza):**
```
📁 /home/user/Manga/
├── 📁 MangaPlus/                    ← Grupo de scan
│   ├── 📁 One Piece/
│   │   ├── 📁 Capítulo 1090/        ← App detecta: One Piece
│   │   └── 📁 Capítulo 1089/
│   └── 📁 Demon Slayer/
│       └── 📁 Capítulo 200/         ← App detecta: Demon Slayer
├── 📁 TCB Scans/                    ← Outro grupo de scan
│   ├── 📁 Jujutsu Kaisen/           ← App detecta: Jujutsu Kaisen (diferente!)
│   │   ├── 📁 Capítulo 250/
│   │   └── 📁 Capítulo 249/
│   └── 📁 Attack on Titan/
│       └── 📁 Capítulo 139/         ← App detecta: Attack on Titan
└── 📁 Coleção Pessoal/              ← Pasta sem nome de scan
    └── 📁 Naruto/
        ├── 📁 Volume 72/
        │   └── 📁 Cap 700/          ← App detecta: Naruto
        └── 📁 Cap 701/
```

**Como o App Detecta na Biblioteca:**
```
🔍 App escaneia recursivamente e encontra:

📖 One Piece          (2 caps em MangaPlus)
📖 Demon Slayer       (1 cap em MangaPlus)  
📖 Jujutsu Kaisen     (2 caps em TCB Scans)
📖 Attack on Titan    (1 cap em TCB Scans)
📖 Naruto              (2 caps em Coleção Pessoal)
```

**Como Aparece na Biblioteca (Sidebar):**
```
🔍 Buscar mangás...
────────────────────
📖 One Piece                    2 caps
   📁 MangaPlus

📖 Demon Slayer                 1 cap  
   📁 MangaPlus

📖 Jujutsu Kaisen               2 caps
   📁 TCB Scans

📖 Attack on Titan              1 cap
   📁 TCB Scans

📖 Naruto                       2 caps
   📁 Coleção Pessoal
```

**Quando usuário clica em "One Piece":**
```
☐ [MangaPlus] Capítulo 1090 (15 imagens)
☐ [MangaPlus] Capítulo 1089 (18 imagens)
```

**Quando usuário clica em "Naruto" (estrutura mista):**
```
☐ [Volume 72] Cap 700 (23 imagens)
☐ Cap 701 (21 imagens)
```

## Funcionalidades Batch e Ordenação 📋

### **Controles de Seleção em Massa:**
```
╔═ ÁREA PRINCIPAL - "One Piece" (Com Batch Controls) ═════════════════════════════════════════════════════════════════════════╗
║                                                                                                                              ║
║  📖 ONE PIECE                                                                                                                ║
║  ▔▔▔▔▔▔▔▔▔▔▔▔▔▔                                                                                                                 ║
║                                                                                                                              ║
║  🎯 1090 capítulos encontrados                                                                                               ║
║  📁 /home/user/Manga/MangaPlus/One Piece                                                                                    ║
║                                                                                                                              ║
║  ┌─ CONTROLES DE SELEÇÃO ────────────────────────────────────────────────────────────────────────────────────────────────┐ ║
║  │                                                                                                                        │ ║
║  │ [☑️ Selecionar Todos] [☐ Desmarcar Todos] [📋 Últimos 10] [📋 Últimos 50] [📋 Range: ___ até ___]                     │ ║
║  │                                                                                                                        │ ║
║  │ [📈 Crescente 1→1090] [📉 Decrescente 1090→1] [📅 Por Data] [📝 Por Nome] [📊 Por Tamanho (imgs)]                     │ ║
║  │                                                                                                                        │ ║
║  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘ ║
║                                                                                                                              ║
║  ┌─ CAPÍTULOS DETECTADOS ─────────────────────────────────────────────────────────────────────────────────────────────────┐ ║
║  │                                                                                                                        │ ║
║  │ ☑️ [MangaPlus] Capítulo 1090 (15 imagens)                                                                            │ ║
║  │    📁 MangaPlus/One Piece/Capítulo 1090                                                                              │ ║
║  │                                                                                                                        │ ║
║  │ ☑️ [MangaPlus] Capítulo 1089 (18 imagens)                                                                            │ ║
║  │    📁 MangaPlus/One Piece/Capítulo 1089                                                                              │ ║
║  │                                                                                                                        │ ║
║  │ ☑️ [MangaPlus] Capítulo 1088 (20 imagens)                                                                            │ ║
║  │    📁 MangaPlus/One Piece/Capítulo 1088                                                                              │ ║
║  │                                                                                                                        │ ║
║  │ ☐ [MangaPlus] Capítulo 1087 (17 imagens)                                                                             │ ║
║  │    📁 MangaPlus/One Piece/Capítulo 1087                                                                              │ ║
║  │                                                                                                                        │ ║
║  │ ... (mais 1086 capítulos - scroll infinito)                                                                          │ ║
║  │                                                                                                                        │ ║
║  │ [🔍 Filtrar por nome: ___________] [🔢 Ir para capítulo: ___]                                                         │ ║
║  │                                                                                                                        │ ║
║  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘ ║
║                                                                                                                              ║
║  ┌─ SELEÇÃO PARA UPLOAD ──────────────────────────────────────────────────────────────────────────────────────────────────┐ ║
║  │                                                                                                                        │ ║
║  │ 🎯 3 capítulos selecionados (53 imagens) - Estimativa: ~12MB                                                         │ ║
║  │                                                                                                                        │ ║
║  │ • [MangaPlus] One Piece - Capítulo 1090 (15 imgs)                                                                    │ ║
║  │ • [MangaPlus] One Piece - Capítulo 1089 (18 imgs)                                                                    │ ║
║  │ • [MangaPlus] One Piece - Capítulo 1088 (20 imgs)                                                                    │ ║
║  │                                                                                                                        │ ║
║  │ ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐ │ ║
║  │ │                            🚀 UPLOAD COM METADADOS (3 capítulos)                                                 │ │ ║
║  │ └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘ │ ║
║  │                                                                                                                        │ ║
║  │ ┌────────────────────────────────────────────┐ ┌────────────────────────────────────────────────────────────────┐ │ ║
║  │ │              📝 EDITAR METADADOS           │ │                    ⚡ SALVAR NO GITHUB                         │ │ ║
║  │ └────────────────────────────────────────────┘ └────────────────────────────────────────────────────────────────┘ │ ║
║  │                                                                                                                        │ ║
║  │ ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐ │ ║
║  │ │                                      🗑️ LIMPAR SELEÇÃO                                                           │ │ ║
║  │ └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘ │ ║
║  │                                                                                                                        │ ║
║  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘ ║
║                                                                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
```

### **Funcionalidades Batch Disponíveis:**

#### **🔄 Seleção em Massa:**
- **☑️ Selecionar Todos** - Marca todos os capítulos visíveis
- **☐ Desmarcar Todos** - Remove todas as seleções
- **📋 Últimos 10/50** - Seleciona os N capítulos mais recentes
- **📋 Range** - Seleciona capítulos entre dois números específicos

#### **⬆️⬇️ Ordenação:**
- **📈 Crescente** - Capítulos do 1 ao último (1→1090)
- **📉 Decrescente** - Capítulos do último ao 1 (1090→1)
- **📅 Por Data** - Baseado na data de modificação do arquivo
- **📝 Por Nome** - Ordem alfabética dos nomes
- **📊 Por Tamanho** - Baseado no número de imagens

#### **🔍 Busca e Navegação:**
- **Filtrar por nome** - Busca textual nos nomes dos capítulos
- **Ir para capítulo** - Navegação rápida para capítulo específico
- **Scroll infinito** - Carrega capítulos conforme necessário

### **4 Botões de Ação Disponíveis:**

#### **🚀 Upload com Metadados (Principal):**
- Botão principal laranja/azul
- Abre dialog para preencher metadados do manga
- Faz upload das imagens + gera arquivo JSON
- Disponível quando há capítulos selecionados

#### **📝 Editar Metadados:**
- Botão amarelo/warning
- Edita metadados existentes do manga
- Carrega dados salvos anteriormente
- Atualiza informações sem fazer novo upload

#### **⚡ Salvar no GitHub:**
- Botão verde/success
- Envia metadados JSON para repositório GitHub
- Só aparece se configuração GitHub estiver preenchida
- Backup automático dos metadados

#### **🗑️ Limpar Seleção:**
- Botão neutro/secondary
- Remove todas as seleções de capítulos
- Reset rápido para começar nova seleção
- Sempre disponível

### **UX Flow Típico:**
```
1. Usuário seleciona "One Piece" → 1090 capítulos carregam
2. Click "📉 Decrescente" → Capítulos mais novos aparecem primeiro
3. Click "📋 Últimos 50" → Seleciona automaticamente 50 mais recentes
4. Ajusta seleção manual conforme necessário
5. Click "🚀 UPLOAD COM METADADOS" → Abre dialog de metadados
6. Preenche dados do manga → Confirma upload em batch
7. [Opcional] Click "⚡ SALVAR NO GITHUB" → Backup dos metadados
```

## Implementação 🔧

### **1. Backend Changes:**

#### **Remover Código Desnecessário:**
- [ ] Deletar métodos `_scan_scan_manga_*` de `models/__init__.py`
- [ ] Remover `folder_structure` de `config.py`
- [ ] Limpar propriedades de estrutura do `backend.py`

#### **Implementar Detecção Universal:**
- [ ] Criar `_scan_recursive()` em `models/__init__.py`
- [ ] Implementar `_has_manga_images()` helper
- [ ] Atualizar `_scan_chapters()` para usar detecção automática

#### **Implementar Funcionalidades Batch:**
- [ ] Adicionar métodos de ordenação em `Manga` class:
  ```python
  def sort_chapters(self, order: str = "asc", by: str = "number"):
      if by == "number":
          self.chapters.sort(key=lambda c: c.number or 0, reverse=(order == "desc"))
      elif by == "name":
          self.chapters.sort(key=lambda c: c.name, reverse=(order == "desc"))
      elif by == "size":
          self.chapters.sort(key=lambda c: len(c.images), reverse=(order == "desc"))
      elif by == "date":
          self.chapters.sort(key=lambda c: c.path.stat().st_mtime, reverse=(order == "desc"))
  ```

- [ ] Implementar seleção batch no `backend.py`:
  ```python
  @Slot()
  def selectAllChapters(self):
      if self.chapter_model:
          self.chapter_model.selectAll()
  
  @Slot()
  def deselectAllChapters(self):
      if self.chapter_model:
          self.chapter_model.deselectAll()
  
  @Slot(int)
  def selectLastN(self, n: int):
      if self.chapter_model:
          self.chapter_model.selectLast(n)
  
  @Slot(int, int)
  def selectRange(self, start: int, end: int):
      if self.chapter_model:
          self.chapter_model.selectRange(start, end)
  
  @Slot(str)
  def sortChapters(self, criteria: str):
      # criteria format: "number_desc", "name_asc", "size_desc", etc.
      if self._current_manga:
          by, order = criteria.split('_')
          self._current_manga.sort_chapters(order, by)
          self._update_chapter_list_from_current_manga()
  
  @Slot(str)
  def filterChapters(self, filter_text: str):
      if self.chapter_model:
          self.chapter_model.setFilterText(filter_text)
  ```

#### **Melhorar Nomes de Capítulos:**
- [ ] Preservar hierarquia nas nomenclaturas (ex: "Scan/Manga/Cap 1")
- [ ] Detectar volumes automaticamente
- [ ] Manter compatibilidade com estruturas simples
- [ ] Adicionar parsing de números de capítulos para ordenação correta

### **2. Frontend Changes (Mínimas):**

#### **Manter Interface Atual:**
- [ ] ✅ **Não mudar** layout geral
- [ ] ✅ **Não mudar** sidebar de mangás
- [ ] ✅ **Não mudar** área principal

#### **Adicionar Controles Batch:**
- [ ] Barra de controles de seleção acima da lista de capítulos:
  ```qml
  RowLayout {
      spacing: 8
      
      Button {
          text: "☑️ Todos"
          onClicked: backend.selectAllChapters()
      }
      
      Button {
          text: "☐ Nenhum"  
          onClicked: backend.deselectAllChapters()
      }
      
      Button {
          text: "📋 Últimos 10"
          onClicked: backend.selectLastN(10)
      }
      
      Button {
          text: "📋 Últimos 50"
          onClicked: backend.selectLastN(50)
      }
      
      TextField {
          id: rangeStart
          placeholderText: "De"
          width: 60
      }
      
      TextField {
          id: rangeEnd  
          placeholderText: "Até"
          width: 60
      }
      
      Button {
          text: "📋 Range"
          onClicked: backend.selectRange(rangeStart.text, rangeEnd.text)
      }
  }
  ```

- [ ] Barra de ordenação:
  ```qml
  RowLayout {
      spacing: 8
      
      Button {
          text: "📈 1→1090"
          onClicked: backend.sortChapters("number_asc")
      }
      
      Button {
          text: "📉 1090→1"
          onClicked: backend.sortChapters("number_desc")
      }
      
      Button {
          text: "📅 Data"
          onClicked: backend.sortChapters("date_desc")
      }
      
      Button {
          text: "📝 Nome"
          onClicked: backend.sortChapters("name_asc") 
      }
      
      Button {
          text: "📊 Tamanho"
          onClicked: backend.sortChapters("size_desc")
      }
  }
  ```

- [ ] Campo de filtro e navegação:
  ```qml
  RowLayout {
      TextField {
          Layout.fillWidth: true
          placeholderText: "🔍 Filtrar por nome..."
          onTextChanged: backend.filterChapters(text)
      }
      
      TextField {
          placeholderText: "🔢 Ir para cap..."
          width: 100
      }
  }
  ```

#### **Melhorar Apenas:**
- [ ] Lista de capítulos mostra hierarquia detectada
- [ ] Tooltips explicam estrutura detectada
- [ ] Loading states durante detecção
- [ ] Contador dinâmico de seleções
- [ ] Scroll infinito para listas grandes
- [ ] Estimativa de tamanho total de upload

### **3. Testing:**

#### **Estruturas para Testar:**
- [ ] `Manga/Capítulo/` (atual)
- [ ] `Scan/NomeScan/Manga/Capítulo/`
- [ ] `Manga/Volume/Capítulo/`
- [ ] `Manga/imagens_diretas/`
- [ ] Estruturas mistas
- [ ] Pastas vazias/inválidas

## Comportamento Dinâmico da Aplicação 🔄

### **Estados dos Elementos de Batch:**

#### **Controles de Seleção:**
```
┌─ Estado: Nenhum manga selecionado ─┐
│ [ ] Tudo                (disabled)  │
│ [ ] Inverter            (disabled)  │  
│ [ ] Últimos N           (disabled)  │
│ [Limpar Seleção]        (disabled)  │
└─────────────────────────────────────┘

┌─ Estado: Manga sem capítulos ──────┐
│ [ ] Tudo                (disabled)  │
│ [ ] Inverter            (disabled)  │
│ [ ] Últimos N           (disabled)  │
│ [Limpar Seleção]        (disabled)  │
└─────────────────────────────────────┘

┌─ Estado: Capítulos disponíveis ────┐
│ [✓] Tudo                (enabled)   │
│ [✓] Inverter            (enabled)   │
│ [✓] Últimos N           (enabled)   │
│ [Limpar Seleção]        (enabled)   │
└─────────────────────────────────────┘
```

#### **Botões de Ordenação:**
```
┌─ Estados dos Botões de Sort ───────┐
│ Nenhum capítulo:                   │
│ [📈 1→1090]            (disabled)  │
│ [📉 1090→1]            (disabled)  │
│ [📅 Data]              (disabled)  │
│ [📝 Nome]              (disabled)  │
│ [📊 Tamanho]           (disabled)  │
│                                    │
│ Com capítulos:                     │
│ [📈 1→1090]            (enabled)   │
│ [📉 1090→1]            (enabled)   │
│ [📅 Data]              (enabled)   │
│ [📝 Nome]              (enabled)   │
│ [📊 Tamanho]           (enabled)   │
│                                    │
│ Ordenação ativa:                   │
│ [📈 1→1090]            (pressed)   │ <- visual feedback
│ [📉 1090→1]            (normal)    │
│ [📅 Data]              (normal)    │
│ [📝 Nome]              (normal)    │
│ [📊 Tamanho]           (normal)    │
└────────────────────────────────────┘
```

#### **Campos de Filtro:**
```
┌─ Campo de Filtro por Nome ─────────┐
│ Sem capítulos:                     │
│ [🔍 Filtrar por nome...] (disabled)│
│                                    │
│ Com capítulos:                     │  
│ [🔍 Filtrar por nome...] (enabled) │
│                                    │
│ Filtrando ativamente:              │
│ [🔍 Naruto] [❌]         (active)  │ <- botão limpar
│ "12 de 450 capítulos"              │ <- contador
└────────────────────────────────────┘

┌─ Campo Ir Para Capítulo ───────────┐
│ Sem capítulos numerados:           │
│ [🔢 Ir para cap...] → (disabled)   │
│                                    │
│ Com capítulos numerados:           │
│ [🔢 Ir para cap...] → (enabled)    │
│                                    │
│ Navegação inválida:                │
│ [🔢 999] → (error state)           │ <- borda vermelha
│ "Cap. não encontrado"              │ <- tooltip erro
└────────────────────────────────────┘
```

#### **Contadores Dinâmicos:**
```
┌─ Informações de Estado ────────────┐
│ Nenhuma seleção:                   │
│ "0 capítulos selecionados"         │
│ "Tamanho estimado: 0 MB"           │
│                                    │
│ Seleção parcial:                   │
│ "25 de 450 capítulos selecionados" │
│ "Tamanho estimado: 1.2 GB"        │
│                                    │
│ Tudo selecionado:                  │
│ "450 capítulos selecionados"       │
│ "Tamanho estimado: 12.8 GB"       │
│                                    │
│ Com filtro ativo:                  │
│ "12 de 25 filtrados selecionados"  │
│ "Tamanho estimado: 340 MB"        │
└────────────────────────────────────┘
```

#### **Lista de Capítulos:**
```
┌─ Estados da Lista ─────────────────┐
│ Carregando estrutura:              │
│ [🔄 Detectando estrutura...]       │
│                                    │
│ Estrutura detectada:               │
│ [ℹ️ Scan/NomeScan/Manga/Cap]       │ <- tooltip
│                                    │
│ Lista vazia:                       │
│ [📁 Nenhum capítulo encontrado]    │
│                                    │
│ Lista com dados:                   │
│ [✓] Cap. 001 - Início    [1.2MB]   │ <- checkbox dinâmico
│ [ ] Cap. 002 - Aventura  [1.8MB]   │
│ [✓] Cap. 003 - Batalha   [2.1MB]   │
│                                    │
│ Scroll infinito:                   │
│ [Cap 1-50 carregados]              │
│ [🔄 Carregando mais...]            │ <- ao fazer scroll
└────────────────────────────────────┘
```

### **Transições de Estado:**

#### **Fluxo Típico de Uso:**
```
1. Aplicação inicia
   ↓
2. [Estado inicial] - Todos controles disabled
   ↓
3. Usuário seleciona pasta raiz
   ↓
4. [Carregando] - Detectando estrutura...
   ↓
5. [Estrutura detectada] - Controles enabled
   ↓
6. Usuário seleciona manga
   ↓
7. [Capítulos carregados] - Batch controles enabled
   ↓
8. Usuário faz seleções/filtros
   ↓
9. [Estado ativo] - Contadores atualizados
   ↓
10. Pronto para upload
```

#### **Estados de Erro:**
```
┌─ Tratamento de Erros ──────────────┐
│ Pasta inválida:                    │
│ [⚠️ Pasta não encontrada]          │
│ → Todos controles disabled         │
│                                    │
│ Sem permissão:                     │
│ [🔒 Acesso negado]                 │
│ → Botão "Escolher outra pasta"     │
│                                    │
│ Estrutura não suportada:           │
│ [❓ Estrutura não reconhecida]     │
│ → Fallback para detecção manual    │
│                                    │
│ Falha na detecção:                 │
│ [🔄 Tentar novamente]              │
│ → Botão retry                      │
└────────────────────────────────────┘
```

## Benefícios da Abordagem ✅

### **Para o Usuário:**
- **Zero configuração** - funciona automaticamente
- **Interface familiar** - nada muda visualmente
- **Máxima compatibilidade** - qualquer organização funciona
- **Feedback visual** - estados claros em tempo real

### **Para o Código:**
- **Menos complexidade** - uma lógica ao invés de 5
- **Mais robusto** - detecta automaticamente
- **Fácil manutenção** - código mais limpo
- **Estados bem definidos** - comportamento previsível

### **Para UX:**
- **Sem confusão** - não precisa escolher estrutura
- **Funciona imediatamente** - sem configuração
- **Visual familiar** - interface não muda
- **Responsivo** - feedback imediato nas ações

## Arquivos Envolvidos

### **Modificações:**
- `src/core/models/__init__.py` - Detecção automática
- `src/core/config.py` - Remover folder_structure  
- `src/ui/backend.py` - Limpar propriedades antigas

### **Não Modificar:**
- `src/ui/qml/main.qml` - Interface mantida
- Layout geral permanece igual
- Fluxo de navegação atual preservado

## Resultado Final

**Interface igual + funcionalidade melhor:**
- Usuário abre pasta raiz normalmente
- App detecta automaticamente todas as estruturas
- Lista de mangás aparece como sempre
- Capítulos detectados independente da organização
- Upload funciona normalmente

**Zero mudança visual, máxima compatibilidade!**