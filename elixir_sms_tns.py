import requests
import cx_Oracle
import yagmail
import css_inline
import cssselect
import cssutils
from urllib.parse import quote

tns_entry = 'CIT'
user='ELIXIR'
password='oracleana'

dsn = f"{user}/{password}@{tns_entry}"
conn = cx_Oracle.connect(dsn)

s = conn.cursor()
s.execute('SELECT SMS_USER,SMS_PWD,SMS_SID FROM GN_SMS_SETUP') # use triple quotes if you want to spread your query across multiple lines
for row in s:
    smsuser = row[0]
    smspwd = row[1]
    smssid = row[2]

sql = ('update GN_SMS_DETAIL '
        'set SMS_STATUS=:status ,'
        'RESPONSE=:resp_msg ,'
        'SENT_TIME=sysdate '
        'where tran_no = :tran_no')

c = conn.cursor()
c.execute('SELECT MESSAGE, TRAN_NO, MOBILE FROM GN_SMS_DETAIL WHERE SMS_STATUS=\'N\' AND APPROVED=\'Y\'')# use triple quotes if you want to spread your query across multiple lines
for row in c:
    msgs = row[0]
    phn = row[2]

    url = ('https://api.smscountry.com/SMSCwebservice_bulk.aspx?User=' +
        quote(smsuser) +
        '&passwd=' + quote(smspwd) +
        '&mobilenumber=974' + quote(phn) +
        '&message=' + quote(msgs) +
        '&sid=' + quote(smssid) +
        '&mtype=N&DR=Y')

    #print(url)

    # Make the request
    response = requests.get(url)
    #print(response.text)
    response_content = response.text.strip()  # Remove any extra whitespace
    print(sql)
    if response.status_code == 200:
        f = conn.cursor()
        if response_content.startswith("OK:"):
            f.execute (sql,['Y',response_content,row[1]])
        else:
            f.execute (sql,['N',response_content,row[1]])
        conn.commit()

conn.close()
