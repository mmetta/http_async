import ast
import json
import os
import sqlite3

appData = os.getenv('APPDATA') + '\\BinanceAsync'
database = os.path.join(appData, 'config.db')


def create_db():
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    # ## CREATE ## #
    cursor.execute("""
            CREATE TABLE configs (
                theme TEXT NOT NULL,
                color_primary TEXT NOT NULL,
                wallet TEXT NOT NULL,
                coin TEXT,
                my_list TEXT NOT NULL,
                all_list TEXT NOT NULL
            );
            """)
    print('Tabela criada com sucesso.')

    theme = 'dark'
    primary = '#00aaff'
    wallet = '0.0'
    my_list = ['BTCBUSD', 'BTCBRL', 'ADABUSD', 'ADABRL', 'MATICBUSD', 'MATICBRL', 'BUSDBRL', 'USDTBRL']
    all_list = []
    conn.execute("INSERT INTO configs (theme, color_primary, my_list, all_list, wallet, coin) VALUES (?, ?, ?, ?, ?, ?)",
                 (theme, primary, str(my_list), str(all_list), wallet, None))
    conn.commit()
    conn.close()


def converter(campo):
    return ast.literal_eval(campo)


def select_all():
    # def project_settings():
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM configs;
    """)
    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    data = []
    for row in rows:
        data.append(dict(zip(columns, row)))
    json_data = json.dumps(data)
    obj = json.loads(json_data)
    obj[0]['my_list'] = eval(obj[0]['my_list'])
    obj[0]['all_list'] = eval(obj[0]['all_list'])
    return obj[0]


def update_data(data):
    # ## UPDATE ## #
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE configs SET theme = ?, color_primary = ?, my_list = ?, all_list = ?, wallet = ?, coin = ?
    """, (data['theme'], data['color_primary'], str(data['my_list']), str(data['all_list']), data['wallet'], data['coin']))
    conn.commit()
    conn.close()
