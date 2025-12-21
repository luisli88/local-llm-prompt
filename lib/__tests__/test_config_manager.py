"""
Pruebas unitarias para ConfigManager
Tests para carga de configuración YAML, validación y gestión de modelos
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open
import yaml

from config_manager import ConfigManager, ModelConfig, AppConfig


class TestConfigManager:
    """Suite de pruebas para ConfigManager"""

    @pytest.fixture
    def temp_config_dir(self):
        """Fixture que crea un directorio temporal para configuración"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def sample_config_data(self):
        """Datos de configuración de ejemplo"""
        return {
            'global': {
                'ollama_host': 'http://localhost:11434',
                'max_loaded_models': 2,
                'auto_stop_inactive': True,
                'inactive_timeout_minutes': 30
            },
            'models': {
                'qwen': {
                    'name': 'qwen2.5-coder:latest',
                    'description': 'Code completion and programming',
                    'max_context': 32768,
                    'temperature': 0.1
                },
                'deepseek': {
                    'name': 'deepseek-coder:latest',
                    'description': 'Technical reasoning and analysis'
                }
            }
        }

    def test_config_manager_init_with_custom_dir(self, temp_config_dir):
        """Test inicialización con directorio personalizado"""
        config_manager = ConfigManager(config_dir=temp_config_dir)

        assert config_manager.config_dir == temp_config_dir
        assert isinstance(config_manager.config, AppConfig)

    def test_load_config_with_valid_file(self, temp_config_dir, sample_config_data):
        """Test carga de configuración desde archivo válido"""
        # Crear archivo de configuración
        config_file = Path(temp_config_dir) / 'models.yml'
        with open(config_file, 'w') as f:
            yaml.dump(sample_config_data, f)

        config_manager = ConfigManager(config_dir=temp_config_dir)

        # Verificar que se cargó correctamente
        assert config_manager.config.ollama_host == 'http://localhost:11434'
        assert config_manager.config.max_loaded_models == 2
        assert len(config_manager.config.models) == 2

        # Verificar modelos
        assert 'qwen' in config_manager.config.models
        assert 'deepseek' in config_manager.config.models

        qwen_model = config_manager.config.models['qwen']
        assert qwen_model.name == 'qwen2.5-coder:latest'
        assert qwen_model.description == 'Code completion and programming'
        assert qwen_model.max_context == 32768
        assert qwen_model.temperature == 0.1

    def test_load_config_creates_default_when_no_file(self, temp_config_dir):
        """Test que crea configuración por defecto cuando no existe archivo"""
        config_manager = ConfigManager(config_dir=temp_config_dir)

        # Debería tener configuración por defecto
        assert config_manager.config.ollama_host == 'http://localhost:11434'
        assert config_manager.config.max_loaded_models == 2
        assert len(config_manager.config.models) >= 3  # qwen, deepseek, mistral

        # Verificar que se creó el archivo
        config_file = Path(temp_config_dir) / 'models.yml'
        assert config_file.exists()

    def test_parse_config_with_global_and_models(self, sample_config_data):
        """Test parsing de configuración con global y models"""
        config_manager = ConfigManager()

        app_config = config_manager._parse_config(sample_config_data)

        assert isinstance(app_config, AppConfig)
        assert app_config.ollama_host == 'http://localhost:11434'
        assert app_config.max_loaded_models == 2
        assert app_config.auto_stop_inactive == True
        assert app_config.inactive_timeout_minutes == 30

        assert len(app_config.models) == 2
        assert isinstance(app_config.models['qwen'], ModelConfig)

    def test_get_models_method(self, sample_config_data):
        """Test método get_models()"""
        with patch('builtins.open', mock_open()) as mock_file:
            mock_file.return_value.read.return_value = yaml.dump(sample_config_data)

            config_manager = ConfigManager()
            models = config_manager.get_models()

            assert isinstance(models, dict)
            assert 'qwen' in models
            assert 'deepseek' in models

    def test_get_model_method(self, sample_config_data):
        """Test método get_model()"""
        with patch('builtins.open', mock_open()) as mock_file:
            mock_file.return_value.read.return_value = yaml.dump(sample_config_data)

            config_manager = ConfigManager()
            model = config_manager.get_model('qwen')

            assert model is not None
            assert model.name == 'qwen2.5-coder:latest'

            # Modelo inexistente
            assert config_manager.get_model('nonexistent') is None

    def test_get_models_list_method(self, sample_config_data):
        """Test método get_models_list()"""
        with patch('builtins.open', mock_open()) as mock_file:
            mock_file.return_value.read.return_value = yaml.dump(sample_config_data)

            config_manager = ConfigManager()
            models_list = config_manager.get_models_list()

            assert isinstance(models_list, list)
            assert len(models_list) == 2
            assert all(isinstance(model, ModelConfig) for model in models_list)

    def test_validate_config_valid(self, sample_config_data):
        """Test validación de configuración válida"""
        with patch('builtins.open', mock_open()) as mock_file:
            mock_file.return_value.read.return_value = yaml.dump(sample_config_data)

            config_manager = ConfigManager()
            errors = config_manager.validate_config()

            assert errors == []

    def test_validate_config_invalid(self):
        """Test validación de configuración inválida"""
        invalid_config = {
            'global': {
                'max_loaded_models': 0  # Inválido
            },
            'models': {
                'invalid': {
                    'name': '',  # Nombre vacío
                    'description': 'Test'
                }
            }
        }

        with patch('builtins.open', mock_open()) as mock_file:
            mock_file.return_value.read.return_value = yaml.dump(invalid_config)

            config_manager = ConfigManager()
            errors = config_manager.validate_config()

            assert len(errors) >= 2  # Al menos 2 errores
            assert any('max_loaded_models' in error for error in errors)
            assert any('invalid' in error for error in errors)

    def test_get_default_config_dir(self):
        """Test obtención del directorio por defecto"""
        config_manager = ConfigManager()

        # Debería usar config/ local o ~/.config/llm-stack/
        default_dir = config_manager._get_default_config_dir()
        assert isinstance(default_dir, str)
        assert len(default_dir) > 0

    def test_get_minimal_config(self):
        """Test configuración mínima"""
        config_manager = ConfigManager()
        minimal = config_manager._get_minimal_config()

        assert 'global' in minimal
        assert 'models' in minimal
        assert minimal['global']['max_loaded_models'] == 1
        assert len(minimal['models']) == 1

    def test_get_default_models_config(self):
        """Test configuración por defecto de modelos"""
        config_manager = ConfigManager()
        default = config_manager._get_default_models_config()

        assert 'global' in default
        assert 'models' in default
        assert len(default['models']) >= 3  # qwen, deepseek, mistral

    @patch('config_manager.yaml.dump')
    def test_save_models_config(self, mock_yaml_dump, temp_config_dir):
        """Test guardado de configuración de modelos"""
        config_manager = ConfigManager(config_dir=temp_config_dir)
        test_data = {'test': 'data'}

        config_manager._save_models_config(test_data)

        # Verificar que se llamó a yaml.dump
        mock_yaml_dump.assert_called_once()

        # Verificar que se creó el archivo
        config_file = Path(temp_config_dir) / 'models.yml'
        assert config_file.exists()

    def test_create_example_config(self, temp_config_dir):
        """Test creación de archivos de configuración de ejemplo"""
        config_manager = ConfigManager(config_dir=temp_config_dir)

        with patch('config_manager.yaml.dump'):
            config_manager.create_example_config()

        # Verificar que se crearon los archivos de ejemplo
        examples_dir = Path(temp_config_dir) / 'examples'
        assert examples_dir.exists()

        example_models = examples_dir / 'models.example.yml'
        example_app = examples_dir / 'app.example.yml'

        assert example_models.exists()
        assert example_app.exists()


