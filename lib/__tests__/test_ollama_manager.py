"""
Pruebas unitarias para OllamaManager
Tests para gestión de modelos Ollama, VRAM y actualizaciones
"""

import pytest
from unittest.mock import patch, MagicMock, call
import subprocess
import requests
from pathlib import Path

from ollama_manager import OllamaManager, ModelStatus, VRAMUsage


class TestOllamaManager:
    """Suite de pruebas para OllamaManager"""

    @pytest.fixture
    def ollama_manager(self):
        """Fixture que crea una instancia de OllamaManager"""
        return OllamaManager()

    def test_init(self, ollama_manager):
        """Test inicialización del OllamaManager"""
        assert ollama_manager.ollama_host == "http://localhost:11434"
        assert ollama_manager.max_loaded == 2

    @patch('ollama_manager.subprocess.run')
    def test_check_ollama_installed_success(self, mock_run, ollama_manager):
        """Test verificación exitosa de instalación de Ollama"""
        mock_run.return_value = MagicMock(returncode=0, stdout="ollama version 0.1.0")

        result = ollama_manager.check_ollama_installed()
        assert result == True
        mock_run.assert_called_once_with(["ollama", "--version"], capture_output=True, text=True, timeout=30)

    @patch('ollama_manager.subprocess.run')
    def test_check_ollama_installed_failure(self, mock_run, ollama_manager):
        """Test verificación fallida de instalación de Ollama"""
        mock_run.return_value = MagicMock(returncode=1, stdout="")

        result = ollama_manager.check_ollama_installed()
        assert result == False

    @patch('ollama_manager.requests.get')
    def test_check_ollama_running_success(self, mock_get, ollama_manager):
        """Test verificación exitosa de servicio Ollama corriendo"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = ollama_manager.check_ollama_running()
        assert result == True
        mock_get.assert_called_once_with("http://localhost:11434/api/tags", timeout=5)

    @patch('ollama_manager.requests.get')
    def test_check_ollama_running_failure(self, mock_get, ollama_manager):
        """Test verificación fallida de servicio Ollama corriendo"""
        mock_get.side_effect = requests.exceptions.RequestException()

        result = ollama_manager.check_ollama_running()
        assert result == False

    @patch('ollama_manager.subprocess.run')
    def test_start_ollama_service_already_running(self, mock_run, ollama_manager):
        """Test inicio de servicio cuando ya está corriendo"""
        with patch.object(ollama_manager, 'check_ollama_running', return_value=True):
            result = ollama_manager.start_ollama_service()
            assert result == True
            mock_run.assert_not_called()

    @patch('ollama_manager.subprocess.run')
    @patch.object(OllamaManager, 'check_ollama_running')
    def test_start_ollama_service_success(self, mock_check_running, mock_run, ollama_manager):
        """Test inicio exitoso de servicio Ollama"""
        # Primero retorna False (no corriendo), luego True (ya corriendo)
        mock_check_running.side_effect = [False, True, True]
        mock_run.return_value = MagicMock(returncode=0)

        result = ollama_manager.start_ollama_service()
        assert result == True

    @patch('ollama_manager.subprocess.run')
    def test_list_installed_models_success(self, mock_run, ollama_manager):
        """Test listado exitoso de modelos instalados"""
        mock_output = """NAME                    ID              SIZE    MODIFIED
