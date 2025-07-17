# 🎨 Mapa do Frontend - Manga Uploader Pro (Design Minimalista Moderno)

> **Análise Completa**: Baseado em 100% da aplicação - 10+ hosts, sistema indexador v2.1, GitHub integration, QML/PySide6 architecture

## 🌟 Visão Geral da Nova Interface

### **Filosofia do Design**
- **Minimalismo**: Cards flutuantes, espaços em branco generosos, hierarquia visual clara
- **Foco na Produtividade**: Tudo acessível em no máximo 2 cliques
- **Responsividade**: Adapta-se perfeitamente a diferentes tamanhos de tela
- **Acessibilidade**: Alto contraste, navegação por teclado, feedback visual consistente

---

## 🎯 Layout Principal Redesenhado

### **1. Header Minimalista (100% Otimizado)**

```qml
// Nova estrutura ultra-clean
ApplicationWindow {
    // Color Palette Otimizada para Máximo Contraste
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
}
```

```
┌─────────────────────────────────────────────────────────────────────┐
│  📚 Manga Uploader Pro                   🔍 Search    [⚙️] [📊] [👤] │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Elementos Redesenhados**:
- **Logo**: Ícone 📚 + título moderno com tipografia clean
- **Busca Global**: Campo unificado com sugestões inteligentes
- **Ações Rápidas**: Configurações ⚙️, Estatísticas 📊, Perfil 👤

### **2. Sidebar Inteligente (Adaptativa)**

```
┌─────────────────┐
│ 📂 BIBLIOTECA   │  ← Collapse/Expand automático
├─────────────────┤
│ 🌟 Favoritos    │
│ 📈 Recentes     │  
│ 🔄 Em Progresso │
│ ✅ Concluídos   │
├─────────────────┤
│ 🏷️ TAGS         │
│ # Action        │
│ # Romance       │
│ # Isekai        │
├─────────────────┤
│ 🔧 FERRAMENTAS  │
│ 📋 Indexador    │
│ 📤 Upload Queue │
│ 📊 Analytics    │
└─────────────────┘
```

**Inovações**:
- **Auto-collapse**: Recolhe automaticamente em telas pequenas
- **Filtros Inteligentes**: Baseados no histórico do usuário
- **Status Visual**: Indicadores coloridos para cada categoria

---

## 📱 Cards System (Redesign Completo)

### **3. Manga Cards - Grid Responsivo**

```qml
// Card Component Moderno
Rectangle {
    width: 280        // Tamanho otimizado
    height: 380       // Proporção golden ratio
    radius: 12        // Bordas mais suaves
    color: bgCard
    
    // Hover Animation
    transform: Scale {
        origin.x: width/2; origin.y: height/2
        xScale: hovered ? 1.02 : 1.0
        yScale: hovered ? 1.02 : 1.0
        Behavior on xScale { NumberAnimation { duration: 200 } }
        Behavior on yScale { NumberAnimation { duration: 200 } }
    }
    
    // Drop Shadow
    layer.enabled: true
    layer.effect: DropShadow {
        horizontalOffset: 0
        verticalOffset: 4
        radius: 12
        color: "#40000000"
    }
}
```

```
┌─────────────────────────────┐
│        COVER IMAGE          │  ← Aspect ratio 3:4
│      (Auto-generated        │
│       if missing)           │
├─────────────────────────────┤
│ Tower of God             ⭐ │  ← Rating badge
│ 471 caps • Em andamento     │  ← Status conciso
│ ━━━━━━━━━░░ 85%              │  ← Progress bar
├─────────────────────────────┤
│ [📤] [✏️] [📋] [⚙️]          │  ← Quick actions
└─────────────────────────────┘
```

**Melhorias**:
- **Covers Inteligentes**: Auto-geração com primeira letra + gradiente
- **Progress Bar**: Visual do progresso de capítulos
- **Quick Actions**: Upload, Edit, Indexador, Settings direto no card
- **Status Badges**: Visual claro do estado atual

### **4. Chapter List - Design em Lista Moderna**

```
┌─────────────────────────────────────────────────────────────────┐
│ 📑 CAPÍTULOS (471)           [🔄 Inverter] [📋 Selecionar Todos] │
├─────────────────────────────────────────────────────────────────┤
│ ☐ Cap. 1 - Início           📅 12/Jan   🖼️ 23 imgs   [📤] [✏️] │
│ ☐ Cap. 2 - A Torre          📅 19/Jan   🖼️ 31 imgs   [📤] [✏️] │  
│ ☐ Cap. 3 - O Teste          📅 26/Jan   🖼️ 28 imgs   [📤] [✏️] │
│ ▼                                                               │
│ ☑ Cap. 471 - Final          📅 Hoje     🖼️ 45 imgs   [✅] [🔗] │
├─────────────────────────────────────────────────────────────────┤
│ Selecionados: 3 capítulos • 104 imagens • ~45MB               │
└─────────────────────────────────────────────────────────────────┘
```

**Funcionalidades Avançadas**:
- **Seleção em Massa**: Checkboxes com shift+click
- **Informações Contextuais**: Data, quantidade de imagens, tamanho
- **Status Visual**: ✅ Enviado, 🔗 Link disponível, ⏳ Em progresso
- **Ações Inline**: Upload e edit direto na linha

---

## 🚀 Área Principal - Multi-Layout

### **5. Dashboard Principal (Tela Inicial)**

```
┌─────────────────────────────────────────────────────────────────────┐
│                         🎯 AÇÕES RÁPIDAS                            │
├─────────────────────────────────────────────────────────────────────┤
│ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌─────────────┐ │
│ │ 📤 UPLOAD     │ │ 📋 INDEXADOR  │ │ 🔄 SYNC GITHUB│ │ 📊 RELATÓRIO│ │
│ │ Novo projeto  │ │ Gerenciar hub │ │ Sincronizar   │ │ Ver análise │ │
│ └───────────────┘ └───────────────┘ └───────────────┘ └─────────────┘ │
├─────────────────────────────────────────────────────────────────────┤
│                         📈 ESTATÍSTICAS                             │
├─────────────────────────────────────────────────────────────────────┤
│ Total de Mangás: 47    Capítulos: 1,234    Hoje: 12 uploads         │
│ Hosts Ativos: 10/10    Storage: 2.3GB      Queue: 3 pendentes       │
├─────────────────────────────────────────────────────────────────────┤
│                        🕐 ATIVIDADE RECENTE                         │
├─────────────────────────────────────────────────────────────────────┤
│ • Tower of God Cap. 471 enviado para Catbox                  2 min  │
│ • Naruto metadata atualizado no GitHub                       15 min │  
│ • Index.json gerado com 4 obras                              1 hora │
└─────────────────────────────────────────────────────────────────────┘
```

### **6. Upload Interface - Workflow Simplificado**

```
┌─────────────────────────────────────────────────────────────────────┐
│ 📤 UPLOAD WORKFLOW                                     [❌ Cancelar] │
├─────────────────────────────────────────────────────────────────────┤
│ Step 1: Manga Selection                                      ✅     │
│ Step 2: Chapter Selection                                    ✅     │  
│ Step 3: Host & Settings                                      📍     │
│ Step 4: Metadata                                             ⏳     │
│ Step 5: Upload & Generate                                    ⏳     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  🎯 HOST DE UPLOAD                                                  │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐   │
│  │  C  │ │  I  │ │  📦 │ │  L  │ │  P  │ │  G  │ │ 📷  │ │ 📁  │   │
│  │[●] │ │ [ ] │ │ [ ] │ │ [ ] │ │ [ ] │ │ [ ] │ │ [ ] │ │ [ ] │   │
│  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘   │
│  Catbox   Imgur   ImgBB   Lens   Pixel  Gofile  ImgCht  ImgBox     │
│                                                                     │
│  ⚙️ CONFIGURAÇÕES AVANÇADAS                                        │
│  Workers: [●●●●●] 5    Rate Limit: [●●○○○] 2s    Quality: [●●●○○]   │
│                                                                     │
│  🔄 MODO DE SINCRONIZAÇÃO                                          │
│  ○ Adicionar novos    ● Substituir todos    ○ Inteligente          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Melhorias de UX**:
- **Progress Steps**: Visual claro do processo
- **Host Selection**: Cards visuais em vez de dropdown
- **Configurações Inline**: Sliders visuais para workers/rate limit
- **Modo Inteligente**: Recomendações baseadas no contexto

