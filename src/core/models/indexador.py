from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime


class SocialPlatform(BaseModel):
    """Rede social do grupo - estrutura EXATA do CAUTION.txt"""
    id: str
    name: str
    platform: str
    url: str
    description: str
    primary: bool = False
    memberCount: Optional[str] = None
    features: List[str] = []


class Icon(BaseModel):
    """Ícone/imagem - estrutura EXATA"""
    url: str
    alt: str
    type: str


class TeamMembers(BaseModel):
    """Membros da equipe - estrutura EXATA"""
    total: int
    translators: int
    editors: int
    typesetters: int
    quality_assurance: int


class Team(BaseModel):
    """Equipe do grupo - estrutura EXATA"""
    name: str
    type: str
    status: str
    founded: str
    members: TeamMembers
    contact: str


class Website(BaseModel):
    """Website do hub - estrutura EXATA"""
    primary: str
    cdn: str


class Hub(BaseModel):
    """Informações do hub - estrutura EXATA do CAUTION.txt"""
    id: str
    title: str
    subtitle: str
    slug: str
    icon: Optional[Icon] = None
    description: str
    disclaimer: str
    team: Team
    website: Website


class Author(BaseModel):
    """Autor da série - estrutura EXATA"""
    name: str
    originalName: str
    nationality: str


class Publication(BaseModel):
    """Publicação da série - estrutura EXATA"""
    year: int
    publisher: str
    originalLanguage: str


class Status(BaseModel):
    """Status da série - estrutura EXATA"""
    translation: str
    original: str
    lastUpdated: str


class Cover(BaseModel):
    """Capa da série - estrutura EXATA"""
    url: str
    alt: str
    type: str


class Chapters(BaseModel):
    """Capítulos da série - estrutura EXATA"""
    total: Union[int, str]  # Pode ser número ou "ongoing"
    translated: int
    available: int
    status: str


class Rating(BaseModel):
    """Avaliação da série - estrutura EXATA"""
    community: float
    totalVotes: int


class Data(BaseModel):
    """Dados da série - estrutura EXATA"""
    url: str
    format: str
    size: str


class Series(BaseModel):
    """Série completa - estrutura EXATA do CAUTION.txt"""
    id: str
    title: str
    originalTitle: str
    slug: str
    author: Author
    publication: Publication
    status: Status
    type: str
    demographics: str
    genres: List[str]
    tags: List[str]
    cover: Cover
    description: str
    chapters: Chapters
    rating: Rating
    data: Data
    priority: int
    featured: Optional[bool] = None
    special: Optional[bool] = None
    latest: Optional[bool] = None
    completionDate: Optional[str] = None
    updateSchedule: Optional[str] = None
    
    # Campos para compatibilidade interna (não aparecem no JSON final)
    local_path: Optional[str] = None
    include_in_index: bool = True
    url_override: Optional[str] = None


class StatisticsOverview(BaseModel):
    """Estatísticas overview - estrutura EXATA"""
    totalSeries: int
    completedSeries: int
    ongoingSeries: int
    totalChapters: int
    totalPages: int


class StatisticsTeam(BaseModel):
    """Estatísticas da equipe - estrutura EXATA"""
    totalMembers: int
    activeMembers: int
    roles: Dict[str, int]


class StatisticsCommunity(BaseModel):
    """Estatísticas da comunidade - estrutura EXATA"""
    totalFollowers: int
    activeUsers: int
    averageRating: float
    totalVotes: int


class StatisticsContent(BaseModel):
    """Estatísticas de conteúdo - estrutura EXATA"""
    totalFileSize: str
    averageChapterSize: str
    supportedFormats: List[str]


class Statistics(BaseModel):
    """Estatísticas completas - estrutura EXATA"""
    overview: StatisticsOverview
    team: StatisticsTeam
    community: StatisticsCommunity
    content: StatisticsContent


class Updates(BaseModel):
    """Atualizações do cronograma - estrutura EXATA"""
    frequency: str
    day: str
    time: str
    timezone: str


class Maintenance(BaseModel):
    """Manutenção do cronograma - estrutura EXATA"""
    day: str
    time: str
    duration: str
    timezone: str


