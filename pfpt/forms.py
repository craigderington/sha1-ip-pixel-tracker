from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class AddCampaignForm(FlaskForm):
    job_number = StringField('job_number', validators=[DataRequired()])
    client_id = StringField('client_id', validators=[DataRequired()])
    campaign = StringField('campaign', validators=[DataRequired()])
