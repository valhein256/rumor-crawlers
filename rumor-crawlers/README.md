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

### Launch Develop Environment

```shell
$ > make devenv
```

### Run app

Make sure you have exported AWS access key setting via STS before run following command

#### CDC

Link: https://www.cdc.gov.tw/Bulletin/List/xpcl4W7tToptl-lFMjle2Q
The Oldest Rumor Date: 2016-05-16
To see more detail about cdc, Login local dev environment

```shell
# make devnev
<devenv> # python app/cdc.py -h
usage: cdc.py [-h] [-d DATE] [-u | --update | --no-update]

optional arguments:
  -h, --help            show this help message and exit
  -d DATE, --date DATE  To crawler content from date
  -u, --update, --no-update
                        To update rumor content by re-crawlering (default: False)
```

##### Run cdc job:
To update rumor content by re-crawlering

```shell
# make run app=app/cdc.py date=2015-01-01 update=true
```

To crawler content from date

```shell
# make run app=app/cdc.py date=2015-01-01
```

#### FDA

Link: https://www.fda.gov.tw/TC/news.aspx?cid=5049
The Oldest Rumor Date: 2015-04-27
To see more detail about fda, Login local dev environment

```shell
# make devnev
<devenv> # python app/fda.py -h
usage: fda.py [-h] [-d DATE] [-u | --update | --no-update]

optional arguments:
  -h, --help            show this help message and exit
  -d DATE, --date DATE  To crawler content from date
  -u, --update, --no-update
                        To update rumor content by re-crawlering (default: False)
```

##### Run fda job:
To update rumor content by re-crawlering

```shell
# make run app=app/fda.py date=2015-01-01 update=true
```

To crawler content from date

```shell
# make run app=app/fda.py date=2015-01-01
```

#### MOFA

Link: https://www.mofa.gov.tw/News.aspx?n=1163&sms=214
The Oldest Rumor Date: 2016-06-03
To see more detail about mofa, Login local dev environment

```shell
# make devnev
<devenv> # python app/mofa.py -h
usage: mofa.py [-h] [-d DATE] [-u | --update | --no-update]

optional arguments:
  -h, --help            show this help message and exit
  -d DATE, --date DATE  To crawler content from date
  -u, --update, --no-update
                        To update rumor content by re-crawlering (default: False)
```

##### Run mofa job:
To update rumor content by re-crawlering

```shell
# make run app=app/mofa.py date=2015-01-01 update=true
```

To crawler content from date

```shell
# make run app=app/mofa.py date=2015-01-01
```

#### TFC

Link: https://tfc-taiwan.org.tw/articles/report
The Oldest Rumor Date: 2018-07-31
To see more detail about tfc, Login local dev environment

```shell
# make devnev
<devenv> # python app/tfc.py -h
usage: tfc.py [-h] [-d DATE] [-u | --update | --no-update]

optional arguments:
  -h, --help            show this help message and exit
  -d DATE, --date DATE  To crawler content from date
  -u, --update, --no-update
                        To update rumor content by re-crawlering (default: False)
```

##### Run tfc job:
To update rumor content by re-crawlering

```shell
# make run app=app/tfc.py date=2015-01-01 update=true
```

To crawler content from date

```shell
# make run app=app/tfc.py date=2015-01-01
```

#### MYGOPEN

Link: https://www.mygopen.com/
The Oldest Rumor Date: 2015-11-25
To see more detail about mygopen, Login local dev environment

```shell
# make devnev
<devenv> # python app/mygopen.py -h
usage: mygopen.py [-h] [-d DATE] [-u | --update | --no-update]

optional arguments:
  -h, --help            show this help message and exit
  -d DATE, --date DATE  To crawler content from date
  -u, --update, --no-update
                        To update rumor content by re-crawlering (default: False)
```

##### Run mygopen job:
To update rumor content by re-crawlering

```shell
# make run app=app/mygopen.py date=2015-01-01 update=true
```

To crawler content from date

```shell
# make run app=app/mygopen.py date=2015-01-01
```

## Quality Assurance

### Unit Testing

```shell
$ > make test
```

## Add / Update Package

### Add new package

```shell
$ > make devenv
(In devenv)
# poetry add <NEW-PACKAGE>
```

### Update package

```shell
$ > make update


