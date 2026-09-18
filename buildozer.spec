[app]
title = PocketScanner
package.name = pocketscanner
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy,opencv-python,numpy
orientation = portrait
osx.kivy_version = 2.2.1
fullscreen = 0
android.permissions = CAMERA,INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
