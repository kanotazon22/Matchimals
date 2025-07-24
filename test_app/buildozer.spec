[app]
title = Matchimals
package.name = matchimals
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,ogg
source.include_dirs = assets
include_patterns = assets/fonts/*.ttf,assets/images/*.png,assets/low-quality/*.png,assets/high-quality/*.png,assets/sound/*.ogg

version = 0.1
requirements = python3==3.10.11,kivy==2.2.1,sdl2,mixer
orientation = portrait
fullscreen = 1
android.permissions = INTERNET

osx.kivy_version = 2.2.1
android.api = 31
android.minapi = 21
android.ndk = 25b
