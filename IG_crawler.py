import requests
import json
import pandas as pd
import time
from bs4 import BeautifulSoup
import queue
import threading
import os



def content_comment(i,d_check,q_storage,q):
 #print("content_comment")
 mydata=[]
 s = requests.session() #建立request
 html = s.get("https://www.instagram.com/p/"+i).text
 soup=BeautifulSoup(html,'lxml')
 content=soup.findAll('script',type="text/javascript")
    
 #----------------------------------------------------
 for i in range(len(content)):
  if str(content[i]).find('csrf_token')!=-1:
   json_format=str(content[i])
 #------------------------------------------------------
 json_format=json_format.replace("<script type=\"text/javascript\">window._sharedData = ","")
 json_format=json_format.replace(";</script>","")
 json_=json.loads(json_format)
 json_format=json_format.replace("<script type=\"text/javascript\">window._sharedData = ","")
 json_format=json_format.replace(";</script>","")
 json_format=json_format.replace("</script>","")
 json_format=json_format.replace("<script type=\"application/ld+json\">","")
 json_=json.loads(json_format)
    

 #print(json_)
 flag=1
 head=[]
 pic_url=[]
 pic_url.clear()
 user_name=str(json_['entry_data']['PostPage'][0]['graphql']["shortcode_media"]['owner']['username'])
 full_name=str(json_['entry_data']['PostPage'][0]['graphql']["shortcode_media"]['owner']['full_name'])
 owner_id=str(json_['entry_data']['PostPage'][0]['graphql']["shortcode_media"]['owner']['id'])
 display_url=str(json_['entry_data']['PostPage'][0]['graphql']["shortcode_media"]['display_url'])             
 shortcode=str(json_['entry_data']['PostPage'][0]['graphql']["shortcode_media"]['shortcode'])
 like_count=str(json_['entry_data']['PostPage'][0]['graphql']["shortcode_media"]["edge_media_preview_like"]['count'])
 time_=str(json_['entry_data']['PostPage'][0]['graphql']["shortcode_media"]["taken_at_timestamp"])
 time_=str(pd.to_datetime(time_,unit='s'))
 unix_time=str(json_['entry_data']['PostPage'][0]['graphql']["shortcode_media"]["taken_at_timestamp"])
 try:
  context=str(json_['entry_data']['PostPage'][0]['graphql']["shortcode_media"]["edge_media_to_caption"]["edges"][0]['node']['text'])
 except:
  context=""
 try:
  comment_count=str(json_['entry_data']['PostPage'][0]['graphql']["shortcode_media"]["edge_media_to_parent_comment"]['count'])
 except:
  print(shortcode,"fail")
  q.put(shortcode)
  flag=0
 try:
  pic_url_json=json_['entry_data']['PostPage'][0]['graphql']["shortcode_media"]["edge_sidecar_to_children"]['edges']
  for i in range(len(pic_url_json)):
   pic_url.append(str(pic_url_json[i]['node']['display_url']))
 except:
  pic_url.append(str(json_['entry_data']['PostPage'][0]['graphql']["shortcode_media"]['display_url']))


 if flag==1:
  head.append({"time":time_,"unix_time":unix_time,"username":user_name,"id":owner_id,"full_name":full_name,"shortcode":"https://www.instagram.com/p/"+shortcode,"picurl":display_url,"all_picture":pic_url,"text":context,"like_count":like_count,"comment_count":comment_count})    
  cursorlist=[]
  cursorlist.clear()
  cursorlist.append("")
  query_hash="97b41c52301f77ce508f55e66d17620e"
  #shortcode=shortcode  ##input the post url
  first="40"
  node1_comment=[]
  node1_username=[]
  node1_text=[]
  node1_time=[]
  node1_unixtime=[]
  node1_id=[]
  node1_picurl=[]
