# Manga Uploader Pro

Aplicação moderna e profissional para upload de mangás com interface QML, arquitetura assíncrona e sistema de indexação JSON automática para grupos de scanlation.

## 🚀 Características Principais

### Upload e Hospedagem
- 🚀 **Upload paralelo assíncrono** com workers dedicados
- 🔌 **Sistema de hosts plugável** com 10+ provedores suportados
- 🔄 **Retry automático** com backoff exponencial
- 📊 **Progresso em tempo real** com fila de processamento
- 🖼️ **Upload inteligente** com detecção automática de imagens

### Interface e Experiência
- 🎨 **Interface moderna QML** com Material Design dark theme
- 📱 **Design responsivo** com alta nitidez e contraste
- 🖱️ **Interação intuitiva** com seleção múltipla de capítulos
- 🔧 **Configuração visual** de hosts e credenciais

### Sistema de Indexação JSON
- 📋 **Geração automática de indexadores** para grupos de scanlation
- 🌐 **URLs RAW automáticas** via CDN (JSDelivr)
- 📊 **Estatísticas automáticas** (total de séries, capítulos)
- 🔗 **Integração GitHub** para hospedagem de metadados

### Integração e Automação
- 🔗 **GitHub Service** integrado para commit automático
- 📦 **Gerenciamento de metadados** com merge inteligente
- 🛠️ **Build system** com PyInstaller para executáveis
- 🧪 **Testes automatizados** com pytest e async support

## ⚡ Melhorias Recentes (v2.0)

- ✅ **Sistema de host padrão**: Configuração persistente do provedor ativo
- ✅ **Busca fuzzy de JSONs**: Localização inteligente de metadados existentes  
- ✅ **Timestamps precisos**: Data/hora exata do upload nos metadados
- ✅ **Grupos nomeados**: Substituição de "default" por nome real do grupo
- ✅ **Interface padronizada**: Layout consistente para todos os hosts
- ✅ **ImgBox otimizado**: Método único (async generator) para uploads
- ✅ **Conversão automática**: WebP → JPG para compatibilidade
- ✅ **Cleanup inteligente**: Remoção automática de arquivos temporários

## 🛠️ Hosts Suportados

| Host | Status | Características |
|------|--------|----------------|
| **Catbox** | ✅ Ativo | Sem limite, não requer API |
| **Imgur** | ✅ Ativo | API v3, álbuns suportados |
| **ImgBB** | ✅ Ativo | API key necessária |
| **Imgbox** | ✅ Ativo | Session cookie required |
| **Lensdump** | ✅ Ativo | Upload anônimo |
| **Pixeldrain** | ✅ Ativo | API opcional |
| **Gofile** | ✅ Ativo | Upload anônimo |
| **ImageChest** | ✅ Ativo | API key required |
| **ImgHippo** | ✅ Ativo | Upload anônimo |
| **ImgPile** | ✅ Ativo | Instâncias customizáveis |

## 📦 Instalação e Configuração

### Pré-requisitos
- Python 3.8+ (recomendado 3.11+)
- Git (para integração GitHub)
- Windows 10/11, Linux ou macOS

### Instalação Rápida

```bash
# Clone o repositório
git clone https://github.com/Jhoorodr/up-host.git
cd up-host

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
python run.py
```

### Instalação para Desenvolvimento

```bash
# Instalar com dependências de desenvolvimento
pip install -e ".[dev]"

# Ou instalar tudo manualmente
pip install -r requirements.txt
pip install pytest pytest-asyncio black flake8 mypy PyInstaller
```

## 🚀 Como Usar

### Execução Básica

```bash
# Método 1: Script de entrada (recomendado)
python run.py

# Método 2: Launcher Windows/WSL
./mangauploadpro.bat  # Windows

# Método 3: Direto do src
cd src && python main.py
```

### Configuração Inicial

1. **Configure um host de imagem**:
   - Abra as configurações na interface
   - Selecione um host (Catbox é recomendado para iniciantes)
   - Configure credenciais se necessário

2. **Configure GitHub (opcional)**:
   - Token de acesso pessoal
   - Repositório para metadados
   - Branch principal (padrão: main)

3. **Configure o indexador (para grupos)**:
   - Nome do grupo de scanlation
   - Descrição e redes sociais
   - Template de URLs personalizável

### Fluxo de Trabalho

1. **Selecione um manga** na lista lateral
2. **Escolha capítulos** para upload (seleção múltipla)
3. **Configure metadados** personalizados se necessário
4. **Inicie o upload** e acompanhe o progresso
5. **Geração automática** de JSON com URLs das imagens
6. **Commit automático** no GitHub (se configurado)

## 📁 Estrutura do Projeto

