# rumor crawlers

Houly crawls CDC, FDA, MYGOPAN, MOFA rumor contents, and put them to rumor-ddb-table: <stage>-rumor_source.

## Development

### Load Config Files For Dev Local Environment
config files source: s3://<CONFIG_PATH>/<stage>/

```shell
$ > make config
```

### Build docker image

```shell
$ > make build
```

### Launch service

```shell
$ > make launch
```

### Run app
Make sure you have exported AWS access key setting via STS before run this command

```shell
$ > make run
```

### Launch Develop Environment

```shell
$ > make devenv
```

## Quality Assurance

### Unit Testing (TBD)

```shell
$ > make test
```

## Add / Update Package

### Add new package

```shell
$ > make devenv
(In devenv)
# pipenv install <NEW-PACKAGE>
```

### Update package

```shell
$ > make update

