"""
Copyright (c) 2025 Alejandro Ramírez  
Bajo la Licencia de Autor Restringida (LAR) v1.0  
Más detalles en LICENSE
""" 
 
import tkinter as tk
from tkinter import messagebox, simpledialog
from core.jiraExtractor import JiraExtractor
from core.valueEdgeExtractor import ValueEdgeExtractor
from core.gherkinConverter import UltimateGherkinConverter
import configparser
import os
import sys
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s @ %(module)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def check_config():
    """Verificación avanzada del archivo de configuración"""
    try:
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        config_path = os.path.join(base_dir, 'secrets', 'secrets.ini')
        config = configparser.ConfigParser()
        config.read(config_path, encoding='utf-8')
        
        required_sections = {
            'ValueEdge': ['URL', 'USER', 'PASSWORD', 'SHARED_SPACE'],
            'JIRA': ['URL', 'EMAIL', 'API_TOKEN']
        }
        
        errors = []
        for section, keys in required_sections.items():
            if not config.has_section(section):
                errors.append(f"❌ Falta sección: [{section}]")
                continue
                
            for key in keys:
                if not config.has_option(section, key):
                    errors.append(f"❌ Falta clave: [{section}] {key}")
        
        if errors:
            error_msg = "\n".join(errors)
            error_msg += f"\n\n🔍 Ruta del archivo: {config_path}"
            raise RuntimeError(error_msg)
            
        return True
        
    except Exception as e:
        messagebox.showerror("Error de Configuración", 
            f"Error en el archivo secrets.ini:\n\n{str(e)}\n\n"
            "Verifica que:\n"
            "1. El archivo existe en secrets/secrets.ini\n"
            "2. Tiene las secciones [ValueEdge] y [JIRA]\n"
            "3. Todas las claves requeridas están presentes")
        sys.exit(1)

