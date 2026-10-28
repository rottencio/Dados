[app]

title = Dados de D&D
package.name = dadosdnd
package.domain = org.example
source.dir = .
source.include_exts = py,kv,png,jpg,atlas
source.exclude_dirs = .venv,tests,__pycache__,.pytest_cache,.git
version = 1.0.0

# Mantener los requisitos de Android mínimos y explícitos.
requirements = python3,kivy==2.3.1
orientation = portrait
fullscreen = 0

# No se solicitan permisos de Android: esta app no necesita red ni archivos externos.
android.permissions =
android.api = 35
android.minapi = 24
android.archs = arm64-v8a
android.accept_sdk_license = True

[buildozer]

log_level = 2
warn_on_root = 1

p4a.branch = develop
p4a.commit = 9a7694e
