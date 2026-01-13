"""
Métricas de Performance para o Viral Bot
Mede tempo de execução de cada etapa
"""

import time
from functools import wraps
from typing import Dict, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
import json
import os


@dataclass
class Metric:
    """Uma métrica de performance."""
    name: str
    duration_ms: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    success: bool = True
    metadata: dict = field(default_factory=dict)


class PerformanceTracker:
    """Rastreador de métricas de performance."""
    
    def __init__(self, log_dir: str = None):
        self.metrics: List[Metric] = []
        self.log_dir = log_dir or os.path.join(os.path.dirname(__file__), "output", "logs")
        os.makedirs(self.log_dir, exist_ok=True)
    
    def track(self, name: str) -> 'TimerContext':
        """Context manager para medir tempo de uma operação."""
        return TimerContext(self, name)
    
    def add_metric(self, metric: Metric):
        """Adiciona uma métrica ao log."""
        self.metrics.append(metric)
    
    def get_summary(self) -> Dict:
        """Retorna resumo das métricas."""
        if not self.metrics:
            return {"total_operations": 0}
        
        durations = [m.duration_ms for m in self.metrics]
        successes = [m for m in self.metrics if m.success]
        
        return {
            "total_operations": len(self.metrics),
            "successful": len(successes),
            "failed": len(self.metrics) - len(successes),
            "total_time_ms": sum(durations),
            "avg_time_ms": sum(durations) / len(durations),
            "min_time_ms": min(durations),
            "max_time_ms": max(durations),
            "by_operation": self._group_by_name()
        }
    
    def _group_by_name(self) -> Dict:
        """Agrupa métricas por nome de operação."""
        groups = {}
        for m in self.metrics:
            if m.name not in groups:
                groups[m.name] = []
            groups[m.name].append(m.duration_ms)
        
        return {
            name: {
                "count": len(times),
                "avg_ms": sum(times) / len(times),
                "total_ms": sum(times)
            }
            for name, times in groups.items()
        }
    
    def save_report(self, filename: str = None):
        """Salva relatório em JSON."""
        if not filename:
            filename = f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = os.path.join(self.log_dir, filename)
        
        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "summary": self.get_summary(),
            "metrics": [
                {
                    "name": m.name,
                    "duration_ms": m.duration_ms,
                    "timestamp": m.timestamp,
                    "success": m.success,
                    "metadata": m.metadata
                }
                for m in self.metrics
            ]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return filepath


class TimerContext:
    """Context manager para medir tempo."""
    
    def __init__(self, tracker: PerformanceTracker, name: str):
        self.tracker = tracker
        self.name = name
        self.start_time = None
        self.metadata = {}
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (time.perf_counter() - self.start_time) * 1000
        
        metric = Metric(
            name=self.name,
            duration_ms=round(duration, 2),
            success=exc_type is None,
            metadata=self.metadata
        )
        
        self.tracker.add_metric(metric)
        return False


def measure(name: str = None):
    """Decorator para medir tempo de execução de funções."""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = name or func.__name__
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = (time.perf_counter() - start) * 1000
                print(f"⏱️ {func_name}: {duration:.2f}ms")
        return wrapper
    return decorator


# Tracker global
tracker = PerformanceTracker()


# Funções de conveniência
def track(name: str):
    return tracker.track(name)

def get_summary():
    return tracker.get_summary()

def save_report():
    return tracker.save_report()
