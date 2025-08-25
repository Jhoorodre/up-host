# Roadmap - Modernização Manga Uploader

## Fase 1: Preparação e Estrutura (Semana 1)
- [x] Criar estrutura de diretórios
- [x] Separar lógica de negócio da UI
- [x] Implementar sistema de hosts plugável
- [x] Criar camada de serviços assíncrona

## Fase 2: Backend Moderno (Semana 2)
- [x] Implementar BaseHost abstract class
- [x] Refatorar CatboxHost com async/await
- [ ] Criar ImgurHost funcional
- [x] Sistema de retry com backoff exponencial
- [ ] Queue system para uploads

## Fase 3: UI Moderna com QML (Semana 3)
- [x] Setup inicial QML + PySide6
- [x] Tela principal moderna
- [x] Sistema de temas (dark/light)
- [ ] Animações e transições
- [ ] Componentes reutilizáveis

## Fase 4: Features Avançadas (Semana 4)
- [ ] Auto-updater
- [ ] Sistema de notificações
- [ ] Drag & drop melhorado
- [ ] Preview de imagens
- [ ] Estatísticas de upload

## Estrutura Final:
```
app-up/
├── src/
│   ├── core/              # Lógica de negócio
│   │   ├── models/        # Dataclasses
│   │   ├── services/      # Serviços
│   │   └── hosts/         # Implementações
│   ├── ui/
│   │   ├── qml/          # Arquivos QML
│   │   ├── components/    # Componentes QML
│   │   └── resources/     # Ícones, fontes
│   └── utils/            # Helpers
├── tests/                # Testes unitários
├── docs/                 # Documentação
└── requirements.txt      # Dependências
```

## Dependências Novas:
- `qasync` - Integração async com Qt
- `aiofiles` - I/O assíncrono
- `httpx` - Cliente HTTP assíncrono
- `pydantic` - Validação de dados
- `loguru` - Logging moderno

## Benefícios Esperados:
- 🚀 Performance 3-5x melhor
- 🎨 UI moderna e responsiva
- 🔌 Fácil adicionar novos hosts
- 🛡️ Código mais testável e mantível
- 📦 Deploy simplificado
