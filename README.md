# Dados de D&D — Python + Kivy

Aplicación táctil de dados para Android. La lógica de tiradas está separada de la interfaz y se prueba con `pytest`.

## Funciones incluidas

- Dados habituales y personalizados: `d4`, `d6`, `d8`, `d10`, `d12`, `d20`, `d100` y expresiones como `3d17+2`.
- Selector por botones para la cantidad de dados (de 1 a 100) y modificador positivo o negativo.
- La expresión de la tirada se muestra en un campo informativo de solo lectura.
- Animación breve de lanzamiento antes de mostrar cada resultado.
- Varias tiradas y visualización de los resultados individuales.
- Ventaja y desventaja para una única tirada de d20.
- Opción de conservar los tres resultados más altos o más bajos al tirar cuatro o más dados.
- Historial en memoria durante la sesión; no se conserva al cerrar la app.
- Validación de expresiones sin `eval()`.

## 1. Trabajar dentro del sistema de archivos de WSL

Conviene tener el proyecto en el sistema de archivos Linux, por ejemplo `~/dados`, no bajo `/mnt/c`, porque la compilación de Android es más fiable y rápida desde el sistema de archivos de WSL.

Comprueba la ubicación:

```bash
cd ~/dados
pwd
ls -la
```

Si tu carpeta `dados` está en otra ubicación, usa esa ruta en lugar de `~/dados`.

## 2. Dependencias de sistema

Comprueba tu versión de Ubuntu:

```bash
lsb_release -a
python3 --version
```

Instala las herramientas de sistema que requiere Buildozer (los nombres de paquetes pueden variar según la versión de Ubuntu):

```bash
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip python3-venv \
  autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev \
  cmake libffi-dev libssl-dev automake
```

Si `apt` informa de que un paquete no existe, no sustituyas nombres al azar: consulta las instrucciones oficiales de Buildozer para tu versión exacta de Ubuntu.

## 3. Crear y activar el entorno virtual

Desde la carpeta del proyecto:

```bash
cd ~/dados
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
```

Al activarse, normalmente aparece `(.venv)` al principio del prompt. Comprueba que Python y pip pertenecen al entorno:

```bash
which python
python --version
python -m pip --version
```

La ruta de Python debe terminar en `dados/.venv/bin/python`.

Instala las dependencias de desarrollo:

```bash
python -m pip install -r requirements-dev.txt
```

Instala Buildozer en este mismo entorno virtual para mantenerlo aislado:

```bash
python -m pip install buildozer
buildozer --version
```

No uses `sudo pip`. `apt` gestiona las dependencias de sistema; `pip` instala paquetes Python dentro de `.venv`.

## 4. Ejecutar las pruebas

No hace falta abrir la interfaz ni conectar el teléfono para probar la lógica:

```bash
python -m pytest -v
```

Las pruebas deben terminar sin fallos. Si alguna falla, no continúes a la compilación: primero corrige el problema y vuelve a ejecutar el comando.

## 5. Ejecutar la interfaz en Ubuntu

```bash
python main.py
```

Esto requiere que la interfaz gráfica de WSLg funcione en tu instalación de WSL. Si aparece un error de OpenGL o de ventana, guarda el mensaje completo; no instales paquetes al azar.

## 6. Preparar y compilar el APK

El archivo `buildozer.spec` ya está incluido. La primera compilación descargará componentes grandes del SDK/NDK de Android y puede tardar bastante.

```bash
buildozer -v android debug
```

El APK de depuración debería aparecer dentro de `bin/`. No se debe considerar correcto hasta que la compilación termine con código de salida cero y se instale y pruebe en Android.

Para instalarlo con un teléfono conectado por ADB y con depuración USB habilitada, consulta primero:

```bash
buildozer android --help
```

Después puedes usar `buildozer android debug deploy run` si la conexión ADB está configurada correctamente.

## 7. Uso diario del entorno virtual

Cada vez que abras una terminal nueva:

```bash
cd ~/dados
source .venv/bin/activate
```

Al terminar:

```bash
deactivate
```

Para comprobar qué paquetes están instalados:

```bash
python -m pip list
python -m pip check
```

Para repetir las pruebas:

```bash
python -m pytest -v
```

No borres `.venv` para actualizar la aplicación. El código fuente y el entorno virtual son cosas distintas. Si el entorno se estropea, puede recrearse a partir de los archivos de requisitos.

## Estructura

```text
dados/
├── main.py                 # Interfaz Kivy
├── dice_logic.py           # Lógica pura de dados, sin interfaz
├── requirements-dev.txt    # Dependencias de desarrollo y pruebas
├── buildozer.spec          # Configuración del APK Android
├── .gitignore
├── README.md
└── tests/
    └── test_dice_logic.py  # Pruebas automatizadas
```

## Alcance y limitaciones

- La aplicación usa una interfaz sencilla para priorizar fiabilidad y facilidad de uso.
- `3 mayores` y `3 menores` siguen la regla de conservar tres dados solo cuando se tiran cuatro o más; con menos dados se conservan todos.
- Ventaja y desventaja están limitadas a una tirada de un d20.
- El historial no se guarda después de cerrar la aplicación.
- Las pruebas automatizadas cubren la lógica de dados, no sustituyen las pruebas manuales del APK en dispositivos Android distintos.
- Antes de publicar en una tienda, revisa la versión de Android objetivo, firma, icono, nombre de paquete y requisitos de la tienda.
