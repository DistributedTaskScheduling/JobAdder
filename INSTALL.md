This file gives a detailed explanation of how to install JobAdder on user clients, the server, or worker clients.
Note that all components of JobAdder were designed to be used exclusively on Linux.
Furthermore, the server and the worker clients are assumed to be using central authentication (e.g. LDAP).
To run the JobAdder test suite all of the steps listed for server, worker client, and user client need to be taken *on the same machine*.

## Installation Notes (Linux)
Detailed step-by-step instructions to install JobAdder.

### 1. Pre-installation
Steps to take before installing JobAdder.
#### 1.1 Pre-installation (Server)
Steps to take before installing JobAdder on the server.
##### 1.1.1 Software requirements
The following software is required to run the JobAdder server:

- Python 3.7+
- PostgreSQL 9.5+, including server dev packages
- The Python packages specified in dependencies_server.txt 

When using a very minimalistic Linux distribution it might be necessary to install [additional packages](https://cryptography.io/en/latest/installation/)
for the installation of the cryptography Python package (an indirect dependency).
#### 1.1.2 JobAdder system account
On the server and the worker client the jobadder user needs to be created.
Add the *jobadder* user and the corresponding group by running:

    sudo useradd --system jobadder

Users in the jobadder group are granted administrative privileges in the context of JobAdder: 
they can manage worker clients and the jobs of any user.

The jobadder user needs to be added to the docker group to run jobs:

    sudo usermod -a -G docker jobadder

A user that intends to run JobAdder integration tests also needs to be a member of the docker group.
#### 1.2 Pre-installation (Worker Client)
Steps to take before installing JobAdder on the worker client.
##### 1.2.1 Software requirements
The following software is required to run the JobAdder worker:

- Python 3.7+
- Docker 18.09.7+ 

#### 1.3 Pre-installation (User Client)
Steps to take before installing JobAdder on the user client.
##### 1.3.1 Software requirements
The following software is required to run the JobAdder user client:

- Python 3.7+

### 2. Install JobAdder
The git repository can be cloned by running:
    
    git clone https://github.com/DistributedTaskScheduling/JobAdder

After that, execute the *install.sh* script located in the git repository's root directory with superuser privileges.
This will install JobAdder system-wide through pip.

### 3. Post-Installation Instructions
Additional steps to take after the installation of JobAdder.
#### 3.1 Post-Installation Instructions (Server)
Additional steps to take on the server.
##### 3.1.1 Configure PostgreSQL
Create a PostgreSQL user called *jobadder*:

    sudo -u postgres createuser --pwprompt jobadder

Create a PostgreSQL database called *jobadder*:

    sudo -u postgres createdb --owner=jobadder jobadder

Make sure to configure the [authentication method](https://www.postgresql.org/docs/12/auth-methods.html) of your PostgreSQL installation.
JobAdder was designed to use password authentication.
##### 3.1.2 Enable the systemd Service
To automatically start the JobAdder server on boot run:

    sudo systemctl enable JobAdderServer.service

##### 3.1.3 Modify the Configuration File
The default values in the configuration file located under */etc/jobadder/server.conf* need to be adjusted:

- Set *database_config/password* to the password you set for the PostgreSQL jobadder user.
- Set the values of *email_config* to the login data of an SMTP server if you want to use email notifications.
- Set *special_resources* available amounts for special resources (e.g. software licenses) that jobs might need to run.
- Set a port for the web server if you want to use it.

The server configuration file is by default not readable by users because it may contain passwords.
#### 3.2 Post-Installation Instructions (Worker Client)
Additional steps to take on worker clients.
##### 3.2.1 Enable the systemd Service
To automatically start the JobAdder worker client on boot run:

    sudo systemctl enable JobAdderWorker.service

##### 3.2.2 Modify the Configuration File
The default values in the configuration file located under */etc/jobadder/worker.conf* need to be adjusted:

- Set *ssh_config/hostname* to the IP address of the server.
- Set the values under *resource_allocation* to the values made available to workers. The values for memory and swap space are interpreted as megabytes.
- Optional: set *uid* to a human-readable name that identifies this worker. If *uid* is not set, the server will assign it.

The worker configuration file is by default not readable by users because it may contain passwords.
#### 3.3 Post-Installation Instructions (User Client)
Additional steps to take on user clients.
##### 3.3.1 Set Up SSH Config (Optional)
Very often the CLI arguments used to connect to the server is the same across multiple jobs.
The defaults for these arguments can be changed by creating a configuration file under *~/.config/jobadder*.
The configuration file must be in the YAML format (<arg_name>: <arg_value>) and can provide a default for the following CLI arguments:

- verbosity
- hostname
- username
- password
- key_path
- passphrase
- email
#### 3.4 Post-Installation instructions (Test Suite)
To run the test suite additional steps need to be taken.

Add yourself to the jobadder group:

    sudo usermod -a -G jobadder <your username here>

Add yourself to the docker group:

    sudo usermod -a -G docker <your username here>

Create the jobadder-test database:

    sudo -u postgres createdb --owner=jobadder jobadder-test
