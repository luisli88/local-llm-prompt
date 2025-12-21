"""Interfaz de línea de comandos para la aplicación LLM Stack Manager."""

import sys
from typing import List, Dict, Any, Optional
from pathlib import Path
import subprocess
import time

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live

from lib.config import APP_CONFIG, UI_CONFIG, MODELS_CONFIG, get_project_root
from lib.docker_manager import DockerManager
from lib.model_manager import ModelManager
from lib.ollama_client import OllamaClient


class LLMStackApp:
    """Aplicación principal para gestión del stack LLM."""

    def __init__(self):
        self.console = Console()
        self.docker_manager = DockerManager()
        self.model_manager = ModelManager()
        self.ollama_client = OllamaClient()

        # Inicializar modelos en DB
        self.model_manager.initialize_models()

    def run(self):
        """Ejecuta el bucle principal de la aplicación."""
        while True:
            self._clear_screen()
            self._show_header()
            self._validate_dependencies()
            self._show_menu()

            choice = Prompt.ask("Selecciona una opción", choices=["1", "2", "3", "4", "5", "6", "0"])

            if choice == "0":
                self._print_success("¡Hasta luego!")
                break
            elif choice == "1":
                self._validate_installation()
            elif choice == "2":
                self._install_stack()
            elif choice == "3":
                self._activate_model()
            elif choice == "4":
                self._deactivate_model()
            elif choice == "5":
                self._update_models()
            elif choice == "6":
                self._deactivate_stack()

            if choice != "0":
                self._wait_for_continue()

    def _clear_screen(self):
        """Limpia la pantalla."""
        self.console.clear()

    def _show_header(self):
        """Muestra el encabezado de la aplicación."""
        header = Panel.fit(
            f"[bold blue]{APP_CONFIG['app_name']}[/bold blue]\n"
            f"[dim]Versión {APP_CONFIG['version']}[/dim]",
            border_style="blue"
        )
        self.console.print(header)
        self.console.print()

    def _validate_dependencies(self):
        """Valida las dependencias del sistema."""
        self.console.print("[bold]Validando Dependencias[/bold]")

        # Verificar Docker
        try:
            import docker
            client = docker.from_env()
            docker_version = client.version()['Version']
            self._print_success(f"Docker: OK (versión {docker_version})")
        except Exception as e:
            self._print_error(f"Docker: ERROR - {e}")

        # Verificar NVIDIA (si está disponible)
        try:
            result = self._run_command(["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader,nounits"])
            if result.returncode == 0:
                nvidia_version = result.stdout.strip()
                self._print_success(f"NVIDIA Driver: OK (versión {nvidia_version})")
            else:
                self._print_warning("NVIDIA Driver: No disponible")
        except Exception:
            self._print_warning("NVIDIA Driver: No disponible")

        self.console.print()

    def _show_menu(self):
        """Muestra el menú principal con información de modelos activos."""
        # Sincronizar estado con Docker
        self.model_manager.sync_with_docker()

        # Mostrar modelos activos
        self.console.print("[bold]Modelos activos:[/bold]")
        active_models = self.model_manager.get_active_models()

        if active_models:
            for model in active_models:
                url = f"http://localhost:{model['port']}/v1"
                self.console.print(f"  ✅ {model['name']} - [link={url}]{url}[/link]")
        else:
            self.console.print("  ℹ️  Ningún modelo activo")

        self.console.print()

        # Menú de opciones
        self.console.print("[bold]Menú Principal:[/bold]")
        self.console.print("  1. Validar Instalación")
        self.console.print("  2. Instalar Stack")
        self.console.print("  3. Activar Modelo")
        self.console.print("  4. Desactivar Modelo")
        self.console.print("  5. Actualizar Modelos")
        self.console.print("  6. Desactivar Stack Completo")
        self.console.print("  0. Salir")
        self.console.print()

    def _validate_installation(self):
        """Valida la instalación completa del stack."""
        self.console.print("[bold]Validando Instalación Completa[/bold]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Verificando componentes...", total=100)

            # Verificar docker-compose.yml (usar ruta configurada)
            from lib.config import get_compose_file
            compose_file = get_compose_file()
            if compose_file.exists():
                progress.update(task, advance=20, description=f"Docker Compose: OK ({compose_file})")
            else:
                progress.update(task, advance=20, description="Docker Compose: FALTA")
                self._print_error(f"Archivo docker-compose.yml no encontrado en: {compose_file}")
                return

            # Verificar Docker
            if self._check_docker():
                progress.update(task, advance=20, description="Docker: OK")
            else:
                progress.update(task, advance=20, description="Docker: FALTA")
                self._print_error("Docker no está instalado o no funciona")
                return

            # Verificar NVIDIA
            if self._check_nvidia():
                progress.update(task, advance=20, description="NVIDIA: OK")
            else:
                progress.update(task, advance=20, description="NVIDIA: FALTA")

            # Verificar contenedores (opcional - pueden no estar corriendo)
            stack_status = self.docker_manager.get_stack_status()
            running_count = sum(1 for status in stack_status.values() if status['container'].get('running'))
            progress.update(task, advance=20, description=f"Contenedores corriendo: {running_count}/3")

        # La instalación es válida si Docker y docker-compose.yml existen
        # Los contenedores pueden no estar corriendo aún
        self._print_success("✅ Instalación válida - componentes básicos OK")
        if running_count == 0:
            self._print_info("ℹ️  Usa 'Instalar Stack' para iniciar los contenedores")
        elif running_count < 3:
            self._print_info(f"ℹ️  {running_count}/3 contenedores activos - algunos modelos pueden no estar disponibles")

    def _install_stack(self):
        """Instala el stack completo."""
        self.console.print("[bold]Instalando Stack Completo[/bold]")

        # Verificar que docker-compose.yml existe (usar ruta configurada)
        from lib.config import get_compose_file
        compose_file = get_compose_file()
        if not compose_file.exists():
            self._print_error(f"Archivo docker-compose.yml no encontrado en: {compose_file}")
            return

        # Iniciar todos los servicios con docker compose
        self._print_info("Iniciando contenedores con Docker Compose...")

        project_root = get_project_root()
        self._print_info(f"Directorio de proyecto: {project_root}")
        self._print_info(f"Archivo compose existe: {compose_file.exists()}")

        try:
            cmd = ["docker", "compose", "-f", str(compose_file), "up", "-d"]
            self._print_info(f"Ejecutando: {' '.join(cmd)} (compose file: {compose_file})")

            result = subprocess.run(
                cmd,
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=120  # 2 minutos timeout
            )

            if result.returncode == 0:
                self._print_success("✅ Stack iniciado exitosamente")

                # Esperar un poco y verificar estado
                self._print_info("Verificando estado de contenedores...")
                time.sleep(5)

                stack_status = self.docker_manager.get_stack_status()
                running_count = sum(1 for status in stack_status.values() if status['container'].get('running'))

                if running_count > 0:
                    self._print_success(f"✅ {running_count}/3 contenedores activos")
                    self._print_info("Los modelos estarán disponibles en unos momentos")
                else:
                    self._print_warning("⚠️  Contenedores iniciados pero aún no listos")

            else:
                self._print_error(f"Error iniciando stack: {result.stderr}")

        except subprocess.TimeoutExpired:
            self._print_error("Timeout iniciando contenedores")
        except Exception as e:
            self._print_error(f"Error inesperado: {str(e)}")

    def _activate_model(self):
        """Activa un modelo específico."""
        self.console.print("[bold]Activando Modelo[/bold]")

        # Mostrar modelos disponibles
        models = self.model_manager.get_all_models()
        self._show_models_table(models, "activar")

        if not models:
            self._print_error("No hay modelos configurados")
            return

        # Seleccionar modelo
        choices = [str(i + 1) for i in range(len(models))]
        choice = Prompt.ask("Selecciona modelo para activar", choices=choices)

        try:
            index = int(choice) - 1
            selected_model = models[index]

            with self.console.status(f"Activando {selected_model['name']}..."):
                success = self.docker_manager.start_container(selected_model['container_name'])

            if success:
                self.model_manager.set_model_status(selected_model['container_name'], 'active')
                self._print_success(f"{selected_model['name']} activado exitosamente")
                url = f"http://localhost:{selected_model['port']}/api/tags"
                self._print_info(f"Verifica funcionamiento: curl {url}")
            else:
                self._print_error(f"Error activando {selected_model['name']}")

        except (ValueError, IndexError):
            self._print_error("Selección inválida")

    def _deactivate_model(self):
        """Desactiva un modelo específico."""
        self.console.print("[bold]Desactivando Modelo[/bold]")

        # Mostrar solo modelos activos
        active_models = self.model_manager.get_active_models()

        if not active_models:
            self._print_warning("No hay modelos activos para desactivar")
            return

        self._show_models_table(active_models, "desactivar")

        # Seleccionar modelo
        choices = [str(i + 1) for i in range(len(active_models))]
        choice = Prompt.ask("Selecciona modelo para desactivar", choices=choices)

        try:
            index = int(choice) - 1
            selected_model = active_models[index]

            with self.console.status(f"Desactivando {selected_model['name']}..."):
                success = self.docker_manager.stop_container(selected_model['container_name'])

            if success:
                self.model_manager.set_model_status(selected_model['container_name'], 'inactive')
                self._print_success(f"{selected_model['name']} desactivado exitosamente")
            else:
                self._print_error(f"Error desactivando {selected_model['name']}")

        except (ValueError, IndexError):
            self._print_error("Selección inválida")

    def _update_models(self):
        """Actualiza modelos."""
        self.console.print("[bold]Actualizando Modelos[/bold]")

        # Por defecto actualizar todos los modelos
        self._print_info("Actualizando todos los modelos...")

        # Ejecutar actualización
        with self.console.status("Actualizando modelos..."):
            results = self.ollama_client.update_models()

        # Mostrar resultados
        success_count = 0
        for model_key, result in results.items():
            if result['success']:
                self._print_success(f"✅ {result['model']} actualizado exitosamente")
                # Actualizar versión en DB
                self.model_manager.update_model_version(result['container'], "latest")
                success_count += 1
            else:
                self._print_error(f"❌ Error actualizando {model_key}: {result.get('error', 'Error desconocido')}")

        if success_count == len(results):
            self._print_success(f"✅ Todos los modelos actualizados exitosamente ({success_count}/{len(results)})")
        else:
            self._print_warning(f"⚠️  Algunos modelos no se pudieron actualizar ({success_count}/{len(results)})")

    def _deactivate_stack(self):
        """Desactiva todo el stack."""
        self.console.print("[bold]Desactivando Stack Completo[/bold]")

        if not Confirm.ask("¿Estás seguro de que quieres detener todos los contenedores?"):
            self._print_info("Operación cancelada")
            return

        with self.console.status("Deteniendo contenedores..."):
            # Usar docker compose para detener todo (usar archivo compose configurado)
            from lib.config import get_compose_file
            compose_file = get_compose_file()
            cmd = ["docker", "compose", "-f", str(compose_file), "down"]
            result = self._run_command(cmd)

        if result.returncode == 0:
            # Marcar todos los modelos como inactivos
            for model_config in MODELS_CONFIG.values():
                self.model_manager.set_model_status(model_config['container_name'], 'inactive')

            self._print_success("Stack completo desactivado")

            # Mostrar memoria liberada
            try:
                result = self._run_command(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"])
                if result.returncode == 0:
                    free_memory = result.stdout.strip()
                    self._print_info(f"GPU liberada: {free_memory} MB libres")
            except Exception:
                pass
        else:
            # Mostrar stderr si está disponible para ayudar al debug
            try:
                err = result.stderr.strip()
                if err:
                    self._print_error(f"Error desactivando stack: {err}")
                else:
                    self._print_error("Error desactivando stack")
            except Exception:
                self._print_error("Error desactivando stack")

    def _show_models_table(self, models: List[Dict[str, Any]], action: str):
        """Muestra una tabla con los modelos."""
        table = Table(title=f"Modelos disponibles para {action}")
        table.add_column("N°", style="cyan", no_wrap=True)
        table.add_column("Modelo", style="white")
        table.add_column("Contenedor", style="blue")
        table.add_column("Puerto", style="green")
        table.add_column("Estado", style="yellow")
        table.add_column("Versión", style="magenta")

        for i, model in enumerate(models, 1):
            status_icon = "●" if model['status'] == 'active' else "○"
            status_color = "green" if model['status'] == 'active' else "red"
            version = model.get('installed_version', 'no instalado') or 'no instalado'

            table.add_row(
                str(i),
                model['name'],
                model['container_name'],
                str(model['port']),
                f"[{status_color}]{status_icon} {model['status']}[/{status_color}]",
                version
            )

        self.console.print(table)
        self.console.print()

    def _wait_for_continue(self):
        """Espera a que el usuario presione Enter."""
        self.console.print()
        Prompt.ask("Presiona Enter para continuar")

    def _run_command(self, cmd: List[str]) -> subprocess.CompletedProcess:
        """Ejecuta un comando del sistema."""
        return subprocess.run(cmd, capture_output=True, text=True)

    def _print_success(self, message: str):
        """Imprime un mensaje de éxito."""
        self.console.print(f"[green]✅ {message}[/green]")

    def _print_error(self, message: str):
        """Imprime un mensaje de error."""
        self.console.print(f"[red]❌ {message}[/red]")

    def _print_warning(self, message: str):
        """Imprime un mensaje de advertencia."""
        self.console.print(f"[yellow]⚠️  {message}[/yellow]")

    def _print_info(self, message: str):
        """Imprime un mensaje informativo."""
        self.console.print(f"[cyan]ℹ {message}[/cyan]")

    def _check_docker(self) -> bool:
        """Verifica que Docker esté instalado y funcionando."""
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _check_nvidia(self) -> bool:
        """Verifica que NVIDIA drivers estén instalados."""
        try:
            result = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False


def main():
    """Función principal."""
    try:
        app = LLMStackApp()
        app.run()
    except KeyboardInterrupt:
        print("\n¡Hasta luego!")
        sys.exit(0)
    except Exception as e:
        print(f"Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()