class Schedule(BaseModel):
    """Cronograma - estrutura EXATA"""
    updates: Updates
    maintenance: Maintenance


class API(BaseModel):
    """API técnica - estrutura EXATA"""
    version: str
    baseUrl: str
    endpoints: Dict[str, str]


class Cache(BaseModel):
    """Cache técnico - estrutura EXATA"""
    policy: str
    etag: bool
    compression: str


class Formats(BaseModel):
    """Formatos técnicos - estrutura EXATA"""
    supported: List[str]
    primary: str
    encoding: str


class Technical(BaseModel):
    """Informações técnicas - estrutura EXATA"""
    api: API
    cache: Cache
    formats: Formats


class Copyright(BaseModel):
    """Copyright legal - estrutura EXATA"""
    notice: str
    holder: str
    year: str


class SupportLink(BaseModel):
    """Link de suporte - estrutura EXATA"""
    name: str
    url: str
    language: str


class Support(BaseModel):
    """Suporte legal - estrutura EXATA"""
    message: str
    links: List[SupportLink]


class Legal(BaseModel):
    """Informações legais - estrutura EXATA"""
    copyright: Copyright
    disclaimer: str
    support: Support


class Search(BaseModel):
    """Busca de features - estrutura EXATA"""
    enabled: bool
    fields: List[str]


class Filtering(BaseModel):
    """Filtros de features - estrutura EXATA"""
    enabled: bool
    options: List[str]


class Sorting(BaseModel):
    """Ordenação de features - estrutura EXATA"""
    enabled: bool
    options: List[str]


class Notifications(BaseModel):
    """Notificações de features - estrutura EXATA"""
    enabled: bool
    types: List[str]


class Features(BaseModel):
    """Features - estrutura EXATA"""
    search: Search
    filtering: Filtering
    sorting: Sorting
    notifications: Notifications


class IndexadorOriginal(BaseModel):
    """Estrutura EXATA do JSON do CAUTION.txt"""
    schema: Dict[str, str]  # Campo direto sem alias
    meta: Dict[str, Any]
    hub: Hub
    social: Dict[str, List[SocialPlatform]]
    series: List[Series]
    statistics: Statistics
    schedule: Schedule
    technical: Technical
    legal: Legal
    features: Features


# Aliases para compatibilidade com código existente
IndexadorData = IndexadorOriginal
HubInfo = Hub  
SeriesInfo = Series
SeriesData = Data


# Classes de configuração e estado (para compatibilidade)
class IndexadorConfig(BaseModel):
    """Configuração do indexador"""
    enabled: bool = True
    hub_name: str = ""
    hub_subtitle: str = ""
    hub_description: str = ""
    hub_website: str = ""
    hub_contact: str = ""  # Campo que estava faltando
    discord_url: str = ""
    discord_description: str = ""
    telegram_url: str = ""
    telegram_description: str = ""
    whatsapp_url: str = ""
    whatsapp_description: str = ""
    twitter_url: str = ""
    twitter_description: str = ""
    url_preference: str = "hybrid"  # "cdn", "raw", "hybrid"
    cdn_auto_promote: bool = True
    template_cdn: str = "https://cdn.jsdelivr.net/gh/{usuario}/{repo}@main/{nome}.json"
    template_raw: str = "https://raw.githubusercontent.com/{usuario}/{repo}/main/{nome}.json"
    use_same_repo: bool = True
    specific_repo: str = ""
    indexador_folder: str = "hub"
    filename_pattern: str = "index_{nome_grupo}.json"
    github_search_folder: str = ""
    github_cache_duration: int = 300  # 5 minutos
    # Campos GitHub que estavam faltando
    github_auto_detect: bool = True
    github_monitor_changes: bool = False
    github_include_subfolders: bool = True
    # Campos de automação que estavam faltando
    auto_update: bool = False
    confirm_before_upload: bool = True


class IndexadorState(BaseModel):
    """Estado interno do indexador"""
    last_indexador_generated: Optional[datetime] = None
    last_indexador_uploaded: Optional[datetime] = None
    pending_cdn_promotions: List[str] = []
    series_count: int = 0
    last_scan_time: Optional[datetime] = None