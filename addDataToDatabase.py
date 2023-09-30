import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://face-recognition-system"
})

ref = db.reference('Users')

data = {
    "1":{
        "Name":"Payal Narwal",
        "Age":20,
        "Gender":"Female",
        "last_login_time":"2023-09-29 00:54:34"
    },
    "2":{
        "Name":"Mayank Narwal",
        "Age":17,
        "Gender":"Male",
        "last_login_time":"2023-09-29 00:54:34"
    },
    "3":{
        "Name":"Seema",
        "Age":40,
        "Gender":"Female",
        "last_login_time":"2023-09-29 00:54:34"
    },
    "4":{
        "Name":"Sanjay Kumar",
        "Age":45,
        "Gender":"Male",
        "last_login_time":"2023-09-29 00:54:34"
    }
    
}

for key, value in data.items():
    ref.child(key).set(value)