```
up-host/
├── src/                        # Código fonte principal
│   ├── main.py                # Entry point da aplicação
│   ├── core/                  # Lógica de negócio
│   │   ├── config.py         # Gerenciamento de configuração
│   │   ├── models/           # Dataclasses e modelos
│   │   │   ├── __init__.py   # Manga, Chapter, UploadResult
│   │   │   └── indexador.py  # Modelos do sistema de indexação
│   │   ├── hosts/            # Implementações de hosts
│   │   │   ├── base.py       # Classe base abstrata
│   │   │   ├── catbox.py     # Catbox.moe implementation
│   │   │   ├── imgur.py      # Imgur API v3
│   │   │   ├── imgbb.py      # ImgBB API
│   │   │   └── ...           # Outros 7 hosts
│   │   └── services/         # Serviços de alto nível
│   │       ├── uploader.py   # Serviço principal de upload
│   │       ├── queue.py      # Fila assíncrona com workers
│   │       └── github.py     # Integração GitHub API
│   ├── ui/                   # Interface do usuário
│   │   ├── backend.py        # Bridge Qt/QML ↔ Python
│   │   ├── models.py         # Models para QML (MangaList, etc)
│   │   └── qml/              # Interface QML
│   │       ├── main.qml      # Janela principal
│   │       └── components/   # Componentes reutilizáveis
│   └── utils/                # Utilitários
│       ├── helpers.py        # Funções auxiliares
│       ├── sanitizer.py      # Sanitização de nomes
│       └── json_updater.py   # Merge inteligente de JSONs
├── docs/                     # Documentação
│   
├── tests/                    # Testes automatizados
│   ├── test_core.py         # Testes da lógica core
│   └── __init__.py
├── run.py                   # Entry point simplificado
├── mangauploadpro.bat       # Launcher para Windows/WSL
├── .env.example             # Exemplo de variáveis de ambiente
├── requirements.txt        # Dependências Python
├── pyproject.toml         # Configuração do projeto
└── README.md              # Este arquivo
```

## 🔨 Build e Deploy

### Criar Executável

```bash
# Exemplo com PyInstaller (manual)
pyinstaller src/main.py --name MangaUploaderPro --onefile --windowed

# O executável será gerado em:
# - Windows: dist/MangaUploaderPro.exe
# - Linux: dist/MangaUploaderPro
# - macOS: dist/MangaUploaderPro.app
```

### Configuração do Build

O build (manual) inclui:
- ✅ Executável standalone (--onefile)
- ✅ Interface gráfica (--windowed)
- ✅ Assets QML inclusos
- ✅ Todas as dependências empacotadas
- ✅ Ícone personalizado (se disponível)

## 🧪 Testes e Qualidade

### Executar Testes

```bash
# Todos os testes
pytest tests/ -v

# Testes específicos
pytest tests/test_core.py

# Com coverage
pytest tests/ --cov=src --cov-report=html
```

### Ferramentas de Qualidade

```bash
# Formatação de código
black src/ tests/ --line-length 100

# Linting
flake8 src/ tests/

# Type checking
mypy src/
```

## 📊 Sistema de Indexação

O Manga Uploader Pro inclui um sistema avançado de indexação JSON para grupos de scanlation:

### Características do Indexador
- 📋 **Catalogação automática** de todas as obras do grupo
- 🌐 **URLs RAW** via CDN para acesso direto aos JSONs
- 📊 **Estatísticas em tempo real** (séries, capítulos, atualizações)
- 🔧 **Configuração flexível** de metadados do grupo
- 🔗 **Integração GitHub** para hospedagem centralizada

### Exemplo de Indexador Gerado

```json
{
  "hub": {
    "title": "Meu Grupo Scan",
    "description": "Grupo focado em manhwas de ação",
    "social": {
      "discord": "https://discord.gg/...",
      "telegram": "@meugrupo"
    }
  },
  "statistics": {
    "total_series": 15,
    "total_chapters": 245,
    "last_updated": "2025-01-13T10:30:00Z"
  },
  "series": {
    "tower_of_god": {
      "title": "Tower of God",
      "url": "https://cdn.jsdelivr.net/gh/user/repo@main/Tower_of_God.json",
      "chapters": 120,
      "status": "ongoing"
    }
  }
}
```

## 🔧 Configuração Avançada

### Variáveis de Ambiente (Opcional)

```env
# Baseie-se no arquivo .env.example
MANGA_ROOT_FOLDER=C:\Manga
MANGA_OUTPUT_FOLDER=C:\Output
GITHUB_TOKEN=ghp_xxxxx
DEFAULT_HOST=Catbox
LOG_LEVEL=INFO
```

### Configuração de Hosts

Cada host pode ser configurado individualmente:
- **Rate limiting** personalizado
- **Máximo de workers** por host
- **Credenciais** específicas (API keys, tokens)
- **URLs customizadas** (para hosts com múltiplas instâncias)

## 🆘 Solução de Problemas

### Problemas Comuns

1. **"Erro ao carregar QML"**
   ```powershell
   # Reinstalar PySide6
   pip uninstall PySide6
   pip install PySide6>=6.5.0
   ```

2. **"Host não responde"**
   - Verifique sua conexão com a internet
   - Teste as credenciais do host
   - Verifique rate limits

3. **"Falha no upload de imagens"**
   - Verifique o formato das imagens (JPG, PNG, WebP)
   - Confirme o tamanho máximo do host
   - Verifique permissões de arquivo

### Logs e Debugging

```powershell
# Logs são salvos em:
# Windows: %USERPROFILE%\.manga_uploader\logs\
# Linux/Mac: ~/.manga_uploader/logs/

# Para debug verbose, edite main.py:
logger.add("debug.log", level="DEBUG")
```

## 🚀 Contribuição

Contribuições são bem-vindas! Veja os arquivos em `docs/` para:
- `BUGMAP.md` - Registro de bugs, correções e pendências

## 📄 Licença

MIT License - veja `pyproject.toml` para detalhes completos.

## 🔗 Links Úteis

- **Documentação**: Pasta `docs/`
- **Issues**: Use o sistema de issues do GitHub

- **Releases**: Executáveis pré-compilados (quando disponível)