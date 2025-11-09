import os

# Prevent accidental collection outside the tests tree
collect_ignore_glob = []

legacy_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "99_doc"))
if os.path.isdir(legacy_dir):
    collect_ignore_glob.append("../99_doc")

