from .__con import db

def saveUsersData (data):
    col = db['users_data']
    return col.insert_one(data)

