# Guia de Implementação: Hosts de Imagem e Arquivos Selecionados

Um resumo comparativo das APIs para os serviços de hospedagem escolhidos, ideal para consulta rápida durante o desenvolvimento.

## Tabela Comparativa de APIs

| Host | Tipo de API | Caso de Uso Ideal | Necessita Conta/Chave? |
| :--- | :--- | :--- | :--- |
| **ImageChest** | **Oficial** | Projetos sérios que precisam de uma API estável e documentada. | Sim (Chave de API) |
| **Imgur** | **Oficial (OAuth)**| Aplicações maiores que se integram com as contas de usuário do Imgur. | Sim (Autenticação de usuário) |
| **ImgBB** | **Oficial (Simples)** | Scripts, bots e projetos menores que precisam de um upload rápido e fácil. | Sim (Chave de API) |
| **Imgbox** | Não Oficial (via `pyimgbox`) | Projetos em Python que querem a conveniência de uma biblioteca pronta. | Não |
| **Catbox.moe** | **Oficial (Simples)** | Uploads anônimos e instantâneos de qualquer tipo de arquivo, sem burocracia. | Não |
| **Gofile** | **Oficial** | Compartilhar múltiplos arquivos de uma vez em uma única página/galeria. | Não (para uso básico) |
| **Pixeldrain** | **Oficial** | Compartilhamento de arquivos com foco em velocidade e limites generosos. | Não (para uso básico) |
| **ImgHippo** | **Oficial (API v1)** | Upload de imagens com API JSON bem documentada, suporte a deleção. | Sim (Chave de API) |
| **ImgPile** | **Não Oficial** | API REST simples para upload de imagens via base64 ou multipart. | Não |

---

### Observações Adicionais

* **Host:** **Lensdump**
    * **Tipo de API:** Oficial (Simples)
    * **Caso de Uso Ideal:** Preservação da qualidade da imagem (sem compressão forçada), ótimo para GIFs e vídeos.
    * **Nota:** É uma excelente alternativa ao Catbox.moe, especialmente se a qualidade máxima da imagem ou o suporte a vídeos for a prioridade principal.

* **Hosts:** **Dropbox / Google Drive**
    * **Tipo de API:** Oficial (Robusta e Complexa)
    * **Caso de Uso Ideal:** Armazenamento de arquivos privados, backups, sincronização e aplicações que precisam de um sistema de arquivos completo na nuvem.
    * **Nota:** Embora possuam APIs extremamente poderosas, elas **não são adequadas para hotlinking direto** como os outros serviços. Os links de compartilhamento geralmente levam a uma página de visualização, e não ao arquivo bruto, e podem ter restrições de tráfego. Use-os para gerenciamento de arquivos, não para exibir imagens em fóruns ou blogs.
    OBS: Para hotlinking é necessario usar referências diretas ao arquivo, como `https://www.dropbox.com/s/abc123/file.jpg?raw=1` para Dropbox ou `https://drive.google.com/uc?id=FILE_ID` para Google Drive, mas isso pode não funcionar em todos os casos e depende das configurações de compartilhamento do arquivo. Como usando regex, `https://www.dropbox.com/s/abc123/file.jpg?raw=1` se torna `https://dl.dropboxusercontent.com/s/abc123/file.jpg` e `https://drive.google.com/uc?id=FILE_ID` se torna `https://drive.google.com/uc?id=FILE_ID`.

* **Host:** **ImgHippo**
    * **Tipo de API:** Oficial (API v1)
    * **Endpoints:** 
      - Upload: `https://api.imghippo.com/v1/upload`
      - Delete: `https://api.imghippo.com/v1/delete`
    * **Método:** POST multipart/form-data
    * **Parâmetros Upload:** `api_key` (obrigatório), `file` (obrigatório, até 50MB), `title` (opcional)
    * **Parâmetros Delete:** `api_key` (obrigatório), `Url` (obrigatório)
    * **Resposta Upload:** JSON com `success`, `status`, `data.url`, `data.view_url`, `data.extension`, `data.size`
    * **Resposta Delete:** JSON com `status`, `message`, `deleted_url`
    * **Formatos:** JPG, JPEG, PNG, BMP, PDF, WEBP
    * **Registro:** Disponível através do site com "Get API Key"
    * **Caso de Uso:** API oficial bem documentada, adequada para produção

* **Host:** **ImgPile**
    * **Tipo de API:** Não Oficial (implementação encontrada no GitHub)
    * **Endpoint:** `/api/images` (POST para upload, GET para listagem)
    * **Método:** POST JSON com imagem em base64 ou multipart
    * **Estrutura:** Flask + MySQL, armazenamento local em `/static/uploads/`
    * **Resposta:** JSON com `id`, `name`, `extension`, `description`
    * **Caso de Uso:** Recomendado por OCR.space API como alternativa confiável ao Imgur
    * **Nota:** Necessário verificar se ImgPile.com real usa essa mesma API