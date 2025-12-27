"""
ConfigManager - Gestión de configuración YAML para LLM Stack Manager
Arquitectura simplificada con Ollama local nativo
"""

import os
import yaml
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ModelConfig:
    """Configuración de un modelo individual"""
    name: str
    description: str
    max_context: Optional[int] = None
    temperature: Optional[float] = None


@dataclass
class AppConfig:
    """Configuración completa de la aplicación"""
    models: Dict[str, ModelConfig]
    ollama_host: str = "http://localhost:11434"
    max_loaded_models: int = 2  # RTX 2070 SUPER 8GB limit
    auto_stop_inactive: bool = True
    inactive_timeout_minutes: int = 30


class ConfigManager:
    """Gestor de configuración YAML para la aplicación"""

    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = config_dir or self._get_default_config_dir()
        self.config = self._load_config()
        self.app_config = self._load_app_config()

        # Detectar plataforma y aplicar perfil si corresponde
        self._detected_platform = None
        self._platform_profile = {}
        self._apply_platform_profile()

    def get_available_models(self) -> List[str]:
        """Obtiene lista de modelos disponibles en Ollama registry"""
        try:
            response = requests.get("https://ollama.com/api/models", timeout=10)
            if response.status_code == 200:
                models_data = response.json()
                return [model.get('name', '') for model in models_data if model.get('name')]
        except Exception:
            pass
        return []


    def _get_default_config_dir(self) -> str:
        """Obtiene la ruta por defecto del directorio de configuración"""
        # Primero buscar en directorio local 'config/', luego en ~/.config/llm-stack/
        local_config = Path.cwd() / 'config'
        if local_config.exists():
            return str(local_config)

        # Fallback a directorio de usuario
        user_config = Path.home() / '.config' / 'llm-stack'
        user_config.mkdir(parents=True, exist_ok=True)
        return str(user_config)

    def _load_config(self) -> AppConfig:
        """Carga la configuración de modelos desde archivo externo"""
        models_file = Path(self.config_dir) / 'models.yml'

        if models_file.exists():
            try:
                with open(models_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                print(f"✅ Configuración cargada desde: {models_file}")
            except Exception as e:
                print(f"❌ Error cargando configuración de modelos: {e}")
                print("📝 Usando configuración mínima...")
                data = self._get_minimal_config()
        else:
            print(f"⚠️  Archivo de configuración no encontrado: {models_file}")
            print("📝 Creando configuración por defecto...")
            data = self._get_default_models_config()
            self._save_models_config(data)

        # Guardar el dict crudo para referencias (p. ej. decidir si debemos sobreescribir valores por perfil)
        self._raw_config = data

        return self._parse_config(data)

    def _load_app_config(self) -> Dict[str, Any]:
        """Carga la configuración de aplicación"""
        app_file = Path(self.config_dir) / 'app.yml'

        if app_file.exists():
            try:
                with open(app_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                print(f"⚠️  Error cargando configuración de app: {e}")

        return {}

    def _get_minimal_config(self) -> Dict[str, Any]:
        """Configuración mínima para funcionamiento básico"""
        return {
            'global': {
                'ollama_host': 'http://localhost:11434',
                'max_loaded_models': 1,
                'auto_stop_inactive': False,
                'inactive_timeout_minutes': 60
            },
            'models': {
                'qwen': {
                    'name': 'qwen2.5-coder:latest',
                    'description': 'Code completion'
                }
            }
        }

    def _get_default_models_config(self) -> Dict[str, Any]:
        """Configuración por defecto de modelos"""
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
                    'description': 'Code completion and programming'
                },
                'deepseek': {
                    'name': 'deepseek-coder:latest',
                    'description': 'Technical reasoning and analysis'
                },
                'mistral': {
                    'name': 'mistral:latest',
                    'description': 'Documentation and architecture'
                }
            }
        }

    def _save_models_config(self, data: Dict[str, Any]) -> None:
        """Guarda la configuración de modelos"""
        config_file = Path(self.config_dir) / 'models.yml'
        config_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            print(f"✅ Configuración guardada en: {config_file}")
        except Exception as e:
            print(f"❌ Error guardando configuración: {e}")

    def _parse_config(self, data: Dict[str, Any]) -> AppConfig:
        """Parsea los datos YAML a objetos de configuración"""
        models = {}
        global_config = data.get('global', {})

        for key, model_data in data.get('models', {}).items():
            models[key] = ModelConfig(
                name=model_data['name'],
                description=model_data.get('description', ''),
                max_context=model_data.get('max_context'),
                temperature=model_data.get('temperature')
            )

        return AppConfig(
            models=models,
            ollama_host=global_config.get('ollama_host', 'http://localhost:11434'),
            max_loaded_models=global_config.get('max_loaded_models', 2),
            auto_stop_inactive=global_config.get('auto_stop_inactive', True),
            inactive_timeout_minutes=global_config.get('inactive_timeout_minutes', 30)
        )

    # -------------------- Platform detection and profiles --------------------
    def detect_platform(self) -> Dict[str, Any]:
        """Detecta la plataforma y devuelve un dict con nombre y perfil.

        - Soporta forzar plataforma mediante la variable de entorno `LLM_FORCE_PLATFORM`.
        - Detecta Apple Silicon (macOS + arm64) y devuelve perfil `apple_m3`.
        """
        import platform

        # Permitir forzar plataforma (útil para tests)
        forced = os.getenv('LLM_FORCE_PLATFORM')
        if forced:
            name = forced.lower()
            if name in ('apple_m3', 'apple-m3', 'apple'):
                return {
                    'platform': 'apple_m3',
                    'profile': {'max_loaded_models': 1, 'memory_unified': True}
                }
            return {'platform': name, 'profile': {}}

        system = platform.system()
        machine = platform.machine()

        # macOS Apple Silicon
        if system == 'Darwin' and machine and machine.startswith('arm'):
            return {
                'platform': 'apple_m3',
                'profile': {'max_loaded_models': 1, 'memory_unified': True}
            }

        # Fallback: devolver sistema en minúsculas
        return {'platform': system.lower(), 'profile': {}}

    def _apply_platform_profile(self) -> None:
        """Aplica ajustes recomendados según el perfil de plataforma detectado."""
        detected = self.detect_platform()
        self._detected_platform = detected.get('platform')
        self._platform_profile = detected.get('profile', {}) or {}

        # Aplicar overrides básicos
        if self._platform_profile.get('max_loaded_models'):
            # Ajustar max_loaded_models si el perfil lo requiere **solo si no fue explícitamente definido** en el archivo de configuración
            try:
                raw_global = getattr(self, '_raw_config', {}).get('global', {}) or {}

                if 'max_loaded_models' not in raw_global:
                    # Solo aplicar cuando la configuración no especifica explícitamente este valor
                    self.config.max_loaded_models = int(self._platform_profile['max_loaded_models'])
                    print(f"🔎 Plataforma detectada: {self._detected_platform} — aplicando perfil")
                else:
                    # Mantener el valor explícito del usuario
                    print(f"🔎 Plataforma detectada: {self._detected_platform} — perfil disponible pero se respeta la configuración explícita")
            except Exception:
                pass

    def get_detected_platform(self) -> Optional[str]:
        """Retorna el nombre de la plataforma detectada (e.g. 'apple_m3')"""
        return self._detected_platform

    def get_platform_profile(self) -> Dict[str, Any]:
        """Retorna el perfil aplicado para la plataforma detectada"""
        return self._platform_profile

    def _save_config(self, data: Dict[str, Any]) -> None:
        """Guarda la configuración en archivo YAML"""
        config_file = Path(self.config_dir) / 'models.yml'
        config_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            print(f"❌ Error guardando configuración: {e}")

    def get_config(self) -> AppConfig:
        """Obtiene la configuración completa"""
        return self.config

    def get_models(self) -> Dict[str, ModelConfig]:
        """Obtiene la lista de modelos configurados"""
        return self.config.models

    def get_model(self, key: str) -> Optional[ModelConfig]:
        """Obtiene un modelo específico por clave"""
        return self.config.models.get(key)

    def get_models_list(self) -> List[ModelConfig]:
        """Obtiene lista de modelos configurados"""
        return list(self.config.models.values())

    def _config_to_dict(self) -> Dict[str, Any]:
        """Convierte la configuración a diccionario para guardar"""
        data = {
            'ollama_host': self.config.ollama_host,
            'max_loaded_models': self.config.max_loaded_models,
            'auto_stop_inactive': self.config.auto_stop_inactive,
            'inactive_timeout_minutes': self.config.inactive_timeout_minutes,
            'models': {}
        }

        for key, model in self.config.models.items():
            data['models'][key] = {
                'name': model.name,
                'description': model.description,
                'max_context': model.max_context,
                'temperature': model.temperature
            }

        return data

    def validate_config(self) -> List[str]:
        """Valida la configuración y retorna lista de errores"""
        errors = []

        if not self.config.models:
            errors.append("No hay modelos configurados")

        for key, model in self.config.models.items():
            if not model.name:
                errors.append(f"Modelo '{key}' no tiene nombre")

        if self.config.max_loaded_models < 1:
            errors.append("max_loaded_models debe ser al menos 1")

        return errors

    def create_example_config(self) -> None:
        """Crea archivos de configuración de ejemplo"""
        example_dir = Path(self.config_dir) / 'examples'
        example_dir.mkdir(parents=True, exist_ok=True)

        # Crear ejemplo de models.yml
        models_example = example_dir / 'models.example.yml'
        with open(models_example, 'w', encoding='utf-8') as f:
            yaml.dump(self._get_default_models_config(), f, default_flow_style=False, sort_keys=False)

        # Crear ejemplo de app.yml
        app_example = example_dir / 'app.example.yml'
        app_config = {
            'logging': {'level': 'INFO', 'file': 'logs/llm-stack.log'},
            'ui': {'theme': 'dark', 'language': 'es'},
            'performance': {'max_concurrent_downloads': 1},
            'security': {'allow_remote_access': False},
            'development': {'debug_mode': False}
        }
        with open(app_example, 'w', encoding='utf-8') as f:
            yaml.dump(app_config, f, default_flow_style=False, sort_keys=False)

        print(f"📝 Configuraciones de ejemplo creadas en: {example_dir}")


# Instancia global para uso en la aplicación
config_manager = ConfigManager()


if __name__ == "__main__":
    # Demo del ConfigManager
    print("🔧 ConfigManager Demo")
    print("=" * 50)

    config = config_manager.get_config()
    print(f"📊 Modelos configurados: {len(config.models)}")
    print(f"🎯 Máximo modelos cargados: {config.max_loaded_models}")
    print(f"⏰ Timeout inactivo: {config.inactive_timeout_minutes}min")
    print()

    print("📋 Modelos configurados:")
    for model in config_manager.get_models_list():
        print(f"  • {model.name} - {model.description}")

    print()
    errors = config_manager.validate_config()
    if errors:
        print("❌ Errores de configuración:")
        for error in errors:
            print(f"  • {error}")
    else:
        print("✅ Configuración válida")