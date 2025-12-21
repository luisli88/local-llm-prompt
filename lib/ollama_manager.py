"""
OllamaManager - Gestión directa de Ollama CLI para arquitectura local nativa
Sin contenedores, sin base de datos, operaciones directas con RTX 2070 SUPER
"""

import subprocess
import json
import time
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
import requests

from config_manager import config_manager, ModelConfig


@dataclass
class ModelStatus:
    """Estado de un modelo en Ollama"""
    name: str
    size: str
    size_vram: str
    digest: str
    loaded: bool = False


@dataclass
class VRAMUsage:
    """Uso de VRAM por modelo"""
    total_vram: str
    used_vram: str
    models_loaded: List[str]


class OllamaManager:
    """Gestor directo de Ollama CLI para operaciones locales"""

    def __init__(self):
        self.config = config_manager.get_config()
        self.ollama_host = self.config.ollama_host
        self.max_loaded = self.config.max_loaded_models

    def _run_command(self, command: List[str], timeout: int = 30) -> Tuple[bool, str]:
        """Ejecuta un comando de Ollama y retorna (éxito, output)"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            success = result.returncode == 0
            output = result.stdout if success else result.stderr
            return success, output.strip()
        except subprocess.TimeoutExpired:
            return False, "Timeout ejecutando comando"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def check_ollama_installed(self) -> bool:
        """Verifica si Ollama está instalado y funcionando"""
        success, output = self._run_command(["ollama", "--version"])
        return success and "ollama version" in output.lower()

    def check_ollama_running(self) -> bool:
        """Verifica si el servicio Ollama está corriendo"""
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def start_ollama_service(self) -> bool:
        """Inicia el servicio Ollama (si no está corriendo)"""
        if self.check_ollama_running():
            return True

        print("🚀 Iniciando servicio Ollama...")
        success, output = self._run_command(["ollama", "serve"], timeout=10)

        if success:
            # Esperar a que el servicio esté listo
            for _ in range(10):
                time.sleep(1)
                if self.check_ollama_running():
                    return True

        return False

    def list_installed_models(self) -> List[ModelStatus]:
        """Lista todos los modelos instalados localmente"""
        success, output = self._run_command(["ollama", "list"])

        if not success:
            return []

        models = []
        lines = output.strip().split('\n')

        # Skip header line
        for line in lines[1:]:
            if line.strip():
                parts = line.split()
                if len(parts) >= 4:
                    name = parts[0]
                    size = parts[2] if len(parts) > 2 else "unknown"
                    size_vram = parts[3] if len(parts) > 3 else "unknown"
                    digest = parts[-1] if len(parts) > 1 else ""

                    models.append(ModelStatus(
                        name=name,
                        size=size,
                        size_vram=size_vram,
                        digest=digest,
                        loaded=False  # Will be updated by get_running_models
                    ))

        return models

    def get_running_models(self) -> List[str]:
        """Obtiene lista de modelos actualmente cargados en memoria"""
        try:
            response = requests.get(f"{self.ollama_host}/api/ps", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
        except:
            pass
        return []

    def get_vram_usage(self) -> VRAMUsage:
        """Obtiene información de uso de VRAM"""
        running = self.get_running_models()

        # Estimación simple de VRAM (podría mejorarse con nvidia-ml)
        total_vram = "8GB"  # RTX 2070 SUPER
        used_vram = f"~{len(running) * 5}GB"  # Estimación aproximada

        return VRAMUsage(
            total_vram=total_vram,
            used_vram=used_vram,
            models_loaded=running
        )

    def pull_model(self, model_name: str, show_progress: bool = True) -> bool:
        """Descarga un modelo desde el registry de Ollama"""
        print(f"📥 Descargando modelo: {model_name}")

        if show_progress:
            # Ejecutar sin capture_output para mostrar progreso
            try:
                result = subprocess.run(["ollama", "pull", model_name])
                return result.returncode == 0
            except KeyboardInterrupt:
                print("\n⚠️  Descarga interrumpida por usuario")
                return False
        else:
            success, output = self._run_command(["ollama", "pull", model_name], timeout=300)  # 5min timeout
            if success:
                print(f"✅ Modelo {model_name} descargado exitosamente")
            else:
                print(f"❌ Error descargando {model_name}: {output}")
            return success

    def remove_model(self, model_name: str) -> bool:
        """Elimina un modelo instalado"""
        print(f"🗑️  Eliminando modelo: {model_name}")
        success, output = self._run_command(["ollama", "rm", model_name])

        if success:
            print(f"✅ Modelo {model_name} eliminado")
        else:
            print(f"❌ Error eliminando {model_name}: {output}")

        return success

    def stop_model(self, model_name: str) -> bool:
        """Detiene un modelo cargado en memoria (libera VRAM)"""
        print(f"🛑 Deteniendo modelo: {model_name}")
        success, output = self._run_command(["ollama", "stop", model_name])

        if success:
            print(f"✅ Modelo {model_name} detenido (VRAM liberada)")
        else:
            print(f"❌ Error deteniendo {model_name}: {output}")

        return success

    def test_model(self, model_name: str, prompt: str = "Hello, how are you?") -> bool:
        """Test básico de funcionamiento de un modelo"""
        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": 50}
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                if "response" in data and data["response"].strip():
                    print(f"✅ Modelo {model_name} responde correctamente")
                    return True

            print(f"❌ Modelo {model_name} no responde correctamente")
            return False

        except Exception as e:
            print(f"❌ Error testeando {model_name}: {str(e)}")
            return False

    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Obtiene información detallada de un modelo"""
        try:
            response = requests.post(
                f"{self.ollama_host}/api/show",
                json={"name": model_name},
                timeout=10
            )

            if response.status_code == 200:
                return response.json()

        except Exception as e:
            print(f"❌ Error obteniendo info de {model_name}: {str(e)}")

        return None

    def ensure_max_loaded_respected(self) -> None:
        """Asegura que no se exceda el límite de modelos cargados"""
        running = self.get_running_models()

        if len(running) > self.max_loaded:
            print(f"⚠️  Demasiados modelos cargados ({len(running)} > {self.max_loaded})")
            print("🧹 Liberando VRAM...")

            # Obtener modelos por prioridad (menos prioritarios primero)
            models_by_priority = config_manager.get_models_by_priority()
            low_priority_names = [m.name for m in models_by_priority[self.max_loaded:]]

            # Detener modelos de baja prioridad que estén corriendo
            for model_name in running:
                if model_name in low_priority_names:
                    self.stop_model(model_name)
                    break  # Solo detener uno por vez

    def smart_activate_model(self, model_key: str) -> bool:
        """Activación inteligente de modelo con gestión de prioridades"""
        model_config = config_manager.get_model(model_key)
        if not model_config:
            print(f"❌ Modelo '{model_key}' no encontrado en configuración")
            return False

        # Verificar que el modelo esté instalado
        installed = self.list_installed_models()
        installed_names = [m.name for m in installed]

        if model_config.name not in installed_names:
            print(f"📥 Modelo {model_config.name} no instalado, descargando...")
            if not self.pull_model(model_config.name):
                return False

        # Asegurar límites de VRAM
        self.ensure_max_loaded_respected()

        # Test del modelo (esto lo carga en memoria)
        print(f"🧪 Activando modelo: {model_config.name}")
        return self.test_model(model_config.name)

    def check_model_updates(self) -> Dict[str, Dict[str, Any]]:
        """Verifica si hay actualizaciones disponibles para modelos instalados"""
        installed = self.list_installed_models()
        updates_available = {}

        try:
            # Consultar registry de Ollama para versiones más recientes
            response = requests.get("https://ollama.com/api/models", timeout=10)
            if response.status_code == 200:
                registry_models = response.json()

                # Crear mapa de modelos del registry
                registry_map = {}
                for model in registry_models:
                    name = model.get('name', '')
                    if ':' in name:
                        base_name = name.split(':')[0]
                        registry_map[base_name] = name

                # Verificar cada modelo instalado
                for installed_model in installed:
                    model_name = installed_model.name
                    if ':' in model_name:
                        base_name = model_name.split(':')[0]
                        current_tag = model_name.split(':')[1]

                        # Verificar si hay versión más reciente en registry
                        if base_name in registry_map:
                            latest_version = registry_map[base_name]
                            if latest_version != model_name:
                                updates_available[model_name] = {
                                    "current": model_name,
                                    "latest": latest_version,
                                    "base_name": base_name
                                }

        except Exception as e:
            print(f"⚠️  Error verificando actualizaciones: {e}")

        return updates_available

    def update_model_if_available(self, model_name: str) -> bool:
        """Actualiza un modelo si hay versión más reciente disponible"""
        updates = self.check_model_updates()

        if model_name in updates:
            latest_version = updates[model_name]["latest"]
            print(f"📥 Actualizando {model_name} → {latest_version}")

            # Primero detener el modelo si está corriendo
            if model_name in self.get_running_models():
                self.stop_model(model_name)

            # Actualizar a la versión más reciente
            success = self.pull_model(latest_version, show_progress=True)
            if success:
                print(f"✅ {model_name} actualizado a {latest_version}")
            return success

        print(f"ℹ️  {model_name} ya está actualizado")
        return True

    def get_status_summary(self) -> Dict[str, Any]:
        """Obtiene resumen completo del estado del sistema"""
        installed = self.list_installed_models()
        running = self.get_running_models()
        vram = self.get_vram_usage()
        updates = self.check_model_updates()

        return {
            "ollama_running": self.check_ollama_running(),
            "models_installed": len(installed),
            "models_running": len(running),
            "models_with_updates": len(updates),
            "vram_total": vram.total_vram,
            "vram_used": vram.used_vram,
            "running_models": running,
            "installed_models": [m.name for m in installed],
            "available_updates": updates
        }


