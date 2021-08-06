class Nullable:
    def __init__(self, type):
        self.type = type

    def __iter__(self):
        return self.type.__iter__()

    def __getitem__(self, item):
        return self.type.__getitem__(item)

    def __str__(self):
        return f'Nullable({type(self.type)})'


def print_wrong_type(key: str, type_is: str, type_should: str):
    print(f"Wrong Type for {key}: {type_is} instead of {type_should}")


def validate(schema, data, parent_key='root'):
    if data is None:
        if '?' not in schema and not isinstance(schema, Nullable):
            print_wrong_type(parent_key, 'None', schema)
            return False
        else:
            return True
    if isinstance(data, str):
        if "String" not in schema:
            print_wrong_type(parent_key, 'String', schema)
            return False
        else:
            return True
    if isinstance(data, int):
        if "Int" not in schema:
            print_wrong_type(parent_key, 'Int', schema)
            return False
        else:
            return True
    if isinstance(data, dict):
        ret = True
        for key, value in data.items():
            if not validate(schema[key], value, f'{parent_key}/{key}'):
                ret = False
        return ret
    if isinstance(data, list):
        ret = True
        for i in range(len(data)):
            if not validate(schema[0], data[i], f'{parent_key}/{i}'):
                ret = False
        return ret


Person = {
    "name": "String",
    "age": '?Int',
    "address_history": [{
        "line1": "String",
        "line2": "String",
        "postcode": "String",
    }],
}

person = {
    'name': 'John',
    'age': 25,
    'address_history': [
        {
            "line1": "10 Downing Street",
            "line2": "sdfsdf",
            "postcode": "...",
        }
    ],
}

assert validate(Person, person) == True

person = {
    'name': 'John',
    'age': 25,
    'address_history': [
        {
            "line1": "10 Downing Street",
            "line2": "sdfsdf",
            "postcode": "...",
        },
        {
            "line1": "20 Downing Street",
            "line2": "other line",
            "postcode": "5874",
        }
    ],
}

assert validate(Person, person) == True

person = {
    'name': 'John',
    'age': None,
    'address_history': [
        {
            "line1": "10 Downing Street",
            "line2": "sdfsdf",
            "postcode": "...",
        }
    ],
}

assert validate(Person, person) == True

person = {
    'name': 'John',
    'age': 'twenty',
    'address_history': [
        {
            "line1": "10 Downing Street",
            "line2": "sdfsdf",
            "postcode": "...",
        }
    ],
}

assert validate(Person, person) == False

person = {
    'name': 1337,
    'age': 5,
    'address_history': [
        {
            "line1": "10 Downing Street",
            "line2": "sdfsdf",
            "postcode": "...",
        }
    ],
}

assert validate(Person, person) == False

person = {
    'name': 'John',
    'age': 25,
    'address_history': [
        {
            "line1": "10 Downing Street",
            "line2": "sdfsdf",
            "postcode": "...",
        },
        {
            "line1": "20 Downing Street",
            "line2": "other line",
            "postcode": 5874,
        }
    ],
}

assert validate(Person, person) == False

Schema = Nullable({'x': 'Int', 'y': 'Int'})
data = None

assert validate(Schema, data) == True

data = {'x': 5, 'y': 8}

assert validate(Schema, data) == True

data = 8

assert validate(Schema, data) == False

Schema = {'x': 'String'}

data = 8

assert validate(Schema, data) == False