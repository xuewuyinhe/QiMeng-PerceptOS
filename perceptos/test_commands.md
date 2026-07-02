# Test info：

## apache-ab benchmark

In the paper:

&#x20;    PC ubuntu：ab -n 1000000 -c 50 http://xxxx

&#x20;    PC fedora： ab -n 1000000 -c 50 http://xxxx

&#x20;    workstation ubuntu：ab -n 1000000 -c 1000 http://xxxx





## redis-redisbenchmark:

In the paper:

&#x20;    PC ubuntu： redis-benchmark -n 50000 -c 25 --csv

&#x20;    PC fedora：  redis-benchmark -n 1000000 -c 50 --csv

&#x20;    workstation ubuntu：  redis-benchmark -n 1000000 -c 50 --csv





## aes- cryptsetup benchmark:

###### Run sh test\_cry\_aes.sh in the util/ directory.



## PostgreSQL - pgbench:

''''

The following steps only need to be configured once for pgbench. They are not required for subsequent pgbench tests:

sudo apt install postgresql postgresql-contrib

sudo systemctl start postgresql   // Start on boot

sudo systemctl enable postgresql

psql --version

sudo -u postgres psql // Login to postgres, after login you'll see postgres=# \\q

ALTER USER postgres PASSWORD '123456'; // After login, change the login password, make sure to end with ; for the command to take effect

create database testdb; // Create test database

// Exit login

pgbench -i -U postgres -d test\_db -h localhost -s 500 // Initialize test tables with scaling factor 500, parameter can be adjusted

'''



Pgbench test command(To improve pgbench stability, run each test command three times and take the average throughput of the three runs):

pgbench -c xx -T yy -h localhost -U postgres -d test\_db // Run benchmark -c number of clients, try to make it large -T test duration

//pgbench is quite special.   increase the -c and -T parameters until the throughput no longer increases with further increases on your computer; otherwise, the benchmark may be not stable enough



In the paper:

&#x20;   PC ubuntu: pgbench -c 80 -T 30 -h localhost -U postgres -d test\_db

&#x20;   PC fedora: pgbench -c 100 -T 60 -U postgres -d testdb

&#x20;   Workstation ubuntu: pgbench -c 64 -T 60 -h localhost -U postgres -d test\_db"



## naive rag- chromadb

For RAG, first download the database we provide in huggingface：xuewuyinhe/rag\_chromdb\_workload .

Next, unzip chroma\_db\_optimized.rar and move the extracted folder into the util/ directory. After that, execute '''python3 run\_rag\_benchmark.py''' to run test.

