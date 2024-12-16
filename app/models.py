from app import db
from sqlalchemy.orm import relationship
from sqlalchemy.orm import aliased
from sqlalchemy.orm import aliased
from flask_login import UserMixin
from app import login_manager
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    nickname = db.Column(db.String(50), nullable=True)  # Никнейм
    university = db.Column(db.String(255), nullable=True)  # Университет
    num_of_course = db.Column(db.String(10), nullable=True)  # Номер курса
    institute = db.Column(db.String(255), nullable=True)  # Институт
    group = db.Column(db.String(50), nullable=True)  # Группа
    role = db.Column(db.String(50), nullable=False)  # student, teacher, admin
    password_hash = db.Column(db.Text, nullable=False)
    registration_date = db.Column(db.DateTime, default=db.func.now())
    status = db.Column(db.String(50), default='offline')  # online/offline
    last_login = db.Column(db.DateTime)
    profile_picture = db.Column(db.Text)
    phone_number = db.Column(db.String(20), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)  # Дата рождения
    accept_policy = db.Column(db.Boolean, nullable=False)  # Чекбокс принятия политики
    address = db.Column(db.Text, nullable=True)
    telegram_link = db.Column(db.Text, nullable=True)
    two_factor_enabled = db.Column(db.Boolean, default=False)
    bio = db.Column(db.Text, nullable=True)
    favorite_sport_club = db.Column(db.String(100), nullable=True)
    # courses = db.relationship(
    #     'Course',
    #     secondary='course_student',
    #     back_populates='students'
    # )
    courses_assoc = db.relationship('CourseStudent', back_populates='student', cascade="all, delete-orphan")
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()

    def __repr__(self):
        return f'<User {self.full_name}>'

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))

# for temporary
# course_student = db.Table(
#     'course_student',
#     db.Column('course_id', db.Integer, db.ForeignKey('courses.id', ondelete="CASCADE"), nullable=False),
#     db.Column('student_id', db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
# )
class CourseStudent(db.Model):
    __tablename__ = 'course_student'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete="CASCADE"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    added_date = db.Column(db.DateTime, default=db.func.now())  # Время добавления записи
    status = db.Column(db.String(50), default='active')  # Например: active/inactive

    # Связь с другими таблицами
    course = db.relationship('Course', back_populates='students_assoc')
    student = db.relationship('User', back_populates='courses_assoc')

class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    tutor_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    status = db.Column(db.String(50), default='active')  # active/finished
    duration = db.Column(db.Interval)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    course_code = db.Column(db.String(50), unique=True)
    category = db.Column(db.String(100))
    # students = db.relationship(
    #     'User',
    #     secondary='course_student',
    #     back_populates='courses'
    # )
    students_assoc = db.relationship('CourseStudent', back_populates='course', cascade="all, delete-orphan")
    lessons = db.relationship(
        'Lesson',
        backref='course',
        cascade="all, delete-orphan"
    )
    feedback = db.relationship(
        'Feedback',
        backref='course_feedbacks',
        cascade="all, delete-orphan"
    )

    @property
    def students_count(self):
        return len(self.students)

    def average_rating(self):
        # Используем db.session для явного запроса
        feedbacks = Feedback.query.filter_by(course_id=self.id).all()
        if feedbacks:
            total_marks = sum(f.mark for f in feedbacks)
            return total_marks / len(feedbacks)
        return 0

    def course_quality(self):
        avg_rating = self.average_rating()
        if avg_rating >= 4.8:
            return "Excellent course, everything is clear"
        elif 4.3 <= avg_rating < 4.8:
            return "Approximately good, but something missed"
        elif 4 < avg_rating < 4.3:
            return "Awesome"
        elif 3.5 < avg_rating < 4:
            return "Not that bad"
        else:
            return "Needs Improvement"

# Таблица занятий
class Lesson(db.Model):
    __tablename__ = 'lessons'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete="CASCADE"))
    date = db.Column(db.Date, nullable=False)
    topic = db.Column(db.String(255), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time)
    location = db.Column(db.String(255))
    # attendance = db.relationship('Attendance', backref = 'lesson')
    # attendance_records = db.relationship('Attendance', backref='lesson_record', lazy=True, overlaps="attendances_list")

# Таблица посещаемости
class Attendance(db.Model):
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id', ondelete="CASCADE"))
    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    status = db.Column(db.String(50), nullable=False)  # was/not
    comments = db.Column(db.Text)
    reason_of_excuse = db.Column(db.Text)
    lesson = db.relationship('Lesson', backref='attendances_list', overlaps="attendance_records")  # Указываем overlaps
    course = db.relationship('Course', secondary='lessons', viewonly=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    student = db.relationship('User', backref='attendance_records')

# Таблица отзывов
class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id', ondelete="CASCADE"))
    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete="CASCADE"))
    mark = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    exact_time = db.Column(db.DateTime, default=db.func.now())
    anonymous = db.Column(db.Boolean, default=False)
    type = db.Column(db.String(50))
    response_on_feedback = db.Column(db.Text)
    lesson = db.relationship('Lesson', lazy=True)
    student = db.relationship('User', lazy=True)
    course = db.relationship('Course', lazy=True, overlaps="course_feedbacks,feedback")
    is_hidden = db.Column(db.Boolean, default=False)  # скрыть фидбек

# Таблица уведомлений
class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    status = db.Column(db.String(50), default='unread')  # read/unread
    date_time = db.Column(db.DateTime, default=db.func.now())
    type = db.Column(db.String(50))

# Таблица ролей
class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(50), unique=True, nullable=False)
    permission_list = db.Column(db.JSON, nullable=False)
    description = db.Column(db.Text)

# Таблица статистики
class Statistic(db.Model):
    __tablename__ = 'statistics'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete="CASCADE"))
    type = db.Column(db.String(50), nullable=False)  # attendance/feedback
    parameters = db.Column(db.JSON)
    generated_at = db.Column(db.DateTime, default=db.func.now())

# Таблица дополнительных материалов
class ExtraMaterial(db.Model):
    __tablename__ = 'extra_materials'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete="CASCADE"))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.Text, nullable=False)
    uploaded_at = db.Column(db.DateTime, default=db.func.now())
    need_to_delete = db.Column(db.String(255), nullable=False) # to upgrade db

# Таблица логов
class Log(db.Model):
    __tablename__ = 'logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    action = db.Column(db.String(255), nullable=False)
    target_id = db.Column(db.Integer)
    target_type = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=db.func.now())
