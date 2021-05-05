# Analysis

## Requiremen Elicitation

### Proposed System 

During this project, we will implement a framework that is intended to simplify network measurements in large scale scenarios. The framework should offer the functionality to define an arbitrary topology in a structured way, that can be instantiated on a P4 capable switch.

### Functional Requirements
- The system can instantiate multiple virtual routers on one physical P4 device.
- Each virtual router can be configured individually, including 
   - the number of ports and corresponding Address spaces
   - the links to other virtual router or hosts
- A mapping from logical ports on a virtual router to physical port on the P4 device can be defined.
- A topology can be configured by the user. A Topology includes optional definition of network ranges.
- The system allows to generate Topologies based on predefined structures e.g.
   - Tree with one router and two hosts 
   - Tree with two routers connected to each other and one host connected to each router. 
   - A balanced tree 3 layers deep, each router is connected to three router below. Each edge router is then connected to two hosts.
   - A n-hop chain of virtual routers with one host on each end
- Both IPv4 and IPv6 have to be supported.
- The system implements static routing. The system creates routing tables derived from the topology information.
- The following metrics will be measured with the system using load generators on the connected hosts.
   - Throughput
   - Latency
   - Loss-rate
- A configuration can be deployed directly to a P4 device
- The system creates a visualisation of the configured topology.
- [Optional] The system allows to create virtual links between virtual switches.
- [Optional] The system verifies if the physical wiring corresponds to the desired topology.

### Non-Functional Requirements
#### Usability 
- The CLI is well structured and can be understood easily. 
- All commands are documented and have expressive help texts available directly in the CLI.

#### Supportability 
- The system has to be extensible. 
  - New deployment targets may be added in the future. 
  - New topology types may be added 
  - P4 implementation may be adapted and should require minimal changes to the deployment system

#### Implementation 
- The network topology has to be represented by a P4_16 capable switch. Namely 
   - BMv2 
   - Tofino
- All the other components have to be implemented using python 3.

#### Interface 
- The system has to be configurable via a Command Line Interface (CLI). All possible network configurations have to be represented as text-files.

## Analysis Object Model 
![AOM](img/AOM.png)


