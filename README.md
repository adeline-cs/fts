# FTS（Fast Text Spotting）
version cpu v3.6

#### 项目介绍
武汉大学大规模OCR引擎FTS，专注于通用场景的实时文字识别，表格下划线等多文本识别，追求高速率、高性能和高准确率。


#### 环境搭建

linux 16.04 docker
cpu 环境版本 
python 3.5
相关依赖 requirement.txt



#### 使用说明
1.单跑批量识别任务，可以执行```python inference.py```
程序将识别test_images目录下的图片，并将识别结果放置于txt_result，pdf_result，test_result文件夹下；
可设置参数 need_text_file, need_text_loc, rotate_img_vis, table_mask_vis, table_joint_vis, table_detect_vis,  draw_table_vis, use_correct

need_text_file -> 是否保存pdf/txt结果文档,对应结果文件夹pdf_result与txt_result.
need_text_loc -> 是否保存检测结果图片，对应结果文件夹draw_text_boxes.
rotate_img_vis -> 是否保存预处理(旋转矫正、去红章)后的图片，对应结果文件夹 rotate_images.
table_mask_vis -> 是否保存表格检测mask结果，常规设置为"False".
table_joint_vis -> 是否保存表格检测joint结果，常规设置为"False".
table_detect_vis -> 是否保存表格检测joint结果，常规设置为"False"
draw_table_vis -> 是否保存表格检测结果图片.
use_correct -> 是否使用文字矫正后的结果，常规设置为"False"，建议根据实际情况修改my_custom_confusion.txt后，借鉴my_custom_confusion.py代码配套使用。

2.若以服务请求的方式请求OCR任务，可以先执行```python flask_server.py```部署好FTS算法服务器，后面执行```python flask_client.py```模拟客户端请求OCR服务。

识别服务请求
```
http请求方式， POST， http协议

发送例子：

                img_file = open(image_path, 'rb')
                save_extension='pdf'
                img_b64encode = base64.b64encode(img_file.read())
                res = {"image": img_b64encode,
                       "image_name": image_list[i],
                       "name": "ocr_req",
                       "need_text_file": "True",
                       "need_text_loc": "True",
                       "rotate_img_vis": "True",
                       "table_detect_vis": "True",
                       "save_docx": "True",
                       "use_correct": "False",
                       "save_extension": save_extension
                      }
                s = requests.post("http://" + HOST + ":" + str(PORT), data=json.dumps(res))
    

文件传输服务请求
```
http请求方式，GET， http协议

发送例子：

                url= "http://"+ HOST + ":" + str(PORT)+'/'+response_path
                save_path=result_dir+image_list[i].split('.')[0]+'.'+save_extension
                try:
                    urllib.urlretrieve(url,save_path)
                except Exception as e:
                    print("Error occurred when downloading file, error message:")
                    print(e)
