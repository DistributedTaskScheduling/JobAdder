This file gives a detailed explanation of how to install JobAdder on user clients, the server, or worker clients.
Note that all components of JobAdder were designed to be used exclusively on Linux.
Furthermore, the server and the worker clients are assumed to be using central authentication (e.g. LDAP).

## Requirements
The following software is required to run JobAdder:

- Python, 3.7 or higher (user client, server, and worker clients)
- PostgreSQL (server)
- Docker, recent version (worker clients)

## Installation Notes (Linux)
Detailed step-by-step instructions to install JobAdder.

### 1. Install JobAdder
The git repository can be cloned by running:
    
    git clone https://github.com/DistributedTaskScheduling/JobAdder

After that, execute the *install.sh* script located in the git repository's root directory with superuser privileges.
This will install JobAdder system-wide through pip.

### 2. Post-Installation Instructions
Additional steps to take after the installation of JobAdder.
#### 2.1 Post-Installation Instructions (Server)
Additional steps to take on the server.
##### 2.1.1 Create the jobadder User and Group
Add the *jobadder* user and the corresponding group by running:

    sudo useradd --system jobadder

The jobadder user is used by the daemons running on the server and the worker clients.
Users in the jobadder group are granted administrative privileges in the context of JobAdder: 
they can manage worker clients and the jobs of any user.

The jobadder user needs to be added to the docker group to run jobs:

    sudo usermod -a -G docker jobadder

##### 2.1.2 Configure PostgreSQL
Create a PostgreSQL user called *jobadder*:

    sudo -u postgres createuser --pwprompt jobadder

Create a PostgreSQL database called *jobadder*:

    sudo -u postgres createdb --owner=jobadder jobadder

Make sure to configure the [authentication method](https://www.postgresql.org/docs/12/auth-methods.html) of your PostgreSQL installation.
JobAdder was designed to use password authentication.
##### 2.1.3 Enable the systemd Service
To automatically start the JobAdder server on boot run:

    sudo systemctl enable JobAdderServer.service

##### 2.1.4 Modify the Configuration File
The default values in the configuration file located under */etc/jobadder/server.conf* need to be adjusted:

- Set *database_config/password* to the password you set for the PostgreSQL jobadder user.
- Set the values of *email_config* to the login data of an SMTP server if you want to use email notifications.
- Set *special_resources* available amounts for special resources (e.g. software licenses) that jobs might need to run.
- Set a port for the web server if you want to use it.

#### 2.1 Post-Installation Instructions (Worker Client)
Additional steps to take on worker clients.
##### 2.1.1 Enable the systemd Service
To automatically start the JobAdder worker client on boot run:

    sudo systemctl enable JobAdderWorker.service

##### 2.1.2 Modify the Configuration File
The default values in the configuration file located under */etc/jobadder/worker.conf* need to be adjusted:

- Set *ssh_config/hostname* to the IP address of the server.
- Set the values under *resource_allocation* to the values made available to workers. The values for memory and swap space are interpreted as megabytes.
- Optional: set *uid* to a human-readable name that identifies this worker. If *uid* is not set, the server will assign it.

#### 2.1 Post-Installation Instructions (User Client)
Additional steps to take on user clients.
##### 2.1.1 Set Up SSH Config (Optional)
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