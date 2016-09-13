# nlp-sentiment-analysis
文本情感分析

## 数据来源
使用 scrapy 爬取豆瓣电影影评
```
cd spide
//input.txt 输入电影名称
//output.txt 输出电影影评(评分、评论内容)
cd Douban
scrapy crawl douban
```

## 文本处理
jieba/THULAC分词，计算TF-IDF，训练分类器  


## 机器学习--分类器
1. 朴素贝叶斯  
2. SVM  
实现使用 sklearn


## 深度学习--神经网络
1. 卷积神经网络  
2. 迭代神经网络  
实现使用 tensorflow 或者 keras
