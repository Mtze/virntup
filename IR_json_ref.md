Dict Layout 
```
{
    "vRouter": {
        "1": {
            "name" : "string", 
            "uplink_network" : "10.0.0.0/24",
            "neighbour": [
                [0,"5"]  # List - Port, Neigh ID
            ],
            "routing_table" : [
                [0,"10.0.1.0/24"],
                [1,"10.0.2.0/24"]
            ] 
        }
    }
    "Host" : {
        "5" :{
            "name" : "string", 
            "uplink_network" : "10.0.5.0/24", 
        }
    }
}
```
