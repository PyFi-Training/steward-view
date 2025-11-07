def show_time_period(table):
    '''
    Display the dates of the earliest and latest transactions in table.
    '''
    start_date  = str(table['date'].min())
    end_date    = str(table['date'].max())
    print('')
    print(f'Time Period: {start_date} to {end_date}')