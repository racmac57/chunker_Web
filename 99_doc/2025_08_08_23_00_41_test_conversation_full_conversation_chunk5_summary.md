# Chunk 5 Summary

https://aka.ms/PSWindows

PS C:\Users\carucci_r> cd C:\Users\carucci_r\Documents\chunker
PS C:\Users\carucci_r\Documents\chunker> .\test_chunker.ps1 -MonitorOnly
At C:\Users\carucci_r\Documents\chunker\test_chunker.ps1:32 char:64
+ ... te-Host "nðŸ“ Test file created: $testFile ($fileSize bytes)" -Fore ...
+                                                             ~~~~~
Unexpected token 'bytes' in expression or statement. At C:\Users\carucci_r\Documents\chunker\test_chunker.ps1:32 char:63
+ ...    Write-Host "nðŸ“ Test file created: $testFile ($fileSize bytes)" ...
+                                                                  ~
Missing closing ')' in expression. At C:\Users\carucci_r\Documents\chunker\test_chunker.ps1:19 char:23
+ function New-TestFile {
+                       ~
Missing closing '}' in statement block or type definition.
