from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart



load_dotenv()  # Load environment variables from .env

app = Flask(__name__)
CORS(app)

# MySQL configuration
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

# Application Configuration
app_config = {
    'APP_URL': os.getenv('APP_URL'),
    'API_KEY': os.getenv('API_KEY'),
    'API_SECRET': os.getenv('API_SECRET'),
    'SECRET_KEY': os.getenv('SECRET_KEY')
}

mysql = MySQL(app)


@app.route('/',methods=['GET'])
def home():
    data={"message":"welcome to React World"}
    return jsonify(data),200
    
# User signup
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')  
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify(message="Missing required fields"), 400
    
    # Hash the password
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    # Check if the user already exists
    cursor1 = mysql.connection.cursor()
    cursor1.execute('SELECT username FROM users WHERE username = %s', (username,))
    user = cursor1.fetchone()
    cursor1.close()

    if user is not None:
        return jsonify(message="That user already exists. Please click the login button"), 400

    cursor = mysql.connection.cursor()
    query = 'INSERT INTO users (username, email, password) VALUES (%s, %s, %s)'
    values = (username, email, password)
    cursor.execute(query, values)

    mysql.connection.commit()
    cursor.close()

    return jsonify(message="User created successfully"), 200

# User login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    reg_password = data.get('password')
    
    
    # check for  authentication
    
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT username FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()
    cursor.close()
    print(user) 
    
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT password FROM users WHERE username = %s', (username,))
    passw = cursor.fetchone()
    cursor.close()
    if user is None and passw is None:
        return jsonify(message="User not found"), 200
    elif user is None and passw[0]==reg_password:
        return jsonify(message="Incorrect User"), 200
    elif user is not None and  passw[0]!=reg_password:
        return jsonify(message="Incorrect Password"),200
    elif user is not None and passw[0]==reg_password:
        cursor =mysql.connection.cursor()
        cursor.execute('SELECT chk FROM users WHERE username = %s', (username,))
        demo = cursor.fetchone()
        cursor.execute('update users set chk=1 where username = %s',(username,))
        mysql.connection.commit()
        cursor.close()
        return jsonify(message="Login successful",count=demo[0]), 200
    else:
        return jsonify(message="Incorrect ID or Pass"),400
    
   

    

# forget password
@app.route('/forget_pass',methods=['POST'])
def forget_pass():
    data=request.json
    email=data.get('email')
    print(email)
    cursor=mysql.connection.cursor()
    cursor.execute('Select password from users where email = %s',(email,))
    snt_pass=cursor.fetchone()
    cursor.close()
    print(snt_pass)
    
    if snt_pass!=None:
        org_password = snt_pass[0]
        
        # Email sending logic
        sender_email =  os.getenv('sender_m') # Replace with your email
        sender_password = os.getenv('sender_p')         # Replace with your email password
        subject = "Your Password Recovery Request"
        recipient_email = email

        # Create email content
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = recipient_email
        message['Subject'] = subject
        body = f"Dear User,\n\nYour password is: {org_password}\n\nRegards,\nSupport Team"
        message.attach(MIMEText(body, 'plain'))
        
        try:
            # Connect to the SMTP server
            server = smtplib.SMTP('smtp.gmail.com', 587)  # Use appropriate SMTP server and port
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
            server.close()
            return jsonify(message="Email has been sent to registered email"), 200
        except Exception as e:
            return jsonify(message="Failed to send email. Please try again later.", error=str(e)), 500
        #return jsonify(message="email has been send to registerd mail"),200
    else:
        return jsonify(message="mail id is not registered")
  
  
  
#complain 
@app.route('/complain_box',methods=['POST'])
def complain_box():
    data=request.json
    quality=data.get('quality')                    #excellent good poor
    star=data.get('star')
    suggestion=data.get('suggestion')
    
    #details of sender and reciever  
    sender_email =  os.getenv('sender_m') 
    sender_password =  os.getenv('sender_p')     
    subject = "Feedback and suggestions"
    recipient_email = 'pwnydv.02@gmail.com'
    
    data_want_send=MIMEMultipart()
    data_want_send['From']=sender_email
    data_want_send['To']=recipient_email
    data_want_send['subject']=subject
    body=f"Feedback from customer- \n Your app quality is :{quality} \n Anonymous person given you {star} stars \n Suggestion from Anonymous person is {suggestion} \n Thank you."
    data_want_send.attach(MIMEText(body,'plain'))
    
    
    try:
        # Connect to the SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587) 
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, data_want_send.as_string())
        server.close()
        return jsonify(message="Feedback has been sent to registered email"), 200
    except Exception as e:
        return jsonify(message="Failed to send email. Please try again later.", error=str(e)), 500
    

# Store app access data
@app.route('/access', methods=['POST'])
def access():
    data = request.json
    user_id = data.get('user_id')

    cursor = mysql.connection.cursor()
    cursor.execute('INSERT INTO access_log (user_id) VALUES (%s)', (user_id,))
    mysql.connection.commit()
    cursor.close()

    return jsonify(message="Access logged"), 200


#Update Password
@app.route('/update_pass',methods=['POST'])
def update_pass():
    data=request.json
    password=data.get('password')
    confirm_password=data.get('confirm_password')
    username=data.get('username')
    if username is None:
        return jsonify(message="username is mandotry"),400
    if password!=confirm_password:
        return jsonify(message="password not meet"),400
    cursor=mysql.connection.cursor()
    cursor.execute('update users set password = %s where username = %s',(password,username,))
    mysql.connection.commit()
    cursor.close()
    
    return jsonify(message="password updated succssfully"),200  

if __name__ == '__main__':
    app.run(debug=True)
    
    
    
  
    
    
    