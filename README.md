# -DataHubble_DataGeneration-
## 一、DataHubble一张宽表数据生成说明
数据生成主要建立在数据基准TPCx-BB的基础上，同时参考了一些真实数据，根据系统优化以后，提供指定大小的一张宽表。
### 1、指定输出数据的格式和位置
/pdgf/config/demo-generation.xml中指定了生成数据的存放位置和格式，可通过修改该文件参数自定义相关内容。
### 2、自定义数据表名称
/pdgf/config/demo-schema.xml设置了表schema的具体参数，可修改生成的数据文件名称和每个字段的具体定义。
### 3、生成指定大小的数据文件，参数为要生成的数据大小（单位为GB）
```
cd pdgf
./generate_table.sh 1000
```
生成的数据表默认存放在/pdgf/output文件夹下。
### 4、将生成的数据上传到HDFS并建立hive外部表fact：
```
Create external table fact
(itemid INT,
quantity INT,
quantity1 INT,
discount DOUBLE,
discount1 DOUBLE,
solddate DATE,
customer STRING, 
age INT,
age1 INT,
gender STRING,
province STRING,
nationality STRING)
ROW FORMAT DELIMITED FIELDS TERMINATED BY '|' STORED AS TEXTFILE;

LOAD DATA LOCAL INPATH '/home/scidb/DataGeneration/pdgf/output/websales_home_myshop_fact_table.dat' INTO TABLE fact;
```
真实数据则作为dimension表（\table\dimension_table.csv），上传到HDFS并建立hive外部表的方式类似，这里就不再赘述了。
### 5、在hive中将fact表和dimension表join生成最终的数据表，即为最终的宽表：
```
Create external table if not exists websales_home_myshop_10000
(itemname STRING,
price double,
price1 double,
quantity INT,
quantity1 INT,
discount DOUBLE,
discount1 DOUBLE,
category STRING,
solddate DATE,
customer STRING, 
age INT,
age1 INT,
gender STRING,
province STRING,
nationality STRING,
itemdesc STRING);

insert into websales_home_myshop_10000(itemname,price,price1,quantity,quantiry1,discount,discount1,category,solddate,customer,age,age1,gender,province,nationality,itemdesc)
select dimension.itemname,dimension.price,dimension.price,fact.quantity,fact.quantity,fact.discount,fact.discount,dimension.category,fact.solddate,fact.customer,fact.age,fact.age,fact.gender,fact.province,fact.nationality,dimension.itemdesc from
fact left outer join dimension
on fact.item_id=dimension.item_id;
```
