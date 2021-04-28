# VirNTUP_4

Virtualized Network Topologies using P_4 - IDP at I8 

## What is virntup?

## Motivation 

## Usage

### Install 
- Clone the repository 
- Crate an virual env and activate it
```bash
virtualenv venv
. venv/bin/activate
```
- Install dependencies 
```
pip3 install -r requirements.txt
```


### Supplemental Files

#### `env.json`
Virntup needs an `env.json` containing the target environment to which a topology should be deployed to. 
The `env.json` contains a list of links to hosts and a list of physical loops between ports. An `env.json` could look similar to this: 

```json 
{
    "host_links" : [
        ["h1", 1],
        ["h2", 2]
    ],

    "links": [
        [3, 4]
    ]
}
```
The `testbed-env-setup` repository contains some preconfigured env files to use, as well as further guidance how to write your own. 

#### `P4.info` and `virntup.bin`
Virntup assumes that the P4 target runs/is able to run the `virntup.p4` program. If the target already runs virntup, these files are not necessary to deploy a topology to the target. 
If you prefer to use virntup to deploy the p4 program, you have to provide both the `p4.info` as well as the `virntup.bin` (which was modified to work with P4Runtime, see [here](https://github.com/p4lang/p4runtime-shell#target-specific-support).

The P4 implementation of virntup can be found in the `vrintup-p4-implementation` repository. 


#### Optional `conf.json`
To unclutter the CLI virntup can be fully configured using a `conf.json` containing all the desired options. A `conf.json` example called `test-config.json` can be found in the repository. 

If CLI parameters are provided additionally to the `conf.json` the CLI parameters will be preferred. 

### Generated Artefacts 

- `ir.json`
- `host.json`
- `dot_representation.dot`



## Development 

### Components

#### Topology 

#### Topology Generator

#### Topology Controller

#### Target Configurator

#### CLI

### P4 Program 
