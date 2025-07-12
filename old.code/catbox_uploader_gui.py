import sys
import os
import json
import yaml
import requests
import traceback
import time
import re  # <--- CORRIGIDO (separado do sys)
# Não é necessário importar 'sys' e 'os' novamente aqui se já foram importados no topo.
# As importações duplicadas de json, yaml, requests, traceback, time, re também são removidas.
import concurrent.futures
from pathlib import Path
import base64
import unicodedata

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog,
    QProgressBar, QSpinBox, QGroupBox, QFormLayout, QMessageBox,
    QListWidget, QListWidgetItem, QTabWidget, QScrollArea, QComboBox,
    QAbstractItemView, QCheckBox
)
from PySide6.QtCore import Qt, QThread, Signal, QObject
from PySide6.QtGui import QFont, QColor

# --- Constantes Globais ---
ALBUM_TITLE_TEMPLATE = "{manga_name} - Capítulo {chapter_name}"
ALBUM_DESCRIPTION_TEMPLATE = "Capítulo {chapter_name} de {manga_name}"
CATBOX_API_URL = "https://catbox.moe/user/api.php"
IMGUR_API_BASE_URL = "https://api.imgur.com/3/" # Para Imgur
DEFAULT_USERHASH = ""
DEFAULT_GROUP_NAME = "DefaultScanGroup"
DEFAULT_METADATA_OUTPUT_SUBDIR = "Manga_Metadata_Output"
MANGA_STATUS_OPTIONS = ["", "Em Andamento", "Concluído", "Hiato", "Cancelado", "Pausado"]
APP_VERSION = "0.9.14" # VERSÃO ATUALIZADA com estrutura para Host

# --- Função Auxiliar de Normalização ---
def normalize_for_comparison(text: str) -> str:
    if not isinstance(text, str):
        return ""
    return unicodedata.normalize('NFKC', text.strip())

# --- Sinais dos Workers ---
class WorkerSignals(QObject):
    overall_progress_setup = Signal(int)
    overall_progress_update = Signal(int, str)
    chapter_progress = Signal(str, int)
    finished = Signal(str, str)
    error = Signal(str)
    log_message = Signal(str)

class GitHubWorkerSignals(QObject):
    finished = Signal(str)
    error = Signal(str)
    log_message = Signal(str)

# --- Worker para Uploads Catbox (UploaderWorker existente) ---
class UploaderWorker(QThread):
    # ... (COLOQUE AQUI O CÓDIGO COMPLETO DA CLASSE UploaderWorker DA VERSÃO 0.9.13) ...
    # Certifique-se de que esta classe está completa e funcional como na v0.9.13
    def __init__(self, userhash, max_workers, rate_limit_delay,
                 manga_title_ui, manga_desc_ui, manga_artist_ui,
                 manga_author_ui, manga_cover_ui, manga_status_ui,
                 manga_base_path,
                 chapters_to_process_names, 
                 group_name_ui,
                 metadata_output_dir_base,
                 start_json_keys_at_zero):
        super().__init__()
        self.signals = WorkerSignals()
        self.userhash = userhash
        self.max_workers = max_workers
        self.rate_limit_delay = float(rate_limit_delay)
        self.manga_title_ui = manga_title_ui
        self.manga_desc_ui = manga_desc_ui
        self.manga_artist_ui = manga_artist_ui
        self.manga_author_ui = manga_author_ui
        self.manga_cover_ui = manga_cover_ui
        self.manga_status_ui = manga_status_ui
        self.manga_base_path = Path(manga_base_path)
        self.chapters_to_process_original_names = list(chapters_to_process_names)
        self.chapters_to_process_normalized_set = {normalize_for_comparison(name) for name in chapters_to_process_names}
        self.group_name_ui = group_name_ui.strip() if group_name_ui.strip() else DEFAULT_GROUP_NAME
        self.metadata_output_dir_base = Path(metadata_output_dir_base)
        self.start_json_keys_at_zero = start_json_keys_at_zero

    def _emit_log(self, message):
        self.signals.log_message.emit(message)

    @staticmethod
    def _sanitize_for_path(name: str, is_filename: bool = False) -> str:
        if not name: return "sem_titulo" if is_filename else "pasta_sem_nome"
        temp_name = name; 
        if is_filename: temp_name = temp_name.replace(" ", "_")
        temp_name = re.sub(r'[\\/*?:"<>|]', "", temp_name)
        if is_filename:
            base, dot, extension = temp_name.rpartition('.')
            if dot: base = base.strip("._ "); temp_name = (base if base else "arquivo_sem_nome") + dot + extension
            else: temp_name = temp_name.strip("._ ")
        else: temp_name = temp_name.strip("._ ")
        return temp_name if temp_name else ("sem_titulo" if is_filename else "pasta_sem_nome")

    @staticmethod
    def _natural_sort_key(s):
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

    def _upload_file_catbox(self, filepath):
        if not filepath.exists(): self._emit_log(f"ERRO: Arquivo não encontrado: {filepath}"); return None, f"Arquivo não encontrado: {filepath}"
        MAX_UPLOAD_RETRIES = 3; RETRY_DELAY_SECONDS = 5; last_exception_str = "N/A"
        for attempt in range(MAX_UPLOAD_RETRIES):
            try:
                if attempt > 0: self._emit_log(f"Tentativa {attempt+1}/{MAX_UPLOAD_RETRIES} para {filepath.name} ({RETRY_DELAY_SECONDS}s espera...)"); time.sleep(RETRY_DELAY_SECONDS)
                self._emit_log(f"Upload {filepath.name} (tentativa {attempt+1}/{MAX_UPLOAD_RETRIES})...");
                with open(filepath, "rb") as f: files={"fileToUpload":f}; data={"reqtype":"fileupload","userhash":self.userhash}; response=requests.post(CATBOX_API_URL,data=data,files=files,timeout=300); response.raise_for_status()
                self._emit_log(f"Sucesso upload {filepath.name} ({attempt+1}). URL: {response.text}"); return response.text, None
            except requests.exceptions.RequestException as e: last_exception_str=str(e); self._emit_log(f"Falha rede/servidor {attempt+1}/{MAX_UPLOAD_RETRIES} ({filepath.name}): {e}")
            except Exception as e: last_exception_str=str(e); self._emit_log(f"Erro inesperado {attempt+1}/{MAX_UPLOAD_RETRIES} ({filepath.name}): {e}")
        self._emit_log(f"Falha upload {filepath.name} ({MAX_UPLOAD_RETRIES} tentativas). Erro: {last_exception_str}"); return None, f"Falha após {MAX_UPLOAD_RETRIES} tentativas: {last_exception_str}"

    def _create_album_catbox(self, title, description, file_ids):
        if not file_ids: self._emit_log(f"Nenhum ID para criar álbum: {title}"); return None
        data = {"reqtype": "createalbum", "userhash": self.userhash, "title": title, "desc": description, "files": " ".join(file_ids)}
        try: response = requests.post(CATBOX_API_URL, data=data, timeout=120); response.raise_for_status(); return response.text
        except Exception as e: self._emit_log(f"Erro ao criar álbum '{title}': {e}"); return None

    def _parallel_upload_files(self, ordered_image_filenames, chapter_path: Path):
        upload_results_map = {}; image_file_ids_for_album = []; failures_log = []
        total_files = len(ordered_image_filenames)
        def process_file_with_delay(filename_str: str):
            if self.rate_limit_delay > 0: time.sleep(self.rate_limit_delay)
            filepath = chapter_path / filename_str; uploaded_url, error = self._upload_file_catbox(filepath)
            return filename_str, uploaded_url, error
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(process_file_with_delay, fn): fn for fn in ordered_image_filenames}
            processed_count = 0
            for future in concurrent.futures.as_completed(futures):
                original_filename, uploaded_url, error = future.result(); processed_count += 1
                progress_percentage = int((processed_count / total_files) * 100)
                self.signals.chapter_progress.emit(f"Cap. {chapter_path.name}: {original_filename} ({processed_count}/{total_files})", progress_percentage)
                if uploaded_url: upload_results_map[original_filename] = uploaded_url; image_file_ids_for_album.append(uploaded_url.split("/")[-1])
                else: upload_results_map[original_filename] = None; failures_log.append((original_filename, error)); 
        direct_image_urls_ordered = [upload_results_map.get(fn) for fn in ordered_image_filenames if upload_results_map.get(fn)]
        if failures_log: self._emit_log(f"{len(failures_log)} uploads falharam definitivamente para o capítulo '{chapter_path.name}'.")
        return image_file_ids_for_album, direct_image_urls_ordered

    def _process_manga_chapter(self, manga_title_for_album_template, chapter_path: Path):
        chapter_name_original = chapter_path.name
        self._emit_log(f"Processando cap: {chapter_name_original}")
        self.signals.chapter_progress.emit(f"Iniciando: {chapter_name_original}", 0)

        if not chapter_path.is_dir():
            self._emit_log(f"Pasta '{chapter_name_original}' ({chapter_path}) não é um diretório válido.")
            return None, None, chapter_name_original

        ordered_image_filenames = sorted(
            [f.name for f in chapter_path.iterdir() if f.is_file() and f.name.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))],
            key=UploaderWorker._natural_sort_key
        )

        if not ordered_image_filenames:
            self._emit_log(f"Nenhuma imagem encontrada em '{chapter_name_original}'.")
            return None, None, chapter_name_original

        self._emit_log(f"{len(ordered_image_filenames)} imagens encontradas em '{chapter_name_original}'.")
        image_file_ids_for_album, direct_image_urls_ordered = self._parallel_upload_files(ordered_image_filenames, chapter_path)

        if not direct_image_urls_ordered:
            self._emit_log(f"Nenhuma imagem foi enviada com sucesso para '{chapter_name_original}'.")
            self.signals.chapter_progress.emit(f"Falha no upload: {chapter_name_original}", 100)
            return "", [], chapter_name_original

        album_url = ""
        if image_file_ids_for_album:
            album_title = ALBUM_TITLE_TEMPLATE.format(manga_name=manga_title_for_album_template, chapter_name=chapter_name_original)
            album_description = ALBUM_DESCRIPTION_TEMPLATE.format(manga_name=manga_title_for_album_template, chapter_name=chapter_name_original)
            self._emit_log(f"Criando álbum para '{chapter_name_original}'...")
            self.signals.chapter_progress.emit(f"Criando álbum: {chapter_name_original}", 99)
            album_url_result = self._create_album_catbox(album_title, album_description, image_file_ids_for_album)
            if album_url_result:
                self._emit_log(f"Álbum criado com sucesso: {album_url_result}")
                album_url = album_url_result
            else:
                self._emit_log(f"Falha ao criar álbum para '{chapter_name_original}'. Álbum URL estará vazio.")
        else:
            self._emit_log(f"Nenhum ID de arquivo de imagem para criar álbum de '{chapter_name_original}'.")

        self.signals.chapter_progress.emit(f"Cap. {chapter_name_original} finalizado.", 100)
        return album_url, direct_image_urls_ordered, chapter_name_original

    def run(self):
        try:
            manga_title_for_paths = self.manga_title_ui
            sanitized_manga_foldername = UploaderWorker._sanitize_for_path(manga_title_for_paths, is_filename=False)
            sanitized_manga_filename_base = UploaderWorker._sanitize_for_path(manga_title_for_paths, is_filename=True)
            
            manga_output_folder = self.metadata_output_dir_base / sanitized_manga_foldername
            manga_output_folder.mkdir(parents=True, exist_ok=True)
            output_json_file_path = manga_output_folder / f"{sanitized_manga_filename_base}.json"
            output_yaml_file_path = manga_output_folder / f"{sanitized_manga_filename_base}.yaml"

            cubari_data_loaded = {}
            if output_json_file_path.exists():
                try:
                    with open(output_json_file_path, "r", encoding="utf-8") as f:
                        cubari_data_loaded = json.load(f)
                    self._emit_log(f"Arquivo JSON existente carregado: {output_json_file_path}")
                except Exception as e:
                    self._emit_log(f"Erro ao ler JSON existente ({output_json_file_path}): {e}. Um novo JSON será criado.")
            
            all_chapters_by_original_title = {} 
            existing_chapters_from_json_data = cubari_data_loaded.get("chapters", {})

            for old_numeric_key, old_chap_data in existing_chapters_from_json_data.items():
                title_from_json_original = old_chap_data.get("title", old_numeric_key)
                title_from_json_normalized = normalize_for_comparison(title_from_json_original)

                if not title_from_json_normalized:
                    self._emit_log(f"Aviso: Capítulo com chave '{old_numeric_key}' no JSON existente ('{title_from_json_original}') tem título vazio ou inválido após normalização. Será ignorado na preservação.")
                    continue
                
                if title_from_json_normalized not in self.chapters_to_process_normalized_set:
                    all_chapters_by_original_title[title_from_json_original] = old_chap_data
            
            ordered_chapters_to_process_original_names = sorted(
                self.chapters_to_process_original_names,
                key=UploaderWorker._natural_sort_key
            )

            total_chapters_to_process = len(ordered_chapters_to_process_original_names)
            self.signals.overall_progress_setup.emit(total_chapters_to_process)
            self._emit_log(f"Processando {total_chapters_to_process} capítulos selecionados para '{self.manga_base_path.name}'.")
            
            yaml_chapters_this_run_numeric_keys = {}

            for current_process_idx, chapter_folder_name_original in enumerate(ordered_chapters_to_process_original_names, start=1):
                self.signals.overall_progress_update.emit(current_process_idx, chapter_folder_name_original)
                chapter_actual_path = self.manga_base_path / chapter_folder_name_original
                
                self._emit_log(f"--- Processando Cap {current_process_idx}/{total_chapters_to_process}: {chapter_folder_name_original} ---")
                
                if not chapter_actual_path.is_dir():
                    self._emit_log(f"Pasta '{chapter_folder_name_original}' não encontrada ou não é um diretório. Pulando.")
                    continue

                album_url_result, direct_image_urls_ordered_result, processed_chapter_original_name = \
                    self._process_manga_chapter(self.manga_base_path.name, chapter_actual_path)
                
                timestamp = str(int(time.time()))

                if direct_image_urls_ordered_result:
                    existing_volume_info = ""
                    if processed_chapter_original_name in all_chapters_by_original_title and "volume" in all_chapters_by_original_title[processed_chapter_original_name]:
                         existing_volume_info = all_chapters_by_original_title[processed_chapter_original_name].get("volume", "")
                    else: 
                        for _, chap_data_loaded in existing_chapters_from_json_data.items():
                            if normalize_for_comparison(chap_data_loaded.get("title", "")) == normalize_for_comparison(processed_chapter_original_name):
                                existing_volume_info = chap_data_loaded.get("volume", "")
                                break
                    
                    all_chapters_by_original_title[processed_chapter_original_name] = {
                        "title": processed_chapter_original_name,
                        "volume": existing_volume_info,
                        "last_updated": timestamp,
                        "groups": {self.group_name_ui: direct_image_urls_ordered_result}
                    }
                    
                    yaml_numeric_key_for_this_run = f"{current_process_idx:03d}" 
                    yaml_chapters_this_run_numeric_keys[yaml_numeric_key_for_this_run] = {
                        "title": processed_chapter_original_name,
                        "volume": existing_volume_info,
                        "groups": {self.group_name_ui: album_url_result if album_url_result else ""}
                    }
                    self._emit_log(f"Dados de '{processed_chapter_original_name}' atualizados/adicionados.")
                else:
                    self._emit_log(f"Nenhuma imagem processada com sucesso para '{processed_chapter_original_name}'. Não será incluído nos metadados.")

            final_ordered_original_titles = sorted(
                list(all_chapters_by_original_title.keys()),
                key=UploaderWorker._natural_sort_key
            )
            
            final_chapters_json_object = {}
            start_index_for_json_keys = 0 if self.start_json_keys_at_zero else 1
            for i, original_title_key in enumerate(final_ordered_original_titles, start=start_index_for_json_keys):
                numeric_key_str = f"{i:03d}"
                final_chapters_json_object[numeric_key_str] = all_chapters_by_original_title[original_title_key]
            
            final_cubari_data = {
                "title": self.manga_title_ui,
                "description": self.manga_desc_ui,
                "artist": self.manga_artist_ui,
                "author": self.manga_author_ui,
                "cover": self.manga_cover_ui,
                "status": self.manga_status_ui,
                "chapters": final_chapters_json_object
            }

            with open(output_json_file_path, "w", encoding="utf-8") as f:
                json.dump(final_cubari_data, f, indent=2, ensure_ascii=False)
            self._emit_log(f"Arquivo JSON salvo com sucesso: {output_json_file_path}")

            final_yaml_data_to_save = {
                "title": final_cubari_data["title"],
                "description": final_cubari_data["description"],
                "artist": final_cubari_data["artist"],
                "author": final_cubari_data["author"],
                "cover": final_cubari_data["cover"],
                "status": final_cubari_data["status"],
                "chapters": yaml_chapters_this_run_numeric_keys
            }
            with open(output_yaml_file_path, "w", encoding="utf-8") as f:
                yaml.dump(final_yaml_data_to_save, f, sort_keys=False, allow_unicode=True, Dumper=getattr(yaml, 'SafeDumper', yaml.Dumper))
            self._emit_log(f"Arquivo YAML de resumo salvo: {output_yaml_file_path}")

            self.signals.finished.emit(str(output_json_file_path), str(output_yaml_file_path))
        except Exception as e:
            error_msg = f"Erro GERAL no worker de upload: {e}\n{traceback.format_exc()}"
            self._emit_log(error_msg)
            self.signals.error.emit(error_msg)

