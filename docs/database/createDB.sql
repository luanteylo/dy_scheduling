CREATE TABLE instances(type TEXT PRIMARY KEY, memory FLOAT NOT NULL, vcpu INTEGER NOT NULL);
CREATE TABLE prices(type TeXT, market INT NOT NULL, region TEXT NOT NULL, zone TEXT,  price FLOAT NOT NULL, PRIMARY KEY(type, market, region, zone), FOREIGN KEY(type) REFERENCES instance(type));