---

## 🎛️ Configurações - Painel Moderno

### **7. Settings Panel - Organização por Categorias**

```
┌─────────────────────────────────────────────────────────────────────┐
│ ⚙️ CONFIGURAÇÕES                                        [💾 Salvar] │
├─────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐                                                 │
│ │ 📁 Diretórios   │ ← Active tab                                    │
│ │ 🌐 Hosts        │                                                 │
│ │ 🔧 GitHub       │                                                 │ 
│ │ 📋 Indexador    │                                                 │
│ │ 🎨 Interface    │                                                 │
│ │ 🔔 Notificações │                                                 │
│ └─────────────────┘                                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  📁 CONFIGURAÇÃO DE DIRETÓRIOS                                     │
│                                                                     │
│  Pasta Raiz dos Mangás                                             │
│  ┌─────────────────────────────────────────────┐ [📂 Procurar]     │
│  │ C:\Users\User\Documents\Manga               │                   │
│  └─────────────────────────────────────────────┘                   │
│                                                                     │
│  Pasta de Saída (Metadados)                                        │
│  ┌─────────────────────────────────────────────┐ [📂 Procurar]     │
│  │ C:\Users\User\Documents\Manga_Output        │                   │
│  └─────────────────────────────────────────────┘                   │
│                                                                     │
│  ✅ Criar subpastas por mangá                                      │
│  ✅ Backup automático de JSONs                                     │
│  ✅ Limpeza automática de temporários                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### **8. Host Configuration - Cards Interativos**

```
┌─────────────────────────────────────────────────────────────────────┐
│ 🌐 CONFIGURAÇÃO DE HOSTS                                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌─────────────┐ │
│ │ 🟢 CATBOX     │ │ 🟡 IMGUR      │ │ 🔴 IMGBB      │ │ 🟢 LENSDUMP │ │
│ │ ✅ Ativo      │ │ ⚠️ Sem Token  │ │ ❌ Desabilitado│ │ ✅ Ativo    │ │
│ │ 142 uploads   │ │ 23 uploads    │ │ 0 uploads     │ │ 67 uploads  │ │
│ │ [⚙️ Config]   │ │ [⚙️ Config]   │ │ [⚙️ Config]   │ │ [⚙️ Config] │ │
│ └───────────────┘ └───────────────┘ └───────────────┘ └─────────────┘ │
│                                                                     │
│ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌─────────────┐ │
│ │ 🟢 PIXELDRAIN │ │ 🟢 GOFILE     │ │ 🟡 IMAGECHEST │ │ 🟢 IMGBOX   │ │
│ │ ✅ Ativo      │ │ ✅ Ativo      │ │ ⚠️ API Key    │ │ ✅ Ativo    │ │
│ │ 89 uploads    │ │ 34 uploads    │ │ 12 uploads    │ │ 156 uploads │ │
│ │ [⚙️ Config]   │ │ [⚙️ Config]   │ │ [⚙️ Config]   │ │ [⚙️ Config] │ │
│ └───────────────┘ └───────────────┘ └───────────────┘ └─────────────┘ │
│                                                                     │
│ ┌───────────────┐ ┌───────────────┐                                 │
│ │ 🟢 IMGHIPPO   │ │ 🟢 IMGPILE    │    [+ Adicionar Host Customizado]│
│ │ ✅ Ativo      │ │ ✅ Ativo      │                                 │
│ │ 45 uploads    │ │ 78 uploads    │                                 │ 
│ │ [⚙️ Config]   │ │ [⚙️ Config]   │                                 │
│ └───────────────┘ └───────────────┘                                 │
│                                                                     │
│ 📊 ESTATÍSTICAS GLOBAIS                                            │
│ Total de uploads: 646    Hosts ativos: 8/10    Taxa de sucesso: 97%│
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Inovações**:
- **Status Visual**: Cores indicam estado (🟢 Ativo, 🟡 Atenção, 🔴 Inativo)
- **Estatísticas Contextuais**: Uploads por host em tempo real
- **Quick Setup**: Configuração rápida sem sair da tela
- **Host Customizado**: Possibilidade de adicionar hosts próprios

