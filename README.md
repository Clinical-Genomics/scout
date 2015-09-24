![Release 1.0](artwork/releases/release-1-0.jpg)

# Scout [![Build Status][travis-img]][travis-url]
**Analyze VCFs quicker and easier.**

Scout makes you life easier by letting you visualize mutiple VCFs in the browser. You can quickly triage variants in search of those sneeky disease causing mutations. Scout also connects your team by linking user comments to cases and variants. The project is completely open source.

![Case page demo](/artwork/scout-variant.png)


## Installation
Scout will ship as a regular Python package through ``pip`` but until then you can install it through GitHub.

```bash
$ mkvirtualenv scout && workon scout
$ pip install git+https://github.com/Clinical-Genomics/scout.git
```

You also need to install MongoDB and run it as a background process.

## Quickstart
Run the following commands to bootstrap your development environment. Make sure you've installed Ansible and Vagrant.

```bash
$ ansible-galaxy install robinandeer.miniconda
$ ansible-galaxy install nodesource.node
$ ansible-galaxy install Stouts.mongodb
$ vagrant up
# Mac specific
$ open http://localhost:5023/
```

When you have the instance folder in place you can start Flask like so:

```bash
$ python manage.py -c "$(pwd)/instance/scout.cfg" runserver
Running on http://localhost:5000...
```


## Features
Scout is implemented in Python and uses the Flask web framework. Data is stored in a MongoDB database. Login is handled through Google OAuth. The raw input to Scout is any valid VCF file with one or more samples.


## About
Scout is developed at SciLifeLab [Clinical Genomics](https://github.com/Clinical-Genomics) in close collaboration with CMMS at Karolinska Institute.


## Contributors
- Robin Andeer ([robinandeer](https://github.com/robinandeer))
- Måns Magnusson ([moonso](https://github.com/moonso))
- Henrik Stranneheim ([henrikstranneheim](https://github.com/henrikstranneheim))
- Mats Dahlberg ([MatsDahlberg](https://github.com/MatsDahlberg))


## License
MIT. See the [LICENSE](LICENSE) file for more details.


## Contributing
Anyone can help make this project better - read [CONTRIBUTION](CONTRIBUTION.md)
to get started!


[travis-img]: https://img.shields.io/travis/Clinical-Genomics/scout/develop.svg?style=flat
[travis-url]: https://travis-ci.org/Clinical-Genomics/scout
