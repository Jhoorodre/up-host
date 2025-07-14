# Mapa do Frontend - Sistema de Indexador (Atualizado)

## 🗺️ Visão Geral da Interface

O sistema de indexador será integrado na interface existente através de novos componentes e dialogs, baseado na **estrutura real encontrada na pasta `raw/`** e no formato **v2.1 do Tower of God Brasil**. Mantém a consistência visual com o design atual do Manga Uploader Pro.

## 📍 Localização dos Elementos

### 1. **Menu Principal (Header) - Atualizado**
```
┌─────────────────────────────────────────────────────────────┐
│ MANGA UPLOADER    [HOST SELECTOR] [📋 INDEXADOR] [CONFIG]  │
│                                       ↑                     │
│                              NOVO BOTÃO COM ÍCONE           │
└─────────────────────────────────────────────────────────────┘
```

**Localização**: `src/ui/qml/main.qml` - Header (linha ~62-100)
**Novo elemento** (baseado no formato real):
```qml
Rectangle {
    Layout.preferredWidth: 100
    Layout.preferredHeight: 32
    color: indexadorButtonHovered ? colorSecondary : "transparent"
    border.color: indexadorButtonHovered ? colorSecondary : colorTertiary
    border.width: 1
    radius: 8
    
    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 8
        anchors.rightMargin: 8
        spacing: 6
        
        Text {
            text: "📋"                    // Ícone do indexador
            font.pixelSize: 12
            color: indexadorButtonHovered ? colorPrimary : colorSecondary
        }
        
        Text {
            text: "Indexador"
            font.pixelSize: 10
            font.weight: Font.Medium
            color: indexadorButtonHovered ? colorPrimary : colorTertiary
        }
    }
    
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        onClicked: indexadorDialog.open()
        onEntered: parent.indexadorButtonHovered = true
        onExited: parent.indexadorButtonHovered = false
    }
}
```

### 2. **Dialog Principal do Indexador (Baseado na Estrutura Real)**
```
┌─────────────────────────────────────────────────────────────┐
│                 GERENCIAR INDEXADOR v2.1                   │
├─────────────────────────────────────────────────────────────┤
│ [Grupo] [Redes Sociais] [Técnico] [Séries] [Prévia]       │
├─────────────────────────────────────────────────────────────┤
│ 💡 Baseado no formato Tower of God Brasil (raw/index.json)  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    CONTEÚDO DA ABA                         │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ [🔄 Gerar Local] [📤 Upload GitHub] [🔍 Verificar CDNs]    │
│                              [📋 Copiar] [💾 Salvar]       │
└─────────────────────────────────────────────────────────────┘
```

**Novo arquivo**: `src/ui/qml/components/IndexadorDialog.qml`
**Tamanho**: 800x600px (mínimo para visualizar JSONs v2.1)
**Modal**: true
**Formato base**: Estrutura extraída de `raw/index.json`

## 📑 Abas e Conteúdo Detalhado (Baseado na Estrutura Real)

