# pysfreport
Get Salesforce report data both details and printable view data

Based on simple-salesforce and some scripts I found in stack overflow.
Return pandas dataframe.


**Usage:** 

```report_id = '00O9000000xxxxx' ```

**set Salesforce session_id some way (by login or reused from other app), check [simple-salesforce](https://github.com/simple-salesforce/simple-salesforce) for details** 

```sf = SfReportsApi(username='xxxx', password='xxxx', security_token='', instance_url='https://efec.my.salesforce.com') ```

**get matrix report printable view data** 

```sf.matrix_to_df(report_id)```

**get report details data** 

```sf.details_to_df(report_id)```
