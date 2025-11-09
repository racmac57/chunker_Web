# Chunk 2 Summary

C:\Users\carucci_r>cd C:\Users\carucci_r\Documents\chunker

C:\Users\carucci_r\Documents\chunker>powershell "Get-Content logs\watcher.log -Tail 20"
2025-06-27 21:58:18,021 [WARNING] File 2025_06_25_20_11_19_chatgpt_cad_rns_code_01a.txt not found, waiting...
2025-06-27 21:58:20,022 [WARNING] File 2025_06_25_20_11_19_chatgpt_cad_rns_code_01a.txt not found, waiting...
2025-06-27 21:58:22,023 [WARNING] File 2025_06_25_20_11_19_chatgpt_cad_rns_code_01a.txt not found, waiting...
2025-06-27 21:58:24,025 [WARNING] File 2025_06_25_20_11_19_chatgpt_cad_rns_code_01a.txt not found, waiting...
2025-06-27 21:58:26,026 [WARNING] File 2025_06_25_20_11_19_chatgpt_cad_rns_code_01a.txt not found, waiting...
2025-06-27 21:58:28,027 [WARNING] File 2025_06_25_20_11_19_chatgpt_cad_rns_code_01a.txt not found, waiting...
2025-06-27 21:58:30,028 [WARNING] File 2025_06_25_20_11_19_chatgpt_cad_rns_code_01a.txt not found, waiting...
2025-06-27 21:58:32,029 [WARNING] File 2025_06_25_20_11_19_chatgpt_cad_rns_code_01a.txt not found, waiting...
2025-06-27 21:58:34,030 [WARNING] File 2025_06_25_20_11_19_chatgpt_cad_rns_code_01a.txt not found, waiting...
2025-06-27 21:58:36,031 [WARNING] File 2025_06_25_20_11_19_chatgpt_cad_rns_code_01a.txt not found, waiting...
2025-06-27 21:58:38,032 [WARNING] File 2025_06_25_20_11_19_chatgpt_cad_rns_code_01a.txt not found, waiting...
2025-06-27 21:58:40,033 [WARNING] File 2025_06_25_20_11_19_chatgpt_cad_rns_code_01a.txt not found, waiting...
2025-06-27 21:58:42,034 [WARNING] File 2025_06_25_20_11_19_chatgpt_cad_rns_code_01a.txt not found, waiting...
2025-06-27 21:58:44,035 [WARNING] File 2025_06_25_20_11_19_chatgpt_cad_rns_code_01a.txt not found, waiting...
2025-06-27 21:58:46,036 [WARNING] File 2025_06_25_20_11_19_chatgpt_cad_rns_code_01a.txt not found, waiting...
2025-06-27 21:58:48,043 [WARNING] File 2025_06_25_20_11_19_chatgpt_cad_rns_code_01a.txt not found, waiting...
2025-06-27 21:58:50,044 [WARNING] File 2025_06_25_20_11_19_chatgpt_cad_rns_code_01a.txt not found, waiting...
2025-06-27 21:58:52,045 [WARNING] File 2025_06_25_20_11_19_chatgpt_cad_rns_code_01a.txt did not stabilize after 30 seconds
2025-06-27 21:58:52,045 [ERROR] File 2025_06_25_20_11_19_chatgpt_cad_rns_code_01a.txt did not stabilize - skipping
2025-06-27 21:58:52,045 [WARNING] \u26a0\ufe0f Processing completed with issues: 2025_06_25_20_11_19_chatgpt_cad_rns_code_01a.txt

