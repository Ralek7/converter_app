DICAI v1.05 - Documentación
============================================

Herramienta para extraer casos de prueba de ValueEdge y issues de JIRA, y convertirlos a scripts Gherkin automatizados.

=== REQUISITOS PREVIOS ===
- Python 3.10+ instalado
- Cuentas activas en:
  * ValueEdge (credenciales API)
  * JIRA Cloud (API Token)
- Acceso a los proyectos destino

=== CONFIGURACIÓN INICIAL ===

1. Crear archivo secrets/secrets.ini con esta estructura:

[ValueEdge]
URL = https://tu-instancia.valueedge.com
SHARED_SPACE = XXXX
WORKSPACE = DEFAULT
TECH_PREVIEW_FLAG = true
USER = tu_usuario
PASSWORD = tu_contraseña

[JIRA]
URL = https://tu-empresa.atlassian.net
EMAIL = usuario@empresa.com
API_TOKEN = tu_api_token_de_jira

=== EJECUCIÓN DESDE CÓDIGO ===

1. Instalar dependencias:
pip install -r requirements.txt

2. Ejecutar programa:
python main.py

* Menú principal ofrece:
- Extracción de ValueEdge:
  * Todos los casos de prueba (guarda en output/test_cases)
  * Casos específicos por ID
- Extracción de JIRA:
  * Todos los issues de un proyecto (guarda en output/jira_issues)
  * Issues individuales
- Conversión automática a Gherkin (output/features)

=== GENERAR EJECUTABLE ===

1. Instalar PyInstaller:
pip install pyinstaller

2. Crear build:
a)pyinstaller --onefile --windowed --icon=assets/icon.ico main.py
b)pyinstaller --onefile --clean --noupx --runtime-tmpdir=. --name DICAI --add-data "secrets/secrets.ini;secrets" --add-data "core/*.py;core" --add-data "output/jira_issues;output/jira_issues" --hidden-import=configparser --hidden-import=requests --hidden-import=urllib3 --hidden-import=tkinter --hidden-import=logging --hidden-import=pathlib --paths=".core" main.py

3. Ejecutable generado en carpeta dist/

=== ESTRUCTURA DE CARPETAS ===

/secretos
  secrets.ini
/output
  /features
  /jira_issues
  /test_cases
/assets
  icon.ico

=== SOLUCIÓN DE PROBLEMAS ===

ERRORES DE AUTENTICACIÓN:
- Verificar formato del secrets.ini
- Confirmar API Token de JIRA activo
- Validar permisos en ValueEdge

ERRORES DE CONEXIÓN:
- Verificar firewall/acceso a URLs
- Probar en red diferente si hay bloqueos

PROYECTOS NO ENCONTRADOS:
- Confirmar Workspace ID en ValueEdge
- Usar formato correcto para IDs:
  * ValueEdge: numérico (ej: 1001)
  * JIRA: Proyecto-Numero (ej: BT115-123)

=== NOTAS IMPORTANTES ===
- Los archivos generados se SOBRESCRIBEN en cada ejecución
- Mantener estructura de carpetas original
- Usar Python 3.10+ para evitar errores
- Reportar errores con captura de pantalla del mensaje

=== LICENCIA ===
LICENCIA DE AUTOR RESTRINGIDA (LAR) v1.0 - Ver archivo LICENSE incluido