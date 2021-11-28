from __future__ import print_function, absolute_import, unicode_literals
from fido2.webauthn import PublicKeyCredentialRpEntity
from fido2.client import ClientData
from fido2.server import Fido2Server
from fido2.ctap2 import AttestationObject, AuthenticatorData
from fido2 import cbor
from flask import *
from sqltasks import *
import pickle
import string
import random
import os

url="reverseproxy.eastus.cloudapp.azure.com"
app = Flask(__name__, static_url_path="")
app.secret_key = os.urandom(32)  # Used for session.

rp = PublicKeyCredentialRpEntity(url, "Demo server")
server = Fido2Server(rp)

credentials = []

@app.route("/")
def index():
    return redirect("/success")

@app.route("/reg")
def reg():
	return render_template("getreg.html")

@app.route("/reginit", methods=["POST"])
def reginit():
	rnum=request.form['rnum']
	print(rnum)
	resp = make_response(render_template('register.html',rnum=rnum))
	resp.set_cookie('rnum',rnum,max_age=60*60*24*365*8)
	return resp

@app.route("/markattendance", methods=["GET"])
def markattendance():
	classid=request.args.get('classId')
	rnum=request.cookies.get('rnum')
	return render_template("authenticate.html",rnum=rnum, cid=classid)
	
@app.route("/attendance")
def attendance():
	return render_template("authenticatelegacy.html")
	
@app.route("/markattendancelegacy", methods=["POST"])
def markattendancelegacy():
	classid=request.form['cid']
	rnum=request.form['rnum']
	return render_template("authenticate.html",rnum=rnum, cid=classid)
	
@app.route("/downloadattendance", methods=["GET"])
def downloadattendance():
	classid=request.args.get('classId')
	res=getReg_nobyclass_id(classid)
	output=make_response(res)
	output.headers["Content-Disposition"] = "attachment; filename=attendance_"+classid+".csv"
	output.headers["Content-type"] = "text/csv"
	return output
	
@app.route("/getportal")
def getportal():
	cid=random.randint(0,999999)
	return render_template("instructor.html",cid=cid)
	
@app.route("/resumeportal")
def resumeportal():
	return render_template("resumeinstructor.html")
	
@app.route("/resumeportalpage", methods=["POST"])
def resumeportalpage():
	cid=request.form['cid']
	return render_template("instructor.html",cid=cid)
	
@app.route("/success")
def success():
	return render_template("success.html")
	
@app.route("/api/register/begin", methods=["POST"])
def register_begin():
    user = request.args.get('nm')
    print(user)
    credentials=readkey(user)
    registration_data, state = server.register_begin(
        {
            "id": b"user_id",
            "name": user,
            "displayName": user,
            "icon": "https://example.com/image.png",
        },
        credentials,
        user_verification="discouraged",
        authenticator_attachment="platform",
    )

    session["state"] = state
    print("\n\n\n\n")
    print(registration_data)
    print("\n\n\n\n")
    return cbor.encode(registration_data)


@app.route("/api/register/complete", methods=["POST"])
def register_complete():
    user = request.args.get('nm')
    print(user)
    credentials=readkey(user)
    data = cbor.decode(request.get_data())
    client_data = ClientData(data["clientDataJSON"])
    att_obj = AttestationObject(data["attestationObject"])
    print("clientData", client_data)
    print("AttestationObject:", att_obj)
    auth_data = server.register_complete(session["state"], client_data, att_obj)
    credentials.append(auth_data.credential_data)
    savekey(credentials,user)
    print("REGISTERED CREDENTIAL:", auth_data.credential_data)
    return cbor.encode({"status": "OK"})


@app.route("/api/authenticate/begin", methods=["POST"])
def authenticate_begin():
    user = request.args.get('nm')
    print(user)
    credentials=readkey(user)

    if not credentials:
        abort(404)

    auth_data, state = server.authenticate_begin(credentials)
    session["state"] = state
    return cbor.encode(auth_data)

@app.route("/api/authenticate/complete", methods=["POST"])
def authenticate_complete():
    user = request.args.get('nm')
    classid=request.args.get('cid')
    print(user)
    print(classid)
    credentials=readkey(user)
    if not credentials:
        abort(404)

    data = cbor.decode(request.get_data())
    credential_id = data["credentialId"]
    client_data = ClientData(data["clientDataJSON"])
    auth_data = AuthenticatorData(data["authenticatorData"])
    signature = data["signature"]
    print("clientData", client_data)
    print("AuthenticatorData", auth_data)

    server.authenticate_complete(
        session.pop("state"),
        credentials,
        credential_id,
        client_data,
        auth_data,
        signature,
    )
    print("ASSERTION OK")
    
    print("\n\n")
    print("Attendance marking for "+user+" in class "+classid);
    addUser(user,classid)    
    return cbor.encode({"status": "OK"})
    
def savekey(credentials,user):
	with open(user+'datafilekey.pkl','wb') as outp1:
		pickle.dump(credentials,outp1,pickle.HIGHEST_PROTOCOL)
		
def readkey(user):
	print(user)
	try:
		with open(user+'datafilekey.pkl', 'rb') as inp:
			temp = pickle.load(inp)
			print("Data read")
			#print(credentials)
			return temp
	except:
		print("no cred data")
		return []


if __name__ == "__main__":
	context = ('server.crt', 'server.key')
	app.run(ssl_context=context, debug=False, host="0.0.0.0", port=8080)
