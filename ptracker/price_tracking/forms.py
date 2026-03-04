from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField
from wtforms.validators import DataRequired


class TrackProductForm(FlaskForm):
    product_url = StringField("Product URL", validators=[DataRequired()])
    submit = SubmitField("Start Tracking")


class ItemDetailsForm(FlaskForm):
    alert_price = StringField("Alert Price", validators=[DataRequired()])
    submit = SubmitField("Save")


class DeleteItemForm(FlaskForm):
    item_id = HiddenField("Item ID", validators=[DataRequired()])
    delete_submit = SubmitField("Stop Tracking")
