# Guia de Migração - Manga Uploader Pro

## Visão Geral
Este guia ajuda na transição do código antigo (`catbox_uploader_gui.py`) para a nova arquitetura modular.

## Mudanças Principais

### 1. Arquitetura
- **Antes**: Monolítico em um único arquivo
- **Agora**: Modular com separação clara de responsabilidades

### 2. Interface
- **Antes**: Widgets tradicionais (QWidget)
- **Agora**: QML moderno com Material Design

### 3. Performance
- **Antes**: Threading básico
- **Agora**: Async/await nativo com httpx

## Como Executar

1. Instalar dependências:
```bash
pip install -r requirements.txt
```

2. Executar aplicação:
```bash
cd src
python main.py
```

## Migração de Dados

### Configurações
As configurações antigas em `settings.json` precisam ser migradas para o novo formato:

**Antigo** (settings_v2.json):
```json
{
    "userhash": "seu_hash",
    "root_folder": "C:/Manga",
    "max_workers": 5
}
```

**Novo** (config.json):
```json
{
    "root_folder": "C:/Manga",
    "selected_host": "Catbox",
    "hosts": {
        "Catbox": {
            "enabled": true,
            "userhash": "seu_hash",
            "max_workers": 5
        }
    }
}
```

### Metadados
Os arquivos JSON de mangá existentes são compatíveis com a nova versão.

## Próximos Passos

1. **Testar** a nova interface com um mangá pequeno
2. **Migrar** as configurações manualmente
3. **Adicionar** novos hosts (Imgur já está preparado)
4. **Customizar** a interface no arquivo `main.qml`

## Funcionalidades Pendentes

- [ ] Imgur host completo
- [ ] Sistema de notificações
- [ ] Preview de imagens
- [ ] Drag & drop
- [ ] Auto-updater

## Problemas Conhecidos

1. QML requer Qt 6.5+ (pode precisar atualizar)
2. Algumas animações ainda não implementadas
3. GitHub upload ainda não migrado