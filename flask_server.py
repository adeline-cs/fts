#coding:utf-8
# Author: heyue
# Date: 2020-8-6
# Email: heyue_hent@163.com
from flask import request, Flask, send_from_directory, make_response
import json
import numpy as np
import cv2
import time
import logging
import base64
from inference import infer
from PIL import Image
import io
from multiprocessing import Queue
logging.basicConfig(level=logging.INFO)
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

decode_img_dir = "./decode_img"
ALLOWED_EXTENSIONS = ['txt','pdf','docx','jpg','xls','JPG','PNG','xlsx','gif','GIF']
txt_out_dir = './txt_result'
pdf_out_dir = './pdf_result'
docx_out_dir = './docx_result'
timeworker=0
limitworker=3
q=Queue(20)  # 2*client_num


def base64toImg(base64str):
    img_b64decode = base64.b64decode(base64str)
    # img_array = np.fromstring(img_b64decode, np.uint8)
    # img = cv2.imdecode(img_array, cv2.COLOR_BGR2RGB)
    image = io.BytesIO(img_b64decode)
    img = np.array(Image.open(image).convert('RGB'))
    return img


def decoding_json(req):
    img_name = req["image_name"]
    frame = req["image"]
    frame = base64toImg(frame)
    if not os.path.exists(decode_img_dir):
        os.mkdir(decode_img_dir)
    cv2.imwrite(os.path.join(decode_img_dir, img_name), cv2.cvtColor(frame,cv2.COLOR_RGB2BGR))
    frame = np.array(Image.open(os.path.join(decode_img_dir, img_name)).convert('RGB'))
    need_text_file = str(True) == req["need_text_file"]
    need_text_loc = str(True) == req["need_text_loc"]
    rotate_img_vis = str(True) == req["rotate_img_vis"]
    table_detect_vis = str(True) == req["table_detect_vis"]
    table_text_save_req = str(True) == req["save_docx"]
    use_correct = str(True) == req["use_correct"]
    download_text_extension=req["save_extension"]
    
    return img_name, frame, need_text_file, need_text_loc, rotate_img_vis, download_text_extension, table_detect_vis, table_text_save_req, use_correct


def build_result(result):
    result_t=[]
    #print(len(result))
    #print(result)
    #print(len(result[2]))
    keys=list(result.keys())
    for i in keys:
        values=result[i]
        text_recs=values[0]
        text_context=values[1]
        if text_recs[0]>=text_recs[4]:
            top_left_x=text_recs[4]
        else:top_left_x=text_recs[0]
        if text_recs[1]>=text_recs[3]:
            top_left_y=text_recs[3]
        else:top_left_y=text_recs[1]
        if text_recs[2]>=text_recs[6]:
            bottom_right_x=text_recs[2]
        else:bottom_right_x=text_recs[6]
        if text_recs[5]>=text_recs[7]:
            bottom_right_y=text_recs[5]
        else:bottom_right_y=text_recs[7]
            
        result_t.append({"box_id":i,
                  "result":text_context,
                  "location":{"top_left_x":top_left_x,
                                  "top_left_y":top_left_y,
                                  "bottom_right_x":bottom_right_x,
                                  "bottom_right_y":bottom_right_y}})
    text_result=result_t    
    return text_result

def build_result1(result):
    result_t = []
    for i in range(len(result)):
        line_pos = result[i][0]
        line = result[i][1]
        prob = result[i][2]
        top_left_x = line_pos[0][0]
        top_left_y = line_pos[0][1]
        bottom_right_x = line_pos[2][0]
        bottom_right_y = line_pos[2][1]
        result_t.append({"box_id":i,
                  "result":line,
                  "location":{"top_left_x":top_left_x,
                                  "top_left_y":top_left_y,
                                  "bottom_right_x":bottom_right_x,
                                  "bottom_right_y":bottom_right_y}})
    text_result=result_t    
    return text_result

def build_response(text_result, img_name, download_result,table_type,has_stamp,rotate_rate):
    s = ''.join(map(str,text_result))
    res = {"img_name": img_name,
           "has_stamp":has_stamp,
           "table_type":table_type,
           "part": s, 
           "download": download_result,
           "rotate_rate":rotate_rate
          }
    
    #print(type(res["img_name"]))
    #print(type(res["has_stamp"]))
    #print(type(res["table_type"]))
    #print(type(res["part"]))
    #print(type(res["download"]))
    #print(type(res["rotate_rate"]))
    return res

###add download message
def download_text(image_file,text_save_req, text_loc_save_req, download_text_extension): 
    filename = os.path.basename(image_file).split('.')[0]
    if text_save_req:
        print("start download")
        if download_text_extension in ALLOWED_EXTENSIONS:
            dir_name=download_text_extension+'_'+'result'
            root_path=os.getcwd()     
            file_dir=os.path.join(root_path,dir_name)
            file_name=filename+'.'+download_text_extension
            file_path=os.path.join(dir_name,file_name)
            #print(file_dir)
            #print(file_name)
            print(file_path)                  
    return file_path 
 
def ocr_reco(req):
    image_file, image, need_text_file, need_text_loc, rotate_img_vis, download_text_extension, table_detect_vis, table_text_save_req, use_correct= decoding_json(req)
    result, table_type,has_stamp,rotate_rate = infer(image_file, image, need_text_file, need_text_loc, rotate_img_vis, False, False, table_detect_vis, table_text_save_req, use_correct)
    text_result = build_result1(result)
    download_result= download_text(image_file,need_text_file, need_text_loc, download_text_extension)
    reponse_dict = build_response(text_result, image_file, download_result, table_type, has_stamp, rotate_rate)
    response_json = json.dumps(reponse_dict)
    return response_json



app = Flask(__name__)


@app.route("/", methods=['POST'])
def ocr():
    start_time = time.time()
    req = json.loads(request.data.decode())
    global timeworker
    global limitworker
    timeworker=timeworker+1
    print("timeworker", timeworker)
    global q
    q.put(req)
    if timeworker <limitworker:      
        value=q.get()
        response = ocr_reco(value)
        timeworker=timeworker-1     
    else:
        time.sleep(5)
        value=q.get()
        response = ocr_reco(value)
        timeworker=timeworker-1 
    duration = time.time() - start_time
    print('duration:[%.0fms]' % (duration*1000))
    return response
 
###add download file
@app.route("/<filepath>/<filename>",methods=['GET'])
def downloader(filepath, filename):
    root_path=os.getcwd()
    file_dir=os.path.join(root_path,filepath)
    response=make_response(send_from_directory(file_dir, filename, as_attachment=True))
    response.headers["Content-Disposition"]="attachment;filename={}".format(filename.encode().decode('latin-1'))### maybe error 5 : the headers write error 
    return response

'''
@app.route("/", methods=['GET'])
def show_page():
    return 'Hello FTS!'
'''

if __name__ == "__main__":
    app.run("127.0.0.1", port=9997)  #端口为8081