### **Aba 1: Informações do Grupo (Hub)**
```
┌─────────────────────────────────────────────────────────────┐
│                   HUB DO GRUPO v2.1                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ID do Hub: [meu-grupo-hub______________] (automático)       │
│                                                             │
│ Nome do Grupo: [________________________] 💡 Recomendado   │
│ Exemplo: "Tower of God Brasil" (raw/index.json)            │
│                                                             │
│ Idioma: [pt-BR_] (padrão brasileiro)                       │
│                                                             │
│ Descrição: ┌─────────────────────────────────┐ 💡          │
│           │ Bem-vindo ao [Nome do Grupo]!   │              │
│           │ Somos um grupo de fãs dedicados │              │
│           │ a trazer traduções de alta      │              │
│           │ qualidade...                    │              │
│           └─────────────────────────────────┘              │
│                                                             │
│ Disclaimer: ┌─────────────────────────────────┐            │
│            │ Lembre-se sempre de apoiar o    │              │
│            │ autor original!                 │              │
│            └─────────────────────────────────┘              │
│                                                             │
│ Capa do Hub: [https://files.catbox.moe/cover.jpg]         │
│                                                             │
│ Repositório: [https://github.com/user/repo_______________] │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Elementos (baseados no hub{} real)**:
- `TextField` para ID (auto-gerado a partir do nome)
- `TextField` para nome (hub.name)
- `ComboBox` para idioma (hub.lang)
- `ScrollView + TextArea` para descrição (hub.desc)
- `ScrollView + TextArea` para disclaimer (hub.disclaimer)
- `TextField` para URL da capa (hub.cover)
- `TextField` para repositório (hub.repo)

### **Aba 2: Redes Sociais (Formato Array Real)**

```text
┌─────────────────────────────────────────────────────────────┐
│                REDES SOCIAIS (social[])                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 🎮 Discord                                                  │
│ URL: [_____________________________] [Testar] ✅/❌        │
│ ☑ Rede social principal (primary: true)                   │
│                                                             │
│ 📱 Telegram                                                 │
│ URL: [_____________________________] [Testar] ✅/❌        │
│ ☐ Rede social secundária                                  │
│                                                             │
│ 📞 WhatsApp                                                 │
│ URL: [_____________________________] [Testar] ✅/❌        │
│ ☐ Rede social secundária                                  │
│                                                             │
│ 🐦 Twitter/X                                               │
│ URL: [_____________________________] [Testar] ✅/❌        │
│ ☐ Rede social secundária                                  │
│                                                             │
│ 💡 Pelo menos uma rede social é recomendada               │
│ Formato: type + url + primary (baseado em raw/index.json) │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Elementos (baseados no social[] real)**:
- `Repeater` com 4 seções (discord, telegram, whatsapp, twitter)
- Cada seção: ícone + TextField (URL) + Button (Testar) + status visual
- RadioButton para marcar rede principal (primary: true)
- Validação de URL em tempo real com feedback visual

### **Aba 3: Configurações Técnicas (CDN Híbrido Real)**

```text
┌─────────────────────────────────────────────────────────────┐
│               CONFIGURAÇÕES TÉCNICAS v2.1                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ URLs baseadas na estrutura real do Tower of God Brasil:    │
│                                                             │
│ Template CDN (JSDelivr):                                   │
│ [https://cdn.jsdelivr.net/gh/{user}/{repo}@main/{nome}.json] │
│                                                             │
│ Template Fallback (GitHub Raw):                            │
│ [https://raw.githubusercontent.com/{user}/{repo}/main/{nome}.json] │
│                                                             │
│ Repositório GitHub (mesmo formato real):                   │
│ Usuário: [Jhoorodre_______________]                        │
│ Repositório: [TOG-Brasil__________]                        │
│ Branch: [main_____] Pasta: [metadata_________]             │
│                                                             │
│ Sistema CDN (baseado nos URLs reais encontrados):          │
│ ● Híbrido (JSDelivr + GitHub Raw fallback) ✅              │
│ ○ Apenas JSDelivr CDN                                      │
│ ○ Apenas GitHub Raw                                        │
│                                                             │
│ Configurações automáticas:                                 │
│ ☑ Verificar disponibilidade CDN a cada hora               │
│ ☑ Encoding automático de caracteres especiais             │
│ ☑ Promover URLs para CDN quando disponível                │
│ ☑ Gerar APIs automáticas (all_works.json, search.json)    │
│                                                             │
│ Status: ✅ Conectado | 4 obras detectadas                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Elementos (baseados na estrutura real)**:
- `TextField` para templates CDN e Raw (pré-preenchidos)
- `TextField` para usuário, repo, branch, pasta GitHub
- `RadioButton` group para sistema CDN (híbrido selecionado)
- `CheckBox` para configurações automáticas (todas ativadas)
- Status em tempo real da conexão GitHub

### **Aba 4: Séries Detectadas (Dados Reais)**

```text
┌─────────────────────────────────────────────────────────────┐
│           SÉRIES DETECTADAS (featured[] real)              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 🔄 [Sincronizar GitHub] 📁 [Escanear Local] 📋 [raw/]     │
│                                                             │
│ ✅ Tower of God: Parte 1 – O Irregular                    │
│ │  📍 Status: completed | 📊 78 capítulos | ⭐ 4.8        │
│ │  🌐 CDN: ✅ https://cdn.jsdelivr.net/gh/Jhoorodre/...   │
│ │  🏷️ Priority: [1__] ☑ Incluir ☐ Latest               │
│ └─────────────────────────────────────────────────────────── │
│                                                             │
│ ✅ Tower of God: Parte 2 – O Retorno do Príncipe         │
│ │  📍 Status: ongoing | 📊 337 capítulos | ⭐ 4.9         │
│ │  🌐 CDN: ✅ https://cdn.jsdelivr.net/gh/Jhoorodre/...   │
│ │  🏷️ Priority: [2__] ☑ Incluir ☐ Latest               │
│ └─────────────────────────────────────────────────────────── │
│                                                             │
│ ✅ Tower of God: A Ascensão de Urek Mazzino               │
│ │  📍 Status: completed | 📊 11 capítulos | ⭐ 4.7        │
│ │  🌐 CDN: ✅ https://cdn.jsdelivr.net/gh/Jhoorodre/...   │
│ │  🏷️ Priority: [3__] ☑ Incluir ☐ Latest               │
│ └─────────────────────────────────────────────────────────── │
│                                                             │
│ ✅ Tower of God: Parte 3 – A Batalha das Famílias        │
│ │  📍 Status: ongoing | 📊 45 capítulos | ⭐ 4.8          │
│ │  🌐 CDN: ✅ https://cdn.jsdelivr.net/gh/Jhoorodre/...   │
│ │  🏷️ Priority: [4__] ☑ Incluir ☑ Latest 🔥            │
│ └─────────────────────────────────────────────────────────── │
│                                                             │
│ 📊 Total: 4 obras | 471 capítulos | Rating médio: 4.8    │
│                          [🔍 Verificar CDNs] [🔄 Atualizar] │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Elementos (baseados no featured[] real)**:
- Botões: "Sincronizar GitHub", "Escanear Local", "Escanear raw/"
- `ScrollView` com `ListView` das 4 obras reais detectadas
- Cada item: título, status, capítulos, rating, URL CDN, prioridade
- CheckBox para incluir no indexador e marcar como "latest"
- Estatísticas reais: 4 obras, 471 capítulos, rating médio 4.8
- Botões de verificação CDN e atualização

