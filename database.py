import sqlite3

# Initialize database
conn = sqlite3.connect("link.db") # или :memory: чтобы сохранить в RAM
cursor = conn.cursor()


# Initialize tables
def create_table_links():
    cursor.execute("""CREATE TABLE linkbase
                 (link text PRIMARY KEY, userId integer not NULL references userbase(userId) on delete cascade on update cascade, noindex bool, checking bool)""")


def delete_table_links():
    cursor.execute("DROP TABLE IF EXISTS linkbase;")
    conn.commit()


async def insert_link(url, userId, time=30):
    sql = "SELECT * FROM linkbase WHERE link = ?"
    if not cursor.execute(sql, [(url)]).fetchall():
        sql = "INSERT INTO linkbase VALUES (?, ?, ?, ?)"
        cursor.execute(sql, [(url),(userId),(False),(True)])
        conn.commit()


async def delete_link(url):
    sql = "DELETE FROM linkbase WHERE link = ?"
    cursor.execute(sql, [(url)])
    conn.commit()


async def delete_all_link(userId):
    sql = "DELETE FROM linkbase WHERE userId = ?"
    cursor.execute(sql, [(userId)])
    conn.commit()


async def change_link(url, check, time):
    sql = "UPDATE linkbase SET checking = ?, time = ? WHERE link = ?"
    cursor.execute(sql, [(check, time, url)])
    conn.commit()


def show_links(userId):
    sql = "SELECT * FROM linkbase WHERE userId = ?"
    return cursor.execute(sql, [(userId)])


def check_links():
    sql = "SELECT * FROM linkbase"
    return cursor.execute(sql)

#########################################

def create_table_users():
    cursor.execute("""CREATE TABLE userbase
                 (username text PRIMARY KEY, userId integer not NULL, privilege integer not NULL, dateReg text not NULL, days integer not NULL, maxcount integer not NULL, count integer not NULL)""")


async def insert_user(username, userId, dateReg, privilege = 1, days = 30, maxcount = 30, count = 0):
    sql = "SELECT * FROM userbase WHERE username = ?"
    print("test1")
    if not cursor.execute(sql, [(username)]).fetchall():
        print("test2")
        sql = "INSERT INTO userbase VALUES (?, ?, ?, ?, ?, ?, 0)"
        cursor.execute(sql, [(username),(userId),(privilege),(dateReg),(days),(maxcount)])
        conn.commit()


def insert_user2(username, userId, dateReg,  privilege = 1, days = 30, maxcount = 30, count = 0):
    sql = "SELECT * FROM userbase WHERE username = ?"
    if not cursor.execute(sql, [(username)]).fetchall():
        sql = "INSERT INTO userbase VALUES (?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(sql, [(username),(userId),(privilege),(days),(dateReg),(maxcount),(count)])
        conn.commit()


async def increase_count(username):
    sql = "SELECT * FROM userbase WHERE username = ?"
    x = cursor.execute(sql, [(username)]).fetchall()
    if x[0][6] < x[0][5] or x[0][5] == -1:
        sql = "UPDATE userbase SET count = ? WHERE username = ?"
        cursor.execute(sql, [(x[0][6]+1), (username)])
        conn.commit()
    return (x[0][5]-x[0][6])


async def decrease_count(username):
    sql = "SELECT * FROM userbase WHERE username = ?"
    x = cursor.execute(sql, [(username)]).fetchall()
    sql = "UPDATE userbase SET count = ? WHERE username = ?"
    cursor.execute(sql, [(x[0][6]-1), (username)])
    conn.commit()
    return (x[0][5]-x[0][6])


async def delete_user(username):
    sql = "DELETE FROM userbase WHERE username = ?"
    cursor.execute(sql, [(username)])
    conn.commit()


async def show_users(userId):
    sql = "SELECT * FROM userbase"
    return cursor.execute(sql)


async def delete_table_users():
    cursor.execute("DROP TABLE IF EXISTS userbase;")
    conn.commit()


async def check_user(username):
    sql = "SELECT * FROM userbase"
    test = cursor.execute(sql).fetchall()
    if test:
        return test[0][0]
    return None


async def check_admin(username):
    sql = "SELECT * FROM userbase WHERE username = ? and privilege = 0"
    test = cursor.execute(sql, [(username)]).fetchall()
    if test:
        return test[0][0]
    return None


#create_table_users()
#create_table_links()