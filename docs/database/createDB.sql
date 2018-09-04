CREATE TABLE instances(type TEXT PRIMARY KEY, memory FLOAT NOT NULL, vcpu INTEGER NOT NULL);

CREATE TABLE prices(type TeXT, market INT NOT NULL, region TEXT NOT NULL, zone TEXT,  price FLOAT NOT NULL,
                    PRIMARY KEY(type, market, region, zone),
                    FOREIGN KEY(type) REFERENCES instance(type));

CREATE TABLE tasks(job_id INT NOT NULL, task_id INT NOT NULL, name TEXT not NULL, memory FLOAT NOT NULL, io_size FLOAT NOT NULL,
                   PRIMARY KEY(job_id, task_id));

CREATE TABLE execution(job_id INT NOT NULL, task_id INT NOT NULL, run_id INTEGER  NOT NULL, type TEXT NOT NULL, runtime FLOAT NOT NULL, status TEXT,
                   PRIMARY KEY(job_id, task_id, run_id, type),
                   FOREIGN KEY(type) REFERENCES instances(type));