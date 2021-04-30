import pytest
import re

test_data = [("10FA0E00", {'field1': 'Low',
                             'field2': '00',
                             'field3': '01',
                             'field4': '00',
                             'field5': '00',
                             'field6': '01',
                             'field7': '00',
                             'field8': 'Very High',
                             'field9': '00',
                             'field10': '00'}),
            ]

#Format settings - array [sett_byte1 as dict {bit: [size, 'field_name']}, sett_byte2, sett_byte3, sett_byte4]
device_settings = [{0: [3, 'field1'], 
                    3: [1, 'field2'],  
                    4: [1, 'field3'], 
                    5: [3, 'field4']}, 
                   {0: [1, 'field5'],  
                    1: [1, 'field6'], 
                    2: [1, 'field7'],  
                    3: [3, 'field8'], 
                   },
                   {0: [1, 'field9'], 
                    5: [1, 'field10']
                   },
                   {}
                  ]

field1 = {'0': 'Low',
          '1': 'reserved',
          '2': 'reserved',
          '3': 'reserved',
          '4': 'Medium', 
          '5': 'reserved',
          '6': 'reserved',
          '7': 'High',  
          }
field4 = {'0': '00', 
          '1': '10',
          '2': '20',
          '3': '30',
          '4': '40',
          '5': '50',
          '6': '60',
          '7': '70',
          }
field8 = {'0': 'Very Low',
          '1': 'reserved',
          '2': 'Low',
          '3': 'reserved',
          '4': 'Medium',
          '5': 'High',
          '6': 'reserved',
          '7': 'Very High',
          }


def get_data_from_payload(payload, settings=device_settings):
    parsed_data = {}
    pattern = r"[^a-fA-F0-9_]"
    if payload == '':
        raise ValueError('No data')
    elif type(payload) != str:
        try:
            payload = str(payload)
        except:
            raise ValueError('Bad data')
    elif len(payload) < (len(settings)*2):
        raise ValueError('Bad data')
    elif  len(re.findall(pattern, payload)) > 0:
        raise ValueError('Bad data')
    

    fields = {'1': field1, '4': field4, '8': field8}
    for i in range(0, len(settings)*2, 2):
        byte = int(payload[i:i+2], 16)
        for start, (span, n) in settings[i >> 1].items():
            m = (byte & (((1 << span) - 1) << start)) >> start
            parsed_data[f"{n}"] = fields[n[5:]][str(m)] if n[5:] in fields else f"{m:02d}"
    return parsed_data


print(get_data_from_payload('10FA0E00'))


def test_positive():
  payload = '10FA0E00'
  correct_data = {'field1': 'Low',
                  'field2': '00',
                  'field3': '01',
                  'field4': '00',
                  'field5': '00',
                  'field6': '01',
                  'field7': '00',
                  'field8': 'Very High',
                  'field9': '00',
                  'field10': '00'}
  assert get_data_from_payload(payload) == correct_data


def test_negative():
    payload = '10000E00'
    data = {'field1': 'Low',
                    'field2': '00',
                    'field3': '01',
                    'field4': '00',
                    'field5': '00',
                    'field6': '01',
                    'field7': '00',
                    'field8': 'Very High',
                    'field9': '00',
                    'field10': '00'}
    assert get_data_from_payload(payload) != data


def test_another_settings():
    payload = '10FA0E03'
    correct_data = {'field1': 'Low',
                    'field2': '00',
                    'field3': '01',
                    'field4': '00',
                    'field5': '00',
                    'field6': '01',
                    'field7': '00',
                    'field8': 'Very High',
                    'field9': '00',
                    'field10': '00',
                    'field11': '01',
                    'field12': '01'}
    another_settings = [{0: [3, 'field1'], 
                    3: [1, 'field2'],  
                    4: [1, 'field3'], 
                    5: [3, 'field4']}, 
                   {0: [1, 'field5'],  
                    1: [1, 'field6'], 
                    2: [1, 'field7'],  
                    3: [3, 'field8'], 
                   },
                   {0: [1, 'field9'], 
                    5: [1, 'field10']
                   },
                   {0: [1, 'field11'], 
                    1: [1, 'field12']}
                  ]

    assert get_data_from_payload(payload, another_settings) == correct_data


def test_small_char():
  payload = '10Fa0E03'
  correct_data = {'field1': 'Low',
                  'field2': '00',
                  'field3': '01',
                  'field4': '00',
                  'field5': '00',
                  'field6': '01',
                  'field7': '00',
                  'field8': 'Very High',
                  'field9': '00',
                  'field10': '00'}
  assert get_data_from_payload(payload) == correct_data

def test_no_data():
  payload = ''
  with pytest.raises(ValueError, match='No data'):
      get_data_from_payload(payload)


def test_bad_data():
  payload = '10F'
  with pytest.raises(ValueError, match='Bad data'):
      get_data_from_payload(payload)

def test_bad_data_2():
  payload = '10F/*E03'
  with pytest.raises(ValueError, match='Bad data'):
      get_data_from_payload(payload)


def test_integer_data():
  payload = 1011100  
  correct_data = {'field1': 'Low',
                  'field2': '00',
                  'field3': '01',
                  'field4': '00',
                  'field5': '01',
                  'field6': '00',
                  'field7': '00',
                  'field8': 'Low',
                  'field9': '00',
                  'field10': '00'}
  assert get_data_from_payload(payload) == correct_data

