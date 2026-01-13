"""
Validation - Validação de integridade do sistema (BMad-CORE: Refine)
Verifica se todos os componentes estão funcionando corretamente
"""

import os
import sys
import importlib
from typing import List, Dict, Tuple
from datetime import datetime


class SystemValidator:
    """Valida todos os componentes do Viral Bot."""
    
    # Módulos obrigatórios
    REQUIRED_MODULES = [
        "main",
        "content",
        "content_modeler",
        "tts_engine",
        "image_generator",
        "video_engine",
        "scheduler",
        "auto_poster",
        "cli",
    ]
    
    # Módulos auxiliares
    AUXILIARY_MODULES = [
        "utils",
        "error_handler",
        "analytics",
        "config_manager",
        "viral_hooks",
        "niches_database",
        "thumbnail_generator",
        "batch_generator",
        "logger",
    ]
    
    # Dependências externas
    EXTERNAL_DEPS = [
        "moviepy",
        "edge_tts",
        "PIL",  # Pillow
        "tqdm",
    ]
    
    def __init__(self):
        self.results = []
        self.errors = []
        self.warnings = []
    
    def _log(self, status: str, message: str):
        """Registra resultado de validação."""
        if status == "ok":
            icon = "✅"
        elif status == "warn":
            icon = "⚠️"
            self.warnings.append(message)
        else:
            icon = "❌"
            self.errors.append(message)
        
        self.results.append(f"{icon} {message}")
        print(f"{icon} {message}")
    
    def validate_modules(self) -> bool:
        """Valida se todos os módulos podem ser importados."""
        print("\n📦 Validando módulos...")
        all_ok = True
        
        for module in self.REQUIRED_MODULES:
            try:
                importlib.import_module(module)
                self._log("ok", f"Módulo {module}")
            except Exception as e:
                self._log("error", f"Módulo {module}: {e}")
                all_ok = False
        
        for module in self.AUXILIARY_MODULES:
            try:
                importlib.import_module(module)
                self._log("ok", f"Módulo auxiliar {module}")
            except Exception as e:
                self._log("warn", f"Módulo auxiliar {module}: {e}")
        
        return all_ok
    
    def validate_dependencies(self) -> bool:
        """Valida dependências externas."""
        print("\n🔗 Validando dependências...")
        all_ok = True
        
        for dep in self.EXTERNAL_DEPS:
            try:
                importlib.import_module(dep)
                self._log("ok", f"Dependência {dep}")
            except ImportError:
                self._log("error", f"Dependência {dep} não instalada")
                all_ok = False
        
        # FFmpeg (opcional)
        import shutil
        if shutil.which("ffmpeg"):
            self._log("ok", "FFmpeg encontrado")
        else:
            self._log("warn", "FFmpeg não encontrado (alguns recursos podem falhar)")
        
        return all_ok
    
    def validate_directories(self) -> bool:
        """Valida estrutura de diretórios."""
        print("\n📁 Validando diretórios...")
        
        required_dirs = ["output", "cache"]
        optional_dirs = ["output/assets", "output/logs", "output/thumbnails"]
        
        for dir_name in required_dirs:
            if os.path.exists(dir_name):
                self._log("ok", f"Diretório {dir_name}")
            else:
                os.makedirs(dir_name, exist_ok=True)
                self._log("ok", f"Diretório {dir_name} (criado)")
        
        for dir_name in optional_dirs:
            if os.path.exists(dir_name):
                self._log("ok", f"Diretório {dir_name}")
            else:
                os.makedirs(dir_name, exist_ok=True)
                self._log("ok", f"Diretório {dir_name} (criado)")
        
        return True
    
    def validate_config(self) -> bool:
        """Valida configurações."""
        print("\n⚙️ Validando configurações...")
        
        try:
            from config_manager import config_manager
            config = config_manager.config
            
            if config.video.width > 0 and config.video.height > 0:
                self._log("ok", f"Config vídeo: {config.video.width}x{config.video.height}")
            else:
                self._log("error", "Config vídeo inválida")
                return False
            
            self._log("ok", f"Config TTS: {config.tts.default_voice}")
            self._log("ok", f"Config nicho: {config.content.nicho}")
            
            return True
            
        except Exception as e:
            self._log("error", f"Erro nas configurações: {e}")
            return False
    
    def validate_output(self) -> bool:
        """Valida arquivos de output existentes."""
        print("\n🎬 Validando outputs...")
        
        output_dir = "output"
        if not os.path.exists(output_dir):
            self._log("warn", "Nenhum output encontrado")
            return True
        
        videos = [f for f in os.listdir(output_dir) if f.endswith(".mp4")]
        audios = [f for f in os.listdir(output_dir) if f.endswith(".mp3")]
        
        self._log("ok", f"Vídeos gerados: {len(videos)}")
        self._log("ok", f"Áudios gerados: {len(audios)}")
        
        # Verificar integridade dos vídeos
        for video in videos:
            filepath = os.path.join(output_dir, video)
            size = os.path.getsize(filepath)
            if size > 10000:  # > 10KB
                self._log("ok", f"Vídeo {video}: {size/1024:.1f}KB")
            else:
                self._log("warn", f"Vídeo {video} muito pequeno: {size}B")
        
        return True
    
    def run_full_validation(self) -> Dict:
        """Executa validação completa do sistema."""
        print("\n" + "="*60)
        print("🔍 VALIDAÇÃO DO SISTEMA VIRAL BOT")
        print("="*60)
        
        start = datetime.now()
        
        results = {
            "modules": self.validate_modules(),
            "dependencies": self.validate_dependencies(),
            "directories": self.validate_directories(),
            "config": self.validate_config(),
            "output": self.validate_output(),
        }
        
        duration = (datetime.now() - start).total_seconds()
        
        # Resumo
        print("\n" + "="*60)
        print("📊 RESUMO DA VALIDAÇÃO")
        print("="*60)
        print(f"⏱️ Tempo: {duration:.2f}s")
        print(f"✅ Sucesso: {sum(results.values())}/{len(results)}")
        print(f"⚠️ Avisos: {len(self.warnings)}")
        print(f"❌ Erros: {len(self.errors)}")
        
        all_ok = all(results.values()) and len(self.errors) == 0
        
        if all_ok:
            print("\n🎉 SISTEMA VALIDADO COM SUCESSO!")
        else:
            print("\n⚠️ SISTEMA COM PROBLEMAS. Corrija os erros acima.")
        
        print("="*60 + "\n")
        
        return {
            "success": all_ok,
            "results": results,
            "errors": self.errors,
            "warnings": self.warnings,
            "duration": duration,
        }


def quick_validate() -> bool:
    """Validação rápida do sistema."""
    validator = SystemValidator()
    result = validator.run_full_validation()
    return result["success"]


# CLI
if __name__ == "__main__":
    success = quick_validate()
    sys.exit(0 if success else 1)