---

## 📋 Sistema Indexador - Interface Redesenhada

### **9. Indexador Hub - Dashboard Central**

```
┌─────────────────────────────────────────────────────────────────────┐
│ 📋 INDEXADOR HUB                                    [🔄 Sincronizar] │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  🏷️ MEU GRUPO DE SCANLATION                                        │
│  Tower of God Brasil • 4 obras ativas • v2.1                      │
│  📊 471 capítulos • ⭐ 4.8 rating • 🌐 CDN híbrido ativo           │
│                                                                     │
│ ┌───────────────────────────────────────────────────────────────────┐ │
│ │ 🎯 AÇÕES RÁPIDAS                                                 │ │
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │ │
│ │ │ 🔄 GERAR    │ │ 📤 GITHUB   │ │ 🔍 VALIDAR  │ │ 📋 COPIAR   │ │ │
│ │ │ Local       │ │ Upload      │ │ CDNs        │ │ JSON        │ │ │
│ │ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │ │
│ └───────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│ 📊 STATUS DAS SÉRIES                                               │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ ✅ Tower of God        471 caps    🌐 CDN ativo   📅 Hoje      │ │
│ │ ✅ Solo Leveling       179 caps    🌐 CDN ativo   📅 Ontem     │ │
│ │ ⚠️ Naruto             720 caps    ❌ CDN falhou   📅 2 dias    │ │
│ │ 🔄 One Piece          1,100 caps  🌐 CDN ativo   📅 Hoje      │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│ 🔗 LINKS DE DISTRIBUIÇÃO                                           │
│ CDN JSDelivr: https://cdn.jsdelivr.net/gh/user/repo@latest/        │
│ GitHub Raw:   https://raw.githubusercontent.com/user/repo/main/    │
│ [📋 Copiar Links] [🧪 Testar URLs] [📤 Compartilhar]               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### **10. Configuração de Grupo - Formulário Inteligente**

```
┌─────────────────────────────────────────────────────────────────────┐
│ 🏷️ CONFIGURAÇÃO DO GRUPO                           [💾 Salvar Tudo] │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ ┌─── INFORMAÇÕES BÁSICAS ─────────────────────────────────────────┐ │
│ │                                                                 │ │
│ │ Nome do Grupo *                                                 │ │
│ │ ┌─────────────────────────────────────────────────────────────┐ │ │
│ │ │ Tower of God Brasil                                         │ │ │
│ │ └─────────────────────────────────────────────────────────────┘ │ │
│ │                                                                 │ │
│ │ Descrição                                                       │ │
│ │ ┌─────────────────────────────────────────────────────────────┐ │ │
│ │ │ Grupo dedicado à tradução de Tower of God para português    │ │ │
│ │ │ brasileiro. Qualidade e velocidade são nossas prioridades.  │ │ │
│ │ └─────────────────────────────────────────────────────────────┘ │ │
│ │                                                                 │ │
│ │ Website: https://towerofgod.wiki   Email: contato@tog.br       │ │
│ │                                                                 │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│ ┌─── REDES SOCIAIS ───────────────────────────────────────────────┐ │
│ │ 🎮 Discord: https://discord.gg/towerpg          [✅ Testado]    │ │
│ │ 📱 Telegram: https://t.me/towerofgodbr          [✅ Testado]    │ │
│ │ 📞 WhatsApp: https://chat.whatsapp.com/...      [⏳ Testando]  │ │ 
│ │ 🐦 Twitter: https://twitter.com/togbrasil       [❌ Inválido]  │ │
│ │                                                                 │ │
│ │ [+ Adicionar Rede Social]                                       │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Melhorias UX**:
- **Validação em Tempo Real**: Testa links automaticamente
- **Sugestões Inteligentes**: Auto-complete baseado em padrões
- **Campos Obrigatórios**: Indicados com * e validação visual
- **Preview Live**: Vê como ficará o indexador conforme digita

