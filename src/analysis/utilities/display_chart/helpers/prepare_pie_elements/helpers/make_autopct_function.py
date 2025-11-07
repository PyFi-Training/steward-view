def make_autopct_function(grouped_df):
    '''
    Create a label formatting function to pass to the Matplotlib pie chart 
    method.
    '''
    def autopct(wedge_percentage):
        total_dollar_value = grouped_df.sum()
        wedge_dollar_value = (wedge_percentage / 100) * total_dollar_value 
        return f'${wedge_dollar_value:,.2f}\n({int(round(wedge_percentage)):d}%)'
    return autopct