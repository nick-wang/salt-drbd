Use for salt development.

# Usually for salt unit test
eg:
  python3 tests/runtests.py -n unit.modules.test_drbd

# For code climate:
eg:
  radon cc -s <python file>
eg:
  # refer to .travis.xml of salt-shaptools
  # run ./test/run.sh for test coverage report

# For pylint:
eg:
  pylint --rcfile=.testing.pylintrc --disable=I,W1307,C0411,C0413,W8410,str-format-in-logging tests/unit/modules/test_drbd.py


# In real:

## ./test/run.sh in repo salt-shaptools
python3 tests/runtests.py -n unit.modules.test_drbd -n unit.states.test_drbd
python2 tests/runtests.py -n unit.modules.test_drbd -n unit.states.test_drbd

## run after copy files
pylint --rcfile=.testing.pylintrc --disable=I,W1307,C0411,C0413,W8410,str-format-in-logging salt/modules/drbd.py salt/states/drbd.py tests/unit/modules/test_drbd.py tests/unit/states/test_drbd.py

Note:
===================================
  to install necessary library/dependencies
  using:
   pip install -r requirements.txt
  Or check with .travis.yml in salt-shaptools repo:
```
    - stage: test
      python: 2.7
      install:
          - pip install --upgrade pip
          - pip install --upgrade pytest
          - pip install pyzmq PyYAML pycrypto msgpack-python jinja2 psutil futures tornado pytest-salt mock pytest-cov enum34
          - git clone --depth=50 https://github.com/openSUSE/salt ../salt
          - rm ../salt/tests/conftest.py
          - git clone --depth=50 https://github.com/SUSE/shaptools.git ../shaptools
          - pip install ../salt
          - pip install ../shaptools
      script:
          - ./tests/run.sh

    - stage: test
      python: 3.6
      install:
          - pip install --upgrade pip
          - pip install --upgrade pytest
          - pip install pyzmq PyYAML pycrypto msgpack-python jinja2 psutil futures tornado pytest-salt mock pytest-cov enum34
          - git clone --depth=50 https://github.com/openSUSE/salt ../salt
          - rm ../salt/tests/conftest.py
          - git clone --depth=50 https://github.com/SUSE/shaptools.git ../shaptools
          - pip install ../salt
          - pip install ../shaptools
```
