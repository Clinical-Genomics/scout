## Setup Scout

### Demo

Once installed, you can setup Scout by running a few commands using the included command line interface. Given you have a MongoDB server listening on the default port (27017), this is how you would setup a fully working Scout demo:

```bash
scout setup demo
```

This will setup an instance of scout with a database called `scout-demo`. Now run

```bash
scout --demo serve
```
And play around with the interface. A user has been created with email clark.kent@mail.com so use that adress to get access

### Initialize scout

To initialize a working instance with all genes, diseases etc run

```bash
scout setup database
```

for more info, run `scout --help`

> If you intent to use authentication, make sure you are using a Google email!

