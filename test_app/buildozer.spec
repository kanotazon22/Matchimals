[buildozer]
log_level = 2

[app]
title = Matchimals
package.name = matchimals
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,mp3,ogg,wav
source.include_dirs = assets
include_patterns = assets/**/*

version = 0.1
requirements = python3==3.10.11,kivy==2.2.1,sdl2,mixer
orientation = portrait
fullscreen = 1
android.permissions = INTERNET
icon.filename = icon.png  # ← Dòng này là mới thêm

osx.kivy_version = 2.2.1
android.api = 31
android.minapi = 21
android.ndk = 25b
