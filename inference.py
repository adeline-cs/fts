# -*- coding: utf-8 -*-
# Author: heyue
# Date: 2020-8-6
# Email: heyue_hent@163.com
import argparse, logging
import cv2, os, time 
import docx, shutil, numpy as np 
import ocr 
from PIL import Image
from glob import glob
from post_process import filter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch,cm
import reportlab.pdfbase.ttfonts
from pre_process import remove_stamp
from pre_process import lines_eraser
import detectTable
import base64
import pycorrector
import sys  

logging.basicConfig(level=logging.INFO)
reportlab.pdfbase.pdfmetrics.registerFont(reportlab.pdfbase.ttfonts.TTFont('song', './fonts/wqy-zenhei.ttc'))
image_files = glob('./test_images/*.*')


def takeSecond(elem):
    return elem[1]


def text_line_combine(result):
    combine_result = []
    combine_list = []
    former_line_y = 0
    new_line = []
    for key in result:
        line_pos = result[key][0]
        logging.debug(line_pos)
        line = result[key][1].strip()
        x = line_pos[0]
        y = line_pos[1]
        # if result y offset less than 5 pixel, we combine this result into one line. Otherwise new line begins.
        logging.debug("offset is %s", abs(int(y) - int(former_line_y)))
        if abs(int(y) - int(former_line_y)) < 10:
            new_line.append((line, x))
        else:
            combine_list.append(new_line)
            new_line = [(line, x)]
        former_line_y = y

    for line_list in combine_list:
        line_list.sort(key=takeSecond)
        line_text = ""
        for text in line_list:
            line_text += text[0] + "           "
        combine_result.append(line_text)

    return combine_result

def text_line_combine1(result):
    combine_result = []
    combine_list = []
    former_line_y = 0
    new_line = []
    for i in range(len(result)):
        line_pos = result[i][0]
        line = result[i][1]
        prob = result[i][2]
        logging.debug("line pos:{0} ,line text:{1}, prob:{2}".format(line_pos,line,prob))
        x = line_pos[0][0]
        y = line_pos[0][1]
        #print(x, y)
        # if result y offset less than 5 pixel, we combine this result into one line. Otherwise new line begins.
        logging.debug("offset is %s", abs(int(y) - int(former_line_y)))
        if abs(int(y) - int(former_line_y)) < 10:
            new_line.append((line, x))
        else:
            combine_list.append(new_line)
            new_line = [(line, x)]
        former_line_y = y

    for line_list in combine_list:
        line_list.sort(key=takeSecond)
        line_text = ""
        for text in line_list:
            line_text += text[0] + "   "
        combine_result.append(line_text)

    return combine_result

def gen_text_result(file_name, combine_result, result, image):
    txt_out_dir = './txt_result'
    if not os.path.exists(txt_out_dir):
        os.mkdir(txt_out_dir)

    pdf_out_dir = './pdf_result'
    if not os.path.exists(pdf_out_dir):
        os.mkdir(pdf_out_dir)
    
    height = image.shape[0]
    weight = image.shape[1]
    #print(combine_result)
    f = open(os.path.join(txt_out_dir, file_name + '.txt'), 'w+')
    c = canvas.Canvas(os.path.join(pdf_out_dir, file_name + '.pdf') )
  
    c.setFont('song', 10)
    for i in range(len(result)):
        c.drawString(21.0 * result[i][0][0][0]/weight * cm, 29.7 * (height-result[i][0][0][1])/height *cm,result[i][1])
    
    for text in combine_result:
        logging.debug(text)
        #print(text)
        f.write(text)
        f.write('\n')
    f.close()
    c.save()

def test_base64decode(file):
    img_file = open(file, 'rb')  # 二进制打开图片文件
    img_b64encode = base64.b64encode(img_file.read())  # base64编码
    img_file.close()  # 文件关闭
    img_b64decode = base64.b64decode(img_b64encode)
    img_array = np.fromstring(img_b64decode, np.uint8)
    img = cv2.imdecode(img_array, cv2.COLOR_BGR2RGB)
    if not os.path.exists("./test_decode"):
        os.mkdir("./test_decode")
    basename = os.path.basename(file)
    decode_path = os.path.join('./test_decode', basename)
    cv2.imwrite(decode_path, img)

