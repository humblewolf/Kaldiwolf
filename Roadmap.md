To do's:

1. Redis

> I think seperate PySimpleQueue(PSQ) objects are not required.
> Queues inside  a PSQ shall be disposed off once used.
> In general tuning of redis stuff

2. Pyro

> Pyro cns does not entertain old nodes once restarted.
> Misc tuning

3. Send executing decode script and kaldi-home path from server to nodes.