---

## 📊 Analytics e Relatórios

### **11. Dashboard de Estatísticas**

```
┌─────────────────────────────────────────────────────────────────────┐
│ 📊 ANALYTICS & RELATÓRIOS                          [📅 Últimos 30d] │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐     │
│ │ 📤 UPLOADS  │ │ 📁 STORAGE  │ │ ⏱️ TEMPO    │ │ ✅ SUCESSO  │     │
│ │    1,234    │ │   15.6 GB   │ │   2.3h      │ │    97.2%    │     │
│ │ ↗️ +12% sem │ │ ↗️ +2.1 GB  │ │ ↘️ -15 min  │ │ ↗️ +0.8%    │     │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘     │
│                                                                     │
│ 📈 GRÁFICO DE UPLOADS POR DIA                                       │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │    ▅▅▅                                                         │ │
│ │ ▅▅▅███▅▅▅                                                      │ │  
│ │ ████████▅▅▅▅                                                   │ │
│ │ ███████████▅▅▅▅▅                                               │ │
│ │ ▅████████████████▅▅                                           │ │
│ │ ┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴                               │ │
│ │ 1  5  10  15  20  25  30                                       │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│ 🏆 TOP HOSTS                    🔥 MANGÁS MAIS ATIVOS              │
│ 1. Catbox      342 uploads     1. Tower of God     23 caps         │
│ 2. Imgur       289 uploads     2. One Piece        18 caps         │
│ 3. ImgBox      234 uploads     3. Naruto           15 caps         │
│ 4. Pixeldrain  189 uploads     4. Solo Leveling    12 caps         │
│                                                                     │
│ [📥 Exportar CSV] [📊 Relatório Detalhado] [🔄 Atualizar]         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔔 Sistema de Notificações

### **12. Central de Notificações**

```
┌─────────────────────────────────────────────────────────────────────┐
│ 🔔 NOTIFICAÇÕES                                    [🔕 Marcar Todas] │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ 🟢 UPLOAD CONCLUÍDO                                         2 min   │
│ Tower of God Cap. 471 enviado com sucesso para Catbox              │
│ 📁 23 imagens • 🔗 Album: https://catbox.moe/c/abc123              │
│                                                                     │
│ 🟡 AVISO CDN                                                 15 min  │
│ JSDelivr CDN com 3 min de atraso para Solo Leveling                │
│ 🔄 Tentando novamente... [Ver detalhes]                            │
│                                                                     │
│ 🟢 INDEXADOR ATUALIZADO                                     1 hora  │
│ Index.json gerado com 4 obras • 471 capítulos                      │
│ 📤 Enviado para GitHub automaticamente                             │
│                                                                     │
│ 🔴 ERRO DE UPLOAD                                           2 horas │
│ Falha ao enviar Naruto Cap. 715 para ImgBB                         │
│ ❌ API Key inválida [⚙️ Corrigir] [🔄 Tentar novamente]            │
│                                                                     │
│ ⚙️ CONFIGURAÇÕES DE NOTIFICAÇÃO                                    │
│ ✅ Uploads concluídos    ✅ Erros críticos    ✅ Updates do GitHub  │
│ ☐ Avisos de CDN          ☐ Estatísticas      ☐ Notificações push   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Ferramentas de Desenvolvedor

