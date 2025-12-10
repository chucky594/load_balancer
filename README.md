# Project Title and Overview 
Project name: Web Service load balancing 

## Project Description
The goal of the project is to configure web servers on two linux machines of different distributions. Setup HAproxy on one distribution to load balance between 
the two and perform SSL termination and run health checks.

### Getting Started 
To kickstart the project you need to have access to the servers to the virtual linux machines. Rocky linux and Ubuntu 24.04. You do this by 
SSHing into the servers by running 'ssh server_name@server_ip' and you should be to access your server. Also ensure you have setup your SSH keys
both public and private and save them on github.

#### Prerequsites 
Make sure to install all the necessary dependencies for the project by running. 
- Nginx 
- Apache 
- HAproxy 
- Flask
- Gunicorn 

#### Installation 
You can run this project locally on your machine by running 
1 Clone git repository :
  '''bash
  git clone https://github.com/chucky594/load_balancer.git 
  '''

2. Install dependencies:
   '''bash 
   pip install requiremnts.txt
   '''

4. Setup Enivronment variables.
   For instance in this case initialize the different host IPs for the different servers e.g UBUNTU_IP and ROCKY_IP

#### Usage (How to use it) 
To implement the project the project :
1. Confirm if both web servers are enable and running smoothly without any errors.By running:
   On Ubuntu:
   '''bash 
   sudo systemctl enable nginx
   sudo systemctl restart nginx
   #For rocky
   sudo systemctl enable httpd
   sudo systemctl restart httpd
   
   #ALways run this command to check for errors on haproxy config file. 
   sudo systemctl journactl -c -f /etc/haproxy/haproxy.cfg 
   
   '''
   If you any error messages make sure to read them and fix them accordingly
   

   Configure the HApooxy to run on port 8000 to avoid collision on port 80 with other running applications.Run
   '''bash
   sudo nano /etc/haproxy/haproxy.cfg
   '''
   Add the following configuration to the haproxy configuration file:
   '''bash
   global
        log /dev/log    local0 notice
        daemon
        maxconn 2000

    defaults
        log     global
        mode    http
        option  httplog
        timeout connect 5000ms
        timeout client  50000ms
        timeout server  50000ms

    #Frontend: Listens for incoming client traffic on port 8000
    frontend http_front
        bind *:8000
        mode http
        default_backend web_servers
    
    #Backend: Distributes traffic to the two web servers
    backend web_servers
        mode http
        balance roundrobin
        option forwardfor
    #Health Check: Crucial for high-availability. Checks the /status endpoint.
    option httpchk GET /status 
    
    #Server 1: Ubuntu Nginx Backend (local loopback)
    server ubuntu_nginx 127.0.0.1:80 check inter 2000ms rise 2 fall 3
    
    #Server 2: Rocky Apache Backend (remote IP)
    server rocky_apache 192.168.1.101:80 check inter 2000ms rise 2 fall 3
    '''
   **Make sure to use local on ubuntu_nginx and not its own IP address.
   For Rocky make sure to its IP address together with the port number.

   Enable and start HAProxy look any errors and fix them .
   Run:
   '''bash
   sudo systemctl enable haproxy

   sudo systemctl restart haproxy.

   #Also confirm that all the applications are running at their desired ports by running:

   sudo ss -tulnp | grep 80

   '''
   ** Ensure to disable the firewalls on each backend by running:
   '''bash
   #On rocky first confirm if its running or not and if it is:
   sudo systemctl status firewalld
   sudo systemctl stop firewalld

   #On Ubuntu do the same thing
   sudo ufw status
   sudo ufw disable
   #If you come across 'command not found' you're in luck there no need of disabling ufw.

   **Disabling the firewall ensures that the applications are not blocked from running.
   To enusre everything is okay run :
   '''bash
   curl -v http://ROCKY_IP:80
   #If your application instance is being is displayed you're good.
   curl -v http://UBUNTU_IP/localhost:80
   #If your application instance is being is displayed you're good.

   #For HAProxy make sure it actually load balancing between the two backends.
   http://UBUNTU_IP:8000
   #Open your browser and confirm whether it switching from ubuntu to rocky app instances and if so you're good.
   
   #Disable one backend server to ensure the load balancer actually works .
   sudo systemctl stop httpd

   #You should only the ubuntu instance being displayed.

#### Summary 
That is how web service load balancing works. Always ensure the firewall is disabled on each backend . 

   
   
   