class AutomationApp:
    def __init__(self):
        check_config()
        self.root = tk.Tk()
        self.root.title("DICAI v1.05")
        self.root.geometry("400x300")
        self.current_project = None
        self.current_workspace = None
        self.jira_extractor = None
        self.ve_extractor = None
        self.load_config()
        self.create_main_menu()

    def load_config(self):
        """Cargar configuración con manejo de rutas empaquetadas"""
        try:
            if getattr(sys, 'frozen', False):
                base_dir = sys._MEIPASS
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
            
            config_path = os.path.join(base_dir, 'secrets', 'secrets.ini')
            self.config = configparser.ConfigParser()
            self.config.read(config_path, encoding='utf-8')
            
            if not self.config.has_section('JIRA'):
                raise ValueError("Sección [JIRA] no encontrada en configuración")
            if not self.config.has_section('ValueEdge'):
                raise ValueError("Sección [ValueEdge] no encontrada")
                
        except Exception as e:
            logger.error(f"Error cargando configuración: {str(e)}")
            messagebox.showerror("Error Fatal", "Configuración inválida")
            sys.exit(1)

    def create_main_menu(self):
        """Crear menú principal con nuevos estilos"""
        self.root.configure(bg="#f0f0f0")
        
        title_frame = tk.Frame(self.root, bg="#f0f0f0")
        title_frame.pack(pady=20)
        
        tk.Label(
            title_frame,
            text="DICAI v1.05",
            font=("Arial", 14, "bold"),
            bg="#f0f0f0"
        ).pack()
        
        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(pady=20)
        
        button_style = {
            "width": 25,
            "height": 2,
            "bg": "#2196F3",
            "fg": "white",
            "font": ("Arial", 10),
            "borderwidth": 0
        }
        
        tk.Button(
            button_frame,
            text="Extraer de ValueEdge",
            command=self.handle_valueedge,
            **button_style
        ).pack(pady=10)
        
        tk.Button(
            button_frame,
            text="Extraer de JIRA",
            command=self.handle_jira,
            **button_style
        ).pack(pady=10)
        
        tk.Button(
            button_frame,
            text="Salir",
            command=self.root.quit,
            bg="#f44336",
            **{k:v for k,v in button_style.items() if k != 'bg'}
        ).pack(pady=20)

    def handle_jira(self):
        """Manejador para JIRA con selección de proyecto primero"""
        self.current_project = simpledialog.askstring(
            "Proyecto JIRA", 
            "Ingrese clave del proyecto (ej: BT115):",
            parent=self.root
        )
        
        if self.current_project and self.current_project.strip():
            self.current_project = self.current_project.strip().upper()
            self.initialize_jira_extractor()
            self.show_jira_options()
        else:
            messagebox.showwarning("Entrada inválida", "Proyecto requerido")

    def handle_valueedge(self):
        """Manejador corregido para ValueEdge"""
        self.current_workspace = simpledialog.askstring(
            "Workspace ValueEdge", 
            "Ingrese Workspace ID de ValueEdge:",
            parent=self.root
        )
        
        if self.current_workspace and self.current_workspace.strip():
            self.current_workspace = self.current_workspace.strip()
            self.show_valueedge_options()
        else:
            messagebox.showwarning("Entrada inválida", "Workspace requerido")

    def show_valueedge_options(self):
        """Nuevo menú para ValueEdge"""
        option_window = tk.Toplevel(self.root)
        option_window.title(f"ValueEdge - Workspace {self.current_workspace}")
        option_window.geometry("300x200")
        option_window.configure(bg="#f0f0f0")
        
        tk.Label(
            option_window,
            text=f"Workspace: {self.current_workspace}",
            font=("Arial", 11),
            bg="#f0f0f0"
        ).pack(pady=10)
        
        button_style = {
            "width": 20,
            "height": 1,
            "bg": "#4CAF50",
            "fg": "white",
            "font": ("Arial", 10)
        }
        
        tk.Button(
            option_window,
            text="Extraer TODOS los casos",
            command=lambda: self.run_valueedge_extraction("all"),
            **button_style
        ).pack(pady=10)
        
        tk.Button(
            option_window,
            text="Extraer caso específico",
            command=lambda: self.run_valueedge_extraction("single"),
            **button_style
        ).pack(pady=10)

    def initialize_jira_extractor(self):
        """Inicializar extractor JIRA con validación"""
        try:
            self.jira_extractor = JiraExtractor(
                self.config.get('JIRA', 'URL'),
                self.config.get('JIRA', 'EMAIL'),
                self.config.get('JIRA', 'API_TOKEN')
            )
            
            if not self.jira_extractor.check_connection():
                messagebox.showerror(
                    "Error de conexión",
                    "Falló la conexión con JIRA\nVerifique credenciales",
                    parent=self.root
                )
                self.jira_extractor = None

        except Exception as e:
            messagebox.showerror("Error", f"Error inicializando JIRA: {str(e)}")
            self.jira_extractor = None

    def show_jira_options(self):
        """Ventana de opciones para JIRA"""
        if not self.jira_extractor:
            return
            
        option_window = tk.Toplevel(self.root)
        option_window.title(f"JIRA - {self.current_project}")
        option_window.geometry("300x200")
        option_window.configure(bg="#f0f0f0")
        
        tk.Label(
            option_window,
            text=f"Proyecto: {self.current_project}",
            font=("Arial", 11),
            bg="#f0f0f0"
        ).pack(pady=10)
        
        button_style = {
            "width": 20,
            "height": 1,
            "bg": "#2196F3",
            "fg": "white",
            "font": ("Arial", 10)
        }
        
        tk.Button(
            option_window,
            text="Extraer UN issue",
            command=lambda: self.run_jira_extraction("single"),
            **button_style
        ).pack(pady=10)
        
        tk.Button(
            option_window,
            text="Extraer TODOS los issues",
            command=lambda: self.run_jira_extraction("all"),
            **button_style
        ).pack(pady=10)

    def run_jira_extraction(self, mode):
        """Ejecutar extracción JIRA con conversión automática"""
        if not self.jira_extractor or not self.current_project:
            return
            
        try:
            output_dir = os.path.join("output", "jira_issues", self.current_project)
            os.makedirs(output_dir, exist_ok=True)
            
            progress_window = tk.Toplevel(self.root)
            progress_window.title("Progreso")
            progress_window.geometry("300x100")
            
            progress_label = tk.Label(
                progress_window,
                text="Iniciando extracción...",
                font=("Arial", 10)
            )
            progress_label.pack(pady=20)
            self.root.update()
            
            if mode == "all":
                issues = self.jira_extractor.get_all_issues(self.current_project)
                if not issues:
                    messagebox.showinfo("Info", "No se encontraron issues")
                    return
                    
                total = len(issues)
                for idx, issue_id in enumerate(issues, 1):
                    issue = self.jira_extractor.get_issue(issue_id)
                    if issue:
                        self.jira_extractor.save_issue(issue, output_dir)
                    progress_label.config(
                        text=f"Procesando {idx}/{total}\n{issue_id}"
                    )
                    progress_window.update()
                    
                messagebox.showinfo("Éxito", f"{total} issues extraídos")
                
            elif mode == "single":
                issue_number = simpledialog.askstring(
                    "Número de Issue", 
                    "Ingrese solo el número (ej: 123):",
                    parent=self.root
                )
                
                if issue_number and issue_number.strip().isdigit():
                    issue_id = f"{self.current_project}-{issue_number.strip()}"
                    issue = self.jira_extractor.get_issue(issue_id)
                    if issue:
                        self.jira_extractor.save_issue(issue, output_dir)
                        messagebox.showinfo("Éxito", f"Issue {issue_id} guardado")
                    else:
                        messagebox.showerror("Error", "Issue no encontrado")
                else:
                    messagebox.showwarning("Error", "Número inválido")
            
            # Conversión a Gherkin
            self.convert_files(
                input_dir=output_dir,
                output_dir=os.path.join("output", "features", "jira"),
                prefix=f"JIRA_{self.current_project}_"
            )

        except Exception as e:
            logger.error(f"Error en extracción JIRA: {str(e)}")
            messagebox.showerror("Error", f"Error crítico: {str(e)}")
        finally:
            if 'progress_window' in locals():
                progress_window.destroy()

    def run_valueedge_extraction(self, mode):
        """Ejecutar extracción ValueEdge con conversión"""
        try:
            output_dir = os.path.join("output", "test_cases", self.current_workspace)
            os.makedirs(output_dir, exist_ok=True)
            
            self.ve_extractor = ValueEdgeExtractor('secrets/secrets.ini')
            self.ve_extractor.workspace = self.current_workspace
            
            if not self.ve_extractor.login():
                messagebox.showerror("Error", "Falló login en ValueEdge")
                return
                
            if mode == "all":
                test_ids = self.ve_extractor.get_all_test_cases()
                if not test_ids:
                    messagebox.showinfo("Info", "No hay casos de prueba")
                    return
                    
                total = len(test_ids)
                progress_window = tk.Toplevel(self.root)
                progress_window.title("Progreso")
                progress_window.geometry("300x100")
                progress_label = tk.Label(progress_window, text="Iniciando...")
                progress_label.pack(pady=20)
                
                for idx, test_id in enumerate(test_ids, 1):
                    test_case = self.ve_extractor.get_test_case(test_id)
                    self.ve_extractor.save_test_case(test_case, output_dir)
                    progress_label.config(
                        text=f"Procesando {idx}/{total}\n{test_id}"
                    )
                    progress_window.update()
                    
                progress_window.destroy()
                messagebox.showinfo("Éxito", f"{total} casos extraídos")
                
            elif mode == "single":
                test_id = simpledialog.askstring(
                    "ID Caso", 
                    "Ingrese ID del caso (ej: 456):",
                    parent=self.root
                )
                
                if test_id and test_id.strip():
                    test_case = self.ve_extractor.get_test_case(test_id.strip())
                    if test_case:
                        self.ve_extractor.save_test_case(test_case, output_dir)
                        messagebox.showinfo("Éxito", "Caso guardado")
                    else:
                        messagebox.showerror("Error", "Caso no encontrado")
            
            # Conversión a Gherkin
            self.convert_files(
                input_dir=output_dir,
                output_dir=os.path.join("output", "features", "ve"),
                prefix=f"VE_{self.current_workspace}_"
            )

        except Exception as e:
            logger.error(f"Error en ValueEdge: {str(e)}")
            messagebox.showerror("Error", f"Error crítico: {str(e)}")

    def convert_files(self, input_dir: str, output_dir: str, prefix: str):
        """Conversión a Gherkin con prefijo único"""
        try:
            converter = UltimateGherkinConverter(input_dir, output_dir)
            
            # Monkey patch para nombres únicos
            original_normalize = converter._normalize_filename
            converter._normalize_filename = lambda x: prefix + original_normalize(x)
            
            converter.convert()
            logger.info(f"Conversión exitosa: {input_dir} -> {output_dir}")
            
        except Exception as e:
            logger.error(f"Error en conversión: {str(e)}")
            messagebox.showerror(
                "Error de Conversión", 
                f"No se pudieron generar features:\n{str(e)}"
            )

if __name__ == "__main__":
    print("""
            ███████╗ ████████╗████████╗ ██████╗ ████████╗
            ██╔═══██╗   ██║   ██╔════╝ ██╔══██╗    ██║   
            ██║   ██║   ██║   ██║      ███████║    ██║   
            ██║   ██║   ██║   ██║      ██╔══██║    ██║   
            ██║   ██║   ██║   ██║      ██║  ██║    ██║   
            ███████║ ████████║████████║╚═╝  ╚═╝ ████████║ v1.05
            </Alek>          
              """)  
    check_config()
    app = AutomationApp()
    app.root.mainloop()