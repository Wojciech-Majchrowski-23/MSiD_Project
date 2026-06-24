import sqlite3
import pandas
from pathlib import Path

LOCAL_FOLDER = Path(__file__).parent.parent / "local_folder"

class DatabaseManager:
    
    def __init__(self, db_filename: str = 'company_database.db'):
        self.db_path = LOCAL_FOLDER / db_filename
        
    def save_companies(self, dataFrame: pandas.DataFrame, table_name: str = 'companies'):
        with sqlite3.connect(self.db_path) as conn:
            dataFrame.to_sql(
                name=table_name,
                con=conn,
                if_exists='replace',
                index=False    
            )
            print(f"[BAZA DANYCH] Zapisano {len(dataFrame)} rekordów do tabeli '{table_name}'.")

    def get_companies(self, table_name: str = 'companies') -> pandas.DataFrame:
        with sqlite3.connect(self.db_path) as conn:
            return pandas.read_sql(f"SELECT * FROM {table_name}", conn)
        
    def get_companies_by_region(self, region: str) -> pandas.DataFrame:
        query = "SELECT CompanyName, Industry, Region, Revenue_WMA FROM companies WHERE Region = ?"
        with sqlite3.connect(self.db_path) as conn:
            return pandas.read_sql(query, conn, params=[region])

    def get_top_esg_stars(self, limit: int = 5) -> pandas.DataFrame:
        query = """
            SELECT CompanyName, Industry, `ESG_Signal-to-Noise` 
            FROM companies 
            ORDER BY `ESG_Signal-to-Noise` DESC 
            LIMIT ?
        """
        with sqlite3.connect(self.db_path) as conn:
            return pandas.read_sql(query, conn, params=[limit])
