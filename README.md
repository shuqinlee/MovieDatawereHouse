# MovieDatawereHouse

1. `git clone https://github.com/shuqinlee/MovieDatawereHouse.git`

2. 下载 Scrapy 这个python包 `pip install scrapy`

3. 进入tutorial里面，编辑config.txt

   ```
   Processed: 'processed.txt' # 存取已经处理过的页面的文件路径
   Input: 'amazon_addr2.txt' # 输入文件路径，根据你们爬的
   ```

   注意保留单引号，编辑完保存。

4. terminal 中运行下面的命令开始爬数据
  `scrapy crawl amazon -o xxx.json`

  `xxx.json`是输出的爬取数据文件，各位自定义

5. 运行lineNo.py查看当前爬到了多少数据，与所爬文件大小对比。因为amazon很多网页不存在了，所以不会完全相等。接近所爬文件大小即可。
6. 一次完全爬，因为会反扒。不断运行`scrapy crawl amazon -o xxx.json`命令爬就可以了。不用修改`xxx.json`.最后解析的时候需要稍微改一下。



文件

| 文件名              | 条数    |
| ---------------- | ----- |
| amazon_addr1.txt | 49999 |
| amazon_addr2.txt | 50000 |
| amazon_addr3.txt | 50000 |
| amazon_addr4.txt | 50000 |
| amazon_addr5.txt | 53060 |

