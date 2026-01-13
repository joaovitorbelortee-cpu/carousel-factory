"""
Test All - Testes unitários para todos os módulos (BMad-CORE: Refine)
"""

import unittest
import os
import sys
import asyncio

# Adicionar diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestUtils(unittest.TestCase):
    """Testes para utils.py"""
    
    def test_check_dependencies(self):
        from utils import check_dependencies
        deps = check_dependencies()
        self.assertIsInstance(deps, dict)
        self.assertIn("python", deps)
        self.assertTrue(deps["python"])
    
    def test_format_size(self):
        from utils import format_size
        self.assertEqual(format_size(1024), "1.0 KB")
        self.assertEqual(format_size(1048576), "1.0 MB")
    
    def test_format_duration(self):
        from utils import format_duration
        self.assertEqual(format_duration(30), "30.0s")
        self.assertEqual(format_duration(90), "1m 30s")
    
    def test_sanitize_filename(self):
        from utils import sanitize_filename
        self.assertEqual(sanitize_filename("file<>:name"), "file___name")


class TestConfig(unittest.TestCase):
    """Testes para config_manager.py"""
    
    def test_config_load(self):
        from config_manager import config_manager
        config = config_manager.config
        self.assertIsNotNone(config)
        self.assertEqual(config.video.width, 1080)
        self.assertEqual(config.video.height, 1920)
    
    def test_config_get(self):
        from config_manager import config_manager
        width = config_manager.get("video.width")
        self.assertEqual(width, 1080)
    
    def test_config_set(self):
        from config_manager import config_manager
        config_manager.set("content.num_videos", 10)
        self.assertEqual(config_manager.get("content.num_videos"), 10)
        # Restaurar
        config_manager.set("content.num_videos", 5)


class TestNiches(unittest.TestCase):
    """Testes para niches_database.py"""
    
    def test_get_niche(self):
        from niches_database import niche_manager
        niche = niche_manager.get_niche("ai_tools")
        self.assertEqual(niche.id, "ai_tools")
        self.assertIsNotNone(niche.name)
    
    def test_get_random_hook(self):
        from niches_database import niche_manager
        hook = niche_manager.get_random_hook()
        self.assertIsInstance(hook, str)
        self.assertGreater(len(hook), 10)
    
    def test_get_random_tools(self):
        from niches_database import niche_manager
        tools = niche_manager.get_random_tools(3)
        self.assertEqual(len(tools), 3)
        self.assertIn("name", tools[0])
    
    def test_rotate_niche(self):
        from niches_database import niche_manager
        initial = niche_manager.current_niche_id
        niche_manager.rotate_niche()
        # Deve ter mudado
        self.assertNotEqual(niche_manager.current_niche_id, initial)


class TestViralHooks(unittest.TestCase):
    """Testes para viral_hooks.py"""
    
    def test_get_random_hook(self):
        from viral_hooks import get_random_hook
        hook = get_random_hook()
        self.assertIsInstance(hook, str)
    
    def test_get_random_cta(self):
        from viral_hooks import get_random_cta
        cta = get_random_cta()
        self.assertIsInstance(cta, str)
    
    def test_get_hashtags(self):
        from viral_hooks import get_hashtags
        tags = get_hashtags("tiktok", 5)
        self.assertEqual(len(tags), 5)
        self.assertTrue(tags[0].startswith("#"))


class TestAnalytics(unittest.TestCase):
    """Testes para analytics.py"""
    
    def test_get_summary(self):
        from analytics import analytics
        summary = analytics.get_summary()
        self.assertIn("total_videos_generated", summary)
        self.assertIn("average_success_rate", summary)


class TestErrorHandler(unittest.TestCase):
    """Testes para error_handler.py"""
    
    def test_error_handler_decorator(self):
        from error_handler import error_handler
        
        @error_handler(context="test", default="fallback")
        def func_com_erro():
            raise ValueError("Erro de teste")
        
        result = func_com_erro()
        self.assertEqual(result, "fallback")


class TestThumbnail(unittest.TestCase):
    """Testes para thumbnail_generator.py"""
    
    def test_create_gradient(self):
        from thumbnail_generator import ThumbnailGenerator
        gen = ThumbnailGenerator()
        img = gen.create_gradient_background((100, 100))
        self.assertEqual(img.size, (100, 100))

    def test_image_generator_glassmorphism(self):
        """Testa se a geração de imagens com glassmorphism funciona."""
        output = os.path.join(self.test_dir, "test_glassmorphism.png")
        path = create_title_card("Teste Glassmorphism", output, context="tech")
        self.assertTrue(os.path.exists(path))
        self.assertTrue(os.path.getsize(path) > 0)


class TestIntegration(unittest.TestCase):
    """Testes de integração"""
    
    def test_full_import(self):
        """Testa se todos os módulos podem ser importados."""
        modules = [
            "utils",
            "config_manager",
            "error_handler",
            "analytics",
            "viral_hooks",
            "niches_database",
            "thumbnail_generator",
            "cli",
        ]
        
        for module in modules:
            try:
                __import__(module)
            except Exception as e:
                self.fail(f"Falha ao importar {module}: {e}")


def run_tests():
    """Executa todos os testes."""
    print("\n" + "="*60)
    print("🔬 EXECUTANDO TESTES UNITÁRIOS")
    print("="*60 + "\n")
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Adicionar todos os testes
    suite.addTests(loader.loadTestsFromTestCase(TestUtils))
    suite.addTests(loader.loadTestsFromTestCase(TestConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestNiches))
    suite.addTests(loader.loadTestsFromTestCase(TestViralHooks))
    suite.addTests(loader.loadTestsFromTestCase(TestAnalytics))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandler))
    suite.addTests(loader.loadTestsFromTestCase(TestThumbnail))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Executar
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    print(f"✅ Testes passados: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Falhas: {len(result.failures)}")
    print(f"💥 Erros: {len(result.errors)}")
    print("="*60 + "\n")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
