from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField, DecimalField
from wtforms.validators import DataRequired, InputRequired, NumberRange


class TrackProductForm(FlaskForm):
    product_url = StringField("Product URL", validators=[DataRequired()])
    target_price = DecimalField(
        "Target Price",
        validators=[InputRequired(), NumberRange(min=0, message="Target price must be a positive number.")],
        places=2,
    )
    submit = SubmitField("Start Tracking")


class ItemDetailsForm(FlaskForm):
    alert_price = DecimalField(
        "Alert Price",
        validators=[InputRequired(), NumberRange(min=0, message="Alert price must be a positive number.")],
        places=2,
    )
    submit = SubmitField("Save")


class DeleteItemForm(FlaskForm):
    item_id = HiddenField("Item ID", validators=[DataRequired()])
    delete_submit = SubmitField("Stop Tracking")
