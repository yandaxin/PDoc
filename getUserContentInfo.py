import requests
import json
import time
import random
import pymysql
import sys

url = "https://timeline-merger-ms.juejin.im/v1/get_entry_by_self"

params = {
        "src": "web",
        "uid": # token 对应的 uid,一般为爬虫登陆账号的 uid,
        "device_id": # device id,
        "token": # token,
        "type": "post",
        "limit": "20",
        "order": "createdAt",
        "before":""
}

class juejinuser(object):

    def __init__(self,url,params):
        self.header = {
            # request header
        }
        self.params = params
        self.url = url
    
    def getUid(self):
        conn = pymysql.connect(host="localhost",user='user',password="password",database="juejin")
        cursor = conn.cursor()
        query = "SELECT uid FROM juejinuserinfo WHERE uid NOT IN(SELECT DISTINCT uid FROM juejincontent) AND username <> 'noexist' LIMIT 1"
        cursor.execute(query)
        uid = cursor.fetchall()
        if len(uid) == 0:
            sys.exit(0)
        uid = uid[0][0]
        cursor.close()
        conn.close()
        return uid

    
    def getData(self):
        if self.params['before']=='':
            self.params['targetUid'] = self.getUid()
        print(params['targetUid'])
        # 检查 params 中 uid 对应的 follower ,folloeeNum 是否为 0，如不为则请求 followee 列表，如为  0 将其 folloee 字段设置为 nofollowee,存入 MySQL
        response  =  requests.get(self.url, headers = self.header, params = self.params)
        if response.status_code == 200:
            data = json.loads(response.text)
            if data['m'] == 'ok' and len(data['d'])!= 0:
                if data['d']['total']!=0:
                    self.saveData(data['d']['entrylist'])
                    self.params['before'] = data['d']['entrylist'][-1]['createdAt']
                elif self.params['before']!='':
                    self.params['before'] = ""
                else:
                    fakedata = [
                        {
                            "collectionCount":0,
                            "createdAt":"2000-01-01T00:00:00.000Z",
                            "originalUrl":"https://juejin.im/post/000000000000000000000000",
                            "title":"no post",
                            "viewsCount":0,
                            "category":{
                                "name":"no post"
                            },
                            "objectId":self.params['targetUid']
                        }
                    ]
                    self.saveData(fakedata)
            elif data['m'] == 'data read failed':
                fakedata = [
                        {
                            "collectionCount":0,
                            "createdAt":"2000-01-01T00:00:00.000Z",
                            "originalUrl":"https://juejin.im/post/000000000000000000000000",
                            "title":"post sseems deleted",
                            "viewsCount":0,
                            "category":{
                                "name":"no post"
                            },
                            "objectId":self.params['targetUid']
                        }
                    ]
                self.saveData(fakedata)
                self.params['before'] = ""
            else:
                print(data)
                time.sleep(30)
                self.getData()
        else:
            print("请求未正确响应")
            print('当前 target 为：',self.params['targetUid'])
    
    def saveData(self,data):
        # params： 与 line53 保持一致
        conn = pymysql.connect(host="localhost",user='root',password="igame750ti",database="juejin") 
        cursor=conn.cursor()
        uid = self.params['targetUid'],
        flag = 0
        for i in data:
            flag = flag+1
            print(flag)
            collectionCount = i['collectionCount']
            createdAt = i['createdAt']
            originalUrl = i['originalUrl']
            title = i['title']
            viewsCount = i['viewsCount']
            category = i['category']['name']
            objectId = i['objectId']
            sql="insert into juejincontent (uid,collectionCount,createdAt,originalUrl,title,viewsCount,category,objectId) VALUE (%s,%s,str_to_date(%s,'%%Y-%%m-%%dT%%T.%%fZ'),%s,%s,%s,%s,%s);"
            try:
                cursor.execute(sql,(uid,collectionCount,createdAt,originalUrl,title,viewsCount,category,objectId))
                conn.commit()   #把修改的数据提交到数据库
            except Exception as e:
                print("错无错误")
                conn.rollback() 
                print(e)#捕捉到错误就回滚
        cursor.close()
        conn.close()

if __name__ == '__main__':
    while(1):
        juejinuser(url,params).getData()