C:\Users\carucci_r\Documents\chunker>dir output /o:d | findstr "06/27/25"
06/27/25  12:39            45,141 2025_06_27_12_39_53_Summons_MVA_part_1.txt
06/27/25  12:39            34,793 2025_06_27_12_39_53_Summons_MVA_part_2.txt
06/27/25  12:39            36,158 2025_06_27_12_39_53_Summons_MVA_part_3.txt
06/27/25  12:39            45,141 2025_06_27_12_39_53_Prompt_Builder_Python_Power_Query_Project_Summons_MVA_part_1.txt
06/27/25  12:39            36,526 2025_06_27_12_39_53_Summons_MVA_part_4.txt
06/27/25  12:39            34,793 2025_06_27_12_39_53_Prompt_Builder_Python_Power_Query_Project_Summons_MVA_part_2.txt
06/27/25  12:39            33,448 2025_06_27_12_39_53_Summons_MVA_part_5.txt
06/27/25  12:39            31,491 2025_06_27_12_39_53_Summons_MVA_part_6.txt
06/27/25  12:39            36,158 2025_06_27_12_39_53_Prompt_Builder_Python_Power_Query_Project_Summons_MVA_part_3.txt
06/27/25  12:39            34,792 2025_06_27_12_39_53_Summons_MVA_part_7.txt
06/27/25  12:39            36,526 2025_06_27_12_39_53_Prompt_Builder_Python_Power_Query_Project_Summons_MVA_part_4.txt
06/27/25  12:39            33,554 2025_06_27_12_39_53_Summons_MVA_part_8.txt
06/27/25  12:39             6,033 2025_06_27_12_39_53_Summons_MVA_part_9.txt
06/27/25  12:39            33,448 2025_06_27_12_39_53_Prompt_Builder_Python_Power_Query_Project_Summons_MVA_part_5.txt
06/27/25  12:39            31,491 2025_06_27_12_39_53_Prompt_Builder_Python_Power_Query_Project_Summons_MVA_part_6.txt
06/27/25  12:39            34,792 2025_06_27_12_39_53_Prompt_Builder_Python_Power_Query_Project_Summons_MVA_part_7.txt
06/27/25  12:39            33,554 2025_06_27_12_39_53_Prompt_Builder_Python_Power_Query_Project_Summons_MVA_part_8.txt
06/27/25  12:39             6,033 2025_06_27_12_39_53_Prompt_Builder_Python_Power_Query_Project_Summons_MVA_part_9.txt
06/27/25  12:39           291,936 full_conversation.txt
06/27/25  12:39               116 summary.md
06/27/25  12:39           291,936 2025_06_27_12_39_53_Prompt_Builder_Python_Power_Query_Project_Summons_MVA_full_conversation.txt
06/27/25  21:49               165 2025_06_27_21_49_01_working_test_chunk1.txt
06/27/25  21:55                 0 2025_06_27_21_55_26_2025_06_27_17_08_32_policy_train_01_chunk1.txt
06/27/25  21:55                 0 2025_06_27_21_55_26_2025_06_27_17_08_32_policy_train_01_chunk2.txt
06/27/25  21:55                 0 2025_06_27_21_55_26_2025_06_27_17_08_32_policy_train_01_chunk3.txt
06/27/25  21:55                 0 2025_06_27_21_55_26_2025_06_27_17_08_32_policy_train_01_chunk4.txt
06/27/25  21:55                 0 2025_06_27_21_55_26_2025_06_27_17_08_32_policy_train_01_chunk5.txt
06/27/25  21:55                 0 2025_06_27_21_55_26_2025_06_27_17_08_32_policy_train_01_chunk6.txt
06/27/25  21:55                 0 2025_06_27_21_55_26_2025_06_27_17_08_32_policy_train_01_chunk7.txt
06/27/25  21:55                 0 2025_06_27_21_55_26_2025_06_27_17_08_32_policy_train_01_chunk8.txt
06/27/25  21:55                 0 2025_06_27_21_55_26_2025_06_27_17_08_32_policy_train_01_chunk9.txt
06/27/25  21:55                 0 2025_06_27_21_55_26_2025_06_27_17_08_32_policy_train_01_chunk10.txt
06/27/25  21:55                 0 2025_06_27_21_55_26_2025_06_27_17_08_32_policy_train_01_chunk11.txt
06/27/25  21:57            22,716 2025_06_27_21_57_53_2025_06_25_20_11_19_chatgpt_cad_rns_code_01a_chunk1.txt
06/27/25  21:57            34,351 2025_06_27_21_57_53_2025_06_25_20_11_19_chatgpt_cad_rns_code_01a_chunk2.txt
06/27/25  21:57            60,245 2025_06_27_21_57_53_2025_06_25_20_11_19_chatgpt_cad_rns_code_01a_chunk3.txt
06/27/25  21:57            30,922 2025_06_27_21_57_53_2025_06_25_20_11_19_chatgpt_cad_rns_code_01a_chunk4.txt
06/27/25  21:57            28,915 2025_06_27_21_57_53_2025_06_25_20_11_19_chatgpt_cad_rns_code_01a_chunk5.txt
06/27/25  21:57            26,061 2025_06_27_21_57_53_2025_06_25_20_11_19_chatgpt_cad_rns_code_01a_chunk6.txt
06/27/25  21:57            39,155 2025_06_27_21_57_53_2025_06_25_20_11_19_chatgpt_cad_rns_code_01a_chunk7.txt
06/27/25  21:57            35,147 2025_06_27_21_57_53_2025_06_25_20_11_19_chatgpt_cad_rns_code_01a_chunk8.txt
06/27/25  21:57            40,129 2025_06_27_21_57_53_2025_06_25_20_11_19_chatgpt_cad_rns_code_01a_chunk9.txt
06/27/25  21:57            26,268 2025_06_27_21_57_53_2025_06_25_20_11_19_chatgpt_cad_rns_code_01a_chunk10.txt
06/27/25  21:57            38,514 2025_06_27_21_57_53_2025_06_25_20_11_19_chatgpt_cad_rns_code_01a_chunk11.txt
06/27/25  21:57            38,635 2025_06_27_21_57_53_2025_06_25_20_11_19_chatgpt_cad_rns_code_01a_chunk12.txt
06/27/25  21:57            23,796 2025_06_27_21_57_53_2025_06_25_20_11_19_chatgpt_cad_rns_code_01a_chunk13.txt
06/27/25  21:57            43,468 2025_06_27_21_57_53_2025_06_25_20_11_19_chatgpt_cad_rns_code_01a_chunk14.txt
06/27/25  21:57    <DIR>          . 06/27/25  21:57            31,628 2025_06_27_21_57_53_2025_06_25_20_11_19_chatgpt_cad_rns_code_01a_chunk15.txt
06/27/25  22:03    <DIR>          ..

