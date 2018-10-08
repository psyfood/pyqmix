## Make a release
- Draft a new release on Github
- Run `git fetch` to fetch the created version tag

## Ensure `twine` is installed
```
conda install twine
```

## Build the package
```
python setup.py sdist bdist_wheel
```

## Do a test upload
```
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```
Check if everything seems to have gone smoothly: visit https://test.pypi.org/project/pyqmix/

## Publish package on PyPI
```
twine upload dist/*
```
