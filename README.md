# clevmetro-nfd
Cleveland Metroparks - Natural Features Database


# Quickstart

Install Python requirements using a virtual environment:
```shell
# create a Python virtual env to install dependences
mkdir venvs ; cd venvs
virtualenv metroparksnfd
# activate the virtual env
source metroparksnfd/bin/activate
# install requirements
pip install -r ../clevmetro-nfd/nfdapi/requirements.txt
```

Create database schema:

```shell
cd clevmetro-nfd/nfdapi
$ ./manage.py migrate
$ ./manage.py createinitialrevisions
```

Optional: Initialize some dictionary tables (Using `./manage.py shell`. Warning: it will delete existing dict tables):
```python
from core import initmodel as i
i.init_model()
```
Optional: Insert some test data (Warning: it will delete existing occurrences):
```python
from core import initmodel as i
i.insert_test_data()
```