# Instancia global
ollama_manager = OllamaManager()


if __name__ == "__main__":
    # Demo del OllamaManager
    print("🤖 OllamaManager Demo")
    print("=" * 50)

    print("🔍 Verificando instalación...")
    if not ollama_manager.check_ollama_installed():
        print("❌ Ollama no está instalado")
        print("Ejecuta: curl -fsSL https://ollama.com/install.sh | sh")
        exit(1)

    print("✅ Ollama instalado")

    print("\n🚀 Verificando servicio...")
    if not ollama_manager.check_ollama_running():
        print("📡 Servicio no corriendo, iniciando...")
        if ollama_manager.start_ollama_service():
            print("✅ Servicio iniciado")
        else:
            print("❌ Error iniciando servicio")
            exit(1)

    print("✅ Servicio corriendo")

    print("\n📊 Estado del sistema:")
    status = ollama_manager.get_status_summary()
    print(f"  • Modelos instalados: {status['models_installed']}")
    print(f"  • Modelos corriendo: {status['models_running']}")
    print(f"  • VRAM: {status['vram_used']} / {status['vram_total']}")

    if status['running_models']:
        print(f"  • Activos: {', '.join(status['running_models'])}")

    print("\n📋 Modelos disponibles:")
    installed = ollama_manager.list_installed_models()
    for model in installed[:5]:  # Mostrar primeros 5
        print(f"  • {model.name} ({model.size})")

    if len(installed) > 5:
        print(f"  • ... y {len(installed) - 5} más")