# --- Esqueleto do Worker para Imgur ---
class ImgurUploaderWorker(QThread):
    signals = WorkerSignals() # Pode reutilizar os mesmos sinais

    def __init__(self, client_id, # Credenciais Imgur
                 max_workers, rate_limit_delay,
                 manga_title_ui, manga_desc_ui, manga_artist_ui,
                 manga_author_ui, manga_cover_ui, manga_status_ui,
                 manga_base_path,
                 chapters_to_process_names,
                 group_name_ui,
                 metadata_output_dir_base,
                 start_json_keys_at_zero,
                 # Adicionar outros parâmetros específicos do Imgur se necessário (ex: access_token)
                 imgur_access_token=None):
        super().__init__()
        self.signals = WorkerSignals()
        self.client_id = client_id
        self.imgur_access_token = imgur_access_token # Para uploads autenticados / criação de álbuns
        self.max_workers = max_workers
        self.rate_limit_delay = float(rate_limit_delay)
        self.manga_title_ui = manga_title_ui
        self.manga_desc_ui = manga_desc_ui
        self.manga_artist_ui = manga_artist_ui
        self.manga_author_ui = manga_author_ui
        self.manga_cover_ui = manga_cover_ui
        self.manga_status_ui = manga_status_ui
        self.manga_base_path = Path(manga_base_path)
        self.chapters_to_process_original_names = list(chapters_to_process_names)
        self.chapters_to_process_normalized_set = {normalize_for_comparison(name) for name in chapters_to_process_names}
        self.group_name_ui = group_name_ui.strip() if group_name_ui.strip() else DEFAULT_GROUP_NAME
        self.metadata_output_dir_base = Path(metadata_output_dir_base)
        self.start_json_keys_at_zero = start_json_keys_at_zero

        # Para armazenar informações de rate limit do Imgur
        self.imgur_user_limit = None
        self.imgur_user_remaining = None
        self.imgur_user_reset = None # Timestamp Unix
        self.imgur_client_limit = None
        self.imgur_client_remaining = None


    def _emit_log(self, message):
        self.signals.log_message.emit(f"[Imgur] {message}")

    @staticmethod
    def _natural_sort_key(s):
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

    @staticmethod
    def _sanitize_for_path(name: str, is_filename: bool = False) -> str:
        # Reutilizar a mesma função de sanitização
        return UploaderWorker._sanitize_for_path(name, is_filename)

    def _update_rate_limits_from_response(self, response_headers):
        try:
            self.imgur_user_limit = int(response_headers.get('X-RateLimit-UserLimit', self.imgur_user_limit))
            self.imgur_user_remaining = int(response_headers.get('X-RateLimit-UserRemaining', self.imgur_user_remaining))
            self.imgur_user_reset = int(response_headers.get('X-RateLimit-UserReset', self.imgur_user_reset))
            self.imgur_client_limit = int(response_headers.get('X-RateLimit-ClientLimit', self.imgur_client_limit))
            self.imgur_client_remaining = int(response_headers.get('X-RateLimit-ClientRemaining', self.imgur_client_remaining))
            # self._emit_log(f"Limites Imgur: User Rem={self.imgur_user_remaining}/{self.imgur_user_limit}, Client Rem={self.imgur_client_remaining}/{self.imgur_client_limit}, Reset em {self.imgur_user_reset}")
        except (TypeError, ValueError) as e:
            self._emit_log(f"Aviso: Não foi possível analisar cabeçalhos de rate limit do Imgur: {e}")


    def _upload_file_imgur(self, filepath):
        self._emit_log(f"Upload Imgur (NÃO TOTALMENTE IMPLEMENTADO): {filepath.name}")
        if not self.client_id:
            return None, "Client ID do Imgur não configurado."

        # Verificar limites de taxa antes de tentar (simplificado)
        if self.imgur_client_remaining is not None and self.imgur_client_remaining < 5: # Deixar uma margem
            wait_time = (self.imgur_user_reset - time.time()) if self.imgur_user_reset else 60
            if wait_time > 0:
                self._emit_log(f"Limite de taxa Imgur baixo. Esperando {int(wait_time)}s...")
                time.sleep(wait_time)
            # Re-verificar limites seria ideal aqui, mas simplificando por agora.

        headers = {'Authorization': f'Client-ID {self.client_id}'}
        if self.imgur_access_token: # Se tiver um token de acesso (OAuth2)
             headers['Authorization'] = f'Bearer {self.imgur_access_token}'

        MAX_UPLOAD_RETRIES = 2
        RETRY_DELAY_SECONDS = 10 
        last_exception_str = "N/A"

        for attempt in range(MAX_UPLOAD_RETRIES):
            try:
                if attempt > 0:
                    self._emit_log(f"Tentativa Imgur {attempt+1}/{MAX_UPLOAD_RETRIES} para {filepath.name} ({RETRY_DELAY_SECONDS}s espera...)")
                    time.sleep(RETRY_DELAY_SECONDS * (attempt + 1)) # Backoff simples

                with open(filepath, "rb") as f_img:
                    files = {'image': f_img}
                    # Você pode adicionar 'title' e 'description' ao payload se desejar
                    # payload = {'title': 'Meu Título', 'description': 'Minha Descrição'}
                    response = requests.post(f"{IMGUR_API_BASE_URL}image", headers=headers, files=files, timeout=300) # data=payload

                self._update_rate_limits_from_response(response.headers)

                if response.status_code == 429: # Too Many Requests
                    retry_after = response.headers.get('Retry-After')
                    reset_time = self.imgur_user_reset if self.imgur_user_reset else (time.time() + 60) # Fallback
                    wait_duration = int(retry_after) if retry_after else (reset_time - time.time())
                    wait_duration = max(5, int(wait_duration)) # Esperar pelo menos 5s
                    self._emit_log(f"Limite de taxa Imgur atingido ({response.status_code}). Esperando {wait_duration}s. ({filepath.name})")
                    time.sleep(wait_duration)
                    # Não conta como uma tentativa "falha" no loop, mas continua para a próxima tentativa se houver.
                    # Ou você pode querer ter uma lógica de retry mais sofisticada aqui.
                    if attempt < MAX_UPLOAD_RETRIES -1 : continue # Tenta novamente após a espera
                    else: last_exception_str = f"Limite de taxa atingido após {MAX_UPLOAD_RETRIES} tentativas."; break


                response.raise_for_status() # Levanta exceção para outros erros HTTP

                data = response.json()
                if data.get('success') and data.get('data', {}).get('link'):
                    img_link = data['data']['link']
                    # img_id = data['data']['id'] # Útil para álbuns
                    # delete_hash = data['data']['deletehash'] # Útil para deletar
                    self._emit_log(f"Sucesso upload Imgur {filepath.name}. URL: {img_link}")
                    return img_link, None
                else:
                    last_exception_str = f"Resposta Imgur não esperada: {data.get('data', {}).get('error', 'Erro desconhecido na resposta')}"
                    self._emit_log(f"Falha upload Imgur {filepath.name}: {last_exception_str}")
                    break # Sai do loop de retries se a resposta não for de sucesso

            except requests.exceptions.RequestException as e:
                last_exception_str = str(e)
                self._emit_log(f"Falha rede/servidor Imgur {attempt+1}/{MAX_UPLOAD_RETRIES} ({filepath.name}): {e}")
            except Exception as e:
                last_exception_str = str(e)
                self._emit_log(f"Erro inesperado Imgur {attempt+1}/{MAX_UPLOAD_RETRIES} ({filepath.name}): {e}")
        
        return None, f"Falha Imgur após {MAX_UPLOAD_RETRIES} tentativas: {last_exception_str}"


    def _create_album_imgur(self, title, description, image_ids):
        self._emit_log(f"Criar álbum Imgur (NÃO IMPLEMENTADO COMPLETAMENTE): {title}")
        if not self.imgur_access_token: # Criar álbuns geralmente requer OAuth2
            self._emit_log("Criação de álbum no Imgur requer autenticação de usuário (OAuth2). Pulando.")
            return None
        if not image_ids:
            self._emit_log("Nenhum ID de imagem para criar álbum Imgur.")
            return None

        headers = {'Authorization': f'Bearer {self.imgur_access_token}'}
        payload = {
            'ids[]': image_ids, # Lista de IDs de imagem
            'title': title,
            'description': description
            # 'privacy': 'hidden', # ou 'public', 'secret'
            # 'cover': image_ids[0] # ID de uma das imagens para ser a capa
        }
        try:
            response = requests.post(f"{IMGUR_API_BASE_URL}album", headers=headers, data=payload, timeout=120)
            self._update_rate_limits_from_response(response.headers)
            response.raise_for_status()
            data = response.json()
            if data.get('success') and data.get('data', {}).get('id'):
                album_id = data['data']['id']
                album_link = f"https://imgur.com/a/{album_id}"
                self._emit_log(f"Álbum Imgur criado: {album_link}")
                return album_link
            else:
                self._emit_log(f"Falha ao criar álbum Imgur: {data.get('data', {}).get('error', 'Erro desconhecido na resposta')}")
                return None
        except Exception as e:
            self._emit_log(f"Erro ao criar álbum Imgur '{title}': {e}")
            return None

    def _parallel_upload_files(self, ordered_image_filenames, chapter_path: Path):
        upload_results_map = {}
        image_ids_for_album = [] # Para Imgur, são IDs/hashes, não URLs
        failures_log = []
        total_files = len(ordered_image_filenames)

        def process_file_with_delay(filename_str: str):
            if self.rate_limit_delay > 0: time.sleep(self.rate_limit_delay) # Delay geral entre inícios de upload
            filepath = chapter_path / filename_str
            uploaded_url, error = self._upload_file_imgur(filepath) # Chama a função de upload do Imgur
            # Para criar álbuns no Imgur, _upload_file_imgur precisaria retornar o ID da imagem também.
            # Por agora, vamos assumir que a URL é suficiente e não tentaremos criar álbuns complexos.
            image_id_placeholder = uploaded_url.split('/')[-1].split('.')[0] if uploaded_url else None
            return filename_str, uploaded_url, image_id_placeholder, error

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(process_file_with_delay, fn): fn for fn in ordered_image_filenames}
            processed_count = 0
            for future in concurrent.futures.as_completed(futures):
                original_filename, uploaded_url, image_id, error = future.result()
                processed_count += 1
                progress_percentage = int((processed_count / total_files) * 100)
                self.signals.chapter_progress.emit(f"Cap. {chapter_path.name} (Imgur): {original_filename} ({processed_count}/{total_files})", progress_percentage)
                if uploaded_url:
                    upload_results_map[original_filename] = uploaded_url
                    if image_id and self.imgur_access_token: # Só coletar IDs se formos tentar criar álbum autenticado
                         image_ids_for_album.append(image_id)
                else:
                    upload_results_map[original_filename] = None
                    failures_log.append((original_filename, error))
        
        direct_image_urls_ordered = [upload_results_map.get(fn) for fn in ordered_image_filenames if upload_results_map.get(fn)]
        if failures_log:
            self._emit_log(f"{len(failures_log)} uploads Imgur falharam para o capítulo '{chapter_path.name}'.")
        
        return image_ids_for_album, direct_image_urls_ordered


    def _process_manga_chapter(self, manga_title_for_album_template, chapter_path: Path):
        chapter_name_original = chapter_path.name # Nome original da pasta
        self._emit_log(f"Processando capítulo para Imgur: {chapter_name_original}")
        self.signals.chapter_progress.emit(f"Iniciando (Imgur): {chapter_name_original}", 0)

        if not chapter_path.is_dir():
            self._emit_log(f"Pasta '{chapter_name_original}' não é um diretório. Pulando.")
            return None, None, chapter_name_original

        ordered_image_filenames = sorted(
            [f.name for f in chapter_path.iterdir() if f.is_file() and f.name.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))],
            key=ImgurUploaderWorker._natural_sort_key # Usar o método estático da classe
        )

        if not ordered_image_filenames:
            self._emit_log(f"Nenhuma imagem encontrada em '{chapter_name_original}'.")
            return None, None, chapter_name_original

        self._emit_log(f"{len(ordered_image_filenames)} imagens encontradas em '{chapter_name_original}' para upload no Imgur.")
        
        image_ids_uploaded, direct_image_urls_ordered = self._parallel_upload_files(ordered_image_filenames, chapter_path)

        if not direct_image_urls_ordered:
            self._emit_log(f"Nenhuma imagem foi enviada com sucesso para '{chapter_name_original}' (Imgur).")
            self.signals.chapter_progress.emit(f"Falha no upload (Imgur): {chapter_name_original}", 100)
            return "", [], chapter_name_original

        album_url = ""
        # Tentar criar álbum no Imgur APENAS se tivermos um access token (OAuth2) e IDs de imagem
        if self.imgur_access_token and image_ids_uploaded:
            album_title = ALBUM_TITLE_TEMPLATE.format(manga_name=manga_title_for_album_template, chapter_name=chapter_name_original)
            album_description = ALBUM_DESCRIPTION_TEMPLATE.format(manga_name=manga_title_for_album_template, chapter_name=chapter_name_original)
            self._emit_log(f"Tentando criar álbum no Imgur para '{chapter_name_original}'...")
            self.signals.chapter_progress.emit(f"Criando álbum Imgur: {chapter_name_original}", 99)
            album_url_result = self._create_album_imgur(album_title, album_description, image_ids_uploaded)
            if album_url_result:
                album_url = album_url_result
            else:
                self._emit_log(f"Falha ao criar álbum Imgur para '{chapter_name_original}'. Usando links diretos.")
        elif image_ids_uploaded: # Se não há token mas há IDs (improvável para Imgur, mas por segurança)
            self._emit_log(f"IDs de imagem Imgur obtidos, mas sem Access Token para criar álbum autenticado para '{chapter_name_original}'.")


        self.signals.chapter_progress.emit(f"Cap. {chapter_name_original} (Imgur) finalizado.", 100)
        # Retorna o nome original da pasta, que será usado como chave e no campo "title" do JSON.
        return album_url, direct_image_urls_ordered, chapter_name_original

    def run(self):
        # ESTA É UMA CÓPIA ADAPTADA DO UploaderWorker.run()
        # Garanta que as chamadas de método e logs reflitam o Imgur.
        try:
            manga_title_for_paths = self.manga_title_ui
            sanitized_manga_foldername = ImgurUploaderWorker._sanitize_for_path(manga_title_for_paths, is_filename=False) # Usar o método da classe
            sanitized_manga_filename_base = ImgurUploaderWorker._sanitize_for_path(manga_title_for_paths, is_filename=True)
            
            manga_output_folder = self.metadata_output_dir_base / sanitized_manga_foldername
            manga_output_folder.mkdir(parents=True, exist_ok=True)
            # Nome do arquivo JSON para Imgur pode ser diferente para evitar sobrescrever o do Catbox
            output_json_file_path = manga_output_folder / f"{sanitized_manga_filename_base}_imgur.json"
            output_yaml_file_path = manga_output_folder / f"{sanitized_manga_filename_base}_imgur.yaml"

            cubari_data_loaded = {}
            if output_json_file_path.exists(): # Procura por um JSON específico do Imgur
                try:
                    with open(output_json_file_path, "r", encoding="utf-8") as f:
                        cubari_data_loaded = json.load(f)
                    self._emit_log(f"Arquivo JSON (Imgur) existente carregado: {output_json_file_path}")
                except Exception as e:
                    self._emit_log(f"Erro ao ler JSON (Imgur) existente ({output_json_file_path}): {e}.")
            
            all_chapters_by_original_title = {}
            existing_chapters_from_json_data = cubari_data_loaded.get("chapters", {})

            for old_numeric_key, old_chap_data in existing_chapters_from_json_data.items():
                title_from_json_original = old_chap_data.get("title", old_numeric_key)
                title_from_json_normalized = normalize_for_comparison(title_from_json_original)
                if not title_from_json_normalized: continue
                if title_from_json_normalized not in self.chapters_to_process_normalized_set:
                    all_chapters_by_original_title[title_from_json_original] = old_chap_data
            
            ordered_chapters_to_process_original_names = sorted(
                self.chapters_to_process_original_names,
                key=ImgurUploaderWorker._natural_sort_key
            )

            total_chapters_to_process = len(ordered_chapters_to_process_original_names)
            self.signals.overall_progress_setup.emit(total_chapters_to_process)
            self._emit_log(f"Processando {total_chapters_to_process} caps para '{self.manga_base_path.name}' (via Imgur).")
            
            yaml_chapters_this_run_numeric_keys = {}

            for current_process_idx, chapter_folder_name_original in enumerate(ordered_chapters_to_process_original_names, start=1):
                self.signals.overall_progress_update.emit(current_process_idx, chapter_folder_name_original)
                chapter_actual_path = self.manga_base_path / chapter_folder_name_original
                self._emit_log(f"--- Processando Cap (Imgur) {current_process_idx}/{total_chapters_to_process}: {chapter_folder_name_original} ---")
                
                if not chapter_actual_path.is_dir(): continue

                album_url_result, direct_image_urls_ordered_result, processed_chapter_original_name = \
                    self._process_manga_chapter(self.manga_base_path.name, chapter_actual_path)
                
                timestamp = str(int(time.time()))
                if direct_image_urls_ordered_result:
                    existing_volume_info = ""
                    # ... (lógica para obter existing_volume_info, similar ao UploaderWorker)
                    if processed_chapter_original_name in all_chapters_by_original_title and "volume" in all_chapters_by_original_title[processed_chapter_original_name]:
                         existing_volume_info = all_chapters_by_original_title[processed_chapter_original_name].get("volume", "")
                    else: 
                        for _, chap_data_loaded in existing_chapters_from_json_data.items(): # Usa existing_chapters_from_json_data
                            if normalize_for_comparison(chap_data_loaded.get("title", "")) == normalize_for_comparison(processed_chapter_original_name):
                                existing_volume_info = chap_data_loaded.get("volume", "")
                                break

                    all_chapters_by_original_title[processed_chapter_original_name] = {
                        "title": processed_chapter_original_name, "volume": existing_volume_info,
                        "last_updated": timestamp,
                        "groups": {self.group_name_ui: (album_url_result if album_url_result else direct_image_urls_ordered_result)} # Prefere álbum se existir
                    }
                    yaml_numeric_key_for_this_run = f"{current_process_idx:03d}"
                    yaml_chapters_this_run_numeric_keys[yaml_numeric_key_for_this_run] = {
                        "title": processed_chapter_original_name, "volume": existing_volume_info,
                        "groups": {self.group_name_ui: album_url_result if album_url_result else ""}
                    }
                    self._emit_log(f"Dados (Imgur) de '{processed_chapter_original_name}' atualizados.")
                else:
                    self._emit_log(f"Nenhuma imagem (Imgur) processada para '{processed_chapter_original_name}'.")

            final_ordered_original_titles = sorted(list(all_chapters_by_original_title.keys()), key=ImgurUploaderWorker._natural_sort_key)
            final_chapters_json_object = {}
            start_index_for_json_keys = 0 if self.start_json_keys_at_zero else 1
            for i, original_title_key in enumerate(final_ordered_original_titles, start=start_index_for_json_keys):
                numeric_key_str = f"{i:03d}"
                final_chapters_json_object[numeric_key_str] = all_chapters_by_original_title[original_title_key]
            
            final_cubari_data = {
                "title": self.manga_title_ui, "description": self.manga_desc_ui,
                "artist": self.manga_artist_ui, "author": self.manga_author_ui,
                "cover": self.manga_cover_ui, "status": self.manga_status_ui,
                "chapters": final_chapters_json_object
            }

            with open(output_json_file_path, "w", encoding="utf-8") as f: json.dump(final_cubari_data, f, indent=2, ensure_ascii=False)
            self._emit_log(f"Arquivo JSON (Imgur) salvo: {output_json_file_path}")
            
            final_yaml_data_to_save = { # YAML para Imgur
                "title": final_cubari_data["title"], "description": final_cubari_data["description"],
                "artist": final_cubari_data["artist"], "author": final_cubari_data["author"],
                "cover": final_cubari_data["cover"], "status": final_cubari_data["status"],
                "chapters": yaml_chapters_this_run_numeric_keys
            }
            with open(output_yaml_file_path, "w", encoding="utf-8") as f: yaml.dump(final_yaml_data_to_save, f, sort_keys=False, allow_unicode=True, Dumper=getattr(yaml, 'SafeDumper', yaml.Dumper))
            self._emit_log(f"Arquivo YAML (Imgur) salvo: {output_yaml_file_path}")

            self.signals.finished.emit(str(output_json_file_path), str(output_yaml_file_path))
        except Exception as e:
            error_msg = f"Erro GERAL no ImgurUploaderWorker: {e}\n{traceback.format_exc()}"
            self._emit_log(error_msg)
            self.signals.error.emit(error_msg)


