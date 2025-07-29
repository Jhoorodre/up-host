# Indexador JSON - Aplicação Standalone

## 📋 Visão Geral

O **Indexador JSON** é uma aplicação standalone especializada em criar e gerenciar automaticamente arquivos de índice que catalogam todas as **URLs RAW dos JSONs** de manga/manhwa de grupos de scanlation. 

Esta aplicação foi separada do Manga Uploader Pro para ser um sistema independente, focado exclusivamente na criação de indexadores profissionais compatíveis com readers como **Tachiyomi** e aplicações web.

---

## 🎯 Objetivos da Aplicação Standalone

### **Por que uma aplicação separada?**
1. **Especialização**: Foco exclusivo no sistema de indexação
2. **Independência**: Não depende do uploader de mangás
3. **Flexibilidade**: Pode trabalhar com JSONs de qualquer fonte
4. **Performance**: Aplicação mais leve e rápida
5. **Distribuição**: Facilita uso por diferentes grupos

### **Público-alvo:**
- **Grupos de scanlation** que querem criar catálogos profissionais
- **Desenvolvedores** que mantêm sites/apps de manga
- **Comunidades** que precisam de APIs JSON organizadas
- **Usuários** que querem seus próprios indexadores personalizados

---

## 🏗️ Arquitetura da Aplicação Standalone

### **Tecnologias Recomendadas:**
```
Frontend: 
  - QML + Python (compatível com Manga Uploader Pro)
  - OU React/Vue.js para versão web
  - OU CLI puro em Python

Backend/Core:
  - Python 3.8+ com Pydantic para validação
  - httpx para requests assíncronos
  - pathlib para manipulação de arquivos
  - loguru para logging avançado

Funcionalidades:
  - Scanner de JSONs locais e remotos
  - Gerador de indexadores automático
  - Validador de URLs CDN
  - Uploader para GitHub/repositórios
  - API REST opcional
```

### **Estrutura do Projeto:**
```
indexador-json/
├── src/
│   ├── core/
│   │   ├── models/          # Modelos Pydantic (extraídos do Manga Uploader)
│   │   │   ├── indexador.py # Todos os modelos de indexação
│   │   │   └── common.py    # Modelos compartilhados
│   │   ├── services/
│   │   │   ├── scanner.py   # Scanner de JSONs
│   │   │   ├── generator.py # Gerador de indexadores
│   │   │   ├── validator.py # Validador de URLs/CDN
│   │   │   └── uploader.py  # Upload para GitHub/repos
│   │   └── config.py        # Configurações da aplicação
│   ├── ui/                  # Interface (QML ou Web)
│   │   ├── qml/            # Se for QML
│   │   ├── web/            # Se for web
│   │   └── cli/            # Interface CLI
│   └── utils/
│       ├── helpers.py      # Funções auxiliares
│       ├── sanitizer.py    # Sanitização de nomes
│       └── cdn.py          # Utilities CDN
├── docs/
│   ├── API.md              # Documentação da API
│   ├── USAGE.md            # Como usar
│   └── EXAMPLES.md         # Exemplos práticos
├── tests/
│   ├── test_scanner.py
│   ├── test_generator.py
│   └── test_validator.py
├── requirements.txt
├── pyproject.toml
└── main.py                 # Entry point
```

---

## 🔄 Funcionalidades Core

### **1. Scanner de JSONs**
```python
class JSONScanner:
    """Escaneia JSONs locais e remotos"""
    
    async def scan_local_folder(self, path: Path) -> List[SeriesInfo]:
        """Escaneia pasta local por JSONs válidos"""
        
    async def scan_github_repo(self, repo: str, folder: str = "") -> List[SeriesInfo]:
        """Escaneia repositório GitHub"""
        
    async def scan_remote_urls(self, urls: List[str]) -> List[SeriesInfo]:
        """Valida lista de URLs remotas"""
        
    def validate_manga_json(self, data: dict) -> bool:
        """Valida se JSON é formato de manga válido"""
```

### **2. Gerador de Indexadores**
```python
class IndexadorGenerator:
    """Gera indexadores no formato padrão"""
    
    def generate_hub_indexador(self, series_list: List[SeriesInfo], 
                              hub_config: HubConfig) -> IndexadorData:
        """Gera indexador principal do hub"""
        
    def generate_api_endpoints(self, indexador: IndexadorData) -> Dict[str, Any]:
        """Gera endpoints de API automáticos"""
        
    def generate_search_index(self, series_list: List[SeriesInfo]) -> Dict[str, Any]:
        """Gera índice de busca otimizado"""
```

### **3. Validador de CDN**
```python
class CDNValidator:
    """Valida status de URLs CDN"""
    
    async def test_cdn_url(self, url: str) -> CDNStatus:
        """Testa status individual de URL"""
        
    async def batch_validate(self, urls: List[str]) -> List[CDNStatus]:
        """Validação em lote de URLs"""
        
    async def monitor_cdn_health(self, indexador: IndexadorData) -> HealthReport:
        """Monitora saúde das CDNs do indexador"""
```