def get_correct(ocr_result):
    print("result",ocr_result)
    #print("len result",len(result))
    correct_result = []
    for k in range(len(ocr_result)):
        box_pose = ocr_result[k][0]
        box_text = ocr_result[k][1]
        box_prob = ocr_result[k][2]
        #box_center_y = (box_pose[0][1]+box_pose[1][1]+box_pose[2][1]+box_pose[3][1])/4
        #box_center_x = (box_pose[0][0]+box_pose[1][0]+box_pose[2][0]+box_pose[3][0])/4
        correct_text = pycorrector.correct(box_text)
        #print("box_text",box_text)
        #print("correct_text",correct_text)
        correct_result.append([box_pose,correct_text,box_prob])
    return correct_result
###########################################################################
## infer one image
## cpuv3.5 no line_earse parament, add rotate_img_vis,table_mask_vis,\
## table_joint_vis,table_vis_index,draw_table_vis 
## parament 
## need_text_file -> just for pdf/txt, save or no save the two form result  
## need_text_loc -> save or no save detect picture
## rotate_img_vis -> save or no save rotated and no stamp picture
## table_mask_vis -> save or no save table mask deal intermediate results
## table_joint_vis -> save or no save table joint deal intermediate results
## table_detect_vis -> save or no save detect table picture
## draw_table_vis -> just for docx, save or no save docx form result
#############################################################################


def infer(image_name, image, need_text_file=True, need_text_loc=True, rotate_img_vis=True, table_mask_vis=True, table_joint_vis=True, table_detect_vis=True,  draw_table_vis = True, use_correct = False):
    result_dir = './test_result'
    if not os.path.exists(result_dir):
        os.mkdir(result_dir)

    file_name = os.path.basename(image_name).split('.')[0]
    logging.info("System is handling image %s.", image_name)

    #test_base64decode(image_file)
    #image = np.array(Image.open(image_file).convert('RGB'))

    t = time.time()
    has_stamp=remove_stamp.detect_red(image)
    image = remove_stamp.remove_red_stamp(image)
    logging.info("System pre-deal image took %s s", time.time() - t)
    t = time.time()
    logging.debug("start ocr")
    result, image_framed = ocr.test_model(image)
    #result = filter.pos_filter(result)
    
    draw_text_boxes_dir='./draw_text_boxes'
    if not os.path.exists(draw_text_boxes_dir):
        os.mkdir(draw_text_boxes_dir)
    draw_text_boxes_path=os.path.join(draw_text_boxes_dir,file_name+'.jpg')
    
    if need_text_loc:
        cv2.imwrite(draw_text_boxes_path,image_framed)      
    
    if use_correct:
       result = get_correct(result)

    img_name = file_name +'.jpg'

    table_loc_array, line_loc_array,joint_edge_loc_array, table_type, rotate_rate = detectTable.tabledetect(img_name, image, result, rotate_img_vis, table_mask_vis, table_joint_vis, table_detect_vis, draw_table_vis)
    logging.info("the all result", result)
    combine_result = text_line_combine1(result)
    ##just for pdf and txt 
    if need_text_file:
        gen_text_result(file_name, combine_result, result, image)

    logging.info("Mission complete, it took %s s", (time.time() - t))
   
    return result, table_type, has_stamp, rotate_rate


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ocr')
    parser.add_argument("--line_erased",type=int,help="0 to turn off line eraser", default=0)
    args = parser.parse_args()

    result_dir = './test_result'
    if os.path.exists(result_dir):
        shutil.rmtree(result_dir)
    os.mkdir(result_dir)

    for file in image_files:
        image = np.array(Image.open(file).convert('RGB'))
        infer(file, image, need_text_file=True, need_text_loc=True, rotate_img_vis=True, table_mask_vis=True, table_joint_vis=True, table_detect_vis=True,  draw_table_vis = True, use_correct = False)



