# Novos Hosts de Imagem Implementados

Este documento descreve os novos hosts de imagem que foram implementados baseados no ROADMAP_HOSTS.md.

## Hosts Implementados

### 1. ImgBB
- **API**: Oficial (Simples)
- **Requer**: API Key
- **Configuração**: `imgbbApiKey`
- **Uso ideal**: Scripts, bots e projetos menores que precisam de upload rápido
- **Álbuns**: Não suportado via API

**Como obter API Key:**
1. Acesse https://api.imgbb.com/
2. Registre-se ou faça login
3. Copie sua API key
4. Configure no aplicativo

### 2. Lensdump
- **API**: Oficial (Simples)
- **Requer**: Nenhuma autenticação
- **Uso ideal**: Preservação da qualidade da imagem (sem compressão forçada)
- **Álbuns**: Não suportado via API
- **Nota**: Excelente para GIFs e vídeos de alta qualidade

### 3. Pixeldrain
- **API**: Oficial
- **Requer**: API Key opcional (para uso básico não é necessário)
- **Configuração**: `pixeldrainApiKey` (opcional)
- **Uso ideal**: Compartilhamento de arquivos com foco em velocidade
- **Álbuns**: Não suportado via API

### 4. Gofile
- **API**: Oficial
- **Requer**: Nenhuma autenticação para uso básico
- **Uso ideal**: Compartilhar múltiplos arquivos em uma galeria
- **Álbuns**: Suportado nativamente
- **Nota**: Retorna página de download, não link direto

### 5. ImageChest
- **API**: Oficial (Estável)
- **Requer**: API Key
- **Configuração**: `imageChestApiKey`
- **Uso ideal**: Projetos sérios que precisam de API estável
- **Álbuns**: Suportado via API

**Como obter API Key:**
1. Acesse https://imagechest.com/
2. Registre-se e acesse as configurações
3. Gere uma API key
4. Configure no aplicativo

### 6. Imgbox
- **API**: Não oficial (via pyimgbox)
- **Requer**: Biblioteca `pyimgbox`
- **Uso ideal**: Projetos Python que querem conveniência
- **Álbuns**: Criados automaticamente para múltiplos uploads
- **Nota**: Requer instalação adicional: `pip install pyimgbox`

## Configuração

### Backend Properties Adicionadas:
- `imgbbApiKey`: API key para ImgBB
- `imageChestApiKey`: API key para ImageChest  
- `pixeldrainApiKey`: API key para Pixeldrain (opcional)

### Hosts Automáticos (sem configuração):
- Lensdump
- Gofile
- Imgbox (requer pyimgbox)

## Dependências Adicionais

### Necessárias:
```bash
pip install aiohttp>=3.8.0
```

### Opcionais:
```bash
pip install pyimgbox>=1.0.4  # Para Imgbox
```

## Como Usar

1. **Configurar API Keys** (quando necessário):
   - Acesse as configurações do aplicativo
   - Insira as API keys nos campos apropriados
   - O host será automaticamente habilitado

2. **Selecionar Host**:
   - Escolha o host desejado na lista dropdown
   - O aplicativo salvará sua preferência

3. **Upload**:
   - Funciona igual aos hosts existentes
   - Cada host tem suas características específicas

## Limitações Conhecidas

- **Gofile**: Retorna página de download, não link direto para imagem
- **Imgbox**: Requer biblioteca adicional
- **Rate Limits**: Cada host tem seus próprios limites
- **Álbuns**: Nem todos os hosts suportam criação de álbuns

## Troubleshooting

### Imgbox não funciona:
```bash
pip install pyimgbox
```

### API Key inválida:
- Verifique se a key foi copiada corretamente
- Confirme se a key tem as permissões necessárias
- Teste a key diretamente na documentação da API

### Upload falha:
- Verifique conexão com internet
- Confirme se o arquivo é uma imagem válida
- Verifique logs para detalhes do erro

## Performance

| Host | Velocidade | Confiabilidade | Qualidade |
|------|------------|----------------|-----------|
| Lensdump | Média | Alta | Máxima |
| Pixeldrain | Alta | Alta | Alta |
| ImgBB | Alta | Média | Boa |
| ImageChest | Média | Muito Alta | Alta |
| Gofile | Média | Média | Boa |
| Imgbox | Média | Alta | Boa |

## Próximos Passos

Para futuras implementações, considere:
- Dropbox/Google Drive (para backup privado)
- Mais hosts conforme demanda
- Melhor suporte a álbuns
- Interface para configuração avançada