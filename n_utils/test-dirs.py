from __future__ import print_function
try:
    from os import scandir, walk
except ImportError:
    from scandir import scandir, walk

for direntry in scandir("."):
    if direntry.is_dir() and not direntry.name.startswith("."):
        print(direntry.name)