C:\Users\carucci_r\Documents\chunker>dir output\*.txt | findstr " 0 "
06/27/25  12:39           291,936 2025_06_27_12_39_53_Prompt_Builder_Python_Power_Query_Project_Summons_MVA_full_conversation.txt
06/27/25  12:39            45,141 2025_06_27_12_39_53_Prompt_Builder_Python_Power_Query_Project_Summons_MVA_part_1.txt
06/27/25  12:39            34,793 2025_06_27_12_39_53_Prompt_Builder_Python_Power_Query_Project_Summons_MVA_part_2.txt
06/27/25  12:39            36,158 2025_06_27_12_39_53_Prompt_Builder_Python_Power_Query_Project_Summons_MVA_part_3.txt
06/27/25  12:39            36,526 2025_06_27_12_39_53_Prompt_Builder_Python_Power_Query_Project_Summons_MVA_part_4.txt
06/27/25  12:39            33,448 2025_06_27_12_39_53_Prompt_Builder_Python_Power_Query_Project_Summons_MVA_part_5.txt
06/27/25  12:39            31,491 2025_06_27_12_39_53_Prompt_Builder_Python_Power_Query_Project_Summons_MVA_part_6.txt
06/27/25  12:39            34,792 2025_06_27_12_39_53_Prompt_Builder_Python_Power_Query_Project_Summons_MVA_part_7.txt
06/27/25  12:39            33,554 2025_06_27_12_39_53_Prompt_Builder_Python_Power_Query_Project_Summons_MVA_part_8.txt
06/27/25  12:39             6,033 2025_06_27_12_39_53_Prompt_Builder_Python_Power_Query_Project_Summons_MVA_part_9.txt
06/27/25  12:39            45,141 2025_06_27_12_39_53_Summons_MVA_part_1.txt
06/27/25  12:39            34,793 2025_06_27_12_39_53_Summons_MVA_part_2.txt
06/27/25  12:39            36,158 2025_06_27_12_39_53_Summons_MVA_part_3.txt
06/27/25  12:39            36,526 2025_06_27_12_39_53_Summons_MVA_part_4.txt
06/27/25  12:39            33,448 2025_06_27_12_39_53_Summons_MVA_part_5.txt
06/27/25  12:39            31,491 2025_06_27_12_39_53_Summons_MVA_part_6.txt
06/27/25  12:39            34,792 2025_06_27_12_39_53_Summons_MVA_part_7.txt
06/27/25  12:39            33,554 2025_06_27_12_39_53_Summons_MVA_part_8.txt
06/27/25  12:39             6,033 2025_06_27_12_39_53_Summons_MVA_part_9.txt
06/27/25  21:49               165 2025_06_27_21_49_01_working_test_chunk1.txt
06/27/25  21:55                 0 2025_06_27_21_55_26_2025_06_27_17_08_32_policy_train_01_chunk1.txt
06/27/25  21:55                 0 2025_06_27_21_55_26_2025_06_27_17_08_32_policy_train_01_chunk10.txt
06/27/25  21:55                 0 2025_06_27_21_55_26_2025_06_27_17_08_32_policy_train_01_chunk11.txt
06/27/25  21:55                 0 2025_06_27_21_55_26_2025_06_27_17_08_32_policy_train_01_chunk2.txt
06/27/25  21:55                 0 2025_06_27_21_55_26_2025_06_27_17_08_32_policy_train_01_chunk3.txt
06/27/25  21:55                 0 2025_06_27_21_55_26_2025_06_27_17_08_32_policy_train_01_chunk4.txt
06/27/25  21:55                 0 2025_06_27_21_55_26_2025_06_27_17_08_32_policy_train_01_chunk5.txt
06/27/25  21:55                 0 2025_06_27_21_55_26_2025_06_27_17_08_32_policy_train_01_chunk6.txt
06/27/25  21:55                 0 2025_06_27_21_55_26_2025_06_27_17_08_32_policy_train_01_chunk7.txt
06/27/25  21:55                 0 2025_06_27_21_55_26_2025_06_27_17_08_32_policy_train_01_chunk8.txt
06/27/25  21:55                 0 2025_06_27_21_55_26_2025_06_27_17_08_32_policy_train_01_chunk9.txt
06/27/25  21:57            22,716 2025_06_27_21_57_53_2025_06_25_20_11_19_chatgpt_cad_rns_code_01a_chunk1.txt
06/27/25  21:57            26,268 2025_06_27_21_57_53_2025_06_25_20_11_19_chatgpt_cad_rns_code_01a_chunk10.txt
06/27/25  21:57            38,514 2025_06_27_21_57_53_2025_06_25_20_11_19_chatgpt_cad_rns_code_01a_chunk11.txt
06/27/25  21:57            38,635 2025_06_27_21_57_53_2025_06_25_20_11_19_chatgpt_cad_rns_code_01a_chunk12.txt
06/27/25  21:57            23,796 2025_06_27_21_57_53_2025_06_25_20_11_19_chatgpt_cad_rns_code_01a_chunk13.txt
06/27/25  21:57            43,468 2025_06_27_21_57_53_2025_06_25_20_11_19_chatgpt_cad_rns_code_01a_chunk14.txt
06/27/25  21:57            31,628 2025_06_27_21_57_53_2025_06_25_20_11_19_chatgpt_cad_rns_code_01a_chunk15.txt
06/27/25  21:57            34,351 2025_06_27_21_57_53_2025_06_25_20_11_19_chatgpt_cad_rns_code_01a_chunk2.txt
06/27/25  21:57            60,245 2025_06_27_21_57_53_2025_06_25_20_11_19_chatgpt_cad_rns_code_01a_chunk3.txt
06/27/25  21:57            30,922 2025_06_27_21_57_53_2025_06_25_20_11_19_chatgpt_cad_rns_code_01a_chunk4.txt
06/27/25  21:57            28,915 2025_06_27_21_57_53_2025_06_25_20_11_19_chatgpt_cad_rns_code_01a_chunk5.txt
06/27/25  21:57            26,061 2025_06_27_21_57_53_2025_06_25_20_11_19_chatgpt_cad_rns_code_01a_chunk6.txt
06/27/25  21:57            39,155 2025_06_27_21_57_53_2025_06_25_20_11_19_chatgpt_cad_rns_code_01a_chunk7.txt
06/27/25  21:57            35,147 2025_06_27_21_57_53_2025_06_25_20_11_19_chatgpt_cad_rns_code_01a_chunk8.txt
06/27/25  21:57            40,129 2025_06_27_21_57_53_2025_06_25_20_11_19_chatgpt_cad_rns_code_01a_chunk9.txt
06/27/25  12:39           291,936 full_conversation.txt
               0 Dir(s)  509,603,868,672 bytes free

C:\Users\carucci_r\Documents\chunker>dir processed /o:d
 Volume in drive C is OS
 Volume Serial Number is A263-CE95

 Directory of C:\Users\carucci_r\Documents\chunker\processed

06/25/25  20:12           519,561 2025_06_25_20_11_19_chatgpt_cad_rns_code_01a.txt
06/27/25  17:09           267,090 2025_06_27_17_08_32_policy_train_01.txt
06/27/25  21:34               153 test_file_now.txt
06/27/25  21:37                94 test_live.txt
06/27/25  21:48                97 working_test.txt
06/27/25  21:57    <DIR>          . 06/27/25  22:03    <DIR>          ..
               5 File(s)        786,995 bytes
               2 Dir(s)  509,603,930,112 bytes free

C:\Users\carucci_r\Documents\chunker>
ChatGPT said:
📄 Technical Summary
This log provides insights into the behavior and state of a file-watching and text-chunking system.
