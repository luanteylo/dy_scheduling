DROP TABLE marketType;
DROP TABLE status;
DROP TABLE instanceType;
DROP TABLE instance;
DROP TABLE task;
DROP TABLE execution;



CREATE TABLE marketType(id INTEGER PRIMARY KEY, name TEXT);
CREATE TABLE status(id INTEGER PRIMARY KEY, name TEXT);
CREATE TABLE instanceType(id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT NOT NULL, memory FLOAT NOT NULL, vcpu INTEGER NOT NULL, ondemand_price FLOAT NOT NULL);
CREATE TABLE task(job_id INTEGER NOT NULL, task_id INTEGER NOT NULL, name TEXT NOT NULL, path TEXT NOT NULL, parameters TEXT, PRIMARY KEY(job_id, task_id));

CREATE TABLE instance(id INTEGER PRIMARY KEY AUTOINCREMENT, type_id INTEGER NOT NULL,  market_type_id INTEGER NOT NULL, start_time TEXT NOT NULL, end_time TEXT, cost FLOAT, status INTEGER NOT NULL,  FOREIGN KEY(type_id) REFERENCES instanceType(id),
 FOREIGN KEY(status) REFERENCES status(id), FOREIGN KEY(market_type_id) REFERENCES marketType(id));

CREATE TABLE execution(id INTEGER PRIMARY KEY AUTOINCREMENT, job_id INTEGER, task_id INTEGER, instance_id INTEGER, start_time TEXT NOT NULL, finish_time TEXT, memory FLOAT, io_size FLOAT,  status INTEGER NOT NULL, FOREIGN KEY(job_id) REFERENCES task(job_id),FOREIGN KEY(task_id) REFERENCES task(task_id), FOREIGN KEY(instance_id) REFERENCES instance(id));