# --- Janela Principal da GUI ---
class CatboxUploaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Mangá Uploader GUI v{APP_VERSION}") # Nome genérico
        self.setGeometry(100, 100, 950, 880)
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.upload_tab = QWidget()
        self.host_tab = QWidget() # Nova aba Host
        self.settings_tab = QWidget()
        self.log_tab = QWidget()

        self.tab_widget.addTab(self.upload_tab, "Upload de Mangá")
        self.tab_widget.addTab(self.host_tab, "Host") # Adicionada
        self.tab_widget.addTab(self.settings_tab, "Configurações")
        self.tab_widget.addTab(self.log_tab, "Log da Aplicação")

        self._create_upload_ui()
        self._create_host_ui() # Criar UI para nova aba
        self._create_settings_ui()
        self._create_log_ui()

        self.current_uploader_worker = None # Para Catbox ou Imgur worker
        self.github_worker = None
        self.last_saved_json_path = None
        
        self.selected_host = "Catbox" # Valor padrão
        self._load_app_settings() # Isso também chamará _update_host_specific_settings_visibility

    @staticmethod
    def _natural_sort_key(s): return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)]

    @staticmethod
    def _sanitize_for_path(name: str, is_filename: bool=False) -> str:
        return UploaderWorker._sanitize_for_path(name, is_filename) # Reutiliza o método estático

    def _create_upload_ui(self):
        # ... (código original de _create_upload_ui, sem alterações) ...
        scroll_area = QScrollArea(); scroll_area.setWidgetResizable(True)
        self.upload_tab.setLayout(QVBoxLayout()); self.upload_tab.layout().addWidget(scroll_area)
        upload_widget_internal = QWidget(); layout = QVBoxLayout(upload_widget_internal)
        manga_selection_group = QGroupBox("1. Selecionar Pasta do Mangá"); manga_selection_layout = QVBoxLayout()
        self.current_root_folder_display = QLineEdit(); self.current_root_folder_display.setReadOnly(True); self.current_root_folder_display.setPlaceholderText("Defina a Pasta Raiz na aba 'Configurações'")
        manga_selection_layout.addWidget(QLabel("Pasta Raiz Atual (de 'Configurações'):")); manga_selection_layout.addWidget(self.current_root_folder_display)
        self.btn_refresh_mangas_upload_tab = QPushButton("Atualizar Lista de Mangás da Pasta Raiz"); self.btn_refresh_mangas_upload_tab.clicked.connect(self.populate_manga_list)
        manga_selection_layout.addWidget(self.btn_refresh_mangas_upload_tab)
        manga_selection_layout.addWidget(QLabel("Mangás Encontrados (dê um duplo clique para selecionar):"))
        self.manga_list_widget = QListWidget(); self.manga_list_widget.itemDoubleClicked.connect(self.manga_item_double_clicked)
        manga_selection_layout.addWidget(self.manga_list_widget); manga_selection_group.setLayout(manga_selection_layout); layout.addWidget(manga_selection_group)
        chapters_detected_group = QGroupBox("Capítulos Detectados no Mangá Selecionado (selecione os que deseja processar)"); chapters_layout = QVBoxLayout()
        self.chapters_list_widget = QListWidget(); self.chapters_list_widget.setStyleSheet("background-color: #2e3338; color: #f0f0f0;")
        self.chapters_list_widget.setFixedHeight(150); self.chapters_list_widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection); self.chapters_list_widget.setToolTip("Selecione um ou mais capítulos. Use Ctrl+Clique ou Shift+Clique.")
        chapters_layout.addWidget(self.chapters_list_widget); chapters_detected_group.setLayout(chapters_layout); layout.addWidget(chapters_detected_group)
        metadata_group = QGroupBox("2. Metadados do Mangá (para os arquivos de saída)"); metadata_outer_layout = QVBoxLayout()
        metadata_top_layout = QHBoxLayout(); metadata_form_left = QFormLayout()
        self.manga_title_input = QLineEdit(); self.manga_title_input.setPlaceholderText("Nome da pasta do mangá"); self.manga_title_input.setReadOnly(True)
        self.manga_artist_input = QLineEdit(); self.manga_artist_input.setPlaceholderText("Ex: SIU")
        self.manga_author_input = QLineEdit(); self.manga_author_input.setPlaceholderText("Ex: SIU")
        self.manga_status_input = QComboBox(); self.manga_status_input.addItems(MANGA_STATUS_OPTIONS)
        self.manga_cover_input = QLineEdit(); self.manga_cover_input.setPlaceholderText("URL direta da imagem de capa")
        self.group_name_input = QLineEdit(DEFAULT_GROUP_NAME); self.group_name_input.setPlaceholderText("Nome do grupo/scan")
        metadata_form_left.addRow("Título do Mangá (Nome da Pasta):", self.manga_title_input); metadata_form_left.addRow("Artista:", self.manga_artist_input); metadata_form_left.addRow("Autor:", self.manga_author_input); metadata_form_left.addRow("Status do Mangá:", self.manga_status_input); metadata_form_left.addRow("URL da Capa:", self.manga_cover_input); metadata_form_left.addRow("Nome do Grupo (JSON/YAML):", self.group_name_input)
        metadata_top_layout.addLayout(metadata_form_left, 1); metadata_form_right = QVBoxLayout()
        metadata_form_right.addWidget(QLabel("Descrição do Mangá:")); self.manga_description_input = QTextEdit(); self.manga_description_input.setPlaceholderText("Sinopse..."); self.manga_description_input.setMinimumHeight(130)
        metadata_form_right.addWidget(self.manga_description_input); metadata_top_layout.addLayout(metadata_form_right, 1)
        metadata_outer_layout.addLayout(metadata_top_layout); self.btn_load_json = QPushButton("Carregar Metadados de Arquivo JSON Externo (.json)"); self.btn_load_json.clicked.connect(self.load_metadata_from_external_json_file)
        metadata_outer_layout.addWidget(self.btn_load_json, alignment=Qt.AlignmentFlag.AlignLeft); metadata_group.setLayout(metadata_outer_layout); layout.addWidget(metadata_group)
        process_progress_group = QGroupBox("3. Iniciar Processamento e Acompanhar Progresso"); process_progress_layout = QVBoxLayout()
        self.btn_process = QPushButton("Iniciar Processamento dos Capítulos Selecionados"); self.btn_process.clicked.connect(self.start_processing_selected_manga); self.btn_process.setFixedHeight(40); self.btn_process.setStyleSheet("font-size: 16px; background-color: #27ae60; color: white; font-weight: bold;")
        process_progress_layout.addWidget(self.btn_process); process_progress_layout.addWidget(QLabel("Progresso Geral dos Capítulos Selecionados:")); self.overall_manga_progress_bar = QProgressBar(); self.overall_manga_progress_bar.setFormat("Capítulo %v de %m (%p%)")
        process_progress_layout.addWidget(self.overall_manga_progress_bar); process_progress_layout.addWidget(QLabel("Progresso do Capítulo Atual:")); self.chapter_progress_bar = QProgressBar(); self.chapter_progress_bar.setFormat("%p%")
        process_progress_layout.addWidget(self.chapter_progress_bar); self.status_label = QLabel("Pronto.")
        process_progress_layout.addWidget(self.status_label)
        self.btn_save_to_github = QPushButton("Salvar Metadados no GitHub"); self.btn_save_to_github.clicked.connect(self.save_metadata_to_github); self.btn_save_to_github.setEnabled(False); self.btn_save_to_github.setToolTip("Salva o JSON gerado no repositório GitHub configurado.")
        process_progress_layout.addWidget(self.btn_save_to_github)
        process_progress_group.setLayout(process_progress_layout); layout.addWidget(process_progress_group); layout.addStretch(); scroll_area.setWidget(upload_widget_internal)

    def _create_host_ui(self): # <<< NOVO MÉTODO
        layout = QVBoxLayout(self.host_tab)
        host_selection_group = QGroupBox("Seleção do Serviço de Hospedagem de Imagens")
        host_form_layout = QFormLayout()

        self.host_combobox = QComboBox()
        self.host_combobox.addItems(["Catbox.moe", "Imgur"]) # Adicionar outros se desejar
        self.host_combobox.currentTextChanged.connect(self.on_host_changed)
        host_form_layout.addRow(QLabel("Escolha o serviço de host:"), self.host_combobox)
        host_selection_group.setLayout(host_form_layout)
        layout.addWidget(host_selection_group)

        # Configurações Específicas do Imgur (inicialmente ocultas)
        self.imgur_settings_group = QGroupBox("Configurações do Imgur")
        imgur_form_layout = QFormLayout()
        self.imgur_client_id_input = QLineEdit()
        self.imgur_client_id_input.setPlaceholderText("Seu Client ID do Imgur (para uploads anônimos)")
        self.imgur_client_id_input.setToolTip("Necessário para qualquer upload no Imgur via API.")
        imgur_form_layout.addRow("Imgur Client ID:", self.imgur_client_id_input)
        
        # Autenticação OAuth2 seria mais complexa
        self.imgur_access_token_input = QLineEdit()
        self.imgur_access_token_input.setPlaceholderText("Opcional: Access Token (para álbuns/uploads autenticados)")
        self.imgur_access_token_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.imgur_access_token_input.setToolTip("Se fornecido, permite uploads na sua conta e criação de álbuns.")
        # btn_imgur_auth = QPushButton("Autenticar com Imgur (OAuth2) - NÃO IMPLEMENTADO") # Placeholder
        imgur_form_layout.addRow("Imgur Access Token:", self.imgur_access_token_input)

        self.imgur_settings_group.setLayout(imgur_form_layout)
        layout.addWidget(self.imgur_settings_group)
        
        layout.addStretch()
        self.imgur_settings_group.setVisible(False) # Ocultar por padrão


    def _create_settings_ui(self):
        layout = QVBoxLayout(self.settings_tab)

        # Grupo para Configurações do Catbox
        self.catbox_specific_settings_group = QGroupBox("Configurações Específicas do Catbox.moe")
        catbox_form_layout = QFormLayout()
        self.userhash_input_cfg = QLineEdit()
        self.userhash_input_cfg.setPlaceholderText("Seu userhash do Catbox (deixe em branco para anônimo)")
        catbox_form_layout.addRow("Userhash Catbox:", self.userhash_input_cfg)
        self.catbox_specific_settings_group.setLayout(catbox_form_layout)
        layout.addWidget(self.catbox_specific_settings_group)

        # Grupo para Configurações Gerais da Aplicação
        general_app_settings_group = QGroupBox("Configurações Gerais de Upload e Saída")
        general_app_form_layout = QFormLayout()
        self.rootfolder_input_cfg = QLineEdit(); self.rootfolder_input_cfg.setPlaceholderText("Ex: D:/Mangas")
        self.btn_browse_root_cfg = QPushButton("Procurar Pasta Raiz..."); self.btn_browse_root_cfg.clicked.connect(self._browse_root_folder_cfg)
        rootfolder_layout_cfg = QHBoxLayout(); rootfolder_layout_cfg.addWidget(self.rootfolder_input_cfg); rootfolder_layout_cfg.addWidget(self.btn_browse_root_cfg)
        general_app_form_layout.addRow("Pasta Raiz dos Mangás:", rootfolder_layout_cfg)

        self.metadata_output_dir_cfg = QLineEdit(); self.metadata_output_dir_cfg.setPlaceholderText(f"Padrão: '{DEFAULT_METADATA_OUTPUT_SUBDIR}' dentro da Pasta Raiz")
        self.btn_browse_metadata_output_cfg = QPushButton("Procurar Destino..."); self.btn_browse_metadata_output_cfg.clicked.connect(self._browse_metadata_output_dir_cfg)
        metadata_output_layout_cfg = QHBoxLayout(); metadata_output_layout_cfg.addWidget(self.metadata_output_dir_cfg); metadata_output_layout_cfg.addWidget(self.btn_browse_metadata_output_cfg)
        general_app_form_layout.addRow("Diretório de Saída dos Metadados:", metadata_output_layout_cfg)

        self.maxworkers_input_cfg = QSpinBox(); self.maxworkers_input_cfg.setRange(1, 20); self.maxworkers_input_cfg.setValue(5); self.maxworkers_input_cfg.setToolTip("Uploads de imagens em paralelo.")
        general_app_form_layout.addRow("Uploads Simultâneos (Max Workers):", self.maxworkers_input_cfg)
        self.ratelimit_input_cfg = QSpinBox(); self.ratelimit_input_cfg.setSuffix(" seg"); self.ratelimit_input_cfg.setRange(0, 10); self.ratelimit_input_cfg.setValue(1); self.ratelimit_input_cfg.setToolTip("Pausa entre inícios de uploads de imagem.")
        general_app_form_layout.addRow("Delay Entre Uploads Individuais:", self.ratelimit_input_cfg)
        self.json_key_start_zero_cfg = QCheckBox("Iniciar chaves de capítulo do JSON em '000'"); self.json_key_start_zero_cfg.setToolTip("Se marcado, o 1º cap. terá chave '000'. Se desmarcado (padrão), chave '001'.")
        general_app_form_layout.addRow(self.json_key_start_zero_cfg)
        general_app_settings_group.setLayout(general_app_form_layout)
        layout.addWidget(general_app_settings_group)

        github_settings_group = QGroupBox("GitHub (Opcional - para salvar JSON de metadados)")
        # ... (código original do grupo GitHub) ...
        github_form_layout = QFormLayout()
        self.github_user_cfg = QLineEdit(); self.github_user_cfg.setPlaceholderText("Seu nome de usuário do GitHub (informativo)");
        self.github_token_cfg = QLineEdit(); self.github_token_cfg.setPlaceholderText("Token de Acesso Pessoal (PAT) do GitHub"); self.github_token_cfg.setEchoMode(QLineEdit.EchoMode.Password)
        self.github_repo_cfg = QLineEdit(); self.github_repo_cfg.setPlaceholderText("Ex: seuUsuario/nome-do-repositorio")
        self.github_branch_cfg = QLineEdit(); self.github_branch_cfg.setPlaceholderText("Ex: main, master"); self.github_branch_cfg.setText("main")
        github_form_layout.addRow("Usuário GitHub:", self.github_user_cfg); github_form_layout.addRow("Token GitHub:", self.github_token_cfg); github_form_layout.addRow("Repositório (usuário/repo):", self.github_repo_cfg); github_form_layout.addRow("Branch:", self.github_branch_cfg)
        github_settings_group.setLayout(github_form_layout); layout.addWidget(github_settings_group)


        self.btn_save_settings = QPushButton("Salvar Todas as Configurações")
        self.btn_save_settings.clicked.connect(self.save_app_settings)
        layout.addWidget(self.btn_save_settings)
        layout.addStretch()

    def _create_log_ui(self):
        # ... (código original de _create_log_ui, sem alterações) ...
        layout = QVBoxLayout(self.log_tab); log_group = QGroupBox("Logs Detalhados da Aplicação"); log_layout = QVBoxLayout()
        self.log_output_textedit = QTextEdit(); self.log_output_textedit.setReadOnly(True); self.log_output_textedit.setStyleSheet("font-family: Consolas, Courier, monospace; color: #f0f0f0; background-color: #2e3338;")
        self.btn_clear_log = QPushButton("Limpar Log"); self.btn_clear_log.clicked.connect(lambda: self.log_output_textedit.clear())
        log_layout.addWidget(self.log_output_textedit); log_layout.addWidget(self.btn_clear_log, alignment=Qt.AlignmentFlag.AlignRight)
        log_group.setLayout(log_layout); layout.addWidget(log_group)


    def _get_settings_file_path(self):
        # ... (código original) ...
        app_data_path = Path(os.getenv('LOCALAPPDATA', Path.home())) / "MangaUploaderGUI" # Nome Genérico
        if sys.platform != "win32": app_data_path = Path.home() / ".config" / "MangaUploaderGUI"
        app_data_path.mkdir(parents=True, exist_ok=True); return app_data_path / "settings_v3.json" # Versão do settings


    def save_app_settings(self):
        settings = {
            "userhash": self.userhash_input_cfg.text().strip(), # Catbox
            "imgur_client_id": self.imgur_client_id_input.text().strip(), # Imgur
            "imgur_access_token": self.imgur_access_token_input.text(), # Imgur (sensível, talvez não salvar ou criptografar)
            "selected_host": self.selected_host, # Novo
            "root_folder": self.rootfolder_input_cfg.text().strip(),
            "metadata_output_dir": self.metadata_output_dir_cfg.text().strip(),
            "max_workers": self.maxworkers_input_cfg.value(),
            "rate_limit_delay_seconds": self.ratelimit_input_cfg.value(),
            "json_start_key_at_zero": self.json_key_start_zero_cfg.isChecked(),
            "github_user": self.github_user_cfg.text().strip(),
            "github_token": self.github_token_cfg.text(), # Sensível
            "github_repo": self.github_repo_cfg.text().strip(),
            "github_branch": self.github_branch_cfg.text().strip()
        }
        try:
            # ... (salvar JSON)
            with open(self._get_settings_file_path(), 'w', encoding='utf-8') as f: json.dump(settings, f, indent=4)
            self._log_to_tab(f"Configurações salvas: {self._get_settings_file_path()}"); QMessageBox.information(self, "Configurações", "Salvo!")
            self.current_root_folder_display.setText(settings["root_folder"]); self.populate_manga_list() # Atualiza UI se necessário
        except Exception as e: # ... (tratamento de erro)
            self._log_to_tab(f"Erro ao salvar configs: {e}"); QMessageBox.critical(self, "Erro", f"Falha: {e}")


    def _load_app_settings(self):
        settings_file = self._get_settings_file_path()
        defaults = { # Valores padrão atualizados
            "userhash": DEFAULT_USERHASH, "imgur_client_id": "", "imgur_access_token": "",
            "selected_host": "Catbox", "root_folder": str(Path.home()),
            "metadata_output_dir": "", "max_workers": 5, "rate_limit_delay_seconds": 1,
            "json_start_key_at_zero": False, "github_user": "", "github_token": "",
            "github_repo": "", "github_branch": "main"
        }
        settings = defaults.copy()
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f: loaded_settings = json.load(f)
                settings.update(loaded_settings)
            except Exception as e: self._log_to_tab(f"Erro ao carregar {settings_file}: {e}")
        else: # ... (lógica para criar arquivo de settings padrão) ...
            self._log_to_tab(f"Config não encontrada ({settings_file}), usando padrões.")
            try:
                with open(settings_file, 'w', encoding='utf-8') as f: json.dump(defaults, f, indent=4)
                self._log_to_tab(f"Config padrão criada: {settings_file}")
            except Exception as e: self._log_to_tab(f"Não foi possível criar config padrão: {e}")

        self.userhash_input_cfg.setText(settings.get("userhash", DEFAULT_USERHASH))
        self.imgur_client_id_input.setText(settings.get("imgur_client_id", ""))
        self.imgur_access_token_input.setText(settings.get("imgur_access_token", ""))
        self.selected_host = settings.get("selected_host", "Catbox")
        self.host_combobox.setCurrentText(f"{self.selected_host}.moe" if self.selected_host == "Catbox" else self.selected_host) # Ajustar para corresponder aos itens do combobox

        self.rootfolder_input_cfg.setText(settings.get("root_folder", str(Path.home())))
        self.metadata_output_dir_cfg.setText(settings.get("metadata_output_dir", ""))
        self.current_root_folder_display.setText(settings.get("root_folder", str(Path.home())))
        self.maxworkers_input_cfg.setValue(settings.get("max_workers", 5))
        self.ratelimit_input_cfg.setValue(settings.get("rate_limit_delay_seconds", 1))
        self.json_key_start_zero_cfg.setChecked(settings.get("json_start_key_at_zero", False))
        self.github_user_cfg.setText(settings.get("github_user", ""))
        self.github_token_cfg.setText(settings.get("github_token", ""))
        self.github_repo_cfg.setText(settings.get("github_repo", ""))
        self.github_branch_cfg.setText(settings.get("github_branch", "main"))
        
        self._log_to_tab("Configurações carregadas.")
        self._update_host_specific_settings_visibility() # Chamar após carregar
        self.populate_manga_list()

    def on_host_changed(self, selected_text): # <<< NOVO MÉTODO
        self.selected_host = selected_text.split(".")[0] if "." in selected_text else selected_text # Ex: "Catbox" ou "Imgur"
        self._log_to_tab(f"Serviço de host alterado para: {self.selected_host}")
        self._update_host_specific_settings_visibility()
        # Opcional: self.save_app_settings() # Para salvar imediatamente a escolha do host

    def _update_host_specific_settings_visibility(self): # <<< NOVO MÉTODO
        if not hasattr(self, 'imgur_settings_group'): return # UI não criada ainda

        is_imgur = (self.selected_host == "Imgur")
        self.imgur_settings_group.setVisible(is_imgur)
        self.catbox_specific_settings_group.setVisible(not is_imgur)

    # --- Métodos restantes da CatboxUploaderApp ---
    # (populate_manga_list, manga_item_double_clicked, load_metadata_from_json_file (MODIFICADA),
    #  load_metadata_from_external_json_file, start_processing_selected_manga (MODIFICADA),
    #  save_metadata_to_github, on_github_finished, on_github_error,
    #  _log_to_tab, setup_overall_progress, update_overall_progress, update_chapter_progress_bar,
    #  on_processing_finished, on_processing_error, closeEvent)
    #
    # COLE AQUI A VERSÃO MODIFICADA DE load_metadata_from_json_file (v0.9.13)
    # COLE AQUI A VERSÃO MODIFICADA DE start_processing_selected_manga
    # Os outros métodos que não foram explicitamente alterados nesta seção podem ser mantidos da v0.9.13
    # (Não vou repetir todos aqui por brevidade, mas eles são necessários para o funcionamento completo)

    # >>> INÍCIO DA load_metadata_from_json_file (v0.9.13) <<<
    def load_metadata_from_json_file(self, file_path_str, actual_chapter_folders_on_disk=None):
        if actual_chapter_folders_on_disk is None:
            actual_chapter_folders_on_disk = [] 
        try:
            with open(file_path_str, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if data.get("title", ""):
                self.manga_title_input.setText(data.get("title", ""))
            self.manga_description_input.setPlainText(data.get("description", ""))
            self.manga_artist_input.setText(data.get("artist", ""))
            self.manga_author_input.setText(data.get("author", ""))
            self.manga_cover_input.setText(data.get("cover", ""))
            status_json = data.get("status", "")
            self.manga_status_input.setCurrentText(status_json if status_json in MANGA_STATUS_OPTIONS else "")

            chapters_data_json = data.get("chapters", {})
            
            json_chapter_titles_normalized = {
                normalize_for_comparison(chap_data.get("title", ""))
                for chap_data in chapters_data_json.values() if chap_data.get("title")
            }
            json_chapter_titles_normalized.discard("") 

            normal_font = QFont()
            italic_font = QFont()
            italic_font.setItalic(True)
            cor_texto_padrao = self.chapters_list_widget.palette().color(self.chapters_list_widget.foregroundRole())
            if cor_texto_padrao.name() == "#000000": 
                cor_texto_padrao = QColor("#f0f0f0") if self.palette().color(self.backgroundRole()).lightness() < 128 else QColor("#101010")
            cor_texto_json = QColor("cyan") 

            for i in range(self.chapters_list_widget.count()):
                item = self.chapters_list_widget.item(i)
                chapter_name_on_disk_normalized = normalize_for_comparison(item.text())

                if chapter_name_on_disk_normalized and chapter_name_on_disk_normalized in json_chapter_titles_normalized:
                    item.setFont(italic_font)
                    item.setForeground(cor_texto_json)
                else:
                    item.setFont(normal_font)
                    item.setForeground(cor_texto_padrao) 
            
            group_name_to_set = DEFAULT_GROUP_NAME
            if chapters_data_json:
                sorted_numeric_keys = sorted([k for k in chapters_data_json.keys() if k.isdigit()], key=int)
                sorted_non_numeric_keys = sorted([k for k in chapters_data_json.keys() if not k.isdigit()], key=self._natural_sort_key)
                first_chap_key = None
                if sorted_numeric_keys: first_chap_key = sorted_numeric_keys[0]
                elif sorted_non_numeric_keys: first_chap_key = sorted_non_numeric_keys[0]
                if first_chap_key and first_chap_key in chapters_data_json:
                    groups = chapters_data_json[first_chap_key].get("groups", {})
                    group_name_to_set = next(iter(groups), DEFAULT_GROUP_NAME)
            self.group_name_input.setText(group_name_to_set)
            self._log_to_tab(f"Metadados de {file_path_str} carregados. Estilos aplicados.")
        except Exception as e:
            self._log_to_tab(f"Erro ao carregar ou processar o arquivo JSON '{file_path_str}': {e}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "Erro de JSON", f"Não foi possível carregar ou ler o arquivo JSON:\n{file_path_str}\n\nErro: {e}")
    # >>> FIM DA load_metadata_from_json_file (v0.9.13) <<<


    # >>> INÍCIO DA start_processing_selected_manga MODIFICADA <<<
    def start_processing_selected_manga(self):
        selected_manga_items = self.manga_list_widget.selectedItems()
        if not selected_manga_items:
            QMessageBox.warning(self, "Nenhum Mangá Selecionado", "Por favor, selecione um mangá da lista (duplo clique) primeiro.")
            return
        selected_manga_base_path_str = selected_manga_items[0].data(Qt.ItemDataRole.UserRole)

        selected_chapter_list_items = self.chapters_list_widget.selectedItems()
        if not selected_chapter_list_items:
            QMessageBox.warning(self, "Nenhum Capítulo Selecionado", "Selecione um ou mais capítulos para processar.")
            return
        
        chapters_to_process_names = [item.text() for item in selected_chapter_list_items]
        manga_title_from_ui = self.manga_title_input.text().strip()
        
        metadata_output_dir_val = self.metadata_output_dir_cfg.text().strip()
        if not metadata_output_dir_val:
            root_folder_val = self.rootfolder_input_cfg.text().strip()
            if not root_folder_val or not Path(root_folder_val).is_dir():
                QMessageBox.critical(self, "Configuração Necessária", "A 'Pasta Raiz dos Mangás' é inválida ou não está definida nas Configurações.")
                self.tab_widget.setCurrentWidget(self.settings_tab)
                return
            metadata_output_dir_val = str(Path(root_folder_val) / DEFAULT_METADATA_OUTPUT_SUBDIR)
            self._log_to_tab(f"Diretório de saída não especificado, usando padrão: {metadata_output_dir_val}")
        
        try:
            Path(metadata_output_dir_val).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(self, "Erro de Diretório", f"Falha ao criar diretório de saída:\n{metadata_output_dir_val}\nErro: {e}")
            return

        if not manga_title_from_ui: # Deve ser preenchido ao selecionar mangá
            QMessageBox.critical(self, "Erro Interno", "Título do mangá (nome da pasta) não definido. Por favor, selecione o mangá novamente.")
            return

        start_json_keys_at_zero_setting = self.json_key_start_zero_cfg.isChecked()

        # Limpar log se um novo processamento está começando e nenhum worker está ativo
        if not (self.current_uploader_worker and self.current_uploader_worker.isRunning()):
            self.log_output_textedit.clear()
        
        self._log_to_tab(f"Iniciando processamento para: {manga_title_from_ui} com host: {self.selected_host}. Capítulos: {', '.join(chapters_to_process_names)}")
        self.status_label.setText(f"Processando {manga_title_from_ui} ({self.selected_host})...")
        self.btn_process.setEnabled(False); self.btn_load_json.setEnabled(False)
        self.btn_save_to_github.setEnabled(False); self.manga_list_widget.setEnabled(False)
        self.chapters_list_widget.setEnabled(False)
        self.chapter_progress_bar.setValue(0); self.overall_manga_progress_bar.setValue(0)

        common_worker_args = {
            "max_workers": self.maxworkers_input_cfg.value(),
            "rate_limit_delay": float(self.ratelimit_input_cfg.value()),
            "manga_title_ui": manga_title_from_ui,
            "manga_desc_ui": self.manga_description_input.toPlainText().strip(),
            "manga_artist_ui": self.manga_artist_input.text().strip(),
            "manga_author_ui": self.manga_author_input.text().strip(),
            "manga_cover_ui": self.manga_cover_input.text().strip(),
            "manga_status_ui": self.manga_status_input.currentText(),
            "manga_base_path": selected_manga_base_path_str,
            "chapters_to_process_names": chapters_to_process_names,
            "group_name_ui": self.group_name_input.text().strip(),
            "metadata_output_dir_base": metadata_output_dir_val,
            "start_json_keys_at_zero": start_json_keys_at_zero_setting
        }

        if self.selected_host == "Catbox":
            userhash = self.userhash_input_cfg.text().strip()
            if not userhash: userhash = DEFAULT_USERHASH
            self.current_uploader_worker = UploaderWorker(userhash=userhash, **common_worker_args)
        elif self.selected_host == "Imgur":
            imgur_client_id = self.imgur_client_id_input.text().strip()
            imgur_access_token = self.imgur_access_token_input.text().strip() # Pode ser vazio
            if not imgur_client_id:
                QMessageBox.warning(self, "Imgur Client ID Faltando", "Por favor, insira o Client ID do Imgur na aba 'Host' (ou Configurações).")
                self._reset_ui_after_error_or_finish(); return
            self.current_uploader_worker = ImgurUploaderWorker(client_id=imgur_client_id, imgur_access_token=imgur_access_token, **common_worker_args)
        else:
            self._log_to_tab(f"Host desconhecido selecionado: {self.selected_host}")
            self._reset_ui_after_error_or_finish(); return

        self.current_uploader_worker.signals.log_message.connect(self._log_to_tab)
        self.current_uploader_worker.signals.overall_progress_setup.connect(self.setup_overall_progress)
        self.current_uploader_worker.signals.overall_progress_update.connect(self.update_overall_progress)
        self.current_uploader_worker.signals.chapter_progress.connect(self.update_chapter_progress_bar)
        self.current_uploader_worker.signals.finished.connect(self.on_processing_finished)
        self.current_uploader_worker.signals.error.connect(self.on_processing_error)
        self.current_uploader_worker.start()
    # >>> FIM DA start_processing_selected_manga MODIFICADA <<<

    def _reset_ui_after_error_or_finish(self): # Função auxiliar para reabilitar UI
        self.btn_process.setEnabled(True)
        self.btn_load_json.setEnabled(True)
        # O botão de salvar no GitHub só é habilitado em on_processing_finished
        self.manga_list_widget.setEnabled(True)
        self.chapters_list_widget.setEnabled(True)


    # ... (Cole aqui os métodos _browse_root_folder_cfg, _browse_metadata_output_dir_cfg, 
    # populate_manga_list, manga_item_double_clicked, load_metadata_from_external_json_file,
    # save_metadata_to_github, on_github_finished, on_github_error, _log_to_tab,
    # setup_overall_progress, update_overall_progress, update_chapter_progress_bar,
    # on_processing_finished (lembre-se de chamar _reset_ui_after_error_or_finish aqui),
    # on_processing_error (lembre-se de chamar _reset_ui_after_error_or_finish aqui),
    # e closeEvent da versão 0.9.13, pois eles não foram alterados fundamentalmente para esta mudança de host,
    # exceto por garantir que on_processing_finished e on_processing_error chamem _reset_ui_after_error_or_finish)
    # Vou adicionar as versões de on_processing_finished e on_processing_error atualizadas
    
    def on_processing_finished(self, json_path, yaml_path):
        self.last_saved_json_path = json_path 
        self.btn_save_to_github.setEnabled(True) 
        final_msg = f"CONCLUÍDO ({self.selected_host})!\nJSON: {json_path}\nYAML: {yaml_path}"; self._log_to_tab(final_msg.replace("\n", " | "))
        self.status_label.setText(f"Concluído ({self.selected_host})!"); 
        self._reset_ui_after_error_or_finish() # Reabilita UI
        self.chapter_progress_bar.setValue(100); self.chapter_progress_bar.setFormat("Concluído - 100%")
        if self.overall_manga_progress_bar.maximum() > 0:
            self.overall_manga_progress_bar.setValue(self.overall_manga_progress_bar.maximum())
            self.overall_manga_progress_bar.setFormat(f"Todos {self.overall_manga_progress_bar.maximum()} caps (100%)")
        else: self.overall_manga_progress_bar.setFormat("Nenhum capítulo processado")
        QMessageBox.information(self, "Sucesso", final_msg); self.tab_widget.setCurrentWidget(self.log_tab)

    def on_processing_error(self, error_message):
        self._log_to_tab(f"ERRO ({self.selected_host}):\n{error_message}"); self.status_label.setText(f"Erro ({self.selected_host})! Ver Log.")
        self._reset_ui_after_error_or_finish() # Reabilita UI
        self.btn_save_to_github.setEnabled(True) # Habilitar mesmo em erro para possível envio manual se o JSON foi gerado
        QMessageBox.critical(self, "Erro", f"Erro no processamento ({self.selected_host}). Verifique Log."); self.tab_widget.setCurrentWidget(self.log_tab)

    # Certifique-se de que os outros métodos não listados aqui são copiados da versão 0.9.13
    # que você tinha (ou da minha resposta anterior que era bem completa para UploaderWorker e GitHubWorker).
    # A classe GitHubWorker e __main__ não precisam de mudanças para ESTA funcionalidade de host.

# ... (Cole o restante do código da classe CatboxUploaderApp e a classe GitHubWorker aqui,
# e o bloco if __name__ == "__main__":)
# O código da classe CatboxUploaderApp é extenso; as principais modificações
# foram mostradas. Você precisará garantir que todos os outros métodos
# da CatboxUploaderApp que não foram explicitamente modificados aqui
# sejam mantidos da sua versão funcional anterior (v0.9.13).

# >>> Os métodos omitidos de CatboxUploaderApp para colar da v0.9.13 são:
# _browse_root_folder_cfg, _browse_metadata_output_dir_cfg, populate_manga_list,
# manga_item_double_clicked (já usa a load_metadata_from_json_file modificada),
# load_metadata_from_external_json_file (já usa a load_metadata_from_json_file modificada),
# save_metadata_to_github, on_github_finished, on_github_error, _log_to_tab,
# setup_overall_progress, update_overall_progress, update_chapter_progress_bar, closeEvent.
# O código do GitHubWorker e o if __name__ == "__main__": não precisam de mudanças.
import concurrent.futures
from pathlib import Path
import base64
import unicodedata # <<< ADICIONADO

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog,
    QProgressBar, QSpinBox, QGroupBox, QFormLayout, QMessageBox,
    QListWidget, QListWidgetItem, QTabWidget, QScrollArea, QComboBox,
    QAbstractItemView, QCheckBox
)
from PySide6.QtCore import Qt, QThread, Signal, QObject
from PySide6.QtGui import QFont, QColor

# --- Constantes Globais ---
ALBUM_TITLE_TEMPLATE = "{manga_name} - Capítulo {chapter_name}"
ALBUM_DESCRIPTION_TEMPLATE = "Capítulo {chapter_name} de {manga_name}"
CATBOX_API_URL = "https://catbox.moe/user/api.php"
DEFAULT_USERHASH = ""
DEFAULT_GROUP_NAME = "DefaultScanGroup"
DEFAULT_METADATA_OUTPUT_SUBDIR = "Manga_Metadata_Output"
MANGA_STATUS_OPTIONS = ["", "Em Andamento", "Concluído", "Hiato", "Cancelado", "Pausado"]
APP_VERSION = "0.9.13" # <<< VERSÃO ATUALIZADA - Original era 0.9.12

# --- Função Auxiliar de Normalização ---
def normalize_for_comparison(text: str) -> str:
    """Normaliza o texto para comparações mais robustas."""
    if not isinstance(text, str):
        return ""
    return unicodedata.normalize('NFKC', text.strip())

# --- Sinais dos Workers ---
class WorkerSignals(QObject):
    overall_progress_setup = Signal(int)
    overall_progress_update = Signal(int, str)
    chapter_progress = Signal(str, int)
    finished = Signal(str, str)
    error = Signal(str)
    log_message = Signal(str)

class GitHubWorkerSignals(QObject):
    finished = Signal(str)
    error = Signal(str)
    log_message = Signal(str)

# --- Worker para Uploads Catbox ---
class UploaderWorker(QThread):
    def __init__(self, userhash, max_workers, rate_limit_delay,
                 manga_title_ui, manga_desc_ui, manga_artist_ui,
                 manga_author_ui, manga_cover_ui, manga_status_ui,
                 manga_base_path,
                 chapters_to_process_names, # Lista de nomes de pastas ORIGINAIS da UI
                 group_name_ui,
                 metadata_output_dir_base,
                 start_json_keys_at_zero):
        super().__init__()
        self.signals = WorkerSignals()
        self.userhash = userhash
        self.max_workers = max_workers
        self.rate_limit_delay = float(rate_limit_delay)
        self.manga_title_ui = manga_title_ui
        self.manga_desc_ui = manga_desc_ui
        self.manga_artist_ui = manga_artist_ui
        self.manga_author_ui = manga_author_ui
        self.manga_cover_ui = manga_cover_ui
        self.manga_status_ui = manga_status_ui
        self.manga_base_path = Path(manga_base_path)
        
        # Mantém os nomes originais das pastas selecionadas (para acesso ao disco, título no JSON)
        self.chapters_to_process_original_names = list(chapters_to_process_names)
        # Cria um conjunto de nomes de pastas NORMALIZADOS para comparações lógicas
        self.chapters_to_process_normalized_set = {normalize_for_comparison(name) for name in chapters_to_process_names}
        
        self.group_name_ui = group_name_ui.strip() if group_name_ui.strip() else DEFAULT_GROUP_NAME
        self.metadata_output_dir_base = Path(metadata_output_dir_base)
        self.start_json_keys_at_zero = start_json_keys_at_zero

    def _emit_log(self, message):
        self.signals.log_message.emit(message)

    @staticmethod
    def _sanitize_for_path(name: str, is_filename: bool = False) -> str:
        if not name: return "sem_titulo" if is_filename else "pasta_sem_nome"
        temp_name = name
        if is_filename: temp_name = temp_name.replace(" ", "_")
        temp_name = re.sub(r'[\\/*?:"<>|]', "", temp_name)
        if is_filename:
            base, dot, extension = temp_name.rpartition('.')
            if dot: base = base.strip("._ "); temp_name = (base if base else "arquivo_sem_nome") + dot + extension
            else: temp_name = temp_name.strip("._ ")
        else: temp_name = temp_name.strip("._ ")
        return temp_name if temp_name else ("sem_titulo" if is_filename else "pasta_sem_nome")

    @staticmethod
    def _natural_sort_key(s):
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

    def _upload_file_catbox(self, filepath):
        if not filepath.exists(): self._emit_log(f"ERRO: Arquivo não encontrado: {filepath}"); return None, f"Arquivo não encontrado: {filepath}"
        MAX_UPLOAD_RETRIES = 3; RETRY_DELAY_SECONDS = 5; last_exception_str = "N/A"
        for attempt in range(MAX_UPLOAD_RETRIES):
            try:
                if attempt > 0: self._emit_log(f"Tentativa {attempt+1}/{MAX_UPLOAD_RETRIES} para {filepath.name} ({RETRY_DELAY_SECONDS}s espera...)"); time.sleep(RETRY_DELAY_SECONDS)
                self._emit_log(f"Upload {filepath.name} (tentativa {attempt+1}/{MAX_UPLOAD_RETRIES})...");
                with open(filepath, "rb") as f: files={"fileToUpload":f}; data={"reqtype":"fileupload","userhash":self.userhash}; response=requests.post(CATBOX_API_URL,data=data,files=files,timeout=300); response.raise_for_status()
                self._emit_log(f"Sucesso upload {filepath.name} ({attempt+1}). URL: {response.text}"); return response.text, None
            except requests.exceptions.RequestException as e: last_exception_str=str(e); self._emit_log(f"Falha rede/servidor {attempt+1}/{MAX_UPLOAD_RETRIES} ({filepath.name}): {e}")
            except Exception as e: last_exception_str=str(e); self._emit_log(f"Erro inesperado {attempt+1}/{MAX_UPLOAD_RETRIES} ({filepath.name}): {e}")
        self._emit_log(f"Falha upload {filepath.name} ({MAX_UPLOAD_RETRIES} tentativas). Erro: {last_exception_str}"); return None, f"Falha após {MAX_UPLOAD_RETRIES} tentativas: {last_exception_str}"

    def _create_album_catbox(self, title, description, file_ids):
        if not file_ids: self._emit_log(f"Nenhum ID para criar álbum: {title}"); return None
        data = {"reqtype": "createalbum", "userhash": self.userhash, "title": title, "desc": description, "files": " ".join(file_ids)}
        try: response = requests.post(CATBOX_API_URL, data=data, timeout=120); response.raise_for_status(); return response.text
        except Exception as e: self._emit_log(f"Erro ao criar álbum '{title}': {e}"); return None

    def _parallel_upload_files(self, ordered_image_filenames, chapter_path: Path):
        upload_results_map = {}; image_file_ids_for_album = []; failures_log = []
        total_files = len(ordered_image_filenames)
        def process_file_with_delay(filename_str: str):
            if self.rate_limit_delay > 0: time.sleep(self.rate_limit_delay)
            filepath = chapter_path / filename_str; uploaded_url, error = self._upload_file_catbox(filepath)
            return filename_str, uploaded_url, error
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(process_file_with_delay, fn): fn for fn in ordered_image_filenames}
            processed_count = 0
            for future in concurrent.futures.as_completed(futures):
                original_filename, uploaded_url, error = future.result(); processed_count += 1
                progress_percentage = int((processed_count / total_files) * 100)
                self.signals.chapter_progress.emit(f"Cap. {chapter_path.name}: {original_filename} ({processed_count}/{total_files})", progress_percentage)
                if uploaded_url: upload_results_map[original_filename] = uploaded_url; image_file_ids_for_album.append(uploaded_url.split("/")[-1])
                else: upload_results_map[original_filename] = None; failures_log.append((original_filename, error));
        direct_image_urls_ordered = [upload_results_map.get(fn) for fn in ordered_image_filenames if upload_results_map.get(fn)]
        if failures_log: self._emit_log(f"{len(failures_log)} uploads falharam definitivamente para o capítulo '{chapter_path.name}'.")
        return image_file_ids_for_album, direct_image_urls_ordered

    def _process_manga_chapter(self, manga_title_for_album_template, chapter_path: Path):
        # chapter_path.name é o nome ORIGINAL da pasta do capítulo
        chapter_name_original = chapter_path.name
        self._emit_log(f"Processando cap: {chapter_name_original}")
        self.signals.chapter_progress.emit(f"Iniciando: {chapter_name_original}", 0)

        if not chapter_path.is_dir():
            self._emit_log(f"Pasta '{chapter_name_original}' ({chapter_path}) não é um diretório válido.")
            return None, None, chapter_name_original

        ordered_image_filenames = sorted(
            [f.name for f in chapter_path.iterdir() if f.is_file() and f.name.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))],
            key=UploaderWorker._natural_sort_key
        )

        if not ordered_image_filenames:
            self._emit_log(f"Nenhuma imagem encontrada em '{chapter_name_original}'.")
            return None, None, chapter_name_original

        self._emit_log(f"{len(ordered_image_filenames)} imagens encontradas em '{chapter_name_original}'.")
        image_file_ids_for_album, direct_image_urls_ordered = self._parallel_upload_files(ordered_image_filenames, chapter_path)

        if not direct_image_urls_ordered:
            self._emit_log(f"Nenhuma imagem foi enviada com sucesso para '{chapter_name_original}'.")
            self.signals.chapter_progress.emit(f"Falha no upload: {chapter_name_original}", 100)
            return "", [], chapter_name_original

        album_url = ""
        if image_file_ids_for_album:
            album_title = ALBUM_TITLE_TEMPLATE.format(manga_name=manga_title_for_album_template, chapter_name=chapter_name_original)
            album_description = ALBUM_DESCRIPTION_TEMPLATE.format(manga_name=manga_title_for_album_template, chapter_name=chapter_name_original)
            self._emit_log(f"Criando álbum para '{chapter_name_original}'...")
            self.signals.chapter_progress.emit(f"Criando álbum: {chapter_name_original}", 99)
            album_url_result = self._create_album_catbox(album_title, album_description, image_file_ids_for_album)
            if album_url_result:
                self._emit_log(f"Álbum criado com sucesso: {album_url_result}")
                album_url = album_url_result
            else:
                self._emit_log(f"Falha ao criar álbum para '{chapter_name_original}'. Álbum URL estará vazio.")
        else:
            self._emit_log(f"Nenhum ID de arquivo de imagem para criar álbum de '{chapter_name_original}'.")

        self.signals.chapter_progress.emit(f"Cap. {chapter_name_original} finalizado.", 100)
        # Retorna o nome ORIGINAL da pasta do capítulo.
        return album_url, direct_image_urls_ordered, chapter_name_original

    def run(self):
        try:
            manga_title_for_paths = self.manga_title_ui
            sanitized_manga_foldername = UploaderWorker._sanitize_for_path(manga_title_for_paths, is_filename=False)
            sanitized_manga_filename_base = UploaderWorker._sanitize_for_path(manga_title_for_paths, is_filename=True)

            manga_output_folder = self.metadata_output_dir_base / sanitized_manga_foldername
            manga_output_folder.mkdir(parents=True, exist_ok=True)
            output_json_file_path = manga_output_folder / f"{sanitized_manga_filename_base}.json"
            output_yaml_file_path = manga_output_folder / f"{sanitized_manga_filename_base}.yaml"

            cubari_data_loaded = {}
            if output_json_file_path.exists():
                try:
                    with open(output_json_file_path, "r", encoding="utf-8") as f:
                        cubari_data_loaded = json.load(f)
                    self._emit_log(f"Arquivo JSON existente carregado: {output_json_file_path}")
                except Exception as e:
                    self._emit_log(f"Erro ao ler JSON existente ({output_json_file_path}): {e}. Um novo JSON será criado.")

            all_chapters_by_original_title = {} # Chaves serão os nomes ORIGINAIS das pastas/títulos.
            existing_chapters_from_json_data = cubari_data_loaded.get("chapters", {})

            # Preserva capítulos do JSON carregado que NÃO foram selecionados para reprocessamento
            for old_numeric_key, old_chap_data in existing_chapters_from_json_data.items():
                title_from_json_original = old_chap_data.get("title", old_numeric_key) # Nome/título original do JSON
                title_from_json_normalized = normalize_for_comparison(title_from_json_original)

                if not title_from_json_normalized:
                    self._emit_log(f"Aviso: Capítulo com chave '{old_numeric_key}' no JSON existente ('{title_from_json_original}') tem título vazio ou inválido após normalização. Será ignorado na preservação.")
                    continue

                # Compara o título NORMALIZADO do JSON com o CONJUNTO de nomes de pastas NORMALIZADOS selecionados para processamento
                if title_from_json_normalized not in self.chapters_to_process_normalized_set:
                    # Se não estiver na lista de reprocessamento, mantém usando o título ORIGINAL como chave
                    all_chapters_by_original_title[title_from_json_original] = old_chap_data
                # else: O capítulo será (re)processado no loop abaixo e sobrescreverá esta entrada se o nome da pasta original corresponder

            # Ordena os nomes ORIGINAIS das pastas selecionadas para processamento para manter a ordem da UI
            ordered_chapters_to_process_original_names = sorted(
                self.chapters_to_process_original_names,
                key=UploaderWorker._natural_sort_key
            )

            total_chapters_to_process = len(ordered_chapters_to_process_original_names)
            self.signals.overall_progress_setup.emit(total_chapters_to_process)
            self._emit_log(f"Processando {total_chapters_to_process} capítulos selecionados para '{self.manga_base_path.name}'.")

            yaml_chapters_this_run_numeric_keys = {} # Para o arquivo YAML de resumo

            for current_process_idx, chapter_folder_name_original in enumerate(ordered_chapters_to_process_original_names, start=1):
                self.signals.overall_progress_update.emit(current_process_idx, chapter_folder_name_original)
                chapter_actual_path = self.manga_base_path / chapter_folder_name_original # Usa nome ORIGINAL para o caminho da pasta

                self._emit_log(f"--- Processando Cap {current_process_idx}/{total_chapters_to_process}: {chapter_folder_name_original} ---")

                if not chapter_actual_path.is_dir():
                    self._emit_log(f"Pasta '{chapter_folder_name_original}' não encontrada ou não é um diretório. Pulando.")
                    continue

                # _process_manga_chapter retorna o nome da pasta ORIGINAL como o terceiro valor
                album_url_result, direct_image_urls_ordered_result, processed_chapter_original_name = \
                    self._process_manga_chapter(self.manga_base_path.name, chapter_actual_path)

                timestamp = str(int(time.time()))

                if direct_image_urls_ordered_result: # Se o processamento do capítulo teve sucesso e retornou URLs
                    existing_volume_info = ""
                    # Tenta obter o volume do JSON já carregado
                    # Primeiro, tenta pelo nome original do capítulo (que é a chave em all_chapters_by_original_title se já existia e foi preservado)
                    if processed_chapter_original_name in all_chapters_by_original_title and "volume" in all_chapters_by_original_title[processed_chapter_original_name]:
                         existing_volume_info = all_chapters_by_original_title[processed_chapter_original_name].get("volume", "")
                    else: # Fallback para buscar no JSON original carregado (cubari_data_loaded)
                        for _, chap_data_loaded in existing_chapters_from_json_data.items():
                            if normalize_for_comparison(chap_data_loaded.get("title", "")) == normalize_for_comparison(processed_chapter_original_name):
                                existing_volume_info = chap_data_loaded.get("volume", "")
                                break
                    
                    # Usa o nome ORIGINAL da pasta processada como chave e para o campo "title"
                    all_chapters_by_original_title[processed_chapter_original_name] = {
                        "title": processed_chapter_original_name, # Nome original da pasta
                        "volume": existing_volume_info,
                        "last_updated": timestamp,
                        "groups": {self.group_name_ui: direct_image_urls_ordered_result}
                    }

                    # Para o YAML, usa a chave numérica (baseada na ordem de processamento ATUAL) e o título original
                    # As chaves numéricas para YAML podem ser diferentes das chaves numéricas do JSON final se capítulos antigos foram preservados.
                    # Isso está ok, pois o YAML é um resumo desta execução.
                    yaml_numeric_key_for_this_run = f"{current_process_idx:03d}" 
                    yaml_chapters_this_run_numeric_keys[yaml_numeric_key_for_this_run] = {
                        "title": processed_chapter_original_name,
                        "volume": existing_volume_info,
                        "groups": {self.group_name_ui: album_url_result if album_url_result else ""}
                    }
                    self._emit_log(f"Dados de '{processed_chapter_original_name}' atualizados/adicionados.")
                else:
                    self._emit_log(f"Nenhuma imagem processada com sucesso para '{processed_chapter_original_name}'. Não será incluído nos metadados.")

            # Constrói o objeto JSON final com capítulos ordenados pelos seus títulos ORIGINAIS
            final_ordered_original_titles = sorted(
                list(all_chapters_by_original_title.keys()),
                key=UploaderWorker._natural_sort_key
            )

            final_chapters_json_object = {}
            start_index_for_json_keys = 0 if self.start_json_keys_at_zero else 1
            for i, original_title_key in enumerate(final_ordered_original_titles, start=start_index_for_json_keys):
                numeric_key_str = f"{i:03d}" # Chave numérica para o JSON final
                final_chapters_json_object[numeric_key_str] = all_chapters_by_original_title[original_title_key]

            # Monta o dicionário final para o JSON
            final_cubari_data = {
                "title": self.manga_title_ui,
                "description": self.manga_desc_ui,
                "artist": self.manga_artist_ui,
                "author": self.manga_author_ui,
                "cover": self.manga_cover_ui,
                "status": self.manga_status_ui,
                "chapters": final_chapters_json_object # Objeto de capítulos com chaves numéricas
            }

            with open(output_json_file_path, "w", encoding="utf-8") as f:
                json.dump(final_cubari_data, f, indent=2, ensure_ascii=False)
            self._emit_log(f"Arquivo JSON salvo com sucesso: {output_json_file_path}")

            # Monta dados para o YAML (usa os capítulos processados nesta execução, como antes)
            final_yaml_data_to_save = {
                "title": final_cubari_data["title"],
                "description": final_cubari_data["description"],
                "artist": final_cubari_data["artist"],
                "author": final_cubari_data["author"],
                "cover": final_cubari_data["cover"],
                "status": final_cubari_data["status"],
                "chapters": yaml_chapters_this_run_numeric_keys # Apenas capítulos processados nesta execução
            }
            with open(output_yaml_file_path, "w", encoding="utf-8") as f:
                yaml.dump(final_yaml_data_to_save, f, sort_keys=False, allow_unicode=True, Dumper=getattr(yaml, 'SafeDumper', yaml.Dumper))
            self._emit_log(f"Arquivo YAML de resumo salvo: {output_yaml_file_path}")

            self.signals.finished.emit(str(output_json_file_path), str(output_yaml_file_path))
        except Exception as e:
            error_msg = f"Erro GERAL no worker de upload: {e}\n{traceback.format_exc()}"
            self._emit_log(error_msg)
            self.signals.error.emit(error_msg)

