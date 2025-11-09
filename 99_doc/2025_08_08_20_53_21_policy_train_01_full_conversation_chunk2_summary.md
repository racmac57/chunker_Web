# Chunk 2 Summary

both, provide the lists for the dropdowns based on the data for course names and location in the file
# Load the relevant sheets to extract course names and delivery mode data
inperson_df = pd.read_excel(excel_path, sheet_name='InPerson OnLine Firearms')
firearms_df = pd.read_excel(excel_path, sheet_name='Firearms')
online_df = pd.read_excel(excel_path, sheet_name='On-line')
# Combine all for lookup
combined_df = pd.concat([inperson_df, firearms_df, online_df], ignore_index=True)
# Normalize column names
combined_df.columns = [str(col).strip() for col in combined_df.columns]
# Extract unique course names
course_col = next((col for col in combined_df.columns if 'Course Name' in col), None)
course_names = sorted(combined_df[course_col].dropna().unique()) if course_col else []
# Extract unique training locations (assume "Delivery Mode" not explicitly listed, we infer from sheet names)
delivery_modes = ['In-Person', 'Online', 'Hybrid']  # Preset list
training_types = ['Firearms', 'Medical', 'Legal', 'Tactics', 'Driving', 'CPR', 'Use of Force', 'Policy']  # Can be extended
course_names[:10], delivery_modes, training_types
ValueError                                Traceback (most recent call last)
Cell In[14], line 3
      1 # Load the relevant sheets to extract course names and delivery mode data
      2 inperson_df = pd.read_excel(excel_path, sheet_name='InPerson OnLine Firearms')
----> 3 firearms_df = pd.read_excel(excel_path, sheet_name='Firearms')
      4 online_df = pd.read_excel(excel_path, sheet_name='On-line')
      6 # Combine all for lookup
File ~/.local/lib/python3.11/site-packages/pandas/util/_decorators.py:211, in deprecate_kwarg.<locals>._deprecate_kwarg.<locals>.wrapper(*args, **kwargs)
    209     else:
    210         kwargs[new_arg_name] = new_arg_value
--> 211 return func(*args, **kwargs)
File ~/.local/lib/python3.11/site-packages/pandas/util/_decorators.py:331, in deprecate_nonkeyword_arguments.<locals>.decorate.<locals>.wrapper(*args, **kwargs)
    325 if len(args) > num_allow_args:
    326     warnings.warn(
    327         msg.format(arguments=_format_argument_list(allow_args)),
    328         FutureWarning,
    329         stacklevel=find_stack_level(),
    330     )
--> 331 return func(*args, **kwargs)
File ~/.local/lib/python3.11/site-packages/pandas/io/excel/_base.py:490, in read_excel(io, sheet_name, header, names, index_col, usecols, squeeze, dtype, engine, converters, true_values, false_values, skiprows, nrows, na_values, keep_default_na, na_filter, verbose, parse_dates, date_parser, thousands, decimal, comment, skipfooter, convert_float, mangle_dupe_cols, storage_options)
    484     raise ValueError(
    485         "Engine should not be specified when passing "
    486         "an ExcelFile - ExcelFile already has the engine set"
    487     )
    489 try:
--> 490     data = io.parse(
    491         sheet_name=sheet_name,
    492         header=header,
    493         names=names,
    494         index_col=index_col,
    495         usecols=usecols,
    496         squeeze=squeeze,
    497         dtype=dtype,
    498         converters=converters,
    499         true_values=true_values,
    500         false_values=false_values,
    501         skiprows=skiprows,
    502         nrows=nrows,
    503         na_values=na_values,
    504         keep_default_na=keep_default_na,
    505         na_filter=na_filter,
    506         verbose=verbose,
    507         parse_dates=parse_dates,
    508         date_parser=date_parser,
    509         thousands=thousands,
    510         decimal=decimal,
    511         comment=comment,
    512         skipfooter=skipfooter,
    513         convert_float=convert_float,
    514         mangle_dupe_cols=mangle_dupe_cols,
    515     )
    516 finally:
    517     # make sure to close opened file handles
    518     if should_close:
File ~/.local/lib/python3.11/site-packages/pandas/io/excel/_base.py:1734, in ExcelFile.parse(self, sheet_name, header, names, index_col, usecols, squeeze, converters, true_values, false_values, skiprows, nrows, na_values, parse_dates, date_parser, thousands, comment, skipfooter, convert_float, mangle_dupe_cols, **kwds)
   1700 def parse(
   1701     self,
   1702     sheet_name: str | int | list[int] | list[str] | None = 0,
   (...)   1721     **kwds,
   1722 ) -> DataFrame | dict[str, DataFrame] | dict[int, DataFrame]:
   1723     """
   1724     Parse specified sheet(s) into a DataFrame. 1725 
   (...)   1732         DataFrame from the passed in Excel file. 1733     """
-> 1734     return self._reader.parse(
   1735         sheet_name=sheet_name,
   1736         header=header,
   1737         names=names,
   1738         index_col=index_col,
   1739         usecols=usecols,
   1740         squeeze=squeeze,
   1741         converters=converters,
   1742         true_values=true_values,
   1743         false_values=false_values,
   1744         skiprows=skiprows,
   1745         nrows=nrows,
   1746         na_values=na_values,
   1747         parse_dates=parse_dates,
   1748         date_parser=date_parser,
   1749         thousands=thousands,
   1750         comment=comment,
   1751         skipfooter=skipfooter,
   1752         convert_float=convert_float,
   1753         mangle_dupe_cols=mangle_dupe_cols,
   1754         **kwds,
   1755     )
File ~/.local/lib/python3.11/site-packages/pandas/io/excel/_base.py:760, in BaseExcelReader.parse(self, sheet_name, header, names, index_col, usecols, squeeze, dtype, true_values, false_values, skiprows, nrows, na_values, verbose, parse_dates, date_parser, thousands, decimal, comment, skipfooter, convert_float, mangle_dupe_cols, **kwds)
    757     print(f"Reading sheet {asheetname}")
    759 if isinstance(asheetname, str):
--> 760     sheet = self.get_sheet_by_name(asheetname)
    761 else:  # assume an integer if not a string
    762     sheet = self.get_sheet_by_index(asheetname)
File ~/.local/lib/python3.11/site-packages/pandas/io/excel/_openpyxl.py:577, in OpenpyxlReader.get_sheet_by_name(self, name)
    576 def get_sheet_by_name(self, name: str):
--> 577     self.raise_if_bad_sheet_by_name(name)
    578     return self.book[name]
File ~/.local/lib/python3.11/site-packages/pandas/io/excel/_base.py:602, in BaseExcelReader.raise_if_bad_sheet_by_name(self, name)
    600 def raise_if_bad_sheet_by_name(self, name: str) -> None:
    601     if name not in self.sheet_names:
--> 602         raise ValueError(f"Worksheet named '{name}' not found")
ValueError: Worksheet named 'Firearms' not found
It looks like the sheet you're referring to as 'Firearms' is actually named something else in the file — possibly "InPerson OnLine Firearms" or a variant like "InPerson OnLine Firearms (2)".
