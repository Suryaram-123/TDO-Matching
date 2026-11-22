import json, os, sqlite3
from datetime import datetime, timezone

DB = os.getenv('DATABASE_PATH', 'store_verification.db')

def init_db():
    con = sqlite3.connect(DB)
    con.execute('''CREATE TABLE IF NOT EXISTS verifications (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      created_at TEXT NOT NULL,
      store_name TEXT, address TEXT, city TEXT, state TEXT, postal_code TEXT, country TEXT,
      final_status TEXT, confidence TEXT, explanation TEXT, report_json TEXT NOT NULL
    )''')
    con.commit(); con.close()

def save_report(report):
    x=report['input']; con=sqlite3.connect(DB)
    con.execute('''INSERT INTO verifications
      (created_at,store_name,address,city,state,postal_code,country,final_status,confidence,explanation,report_json)
      VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
      (datetime.now(timezone.utc).isoformat(), x.get('store_name'),x.get('address'),x.get('city'),x.get('state'),x.get('postal_code'),x.get('country'), report.get('final_status'),report.get('confidence'),report.get('explanation'),json.dumps(report,ensure_ascii=False)))
    con.commit(); con.close()

def history(limit=500):
    con=sqlite3.connect(DB); cur=con.execute('''SELECT id,created_at,store_name,address,city,state,postal_code,final_status,confidence,explanation FROM verifications ORDER BY id DESC LIMIT ?''',(limit,))
    cols=[d[0] for d in cur.description]; rows=[dict(zip(cols,r)) for r in cur.fetchall()]; con.close(); return rows
