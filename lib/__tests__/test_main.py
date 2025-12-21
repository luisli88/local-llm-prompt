"""
Pruebas unitarias para main.py
Tests para la interfaz de usuario y lógica principal de la aplicación
"""

import pytest
from unittest.mock import patch, MagicMock, call
from io import StringIO
import sys

from main import LLMStackApp


class TestLLMStackApp:
    """Suite de pruebas para LLMStackApp"""

    @pytest.fixture
    def app(self):
        """Fixture que crea una instancia de LLMStackApp"""
        return LLMStackApp()

    def test_app_init(self, app):
        """Test inicialización de la aplicación"""
        assert app.config is not None
        assert hasattr(app, 'console')

    @patch('main.ollama_manager')
    def test_validate_installation_success(self, mock_ollama, app):
        """Test validación exitosa de instalación"""
        # Configurar mocks
        mock_ollama.check_ollama_installed.return_value = True
        mock_ollama.check_ollama_running.return_value = True

        with patch.object(app, '_print_success') as mock_print:
            app._validate_installation()

            # Verificar que se llamaron las funciones de validación
            mock_ollama.check_ollama_installed.assert_called_once()
            mock_ollama.check_ollama_running.assert_called_once()

            # Verificar mensajes de éxito
            assert mock_print.call_count >= 3  # Python, dependencias, Ollama

    @patch('main.ollama_manager')
    def test_validate_installation_ollama_missing(self, mock_ollama, app):
        """Test validación cuando Ollama no está instalado"""
        mock_ollama.check_ollama_installed.return_value = False

        with patch.object(app, '_print_error') as mock_print:
            app._validate_installation()

            mock_print.assert_called_once_with("❌ Ollama no está instalado")

    @patch('main.ollama_manager')
    def test_show_status(self, mock_ollama, app):
        """Test muestra de estado del sistema"""
        # Mock del estado del sistema
        mock_status = {
            "ollama_running": True,
            "models_installed": 2,
            "models_running": 1,
            "models_with_updates": 1,
            "vram_total": "8GB",
            "vram_used": "4GB",
            "running_models": ["qwen:latest"],
            "available_updates": {
                "mistral:latest": {
                    "current": "mistral:latest",
                    "latest": "mistral:7b",
                    "base_name": "mistral"
                }
            }
        }

        mock_ollama.get_status_summary.return_value = mock_status
        mock_ollama.get_vram_usage.return_value = MagicMock(
            total_vram="8GB",
            used_vram="4GB",
            models_loaded=["qwen:latest"]
        )

        with patch.object(app.console, 'print') as mock_console_print:
            app._show_status()

            # Verificar que se imprimió información del estado
            calls = mock_console_print.call_args_list
            assert len(calls) > 0

            # Verificar que se mostró información de actualizaciones
            status_text = str(calls)
            assert "1 actualización" in status_text or "1 actualizaciones" in status_text

    @patch('main.ollama_manager')
    @patch('main.Prompt')
    def test_activate_model_success(self, mock_prompt, mock_ollama, app):
        """Test activación exitosa de modelo"""
        # Mock selección de modelo
        mock_prompt.ask.return_value = "qwen"

        # Mock activación exitosa
        mock_ollama.smart_activate_model.return_value = True

        with patch.object(app, '_print_success') as mock_print, \
             patch('main.Confirm', return_value=MagicMock(ask=MagicMock(return_value=True))):
            app._activate_model()

            mock_ollama.smart_activate_model.assert_called_once_with("qwen")
            mock_print.assert_called_with("✅ Modelo activado exitosamente")

    @patch('main.ollama_manager')
    @patch('main.Prompt')
    def test_deactivate_model_success(self, mock_prompt, mock_ollama, app):
        """Test desactivación exitosa de modelo"""
        # Mock modelos corriendo
        mock_ollama.get_running_models.return_value = ["qwen:latest", "deepseek:latest"]

        # Mock selección
        mock_prompt.ask.return_value = "1"

        # Mock confirmación
        with patch('main.Confirm', return_value=MagicMock(ask=MagicMock(return_value=True))), \
             patch.object(app, '_print_success') as mock_print:
            app._deactivate_model()

            mock_ollama.stop_model.assert_called_once_with("qwen:latest")
            mock_print.assert_called_with("✅ Modelo detenido exitosamente")

    @patch('main.ollama_manager')
    @patch('main.Prompt')
    def test_update_models_success(self, mock_prompt, mock_ollama, app):
        """Test actualización exitosa de modelos"""
        # Mock confirmación
        with patch('main.Confirm', return_value=MagicMock(ask=MagicMock(return_value=True))), \
             patch.object(app, '_print_success') as mock_print:
            app._update_models()

            # Verificar que se intentó actualizar modelos
            assert mock_ollama.pull_model.called

    @patch('main.ollama_manager')
    def test_check_updates_with_available_updates(self, mock_ollama, app):
        """Test verificación de actualizaciones cuando hay disponibles"""
        # Mock actualizaciones disponibles
        mock_ollama.check_model_updates.return_value = {
            "qwen:latest": {
                "current": "qwen:latest",
                "latest": "qwen:7b",
                "base_name": "qwen"
            }
        }

        with patch('main.Prompt') as mock_prompt, \
             patch('main.Confirm', return_value=MagicMock(ask=MagicMock(return_value=False))), \
             patch.object(app, '_print_info') as mock_print:
            # Simular selección de "0. Cancelar"
            mock_prompt.ask.return_value = "0"

            app._check_updates()

            # Verificar que se mostró información de actualizaciones
            mock_ollama.check_model_updates.assert_called_once()

    @patch('main.ollama_manager')
    def test_check_updates_no_updates(self, mock_ollama, app):
        """Test verificación de actualizaciones cuando no hay disponibles"""
        # Mock sin actualizaciones
        mock_ollama.check_model_updates.return_value = {}

        with patch.object(app, '_print_success') as mock_print:
            app._check_updates()

            mock_print.assert_called_once_with("✅ Todos los modelos están actualizados")

    @patch('main.ollama_manager')
    @patch('main.Prompt')
    def test_check_updates_update_all(self, mock_prompt, mock_ollama, app):
        """Test actualización de todos los modelos disponibles"""
        # Mock actualizaciones disponibles
        updates = {
            "qwen:latest": {
                "current": "qwen:latest",
                "latest": "qwen:7b",
                "base_name": "qwen"
            }
        }
        mock_ollama.check_model_updates.return_value = updates
        mock_ollama.update_model_if_available.return_value = True

        # Simular selección de "1. Actualizar todos"
        mock_prompt.ask.side_effect = ["1"]  # Opción de menú

        with patch('main.Confirm', return_value=MagicMock(ask=MagicMock(return_value=True))), \
             patch.object(app, '_print_success') as mock_print:
            app._check_updates()

            # Verificar que se intentó actualizar
            mock_ollama.update_model_if_available.assert_called_once_with("qwen:latest")
            mock_print.assert_called_with("✅ 1/1 modelos actualizados")

    @patch('main.ollama_manager')
    @patch('main.Prompt')
    def test_check_updates_select_specific(self, mock_prompt, mock_ollama, app):
        """Test selección y actualización de modelo específico"""
        # Mock actualizaciones disponibles
        updates = {
            "qwen:latest": {
                "current": "qwen:latest",
                "latest": "qwen:7b",
                "base_name": "qwen"
            },
            "deepseek:latest": {
                "current": "deepseek:latest",
                "latest": "deepseek:v2",
                "base_name": "deepseek"
            }
        }
        mock_ollama.check_model_updates.return_value = updates
        mock_ollama.update_model_if_available.return_value = True

        # Simular selección de "2. Seleccionar modelos específicos" -> "1" (primer modelo)
        mock_prompt.ask.side_effect = ["2", "1"]

        with patch('main.Confirm', return_value=MagicMock(ask=MagicMock(return_value=True))), \
             patch.object(app, '_print_success') as mock_print:
            app._check_updates()

            # Verificar que se actualizó solo el modelo seleccionado
            mock_ollama.update_model_if_available.assert_called_once_with("qwen:latest")

    def test_print_success(self, app):
        """Test método de impresión de éxito"""
        with patch.object(app.console, 'print') as mock_print:
            app._print_success("Test message")

            mock_print.assert_called_once()
            call_args = mock_print.call_args[0][0]
            assert "✅" in str(call_args)
            assert "Test message" in str(call_args)

    def test_print_error(self, app):
        """Test método de impresión de error"""
        with patch.object(app.console, 'print') as mock_print:
            app._print_error("Test error")

            mock_print.assert_called_once()
            call_args = mock_print.call_args[0][0]
            assert "❌" in str(call_args)
            assert "Test error" in str(call_args)

    def test_print_info(self, app):
        """Test método de impresión de información"""
        with patch.object(app.console, 'print') as mock_print:
            app._print_info("Test info")

            mock_print.assert_called_once()
            call_args = mock_print.call_args[0][0]
            assert "ℹ️" in str(call_args)
            assert "Test info" in str(call_args)

    @patch('main.ollama_manager')
    def test_show_menu(self, mock_ollama, app):
        """Test muestra del menú principal"""
        with patch.object(app.console, 'print') as mock_print:
            app._show_menu()

            # Verificar que se imprimieron las opciones del menú
            calls = mock_print.call_args_list
            assert len(calls) >= 8  # 8 opciones de menú

            # Verificar que incluye la nueva opción de actualizaciones
            menu_text = str(calls)
            assert "Verificar Actualizaciones" in menu_text

    @patch('main.ollama_manager')
    @patch('main.Prompt')
    def test_run_exit_immediately(self, mock_prompt, mock_ollama, app):
        """Test ejecución que sale inmediatamente"""
        # Mock validaciones exitosas
        mock_ollama.check_ollama_installed.return_value = True
        mock_ollama.check_ollama_running.return_value = True

        # Mock selección de salir
        mock_prompt.ask.return_value = "0"

        with patch.object(app, '_print_success') as mock_print:
            app.run()

            mock_print.assert_called_with("¡Hasta luego!")

    @patch('main.ollama_manager')
    def test_run_ollama_not_installed(self, mock_ollama, app):
        """Test ejecución cuando Ollama no está instalado"""
        mock_ollama.check_ollama_installed.return_value = False

        with patch.object(app, '_print_error') as mock_print:
            app.run()

            mock_print.assert_called_with("❌ Ollama no está instalado")

    @patch('main.ollama_manager')
    def test_run_ollama_not_running(self, mock_ollama, app):
        """Test ejecución cuando Ollama no está corriendo"""
        mock_ollama.check_ollama_installed.return_value = True
        mock_ollama.check_ollama_running.return_value = False
        mock_ollama.start_ollama_service.return_value = False

        with patch.object(app, '_print_error') as mock_print:
            app.run()

            mock_print.assert_called_with("❌ Error iniciando servicio")


