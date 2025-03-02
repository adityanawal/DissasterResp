import sys
import pandas as pd
from sqlalchemy import create_engine

def load_data(messages_filepath, categories_filepath):
    '''
    Load the messages and categories CSV's for processing
    
    INPUT:
    messages_filepath : Path to the messages csv
    categories_filepath: Path to the categories csv
    OUTPUT:
    df: merged dataset
    '''
    messages = pd.read_csv(messages_filepath)
    categories = pd.read_csv(categories_filepath)
    df = messages.merge(categories, on='id')
    return df


def clean_data(df):
    '''
    Cleaning the dataframe for further processing
    
    INPUT:
    df: Loaded and merged dataframe
    OUTPUT:
    clean_df: cleaned dataframe
    '''
    #Working on the categories. Split into individual categories and store in new dataframe 
    categories = df['categories'].str.split(pat=';', expand=True)
    # select the first row of the categories dataframe
    row = categories.iloc[0]
    # use this row to extract a list of new column names for categories.
    category_colnames = row.apply(lambda x: x[:-2])
    # rename the columns of `categories`
    categories.columns = category_colnames
    
    #convert categories to numbers : 0 and 1
    for column in categories:
        # set each value to be the last character of the string
        categories[column] = categories[column].astype(str).str[-1:]
        # convert column from string to numeric
        categories[column] = categories[column].astype(int)

    #There is an error in related. Setting it to 0 as it seems like an entry error. 1 would not be appropriate
    categories['related']=categories['related'].map(lambda x: 0 if x > 1 else x)
    
    #child alone has not a single 1 : dropping the column
    categories = categories.drop(['child_alone'],axis=1)
    
    # drop the original categories column from `df`
    df.drop(['categories'], axis=1, inplace=True)
    # concatenate the original dataframe with the new `categories` dataframe
    df = pd.concat([df, categories], axis=1)

    # drop duplicates
    df.drop_duplicates(inplace=True)
    # We need to drop the duplicated ID columns, as they are the same message classified differently
    df.drop_duplicates(subset='id', inplace=True)
    #It seems there are 138 rows in which all classification values are Null. removing them
    clean_df = df[df['request'].notnull()] 
        
    return clean_df


def save_data(df, database_filename):
    '''
    Save cleaned dataset into an sql database
    
    INPUT:
    df : Cleaned dataset
    database_filename : database file
    
    OUTPUT:
    none
    '''
    engine = create_engine('sqlite:///{}'.format(database_filename))
    df.to_sql('DisasterResponse', engine, index=False, if_exists = 'replace')


def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()