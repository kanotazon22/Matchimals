[buildozer]
log_level = 2
source.main = label27

[app]
title = Matchimals
package.name = matchimals
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,mp3,ogg,wav
source.include_dirs = assets

version = 0.1
requirements = python3==3.10,kivy==2.2.1,sdl2,mixer
orientation = portrait

osx.kivy_version = 2.2.1
fullscreen = 1
android.permissions = INTERNET