class TestIntegration:
    """Pruebas de integración"""

    @patch('main.ollama_manager')
    @patch('main.config_manager')
    def test_full_workflow_simulation(self, mock_config, mock_ollama):
        """Test simulación de workflow completo"""
        # Configurar mocks para un workflow exitoso
        mock_config.get_config.return_value = MagicMock(max_loaded_models=2)
        mock_config.get_models.return_value = {
            'qwen': MagicMock(name='qwen:latest', description='Code completion')
        }

        mock_ollama.check_ollama_installed.return_value = True
        mock_ollama.check_ollama_running.return_value = True
        mock_ollama.get_status_summary.return_value = {
            "ollama_running": True,
            "models_installed": 1,
            "models_running": 0,
            "models_with_updates": 0,
            "available_updates": {}
        }
        mock_ollama.get_vram_usage.return_value = MagicMock(
            total_vram="8GB", used_vram="0GB", models_loaded=[]
        )

        app = LLMStackApp()

        # Simular workflow: mostrar estado -> salir
        with patch('main.Prompt') as mock_prompt, \
             patch.object(app, '_print_success') as mock_print:
            mock_prompt.ask.return_value = "0"

            app.run()

            # Verificar que se ejecutó correctamente
            mock_print.assert_called_with("¡Hasta luego!")


if __name__ == "__main__":
    pytest.main([__file__])