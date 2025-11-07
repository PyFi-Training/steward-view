# Maps existing column names to standard names for rename_columns

COLUMNS = {
    'Date'            : 'date',
    'Transaction Date': 'date',
    'Order Date'      : 'date',
    0                 : 'date',
    
    'Description'     : 'description',
    'Product Name'    : 'description',
    3                 : 'description',
    
    'Amount'          : 'amount',
    'Total Owed'      : 'amount',
    1                 : 'amount'
}


# Description substrings that indicate that filter_rows should exclude 
# a row

ROW_EXCLUSION_INDICATORS = 'Mobile Payment|Beginning balance|EPAY ID'