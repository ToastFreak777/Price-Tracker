from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class TrackProductForm(FlaskForm):
    product_url = StringField("Product URL", validators=[DataRequired()])
    submit = SubmitField("Start Tracking")


class ItemDetailsForm(FlaskForm):
    alert_price = StringField("Alert Price", validators=[DataRequired()])
    submit = SubmitField("Save")
