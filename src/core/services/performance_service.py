"""
Performance Analytics and Optimization Service
Provides comprehensive monitoring, analysis, and automatic optimization
"""

import time
import psutil
import statistics
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from loguru import logger


@dataclass
class PerformanceMetric:
    """Single performance measurement"""
    timestamp: float
    scan_time: float
    folder_count: int
    file_count: int
    cache_hit_rate: float
    memory_usage_mb: float
    cpu_usage_percent: float
    worker_count: int
    
    @property
    def scan_rate(self) -> float:
        """Folders per second"""
        return self.folder_count / self.scan_time if self.scan_time > 0 else 0
    
    @property
    def performance_grade(self) -> str:
        """Overall performance grade A-F"""
        score = 0.0
        
        # Scan speed (40% of score)
        if self.scan_rate > 10:
            score += 40
        elif self.scan_rate > 5:
            score += 30
        elif self.scan_rate > 2:
            score += 20
        elif self.scan_rate > 1:
            score += 10
        
        # Cache performance (30% of score)
        if self.cache_hit_rate > 90:
            score += 30
        elif self.cache_hit_rate > 70:
            score += 20
        elif self.cache_hit_rate > 50:
            score += 15
        elif self.cache_hit_rate > 20:
            score += 10
        
        # Resource efficiency (30% of score)
        memory_efficiency = min(30, max(0, 30 - (self.memory_usage_mb - 100) / 20))
        cpu_efficiency = min(15, max(0, 15 - self.cpu_usage_percent / 4))
        score += memory_efficiency + cpu_efficiency
        
        # Convert to grade
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"


@dataclass
class PerformanceAnalysis:
    """Analysis of performance trends and recommendations"""
    current_grade: str
    avg_scan_time: float
    avg_cache_hit_rate: float
    avg_memory_usage: float
    performance_trend: str  # "improving", "stable", "declining"
    bottlenecks: List[str]
    recommendations: List[str]
    optimal_worker_count: int