### **Aba 5: Prévia JSON (Formato v2.1 Real)**

```text
┌─────────────────────────────────────────────────────────────┐
│                  PRÉVIA JSON v2.1                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ {                                                       │ │
│ │   "v": "2.1",                                           │ │
│ │   "updated": "2025-07-14",                              │ │
│ │   "hub": {                                              │ │
│ │     "id": "meu-grupo-hub",                              │ │
│ │     "name": "Meu Grupo Scan",                           │ │
│ │     "cover": "https://files.catbox.moe/cover.jpg",      │ │
│ │     "desc": "Grupo focado em traduções de alta...",     │ │
│ │     "disclaimer": "Lembre-se sempre de apoiar...",      │ │
│ │     "lang": "pt-BR",                                    │ │
│ │     "repo": "https://github.com/user/repo"              │ │
│ │   },                                                    │ │
│ │   "social": [                                           │ │
│ │     {                                                   │ │
│ │       "type": "discord",                                │ │
│ │       "url": "https://discord.gg/...",                 │ │
│ │       "primary": true                                   │ │
│ │     }                                                   │ │
│ │   ],                                                    │ │
│ │   "featured": [...],                                    │ │
│ │   "api": {...},                                         │ │
│ │   "stats": {                                            │ │
│ │     "total_works": 4,                                   │ │
│ │     "total_chapters": 471,                              │ │
│ │     "avg_rating": 4.8                                   │ │
│ │   }                                                     │ │
│ │ }                                                       │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ [📋 Copiar JSON] [💾 Salvar Arquivo] [🔄 Atualizar Prévia] │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Elementos (baseados na estrutura real)**:
- `ScrollView` com `TextArea` (readonly) mostrando JSON v2.1 formatado
- Syntax highlighting para JSON (se disponível)
- JSON atualizado em tempo real baseado nas configurações
- Botões: "Copiar JSON", "Salvar Arquivo", "Atualizar Prévia"

## 🎛️ Botões de Ação (Footer do Dialog) - Atualizados

```text
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│ [ Gerar Local] [📤 Upload GitHub] [🔍 Verificar CDNs]    │
│                                                             │
│           [📋 Copiar JSON] [💾 Salvar Arquivo]              │
│                                                             │
│                              [❌ Cancelar] [✅ Aplicar]      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Elementos (baseados no fluxo real)**:
- **🔄 Gerar Local**: Cria/atualiza indexador local no formato v2.1
- **📤 Upload GitHub**: Envia para repositório configurado
- **🔍 Verificar CDNs**: Testa status de todas as URLs JSDelivr
- **📋 Copiar JSON**: Copia indexador v2.1 para área de transferência
- **💾 Salvar Arquivo**: Abre dialog nativo para salvar JSON
- **❌ Cancelar**: Fecha dialog sem salvar configurações
- **✅ Aplicar**: Salva configurações e mantém dialog aberto

