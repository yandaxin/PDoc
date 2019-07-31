import requests
import json
import time
import random
import pymysql
import sys

url = "https://lccro-api-ms.juejin.im/v1/get_multi_user"

params = {
        # 修改此处 uid 可以更换爬虫的起点
        "uid": "5aae85666fb9a028e33b3b35",
        "device_id": "1563801994694",
        "token":# token
        "src": "web",
        "ids": # 目标 id,
        "cols": "viewedEntriesCount|role|totalCollectionsCount|allowNotification|subscribedTagsCount|appliedEditorAt|email|followersCount|postedEntriesCount|latestCollectionUserNotification|commentedEntriesCount|weeklyEmail|collectedEntriesCount|postedPostsCount|username|latestLoginedInAt|totalHotIndex|blogAddress|selfDescription|latestCheckedNotificationAt|emailVerified|totalCommentsCount|installation|blacklist|weiboId|mobilePhoneNumber|apply|followeesCount|deviceType|editorType|jobTitle|company|latestVoteLikeUserNotification|authData|avatarLarge|mobilePhoneVerified|objectId|createdAt|updatedAt"
}

class juejinuser(object):

    def __init__(self,url,params):
        self.header = {
           # request header
        }
        self.params = params
        self.url = url
    
    def getData(self):
        # 检查 params 中 uid 对应的 follower ,folloeeNum 是否为 0，如不为则请求 followee 列表，如为  0 将其 folloee 字段设置为 nofollowee,存入 MySQL
        response  =  requests.get(self.url, headers = self.header, params = self.params)
        if response.status_code == 200:
            data = json.loads(response.text)
            if data['m'] == 'ok' and len(data['d'])!= 0:
                if len(data['d'][self.params['ids']])!=0:
                    self.saveData(data['d'])
                    self.changeUid()
                else:
                    data[self.params['ids']] = {
                        'username':'noexist'
                    }
                    self.saveData(data)
                    self.changeUid()
            else:
                time.sleep(3)
                self.getData()
        else:
            print("请求未正确响应")
            print('当前 ids 为：',self.params['ids'])

    def changeUid(self):
        # tablename: 所使用的表的名字
        sql = "select followeeId from juejinuser where followeeId not in (select uid from juejinuserinfo) and followeeId <> 'nofollowee' limit 1"
        try:
            #params:
            #host：mysql 地址
            #user: mysql 登陆用户名
            #password: mysql 登陆用户名对应的登陆密码
            #database: 期望使用的 database 名字
            conn = pymysql.connect(host="localhost",user='user',password="password",database="juejin") 
            cursor=conn.cursor()
            cursor.execute(sql)
            results = cursor.fetchall()
            if len(results) == 0:
                sys.exit(0)
            params['ids'] = results[0][0]
            cursor.close()
            conn.close()
        except Exception as e:
            conn.rollback() 
            print(e)#捕捉到错误就回滚
    
    def saveData(self,data):
        # params： 与 line53 保持一致
        conn = pymysql.connect(host="localhost",user='user',password="password",database="juejin") 
        cursor=conn.cursor()
        uid = self.params['ids']
        followeesCount = data[uid].get('followeesCount',0)
        followersCount = data[uid].get('followersCount',0)
        latestLoginedInAt = data[uid].get('latestLoginedInAt','2000-01-01T00:00:00.000Z')
        createdAt = data[uid].get('createdAt','2000-01-01T00:00:00.000Z')
        username = data[uid]['username']
        subscribedTagsCount = data[uid].get('subscribedTagsCount',0)
        totalViewsCount = data[uid].get('totalViewsCount',0)
        viewedEntriesCount = data[uid].get('viewedEntriesCount',0)
        totalCollectionsCount = data[uid].get('totalCollectionsCount',0)
        juejinPower = data[uid].get('juejinPower',0)
        sql="insert into juejinuserinfo (uid,followeesCount,followersCount,latestLoginedInAt,createdAt,username,subscribedTagsCount,totalViewsCount,viewedEntriesCount,totalCollectionsCount,juejinPower) VALUE (%s,%s,%s,str_to_date(%s,'%%Y-%%m-%%dT%%T.%%fZ'),str_to_date(%s,'%%Y-%%m-%%dT%%T.%%fZ'),%s,%s,%s,%s,%s,%s);"
        try:
            cursor.execute(sql,(uid,followeesCount,followersCount,latestLoginedInAt,createdAt,username,subscribedTagsCount,totalViewsCount,viewedEntriesCount,totalCollectionsCount,juejinPower))
            conn.commit()   #把修改的数据提交到数据库
        except Exception as e:
                print("错无错误")
                conn.rollback() 
                print(e)#捕捉到错误就回滚
        cursor.close()
        conn.close()

if __name__ == '__main__':
    while(True):
        juejinuser(url,params).getData()
    