# --- Worker para GitHub ---
# Nenhuma mudança necessária no GitHubWorker para esta correção específica.
class GitHubWorker(QThread):
    def __init__(self, github_token, github_repo_full_name,
                 github_branch, local_json_path, remote_file_path_in_repo):
        super().__init__()
        self.signals = GitHubWorkerSignals()
        self.github_token = github_token
        self.github_repo_full_name = github_repo_full_name
        self.github_branch = github_branch
        self.local_json_path = Path(local_json_path)
        self.remote_file_path_in_repo = remote_file_path_in_repo

    def _emit_log(self, message):
        self.signals.log_message.emit(f"[GitHub] {message}")

    def run(self):
        try:
            if not all([self.github_token, self.github_repo_full_name, self.github_branch]):
                self._emit_log("Configurações GitHub incompletas (Token, Repositório, Branch)."); self.signals.error.emit("Configurações GitHub incompletas."); return
            if not self.local_json_path.exists():
                self._emit_log(f"JSON local não encontrado: {self.local_json_path}"); self.signals.error.emit("JSON local não encontrado."); return
            owner, repo_name = self.github_repo_full_name.split('/', 1) if '/' in self.github_repo_full_name else (None, None)
            if not owner or not repo_name: self._emit_log("Formato repo inválido. Use 'usuario/nome_repo'."); self.signals.error.emit("Formato repo inválido."); return
            processed_token = str(self.github_token).strip()
            auth_header_value = "token " + processed_token
            headers = {"Authorization": auth_header_value, "Accept": "application/vnd.github.v3+json"}
            with open(self.local_json_path, 'r', encoding='utf-8') as f: content = f.read()
            content_base64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            clean_remote_path = self.remote_file_path_in_repo.lstrip('/')
            api_url_file = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{clean_remote_path}"
            self._emit_log(f"Verificando GitHub: {api_url_file} (branch: {self.github_branch})"); sha = None
            try:
                response_get = requests.get(api_url_file, headers=headers, params={'ref': self.github_branch}, timeout=30)
                if response_get.status_code == 200: sha = response_get.json().get("sha"); self._emit_log(f"Arquivo encontrado. SHA: {sha}")
                elif response_get.status_code == 404: self._emit_log("Arquivo não encontrado. Será criado.")
                elif response_get.status_code not in [401, 403]: response_get.raise_for_status()
            except requests.exceptions.RequestException as e: self._emit_log(f"Erro ao verificar arquivo (GET): {e}")
            commit_message = f"Atualiza metadados: {self.local_json_path.name} via CatboxUploaderGUI v{APP_VERSION}"
            data_payload = {"message": commit_message, "content": content_base64, "branch": self.github_branch}
            if sha: data_payload["sha"] = sha
            self._emit_log(f"Enviando para GitHub (PUT {api_url_file})..."); response_put = requests.put(api_url_file, headers=headers, json=data_payload, timeout=60)
            if response_put.status_code == 200 or response_put.status_code == 201:
                commit_sha = response_put.json().get("content", {}).get("sha", "N/A")
                self._emit_log(f"Arquivo salvo no GitHub! SHA do conteúdo: {commit_sha}"); self.signals.finished.emit(f"JSON salvo no GitHub!\nRepo: {self.github_repo_full_name}\nCaminho: {clean_remote_path}")
            else:
                error_details_text = response_put.text;
                try: error_details_json = response_put.json(); error_details_msg = error_details_json.get("message", str(error_details_json))
                except: error_details_msg = error_details_text
                self._emit_log(f"Falha ao salvar no GitHub. Status: {response_put.status_code}. Resposta: {error_details_msg}"); self.signals.error.emit(f"Falha GitHub ({response_put.status_code}): {error_details_msg}")
        except Exception as e: error_msg = f"Erro GitHubWorker: {e}\n{traceback.format_exc()}"; self._emit_log(error_msg); self.signals.error.emit(f"Erro: {e}")