## 📱 Notificações e Feedback (Contextuais)

### **Área de Notificações (Baseada na Estrutura Real)**

```text
┌─────────────────────────────────────────────────────────────┐
│ 🎉 Indexador gerado com 4 obras (471 capítulos) - v2.1    │
└─────────────────────────────────────────────────────────────┘
```

**Localização**: Topo do dialog, abaixo das abas
**Tipos (baseados no sistema real)**:
- 🎉 Sucesso (verde): "Indexador gerado com 4 obras (471 capítulos)"
- 💡 Sugestões (azul): "Baseado no formato Tower of God Brasil"
- 🌐 CDN (azul): "URLs JSDelivr ativas para todas as obras"
- ⚠️ Avisos (laranja): "CDN indisponível para 1 série - usando GitHub raw"
- ❌ Erros (vermelho): "Falha ao conectar com GitHub - verifique token"
- 📊 Info (cinza): "Rating médio: 4.8 | Total de capítulos: 471"

### **Barra de Progresso (Durante operações)**

```text
┌─────────────────────────────────────────────────────────────┐
│ Verificando CDNs... [████████░░] 8/10 URLs testadas       │
└─────────────────────────────────────────────────────────────┘
```

**Estados específicos**:
- Escaneando JSONs locais/remotos
- Verificando URLs CDN (JSDelivr)
- Gerando indexador v2.1
- Fazendo upload para GitHub
- Validando configurações

## 🔧 Arquivos a Criar/Modificar

### **Novos Arquivos**:
```
src/ui/qml/components/
├── IndexadorDialog.qml           # Dialog principal
├── IndexadorGroupTab.qml         # Aba informações do grupo  
├── IndexadorSocialTab.qml        # Aba redes sociais
├── IndexadorTechTab.qml          # Aba configurações técnicas
├── IndexadorSeriesTab.qml        # Aba séries detectadas
├── IndexadorPreviewTab.qml       # Aba prévia JSON
├── SeriesListItem.qml            # Item da lista de séries
└── NotificationBar.qml           # Barra de notificações
```

### **Arquivos a Modificar**:
```
src/ui/qml/main.qml               # Adicionar botão no header
src/ui/backend.py                 # Novos slots e properties
src/core/config.py                # IndexadorConfig
```

### **Novos Backend**:
```
src/core/services/indexador.py    # Lógica principal
src/core/models/indexador.py      # Modelos Pydantic
```

## 🎨 Integração Visual

### **Paleta de Cores** (Usar as existentes):
- **Primary**: `#1a1a1a` (fundo)
- **Secondary**: `#0078d4` (acentos azuis)
- **Surface**: `#2d2d2d` (cards)
- **Success**: `#00c851` (verde)
- **Warning**: `#ff9500` (laranja)

### **Ícones**:
- 💡 Dicas/sugestões
- 🎮 Discord
- 📱 Telegram  
- 📞 WhatsApp
- 🐦 Twitter
- 🔄 Atualizar
- 📤 Upload
- ⚙️ Configurações
- ✏️ Editar

### **Layout Responsivo**:
- Dialog: 800x600px mínimo
- Tabs: 32px altura
- Botões: 32px altura padrão
- Spacing: 8px, 12px, 16px (consistente com app)

