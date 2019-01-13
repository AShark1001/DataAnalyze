from flask_wtf import Form, FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import TextField, PasswordField, FileField, MultipleFileField
from wtforms import validators


class SelectForm(FlaskForm):
    data_file = MultipleFileField('Data Files')

    # FileField('Data Files', validators=[
    #    FileRequired(),
    #    FileAllowed(['csv'], 'CSV files only!')])

    def validate(self):
        check_validate = super(SelectForm, self).validate()

        # if our validators do not pass
        if not check_validate:
            return False

        return True


from .models import User


class LoginForm(Form):
    username = TextField(u'Username', validators=[validators.required()])
    password = PasswordField(u'Password', validators=[validators.optional()])

    def validate(self):
        check_validate = super(LoginForm, self).validate()

        # if our validators do not pass
        if not check_validate:
            return False

        # Does our the exist
        user = User.query.filter_by(username=self.username.data).first()
        if not user:
            self.username.errors.append('Invalid username or password')
            return False

        # Do the passwords match
        if not user.check_password(self.password.data):
            self.username.errors.append('Invalid username or password')
            return False

        return True
