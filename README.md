# Manga Uploader Pro

Aplicação moderna para upload de mangás com interface QML e arquitetura assíncrona.

## Características

- 🚀 Upload paralelo assíncrono
- 🎨 Interface moderna com QML/Material Design
- 🔌 Sistema de hosts plugável (Catbox, Imgur, etc)
- 📦 Fila de processamento com workers
- 🔄 Retry automático com backoff exponencial
- 📊 Progresso em tempo real

## Instalação

```bash
git clone [seu-repo]
cd app-up
pip install -r requirements.txt
```

## Uso

```bash
cd src
python main.py
```

## Estrutura

```
src/
├── core/          # Lógica de negócio
│   ├── models/    # Dataclasses
│   ├── hosts/     # Implementações (Catbox, Imgur)
│   └── services/  # Serviços (Upload, Queue, GitHub)
├── ui/            # Interface
│   └── qml/       # Arquivos QML
└── utils/         # Funções auxiliares
```

## Build

Para criar executável:

```bash
python build.py
```

## Testes

```bash
pytest tests/
```

## Migração

Veja `docs/MIGRATION.md` para migrar do código antigo.