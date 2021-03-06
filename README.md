# MWLinkResolve

This tool fetches a MediaWiki wiki's redirect pages, and using that, compiles a list of all pages linking to redirect pages. It then edits those pages to instead link to the target of the redirect.

It doesn't resolve links to (redirects of) Files and links constructed with a Template. (Although it's not limited to main name-space pages, so if a Template hard-codes a link, it will revise that.)

Note, that Wikipedia guidelines discourage the "correction" of links pointing to redirect pages. This would cause a disproportionate amount of workload compared to what serving the redirect page does. It is theorized, however, that search-engine crawler budgets are chipped away at by 3xx HTTP responses, and so, resolving these links might mean improved visibility.

## Installation

A Windows executable release is available [here](https://github.com/KovacsGG/mwlinkresolve/releases)

It is recommended to use the source scripts, if your system provides a python interpreter. Install `mwclient` and `mwparserfromhell` with pip.

## Usage

`python3 mwlinkresolve.py [OPTIONS]`

`./mwlinkresolve.exe [OPTIONS]`

#### `--site`, `-s`

To select the target wiki and provide the API URL. Either a fully qualified domain name along with the path of the API, or simply the subdomain of a fandom.com wiki. In the former case, it should end with `api.php`, such as `en.wikipedia.org/w/api.php`

#### `--user`, `-u`

The botpassword credentials of the wiki's user, necessary to edit it. It should have permissions for high-volume editing, and to set edits as bot edits. Usually in the form of UserName@BotpasswordName

#### `--password`, `-p`

The botpassword's token.

#### `--dry`

If set, all edits will be skipped.

#### `--config`, `-c`

Path to the configuration file. If no valid (or an incomplete) configuration file exists at the destination, the missing options of `-s`, `-u` and `-p` must be provided. Defaults to `./mwlinkresolve.conf`. Any such configurations are overridden by the command line options `-s`, `-u` and `-p`

#### `--help`

### Configuration

A sample configuration file might look like this:

```
[Config]
Site = oxygennotincluded
User = User@BotName
Password = ge91BotToken2sw45pws5
```

In this example, `oxygennotincluded` will be taken to mean `oxygennotincluded.fandom.com/api.php`. Strings ending with `api.php` are taken literally.
