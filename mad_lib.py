import parse_activities as pa
import random
import re

first_gerund = re.compile(r'^\w+ing\b')
activities = pa.activities
persons = ['Jack', 'Jill', 'Rocky', 'Dale', 'Urkel', 'Sharona', 'Mr. Noodle', 'Dr. Evil']
places = ['home', 'work', 'the gym', 'the pool', 'the coffeeshop', "your mom's house"]
whens = ['earlier', 'today', 'yesterday', 'a while back', 'last night', 'the other day', 'long ago', 'in his/her prime', 'back when it meant something']

activity = random.choice(list(activities.values()))
lib = {'person': random.choice(persons),
       'verb' : activity.lower(),
       'place': random.choice(places),
       'when' : random.choice(whens),
       }
starts_with_gerund = re.match(first_gerund, lib['verb'])
if starts_with_gerund:
    lib['verb'] = 'was really enjoying ' + lib['verb']
else:
    lib['verb'] = 'did a bit of ' + lib['verb']
print('{person} {verb} at {place} {when}.'.format(**lib))
