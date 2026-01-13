"""
Batch Generator - Geração em lote de vídeos (BMad-CORE: Automate + Optimize)
Permite gerar múltiplos vídeos de forma otimizada
"""

import asyncio
import os
from datetime import datetime
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
import time


class BatchGenerator:
    """
    Gerador em lote para criar múltiplos vídeos de forma otimizada.
    Usa paralelização onde possível.
    """
    
    def __init__(self, max_workers: int = 3):
        self.max_workers = max_workers
        self.results = []
        self.errors = []
        self.start_time = None
        self.end_time = None
    
    async def generate_batch(
        self,
        num_videos: int = 5,
        use_trends: bool = True,
        parallel_audio: bool = True
    ) -> List[str]:
        """
        Gera um lote de vídeos.
        
        Args:
            num_videos: Número de vídeos a gerar
            use_trends: Se deve usar trends do TikTok
            parallel_audio: Se deve gerar áudios em paralelo
        
        Returns:
            Lista de caminhos dos vídeos gerados
        """
        from main import run_full_pipeline
        
        self.start_time = datetime.now()
        print(f"\n🚀 Iniciando geração em lote de {num_videos} vídeos...")
        
        try:
            videos = await run_full_pipeline(num_videos, use_trends)
            self.results = videos
        except Exception as e:
            self.errors.append(str(e))
            print(f"❌ Erro na geração: {e}")
            videos = []
        
        self.end_time = datetime.now()
        self._print_summary()
        
        return videos
    
    def _print_summary(self):
        """Imprime resumo da geração."""
        duration = (self.end_time - self.start_time).total_seconds()
        
        print("\n" + "="*50)
        print("📊 RESUMO DA GERAÇÃO EM LOTE")
        print("="*50)
        print(f"✅ Vídeos gerados: {len(self.results)}")
        print(f"❌ Erros: {len(self.errors)}")
        print(f"⏱️ Tempo total: {duration:.1f} segundos")
        if self.results:
            print(f"⚡ Média por vídeo: {duration/len(self.results):.1f} segundos")
        print("="*50 + "\n")
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas da geração."""
        duration = 0
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
        
        return {
            "videos_generated": len(self.results),
            "errors": len(self.errors),
            "total_time_seconds": duration,
            "avg_time_per_video": duration / max(len(self.results), 1),
            "success_rate": len(self.results) / max(len(self.results) + len(self.errors), 1),
        }


class BatchScheduler:
    """
    Agendador de lotes de vídeos.
    Permite agendar múltiplas gerações ao longo do dia.
    """
    
    def __init__(self):
        self.jobs = []
        self.completed_jobs = []
    
    def schedule_batch(
        self,
        time_str: str,
        num_videos: int = 5,
        use_trends: bool = True
    ):
        """
        Agenda uma geração de lote.
        
        Args:
            time_str: Horário no formato "HH:MM"
            num_videos: Número de vídeos
            use_trends: Se deve usar trends
        """
        self.jobs.append({
            "time": time_str,
            "num_videos": num_videos,
            "use_trends": use_trends,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
        })
        
        print(f"📅 Agendado: {num_videos} vídeos às {time_str}")
    
    def list_jobs(self):
        """Lista todos os jobs agendados."""
        print("\n📋 JOBS AGENDADOS:")
        print("-"*40)
        for i, job in enumerate(self.jobs, 1):
            status = "✅" if job["status"] == "completed" else "⏳"
            print(f"{i}. {status} {job['time']} - {job['num_videos']} vídeos")
    
    async def run_pending(self):
        """Executa jobs pendentes cujo horário já passou."""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        for job in self.jobs:
            if job["status"] == "pending" and job["time"] <= current_time:
                print(f"\n⏰ Executando job agendado para {job['time']}...")
                
                generator = BatchGenerator()
                await generator.generate_batch(
                    num_videos=job["num_videos"],
                    use_trends=job["use_trends"]
                )
                
                job["status"] = "completed"
                job["completed_at"] = datetime.now().isoformat()
                self.completed_jobs.append(job)


async def quick_batch(num_videos: int = 5) -> List[str]:
    """
    Função rápida para gerar um lote de vídeos.
    
    Args:
        num_videos: Número de vídeos a gerar
    
    Returns:
        Lista de caminhos dos vídeos
    """
    generator = BatchGenerator()
    return await generator.generate_batch(num_videos)


# CLI
if __name__ == "__main__":
    import sys
    
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    if not args or args[0] == "help":
        print("""
🚀 BATCH GENERATOR - Geração em Lote

Uso: python batch_generator.py <comando> [opções]

Comandos:
    generate <num>    Gera <num> vídeos (padrão: 5)
    schedule          Mostra jobs agendados
    help              Mostra esta ajuda

Exemplos:
    python batch_generator.py generate 10
    python batch_generator.py generate 3
        """)
    
    elif args[0] == "generate":
        num = int(args[1]) if len(args) > 1 else 5
        asyncio.run(quick_batch(num))
    
    elif args[0] == "schedule":
        scheduler = BatchScheduler()
        scheduler.schedule_batch("12:00", 5)
        scheduler.schedule_batch("18:00", 5)
        scheduler.list_jobs()
