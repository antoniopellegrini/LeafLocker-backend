from marshmallow import ValidationError
from config.exceptions import ValidationException
from datetime import datetime

validate_email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

def parse_query_params(schema,request, error_message = None):
    try:
        if request.args:
            return schema.load(request.args)
        else:
            raise(ValidationException(message='request args required'))
    except ValidationError as e:
        if error_message:
            raise ValidationException(message=error_message,errors=e.normalized_messages())
        else:
            raise ValidationException(errors=e.normalized_messages())

def parse_json_body(schema,request, error_message = None):
    try:
        if request.data:
            return schema.loads(request.data)
        else:
            raise(ValidationException(message='request body required'))
    except ValidationError as e:
        if error_message:
            raise ValidationException(message=error_message,errors=e.normalized_messages())
        else:
            raise ValidationException(errors=e.normalized_messages())
        
def milliseconds_since_epoch():
    date = datetime.utcnow() - datetime(1970, 1, 1)
    return round(date.total_seconds()*1000)