qwen2.5-coder:latest    abc123          4.7 GB  2 hours ago
deepseek-coder:latest   def456          6.0 GB  1 hour ago"""

        mock_run.return_value = MagicMock(returncode=0, stdout=mock_output)

        models = ollama_manager.list_installed_models()

        assert len(models) == 2
        assert models[0].name == "qwen2.5-coder:latest"
        assert models[0].size == "4.7 GB"
        assert models[1].name == "deepseek-coder:latest"
        assert models[1].size == "6.0 GB"

    @patch('ollama_manager.subprocess.run')
    def test_list_installed_models_failure(self, mock_run, ollama_manager):
        """Test listado fallido de modelos instalados"""
        mock_run.return_value = MagicMock(returncode=1, stdout="")

        models = ollama_manager.list_installed_models()
        assert models == []

    @patch('ollama_manager.requests.get')
    def test_get_running_models_success(self, mock_get, ollama_manager):
        """Test obtención exitosa de modelos corriendo"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "qwen2.5-coder:latest"},
                {"name": "deepseek-coder:latest"}
            ]
        }
        mock_get.return_value = mock_response

        running = ollama_manager.get_running_models()
        assert running == ["qwen2.5-coder:latest", "deepseek-coder:latest"]

    @patch('ollama_manager.requests.get')
    def test_get_running_models_failure(self, mock_get, ollama_manager):
        """Test obtención fallida de modelos corriendo"""
        mock_get.side_effect = requests.exceptions.RequestException()

        running = ollama_manager.get_running_models()
        assert running == []

    def test_get_vram_usage(self, ollama_manager):
        """Test obtención de uso de VRAM"""
        with patch.object(ollama_manager, 'get_running_models', return_value=["qwen:latest", "deepseek:latest"]):
            vram = ollama_manager.get_vram_usage()

            assert isinstance(vram, VRAMUsage)
            assert vram.total_vram == "8GB"
            assert "4" in vram.used_vram  # Estimación aproximada
            assert vram.models_loaded == ["qwen:latest", "deepseek:latest"]

    @patch('ollama_manager.subprocess.run')
    def test_pull_model_success(self, mock_run, ollama_manager):
        """Test descarga exitosa de modelo"""
        mock_run.return_value = MagicMock(returncode=0)

        result = ollama_manager.pull_model("test-model:latest", show_progress=False)
        assert result == True
        mock_run.assert_called_once_with(["ollama", "pull", "test-model:latest"], capture_output=True, text=True, timeout=300)

    @patch('ollama_manager.subprocess.run')
    def test_pull_model_failure(self, mock_run, ollama_manager):
        """Test descarga fallida de modelo"""
        mock_run.return_value = MagicMock(returncode=1, stderr="Error downloading model")

        result = ollama_manager.pull_model("test-model:latest", show_progress=False)
        assert result == False

    @patch('ollama_manager.subprocess.run')
    def test_remove_model_success(self, mock_run, ollama_manager):
        """Test eliminación exitosa de modelo"""
        mock_run.return_value = MagicMock(returncode=0)

        result = ollama_manager.remove_model("test-model:latest")
        assert result == True
        mock_run.assert_called_once_with(["ollama", "rm", "test-model:latest"], capture_output=True, text=True, timeout=30)

    @patch('ollama_manager.subprocess.run')
    def test_stop_model_success(self, mock_run, ollama_manager):
        """Test detención exitosa de modelo"""
        mock_run.return_value = MagicMock(returncode=0)

        result = ollama_manager.stop_model("test-model:latest")
        assert result == True
        mock_run.assert_called_once_with(["ollama", "stop", "test-model:latest"], capture_output=True, text=True, timeout=30)

    @patch('ollama_manager.requests.post')
    @patch.object(OllamaManager, 'get_running_models', return_value=[])
    def test_test_model_success(self, mock_get_running, mock_post, ollama_manager):
        """Test validación exitosa de modelo"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Hello, this is a test response"}
        mock_post.return_value = mock_response

        result = ollama_manager.test_model("test-model:latest")
        assert result == True

    @patch('ollama_manager.requests.post')
    def test_test_model_failure(self, mock_post, ollama_manager):
        """Test validación fallida de modelo"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": ""}
        mock_post.return_value = mock_response

        result = ollama_manager.test_model("test-model:latest")
        assert result == False

    @patch('ollama_manager.requests.get')
    def test_check_model_updates_success(self, mock_get, ollama_manager):
        """Test verificación exitosa de actualizaciones"""
        # Mock respuesta del registry
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"name": "qwen2.5-coder:7b"},  # Versión más reciente
            {"name": "deepseek-coder:v2-lite"}  # Versión más reciente
        ]
        mock_get.return_value = mock_response

        # Mock modelos instalados
        with patch.object(ollama_manager, 'list_installed_models') as mock_list:
            mock_list.return_value = [
                ModelStatus(name="qwen2.5-coder:latest", size="4.7 GB", size_vram="5.0 GB", digest="old"),
                ModelStatus(name="deepseek-coder:latest", size="6.0 GB", size_vram="6.5 GB", digest="old")
            ]

            updates = ollama_manager.check_model_updates()

            assert len(updates) == 2
            assert "qwen2.5-coder:latest" in updates
            assert "deepseek-coder:latest" in updates

    @patch('ollama_manager.requests.get')
    def test_check_model_updates_no_updates(self, mock_get, ollama_manager):
        """Test verificación cuando no hay actualizaciones"""
        # Mock respuesta del registry
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"name": "qwen2.5-coder:latest"},  # Misma versión
            {"name": "deepseek-coder:latest"}  # Misma versión
        ]
        mock_get.return_value = mock_response

        # Mock modelos instalados
        with patch.object(ollama_manager, 'list_installed_models') as mock_list:
            mock_list.return_value = [
                ModelStatus(name="qwen2.5-coder:latest", size="4.7 GB", size_vram="5.0 GB", digest="current"),
                ModelStatus(name="deepseek-coder:latest", size="6.0 GB", size_vram="6.5 GB", digest="current")
            ]

            updates = ollama_manager.check_model_updates()
            assert updates == {}

    @patch('ollama_manager.requests.get')
    def test_check_model_updates_failure(self, mock_get, ollama_manager):
        """Test verificación de actualizaciones con error de red"""
        mock_get.side_effect = requests.exceptions.RequestException()

        updates = ollama_manager.check_model_updates()
        assert updates == {}

    @patch.object(OllamaManager, 'stop_model')
    @patch.object(OllamaManager, 'pull_model')
    @patch.object(OllamaManager, 'test_model')
    def test_update_model_if_available_with_update(self, mock_test, mock_pull, mock_stop, ollama_manager):
        """Test actualización de modelo cuando hay versión más reciente"""
        mock_pull.return_value = True
        mock_test.return_value = True

        with patch.object(ollama_manager, 'check_model_updates') as mock_check:
            mock_check.return_value = {
                "qwen2.5-coder:latest": {
                    "current": "qwen2.5-coder:latest",
                    "latest": "qwen2.5-coder:7b",
                    "base_name": "qwen2.5-coder"
                }
            }

            result = ollama_manager.update_model_if_available("qwen2.5-coder:latest")
            assert result == True

            # Verificar que se llamó a stop, pull y test
            mock_stop.assert_called_once_with("qwen2.5-coder:latest")
            mock_pull.assert_called_once_with("qwen2.5-coder:7b", show_progress=True)
            mock_test.assert_called_once_with("qwen2.5-coder:7b")

    @patch.object(OllamaManager, 'stop_model')
    @patch.object(OllamaManager, 'pull_model')
    def test_update_model_if_available_no_update(self, mock_pull, mock_stop, ollama_manager):
        """Test actualización de modelo cuando no hay updates"""
        with patch.object(ollama_manager, 'check_model_updates', return_value={}):
            result = ollama_manager.update_model_if_available("qwen2.5-coder:latest")
            assert result == True

            # No se deberían llamar stop ni pull
            mock_stop.assert_not_called()
            mock_pull.assert_not_called()

    def test_ensure_max_loaded_respected(self, ollama_manager):
        """Test aseguramiento de límite de modelos cargados"""
        with patch.object(ollama_manager, 'get_running_models', return_value=["model1", "model2", "model3"]):
            with patch.object(ollama_manager, 'stop_model') as mock_stop:
                ollama_manager.ensure_max_loaded_respected()

                # Debería detener un modelo para respetar el límite de 2
                mock_stop.assert_called_once()

    def test_get_status_summary(self, ollama_manager):
        """Test obtención de resumen completo de estado"""
        with patch.object(ollama_manager, 'check_ollama_running', return_value=True), \
             patch.object(ollama_manager, 'list_installed_models', return_value=[ModelStatus(name="test", size="1GB", size_vram="1GB", digest="abc")]), \
             patch.object(ollama_manager, 'get_running_models', return_value=["test"]), \
             patch.object(ollama_manager, 'check_model_updates', return_value={"test": {"current": "test", "latest": "test:v2", "base_name": "test"}}):

            status = ollama_manager.get_status_summary()

            assert status["ollama_running"] == True
            assert status["models_installed"] == 1
            assert status["models_running"] == 1
            assert status["models_with_updates"] == 1
            assert "available_updates" in status


class TestModelStatus:
    """Pruebas para la clase ModelStatus"""

    def test_model_status_creation(self):
        """Test creación de ModelStatus"""
        status = ModelStatus(
            name="test-model:latest",
            size="4.7 GB",
            size_vram="5.0 GB",
            digest="abc123",
            loaded=True
        )

        assert status.name == "test-model:latest"
        assert status.size == "4.7 GB"
        assert status.size_vram == "5.0 GB"
        assert status.digest == "abc123"
        assert status.loaded == True

    def test_model_status_defaults(self):
        """Test valores por defecto de ModelStatus"""
        status = ModelStatus(
            name="test-model:latest",
            size="4.7 GB",
            size_vram="5.0 GB",
            digest="abc123"
        )

        assert status.loaded == False


class TestVRAMUsage:
    """Pruebas para la clase VRAMUsage"""

    def test_vram_usage_creation(self):
        """Test creación de VRAMUsage"""
        vram = VRAMUsage(
            total_vram="8GB",
            used_vram="4GB",
            models_loaded=["model1", "model2"]
        )

        assert vram.total_vram == "8GB"
        assert vram.used_vram == "4GB"
        assert vram.models_loaded == ["model1", "model2"]


if __name__ == "__main__":
    pytest.main([__file__])