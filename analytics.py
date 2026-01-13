"""
Analytics - Rastreamento de métricas e desempenho (BMad-CORE: Evolve)
Coleta dados para otimização contínua do sistema
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class VideoMetrics:
    """Métricas de um vídeo gerado."""
    video_id: int
    title: str
    generated_at: str
    generation_time_seconds: float
    file_size_bytes: int
    audio_size_bytes: int
    num_images: int
    format_type: str
    posted: bool = False
    posted_at: Optional[str] = None
    platform: Optional[str] = None
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0


@dataclass
class SessionMetrics:
    """Métricas de uma sessão de geração."""
    session_id: str
    started_at: str
    ended_at: Optional[str]
    videos_requested: int
    videos_generated: int
    total_time_seconds: float
    errors: List[str]
    success_rate: float


class Analytics:
    """Sistema de analytics para rastrear métricas e desempenho."""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.join(
            os.path.dirname(__file__), "output", "analytics"
        )
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.metrics_file = os.path.join(self.data_dir, "video_metrics.json")
        self.sessions_file = os.path.join(self.data_dir, "sessions.json")
        self.daily_file = os.path.join(self.data_dir, "daily_stats.json")
    
    def _load_json(self, filepath: str) -> list:
        """Carrega dados de arquivo JSON."""
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def _save_json(self, filepath: str, data: list):
        """Salva dados em arquivo JSON."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def log_video(self, metrics: VideoMetrics):
        """Registra métricas de um vídeo."""
        data = self._load_json(self.metrics_file)
        data.append(asdict(metrics))
        self._save_json(self.metrics_file, data)
    
    def log_session(self, metrics: SessionMetrics):
        """Registra métricas de uma sessão."""
        data = self._load_json(self.sessions_file)
        data.append(asdict(metrics))
        self._save_json(self.sessions_file, data)
    
    def get_video_metrics(self, video_id: int = None) -> List[Dict]:
        """Retorna métricas de vídeos."""
        data = self._load_json(self.metrics_file)
        if video_id:
            return [v for v in data if v.get("video_id") == video_id]
        return data
    
    def get_session_metrics(self, limit: int = 10) -> List[Dict]:
        """Retorna últimas sessões."""
        data = self._load_json(self.sessions_file)
        return data[-limit:]
    
    def get_daily_stats(self, date: str = None) -> Dict:
        """Retorna estatísticas diárias."""
        date = date or datetime.now().strftime("%Y-%m-%d")
        daily = self._load_json(self.daily_file)
        
        for day in daily:
            if day.get("date") == date:
                return day
        
        return {
            "date": date,
            "videos_generated": 0,
            "total_views": 0,
            "total_likes": 0,
            "total_errors": 0,
        }
    
    def update_daily_stats(self, videos: int = 0, views: int = 0, 
                          likes: int = 0, errors: int = 0):
        """Atualiza estatísticas diárias."""
        date = datetime.now().strftime("%Y-%m-%d")
        daily = self._load_json(self.daily_file)
        
        # Encontrar ou criar entrada para hoje
        today_stats = None
        for day in daily:
            if day.get("date") == date:
                today_stats = day
                break
        
        if not today_stats:
            today_stats = {
                "date": date,
                "videos_generated": 0,
                "total_views": 0,
                "total_likes": 0,
                "total_errors": 0,
            }
            daily.append(today_stats)
        
        # Atualizar
        today_stats["videos_generated"] += videos
        today_stats["total_views"] += views
        today_stats["total_likes"] += likes
        today_stats["total_errors"] += errors
        
        self._save_json(self.daily_file, daily)
    
    def get_summary(self) -> Dict:
        """Retorna resumo geral das métricas."""
        videos = self._load_json(self.metrics_file)
        sessions = self._load_json(self.sessions_file)
        
        total_videos = len(videos)
        total_sessions = len(sessions)
        
        # Calcular médias
        if sessions:
            avg_success = sum(s.get("success_rate", 0) for s in sessions) / len(sessions)
            avg_time = sum(s.get("total_time_seconds", 0) for s in sessions) / len(sessions)
        else:
            avg_success = 0
            avg_time = 0
        
        # Calcular engajamento total
        total_views = sum(v.get("views", 0) for v in videos)
        total_likes = sum(v.get("likes", 0) for v in videos)
        total_comments = sum(v.get("comments", 0) for v in videos)
        
        return {
            "total_videos_generated": total_videos,
            "total_sessions": total_sessions,
            "average_success_rate": round(avg_success * 100, 1),
            "average_generation_time": round(avg_time, 1),
            "total_views": total_views,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "engagement_rate": round((total_likes + total_comments) / max(total_views, 1) * 100, 2),
        }
    
    def print_dashboard(self):
        """Imprime dashboard de métricas."""
        summary = self.get_summary()
        
        print("\n" + "="*50)
        print("📊 ANALYTICS DASHBOARD")
        print("="*50)
        print(f"🎬 Vídeos gerados: {summary['total_videos_generated']}")
        print(f"📈 Taxa de sucesso: {summary['average_success_rate']}%")
        print(f"⏱️ Tempo médio: {summary['average_generation_time']}s")
        print("-"*50)
        print(f"👁️ Total de views: {summary['total_views']:,}")
        print(f"❤️ Total de likes: {summary['total_likes']:,}")
        print(f"💬 Total de comments: {summary['total_comments']:,}")
        print(f"📈 Taxa de engajamento: {summary['engagement_rate']}%")
        print("="*50 + "\n")


# Instância global
analytics = Analytics()


def track_video_generation(video_id: int, title: str, generation_time: float,
                          file_path: str, audio_path: str, num_images: int,
                          format_type: str = "listicle"):
    """Função helper para rastrear geração de vídeo."""
    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
    audio_size = os.path.getsize(audio_path) if os.path.exists(audio_path) else 0
    
    metrics = VideoMetrics(
        video_id=video_id,
        title=title,
        generated_at=datetime.now().isoformat(),
        generation_time_seconds=generation_time,
        file_size_bytes=file_size,
        audio_size_bytes=audio_size,
        num_images=num_images,
        format_type=format_type,
    )
    
    analytics.log_video(metrics)
    analytics.update_daily_stats(videos=1)


# Teste
if __name__ == "__main__":
    print("📊 Testando analytics.py...")
    
    # Testar registro de vídeo
    track_video_generation(
        video_id=1,
        title="Teste de Analytics",
        generation_time=45.5,
        file_path="output/video_1_final.mp4",
        audio_path="output/audio_video_1.mp3",
        num_images=7,
    )
    
    # Mostrar dashboard
    analytics.print_dashboard()
