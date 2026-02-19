[app]

# (str) Title of your application
title = Mom's Happy Birthday

# (str) Package name
package.name = mombirthday

# (str) Package domain (uniquely identifies the app)
package.domain = org.hao26650824

# (source.dir) Source code directory
source.dir = .

# (source.include_exts) Source files to include
source.include_exts = py,png,jpg,kv,atlas,txt

# (version) Application version
version = 1.0

# (list) Application requirements
requirements = python3,kivy

# (string) Supported orientations
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# iOS specific settings
ios.requirements = python3,kivy
ios.codesign.allowed = false

[buildozer]

# (int) Log level
log_level = 2

# (int) Display warnings
warn_on_root = 1
