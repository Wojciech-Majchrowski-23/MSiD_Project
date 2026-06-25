import pandas as pd
from sqlalchemy import create_engine, text

class DatabaseManager:
    
    def __init__(self, db_url: str = 'postgresql://myuser:mypassword@localhost:5432/company_db'):
        self.engine = create_engine(db_url)
        
    def save_companies(self, dataFrame: pd.DataFrame, table_name: str = 'companies'):
        dataFrame.to_sql(
            name=table_name,
            con=self.engine,
            if_exists='replace',
            index=False    
        )
        print(f"[BAZA DANYCH] Zapisano {len(dataFrame)} rekordów do tabeli '{table_name}'.")

    def get_companies(self, table_name: str = 'companies') -> pd.DataFrame:
        return pd.read_sql(f"SELECT * FROM {table_name}", con=self.engine)
        
    def get_companies_by_region(self, region: str) -> pd.DataFrame:
        query = text('SELECT "CompanyName", "Industry", "Region", "Revenue_WMA" FROM companies WHERE "Region" = :region')
        
        with self.engine.connect() as conn:
            return pd.read_sql(query, conn, params={"region": region})

    def get_top_esg_stars(self, limit: int = 5) -> pd.DataFrame:
        query = text("""
            SELECT "CompanyName", "Industry", "ESG_Signal-to-Noise" 
            FROM companies 
            ORDER BY "ESG_Signal-to-Noise" DESC 
            LIMIT :limit
        """)
        
        with self.engine.connect() as conn:
            return pd.read_sql(query, conn, params={"limit": limit})