#--------------
  node2_comment=[]
  node2_username=[]
  node2_text=[]
  node2_time=[]
  node2_unixtime=[]
  node2_id=[]
  node2_picurl=[]
  loop_check=0


  while cursorlist[-1]!=None: 
   html = s.get("https://www.instagram.com/graphql/query/?query_hash="+query_hash+"&variables={\"shortcode\":\""+shortcode+"\",\"first\":"+first+",\"after\":\""+cursorlist[-1]+"\"}").text
   json_=json.loads(html)
   try:
    cursor=json_["data"]["shortcode_media"]["edge_media_to_parent_comment"]["page_info"]['end_cursor']
    loop_check=1
   except:
    q.put(shortcode)
    loop_check=0
    print(shortcode,json_)
    time.sleep(199)
    break
   cursorlist.append(cursor)
   node_1=json_["data"]["shortcode_media"]["edge_media_to_parent_comment"]["edges"]
   for i in range(len(node_1)):
    node1_unixtime.append(str(node_1[i]['node']['created_at']))
    time_1=pd.to_datetime(str(node_1[i]['node']['created_at']),unit='s')
    node1_picurl.append(node_1[i]['node']['owner']['profile_pic_url'])
    node1_id.append(node_1[i]['node']['owner']['id'])
    node1_username.append(node_1[i]['node']['owner']['username'])
    node1_text.append(node_1[i]['node']['text'])
    node1_time.append(str(time_1))
    node1_node2=[]
    node1_comment.append({"user":str(node1_username[0]),"id":str(node1_id[0]),"picurl":str(node1_picurl[0]),"text":str(node1_text[0]),"time":str(node1_time[0]),"unix_time":str(node1_unixtime[0]),"node2":[]})
    node1_unixtime=[]
    node1_username=[]
    node1_text=[]
    node1_time=[]
    node1_id=[]
    node1_picurl=[]

    for j in range(len(node_1[i]['node']['edge_threaded_comments']['edges'])):
     node2_unixtime.append(str(node_1[i]['node']['edge_threaded_comments']['edges'][j]['node']['created_at']))
     time_2=pd.to_datetime(str(node_1[i]['node']['edge_threaded_comments']['edges'][j]['node']['created_at']),unit='s')
     node2_picurl.append(node_1[i]['node']['edge_threaded_comments']['edges'][j]['node']['owner']['profile_pic_url'])
     node2_id.append(node_1[i]['node']['edge_threaded_comments']['edges'][j]['node']['owner']['id'])
     node2_username.append(node_1[i]['node']['edge_threaded_comments']['edges'][j]['node']['owner']['username'])
     node2_text.append(node_1[i]['node']['edge_threaded_comments']['edges'][j]['node']['text'])
     node2_time.append(str(time_2))
     node2_comment.append({"user":str(node2_username[0]),"id":str(node2_id[0]),"picurl":str(node2_picurl[0]),"text":str(node2_text[0]),"time":str(node2_time[0]),"unix_time":str(node2_unixtime[0])})
     node2_unixtime=[]
     node2_username=[]
     node2_text=[]
     node2_time=[]
     node2_id=[]
     node2_picurl=[]
    node1_comment[i]["node2"]=node2_comment
    node2_comment=[]
    
    
  if loop_check==1:
   head[0]['comment']=node1_comment
   q_storage.put(head[0])
 else:
  time.sleep(19)

 d_check.get()


def urlget(url_):
 #print("urlget_work")
 s = requests.session() #建立request
 html = s.get(url_).text
 #print(html)
 soup=BeautifulSoup(html,'lxml')
 content=soup.findAll('script',type="text/javascript")
    
 #------------------------------------要偵測有csrf_token的那個json格式-------------------------------------------#
 for i in range(len(content)):
  if str(content[i]).find('csrf_token')!=-1:
   json_format=str(content[i])
    
 json_format=json_format.replace("<script type=\"text/javascript\">window._sharedData = ","")
 json_format=json_format.replace(";</script>","")
 json_=json.loads(json_format)
 #--------------------------------------------------------------------------------------------------------------#
    
    
 query_hash="f2405b236d85e8296cf30347c9f08c2a"
 id_=str(json_['entry_data']['ProfilePage'][0]['graphql']['user']['id'])  ##input the id  
 first="40"
 cursorlist=[]
 cursorlist.clear()
 cursorlist.append("")
 url=[]
 url.clear()
 #-------
 while cursorlist[-1]!=None:
  html = s.get("https://www.instagram.com/graphql/query/?query_hash="+query_hash+"&variables={\"id\":\""+id_+"\",\"first\":"+first+",\"after\":\""+cursorlist[-1]+"\"}").text
  json_=json.loads(html)
  node_1=json_['data']['user']['edge_owner_to_timeline_media']['edges']
  cursor=json_['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
  cursorlist.append(cursor)
  for i in range(len(node_1)):
   #print(json.dumps(node_1[i]['node']["shortcode"],indent=2,ensure_ascii=False))
   url.append(node_1[i]['node']["shortcode"])
 return url

def thread_(q,d_check,q_storage,range_):
 #print("thread_work")
 if q.qsize()==0:
  print('over')
 else:
  i=q.get()
  t=threading.Thread(target=content_comment,args=(i,d_check,q_storage,q,),daemon=True)
  while d_check.qsize()==range_:
   print("--")
   time.sleep(30)
  d_check.put(i)
  t.start()
  thread_(q,d_check,q_storage,range_)
    
 
if __name__ == '__main__':
 url_name=str(input())
 url_='https://www.instagram.com/'+url_name
 range_=20
 url=urlget(url_)   #回傳一個url的list
 d_check=queue.Queue()
 q=queue.Queue()
 q_storage=queue.Queue()
 #print("return",url)
 for i in url:
  q.put(i)
 thread_(q,d_check,q_storage,range_)

 data=[]
 data.clear()
 for i in range(q_storage.qsize()):
  data.append(q_storage.get())
 
 output=json.dumps(data,indent=2,ensure_ascii=False)
 #print(output)
 with open(url_name+'.json',"w") as f:
  f.write(output)
 f.close()

