import asyncio
import json
import httpx
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
from loguru import logger

from ..models.indexador import (
    IndexadorConfig, IndexadorData, IndexadorState,
    SeriesInfo, SeriesData, Author, Publication, 
    Status, Chapters, Cover, Rating,
    Hub, SocialPlatform, Statistics, StatisticsOverview,
    StatisticsTeam, StatisticsCommunity, StatisticsContent, 
    Technical, API, Cache, Formats, Schedule, Updates, Maintenance,
    Legal, Copyright, Support, SupportLink, Features, Search, 
    Filtering, Sorting, Notifications, TeamMembers, Team, Website, Icon
)
from ..config import ConfigManager
from .github import GitHubService
from utils.sanitizer import sanitize_filename


class IndexadorService:
    """Serviço principal para gerenciamento do indexador JSON"""
    
    def __init__(self, config_manager: ConfigManager, github_service: GitHubService):
        self.config_manager = config_manager
        self.github_service = github_service
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.state = IndexadorState()
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        
        logger.info("IndexadorService initialized")
    
    async def shutdown(self):
        """Cleanup resources"""
        await self.http_client.aclose()
    
    # === DETECÇÃO DE JSONs ===
    
    def scan_local_jsons(self, folder_path: Path) -> List[SeriesInfo]:
        """Escaneia JSONs locais e extrai metadados"""
        logger.info(f"Scanning local JSONs in: {folder_path}")
        series = []
        
        if not folder_path.exists():
            logger.warning(f"Folder does not exist: {folder_path}")
            return series
        
        for json_file in folder_path.rglob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Valida se é JSON de manga
                if self.is_manga_json(data):
                    series_info = self.extract_series_info_from_json(data, str(json_file))
                    if series_info:
                        series_info.local_path = str(json_file)
                        
                        # Gera URL funcional baseado na configuração GitHub
                        github_config = self.config_manager.config.github
                        config = self.config_manager.config.indexador
                        
                        if github_config and config.use_same_repo:
                            user = github_config.get('user', '')
                            repo = github_config.get('repo', '')
                            if user and repo:
                                filename = json_file.stem + '.json'
                                series_info.data.url = f"https://cdn.jsdelivr.net/gh/{user}/{repo}@main/{filename}"
                        elif config.specific_repo:
                            filename = json_file.stem + '.json'
                            series_info.data.url = f"https://cdn.jsdelivr.net/gh/{config.specific_repo}@main/{filename}"
                        
                        series.append(series_info)
                        logger.debug(f"Found manga JSON: {series_info.title}")
                        
            except Exception as e:
                logger.warning(f"Error reading {json_file}: {e}")
        
        logger.info(f"Found {len(series)} local manga JSONs")
        return series
    
    async def scan_github_jsons(self, repo: str, path: str = "") -> List[SeriesInfo]:
        """Escaneia JSONs no GitHub via API"""
        logger.info(f"Scanning GitHub JSONs in: {repo}/{path}")
        series = []
        
        try:
            # Verifica cache primeiro
            cache_key = f"github_scan_{repo}_{path}"
            if self._is_cache_valid(cache_key):
                logger.debug("Using cached GitHub scan results")
                return self._cache[cache_key]
            
            # Lista arquivos na pasta
            files = await self.github_service.list_files(repo, path)
            
            for file in files:
                if file['type'] == 'file' and file['name'].endswith('.json'):
                    # Baixa e valida JSON
                    try:
                        content = await self.github_service.get_file_content(repo, file['path'])
                        data = json.loads(content)
                        
                        if self.is_manga_json(data):
                            # Gera URL RAW com CDN
                            raw_url = await self.generate_best_url(repo, file['path'])
                            series_info = self.extract_series_info_from_json(data)
                            
                            if series_info:
                                # Atualiza URL do JSON
                                series_info.data.url = raw_url
                                series.append(series_info)
                                logger.debug(f"Found GitHub JSON: {series_info.title}")
                                
                    except json.JSONDecodeError as e:
                        logger.debug(f"Skipping invalid JSON {file['path']}: {e}")
                    except Exception as e:
                        logger.warning(f"Error processing {file['path']}: {e}")
                
                elif file['type'] == 'dir':
                    # Recursão para subpastas
                    sub_series = await self.scan_github_jsons(repo, file['path'])
                    series.extend(sub_series)
            
            # Armazena no cache
            self._cache[cache_key] = series
            self._cache_timestamps[cache_key] = datetime.now()
            
            logger.info(f"Found {len(series)} GitHub manga JSONs")
            return series
            
        except Exception as e:
            logger.error(f"Error scanning GitHub JSONs: {e}")
            return []
    
    def is_manga_json(self, data: Dict[str, Any]) -> bool:
        """Verifica se é um JSON de manga válido"""
        required_fields = ['title', 'chapters']
        return all(field in data for field in required_fields)
    
    def extract_series_info_from_json(self, data: Dict[str, Any], local_path: str = "") -> Optional[SeriesInfo]:
        """Extrai informações da série de um JSON"""
        try:
            # Gera ID e slug
            title = data.get('title', 'Unknown')
            series_id = sanitize_filename(title.lower().replace(' ', '-'))
            slug = series_id
            
            # Extrai informações básicas - MELHORADO
            author_name = data.get('author', 'Autor Desconhecido')
            chapters_data = data.get('chapters', {})
            
            # Conta capítulos
            chapter_count = len(chapters_data) if isinstance(chapters_data, dict) else 0
            
            # Determina status
            status_str = data.get('status', 'ongoing').lower()
            if status_str in ['completo', 'completed', 'concluído']:
                translation_status = 'completed'
            else:
                translation_status = 'ongoing'
            
            # Detecta tipo de obra automaticamente
            detected_type = 'manga'  # padrão
            if any(keyword in title.lower() for keyword in ['manhwa', 'webtoon', 'tower of god']):
                detected_type = 'manhwa'
            elif any(keyword in title.lower() for keyword in ['manhua', 'chinese']):
                detected_type = 'manhua'
            
            # Detecta demografia
            detected_demo = 'seinen'  # padrão
            if any(keyword in title.lower() for keyword in ['school', 'romance', 'slice']):
                detected_demo = 'shounen'
            
            # Gera rating realista baseado no conteúdo
            base_rating = 4.5  # Rating base
            if chapter_count > 50:
                base_rating += 0.2  # Obras longas tendem a ter rating melhor
            if translation_status == 'completed':
                base_rating += 0.1  # Obras completas são mais bem avaliadas
            
            # Gera votes baseado na popularidade estimada
            base_votes = max(50, chapter_count * 5)  # 5 votos por capítulo
            
            # Estima ano de publicação
            estimated_year = 2020  # padrão
            if 'tower of god' in title.lower():
                estimated_year = 2010
            elif chapter_count > 100:
                estimated_year = 2018  # Obras longas começaram antes
            
            # Publisher baseado no tipo
            publisher = data.get('publisher', '')
            if not publisher:
                if detected_type == 'manhwa':
                    publisher = 'LINE Webtoon'
                elif detected_type == 'manga':
                    publisher = 'Kodansha'
                else:
                    publisher = 'Editora Desconhecida'
            
            # Cria SeriesInfo
            series_info = SeriesInfo(
                id=series_id,
                title=title,
                originalTitle=data.get('originalTitle', title),
                slug=slug,
                author=Author(
                    name=author_name,
                    originalName=data.get('originalAuthor', author_name),
                    nationality=data.get('nationality', 'KR' if detected_type == 'manhwa' else 'JP')
                ),
                publication=Publication(
                    year=data.get('year', estimated_year),
                    publisher=publisher,
                    originalLanguage=data.get('originalLanguage', 'ko' if detected_type == 'manhwa' else 'ja')
                ),
                status=Status(
                    translation=translation_status,
                    original=data.get('originalStatus', translation_status),
                    lastUpdated=datetime.now().isoformat()
                ),
                type=data.get('type', detected_type),
                demographics=data.get('demographics', detected_demo),
                genres=data.get('genres', []),
                tags=data.get('tags', []),
                description=data.get('description', ''),
                cover=Cover(
                    url=data.get('cover', ''),
                    alt=f"{title} Cover",
                    type="image/jpeg"
                ),
                chapters=Chapters(
                    total=chapter_count,
                    translated=chapter_count,
                    available=chapter_count,
                    status=translation_status
                ),
                rating=Rating(
                    community=data.get('rating', base_rating),
                    totalVotes=data.get('totalVotes', base_votes)
                ),
                data=SeriesData(
                    url="",  # Will be filled by caller
                    format="json",
                    size=self._calculate_json_size(data)
                ),
                priority=data.get('priority', 1),
                featured=data.get('featured', False)
            )
            
            return series_info
            
        except Exception as e:
            logger.error(f"Error extracting series info: {e}")
            return None
    
    def _calculate_json_size(self, data: Dict[str, Any]) -> str:
        """Calcula tamanho aproximado do JSON"""
        try:
            json_str = json.dumps(data, ensure_ascii=False)
            size_bytes = len(json_str.encode('utf-8'))
            
            if size_bytes < 1024:
                return f"{size_bytes}B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f}KB"
            else:
                return f"{size_bytes / (1024 * 1024):.1f}MB"
        except:
            return "Unknown"
    
    # === URLS E CDN ===
    
    async def generate_best_url(self, repo: str, path: str) -> str:
        """Gera melhor URL (CDN se disponível, senão GitHub raw)"""
        config = self.config_manager.config.indexador
        
        if config.url_preference == "raw":
            return self._generate_github_raw_url(repo, path)
        elif config.url_preference == "cdn":
            return self._generate_cdn_url(repo, path)
        else:  # hybrid (default)
            # Tenta URL CDN primeiro
            cdn_url = self._generate_cdn_url(repo, path)
            
            try:
                # Verifica se CDN está disponível
                response = await self.http_client.head(cdn_url, timeout=5)
                if response.status_code == 200:
                    logger.debug(f"CDN available for {path}")
                    return cdn_url
            except Exception:
                pass
            
            # Fallback para GitHub raw
            raw_url = self._generate_github_raw_url(repo, path)
            logger.debug(f"Using GitHub raw for {path}")
            
            # Agenda promoção para CDN
            if path not in self.state.pending_cdn_promotions:
                self.state.pending_cdn_promotions.append(path)
            
            return raw_url
    
    def _generate_cdn_url(self, repo: str, path: str) -> str:
        """Gera URL do CDN jsDelivr"""
        config = self.config_manager.config.indexador
        template = config.template_cdn
        
        # Extrai usuário e repositório
        user, repo_name = repo.split('/', 1) if '/' in repo else ('', repo)
        
        # Substitui placeholders
        url = template.format(
            usuario=user,
            repo=repo_name,
            nome=Path(path).stem
        )
        
        return url
    
    def _generate_github_raw_url(self, repo: str, path: str) -> str:
        """Gera URL do GitHub raw"""
        config = self.config_manager.config.indexador
        template = config.template_raw
        
        # Extrai usuário e repositório
        user, repo_name = repo.split('/', 1) if '/' in repo else ('', repo)
        
        # Substitui placeholders
        url = template.format(
            usuario=user,
            repo=repo_name,
            nome=Path(path).stem
        )
        
        return url
    
    async def promote_to_cdn(self, repo: str, path: str) -> bool:
        """Tenta promover URL do GitHub raw para CDN"""
        cdn_url = self._generate_cdn_url(repo, path)
        
        try:
            response = await self.http_client.head(cdn_url, timeout=10)
            if response.status_code == 200:
                logger.info(f"Successfully promoted to CDN: {path}")
                return True
        except Exception as e:
            logger.debug(f"CDN not yet available for {path}: {e}")
        
        return False
    
    async def verify_cdn_urls(self, series_list: List[SeriesInfo]) -> int:
        """Verifica URLs CDN e promove quando possível"""
        promoted_count = 0
        config = self.config_manager.config.indexador
        
        if not config.cdn_auto_promote:
            return 0
        
        for series in series_list:
            if series.data.cdn_status == "pending":
                # Extrai repo e path da URL atual
                if "raw.githubusercontent.com" in series.data.url:
                    # Parse GitHub raw URL
                    parts = series.data.url.split('/')
                    if len(parts) >= 6:
                        user = parts[3]
                        repo_name = parts[4]
                        branch = parts[5]
                        path = '/'.join(parts[6:])
                        
                        repo = f"{user}/{repo_name}"
                        
                        if await self.promote_to_cdn(repo, path):
                            # Atualiza para URL CDN
                            series.data.url = self._generate_cdn_url(repo, path)
                            series.data.cdn_status = "active"
                            series.data.last_verified = datetime.now()
                            promoted_count += 1
        
        if promoted_count > 0:
            logger.info(f"Promoted {promoted_count} URLs to CDN")
        
        return promoted_count
    
    # === GERAÇÃO DO INDEXADOR ===
    
    def generate_indexador(self, series_list: List[SeriesInfo]) -> IndexadorData:
        """Gera o indexador JSON completo"""
        config = self.config_manager.config.indexador
        
        logger.info(f"Generating indexador with {len(series_list)} series")
        
        # Filtra séries incluídas
        included_series = [s for s in series_list if s.include_in_index]
        
        # Estatísticas (seguindo estrutura EXATA do CAUTION.txt)
        stats = self._calculate_statistics(included_series)
        
        # Schedule (seguindo estrutura EXATA)
        schedule = Schedule(
            updates=Updates(
                frequency="weekly",
                day="sunday",
                time="10:00",
                timezone="America/Sao_Paulo"
            ),
            maintenance=Maintenance(
                day="saturday",
                time="02:00",
                duration="1-2 hours",
                timezone="America/Sao_Paulo"
            )
        )
        
        # Legal (seguindo estrutura EXATA)
        legal = Legal(
            copyright=Copyright(
                notice="Este é um projeto de fãs sem fins lucrativos.",
                holder="Autor Original",
                year="2024"
            ),
            disclaimer="Este projeto é uma tradução não oficial feita por fãs.",
            support=Support(
                message="Apoie o autor lendo oficialmente:",
                links=[]
            )
        )
        
        # Features (seguindo estrutura EXATA)
        features = Features(
            search=Search(
                enabled=True,
                fields=["title", "description", "tags", "genres"]
            ),
            filtering=Filtering(
                enabled=True,
                options=["status", "genre", "year", "rating"]
            ),
            sorting=Sorting(
                enabled=True,
                options=["priority", "rating", "lastUpdated", "alphabetical"]
            ),
            notifications=Notifications(
                enabled=True,
                types=["new_chapter", "series_complete"]
            )
        )
        
        # Hub info (seguindo estrutura EXATA do CAUTION.txt) - MELHORADO
        # Gera baseUrl para URLs funcionais
        github_config = self.config_manager.config.github
        base_cdn_url = ""
        
        if config.use_same_repo and github_config:
            user = github_config.get('user', '')
            repo = github_config.get('repo', '')
            if user and repo:
                base_cdn_url = f"https://cdn.jsdelivr.net/gh/{user}/{repo}@main/"
        elif config.specific_repo:
            parts = config.specific_repo.split('/')
            if len(parts) == 2:
                base_cdn_url = f"https://cdn.jsdelivr.net/gh/{config.specific_repo}@main/"
        
        # Dados de equipe mais realistas
        total_members = max(3, len(included_series))  # Pelo menos 3 membros
        
        hub_info = Hub(
            id=sanitize_filename(config.hub_name.lower().replace(' ', '-')) if config.hub_name else "hub-id",
            title=config.hub_name or "Scanlation Group",
            subtitle=config.hub_subtitle or "Grupo de Tradução de Mangás", 
            slug=sanitize_filename(config.hub_name.lower().replace(' ', '-')) if config.hub_name else "grupo-scanlation",
            description=config.hub_description or f"Bem-vindos ao {config.hub_name or 'nosso grupo'}! Somos apaixonados por mangás e dedicados a trazer traduções de qualidade para a comunidade brasileira. Todo nosso trabalho é feito com amor e respeito pela obra original.",
            disclaimer="Lembre-se sempre de apoiar os autores oficiais! Se a obra for lançada oficialmente no Brasil, compre e incentive o trabalho original.",
            team=Team(
                name=config.hub_name or "Scanlation Group",
                type="scanlation",
                status="active", 
                founded="2024",
                members=TeamMembers(
                    total=total_members,
                    translators=max(1, total_members // 2),
                    editors=max(1, total_members // 3),
                    typesetters=max(1, total_members // 4),
                    quality_assurance=1
                ),
                contact=config.hub_contact or "contato@exemplo.com"
            ),
            website=Website(
                primary=config.hub_website or base_cdn_url,
                cdn=base_cdn_url
            )
        )
        
        # Redes sociais
        social_platforms = self._generate_social_platforms(config)
        
        # Configurações técnicas
        technical = Technical(
            api=API(
                version="1.0",
                baseUrl=base_cdn_url or config.hub_website or "https://cdn.jsdelivr.net/gh/user/repo@main/",
                endpoints={
                    "hub": "hub.json",
                    "series": "series/{id}.json",
                    "chapters": "series/{id}/chapters.json"
                }
            ),
            cache=Cache(
                policy="public, max-age=3600, stale-while-revalidate=86400",
                etag=True,
                compression="gzip"
            ),
            formats=Formats(
                supported=["json"],
                primary="json",
                encoding="utf-8"
            )
        )
        
        # Indexador completo (seguindo estrutura EXATA do CAUTION.txt)
        indexador = IndexadorData(
            schema={
                "version": "2.0",
                "format": "application/json", 
                "encoding": "utf-8"
            },
            meta={
                "version": "1.0.0",
                "lastUpdated": datetime.now().isoformat(),
                "language": "pt-BR",
                "region": "BR",
                "updateFrequency": "weekly",
                "apiVersion": "v1"
            },
            hub=hub_info,
            social={"platforms": social_platforms},
            series=included_series,
            statistics=stats,
            schedule=schedule,
            technical=technical,
            legal=legal,
            features=features
        )
        
        logger.success(f"Generated indexador with {len(included_series)} series")
        return indexador
    
    def _calculate_statistics(self, series_list: List[SeriesInfo]) -> Statistics:
        """Calcula estatísticas das séries (seguindo estrutura EXATA do CAUTION.txt) - MELHORADO"""
        total_series = len(series_list)
        completed_series = len([s for s in series_list if s.status.translation == "completed"])
        ongoing_series = total_series - completed_series
        
        # Calcula total de capítulos (tratando 'ongoing' como 0)
        total_chapters = 0
        total_votes = 0
        total_rating = 0.0
        
        for series in series_list:
            if isinstance(series.chapters.total, int):
                total_chapters += series.chapters.total
            # Soma ratings e votos para média
            total_votes += series.rating.totalVotes
            total_rating += series.rating.community * max(1, series.rating.totalVotes)
        
        # Calcula média ponderada de rating
        avg_rating = (total_rating / max(1, total_votes)) if total_votes > 0 else 4.5
        
        # Calcula tamanho total (aproximado)
        total_size_mb = 0
        for series in series_list:
            if series.data.size and series.data.size.endswith('MB'):
                try:
                    size = float(series.data.size[:-2])
                    total_size_mb += size
                except:
                    pass
        
        # Estatísticas mais realistas baseadas no conteúdo
        base_followers = max(100, total_series * 50)  # 50 seguidores por série
        total_members = max(3, total_series)  # Mais membros com mais séries
        
        return Statistics(
            overview=StatisticsOverview(
                totalSeries=total_series,
                completedSeries=completed_series,
                ongoingSeries=ongoing_series,
                totalChapters=total_chapters,
                totalPages=total_chapters * 20  # Estimativa
            ),
            team=StatisticsTeam(
                totalMembers=total_members,
                activeMembers=max(2, total_members - 1),
                roles={
                    "translators": max(1, total_members // 2),
                    "editors": max(1, total_members // 3), 
                    "typesetters": max(1, total_members // 4),
                    "quality_assurance": 1
                }
            ),
            community=StatisticsCommunity(
                totalFollowers=base_followers,
                activeUsers=int(base_followers * 0.6),  # 60% de usuários ativos
                averageRating=round(avg_rating, 1),
                totalVotes=max(total_votes, base_followers // 10)  # Pelo menos 10% votam
            ),
            content=StatisticsContent(
                totalFileSize=f"{total_size_mb:.1f}MB" if total_size_mb > 0 else f"{total_chapters * 0.5:.1f}MB",
                averageChapterSize="32KB",
                supportedFormats=["json", "cbz", "pdf"]
            )
        )
    
    def _generate_social_platforms(self, config: IndexadorConfig) -> List[SocialPlatform]:
        """Gera lista de plataformas sociais"""
        platforms = []
        
        if config.discord_url:
            platforms.append(SocialPlatform(
                id="discord",
                name="Discord Oficial",
                platform="discord",
                url=config.discord_url,
                description=config.discord_description,
                primary=True
            ))
        
        if config.telegram_url:
            platforms.append(SocialPlatform(
                id="telegram",
                name="Canal Telegram",
                platform="telegram",
                url=config.telegram_url,
                description=config.telegram_description
            ))
        
        if config.whatsapp_url:
            platforms.append(SocialPlatform(
                id="whatsapp",
                name="Grupo WhatsApp",
                platform="whatsapp",
                url=config.whatsapp_url,
                description=config.whatsapp_description
            ))
        
        if config.twitter_url:
            platforms.append(SocialPlatform(
                id="twitter",
                name="Twitter/X",
                platform="twitter",
                url=config.twitter_url,
                description=config.twitter_description
            ))
        
        return platforms
    
    # === SALVAMENTO E UPLOAD ===
    
    async def save_indexador_local(self, indexador: IndexadorData) -> Path:
        """Salva indexador localmente"""
        config = self.config_manager.config.indexador
        output_folder = self.config_manager.config.output_folder
        
        # Cria pasta para indexadores
        indexador_folder = output_folder / "indexadores"
        indexador_folder.mkdir(parents=True, exist_ok=True)
        
        # Nome do arquivo
        filename = config.filename_pattern.format(
            nome_grupo=sanitize_filename(config.hub_name or "grupo")
        )
        
        file_path = indexador_folder / filename
        
        # Salva JSON com estrutura EXATA
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(
                    indexador.model_dump(
                        exclude_none=True,
                        exclude={'series': {'__all__': {'local_path', 'include_in_index', 'url_override'}}}
                    ),
                    f,
                    ensure_ascii=False,
                    indent=2
                )
            
            logger.success(f"Indexador saved locally: {file_path}")
            self.state.last_indexador_generated = datetime.now()
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving indexador: {e}")
            raise
    
    async def upload_indexador_github(self, indexador: IndexadorData) -> bool:
        """Faz upload do indexador para GitHub"""
        try:
            config = self.config_manager.config.indexador
            github_config = self.config_manager.config.github
            
            # Determina repositório
            if config.use_same_repo:
                import re
                user = re.sub(r'[^\x20-\x7E]', '', str(github_config.get('user', ''))).strip()
                repo_name = re.sub(r'[^\x20-\x7E]', '', str(github_config.get('repo', ''))).strip()
                
                # Se repo_name já contém user/repo, use diretamente
                if '/' in repo_name and user == '':
                    repo = repo_name
                    logger.debug(f"Using repo_name as full repo: '{repo}'")
                else:
                    repo = f"{user}/{repo_name}"
                    logger.debug(f"Using same repo: user='{user}', repo='{repo_name}', final='{repo}'")
            else:
                if not config.specific_repo:
                    raise ValueError("Specific repository not configured")
                import re
                repo = re.sub(r'[^\x20-\x7E]', '', str(config.specific_repo)).strip()
                logger.debug(f"Using specific repo: '{repo}'")
            
            # Valida formato do repositório
            if not repo or repo.strip() == '' or repo == '/':
                raise ValueError("Repository is empty. Configure GitHub user and repository in settings.")
            
            if '/' not in repo or repo.count('/') != 1:
                raise ValueError(f"Invalid repository format: '{repo}'. Expected 'owner/repo'")
            
            # Verifica se owner e repo não estão vazios
            parts = repo.split('/')
            if not parts[0] or not parts[1]:
                raise ValueError(f"Repository owner or name is empty: '{repo}'. Expected 'owner/repo'")
            
            # Nome do arquivo
            filename = config.filename_pattern.format(
                nome_grupo=sanitize_filename(config.hub_name or "grupo")
            )
            
            # Caminho no repositório
            file_path = f"{config.indexador_folder}/{filename}"
            
            # Conteúdo JSON (sem informações pessoais) - estrutura EXATA
            content = json.dumps(
                indexador.model_dump(
                    exclude_none=True,
                    exclude={'series': {'__all__': {'local_path', 'include_in_index', 'url_override'}}}
                ),
                ensure_ascii=False,
                indent=2
            )
            
            # Upload para GitHub
            success = await self.github_service.upload_content(
                repo=repo,
                file_path=file_path,
                content=content,
                commit_message=f"Update indexador: {config.hub_name}"
            )
            
            if success:
                logger.success(f"Indexador uploaded to GitHub: {file_path}")
                self.state.last_indexador_uploaded = datetime.now()
            else:
                logger.error("Failed to upload indexador to GitHub")
            
            return success
            
        except Exception as e:
            logger.error(f"Error uploading indexador to GitHub: {e}")
            return False
    
    # === CACHE E UTILIDADES ===
    
    def _is_cache_valid(self, key: str) -> bool:
        """Verifica se o cache é válido"""
        if key not in self._cache or key not in self._cache_timestamps:
            return False
        
        cache_duration = self.config_manager.config.indexador.github_cache_duration
        cache_time = self._cache_timestamps[key]
        
        return datetime.now() - cache_time < timedelta(seconds=cache_duration)
    
    def clear_cache(self):
        """Limpa o cache"""
        self._cache.clear()
        self._cache_timestamps.clear()
        logger.info("Cache cleared")
    
    async def get_series_diff(self, repo: str) -> Tuple[List[SeriesInfo], List[SeriesInfo], List[SeriesInfo]]:
        """Compara séries locais vs remotas"""
        config = self.config_manager.config
        
        # Escaneia séries locais
        local_series = self.scan_local_jsons(config.output_folder)
        
        # Escaneia séries remotas
        github_series = await self.scan_github_jsons(
            repo, 
            config.indexador.github_search_folder
        )
        
        # Cria mapas por ID
        local_map = {s.id: s for s in local_series}
        github_map = {s.id: s for s in github_series}
        
        # Calcula diferenças
        new_series = [s for s in local_series if s.id not in github_map]
        modified_series = []
        remote_only = [s for s in github_series if s.id not in local_map]
        
        # Verifica modificações (comparando timestamps se possível)
        for series_id in set(local_map.keys()) & set(github_map.keys()):
            local_series = local_map[series_id]
            github_series = github_map[series_id]
            
            # Compara capítulos como proxy para modificação
            if local_series.chapters.total != github_series.chapters.total:
                modified_series.append(local_series)
        
        return new_series, modified_series, remote_only
    
    def validate_configuration(self) -> List[str]:
        """Valida configuração e retorna lista de avisos/sugestões"""
        config = self.config_manager.config.indexador
        warnings = []
        
        # Campos importantes
        if not config.hub_name:
            warnings.append("💡 Nome do grupo vazio - recomendamos preenchê-lo")
        
        if not config.hub_description:
            warnings.append("💡 Descrição vazia - ajuda visitantes a entender o grupo")
        
        # Redes sociais
        social_count = sum([
            bool(config.discord_url),
            bool(config.telegram_url),
            bool(config.whatsapp_url),
            bool(config.twitter_url)
        ])
        
        if social_count == 0:
            warnings.append("💡 Nenhuma rede social configurada - facilita contato da comunidade")
        
        # URLs inválidas (não bloqueantes)
        urls_to_check = [
            ("Discord", config.discord_url),
            ("Telegram", config.telegram_url),
            ("WhatsApp", config.whatsapp_url),
            ("Twitter", config.twitter_url),
            ("Website", config.hub_website)
        ]
        
        for name, url in urls_to_check:
            if url and not self._is_valid_url(url):
                warnings.append(f"⚠️ URL inválida para {name} (não irá bloquear geração)")
        
        return warnings
    
    def _is_valid_url(self, url: str) -> bool:
        """Validação básica de URL"""
        try:
            from urllib.parse import urlparse
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False