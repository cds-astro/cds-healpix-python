
See the [maturin web page](https://github.com/PyO3/maturin).

Install maturin using `pip` (or `pip3`):
```bash
pip install maturin
```

Build the `.so`:
```
maturin build --release
```

To perform development tests with `maturin develop`, 
use [python virtual env](https://docs.python.org/3/library/venv.html),
see also [venv tuto](https://docs.python.org/3/tutorial/venv.html):
```bash
# Install virtualenv (venv)
pip install virtualenv
# Create venv cdshealpix_tests
virtualenv -p=python3 cdshealpix_tests
# Activate the venv
source cdshealpix_tests/bin/activate
# Do your stuff, e.g:
pip install -r requirements-dev.txt
maturin develop
...
# Exit the venv
deactivate
```

To remove the virtual env, see [this post](https://stackoverflow.com/questions/11005457/how-do-i-remove-delete-a-virtualenv)
```bash
source cdshealpix_tests/bin/activate
pip freeze > requirements-dev.txt
pip uninstall -r requirements-dev.txt -y
deactivate
rm -r cdshealpix_tests/
```