### **4. GitHub Integration**
```python
class GitHubUploader:
    """Upload e sincronização com GitHub"""
    
    async def upload_indexador(self, indexador: IndexadorData, 
                              repo_config: RepoConfig) -> bool:
        """Upload do indexador para GitHub"""
        
    async def sync_with_github(self, local_path: Path, 
                              repo_config: RepoConfig) -> SyncReport:
        """Sincroniza JSONs locais com GitHub"""
        
    async def create_release(self, version: str, 
                           changelog: str) -> bool:
        """Cria release automático"""
```

---

## 📊 Formatos de Indexador

### **Indexador Principal (index.json)**
```json
{
  "v": "2.1",
  "updated": "2025-07-29T10:30:00Z",
  "hub": {
    "id": "grupo-scan-hub",
    "name": "Grupo Scan Brasil",
    "subtitle": "Mangás e Manhwas em Português",
    "description": "Grupo brasileiro especializado em séries de ação",
    "cover": "https://files.catbox.moe/hub-cover.jpg",
    "website": "https://gruposcan.com.br",
    "lang": "pt-BR",
    "disclaimer": "Lembre-se sempre de apoiar o autor original!"
  },
  "social": [
    {
      "id": "discord",
      "name": "Discord",
      "platform": "discord",
      "url": "https://discord.gg/exemplo",
      "description": "Servidor principal do grupo",
      "primary": true,
      "memberCount": "1500+",
      "features": ["chat", "releases", "support"]
    },
    {
      "id": "telegram",
      "name": "Telegram",
      "platform": "telegram", 
      "url": "https://t.me/gruposcan",
      "description": "Canal de anúncios",
      "primary": false,
      "features": ["announcements"]
    }
  ],
  "featured": [
    {
      "id": "manga-destaque-1",
      "title": "Manga em Destaque",
      "slug": "manga-destaque",
      "cover": "https://images.catbox.moe/cover.jpg",
      "status": "ongoing",
      "chapters": 45,
      "rating": 4.8,
      "url": "https://cdn.jsdelivr.net/gh/grupo/repo@main/manga.json",
      "priority": 1,
      "latest": true,
      "tags": ["ação", "aventura"]
    }
  ],
  "statistics": {
    "overview": {
      "total_series": 25,
      "total_chapters": 890,
      "active_series": 18,
      "completed_series": 7
    },
    "team": {
      "total_members": 12,
      "translators": 4,
      "editors": 3,
      "typesetters": 3,
      "quality_assurance": 2
    },
    "community": {
      "discord_members": 1500,
      "telegram_members": 800,
      "total_followers": 2300
    },
    "content": {
      "avg_rating": 4.6,
      "total_votes": 1250,
      "monthly_releases": 45,
      "weekly_releases": 12
    }
  },
  "api": {
    "base_url": "https://cdn.jsdelivr.net/gh/grupo/repo@main/",
    "endpoints": {
      "all_series": "api/series.json",
      "search": "api/search.json",
      "featured": "api/featured.json",
      "statistics": "api/stats.json"
    }
  },
  "technical": {
    "cache": {
      "cdn_ttl": 3600,
      "api_ttl": 1800,
      "image_ttl": 86400
    },
    "formats": {
      "supported_images": ["jpg", "png", "webp"],
      "json_version": "2.1",
      "encoding": "utf-8"
    }
  }
}
```

### **API Endpoints Automáticos**

#### **api/series.json** (Lista completa)
```json
{
  "total": 25,
  "updated": "2025-07-29T10:30:00Z",
  "series": [
    {
      "id": "manga-1",
      "title": "Nome do Manga",
      "slug": "nome-do-manga",
      "status": "ongoing",
      "chapters": 45,
      "url": "https://cdn.jsdelivr.net/gh/grupo/repo@main/manga1.json",
      "cover": "https://images.catbox.moe/cover1.jpg",
      "tags": ["ação", "aventura"],
      "rating": 4.8,
      "last_updated": "2025-07-28T15:20:00Z"
    }
  ]
}
```

#### **api/search.json** (Índice de busca)
```json
{
  "index": {
    "titles": [
      {"id": "manga-1", "title": "Nome do Manga", "alt_titles": ["Alternative Name"]},
      {"id": "manga-2", "title": "Outro Manga", "alt_titles": []}
    ],
    "tags": {
      "ação": ["manga-1", "manga-3"],
      "aventura": ["manga-1", "manga-2"],
      "romance": ["manga-4"]
    },
    "authors": {
      "Autor 1": ["manga-1"],
      "Autor 2": ["manga-2", "manga-3"]
    }
  }
}
```

