from marshmallow import fields, validate

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