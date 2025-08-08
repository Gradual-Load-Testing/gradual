import psycopg2


conn = psycopg2.connect(
    host="postgres",
    port=5432,
    database="stress_db",
    user="stress_user",
    password="stress_password",
)

print(conn)
