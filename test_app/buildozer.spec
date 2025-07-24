[buildozer]
log_level = 2
warn_on_root = 1
# Bỏ qua update Python-for-Android mỗi lần build (giảm thời gian)
android.skip_update = true

[app]
title = Matchimals
package.name = matchimals
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,mp3,ogg,wav
source.include_dirs = assets
include_patterns = assets/**/*.png, assets/**/*.jpg, assets/**/*.ogg, assets/**/*.ttf
exclude_patterns = *.pyc, __pycache__

version = 0.1
# Giữ requirements tối giản để giảm thời gian compile
requirements = python3,kivy,sdl2,ffpyplayer
orientation = portrait
fullscreen = 1

android.permissions = INTERNET,VIBRATE
android.hardwareAccelerated = true
android.private_storage = true

# Build dạng debug để nhanh hơn (không sign, không optimize)
android.release = 0
# Bỏ bước compile lại file py nếu không thay đổi
android.skip_compile = true

# Cố định phiên bản API và NDK để không bị tải lại
android.api = 31
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21

osx.kivy_version = 2.2.1