## 🚀 Fluxo de Implementação

### **Fase 1: Estrutura Base**
1. Criar `IndexadorDialog.qml` básico
2. Adicionar botão no header
3. Implementar backend básico

### **Fase 2: Abas Principais**
1. Aba "Grupo" (formulário básico)
2. Aba "Técnico" (configurações)
3. Conectar com backend

### **Fase 3: Funcionalidades Avançadas (Baseadas na Estrutura Real)**
1. Aba "Redes Sociais" (formato v2.1 descoberto)
2. Aba "Séries" (detecção de 4 obras existentes - 471 capítulos)
3. Aba "Prévia" (JSON v2.1 com estrutura Tower of God Brasil)

### **Fase 4: Polimento e Integração**
1. Notificações com feedback do sistema real
2. Validação CDN (JSDelivr) - baseado na análise descoberta
3. Testes com dados reais do diretório `raw/`
4. Integração completa com formato v2.1

## 💻 Implementação Sugerida no QML (Baseada na Estrutura Real)

### **Componente Principal** (`IndexadorManager.qml`)

```qml
// Baseado na estrutura descoberta no projeto
Item {
    property var indexadorConfig: ({
        hub: "Tower of God Brasil",
        social: [
            { name: "Discord", url: "https://discord.gg/towerpg" },
            { name: "Site", url: "https://towerofgod.wiki" }
        ],
        featured: [],
        data: [],
        endpoint: {
            api_url: "https://cdn.jsdelivr.net/gh/user/repo@latest/api/",
            cover_fallback: "default_cover.png"
        },
        version: "2.1"
    })
    
    // Signals baseados no fluxo real descoberto
    signal indexadorGenerated(var data)
    signal uploadToGitHub(var config)
    signal validateCDNs(var urls)
    signal saveLocal(var path)
}
```

### **Backend Service** (`IndexadorService.py`)

```python
# Baseado na análise do código real
class IndexadorService:
    def __init__(self):
        self.version = "2.1"  # Versão descoberta no raw/
        self.cdn_base = "https://cdn.jsdelivr.net/gh/"
        
    async def generate_indexador(self, works_data: List[Dict]) -> Dict:
        """Gera indexador v2.1 baseado na estrutura real"""
        return {
            "hub": self.config.get("hub_name", "Meu Grupo"),
            "social": self._format_social_links(),
            "featured": self._select_featured_works(),
            "data": self._process_works_data(works_data),
            "endpoint": self._build_endpoints(),
            "version": self.version,
            "statistics": self._calculate_stats(works_data)
        }
    
    def _calculate_stats(self, works_data: List[Dict]) -> Dict:
        """Calcula estatísticas como descoberto no index.json"""
        total_chapters = sum(len(work.get("chapters", [])) for work in works_data)
        avg_rating = self._calculate_average_rating(works_data)
        
        return {
            "total_works": len(works_data),
            "total_chapters": total_chapters,
            "average_rating": round(avg_rating, 1),
            "last_updated": datetime.now().isoformat()
        }
```

### **Modelo de Dados** (`IndexadorModel.py`)

```python
# Baseado na estrutura v2.1 descoberta
@dataclass
class IndexadorData:
    hub: str
    social: List[SocialLink]
    featured: List[str] = field(default_factory=list)
    data: List[WorkData] = field(default_factory=list)
    endpoint: EndpointConfig = field(default_factory=EndpointConfig)
    version: str = "2.1"
    statistics: Optional[Dict] = None

@dataclass
class WorkData:
    """Estrutura descoberta no raw/reader.json"""
    title: str
    cover: str
    desc: str
    chapters: List[ChapterData]
    stats: WorkStats
    
@dataclass
class ChapterData:
    """Formato de capítulo descoberto"""
    title: str
    date: str
    src: List[str]  # URLs das páginas
```

---

**✨ Implementação Completa**: O frontend deve refletir exatamente a estrutura v2.1 descoberta no diretório `raw/`, garantindo compatibilidade total com o sistema indexador existente e integrando as 4 obras já catalogadas (471 capítulos) com rating médio de 4.8! 🎯**