# --- Janela Principal da GUI ---
class CatboxUploaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Catbox Mangá Uploader GUI v{APP_VERSION}") # Usa a APP_VERSION atualizada
        self.setGeometry(100, 100, 950, 880)
        self.tab_widget = QTabWidget(); self.setCentralWidget(self.tab_widget)
        self.upload_tab = QWidget(); self.settings_tab = QWidget(); self.log_tab = QWidget()
        self.tab_widget.addTab(self.upload_tab, "Upload de Mangá"); self.tab_widget.addTab(self.settings_tab, "Configurações"); self.tab_widget.addTab(self.log_tab, "Log da Aplicação")
        self._create_upload_ui(); self._create_settings_ui(); self._create_log_ui()
        self.uploader_worker = None; self.github_worker = None; self.last_saved_json_path = None
        self._load_app_settings()

    @staticmethod
    def _natural_sort_key(s): return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)]

    @staticmethod
    def _sanitize_for_path(name: str, is_filename: bool=False) -> str:
        if not name: return "sem_titulo" if is_filename else "pasta_sem_nome"
        temp_name = name;
        if is_filename: temp_name = temp_name.replace(" ", "_")
        temp_name = re.sub(r'[\\/*?:"<>|]', "", temp_name)
        if is_filename:
            base, dot, extension = temp_name.rpartition('.')
            if dot: base = base.strip("._ "); temp_name = (base if base else "arquivo_sem_nome") + dot + extension
            else: temp_name = temp_name.strip("._ ")
        else: temp_name = temp_name.strip("._ ")
        return temp_name if temp_name else ("sem_titulo" if is_filename else "pasta_sem_nome")

    def _create_upload_ui(self):
        # ... (código original, sem alterações nesta função para esta correção) ...
        scroll_area = QScrollArea(); scroll_area.setWidgetResizable(True)
        self.upload_tab.setLayout(QVBoxLayout()); self.upload_tab.layout().addWidget(scroll_area)
        upload_widget_internal = QWidget(); layout = QVBoxLayout(upload_widget_internal)
        manga_selection_group = QGroupBox("1. Selecionar Pasta do Mangá"); manga_selection_layout = QVBoxLayout()
        self.current_root_folder_display = QLineEdit(); self.current_root_folder_display.setReadOnly(True); self.current_root_folder_display.setPlaceholderText("Defina a Pasta Raiz na aba 'Configurações'")
        manga_selection_layout.addWidget(QLabel("Pasta Raiz Atual (de 'Configurações'):")); manga_selection_layout.addWidget(self.current_root_folder_display)
        self.btn_refresh_mangas_upload_tab = QPushButton("Atualizar Lista de Mangás da Pasta Raiz"); self.btn_refresh_mangas_upload_tab.clicked.connect(self.populate_manga_list)
        manga_selection_layout.addWidget(self.btn_refresh_mangas_upload_tab)
        manga_selection_layout.addWidget(QLabel("Mangás Encontrados (dê um duplo clique para selecionar):"))
        self.manga_list_widget = QListWidget(); self.manga_list_widget.itemDoubleClicked.connect(self.manga_item_double_clicked)
        manga_selection_layout.addWidget(self.manga_list_widget); manga_selection_group.setLayout(manga_selection_layout); layout.addWidget(manga_selection_group)
        chapters_detected_group = QGroupBox("Capítulos Detectados no Mangá Selecionado (selecione os que deseja processar)"); chapters_layout = QVBoxLayout()
        self.chapters_list_widget = QListWidget(); self.chapters_list_widget.setStyleSheet("background-color: #2e3338; color: #f0f0f0;")
        self.chapters_list_widget.setFixedHeight(150); self.chapters_list_widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection); self.chapters_list_widget.setToolTip("Selecione um ou mais capítulos. Use Ctrl+Clique ou Shift+Clique.")
        chapters_layout.addWidget(self.chapters_list_widget); chapters_detected_group.setLayout(chapters_layout); layout.addWidget(chapters_detected_group)
        metadata_group = QGroupBox("2. Metadados do Mangá (para os arquivos de saída)"); metadata_outer_layout = QVBoxLayout()
        metadata_top_layout = QHBoxLayout(); metadata_form_left = QFormLayout()
        self.manga_title_input = QLineEdit(); self.manga_title_input.setPlaceholderText("Nome da pasta do mangá"); self.manga_title_input.setReadOnly(True)
        self.manga_artist_input = QLineEdit(); self.manga_artist_input.setPlaceholderText("Ex: SIU")
        self.manga_author_input = QLineEdit(); self.manga_author_input.setPlaceholderText("Ex: SIU")
        self.manga_status_input = QComboBox(); self.manga_status_input.addItems(MANGA_STATUS_OPTIONS)
        self.manga_cover_input = QLineEdit(); self.manga_cover_input.setPlaceholderText("URL direta da imagem de capa")
        self.group_name_input = QLineEdit(DEFAULT_GROUP_NAME); self.group_name_input.setPlaceholderText("Nome do grupo/scan")
        metadata_form_left.addRow("Título do Mangá (Nome da Pasta):", self.manga_title_input); metadata_form_left.addRow("Artista:", self.manga_artist_input); metadata_form_left.addRow("Autor:", self.manga_author_input); metadata_form_left.addRow("Status do Mangá:", self.manga_status_input); metadata_form_left.addRow("URL da Capa:", self.manga_cover_input); metadata_form_left.addRow("Nome do Grupo (JSON/YAML):", self.group_name_input)
        metadata_top_layout.addLayout(metadata_form_left, 1); metadata_form_right = QVBoxLayout()
        metadata_form_right.addWidget(QLabel("Descrição do Mangá:")); self.manga_description_input = QTextEdit(); self.manga_description_input.setPlaceholderText("Sinopse..."); self.manga_description_input.setMinimumHeight(130)
        metadata_form_right.addWidget(self.manga_description_input); metadata_top_layout.addLayout(metadata_form_right, 1)
        metadata_outer_layout.addLayout(metadata_top_layout); self.btn_load_json = QPushButton("Carregar Metadados de Arquivo JSON Externo (.json)"); self.btn_load_json.clicked.connect(self.load_metadata_from_external_json_file)
        metadata_outer_layout.addWidget(self.btn_load_json, alignment=Qt.AlignmentFlag.AlignLeft); metadata_group.setLayout(metadata_outer_layout); layout.addWidget(metadata_group)
        process_progress_group = QGroupBox("3. Iniciar Processamento e Acompanhar Progresso"); process_progress_layout = QVBoxLayout()
        self.btn_process = QPushButton("Iniciar Processamento dos Capítulos Selecionados"); self.btn_process.clicked.connect(self.start_processing_selected_manga); self.btn_process.setFixedHeight(40); self.btn_process.setStyleSheet("font-size: 16px; background-color: #27ae60; color: white; font-weight: bold;")
        process_progress_layout.addWidget(self.btn_process); process_progress_layout.addWidget(QLabel("Progresso Geral dos Capítulos Selecionados:")); self.overall_manga_progress_bar = QProgressBar(); self.overall_manga_progress_bar.setFormat("Capítulo %v de %m (%p%)")
        process_progress_layout.addWidget(self.overall_manga_progress_bar); process_progress_layout.addWidget(QLabel("Progresso do Capítulo Atual:")); self.chapter_progress_bar = QProgressBar(); self.chapter_progress_bar.setFormat("%p%")
        process_progress_layout.addWidget(self.chapter_progress_bar); self.status_label = QLabel("Pronto.")
        process_progress_layout.addWidget(self.status_label)
        self.btn_save_to_github = QPushButton("Salvar Metadados no GitHub"); self.btn_save_to_github.clicked.connect(self.save_metadata_to_github); self.btn_save_to_github.setEnabled(False); self.btn_save_to_github.setToolTip("Salva o JSON gerado no repositório GitHub configurado.")
        process_progress_layout.addWidget(self.btn_save_to_github)
        process_progress_group.setLayout(process_progress_layout); layout.addWidget(process_progress_group); layout.addStretch(); scroll_area.setWidget(upload_widget_internal)

    def _create_settings_ui(self):
        # ... (código original, sem alterações nesta função para esta correção) ...
        layout = QVBoxLayout(self.settings_tab)
        app_settings_group = QGroupBox("Configurações da Aplicação (Catbox e Local)"); app_form_layout = QFormLayout()
        self.userhash_input_cfg = QLineEdit(); self.userhash_input_cfg.setPlaceholderText("Seu userhash do Catbox (deixe em branco para anônimo)")
        self.rootfolder_input_cfg = QLineEdit(); self.rootfolder_input_cfg.setPlaceholderText("Ex: D:/Mangas")
        self.btn_browse_root_cfg = QPushButton("Procurar Pasta Raiz..."); self.btn_browse_root_cfg.clicked.connect(self._browse_root_folder_cfg)
        rootfolder_layout_cfg = QHBoxLayout(); rootfolder_layout_cfg.addWidget(self.rootfolder_input_cfg); rootfolder_layout_cfg.addWidget(self.btn_browse_root_cfg)
        self.metadata_output_dir_cfg = QLineEdit(); self.metadata_output_dir_cfg.setPlaceholderText(f"Padrão: '{DEFAULT_METADATA_OUTPUT_SUBDIR}' dentro da Pasta Raiz selecionada")
        self.btn_browse_metadata_output_cfg = QPushButton("Procurar Destino..."); self.btn_browse_metadata_output_cfg.clicked.connect(self._browse_metadata_output_dir_cfg)
        metadata_output_layout_cfg = QHBoxLayout(); metadata_output_layout_cfg.addWidget(self.metadata_output_dir_cfg); metadata_output_layout_cfg.addWidget(self.btn_browse_metadata_output_cfg)
        self.maxworkers_input_cfg = QSpinBox(); self.maxworkers_input_cfg.setRange(1, 20); self.maxworkers_input_cfg.setValue(5); self.maxworkers_input_cfg.setToolTip("Uploads de imagens em paralelo.")
        self.ratelimit_input_cfg = QSpinBox(); self.ratelimit_input_cfg.setSuffix(" seg"); self.ratelimit_input_cfg.setRange(0, 10); self.ratelimit_input_cfg.setValue(1); self.ratelimit_input_cfg.setToolTip("Pausa entre uploads de imagem.")
        self.json_key_start_zero_cfg = QCheckBox("Iniciar chaves de capítulo do JSON em '000'"); self.json_key_start_zero_cfg.setToolTip("Se marcado, o 1º cap. terá chave '000' no JSON.\nSe desmarcado (padrão), o 1º cap. terá chave '001'.")
        app_form_layout.addRow("Userhash Catbox:", self.userhash_input_cfg); app_form_layout.addRow("Pasta Raiz dos Mangás:", rootfolder_layout_cfg); app_form_layout.addRow("Diretório de Saída dos Metadados:", metadata_output_layout_cfg); app_form_layout.addRow("Uploads Simultâneos (Max Workers):", self.maxworkers_input_cfg); app_form_layout.addRow("Delay Entre Uploads Individuais:", self.ratelimit_input_cfg); app_form_layout.addRow(self.json_key_start_zero_cfg)
        app_settings_group.setLayout(app_form_layout); layout.addWidget(app_settings_group)
        github_settings_group = QGroupBox("GitHub (Opcional - para salvar JSON de metadados)"); github_form_layout = QFormLayout()
        self.github_user_cfg = QLineEdit(); self.github_user_cfg.setPlaceholderText("Seu nome de usuário do GitHub (informativo)");
        self.github_token_cfg = QLineEdit(); self.github_token_cfg.setPlaceholderText("Token de Acesso Pessoal (PAT) do GitHub"); self.github_token_cfg.setEchoMode(QLineEdit.EchoMode.Password)
        self.github_repo_cfg = QLineEdit(); self.github_repo_cfg.setPlaceholderText("Ex: seuUsuario/nome-do-repositorio")
        self.github_branch_cfg = QLineEdit(); self.github_branch_cfg.setPlaceholderText("Ex: main, master"); self.github_branch_cfg.setText("main")
        github_form_layout.addRow("Usuário GitHub:", self.github_user_cfg); github_form_layout.addRow("Token GitHub:", self.github_token_cfg); github_form_layout.addRow("Repositório (usuário/repo):", self.github_repo_cfg); github_form_layout.addRow("Branch:", self.github_branch_cfg)
        github_settings_group.setLayout(github_form_layout); layout.addWidget(github_settings_group)
        self.btn_save_settings = QPushButton("Salvar Todas as Configurações"); self.btn_save_settings.clicked.connect(self.save_app_settings)
        layout.addWidget(self.btn_save_settings); layout.addStretch()

    def _create_log_ui(self):
        # ... (código original, sem alterações nesta função para esta correção) ...
        layout = QVBoxLayout(self.log_tab); log_group = QGroupBox("Logs Detalhados da Aplicação"); log_layout = QVBoxLayout()
        self.log_output_textedit = QTextEdit(); self.log_output_textedit.setReadOnly(True); self.log_output_textedit.setStyleSheet("font-family: Consolas, Courier, monospace; color: #f0f0f0; background-color: #2e3338;")
        self.btn_clear_log = QPushButton("Limpar Log"); self.btn_clear_log.clicked.connect(lambda: self.log_output_textedit.clear())
        log_layout.addWidget(self.log_output_textedit); log_layout.addWidget(self.btn_clear_log, alignment=Qt.AlignmentFlag.AlignRight)
        log_group.setLayout(log_layout); layout.addWidget(log_group)

    def _get_settings_file_path(self):
        # ... (código original, sem alterações nesta função para esta correção) ...
        app_data_path = Path(os.getenv('LOCALAPPDATA', Path.home())) / "CatboxUploaderGUI"
        if sys.platform != "win32": app_data_path = Path.home() / ".config" / "CatboxUploaderGUI"
        app_data_path.mkdir(parents=True, exist_ok=True); return app_data_path / "settings_v2.json"

    def save_app_settings(self):
        # ... (código original, sem alterações nesta função para esta correção) ...
        settings = {"userhash": self.userhash_input_cfg.text().strip(), "root_folder": self.rootfolder_input_cfg.text().strip(), "metadata_output_dir": self.metadata_output_dir_cfg.text().strip(), "max_workers": self.maxworkers_input_cfg.value(), "rate_limit_delay_seconds": self.ratelimit_input_cfg.value(), "json_start_key_at_zero": self.json_key_start_zero_cfg.isChecked(), "github_user": self.github_user_cfg.text().strip(), "github_token": self.github_token_cfg.text(), "github_repo": self.github_repo_cfg.text().strip(), "github_branch": self.github_branch_cfg.text().strip()}
        try:
            with open(self._get_settings_file_path(), 'w', encoding='utf-8') as f: json.dump(settings, f, indent=4)
            self._log_to_tab(f"Configurações salvas: {self._get_settings_file_path()}"); QMessageBox.information(self, "Configurações", "Salvo!")
            self.current_root_folder_display.setText(settings["root_folder"]); self.populate_manga_list()
        except Exception as e: self._log_to_tab(f"Erro ao salvar configs: {e}"); QMessageBox.critical(self, "Erro", f"Falha: {e}")

    def _load_app_settings(self):
        # ... (código original, sem alterações nesta função para esta correção) ...
        # Pequena correção no bloco try/except para criação do arquivo de config padrão, já estava no original
        settings_file = self._get_settings_file_path()
        defaults = {"userhash": DEFAULT_USERHASH, "root_folder": str(Path.home()), "metadata_output_dir": "", "max_workers": 5, "rate_limit_delay_seconds": 1, "json_start_key_at_zero": False, "github_user": "", "github_token": "", "github_repo": "", "github_branch": "main"}
        settings = defaults.copy()
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f: loaded_settings = json.load(f)
                settings.update(loaded_settings)
            except Exception as e: self._log_to_tab(f"Erro ao carregar {settings_file}: {e}")
        else:
            self._log_to_tab(f"Config não encontrada ({settings_file}), usando padrões.")
            try:
                with open(settings_file, 'w', encoding='utf-8') as f: 
                    json.dump(defaults, f, indent=4)
                self._log_to_tab(f"Config padrão criada: {settings_file}")
            except Exception as e:
                self._log_to_tab(f"Não foi possível criar config padrão: {e}")
        self.userhash_input_cfg.setText(settings.get("userhash", DEFAULT_USERHASH)); self.rootfolder_input_cfg.setText(settings.get("root_folder", str(Path.home()))); self.metadata_output_dir_cfg.setText(settings.get("metadata_output_dir", "")); self.current_root_folder_display.setText(settings.get("root_folder", str(Path.home()))); self.maxworkers_input_cfg.setValue(settings.get("max_workers", 5)); self.ratelimit_input_cfg.setValue(settings.get("rate_limit_delay_seconds", 1)); self.json_key_start_zero_cfg.setChecked(settings.get("json_start_key_at_zero", False)); self.github_user_cfg.setText(settings.get("github_user", "")); self.github_token_cfg.setText(settings.get("github_token", "")); self.github_repo_cfg.setText(settings.get("github_repo", "")); self.github_branch_cfg.setText(settings.get("github_branch", "main"))
        self._log_to_tab("Configurações carregadas."); self.populate_manga_list()

    def _browse_root_folder_cfg(self):
        # ... (código original, sem alterações nesta função para esta correção) ...
        folder = QFileDialog.getExistingDirectory(self, "Selecionar Pasta Raiz", self.rootfolder_input_cfg.text().strip() or str(Path.home()));
        if folder: self.rootfolder_input_cfg.setText(folder)
        
    def _browse_metadata_output_dir_cfg(self):
        # ... (código original, sem alterações nesta função para esta correção) ...
        folder = QFileDialog.getExistingDirectory(self, "Selecionar Saída dos Metadados", self.metadata_output_dir_cfg.text().strip() or self.rootfolder_input_cfg.text().strip() or str(Path.home()));
        if folder: self.metadata_output_dir_cfg.setText(folder)

    def populate_manga_list(self):
        # ... (código original, sem alterações nesta função para esta correção) ...
        self.manga_list_widget.clear(); self.chapters_list_widget.clear(); self.chapters_list_widget.clearSelection()
        root_path_str = self.rootfolder_input_cfg.text().strip()
        if not root_path_str: self.current_root_folder_display.setText("Pasta raiz não definida nas Configurações"); self._log_to_tab("Pasta raiz não definida."); return
        if not Path(root_path_str).is_dir(): self.current_root_folder_display.setText(f"Pasta raiz inválida: {root_path_str}"); self._log_to_tab(f"Pasta raiz inválida: {root_path_str}"); return
        self.current_root_folder_display.setText(root_path_str); root_path = Path(root_path_str)
        self._log_to_tab(f"Procurando pastas de mangá em: {root_path}")
        try:
            manga_dirs = sorted([d for d in root_path.iterdir() if d.is_dir() and not d.name.startswith(('.', '$'))], key=lambda p: self._natural_sort_key(p.name))
            if not manga_dirs: self._log_to_tab(f"Nenhuma pasta de mangá encontrada em {root_path}"); return
            for manga_dir_path in manga_dirs: item = QListWidgetItem(manga_dir_path.name); item.setData(Qt.ItemDataRole.UserRole, str(manga_dir_path)); self.manga_list_widget.addItem(item)
            self._log_to_tab(f"Lista de mangás atualizada. {len(manga_dirs)} pastas encontradas.")
        except Exception as e: self._log_to_tab(f"Erro ao listar pastas de mangá em '{root_path}': {e}"); QMessageBox.warning(self, "Erro ao Listar Pastas", f"Não foi possível listar as pastas em '{root_path}':\n{e}")

    def manga_item_double_clicked(self, item: QListWidgetItem):
        # ... (código original, sem alterações nesta função para esta correção) ...
        # A chamada para self.load_metadata_from_json_file dentro desta função agora usará a versão modificada.
        if not item: return
        selected_manga_path_str = item.data(Qt.ItemDataRole.UserRole); manga_folder_name = item.text()
        self.manga_title_input.setText(manga_folder_name); self._log_to_tab(f"Mangá '{manga_folder_name}' selecionado (caminho: {selected_manga_path_str}).")
        self.chapters_list_widget.clear(); self.chapters_list_widget.clearSelection()
        if not selected_manga_path_str or not Path(selected_manga_path_str).is_dir():
            self._log_to_tab(f"Caminho da pasta do mangá '{selected_manga_path_str}' é inválido."); QMessageBox.warning(self, "Erro", f"O caminho para '{manga_folder_name}' parece ser inválido.")
            self.manga_description_input.clear(); self.manga_artist_input.clear(); self.manga_author_input.clear(); self.manga_status_input.setCurrentIndex(0); self.manga_cover_input.clear(); self.group_name_input.setText(DEFAULT_GROUP_NAME)
            return
        self._log_to_tab(f"Listando capítulos (subpastas) de: {selected_manga_path_str}"); actual_chapter_folders_on_disk = []
        try:
            manga_path = Path(selected_manga_path_str)
            chapter_folders = sorted([d.name for d in manga_path.iterdir() if d.is_dir() and not d.name.startswith(('.', '$'))], key=CatboxUploaderApp._natural_sort_key)
            actual_chapter_folders_on_disk = chapter_folders # Guardar para passar para load_metadata
            if chapter_folders:
                for chap_name in chapter_folders: self.chapters_list_widget.addItem(QListWidgetItem(chap_name))
                self._log_to_tab(f"{len(chapter_folders)} capítulos detectados (do disco) para '{manga_folder_name}'.")
            else: self._log_to_tab(f"Nenhum subdiretório (capítulo) que corresponda aos critérios encontrado em '{manga_folder_name}'.")
        except Exception as e: self._log_to_tab(f"Erro desconhecido ao listar capítulos para '{manga_folder_name}': {e}\n{traceback.format_exc()}"); QMessageBox.warning(self, "Erro", f"Ocorreu um erro ao tentar listar os capítulos de '{manga_folder_name}'.")
        
        metadata_output_base = self.metadata_output_dir_cfg.text().strip()
        if not metadata_output_base:
            root_folder_val = self.rootfolder_input_cfg.text().strip()
            if root_folder_val and Path(root_folder_val).is_dir(): metadata_output_base = str(Path(root_folder_val) / DEFAULT_METADATA_OUTPUT_SUBDIR)
            else:
                self._log_to_tab("Pasta raiz não configurada, não é possível procurar JSON de metadados prévio."); self.manga_description_input.setPlainText(f"Descrição para {manga_folder_name}..."); self.manga_artist_input.clear(); self.manga_author_input.clear(); self.manga_status_input.setCurrentIndex(0); self.manga_cover_input.clear(); self.group_name_input.setText(DEFAULT_GROUP_NAME)
                self.tab_widget.setCurrentWidget(self.upload_tab); return
        
        sanitized_manga_foldername = CatboxUploaderApp._sanitize_for_path(manga_folder_name, is_filename=False)
        sanitized_manga_filename_base = CatboxUploaderApp._sanitize_for_path(manga_folder_name, is_filename=True)
        potential_json_path = Path(metadata_output_base) / sanitized_manga_foldername / f"{sanitized_manga_filename_base}.json"
        
        if potential_json_path.exists():
            self._log_to_tab(f"Tentando carregar metadados do arquivo JSON existente: {potential_json_path}")
            self.load_metadata_from_json_file(str(potential_json_path), actual_chapter_folders_on_disk)
        else:
            self._log_to_tab(f"Nenhum arquivo JSON de metadados ({potential_json_path.name}) encontrado para '{manga_folder_name}'."); self.manga_description_input.setPlainText(f"Descrição para {manga_folder_name}..."); self.manga_artist_input.clear(); self.manga_author_input.clear(); self.manga_status_input.setCurrentIndex(0); self.manga_cover_input.clear(); self.group_name_input.setText(DEFAULT_GROUP_NAME)
        self.tab_widget.setCurrentWidget(self.upload_tab)


    def load_metadata_from_external_json_file(self):
        # ... (código original, sem alterações nesta função para esta correção) ...
        # A chamada para self.load_metadata_from_json_file dentro desta função agora usará a versão modificada.
        initial_dir = self.metadata_output_dir_cfg.text().strip() or self.rootfolder_input_cfg.text().strip() or str(Path.home())
        dialog_path, _ = QFileDialog.getOpenFileName(self, "Carregar Arquivo JSON de Metadados Externo", initial_dir, "JSON Files (*.json)")
        if dialog_path: self.load_metadata_from_json_file(dialog_path) # Não precisa passar actual_chapter_folders_on_disk aqui, pois a lista de capítulos já deve estar populada se um mangá foi selecionado.

    # >>> INÍCIO DA VERSÃO MODIFICADA DE load_metadata_from_json_file <<<
    def load_metadata_from_json_file(self, file_path_str, actual_chapter_folders_on_disk=None):
        if actual_chapter_folders_on_disk is None:
            actual_chapter_folders_on_disk = [] 
        try:
            with open(file_path_str, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if data.get("title", ""):
                self.manga_title_input.setText(data.get("title", ""))
            self.manga_description_input.setPlainText(data.get("description", ""))
            self.manga_artist_input.setText(data.get("artist", ""))
            self.manga_author_input.setText(data.get("author", ""))
            self.manga_cover_input.setText(data.get("cover", ""))
            status_json = data.get("status", "")
            self.manga_status_input.setCurrentText(status_json if status_json in MANGA_STATUS_OPTIONS else "")

            chapters_data_json = data.get("chapters", {})
            
            json_chapter_titles_normalized = {
                normalize_for_comparison(chap_data.get("title", ""))
                for chap_data in chapters_data_json.values() if chap_data.get("title")
            }
            json_chapter_titles_normalized.discard("") 

            normal_font = QFont()
            italic_font = QFont()
            italic_font.setItalic(True)
            # Use as cores padrão do tema, se possível, ou defina explicitamente.
            # As cores abaixo são para um tema escuro. Ajuste se necessário.
            cor_texto_padrao = self.chapters_list_widget.palette().color(self.chapters_list_widget.foregroundRole()) # Tenta usar a cor padrão do widget
            if cor_texto_padrao.name() == "#000000": # Fallback se a cor padrão for preta (pode acontecer em alguns temas claros não configurados)
                cor_texto_padrao = QColor("#f0f0f0") if self.palette().color(self.backgroundRole()).lightness() < 128 else QColor("#101010")

            cor_texto_json = QColor("cyan") 

            for i in range(self.chapters_list_widget.count()):
                item = self.chapters_list_widget.item(i)
                chapter_name_on_disk_normalized = normalize_for_comparison(item.text())

                if chapter_name_on_disk_normalized and chapter_name_on_disk_normalized in json_chapter_titles_normalized:
                    item.setFont(italic_font)
                    item.setForeground(cor_texto_json)
                else:
                    item.setFont(normal_font)
                    item.setForeground(cor_texto_padrao) 
            
            group_name_to_set = DEFAULT_GROUP_NAME
            if chapters_data_json:
                # Lógica para pegar o nome do grupo do primeiro capítulo encontrado
                # Ordena por chaves numéricas primeiro, depois por chaves não numéricas naturalmente
                sorted_numeric_keys = sorted([k for k in chapters_data_json.keys() if k.isdigit()], key=int)
                sorted_non_numeric_keys = sorted([k for k in chapters_data_json.keys() if not k.isdigit()], key=self._natural_sort_key)
                
                first_chap_key = None
                if sorted_numeric_keys:
                    first_chap_key = sorted_numeric_keys[0]
                elif sorted_non_numeric_keys:
                    first_chap_key = sorted_non_numeric_keys[0]

                if first_chap_key and first_chap_key in chapters_data_json:
                    groups = chapters_data_json[first_chap_key].get("groups", {})
                    group_name_to_set = next(iter(groups), DEFAULT_GROUP_NAME)
            self.group_name_input.setText(group_name_to_set)

            self._log_to_tab(f"Metadados de {file_path_str} carregados. Estilos aplicados conforme correspondência de títulos normalizados.")
        except Exception as e:
            self._log_to_tab(f"Erro ao carregar ou processar o arquivo JSON '{file_path_str}': {e}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "Erro de JSON", f"Não foi possível carregar ou ler o arquivo JSON:\n{file_path_str}\n\nErro: {e}")
    # >>> FIM DA VERSÃO MODIFICADA DE load_metadata_from_json_file <<<

    def start_processing_selected_manga(self):
        # ... (código original, sem alterações nesta função para esta correção, UploaderWorker já foi modificado) ...
        selected_manga_items = self.manga_list_widget.selectedItems()
        if not selected_manga_items: QMessageBox.warning(self, "Nenhum Mangá Selecionado", "Por favor, selecione um mangá da lista (duplo clique) primeiro."); return
        selected_manga_base_path_str = selected_manga_items[0].data(Qt.ItemDataRole.UserRole)
        selected_chapter_list_items = self.chapters_list_widget.selectedItems()
        if not selected_chapter_list_items: QMessageBox.warning(self, "Nenhum Capítulo Selecionado", "Selecione um ou mais capítulos para processar."); return
        chapters_to_process_names = [item.text() for item in selected_chapter_list_items]
        manga_title_from_ui = self.manga_title_input.text().strip(); userhash = self.userhash_input_cfg.text().strip()
        metadata_output_dir_val = self.metadata_output_dir_cfg.text().strip()
        if not metadata_output_dir_val:
            root_folder_val = self.rootfolder_input_cfg.text().strip()
            if not root_folder_val or not Path(root_folder_val).is_dir(): QMessageBox.critical(self, "Configuração Necessária", "A 'Pasta Raiz dos Mangás' é inválida."); self.tab_widget.setCurrentWidget(self.settings_tab); return
            metadata_output_dir_val = str(Path(root_folder_val) / DEFAULT_METADATA_OUTPUT_SUBDIR)
            self._log_to_tab(f"Diretório de saída não especificado, usando padrão: {metadata_output_dir_val}")
        try: Path(metadata_output_dir_val).mkdir(parents=True, exist_ok=True)
        except Exception as e: QMessageBox.critical(self, "Erro de Diretório", f"Falha ao criar diretório de saída:\n{metadata_output_dir_val}\nErro: {e}"); return
        if not userhash: userhash = DEFAULT_USERHASH; self._log_to_tab(f"Userhash do Catbox não fornecido. Uploads podem ser anônimos ou usar um padrão.")
        if not manga_title_from_ui: QMessageBox.critical(self, "Erro Interno", "Título do mangá (nome da pasta) não definido."); return

        start_json_keys_at_zero_setting = self.json_key_start_zero_cfg.isChecked()
        if not (self.uploader_worker and self.uploader_worker.isRunning()): self.log_output_textedit.clear()
        self._log_to_tab(f"Iniciando processamento para: {manga_title_from_ui}. Capítulos: {', '.join(chapters_to_process_names)}")
        self.status_label.setText(f"Processando {manga_title_from_ui}..."); self.btn_process.setEnabled(False); self.btn_load_json.setEnabled(False); self.btn_save_to_github.setEnabled(False); self.manga_list_widget.setEnabled(False); self.chapters_list_widget.setEnabled(False)
        self.chapter_progress_bar.setValue(0); self.overall_manga_progress_bar.setValue(0)
        self.uploader_worker = UploaderWorker(userhash=userhash, max_workers=self.maxworkers_input_cfg.value(), rate_limit_delay=float(self.ratelimit_input_cfg.value()), manga_title_ui=manga_title_from_ui, manga_desc_ui=self.manga_description_input.toPlainText().strip(), manga_artist_ui=self.manga_artist_input.text().strip(), manga_author_ui=self.manga_author_input.text().strip(), manga_cover_ui=self.manga_cover_input.text().strip(), manga_status_ui=self.manga_status_input.currentText(), manga_base_path=selected_manga_base_path_str, chapters_to_process_names=chapters_to_process_names, group_name_ui=self.group_name_input.text().strip(), metadata_output_dir_base=metadata_output_dir_val, start_json_keys_at_zero=start_json_keys_at_zero_setting)
        self.uploader_worker.signals.log_message.connect(self._log_to_tab); self.uploader_worker.signals.overall_progress_setup.connect(self.setup_overall_progress); self.uploader_worker.signals.overall_progress_update.connect(self.update_overall_progress); self.uploader_worker.signals.chapter_progress.connect(self.update_chapter_progress_bar); self.uploader_worker.signals.finished.connect(self.on_processing_finished); self.uploader_worker.signals.error.connect(self.on_processing_error)
        self.uploader_worker.start()

    def save_metadata_to_github(self):
        # ... (código original, sem alterações nesta função para esta correção) ...
        if not hasattr(self, 'last_saved_json_path') or not self.last_saved_json_path: QMessageBox.warning(self, "JSON Não Salvo", "Nenhum JSON gerado para enviar."); return
        local_json_path = Path(self.last_saved_json_path)
        if not local_json_path.exists(): QMessageBox.warning(self, "Arquivo Não Encontrado", f"JSON não encontrado em:\n{local_json_path}"); return
        gh_token = self.github_token_cfg.text(); gh_repo_full = self.github_repo_cfg.text().strip(); gh_branch = self.github_branch_cfg.text().strip()
        if not gh_token or not gh_repo_full or not gh_branch: QMessageBox.warning(self, "Config GitHub Incompleta", "Preencha Token, Repositório e Branch do GitHub."); self.tab_widget.setCurrentWidget(self.settings_tab); return

        remote_file_path = local_json_path.name # Salva na raiz da branch

        self._log_to_tab(f"Iniciando salvamento GitHub: {gh_repo_full}, branch: {gh_branch}, caminho no repo: {remote_file_path}")
        self.status_label.setText("Salvando no GitHub..."); self.btn_save_to_github.setEnabled(False); self.btn_process.setEnabled(False)
        self.github_worker = GitHubWorker(github_token=gh_token, github_repo_full_name=gh_repo_full, github_branch=gh_branch, local_json_path=str(local_json_path), remote_file_path_in_repo=remote_file_path)
        self.github_worker.signals.log_message.connect(self._log_to_tab); self.github_worker.signals.finished.connect(self.on_github_finished); self.github_worker.signals.error.connect(self.on_github_error)
        self.github_worker.start()

    def on_github_finished(self, message):
        # ... (código original, sem alterações nesta função para esta correção) ...
        self._log_to_tab(f"[GitHub] Sucesso: {message}"); self.status_label.setText("JSON salvo no GitHub!")
        QMessageBox.information(self, "GitHub", message); self.btn_save_to_github.setEnabled(True); self.btn_process.setEnabled(True)

    def on_github_error(self, error_message):
        # ... (código original, sem alterações nesta função para esta correção) ...
        self._log_to_tab(f"[GitHub] ERRO: {error_message}"); self.status_label.setText("Erro ao salvar no GitHub.")
        QMessageBox.critical(self, "Erro GitHub", f"Falha GitHub:\n{error_message}"); self.btn_save_to_github.setEnabled(True); self.btn_process.setEnabled(True)

    def _log_to_tab(self, message):
        # ... (código original, sem alterações nesta função para esta correção) ...
        self.log_output_textedit.append(f"[{time.strftime('%H:%M:%S')}] {message}"); self.log_output_textedit.ensureCursorVisible()

    def setup_overall_progress(self, total_chapters):
        # ... (código original, sem alterações nesta função para esta correção) ...
        self.overall_manga_progress_bar.setRange(0, total_chapters); self.overall_manga_progress_bar.setValue(0); self.overall_manga_progress_bar.setFormat(f"Total: %v de %m caps (%p%)" if total_chapters > 0 else "Nenhum cap")

    def update_overall_progress(self, current_chapter_index, chapter_name_processed):
        # ... (código original, sem alterações nesta função para esta correção) ...
        self.overall_manga_progress_bar.setValue(current_chapter_index)

    def update_chapter_progress_bar(self, message, percentage):
        # ... (código original, sem alterações nesta função para esta correção) ...
        self.status_label.setText(message); self.chapter_progress_bar.setValue(percentage); self.chapter_progress_bar.setFormat(f"{message} - %p%")

    def on_processing_finished(self, json_path, yaml_path):
        # ... (código original, sem alterações nesta função para esta correção) ...
        self.last_saved_json_path = json_path
        self.btn_save_to_github.setEnabled(True)
        final_msg = f"CONCLUÍDO!\nJSON: {json_path}\nYAML: {yaml_path}"; self._log_to_tab(final_msg.replace("\n", " | "))
        self.status_label.setText("Concluído!"); self.btn_process.setEnabled(True); self.btn_load_json.setEnabled(True); self.manga_list_widget.setEnabled(True); self.chapters_list_widget.setEnabled(True)
        self.chapter_progress_bar.setValue(100); self.chapter_progress_bar.setFormat("Concluído - 100%")
        if self.overall_manga_progress_bar.maximum() > 0:
            self.overall_manga_progress_bar.setValue(self.overall_manga_progress_bar.maximum())
            self.overall_manga_progress_bar.setFormat(f"Todos {self.overall_manga_progress_bar.maximum()} caps (100%)")
        else:
            self.overall_manga_progress_bar.setFormat("Nenhum capítulo processado")
        QMessageBox.information(self, "Sucesso", final_msg); self.tab_widget.setCurrentWidget(self.log_tab)

    def on_processing_error(self, error_message):
        # ... (código original, sem alterações nesta função para esta correção) ...
        self._log_to_tab(f"ERRO:\n{error_message}"); self.status_label.setText("Erro! Ver Log.")
        self.btn_process.setEnabled(True); self.btn_load_json.setEnabled(True); self.btn_save_to_github.setEnabled(True); self.manga_list_widget.setEnabled(True); self.chapters_list_widget.setEnabled(True)
        QMessageBox.critical(self, "Erro", "Erro no processamento. Verifique Log."); self.tab_widget.setCurrentWidget(self.log_tab)

    def closeEvent(self, event):
        # ... (código original, sem alterações nesta função para esta correção) ...
        self.save_app_settings()
        workers_running = []
        if self.uploader_worker and self.uploader_worker.isRunning(): workers_running.append("Upload Catbox")
        if self.github_worker and self.github_worker.isRunning(): workers_running.append("Salvar no GitHub")
        if workers_running:
            process_names = " e ".join(workers_running)
            if QMessageBox.question(self, "Sair?", f"Processo(s) de {process_names} em andamento. Sair mesmo?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                self._log_to_tab(f"Saindo com processo(s) de {process_names} em execução...")
                if self.uploader_worker and self.uploader_worker.isRunning():
                    self.uploader_worker.quit();
                    if not self.uploader_worker.wait(2000): self.uploader_worker.terminate(); self.uploader_worker.wait()
                if self.github_worker and self.github_worker.isRunning():
                    self.github_worker.quit()
                    if not self.github_worker.wait(2000): self.github_worker.terminate(); self.github_worker.wait()
                event.accept()
            else: event.ignore(); return
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CatboxUploaderApp()
    window.show()
    sys.exit(app.exec())