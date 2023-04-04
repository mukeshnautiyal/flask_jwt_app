from flask_sqlalchemy import SQLAlchemy
 
db = SQLAlchemy()

class TA(db.Model):
    __tablename__ = "ta"
    
    id = db.Column(db.Integer, primary_key=True)
    native_english_speaker = db.Column(db.String())
    course_instructor = db.Column(db.String())
    course = db.Column(db.String())
    semester = db.Column(db.String(80))
    class_size = db.Column(db.Integer)
    performance_score = db.Column(db.Integer)
    
    def __init__(self,native_english_speaker,course_instructor,course,semester,class_size,performance_score):
        self.native_english_speaker = native_english_speaker
        self.course_instructor = course_instructor
        self.course = course
        self.semester = semester
        self.class_size = class_size
        self.performance_score = performance_score
 
    def __repr__(self):
        return f"{self.course}:{self.native_english_speaker}"
        
        
class User(db.Model):
    __tablename__="users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String())
    email = db.Column(db.String())
    password = db.Column(db.String())
    
    def __init__(self, username,email,password):
        self.username = username
        self.email = email
        self.password = password
        
    def __repr__(self):
        return f"{self.email}:{self.username}"