---

## 🚀 Casos de Uso

### **1. Grupo de Scanlation Básico**
```bash
# Escaneia pasta local com JSONs
indexador scan-local ./meus-jsons/

# Gera indexador
indexador generate --hub-name "Meu Grupo" --output ./index.json

# Upload para GitHub
indexador upload-github --repo "meugrupo/data" --file ./index.json
```

### **2. Sincronização Automática**
```bash
# Monitora pasta e auto-atualiza
indexador watch ./jsons/ --auto-upload --repo "grupo/data"

# Valida CDN periodicamente
indexador validate-cdn --indexador ./index.json --schedule daily
```

### **3. API REST (Opcional)**
```bash
# Inicia servidor API local
indexador serve --port 8080 --indexador ./index.json

# Endpoints disponíveis:
# GET /api/series        - Lista todas as séries
# GET /api/search?q=...  - Busca por séries
# GET /api/featured      - Séries em destaque
# GET /api/stats         - Estatísticas do hub
```

---

## ⚙️ Configuração

### **config.json**
```json
{
  "hub": {
    "name": "Meu Grupo Scan",
    "subtitle": "Mangás em Português",
    "description": "Descrição do grupo...",
    "website": "https://meugrupo.com",
    "cover": "https://files.catbox.moe/cover.jpg",
    "lang": "pt-BR"
  },
  "social": {
    "discord": "https://discord.gg/...",
    "telegram": "https://t.me/...",
    "twitter": "https://twitter.com/...",
    "facebook": "https://facebook.com/..."
  },
  "github": {
    "token": "ghp_...",
    "repo": "meugrupo/data",
    "branch": "main",
    "folder": "api"
  },
  "cdn": {
    "preferred": "jsdelivr",
    "template": "https://cdn.jsdelivr.net/gh/{user}/{repo}@{branch}/{file}",
    "fallback": "raw.githubusercontent.com"
  },
  "automation": {
    "auto_upload": true,
    "validate_cdn": true,
    "monitor_changes": true,
    "schedule": "daily"
  }
}
```

---

## 📦 Instalação e Deploy

### **Para Usuários**
```bash
# Via pip
pip install indexador-json

# Via executável
./IndexadorJSON.exe  # Windows
./IndexadorJSON      # Linux/Mac
```

### **Para Desenvolvedores**
```bash
# Clone e instale
git clone https://github.com/usuario/indexador-json
cd indexador-json
pip install -e ".[dev]"

# Execute
python main.py --help
```

### **Docker (Opcional)**
```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -e .
CMD ["python", "main.py", "serve"]
```

---

## 🔗 Integração com Readers

### **Tachiyomi**
```json
{
  "name": "Meu Grupo Scan",
  "base_url": "https://cdn.jsdelivr.net/gh/grupo/data@main/",
  "indexador_url": "https://cdn.jsdelivr.net/gh/grupo/data@main/index.json",
  "supports": ["search", "latest", "popular"]
}
```

### **Web Readers**
```javascript
// Carregar indexador
const indexador = await fetch('https://cdn.jsdelivr.net/gh/grupo/data@main/index.json')
  .then(r => r.json());

// Buscar séries
const series = await fetch(indexador.api.base_url + indexador.api.endpoints.all_series)
  .then(r => r.json());
```

---

## 🎯 Roadmap da Aplicação

### **Versão 1.0 (MVP)**
- ✅ Scanner de JSONs locais
- ✅ Gerador de indexador básico
- ✅ Upload GitHub
- ✅ Interface CLI

### **Versão 1.1**
- 🔄 Interface QML/GUI
- 🔄 Validador de CDN
- 🔄 API REST opcional
- 🔄 Sincronização automática

### **Versão 1.2**
- ⏳ Scanner de repositórios remotos
- ⏳ Sistema de templates
- ⏳ Dashboard web
- ⏳ Integração com múltiplas CDNs

### **Versão 2.0**
- ⏳ Suporte a múltiplos grupos
- ⏳ Sistema de federação
- ⏳ API GraphQL
- ⏳ Analytics avançado

---

## 📚 Recursos Adicionais

### **Documentação**
- `docs/API.md` - Referência completa da API
- `docs/TEMPLATES.md` - Sistema de templates
- `docs/INTEGRATION.md` - Guias de integração
- `docs/EXAMPLES.md` - Exemplos práticos

### **Ferramentas**
- `tools/migrate.py` - Migração de indexadores antigos
- `tools/validate.py` - Validador standalone
- `tools/convert.py` - Conversores de formato

### **Comunidade**
- **Discord**: Suporte e discussões
- **GitHub Issues**: Bugs e sugestões
- **Wiki**: Documentação comunitária

---

**O Indexador JSON Standalone será uma ferramenta poderosa e focada para grupos de scanlation criarem catálogos profissionais de suas obras!** 🚀