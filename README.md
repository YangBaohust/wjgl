# wjgl
后端采用python3.6 + django2.2  
前端采用html + css + js  

我的本职工作是DBA，开发网站是兴趣爱好，恰好公司需要这么一个系统，因此在闲暇时间写了该项目。由于该项目本身不属于业务系统，不存在保密性要求，就将其开源，希望能帮到有同我一样需求的人，有bug可以联系我(yangbhust@163.com)  
项目的经过可以看本人博客https://www.cnblogs.com/ddzj01/p/11452940.html  

项目在最开始公开的时候，我接到了不少人发送给我的邮件，问我网站相关的问题，这给了我一些惊喜，我想不到竟然还有人关注这个项目。既然有人在看，那还是好好整理下readme，把代码review下，不误人子弟。

# 下面是项目的部分截图
登录  
![Image text](https://github.com/YangBaohust/myimages/blob/master/wjgl/login.png)

文件列表
![Image text](https://github.com/YangBaohust/myimages/blob/master/wjgl/list.png)

上传文件
![Image text](https://github.com/YangBaohust/myimages/blob/master/wjgl/upload.png)

人员管理
![Image text](https://github.com/YangBaohust/myimages/blob/master/wjgl/personlist.png)

指定能上传的ip地址
![Image text](https://github.com/YangBaohust/myimages/blob/master/wjgl/setting.png)

日志记录
![Image text](https://github.com/YangBaohust/myimages/blob/master/wjgl/loglist.png)

# 文件管理系统开发手册  
一、开发需求  
根据公司安全性要求，公司内部所有电脑的USB端口以及类似“百度网盘”等云服务都被禁止使用。但由于实际工作需要，员工有将外部文件拷入到内网和将内网文件拷出到外网的需求，因此需要一个文件管理系统。  

二、系统功能  
当员工将外部文件拷入到内网中时，需要在指定的电脑（已开放USB端口）通过该系统上传文件，并且该文件会永久保存到系统中，同时生成上传的日志，供后期稽核。当员工将内网中的文件拷出时，首先需要提交纸质申请单，填写申请下载的文件号，经过审批后，方可在指定的电脑通过该系统下载文件，并生成下载的日志。员工通过自身办公电脑上传下载文件并不受限制。  

三、系统详细介绍  
1. 登录  
 用户名填写工号或者姓名，初始密码是“123456”  
 
2. 网站角色  
网站一共有三种角色：普通用户、系统管理员、稽核监察员  

普通用户拥有的功能：  
a 上传和下载文件  
b 修改密码  

系统管理员拥有的功能：  
a 上传和下载文件  
b 修改密码  
c 对人员进行管理，添加用户，分配角色，密码重置  
d 对文件进行终审，但不能对自身上传的文件进行终审  
e 填写开放了USB端口的电脑IP地址  

系统管理员拥有的功能：  
a 上传和下载文件  
b 修改密码  
c 对文件进行审批，根据子角色的不同分为一审和二审  
d 能查看所有人上传的文件  
e 能将所有人上传的文件名称导出为excel  
f 能查看所有人的上传和下载记录  

3. 文件上传和下载  
文件上传限定在每个文件500M以内，并且不允许上传bat和exe格式文件。文件如需在公用电脑下载，需要经过一审、二审、终审都通过后，方可下载。文件在一审和二审的过程中，一审员和二审员可以查看该文件的具体内容。  
