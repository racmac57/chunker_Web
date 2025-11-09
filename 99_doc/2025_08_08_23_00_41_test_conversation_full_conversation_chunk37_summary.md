# Chunk 37 Summary

Please use the NLTK Downloader to obtain the resource:

  [31m>>> import nltk
  >>> nltk.download('punkt_tab')
  [0m
  For more information see: https://www.nltk.org/data.html

  Attempted to load [93mtokenizers/punkt_tab/english/[0m

  Searched in:
    - 'C:\\Users\\carucci_r/nltk_data'
    - 'C:\\Users\\carucci_r\\AppData\\Local\\Programs\\Python\\Python312\\nltk_data'
    - 'C:\\Users\\carucci_r\\AppData\\Local\\Programs\\Python\\Python312\\share\\nltk_data'
    - 'C:\\Users\\carucci_r\\AppData\\Local\\Programs\\Python\\Python312\\lib\\nltk_data'
    - 'C:\\Users\\carucci_r\\AppData\\Roaming\\nltk_data'
    - 'C:\\nltk_data'
    - 'D:\\nltk_data'
    - 'E:\\nltk_data'
    - 'C:\\Users\\carucci_r\\Documents\\chunker\\nltk_data'
**********************************************************************

2025-06-27 18:40:46,963 [INFO] Detected new file: outreach table.txt
2025-06-27 18:40:49,263 [ERROR] Unhandled error in watcher loop
Traceback (most recent call last):
  File "C:\Users\carucci_r\Documents\chunker\watcher_splitter.py", line 134, in main
    if process_file(file_path, CONFIG):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\carucci_r\Documents\chunker\watcher_splitter.py", line 91, in process_file
    chunks = chunk_text(text, sentence_limit)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\carucci_r\Documents\chunker\watcher_splitter.py", line 35, in chunk_text
    sentences = sent_tokenize(text)
                ^^^^^^^^^^^^^^^^^^^
  File "C:\Users\carucci_r\AppData\Local\Programs\Python\Python312\Lib\site-packages\nltk\tokenize\__init__.py", line 119, in sent_tokenize
    tokenizer = _get_punkt_tokenizer(language)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\carucci_r\AppData\Local\Programs\Python\Python312\Lib\site-packages\nltk\tokenize\__init__.py", line 105, in _get_punkt_tokenizer
    return PunktTokenizer(language)
           ^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\carucci_r\AppData\Local\Programs\Python\Python312\Lib\site-packages\nltk\tokenize\punkt.py", line 1744, in __init__
    self.load_lang(lang)
  File "C:\Users\carucci_r\AppData\Local\Programs\Python\Python312\Lib\site-packages\nltk\tokenize\punkt.py", line 1749, in load_lang
    lang_dir = find(f"tokenizers/punkt_tab/{lang}/")
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\carucci_r\AppData\Local\Programs\Python\Python312\Lib\site-packages\nltk\data.py", line 579, in find
    raise LookupError(resource_not_found)
LookupError: 
**********************************************************************
  Resource [93mpunkt_tab[0m not found. Please use the NLTK Downloader to obtain the resource:

  [31m>>> import nltk
  >>> nltk.download('punkt_tab')
  [0m
  For more information see: https://www.nltk.org/data.html

  Attempted to load [93mtokenizers/punkt_tab/english/[0m

  Searched in:
    - 'C:\\Users\\carucci_r/nltk_data'
    - 'C:\\Users\\carucci_r\\AppData\\Local\\Programs\\Python\\Python312\\nltk_data'
    - 'C:\\Users\\carucci_r\\AppData\\Local\\Programs\\Python\\Python312\\share\\nltk_data'
    - 'C:\\Users\\carucci_r\\AppData\\Local\\Programs\\Python\\Python312\\lib\\nltk_data'
    - 'C:\\Users\\carucci_r\\AppData\\Roaming\\nltk_data'
    - 'C:\\nltk_data'
    - 'D:\\nltk_data'
    - 'E:\\nltk_data'
    - 'C:\\Users\\carucci_r\\Documents\\chunker\\nltk_data'
**********************************************************************

2025-06-27 18:40:49,264 [INFO] Detected new file: outreach table.txt
2025-06-27 18:40:51,501 [ERROR] Unhandled error in watcher loop
Traceback (most recent call last):
  File "C:\Users\carucci_r\Documents\chunker\watcher_splitter.py", line 134, in main
    if process_file(file_path, CONFIG):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\carucci_r\Documents\chunker\watcher_splitter.py", line 91, in process_file
    chunks = chunk_text(text, sentence_limit)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\carucci_r\Documents\chunker\watcher_splitter.py", line 35, in chunk_text
    sentences = sent_tokenize(text)
                ^^^^^^^^^^^^^^^^^^^
  File "C:\Users\carucci_r\AppData\Local\Programs\Python\Python312\Lib\site-packages\nltk\tokenize\__init__.py", line 119, in sent_tokenize
    tokenizer = _get_punkt_tokenizer(language)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\carucci_r\AppData\Local\Programs\Python\Python312\Lib\site-packages\nltk\tokenize\__init__.py", line 105, in _get_punkt_tokenizer
    return PunktTokenizer(language)
           ^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\carucci_r\AppData\Local\Programs\Python\Python312\Lib\site-packages\nltk\tokenize\punkt.py", line 1744, in __init__
    self.load_lang(lang)
  File "C:\Users\carucci_r\AppData\Local\Programs\Python\Python312\Lib\site-packages\nltk\tokenize\punkt.py", line 1749, in load_lang
    lang_dir = find(f"tokenizers/punkt_tab/{lang}/")
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\carucci_r\AppData\Local\Programs\Python\Python312\Lib\site-packages\nltk\data.py", line 579, in find
    raise LookupError(resource_not_found)
LookupError: 
**********************************************************************
  Resource [93mpunkt_tab[0m not found. Please use the NLTK Downloader to obtain the resource:

  [31m>>> import nltk
  >>> nltk.download('punkt_tab')
  [0m
  For more information see: https://www.nltk.org/data.html

  Attempted to load [93mtokenizers/punkt_tab/english/[0m

  Searched in:
    - 'C:\\Users\\carucci_r/nltk_data'
    - 'C:\\Users\\carucci_r\\AppData\\Local\\Programs\\Python\\Python312\\nltk_data'
    - 'C:\\Users\\carucci_r\\AppData\\Local\\Programs\\Python\\Python312\\share\\nltk_data'
    - 'C:\\Users\\carucci_r\\AppData\\Local\\Programs\\Python\\Python312\\lib\\nltk_data'
    - 'C:\\Users\\carucci_r\\AppData\\Roaming\\nltk_data'
    - 'C:\\nltk_data'
    - 'D:\\nltk_data'
    - 'E:\\nltk_data'
    - 'C:\\Users\\carucci_r\\Documents\\chunker\\nltk_data'
**********************************************************************

2025-06-27 18:40:51,502 [INFO] Detected new file: outreach table.txt
2025-06-27 18:40:53,710 [ERROR] Unhandled error in watcher loop
Traceback (most recent call last):
  File "C:\Users\carucci_r\Documents\chunker\watcher_splitter.py", line 134, in main
    if process_file(file_path, CONFIG):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\carucci_r\Documents\chunker\watcher_splitter.py", line 91, in process_file
    chunks = chunk_text(text, sentence_limit)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\carucci_r\Documents\chunker\watcher_splitter.py", line 35, in chunk_text
    sentences = sent_tokenize(text)
                ^^^^^^^^^^^^^^^^^^^
  File "C:\Users\carucci_r\AppData\Local\Programs\Python\Python312\Lib\site-packages\nltk\tokenize\__init__.py", line 119, in sent_tokenize
    tokenizer = _get_punkt_tokenizer(language)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\carucci_r\AppData\Local\Programs\Python\Python312\Lib\site-packages\nltk\tokenize\__init__.py", line 105, in _get_punkt_tokenizer
    return PunktTokenizer(language)
           ^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\carucci_r\AppData\Local\Programs\Python\Python312\Lib\site-packages\nltk\tokenize\punkt.py", line 1744, in __init__
    self.load_lang(lang)
  File "C:\Users\carucci_r\AppData\Local\Programs\Python\Python312\Lib\site-packages\nltk\tokenize\punkt.py", line 1749, in load_lang
    lang_dir = find(f"tokenizers/punkt_tab/{lang}/")
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\carucci_r\AppData\Local\Programs\Python\Python312\Lib\site-packages\nltk\data.py", line 579, in find
    raise LookupError(resource_not_found)
LookupError: 
**********************************************************************
  Resource [93mpunkt_tab[0m not found.
