# ItemCatalog-
This project is about developing a Blood Bank web application that provids a list of the availabe blood types in the bank. It also allows some users to register in the system in order to give them the ability to add new blood types, edit information about some blood types, or delete blood types form the list if the back is run out of them.

# Getting Started
In order to start running this web applicatinyou need first to clone or download this whole folder [ItemCatalog-Project](https://github.com/wejdanbab10/ItemCatalog-Project) and put it inside your vagrant folder inside the VM machine.


# Prerequisites
•	Install Linux-based virtual machine (VM)<br/>
•	Download [Vagrant](https://www.vagrantup.com)<br/>
•	Download [VirtualBox](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1)<br/>
•	Download [ItemCatalog-Project](https://github.com/wejdanbab10/ItemCatalog-Project)
•	Download [Python 3.6.6](https://www.python.org/downloads/release/python-366/)<br/>


# Installing
 1. Put the [ItemCatalog-Project](https://github.com/wejdanbab10/ItemCatalog-Project) folder inside the <b>vagrant</b> folder
 2. Open up your Terminal and change the directory to the vagrant directory by using <b>cd</b>
 3. Run the command <b>vagrant up</b> to start installing Linux
 4. Run the commaed <b>vagrant ssh</b> to log in to the VM
 5. Change the directory to the vagrant directory by using <b>cd/vagrant</b>
 6. Change the directory to to catalog directory by using <b>cd/catalog</b>
 7. Install or upgrade Flask by using this comman  <b>sudo python3 -m pip install --upgrade flask</b>
 8. Run the following command <b>python database_setup.py</b> to set up the Blood Bank Database in which all the information will be stored.
 9. Now run this command <b>python databaseInfo.py</b> to insert information into the database.
 10. Finally, run the web application by using this command <b>python application.py</b>
 
 
