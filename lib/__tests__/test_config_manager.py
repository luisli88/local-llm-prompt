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

    def test_get_models_method(self, temp_config_dir, sample_config_data):
        """Test método get_models()"""
        # Crear archivo de configuración
        config_file = Path(temp_config_dir) / 'models.yml'
        with open(config_file, 'w') as f:
            yaml.dump(sample_config_data, f)

        with patch('config_manager.requests.get'):
            config_manager = ConfigManager(config_dir=temp_config_dir)
            models = config_manager.get_models()

            assert isinstance(models, dict)
            assert 'qwen' in models
            assert 'deepseek' in models

    def test_get_model_method(self, temp_config_dir, sample_config_data):
        """Test método get_model()"""
        # Crear archivo de configuración
        config_file = Path(temp_config_dir) / 'models.yml'
        with open(config_file, 'w') as f:
            yaml.dump(sample_config_data, f)

        with patch('config_manager.requests.get'):
            config_manager = ConfigManager(config_dir=temp_config_dir)
            model = config_manager.get_model('qwen')

            assert model is not None
            assert model.name == 'qwen2.5-coder:latest'

            # Modelo inexistente
            assert config_manager.get_model('nonexistent') is None

    def test_get_models_list_method(self, temp_config_dir, sample_config_data):
        """Test método get_models_list()"""
        # Crear archivo de configuración
        config_file = Path(temp_config_dir) / 'models.yml'
        with open(config_file, 'w') as f:
            yaml.dump(sample_config_data, f)

        with patch('config_manager.requests.get'):
            config_manager = ConfigManager(config_dir=temp_config_dir)
            models_list = config_manager.get_models_list()

            assert isinstance(models_list, list)
            assert len(models_list) == 2
            assert all(isinstance(model, ModelConfig) for model in models_list)

    def test_validate_config_valid(self, temp_config_dir, sample_config_data):
        """Test validación de configuración válida"""
        # Crear archivo de configuración
        config_file = Path(temp_config_dir) / 'models.yml'
        with open(config_file, 'w') as f:
            yaml.dump(sample_config_data, f)

        with patch('config_manager.requests.get'):
            config_manager = ConfigManager(config_dir=temp_config_dir)
            errors = config_manager.validate_config()

            assert errors == []

    def test_validate_config_invalid(self, temp_config_dir):
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

        # Crear archivo de configuración inválida
        config_file = Path(temp_config_dir) / 'models.yml'
        with open(config_file, 'w') as f:
            yaml.dump(invalid_config, f)

        with patch('config_manager.requests.get'):
            config_manager = ConfigManager(config_dir=temp_config_dir)
            errors = config_manager.validate_config()

            assert len(errors) >= 2  # Al menos 2 errores
            assert any('max_loaded_models' in error for error in errors)
            assert any('invalid' in error for error in errors)

    def test_get_default_config_dir(self, temp_config_dir):
        """Test obtención del directorio por defecto"""
        with patch('config_manager.requests.get'):
            config_manager = ConfigManager(config_dir=temp_config_dir)

            # Debería usar config/ local o ~/.config/llm-stack/
            default_dir = config_manager._get_default_config_dir()
            assert isinstance(default_dir, str)
            assert len(default_dir) > 0

    def test_get_minimal_config(self, temp_config_dir):
        """Test configuración mínima"""
        with patch('config_manager.requests.get'):
            config_manager = ConfigManager(config_dir=temp_config_dir)
            minimal = config_manager._get_minimal_config()

            assert 'global' in minimal
            assert 'models' in minimal
            assert minimal['global']['max_loaded_models'] == 1
            assert len(minimal['models']) == 1

    def test_get_default_models_config(self, temp_config_dir):
        """Test configuración por defecto de modelos"""
        with patch('config_manager.requests.get'):
            config_manager = ConfigManager(config_dir=temp_config_dir)
            default = config_manager._get_default_models_config()

            assert 'global' in default
            assert 'models' in default
            assert len(default['models']) >= 3  # qwen, deepseek, mistral

    @patch('config_manager.yaml.dump')
    def test_save_models_config(self, mock_yaml_dump, temp_config_dir):
        """Test guardado de configuración de modelos"""
        # Crear un ConfigManager sin llamar al constructor para evitar el dump inicial
        with patch('config_manager.requests.get'):
            with patch('config_manager.yaml.dump'):  # Mock yaml.dump durante __init__
                config_manager = ConfigManager(config_dir=temp_config_dir)
        
        # Limpiar el mock para contar solo las llamadas posteriores
        mock_yaml_dump.reset_mock()
        
        test_data = {'test': 'data'}
        config_manager._save_models_config(test_data)

        # Verificar que se llamó a yaml.dump solo una vez (la que queremos probar)
        mock_yaml_dump.assert_called_once()

        # Verificar que se creó el archivo
        config_file = Path(temp_config_dir) / 'models.yml'
        assert config_file.exists()

    def test_create_example_config(self, temp_config_dir):
        """Test creación de archivos de configuración de ejemplo"""
        with patch('config_manager.requests.get'):
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

    def test_detect_platform_forced_env(self, temp_config_dir, monkeypatch):
        """Test forzar detección de plataforma mediante variable de entorno"""
        monkeypatch.setenv('LLM_FORCE_PLATFORM', 'apple_m3')
        
        # Crear un config sin max_loaded_models explícito para que se aplique el perfil
        custom_config = {
            'global': {
                'ollama_host': 'http://localhost:11434',
                'auto_stop_inactive': True,
                'inactive_timeout_minutes': 30
                # Omitir max_loaded_models para que se aplique el perfil de plataforma
            },
            'models': {
                'qwen': {'name': 'qwen2.5-coder:latest', 'description': 'Test'}
            }
        }
        
        config_file = Path(temp_config_dir) / 'models.yml'
        with open(config_file, 'w') as f:
            yaml.dump(custom_config, f)
        
        with patch('config_manager.requests.get'):
            cm = ConfigManager(config_dir=temp_config_dir)

        assert cm.get_detected_platform() == 'apple_m3'
        profile = cm.get_platform_profile()
        assert profile.get('max_loaded_models') == 1
        # El max_loaded_models en config debe ser 1 porque se aplica el perfil de plataforma
        assert cm.config.max_loaded_models == 1

    def test_detect_platform_system_machine(self, temp_config_dir, monkeypatch):
        """Test detección por system/machine (Darwin + arm -> apple_m3)"""
        # Asegurar que no esté forzada la variable de entorno
        monkeypatch.delenv('LLM_FORCE_PLATFORM', raising=False)

        import platform
        monkeypatch.setattr(platform, 'system', lambda: 'Darwin')
        monkeypatch.setattr(platform, 'machine', lambda: 'arm64')

        # Crear un config sin max_loaded_models explícito para que se aplique el perfil
        custom_config = {
            'global': {
                'ollama_host': 'http://localhost:11434',
                'auto_stop_inactive': True,
                'inactive_timeout_minutes': 30
                # Omitir max_loaded_models para que se aplique el perfil de plataforma
            },
            'models': {
                'qwen': {'name': 'qwen2.5-coder:latest', 'description': 'Test'}
            }
        }
        
        config_file = Path(temp_config_dir) / 'models.yml'
        with open(config_file, 'w') as f:
            yaml.dump(custom_config, f)

        with patch('config_manager.requests.get'):
            cm = ConfigManager(config_dir=temp_config_dir)
        assert cm.get_detected_platform() == 'apple_m3'
        assert cm.get_platform_profile().get('memory_unified') is True
        # El max_loaded_models debe ser 1 porque se aplica el perfil de plataforma
        assert cm.config.max_loaded_models == 1


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



    def test_launcher_no_installation_in_launcher(self):
        """Verificar que el launcher NO incluye pasos de instalación (centralizado en la app)"""
        from pathlib import Path
        script = Path(__file__).resolve().parents[2] / 'llm-stack'
        assert script.exists(), "El script 'llm-stack' debe existir en el repo"
        content = script.read_text()
        # El launcher ya no debe contener instrucciones para instalar Homebrew u Ollama
        assert 'brew install --cask ollama' not in content
        assert 'brew install ollama' not in content
        assert 'raw.githubusercontent.com/Homebrew/install/HEAD/install.sh' not in content
        assert 'ollama' not in content or 'install' not in content.lower()
        # Verificar que el launcher no solicita confirmación interactiva
        assert 'read -p' not in content
        assert 'read -r' not in content
        assert 'read -n' not in content
        assert 'Press any key' not in content

    def test_main_contains_install_routine(self):
        """Verificar que la aplicación principal contiene la rutina de instalación centralizada"""
        from pathlib import Path
        main_py = Path(__file__).resolve().parents[2] / 'lib' / 'main.py'
        assert main_py.exists(), "El archivo 'lib/main.py' debe existir"
        content = main_py.read_text()
        # Debe existir la función de instalación de Ollama/Dependencias
        assert '_install_ollama' in content or 'install_ollama' in content
        # Debe existir una opción de menú para instalar dependencias
        assert 'Instalar Dependencias' in content or 'Install Dependencies' in content


if __name__ == "__main__":
    pytest.main([__file__])