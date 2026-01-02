import os
os.environ["ENV_LOGIN"] = "production"
os.environ["DATABASE_URL"] = "postgres://postgres.zebohotkplhbssxujtns:IaWJmFqCvgE28Smh@aws-1-sa-east-1.pooler.supabase.com:5432/postgres?sslmode=require"
from loadDB import llenar_base_de_datos

if __name__ == "__main__":
    print("🚀 Inicializando base de datos de PostgreSQL...")
    llenar_base_de_datos()
    print("✅ Base de datos inicializada correctamente")