class PerformanceService:
    """
    Performance analytics and optimization service
    
    Features:
    - Real-time performance monitoring and grading
    - Historical performance tracking and trend analysis
    - Automatic bottleneck detection
    - Dynamic optimization recommendations
    - Automatic worker count optimization
    - System resource monitoring with warnings
    """
    
    def __init__(self, max_history_size: int = 100):
        self.max_history_size = max_history_size
        self.performance_history: List[PerformanceMetric] = []
        
        # System monitoring
        self.system_cpu_count = psutil.cpu_count() or 1
        self.system_memory_gb = psutil.virtual_memory().total / (1024**3)
        
        # Optimization thresholds
        self.memory_warning_mb = 500
        self.cpu_warning_percent = 80
        self.cache_target_rate = 85
        
        logger.info(f"PerformanceService initialized: {self.system_cpu_count} CPU cores, "
                   f"{self.system_memory_gb:.1f}GB RAM")
    
    def record_scan_performance(
        self,
        scan_time: float,
        folder_count: int,
        file_count: int,
        cache_hit_rate: float,
        worker_count: int
    ) -> Optional[PerformanceMetric]:
        """
        Record a performance measurement
        
        Args:
            scan_time: Total scan time in seconds
            folder_count: Number of folders scanned
            file_count: Total number of files processed
            cache_hit_rate: Cache hit rate percentage (0-100)
            worker_count: Number of workers used
            
        Returns:
            PerformanceMetric object
        """
        try:
            # Get current system metrics
            memory_usage_mb = self._get_current_memory_usage()
            cpu_usage_percent = self._get_current_cpu_usage()
            
            # Create performance metric
            metric = PerformanceMetric(
                timestamp=time.time(),
                scan_time=scan_time,
                folder_count=folder_count,
                file_count=file_count,
                cache_hit_rate=cache_hit_rate,
                memory_usage_mb=memory_usage_mb,
                cpu_usage_percent=cpu_usage_percent,
                worker_count=worker_count
            )
            
            # Add to history
            self.performance_history.append(metric)
            
            # Trim history if needed
            if len(self.performance_history) > self.max_history_size:
                self.performance_history.pop(0)
            
            logger.debug(f"Performance recorded: {metric.performance_grade} grade, "
                        f"{metric.scan_rate:.1f} folders/s, {cache_hit_rate:.1f}% cache hit")
            
            return metric
            
        except Exception as e:
            logger.error(f"Error recording performance: {e}")
            return None
    
    def get_current_performance_grade(self) -> str:
        """Get current performance grade"""
        if not self.performance_history:
            return "N/A"
        
        return self.performance_history[-1].performance_grade
    
    def analyze_performance(self) -> PerformanceAnalysis:
        """
        Analyze performance trends and provide recommendations
        
        Returns:
            PerformanceAnalysis with trends and recommendations
        """
        if len(self.performance_history) < 2:
            return PerformanceAnalysis(
                current_grade="N/A",
                avg_scan_time=0.0,
                avg_cache_hit_rate=0.0,
                avg_memory_usage=0.0,
                performance_trend="unknown",
                bottlenecks=[],
                recommendations=["Need more performance data"],
                optimal_worker_count=4
            )
        
        # Calculate averages
        recent_metrics = self.performance_history[-10:]  # Last 10 measurements
        
        avg_scan_time = statistics.mean(m.scan_time for m in recent_metrics)
        avg_cache_hit_rate = statistics.mean(m.cache_hit_rate for m in recent_metrics)
        avg_memory_usage = statistics.mean(m.memory_usage_mb for m in recent_metrics)
        current_grade = recent_metrics[-1].performance_grade
        
        # Analyze trends
        performance_trend = self._analyze_performance_trend()
        
        # Detect bottlenecks
        bottlenecks = self._detect_bottlenecks(recent_metrics)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(recent_metrics, bottlenecks)
        
        # Calculate optimal worker count
        optimal_worker_count = self._calculate_optimal_worker_count(recent_metrics)
        
        return PerformanceAnalysis(
            current_grade=current_grade,
            avg_scan_time=avg_scan_time,
            avg_cache_hit_rate=avg_cache_hit_rate,
            avg_memory_usage=avg_memory_usage,
            performance_trend=performance_trend,
            bottlenecks=bottlenecks,
            recommendations=recommendations,
            optimal_worker_count=optimal_worker_count
        )
    
    def get_optimization_suggestions(self) -> List[str]:
        """Get current optimization suggestions"""
        analysis = self.analyze_performance()
        return analysis.recommendations
    
    def calculate_optimal_worker_count(self) -> int:
        """Calculate optimal number of workers for current system"""
        analysis = self.analyze_performance()
        return analysis.optimal_worker_count
    
    def is_performance_degrading(self) -> bool:
        """Check if performance is degrading over time"""
        analysis = self.analyze_performance()
        return analysis.performance_trend == "declining"
    
    def get_system_resource_status(self) -> Dict[str, Any]:
        """Get current system resource status"""
        try:
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            return {
                "memory_used_mb": (memory.used / (1024**2)),
                "memory_available_mb": (memory.available / (1024**2)),
                "memory_percent": memory.percent,
                "cpu_percent": cpu_percent,
                "cpu_count": self.system_cpu_count,
                "warnings": self._get_resource_warnings(memory.percent, cpu_percent)
            }
        except Exception as e:
            logger.error(f"Error getting system resource status: {e}")
            return {}
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        if not self.performance_history:
            return {"status": "No data available"}
        
        analysis = self.analyze_performance()
        latest_metric = self.performance_history[-1]
        resource_status = self.get_system_resource_status()
        
        return {
            "current_grade": analysis.current_grade,
            "scan_rate": latest_metric.scan_rate,
            "cache_hit_rate": analysis.avg_cache_hit_rate,
            "memory_usage_mb": analysis.avg_memory_usage,
            "performance_trend": analysis.performance_trend,
            "bottlenecks": analysis.bottlenecks,
            "recommendations": analysis.recommendations[:3],  # Top 3 recommendations
            "optimal_worker_count": analysis.optimal_worker_count,
            "system_resources": resource_status
        }
    
    def export_performance_data(self, export_path: Path) -> bool:
        """Export performance data for analysis"""
        try:
            export_data = {
                "export_time": time.time(),
                "system_info": {
                    "cpu_count": self.system_cpu_count,
                    "memory_gb": self.system_memory_gb
                },
                "performance_history": [asdict(metric) for metric in self.performance_history],
                "analysis": asdict(self.analyze_performance())
            }
            
            import json
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Performance data exported to: {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting performance data: {e}")
            return False
    
    # Private methods
    
    def _get_current_memory_usage(self) -> float:
        """Get current process memory usage in MB"""
        try:
            import os
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / (1024**2)
        except Exception:
            return 0.0
    
    def _get_current_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        try:
            return psutil.cpu_percent(interval=0.1)
        except Exception:
            return 0.0
    
    def _analyze_performance_trend(self) -> str:
        """Analyze if performance is improving, stable, or declining"""
        if len(self.performance_history) < 5:
            return "unknown"
        
        # Compare recent performance vs older performance
        recent_metrics = self.performance_history[-5:]
        older_metrics = self.performance_history[-10:-5] if len(self.performance_history) >= 10 else []
        
        if not older_metrics:
            return "stable"
        
        recent_avg_rate = statistics.mean(m.scan_rate for m in recent_metrics)
        older_avg_rate = statistics.mean(m.scan_rate for m in older_metrics)
        
        rate_change = (recent_avg_rate - older_avg_rate) / older_avg_rate if older_avg_rate > 0 else 0
        
        if rate_change > 0.1:
            return "improving"
        elif rate_change < -0.1:
            return "declining" 
        else:
            return "stable"
    
    def _detect_bottlenecks(self, metrics: List[PerformanceMetric]) -> List[str]:
        """Detect performance bottlenecks"""
        bottlenecks = []
        
        avg_memory = statistics.mean(m.memory_usage_mb for m in metrics)
        avg_cpu = statistics.mean(m.cpu_usage_percent for m in metrics)
        avg_cache_rate = statistics.mean(m.cache_hit_rate for m in metrics)
        avg_scan_rate = statistics.mean(m.scan_rate for m in metrics)
        
        if avg_memory > self.memory_warning_mb:
            bottlenecks.append("high_memory")
        
        if avg_cpu > self.cpu_warning_percent:
            bottlenecks.append("high_cpu")
        
        if avg_cache_rate < self.cache_target_rate:
            bottlenecks.append("low_cache_hit_rate")
        
        if avg_scan_rate < 2:
            bottlenecks.append("slow_scan_rate")
        
        return bottlenecks
    
    def _generate_recommendations(self, metrics: List[PerformanceMetric], bottlenecks: List[str]) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        if "high_memory" in bottlenecks:
            recommendations.append("Reduza o número de workers para diminuir uso de memória")
            recommendations.append("Considere fechar outras aplicações para liberar memória")
        
        if "high_cpu" in bottlenecks:
            recommendations.append("Sistema sobrecarregado - reduza workers ou feche outros programas")
        
        if "low_cache_hit_rate" in bottlenecks:
            recommendations.append("Cache com baixa eficiência - execute otimização do cache")
            recommendations.append("Varreduras frequentes reduzem eficiência do cache")
        
        if "slow_scan_rate" in bottlenecks:
            avg_workers = statistics.mean(m.worker_count for m in metrics)
            if avg_workers < self.system_cpu_count - 1:
                recommendations.append(f"Aumente workers para {min(self.system_cpu_count - 1, avg_workers + 2)} para melhor performance")
            else:
                recommendations.append("Varredura lenta - verificar se há problemas no disco")
        
        # General recommendations
        avg_cache_rate = statistics.mean(m.cache_hit_rate for m in metrics)
        if avg_cache_rate < 50:
            recommendations.append("Cache quase vazio - varreduras subsequentes serão mais rápidas")
        
        if not recommendations:
            recommendations.append("Performance boa - nenhuma otimização necessária")
        
        return recommendations
    
    def _calculate_optimal_worker_count(self, metrics: List[PerformanceMetric]) -> int:
        """Calculate optimal worker count based on system and performance"""
        if not metrics:
            return 4
        
        # Start with system capabilities
        base_workers = max(2, self.system_cpu_count - 1)  # Leave one core free
        
        # Adjust based on memory usage
        avg_memory = statistics.mean(m.memory_usage_mb for m in metrics)
        if avg_memory > self.memory_warning_mb:
            base_workers = max(2, base_workers - 2)
        
        # Adjust based on CPU usage
        avg_cpu = statistics.mean(m.cpu_usage_percent for m in metrics)
        if avg_cpu > self.cpu_warning_percent:
            base_workers = max(2, base_workers - 1)
        
        # Ensure reasonable bounds
        return min(8, max(2, base_workers))
    
    def _get_resource_warnings(self, memory_percent: float, cpu_percent: float) -> List[str]:
        """Get resource usage warnings"""
        warnings = []
        
        if memory_percent > 85:
            warnings.append("Memória muito alta (>85%)")
        elif memory_percent > 70:
            warnings.append("Uso de memória elevado (>70%)")
        
        if cpu_percent > 90:
            warnings.append("CPU sobrecarregada (>90%)")
        elif cpu_percent > 75:
            warnings.append("Uso de CPU alto (>75%)")
        
        return warnings