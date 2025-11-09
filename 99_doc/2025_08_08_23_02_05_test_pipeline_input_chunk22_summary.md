# Chunk 22 Summary

Why the original .txt remains in watch_folder
It should be moved here:

Path(config["processed_folder"]).mkdir(parents=True, exist_ok=True)
processed_dest = Path(config["processed_folder"]) / filepath.name
shutil.move(str(filepath), processed_dest)
So if your watch_folder still has the file:

The move silently failed (locked file?). The script terminated mid-way. You might be viewing a copy of the original elsewhere (check timestamp).
