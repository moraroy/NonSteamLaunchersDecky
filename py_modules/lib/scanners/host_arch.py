import os
import platform

# Decky's loader is x86_64 under FEX on arm64 hosts, so platform.machine() reports
# x86_64 there; the host's aarch64 dynamic loader is still visible.
IS_ARM64 = platform.machine() == "aarch64" or os.path.exists("/lib/ld-linux-aarch64.so.1")

# Arch for `flatpak run --arch=...`; Edge has no aarch64 build and keeps x86_64 (FEX)
FLATPAK_ARCH = "aarch64" if IS_ARM64 else "x86_64"
