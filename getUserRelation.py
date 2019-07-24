import requests
import json
import time
import random
import pymysql

url = "https://follow-api-ms.juejin.im/v1/getUserFolloweeList"

params = {
        # 修改此处 uid 可以更换爬虫的起点
        "uid":"5ae038c0f265da0b8e7f1237",
        "src":"web",
}

class juejinuser(object):

    def __init__(self,url,params):
        self.header = {
            # 从浏览器中拷贝 header 至此处
            #
            #
            #
        }
        self.params = params
        self.url = url
    
    def getData(self):
        # 检查 params 中 uid 对应的 follower ,folloeeNum 是否为 0，如不为则请求 followee 列表，如为  0 将其 folloee 字段设置为 nofollowee,存入 MySQL
        folloeeNum = self.getFolloeeNum()
        if folloeeNum == 0:
            data = [{
                'followee':{
                    'objectId':'nofollowee'
                },
                'createdAtString':'nofollowee'
            }]
            self.saveData(data)
            self.changeUid()
        else:
            response = requests.get(self.url, headers=self.header, params=self.params)
            if response.status_code == 200:
                data = json.loads(response.text)
                # 请求成功且请求到的 followee 列表不为空，直接将数据存入 <tablename> 并更新 before 参数为列表中最后一个 followee 的 createdAtString
                if data['m'] == 'ok' and len(data['d'])!= 0:
                    self.saveData(data['d'])
                    utc = data['d'][-1]['createdAtString']
                    self.params['before'] = utc

                # 请求成功且请求到的 followee 列表为空，说明此用户 followee 已全部采集。从 <tablename> 中查询 followee 字段不为 nofollowee 且不在 follower 中的 uid 继续查询 
                elif data['m'] == 'ok' and len(data['d']) == 0:
                   self.changeUid()

    def changeUid(self):
        # tablename: 所使用的表的名字
        sql = "select followeeId from <tablename> where followeeId not in (select distinct followerId from <tablename>) and followeeId <> 'nofollowee' limit 10"
        try:
            #params:
            #host：mysql 地址
            #user: mysql 登陆用户名
            #password: mysql 登陆用户名对应的登陆密码
            #database: 期望使用的 database 名字
            conn = pymysql.connect(host="********",user='******',password="*********",database="juejin") 
            cursor=conn.cursor()
            cursor.execute(sql)
            results = cursor.fetchall()
            for i in results:
                if self.params['uid'] != i:
                    self.params['uid'] = i
                    self.params['before'] = ''
                    break
            cursor.close()
            conn.close()
        except Exception as e:
            conn.rollback() 
            print(e)#捕捉到错误就回滚

    def getFolloeeNum(self):
        response = requests.get(url = 'https://follow-api-ms.juejin.im/v1/getUserFollowInfo', headers=self.header, params=self.params)
        if response.status_code == 200:
            num = json.loads(response.text)
        return num['d']['followeeNum']
    
    def saveData(self,data):
        # params： 与 line53 保持一致
        conn = pymysql.connect(host="******",user='*******',password="********",database="juejin")
        cursor=conn.cursor()
        followerId = self.params['uid']
        print(followerId)
        for i in data:
            objectId = i['followee']['objectId']
            print(objectId,i['createdAtString'])
            sql="insert into <tablename> (followerId,followeeId) VALUE (%s,%s);"
            try:
                cursor.execute(sql,(followerId,objectId))
                conn.commit()   #把修改的数据提交到数据库
            except Exception as e:
                conn.rollback() 
                print(e)#捕捉到错误就回滚
        cursor.close()
        conn.close()

if __name__ == '__main__':
    i = 0
    while(i<40000):
        i = i+1
        juejinuser(url,params).getData()