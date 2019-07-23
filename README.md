# Adaptive Scheduler
Runs Gurobi solver to schedule the network of telescopes with requests from the observation portal.
Scheduled observations are placed in the Pond at the end of each run.
The scheduler is meant to run continuously, with each round of scheduling consisting of scheduling 
all the ToO requests followed by scheduling all of the normal requests. 

Currently, the scheduler runs on scheduler1.lco.gtn as a service, using the init.d file in this project.
Eventually, it will be run via docker using the container generated by the Dockerfile of this project.

### Setup instructions (scheduler1)
#### First Time
First, clone this repository into /lco/. Create a virtualenv as /lco/env/scheduler and pip install the requirements from
this project into there. Copy the init.d script from /lco/adaptive_scheduler/init.d/adaptive_scheduler.sh to 
/etc/init.d/. Open up the copied init.d script and make sure the environment variables have the correct hosts/paths and 
the startup options for the scheduler are correct. 

Look in the production gurobi license at /lco/adaptive_scheduler/gurobi/gurobi_prod.lic and copy down the HOSTID field.
If this isn't the original scheduler1 machine (it is the backup), then spoof the mac address of the machine to be the
HOSTID from the license file. You can set the mac address of eth0 on the machine using 
<code>ip link set dev eth0 address de:ad:be:ef:ca:fe</code> with the proper mac address.

The scheduler should now be ready to start as a service.

#### To update
* Logon to scheduler1 as eng
* Stop the scheduler: <code>service adaptive_scheduler stop</code>. Make sure it is not in the middle of a connection 
to the observation portal before stopping it - look at its log file in /var/log/adaptive_scheduler.err.
* Go to /lco/adaptive_scheduler directory and git pull the latest code
* source the scheduler virtual env at /lco/env/scheduler/bin/ and pip install the requirements if any have changed
* Start the scheduler: <code>service adaptive_scheduler start</code>

### Setup Instructions (docker)
* build the container: <code>docker build -t docker.lco.global/adaptive_scheduler .</code>
* push the container: <code>docker push docker.lco.global/adaptive_scheduler</code>
* if using the docker-compose.yml file in the project, make sure it's entrypoint is set correctly, and that the 
environment variables are set correctly with the hosts correct for all the services. There is a test entrypoint to run 
the unit tests and a normal entrypoint to run the scheduler. 

#### Authors: 
Eric Saunders

Sotiria Lampoudi

Jonathan Nation

Elisabeth Heinrich-Josties

