Hmdapolis-backend
=================

From a fresh EC2 Instance:
```bash
$ wget http://www.ffiec.gov/hmdarawdata/LAR/National/2011HMDALAR%20-%20National.zip
$ wget http://www.ffiec.gov/hmdarawdata/LAR/National/2010HMDALAR%20-%20National.zip
$ wget http://www.ffiec.gov/hmdarawdata/LAR/National/2009HMDALAR%20-%20National.zip
$ wget http://www.ffiec.gov/hmdarawdata/LAR/National/2008HMDALAR%20-%20National.zip
$ wget http://www.ffiec.gov/hmdarawdata/LAR/National/2007HMDALAR%20-%20National.zip
$ wget http://www.ffiec.gov/hmdarawdata/LAR/National/2006HMDALAR%20-%20National.zip
$ sudo apt-get install postgresql python-pip postgresql-server-dev-all python-dev
$ sudo pip install virtualenvwrapper
$ vim ~/.bashrc
    #   Add:
    export WORKON_HOME=$HOME/.virtualenvs
    export PROJECT_HOME=$HOME/Devel
    source /usr/local/bin/virtualenvwrapper.sh
$ source ~/.bashrc

#   Setup DB
#   EC2 Shenanigans to move DB to the mounted drive
$ sudo /etc/init.d/postgresql stop
$ sudo mv /var/lib/postgresql/9.1/main /mnt/pg
$ sudo chown postgres:postgres /mnt/pg
$ sudo su postgres -c "ln -s /mnt/pg /var/lib/postgresql/9.1/main"
$ sudo /etc/init.d/postgresql start
$ sudo mkdir /mnt/workspace
$ sudo chown ubuntu:ubuntu /mnt/workspace/
$ mv *.zip /mnt/workspace/
$ cd /mnt/workspace

#   Back to All cases
$ sudo vim /etc/postgresql/9.1/main/pg_hba.conf
    #   Add:
    #   local   all             all                                     md5
$ sudo /etc/init.d/postgresql restart
$ sudo su postgres -c "createuser hmda -P"
    #   hmda
    #   hmda
    #   n
    #   n
    #   n
$ sudo su postgres -c "createdb -O hmda hmda"

#   HMDA Tools
$ git clone git://github.com/cfpb/hmda-tools.git
$ mkvirtualenv hmdatools
$ cd hmda-tools
$ pip install -r requirements.txt
$ python setup.py install
$ pip install psycopg2
$ hmda_create_schemas postgresql://hmda:hmda@localhost/hmda

#   Import the datas
$ unzip 2006HMDALAR\ -\ National.zip
$ unzip 2007HMDALAR\ -\ National.zip
$ unzip 2008HMDALAR\ -\ National.zip
$ unzip 2009HMDALAR\ -\ National.zip
$ unzip 2010HMDALAR\ -\ National.zip
$ unzip 2011HMDALAR\ -\ National.zip
$ cat 2006HMDALAR\ -\ National.CSV | sed 's/NA//gI' | sed 's/ //g' > hmda06.csv
$ cat 2007HMDALAR\ -\ National.CSV | sed 's/NA//g' | sed 's/ //g' > hmda07.csv
$ cat 2008HMDALAR\ -\ National.CSV | sed 's/NA//g' | sed 's/ //g' > hmda08.csv
$ cat 2009HMDALAR\ -\ National.CSV | sed 's/NA//g' | sed 's/ //g' > hmda09.csv
$ cat 2010HMDALAR\ -\ National.csv | sed 's/NA//g' | sed 's/ //g' > hmda10.csv
$ cat 2011HMDALAR\ -\ National.csv | sed 's/NA//g' | sed 's/ //g' > hmda11.csv
$ psql -U hmda hmda
    >   \copy hmda FROM '/mnt/workspace/hmda06.csv' DELIMITERS ',' CSV;
    >   \copy hmda FROM '/mnt/workspace/hmda07.csv' DELIMITERS ',' CSV;
    >   \copy hmda FROM '/mnt/workspace/hmda08.csv' DELIMITERS ',' CSV;
    >   \copy hmda FROM '/mnt/workspace/hmda09.csv' DELIMITERS ',' CSV;
    >   \copy hmda FROM '/mnt/workspace/hmda10.csv' DELIMITERS ',' CSV;
    >   \copy hmda FROM '/mnt/workspace/hmda11.csv' DELIMITERS ',' CSV;
    >   create index hmda_all_idx on hmda (year, msa_md, action_type, agency, loan_amount, applicant_income);

$ mkvirtualenv hmdabackend
$ cd Hmdapolis-backend/
$ pip install -r requirements.txt

```
