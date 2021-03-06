# -DataHubble-Bench-
DataHubble-Bench中包括数据的生成程序、步骤文档以及某电商的原始数据，其中数据生成主要建立在数据基准TPCx-BB的基础上，同时参考了真实数据，根据系统优化以后，可以提供指定大小的宽表与多表数据，其中宽表中的数据全部来源于多表。
## 一、DataHubble多表数据生成说明
### 1、数据生成
数据生成使用了TPCx-BB Tools中data-generator文件夹中的pdgf.jar工具（/Multi_table/pdgf/）进行数据生成，生成指令如下：
```
java -jar pdgf.jar -l schema.xml -l generation.xml -c -s -sf 1
```
该命令生成的9张表总大小约为100MB，使用默认SF=1（scale factor），可以根据实际的需求调整sf的大小。
上面的两个XML文件为config文件夹下的配置文件，其中schema.xml是对于生成数据的schema的描述，generation.xml则配置数据输出时的相应信息。
生成的数据在“/Multi_table/pdgf/output”目录下，为“.dat“文件
### 2、导入数据
将数据导入hive，首先定义表结构，以store_returns表为例，如下所示：
```
CREATE TABLE store_returns(sr_returned_date_sk BIGINT, sr_returned_date_sk1 BIGINT,sr_item_sk BIGINT, sr_item_sk1 BIGINT,sr_customer_skr BIGINT, sr_customer_sk1 BIGINT, sr_ticket_number BIGINT, sr_ticket_number1 BIGINT, sr_return_quantity INTEGER, sr_return_quantity1 INTEGER, sr_return_amt DECIMAL(7, 2), sr_return_amt1 DECIMAL(7, 2))
ROW FORMAT DELIMITED FIELDS TERMINATED BY '|'
STORED AS TEXTFILE;
```
之后将“.dat“文件中的数据导入hive中：
```
LOAD DATA LOCAL INPATH '/Multi_table/pdgf/output
/store_returns.dat' 
INTO TABLE ITEM_RAW;
```
其余8张表也是类似的方法。
### 3、融合真实数据
需要将真实数据融合到新建的多表中的item表，首先建立hive的外部表dimension，并将/Wide_table/DataGeneration/table/dimension_table.csv处的数据导入：
```
Create external table dimension
(item_id INT,
itemname STRING,
price DOUBLE,
category STRING,
desc STRING
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY '|' STORED AS TEXTFILE;

LOAD DATA LOCAL INPATH '/Wide_table/DataGeneration/table/dimension_table.csv' INTO TABLE dimension;
```
建立新的item表，此处为item_2，将真实的数据从dimension导入到item_2中： 
```
Create external table if not exists item_2(i_item_sk BIGINT, i_item_sk1 BIGINT, i_item_id CHAR(16), i_item_desc VARCHAR(200), i_current_price DECIMAL(7, 2), i_current_price1 DECIMAL(7, 2), i_class_id INT, i_class_id1 INT, i_category_id INT, i_category_id1 INT, i_category CHAR(50));

insert into item_2(i_item_sk, i_item_sk1, i_item_id, i_item_desc, i_current_price, i_current_price1, i_class_id, i_class_id1, i_category_id, i_category_id1, i_category)
select 
item.i_item_sk, item.i_item_sk1, dimension.itemname, dimension.desc, dimension.price, dimension.price, item.i_class_id, item.i_class_id1, item.i_category_id, item.i_category_id1, dimension.category from
item left outer join dimension
on item.i_item_sk=dimension.item_id;
```
接下来对item_2进行更名即可，这里不再赘述，新生成的item就是融合了真实数据的数据集。
## 二、DataHubble一张宽表数据生成说明
### 1、指定输出数据的格式和位置
/Wide_table/DataGeneration/pdgf/config/demo-generation.xml中指定了生成数据的存放位置和格式，可通过修改该文件参数自定义相关内容。
### 2、自定义数据表名称
/Wide_table/DataGeneration/pdgf/config/demo-schema.xml设置了表schema的具体参数，可修改生成的数据文件名称和每个字段的具体定义。
### 3、生成指定大小的数据文件，参数为要生成的数据大小（单位为GB）
```
cd /Wide_table/DataGeneration/pdgf
./generate_table.sh 1000
```
生成的数据表默认存放在/Wide_table/DataGeneration/pdgf/output文件夹下。
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

LOAD DATA LOCAL INPATH '/Wide_table/DataGeneration/pdgf/output/websales_home_myshop_fact_table.dat' INTO TABLE fact;
```
### 5、建立dimension表并导入真实数据
真实数据作为dimension表（/Wide_table/DataGeneration/table/dimension_table.csv），需要先建立hive的外部表并将数据导入：
```
Create external table dimension
(item_id INT,
itemname STRING,
price DOUBLE,
category STRING,
desc STRING
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY '|' STORED AS TEXTFILE;

LOAD DATA LOCAL INPATH '/Wide_table/DataGeneration/table/dimension_table.csv' INTO TABLE dimension;
```
### 6、在hive中将fact表和dimension表join生成最终的数据表，即为最终的宽表：
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