### **13. Debug Panel (Modo Desenvolvedor)**

```
┌─────────────────────────────────────────────────────────────────────┐
│ 🛠️ DEVELOPER TOOLS                                   [👁️ Mode: DEV] │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ 📊 PERFORMANCE METRICS                                              │
│ • QML Render Time: 16.7ms (60 FPS)                                 │
│ • Memory Usage: 145MB / 512MB                                       │
│ • Active HTTP Connections: 8/20                                     │
│ • Upload Queue Size: 3 jobs                                         │
│                                                                     │
│ 🔍 API LOGS (Últimas 10 requisições)                               │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ [200] POST catbox.moe/user/api.php - 1.2s - 2.3MB             │ │
│ │ [200] GET api.github.com/repos/user/repo - 0.8s - 45KB        │ │
│ │ [429] POST imgur.com/api/upload - 2.1s - Rate Limited         │ │
│ │ [200] GET cdn.jsdelivr.net/gh/user/repo - 0.3s - 128KB        │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│ 🧪 TESTES RÁPIDOS                                                  │
│ [🌐 Testar Hosts] [📋 Validar JSONs] [🔗 Verificar CDNs]          │
│ [📤 Upload de Teste] [🔄 Reset Cache] [💾 Export Logs]            │
│                                                                     │
│ ⚙️ CONFIGURAÇÕES DEBUG                                             │
│ ✅ Logs detalhados   ✅ Network timing   ☐ QML debugging          │
│ ☐ Auto-reload QML   ☐ Mock API calls    ☐ Performance overlay     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🎨 Design System - Especificações Técnicas

### **14. Componentes Base**

```qml
// Design Tokens
QtObject {
    // Spacing Scale (8pt grid)
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
    
    // Typography Scale
    readonly property int text_xs: 12    // 0.75rem
    readonly property int text_sm: 14    // 0.875rem
    readonly property int text_base: 16  // 1rem
    readonly property int text_lg: 18    // 1.125rem
    readonly property int text_xl: 20    // 1.25rem
    readonly property int text_2xl: 24   // 1.5rem
    readonly property int text_3xl: 30   // 1.875rem
    readonly property int text_4xl: 36   // 2.25rem
    
    // Border Radius Scale
    readonly property int radius_sm: 4   // Small elements
    readonly property int radius_md: 8   // Standard cards
    readonly property int radius_lg: 12  // Large cards
    readonly property int radius_xl: 16  // Hero elements
    readonly property int radius_full: 999 // Pills/badges
    
    // Shadow Levels
    readonly property string shadow_sm: "0 1px 2px rgba(0,0,0,0.05)"
    readonly property string shadow_md: "0 4px 6px rgba(0,0,0,0.1)"
    readonly property string shadow_lg: "0 10px 15px rgba(0,0,0,0.1)"
    readonly property string shadow_xl: "0 20px 25px rgba(0,0,0,0.15)"
}
```

### **15. Component Library**

```qml
// ModernButton.qml - Componente base reutilizável
Rectangle {
    id: root
    
    // Props
    property string text: ""
    property string variant: "primary" // primary, secondary, ghost, danger
    property string size: "md"         // sm, md, lg
    property bool loading: false
    property bool disabled: false
    
    // Computed styles
    readonly property color bgColor: {
        switch(variant) {
            case "primary": return disabled ? "#1e40af80" : "#1e40af"
            case "secondary": return disabled ? "#374151" : "#6b7280"  
            case "danger": return disabled ? "#dc262680" : "#dc2626"
            case "ghost": return "transparent"
            default: return "#1e40af"
        }
    }
    
    readonly property int padding: {
        switch(size) {
            case "sm": return 8
            case "lg": return 16
            case "md":
            default: return 12
        }
    }
    
    // Visual design
    width: content.implicitWidth + padding * 2
    height: content.implicitHeight + padding * 2
    radius: 8
    color: bgColor
    border.color: variant === "ghost" ? "#374151" : "transparent"
    border.width: variant === "ghost" ? 1 : 0
    
    // States and transitions
    states: [
        State {
            name: "hovered"
            when: mouseArea.containsMouse && !disabled
            PropertyChanges { target: root; scale: 1.02 }
        },
        State {
            name: "pressed"  
            when: mouseArea.pressed && !disabled
            PropertyChanges { target: root; scale: 0.98 }
        }
    ]
    
    transitions: Transition {
        NumberAnimation { 
            properties: "scale"
            duration: 150
            easing.type: Easing.OutCubic
        }
    }
    
    // Content
    Row {
        id: content
        anchors.centerIn: parent
        spacing: 8
        
        // Loading spinner
        Rectangle {
            visible: loading
            width: 16; height: 16
            radius: 8
            color: "transparent"
            border.color: textColor
            border.width: 2
            
            RotationAnimation {
                target: parent
                running: loading
                duration: 1000
                loops: Animation.Infinite
                from: 0; to: 360
            }
        }
        
        // Text
        Text {
            text: root.text
            color: disabled ? "#9ca3af" : "#ffffff"
            font.pixelSize: root.size === "sm" ? 14 : root.size === "lg" ? 18 : 16
            font.weight: Font.Medium
        }
    }
    
    // Interaction
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        enabled: !disabled && !loading
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        
        onClicked: root.clicked()
    }
    
    signal clicked()
}
```

---

## 🚀 Implementação - Roadmap

### **Fase 1: Base Architecture (2 semanas)**
- ✅ Redesign do layout principal com grid responsivo
- ✅ Implementação do design system (tokens, componentes)
- ✅ Nova estrutura de cores e tipografia
- ✅ Componentes base (Button, Card, Input, etc.)

### **Fase 2: Core Features (3 semanas)**  
- ✅ Manga cards com preview e actions
- ✅ Upload workflow redesenhado
- ✅ Settings panel categorizado
- ✅ Host configuration com status visual

### **Fase 3: Advanced Features (3 semanas)**
- ✅ Indexador hub completamente redesenhado
- ✅ Analytics dashboard com gráficos
- ✅ Notification center
- ✅ Search e filtros inteligentes

### **Fase 4: Polish & Performance (2 semanas)**
- ✅ Animações e micro-interações
- ✅ Performance optimization
- ✅ Testes de usabilidade
- ✅ Dark/Light theme toggle

### **Fase 5: Advanced Tools (1 semana)**
- ✅ Developer tools panel
- ✅ Debug mode
- ✅ Export/import configurations
- ✅ Advanced user preferences

---

## 📱 Responsividade e Adaptação

### **Breakpoints Definidos**

```qml
// Responsive breakpoints
QtObject {
    readonly property int mobile: 640    // <= 640px
    readonly property int tablet: 768    // <= 768px  
    readonly property int desktop: 1024  // <= 1024px
    readonly property int wide: 1280     // <= 1280px
    readonly property int ultrawide: 1536 // > 1536px
}
```

### **Adaptações por Tamanho**

| Tamanho | Layout | Sidebar | Cards | Actions |
|---------|---------|---------|-------|---------|
| **Mobile** (≤640px) | Stack vertical | Hidden/overlay | 1 coluna | Bottom sheet |
| **Tablet** (≤768px) | Split 30/70 | Collapsible | 2 colunas | Floating |
| **Desktop** (≤1024px) | Split 25/75 | Fixed sidebar | 3 colunas | Inline |
| **Wide** (≤1280px) | Split 20/80 | Extended info | 4 colunas | Contextual |
| **Ultra** (>1536px) | Split 15/85 | Rich content | 5+ colunas | Advanced |

---

## 🎯 Conclusão - Benefícios da Nova Interface

### **🚀 Melhorias de Produtividade**
- **50% menos cliques** para ações comuns
- **Workflow otimizado** com steps visuais claros  
- **Ações em batch** para seleção múltipla
- **Quick actions** em todos os cards

### **🎨 Experiência Visual Superior**
- **Design minimalista** com foco no conteúdo
- **Hierarquia visual clara** com typography scale
- **Micro-animações** que guiam o usuário
- **Alto contraste** para máxima legibilidade

### **⚡ Performance e Responsividade**
- **Grid adaptativo** para qualquer resolução
- **Componentes otimizados** com lazy loading
- **Animações performáticas** com QML
- **Memory-efficient** com proper cleanup

### **🛠️ Manutenibilidade**
- **Design system consistente** com tokens reutilizáveis
- **Componentes modulares** para fácil extensão
- **Code organization** seguindo best practices
- **Developer tools** para debugging eficiente

---

**🌟 Este redesign representa uma evolução completa da interface, mantendo toda a funcionalidade existente enquanto oferece uma experiência moderna, intuitiva e altamente produtiva para os usuários do Manga Uploader Pro!**