class TestModelConfig:
    """Pruebas para la clase ModelConfig"""

    def test_model_config_creation(self):
        """Test creación de ModelConfig"""
        model = ModelConfig(
            name="test-model:latest",
            description="Test model",
            max_context=4096,
            temperature=0.7
        )

        assert model.name == "test-model:latest"
        assert model.description == "Test model"
        assert model.max_context == 4096
        assert model.temperature == 0.7

    def test_model_config_defaults(self):
        """Test valores por defecto de ModelConfig"""
        model = ModelConfig(
            name="test-model:latest",
            description="Test model"
        )

        assert model.max_context is None
        assert model.temperature is None


class TestAppConfig:
    """Pruebas para la clase AppConfig"""

    def test_app_config_creation(self):
        """Test creación de AppConfig"""
        models = {
            'test': ModelConfig(name="test:latest", description="Test")
        }

        config = AppConfig(
            models=models,
            ollama_host="http://test:11434",
            max_loaded_models=3,
            auto_stop_inactive=False,
            inactive_timeout_minutes=60
        )

        assert config.models == models
        assert config.ollama_host == "http://test:11434"
        assert config.max_loaded_models == 3
        assert config.auto_stop_inactive == False
        assert config.inactive_timeout_minutes == 60

    def test_app_config_defaults(self):
        """Test valores por defecto de AppConfig"""
        config = AppConfig(models={})

        assert config.ollama_host == "http://localhost:11434"
        assert config.max_loaded_models == 2
        assert config.auto_stop_inactive == True
        assert config.inactive_timeout_minutes == 30


if __name__ == "__main__":
    pytest.main([__file__])