```

识别服务返回
```

                    client 0 rev a response:{"has_stamp": 1, "download": "pdf_result/20181022100900543.pdf", "table_type": 2, "rotate_rate": 0.0025595965898362614, "part": "{'box_id': 0, 'location': {'top_left_y': 351, 'bottom_right_y': 395,} 'top_left_x': 705, 'bottom_right_x': 967}, 'result': '寿光市公安局'}{'box_id': 1, 'location': {'top_left_y': 432, 'bottom_right_y': 496, 'top_left_x': 682, 'bottom_right_x': 976}, 'result': '传唤证'}{'box_id': 2, 'location': {'top_left_y': 526, 'bottom_right_y': 575, 'top_left_x': 732, 'bottom_right_x': 933}, 'result': '(副本)'}{'box_id': 3, 'location': {'top_left_y': 667, 'bottom_right_y': 718, 'top_left_x': 909, 'bottom_right_x': 1482}, 'result': '寿公(城)传唤字[2018]2号'}{'box_id': 4, 'location': {'top_left_y': 791, 'bottom_right_y': 851, 'top_left_x': 261, 'bottom_right_x': 1435}, 'result': '根据《中华人民共和国刑事诉讼法》第一百一十七条之规定'}{'box_id': 5, 'location': {'top_left_y': 888, 'bottom_right_y': 940, 'top_left_x': 176, 'bottom_right_x': 580}, 'result': '兹传唤涉嫌聚众斗殴'}{'box_id': 6, 'location': {'top_left_y': 889, 'bottom_right_y': 946, 'top_left_x': 917, 'bottom_right_x': 1419}, 'result': '的犯罪嫌疑人此秀华'}{'box_id': 7, 'location': {'top_left_y': 967, 'bottom_right_y': 1037, 'top_left_x': 181, 'bottom_right_x': 1482}, 'result': '(性别男,出生日期1994年03月08日,住址云南省怒江傈便族自'}{'box_id': 8, 'location': {'top_left_y': 1054, 'bottom_right_y': 1102, 'top_left_x': 178, 'bottom_right_x': 660}, 'result': '治州福贡县架科底乡阿打村'}{'box_id': 9, 'location': {'top_left_y': 1070, 'bottom_right_y': 1111, 'top_left_x': 1387, 'bottom_right_x': 1471}, 'result': ')于'}{'box_id': 10, 'location': {'top_left_y': 1156, 'bottom_right_y': 1203, 'top_left_x': 223, 'bottom_right_x': 1240}, 'result': '2018年09月21日23时到寿光市公安局城区派出所'}{'box_id': 11, 'location': {'top_left_y': 1238, 'bottom_right_y': 1293, 'top_left_x': 169, 'bottom_right_x': 1224}, 'result': '接受讯问。无正当理由拒不接受传唤的,可以依法拘传'}{'box_id': 12, 'location': {'top_left_y': 1409, 'bottom_right_y': 1465, 'top_left_x': 1107, 'bottom_right_x': 1448}, 'result': '头寿光市公安局'}{'box_id': 13, 'location': {'top_left_y': 1491, 'bottom_right_y': 1567, 'top_left_x': 882, 'bottom_right_x': 1405}, 'result': '二O一八年九月二十一日助'}{'box_id': 14, 'location': {'top_left_y': 1657, 'bottom_right_y': 1727, 'top_left_x': 243, 'bottom_right_x': 600}, 'result': '本证已于2018'}{'box_id': 15, 'location': {'top_left_y': 1652, 'bottom_right_y': 1744, 'top_left_x': 695, 'bottom_right_x': 1184}, 'result': '4月24日收到:'}{'box_id': 16, 'location': {'top_left_y': 1730, 'bottom_right_y': 1847, 'top_left_x': 491, 'bottom_right_x': 950}, 'result': '被传唤人:香出'}{'box_id': 17, 'location': {'top_left_y': 1756, 'bottom_right_y': 1800, 'top_left_x': 955, 'bottom_right_x': 1180}, 'result': '(捺指印)'}{'box_id': 18, 'location': {'top_left_y': 1819, 'bottom_right_y': 1909, 'top_left_x': 230, 'bottom_right_x': 1298}, 'result': '被传唤人到达时间2618年90月21日23时,'}{'box_id': 19, 'location': {'top_left_y': 1909, 'bottom_right_y': 1998, 'top_left_x': 486, 'bottom_right_x': 1190}, 'result': '被传唤人:的法的(播指印)'}{'box_id': 20, 'location': {'top_left_y': 2003, 'bottom_right_y': 2058, 'top_left_x': 238, 'bottom_right_x': 651}, 'result': '传唤结束时间9518'}{'box_id': 21, 'location': {'top_left_y': 2002, 'bottom_right_y': 2070, 'top_left_x': 734, 'bottom_right_x': 1245}, 'result': '年9二月22日09时,'}{'box_id': 22, 'location': {'top_left_y': 2068, 'bottom_right_y': 2182, 'top_left_x': 485, 'bottom_right_x': 946}, 'result': '被传唤人此香他'}{'box_id': 23, 'location': {'top_left_y': 2095, 'bottom_right_y': 2138, 'top_left_x': 913, 'bottom_right_x': 1184}, 'result': '(捺指印)'}{'box_id': 24, 'location': {'top_left_y': 2203, 'bottom_right_y': 2247, 'top_left_x': 192, 'bottom_right_x': 345}, 'result': '此联附卷'}", "img_name": "20181022100900543.jpg"}pdf_result/20181022100900543.pdf http://127.0.0.1:9997/pdf_result/20181022100900543.pdf  ./receive_result/20181022100900543.pdf

