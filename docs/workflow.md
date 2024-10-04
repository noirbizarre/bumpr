# Workflow

When you execute Bump'R it will follow the following workflow:

1. clean
2. test
3. bump
4. publish
5. prepare

If you have been using Maven, it's inspired by the Maven Release Plugin.

## Clean phase

Optionnal phase that simply execute the commands provided by the `clean` configuration parameter.

## Test phase

Optionnal phase that simply execute the commands provided by the `tests` configuration parameter.

## Bump phase

This is the main phase in which Bump'R will:

1. Compute replacements
2. Execute the bump phase for each hook
3. Bump replacement in version file and extra files
4. Commit the changes if a VCS is configured with `commit=True`
5. Tag the previously created commit if `tag=True`

## Publish phase

Optionnal phase that simply execute the commands provided by the `publish` configuration parameter.

Most of the time for Python project, you will want to execute:

```bash
python setup.py sdist register upload
```

## Prepare phase

This is the second main phase in which Bump'R will:

1. Compute replacements
2. Execute the prepare phase for each hook
3. Bump replacement in version file and extra files
4. Commit the changes if a VCS is configured with `commit=True`
