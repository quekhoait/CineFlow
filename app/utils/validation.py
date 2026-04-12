from datetime import datetime

from cloudinary.uploader import upload
from marshmallow import fields, validate, ValidationError


class PasswordField(fields.String):
    def __init__(self, *args, **kwargs):
        length_val = validate.Length(min=6, max=32, error='Password must be between 6 and 32 characters long.')
        regex_val = validate.Regexp(
            regex=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$",
            error='The password must contain at least one uppercase letter, one lowercase letter, one number, and one special character.'
        )

        validators = kwargs.get('validate', [])
        if not isinstance(validators, list):
            validators = [validators]
        validators.extend([length_val, regex_val])
        kwargs['validate'] = validators
        super().__init__(*args, **kwargs)

class PhoneNumberField(fields.String):
    def __init__(self, *args, **kwargs):
        regex_val = validate.Regexp(
            regex=r"^\+?[0-9]{7,15}$",
            error="The phone number is not in the correct format."
        )
        validators = kwargs.get('validate', [])
        if not isinstance(validators, list):
            validators = [validators]
        validators.extend([regex_val])
        kwargs['validate'] = validators
        super().__init__(*args, **kwargs)




class CloudinaryImageField(fields.String):
    def __init__(self, folder="general", **kwargs):
        self.folder = folder
        super().__init__(**kwargs)

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None: return value
        if isinstance(value, str) and value.startswith('http'):
            return value

        try:
            image = upload(value, folder=self.folder, resource_type='auto')
            return image.get('secure_url')
        except Exception as e:
            raise ValidationError(str(e))