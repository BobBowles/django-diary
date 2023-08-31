# Overrides for localisation defaults go here.

# the django default does not allow time with meridian
TIME_INPUT_FORMATS = [
    '%H:%M:%S',
    '%H:%M',
    '%I %p',
    '%I:%M %p',
    '%I:%M%p',
    '%H:%M:%S.%f',
]
