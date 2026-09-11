[app]

title = Ratbuster World Tour
package.name = ratbuster
package.domain = org.ratbuster

source.dir = .
source.include_exts = py,png,wav,jpg,kv,atlas

# ship the procedurally-generated art/sound folders
source.include_patterns = assets/images/*.png,assets/sounds/*.wav

version = 1.0.0
requirements = python3,kivy

icon.filename = %(source.dir)s/assets/images/icon.png
presplash.filename = %(source.dir)s/assets/images/presplash.png

orientation = landscape
fullscreen = 1

# Minimum Android version supported. Target API / NDK are left at
# Buildozer's own current defaults (commented out below) rather than
# pinned here, so the build doesn't break as those defaults advance.
android.minapi = 21
#android.api =
#android.ndk =
android.archs = arm64-v8a, armeabi-v7a

# Needed so `buildozer android debug` runs non-interactively in CI.
android.accept_sdk_license = True
android.allow_backup = True

# No special permissions needed: progress is saved to the app's private
# data directory via Kivy's JsonStore, and the game makes no network calls.
android.permissions =

[buildozer]
log_level = 2
warn_on_root = 1
