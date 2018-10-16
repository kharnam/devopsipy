## DevOpsiPy Project

#### Abstract  
Project aims to create generic, DevOps oriented framework in Python 3

---

#### Usage

Copy module to your project directory:
```bash
git clone git@github.com:kharnam/devopsipy.git
```

In your modules:  
_**logger.py**_  
_main.py_ module:
```python
from devopsipy import logger

log = logger.set_logger('MyCoolProject')
log.info('The first message from MyCoolProject Main module')

```

_test.py_ module:
```python
# Close to module top
import logging
log = logging.getLogger(__name__)
log.info('Logging from MyCoolProject Test module')

```


_**host_base.py**_  
```python
from devopsipy.host_base import HostBase

l_host = HostBase('localhost')
r_host = HostBase('my_remote_machine.example.com', ssh_user='user', ssh_key_file='~/.ssh/id_rsa')

l_host.run('uptime', print_pstate=True)
r_host.run(['mkdir test', 'cd test', 'ls -l'], print_stdout=True)

```

---

#### Current functionality

_**logger.py**_

Fully functional pre-configured logging facility

* 3 logger formatters: 
    * default
    * detailed
    * silent

* 4 logger handlers: 
    * console -- colorized stream handler
    * info_file_handler -- level INFO, separate log file with rotation
    * error_file_handler -- level ERROR, separate log file with rotation
    * debug_file_handler -- level DEBUG, separate log file with rotation
* Creates separate folder under '/tmp/logs' on every init and creates symlinks to the latest log files
```bash
/tmp/logs# ls -ltr
lrwxr-xr-x  1 kharnam  wheel    76B 15 Oct 22:17 latest.info -> /tmp/logs/HostBaseTest_20181015_221711/HostBaseTest_20181015_221711.info.log
lrwxr-xr-x  1 kharnam  wheel    77B 15 Oct 22:17 latest.error -> /tmp/logs/HostBaseTest_20181015_221711/HostBaseTest_20181015_221711.error.log
lrwxr-xr-x  1 kharnam  wheel    77B 15 Oct 22:17 latest.debug -> /tmp/logs/HostBaseTest_20181015_221711/HostBaseTest_20181015_221711.debug.log
drwxr-xr-x  5 kharnam  wheel   160B 15 Oct 22:17 HostBaseTest_20181015_221711

/tmp/logs# ll HostBaseTest_20181015_221711
-rw-r--r--  1 kharnam  wheel    12K 15 Oct 22:17 HostBaseTest_20181015_221711.debug.log
-rw-r--r--  1 kharnam  wheel   2.6K 15 Oct 22:17 HostBaseTest_20181015_221711.info.log
-rw-r--r--  1 kharnam  wheel     0B 15 Oct 22:17 HostBaseTest_20181015_221711.error.log
```

---
_**host_base.py**_

Module represents generic Linux host functionality
* Class HostBase
* HostBase State
* HostBase State Functions
* HostBase State Actions

---
_**utils.py**_

Module provides generic auxiliary functionality, like the folloowing:
* create_symlinks_to_files()
* yaml_to_dic()
* create_dir()
* is_dir_exist()
* save_data_to_file()
* load_data_from_file()
* get_caller()
* get_random_string()
* set_env_vars()
* replace_string_in_file()