```

文件传输服务返回
```
               本地路径save_path为传输文件
```

3.可单独运行文词纠正，启动```python use_custom_confusion.py```进行自定义字典文词纠正。 

#### 参与贡献

1. AI架构设计：网络库设计、微服务框架设计、高性能任务调度，可并行多进程多客户端使用。
2. OCR算法设计：CTPN+CRNN -> densenet+crnn ->yolov3(darkent)+crnn -> dbnet+cnn_lite_lstm。
3. 图像预处理：旋转矫正、检测红章指纹、图片去红章等。
4. 表格、纯文本、下划线图片一体式检测识别处理。
5. 支持docx二次编辑文件录入。
6. 自定义字典部分文词矫正。




## 武汉大学OCR引擎FTS的使用手册v3.6
  1. 下载解压本项目代码
  2. 若已经有FTS容器在运行，则```docker exec -it containerID /bin/bash```
  3. 对于CPU版本环境:若无FTS容器实例存在，则先建立docker image FTS引擎的容器：第一步先拉取镜像```docker pull registry.cn-hangzhou.aliyuncs.com/heyue_2020/fts2020:v3.6```，第二步启动容器 ```docker run -it -p 9998:9998 -v your_FTS_project_path:/FTS registry.cn-hangzhou.aliyuncs.com/heyue_2020/fts2020:v3.6```
  4. 进入FTS容器后，我们先```cd FTS```，先将我们要P识别的图片放在/FTS/test_image文件夹下，确保编译环境识别中文，每个需要运行的docker容器```source /etc/profile```，然后我们在路径/FTS下执行```python inference.py```就可以开始对待识别的图片进行识别，识别结果以txt文件的形式会放在/FTS/txt_result文件夹下，同时在/FTS/test_result下会有文字检测结果的图像。
  5. 或者我们启动```python flask_server.py``` 启动OCR服务器进程（进程IP和Port可以在文件flask_server.py里修改）。同时需要写一个请求服务的客户端模拟请求，我写了个模拟器，```python flask_client.py```，模拟了整个服务请求流程。如果需要传输识别结果文件，只需要修改请求服务的客户端请求，save_extension修改为需要的文件后缀。
need_text_file为是否保存识别结果相关pdf及txt文件，need_text_loc为是否保存文字检测结果图片，rotate_img_vis为是否保存旋转后的图片结果，table_detect_vis为是否保存表格检测结果图片，save_docx为是否保存识别结果相关docx文件.若save_extension设置为"pdf"或"txt"，对应的need_text_file需设置为"True",若save_extension设置为"docx"，对应的save_docx需设置为"True".
  6. 可同时启动多个flask_client.py,服务器可同时处理。在flask_server.py内部设置limitworker为同时处理的请求数，其中q=Queue(n)中n为设置最大存在的client数量。
  7. 其中detectTable.so对应表格检测结果, use_custom_confusion.py用于自定义的文字纠错，配套my_custom_confusion.txt使用。我们启动```python use_custom_confusion.py```来进行对应文字的纠错，通过修改my_custom_confusion.txt实现错误文字纠错为已设置好的文字内容。

### 目录介绍
一级目录
dbnet: 文本检测的算法代码
crnn: 不定长文字识别算法代码
fonts: 生成的pdf文字的字体
network_lib: 项目的网络库、调度框架
pycorrector: 文字纠错的算法代码
models: 已训练好的网络模型权重
pre_process: 图像预处理算法，包括去直线，移除红章等
post_process: 识别后处理算法
test_images: 待识别的图像
no_stamp_images: 无印章处理图片结果
draw_text_boxes:文本检测结果
table_vis_images: 表格检测可视化结果
rotate_images: 旋转角度后图片结果
pdf_result: 识别出来pdf文件结果
txt_result: 识别出来的txt文件结果
docx_result: 识别出来的docx文件结果
test_result: 文本检测结果
receive_result: 模拟客户端下载后的保存文件夹


本项目提供2种运行模式
模式一：批量识别模式
指定目录批量识别图像，识别后的结果放置于指定目录。python inference.py
模式二：算法服务器形式
Python flask_server.py 启动服务器




