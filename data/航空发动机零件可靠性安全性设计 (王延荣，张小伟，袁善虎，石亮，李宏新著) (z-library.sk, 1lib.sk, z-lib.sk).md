![](images/f45a41e9456b1f9dcf092f3cdeae1b356e615089f674edacc088add1b1030481.jpg)

# 航空发动机零件可靠性安全性设计

# The Reliability and Safety Design of Aero Engine Components

王延荣等著

# 航空工北出版社

# 航空发动机零件可靠性安全性设计

# 航空工业出版社北京

# 内容提要

本书是一本关于航空发动机可靠性与安全性的学术理论专著，内容涉及航空发动机结构疲劳、高温结构蠕变、空心风扇叶片结构优化设计，以及圆弧形榫连结构寿命预测、叶片气动弹性稳定性预测方法、叶片颤振机制及其影响参数、转动结构疲劳可靠性、含缺陷粉末盘结构疲劳和轮盘结构安全性预测等方面。

本书可为从事航空发动机结构强度、可靠性与安全性研究人员提供一定的参考，也可作为航空发动机专业师生的教材用书。

# 图书在版编目（CIP）数据

航空发动机零件可靠性安全性设计/王延荣等著--北京：航空工业出版社，2018.6ISBN978-7-5165-1738-3

1. $\textcircled{1}$ 航…Ⅱ $\textcircled{1}$ 王…Ⅲ $\textcircled{1}$ 航空发动机-零部件—安全可靠性-设计 ⅣV. $\textcircled{1}$ V232

中国版本图书馆CIP数据核字(2018)第282495号

航空工业出版社出版发行（北京市朝阳区北苑2号院 100012）发行部电话：010-84936597010-84936343  
三河市华骏印务包装有限公司印刷 全国各地新华书店经售  
2018年6月第1版 2018年6月第1次印刷  
开本： $7 8 7 \times 1 0 9 2$ 1/16 印张：24 字数：567千字  
印数：11500 定价：96.00元

# 前 言

近年来，航空燃涡轮发动机设计和制造技术的持续进步在使发动机性能逐步提升的同时，也使其结构完整性和可靠性得到了显著提。尽管如此，作为复杂热动旋转机械的航空发动机在研制和使中仍时有问题出现，如常见的结构件故障多为裂纹甚断裂，严重迟滞新机研制进程，并可能危及现役发动机的使安全。先进航空飞器对其动装置的性能和可靠性要求越来越，也就对发动机结构设计提出了更的要求。因此，迫切需要出版这方面的专业性学术著作，以便更好地为当前航空发动机的研制和使用发展服务。

多年前，作为编者之，我参加了《航空涡喷、涡扇发动机主要零部件定寿指南》（航空工业出版社，2004）的编写，为此航空工业出版社副总编辑刘宁建议在其基础上进修订，以《航空发动机零件可靠性安全性设计》为书名出版，并列了出版计划。由于《航空涡喷、涡扇发动机主要零部件定寿指南》的内容与《航空发动机零件可靠性安全性设计》的含义有差异，加之我只是当时的编者之，修订也实属不易，故决定重新编写，当然内也感到很惶恐。

《航空发动机零件可靠性安全性设计》主要是我和与我起学习和作的博士、硕研究生近十年来针对航空发动机结构件——叶/盘转子等零件在疲劳、蠕变、颤振，以及结构可靠性和安全性等方面所开展的研究工作基础上撰写的，内容主要取材于他们的学位论文工作。

本书共9章，各章主要内容为：“结构疲劳设计分析方法”重点考虑了平均应力、应力梯度和尺寸效应等对实际构件疲劳寿命的影响；“高温结构蠕变设计分析方法”着重发展了能完整刻画蠕变三个阶段变形为的归一化参数模型，实现了涡轮叶/盘结构蠕变预测设计分析；“空风扇叶结构优化设计法”重点针对叶壁板、内部结构，以及叶型积叠等给出了多标优化策略和实现法；“圆弧形榫连结构接触分析及寿命预测”主要针对涵道涡扇发动机风扇叶榫连结构发展并形成了疲劳寿命预测法和流程；“动弹性稳定性预测设计的能量法”重点发展了叶动格技术，以及结构与绕流场的耦合界面上位移和压等信息的传递算法，由叶个振动周期内的定常气动（累积）功得到了模态动阻尼比，实现了颤振预测；“叶颤振机制及其影响参数分析”着重考察了叶模态、进流攻、折合频率、进相对马赫数、激波与波后流分离、叶间相位等参数，以及多级环境的影响；“转动结构疲劳可靠性分析方法”重点针对轮盘结构的应力疲劳和考虑应力梯度影响的疲劳，以及叶振动的可靠性预测给出了设计分析方法和流程；“含缺陷粉末盘结构疲劳设计分析方法”着重考察了孔洞和夹杂等典型缺陷的形状、大小及其出现位置对构件应力和疲劳寿命的影响，给出了预测设计法和分析流程；“轮盘结构安全性预测分析法”重点针对粉末冶构件因所含孔洞和夹杂等典型缺陷引起的疲劳给出了失效概率预测分析方法和流程，并对含“孔”结构及其艺特征的轮盘因缺陷导致疲劳失效给出了概率分析法和流程。需要说明的是，书中部分方法和流程已在航空发动机研究院所的设计工作中得到了应用；本书所提供的方法及分析流程虽针对轮盘和叶片等转动结构件，却有一定的普适性，亦可用于其他结构件。

本书各章的撰写人为：第1章，王延荣、李宏新、袁善虎；第2章，李宏新、程域钊、王延荣；第3章，石亮、王延荣；第4章，石亮、王延荣、杨剑秋；第5章，张小伟、王延荣；第6章，张小伟、王延荣；第7章，蒋向华、王延荣、冯欢欢；第8章，袁善虎、王延荣；第9章，魏大盛、王佳良。全书最终由王延荣定稿。

本20世纪80年代中期起在北京航空航天学求学，后研究毕业留校任教，多年来直从事与航空发动机结构强度、振动及寿命和可靠性面相关的教学科研作。30多年来，感谢师对我的指导、同事给我的帮助，以及与我起学习和作的研究生，与其就相关问题的研讨和交流，使我不断思考，大有裨益。这，要特别感谢我不同求学时期的导师：宋兆泓教授、孔瑞莲教授、周盛教授和郑祺选教授，以及我所在的航空推进系（原结构强度教研室）恩师饶寿期教授、朱梓根教授和李其汉教授，是您们引领我向职业生涯。

构成本书内容的相关研究作多年来得到了航空发动机研究院所的大力持，以及国家自然科学基（项目批准号：50571004，51475022）的资助。与航空发动机研究院所设计研究员讨论和交流，使我对程背景和问题的物理本质有了更深刻的认识，这我尤其要感谢沈阳发动机研究所杨士杰研究员和张连祥研究员多年来的指导和帮助。在本书即将出版之际，感谢北京航空航天学刘大响院、方韧教授和桂幸民教授对本书的指导与持、航空业出版社刘副总编辑的信任，以及两年多来吕烨编辑的耐心和帮助。

航空燃涡轮发动机结构完整性涉及结构强度、振动、寿命，以及可靠性和安全性等多个面，专业领域泛。本书内容涉及面较宽、各章内容相对独、体例亦不尽统一，尤其是受研究作和认识的局限，书中不妥之处在所难免，敬请您批评、指正，并提出宝贵的意见和建议。

# 目 录

# 第1章 结构疲劳设计分析方法 （1）

1.1 引 …(1】

1.2 总应变寿命程参数的确定法 …(3)

1.2.1材料试验数据…

1.2.2确定材料疲劳参数的传统方法… (4)

1.2.3 确定总应变寿命方程参数的一种新方法 …（8）

1.2.4材料疲劳参数的对比分析 （13）

1.3 考虑应力梯度影响的缺口疲劳寿命预测方法

1.3.1TC4钛合金材料数据 （16）  
1.3.2局部应力/应变法 （18）  
1.3.3 考虑应力梯度影响的缺口疲劳寿命预测 （24）

1.4 涡轮盘结构疲劳寿命评估流程及法 …(31)

1.4.1涡轮盘结构疲劳寿命评估流程 …（31）  
1.4.2涡轮盘结构的应力/应变分析. （33）  
1.4.3 涡轮盘结构的疲劳寿命预测 （38）

1.5小结 47)

参考文献 …(48）

# 2章 高温结构蠕变设计分析方法 （ 50

2.1引 ( 50）

2.2种基于归化参数的蠕变模型 …( 51)

2.2.1基于归一化参数蠕变模型的构造 …(51)  
2.2.2 基于归一化参数蠕变模型的验证 （53）  
2.2.3 基于归一化参数蠕变模型的改进 （55）  
2.2.4 各向异性材料的归一化参数蠕变模型 （56）  
2.2.5 归一化参数蠕变模型中相应参数的确定方法 ( 58）

2.3 归化参数蠕变模型的程序实现及验证

2.3.1归一化参数蠕变模型的子程序实现 …(62)

2.3.2 归一化参数蠕变模型的usercreep子程序的考核验证 …(66)

2.3.3 Usercreep子程序计算精度和时间的对比分析… …（ 71)

2.3.4变载条件下的蠕变行为 ( 72)

2.3.5应力松弛效应的计算分析示例 ( 75)

# 2.4 涡轮盘与叶结构的蠕变分析 …( 7)

2.4.1 涡轮盘的蠕变分析 （78）  
2.4.2 涡轮转子叶片的蠕变分析 …(86)

2.5 小结 …（95）参考文献 （97）

# 第3章 空心风扇叶结构优化设计方法 ……(99)

3.1 引 …（99)

3.2 空风扇叶结构设计流程 …（99)

3.2.1设计框架 …(99  
3.2.2冷态叶型的迭代解法 （101

3.3 空腔结构优化设计技术及算例 （102）

3.3.1 优化策略与关键技术 （102）  
3.3.2 空心风扇叶片初始叶型的确定 （108）  
3.3.3 空心风扇叶片的参数化建模 （109）  
3.3.4基于组合优化策略的优化分析 （111）

# 3.4 叶径向积叠优化 （116

3.4.1优化设计方法及策略 （116）3.4.2 单目标下的径向积叠优化 （119）3.4.3 多目标下的径向积叠优化 （125）参考文献 （128）

# 第4章 圆弧形榫连结构接触分析及寿命预测 (1

4.1 引 （130

4.2 圆弧形榫连结构低循环疲劳试验 （131）

4.2.1 试验件设计… （131）  
4.2.2试验过程及结果 （131）

4.3 榫连结构接触有限元分析 （134）

4.3.1有限元建模… （134）  
4.3.2 接触应力分布特征 （135）  
4.3.3 接触状态特征 （137）  
4.3.4 循环加载下的接触分析 （139）

4.4 圆弧形榫连结构疲劳寿命预测法 （142）

4.4.1基于临界面法的疲劳寿命预测 ……(142)

4.4.2 考虑应力梯度影响的寿命预测 …(145)

4.4.3基于二维有限元分析的寿命预测 （148）

4.4.4基于三维有限元分析的寿命预测 （153）

参考文献 （167）

# 第5章 气动弹性稳定性预测设计的能量法 （1i

5.1 叶动弹性稳定性理论模型 ——能量法

5.1.1 叶片气动弹性稳定性计算模型 （169）  
5.1.2 界面信息传递与多层动网格技术 （171）  
5.1.3 气动等效的模态阻尼比 （176）

5.2 能量法的叶颤振边界预测——NASA67转算例 （178）

5.2.1计算模型 （178）  
5.2.2 叶片模态分析 （180）  
5.2.3定常流场分析 （182）  
5.2.4非定常流场分析 （185）  
5.2.5 叶片颤振边界预测 （187）

5.3 能量法的叶颤振边界预测——某压机第级转算例… （190）

5.3.1叶片颤振试验简介 （190）  
5.3.2计算模型… （192）  
5.3.3 叶片模态分析 …（193)  
5.3.4定常流场分析 （194）  
5.3.5叶片颤振边界预测 （197）

5.4小结 .(199)

参考文献 (200）

# 第 ${ \mathfrak { G } }$ 章 叶颤振机制及其影响参数分析 …(201

6.1 叶结构参数 （201

6.1.1 叶片模态… （201）  
6.1.2叶间相位角 （203）

6.2 叶动参数 （205）

6.2.1进口气流攻角 (205）  
6.2.2折合频率… （206）  
6.2.3 进口相对马赫数 … （207）  
6.2.4 激波与波后气流分离 （208）

6.3 双级压机叶颤振 …(211)

6.3.1 叶片颤振试验简介 (211）  
6.3.2叶片模态分析… （216）  
6.3.3定常流场分析 （216）  
6.3.4 非定常流场分析及颤振边界预测 （219）

6.4 小结… （223）

# 参考文献 （223

# 第7章 转动结构疲劳可靠性分析方法 （224）

# 7.1 引 （224）

7.1.1 结构可靠性 （224）  
7.1.2 结构设计的概率表征 （224）  
7.1.3 结构概率响应分析 （225）  
7.1.4 结构可靠性设计 (226）

7.2 涡轮盘结构可靠性设计法 （226）

7.2.1涡轮盘结构特征和载荷/环境的概率表征方法· （226）  
7.2.2涡轮盘结构单一失效模式的可靠性模型 （235）  
7.2.3 涡轮盘结构可靠性算法的程序实现… （237）  
7.2.4 涡轮盘结构应力疲劳可靠性分析 (243）  
7.2.5涡轮盘结构疲劳可靠性分析 （252）

7.3 涡轮叶结构可靠性试验及其评定法… (264）

7.3.1 涡轮叶片结构可靠性评定方法简介 （264）  
7.3.2 涡轮叶片结构危险截面及寿命考核点的确定 （264）  
7.3.3 试验载荷谱与等效加速试验载荷谱 （265）  
7.3.4试验结果及其统计分析 （267）

7.4 叶结构振动可靠性设计法 (269)

7.4.1结构振动可靠性模型 （269）  
7.4.2 多参数具有分散性的叶片结构振动可靠性模型 (273）  
7.4.3 叶片结构振动可靠性分析流程与数值算法的实现 （274）  
7.7.4叶片结构振动可靠性评估示例 (275）  
参考文献

（279）

# 第8章 含缺陷粉末盘结构疲劳设计分析方法 (282)

8.1 引 （282）

8.2 含缺陷结构有限元数值分析的何建模 (283）

8.3 缺陷对局部应集中影响的数值模拟 （285）

8.3.1缺陷类型对局部应力集中影响的数值模拟 （285）  
8.3.2 缺陷形状对局部应力集中影响的数值模拟 (287）  
8.3.3 缺陷位置对局部应力集中影响的数值模拟 （289）

# 8.4 缺陷对疲劳裂纹萌寿命影响 （293）

8.4.1考虑应力集中影响的寿命预测方法对比分析 （293）  
8.4.2参考试样及寿命预测模型的选取. (309）  
8.4.3 不同位置及尺寸大小的球形孔洞对疲劳寿命的影响 （309）

8.5 含缺陷结构的损伤容限分析法 （311

8.5.1 FGH97合金裂纹扩展试验 (312）

8.5.2 FGH97合金缺口试样裂纹扩展分析 （313）

3.6 含缺陷FGH97粉末盘寿命预测 （316

8.6.1 FGH97粉末盘应力/应变分析 (316）  
8.6.2 FGH97粉末盘低循环疲劳寿命预测… (319）  
8.6.3 含缺陷FGH97粉末盘疲劳裂纹萌生寿命预测 （320）  
8.6.4含缺陷FGH97粉末盘损伤容限分析… (325）  
参考文献… …(327)  
第9章 轮盘结构安全性预测分析方法 （331）  
9.1 引… （331）  
9.2 寿命预测概率模型的建… （332）  
9.2.1 临界确定(3)  
9.2.2 面缺陷引起失效的概率…(35)  
9.2..面和内部缺陷引起的概率… （337）  
9.2.4总失效概率… (337）  
9.2.5 概率寿命计算结果及分析 （338）  
9.3 基于寿命预测概率模型的粉末盘可靠度计算 （345）  
9.3.1 粉末盘弹塑性应力有限元分…(346)  
9.3.2 单元缺陷临界尺寸的计算… …(348)  
9.3.3 轮盘中缺陷的分布形式 …. （350）  
9.3.4轮盘可靠度计算及结果分析 (351）  
9.4 基于螺栓孔特征的带缺陷轮盘失效概率分析流程(355）  
9.4.1初始缺陷分布概率的确定与修正… (55)  
9.4.2 实际问题的简化与应力分析… （356）  
9.4.3 缺陷导致的失效分析与寿命计算… （357）  
9.4.4制造评分与失效概率修正 （359）  
9.4..轮盘缺陷检测与剔除… （359）  
9.4.6.检测与方案改进 360）  
9.5 涡轮盘实例分析… （361）  
9.5.1 初始缺陷分布概率的确定与修正 (361）  
9.5.2实际问题的简化与应力分析 （362）  
9.5.3 缺陷导致的失效分析与寿命计算… …(366)  
9.5.4 轮盘检验与剔除 （366）  
9.5.5 计算结果及分析… （367）  
9.6 小结… （368）  
参考文献 (369）

# 第1章 结构疲劳设计分析方法

# 1.1引言

结构件的疲劳破坏是其失效的重要模式，为了能够准确预测疲劳寿命，需要合适的寿命预测方法和材料疲劳参数，而材料疲劳参数的准确获取更是其中的关键和基础。同时大多数工程实际结构件都含有几何不连续处，如开槽、开孔等，通常统一称之为缺口。当含缺口构件承受载荷时，在缺口区域会产生局部的应力和应变集中，甚至在相对低的弹性名义应力下，缺口根部小区域内的应力也可能超过屈服强度而发生塑性变形。当缺构件承受循环载荷时，应/应变集中区域的循环弹性应变会导致裂纹的萌，且其进步扩展将导致构件断裂。对于航空发动机关键结构件，疲劳失效很有可能造成严重的后果，因在应集中条件下，准确预测结构件的疲劳寿命具有重要意义[1]。作为航空发动机中的关键结构件之的涡轮盘，其最主要的失效模式是低循环疲劳破坏[2]。随着现代飞机对航空发动机性能要求的不断提，涡轮盘所承受的应和温度载荷也日趋严酷且复杂，同时还要求其具备足够的安全使用寿命和高可靠性，这就需要准确评估涡轮盘的低循环疲劳寿命。

近些年来，许多学者对疲劳寿命预测法进了深研究并取得了系列进展及应用成果。特别是，1965年，莫罗（Morrow）[31在巴斯坎（Basquin）的应幅寿命关系和曼森-科芬（Manson-Coffin）的塑性应变幅寿命关系基础上，提出了总应变寿命方程，该方程不仅适用于低循环疲劳，还适用于高循环疲劳。在实际结构件的寿命评估中，研究人员基于该方程综合考虑了不同载荷条件和几何形状等因素的影响，发展了众多的寿命预测法[4\~9]。因此，总应变程是材料和结构件寿命预测的基本方程，其材料疲劳参数包括：疲劳强度系数 $\sigma _ { \mathrm { ~ f ~ } } ^ { \prime }$ 、疲劳延性系数 $\varepsilon _ { \mathrm { ~ f ~ } } ^ { \prime }$ 、疲劳强度指数 $b$ 和疲劳延性指数 $_ c$ 。这4个参数可由单轴疲劳试验结果得到，但是因为在双对数坐标系下总应变寿命程不再具有线性关系，难以通过线性拟合直接得到，针对此现象，们提出了众多的参数获取法。较为具有代表性的法如通斜率法（1965)[10]、四点相关法（1965)[10]、修正的通斜率法（1988）[11）、修正的四点相关法（1933）[12]和简单近似法（1999)[13]等，都给出了总应变寿命程参数的获取法。这些法从易于获得参数值的角度出发，结合单调拉伸数据便可获得总应变寿命方程参数值，但这些法大都是近似法，虽然获得了具有相对明确物理意义的参数，但由于参数的确定包含较大的经验成分，导致较低的寿命预测精度。随着技术的发展，方程中的材料参数值多通过试验数据采线性拟合的式获得，但这样获得的参数往往缺乏明确的物理意义，有时偏差较大，难以得到理想的结果。同时，研究人员多利材料数据册[14,15]中提供的材料性能参数和寿命参数进寿命预测，但是由于以上参数确定法的不，采用册中参数对中循环疲劳寿命预测并不理想，因需要建能够准确确定寿命预测中相关材料参数的方法。

对于评估缺口构件的疲劳寿命，要获得缺口根部区域的应力和应变幅值，前获得缺口构件高应力集中区应力和应变状态的方法包括：试验法、近似算法和有限元法[1]。程中常的是近似算法和有限元法。近似算法中诺伊贝尔（Neuber）法和修正Neuber法简单易，因而获得泛应，但是这两种法于计算缺口局部应和应变时，需要获得缺口的理论应集中系数 $K _ { i }$ 和疲劳缺口系数 $K _ { \mathfrak { f } }$ ，然而，对于实际的复杂结构件，这两个系数均难以准确获得，因不易于采用。随着计算机技术的发展，有限元法越来越成为计算复杂结构件应力和应变的有效工具，且其计算较为准确，但是对于有应集中的构件，往往局部产了塑性变形，这就需要采弹塑性有限元分析，由于线性的引，增了计算的难度和复杂程度。因此，结合弹性有限元分析和近似算法给出种快速确定缺口构件应集中区域应和应变的法，有助于实际构件应力和应变的快速计算。

由于几何不连续，缺口根部周围自然产应梯度。仅以缺口根部危险点的应和应变通过应寿命或应变寿命程进寿命评估的法称为热点法（hot spotmethod），常用的有名义应力法、局部应力/应变法等；与此相对应，另一种考虑应力梯度影响，将缺口根部危险点周围区域应进平均的法称为局部的法，前较有影响的有临界距离法、应场强法和体积法等。热点法计算简单，工程上泛采用，但是计算精度不，而局部法物理意义明确，精度也相对较，但是计算复杂且要求较，在实际结构件上不易实现，因虽然前针对缺疲劳寿命评估已有众多的寿命预测法，但是还没有任何一种方法获得普遍接受。

本章主要开展三个方面的研究：（1）基于总应变方程中不同参数的物理意义，构建了它们与次单调拉伸时断收缩率和强度极限之间的关系，并利航空发动机中常用材料（TC4钛合、GH4169及GH901温合）的单调拉伸和疲劳试验数据，分别拟合得到了这3种材料的总应变寿命程参数，进采总应变寿命程开展了疲劳寿命预测；（2）采程中常的Neuber法和修正Neuber法计算TC4钛合材料 $K _ { \mathrm { r } } = 3$ 和 $K _ { \mathrm { t } } = 5$ 两种缺口试样的缺口局部应力和应变，并结合应变寿命方程进了两种缺口试样的寿命预测。通过对缺局部区域进弹性应分析，发展了种新的疲劳寿命预测法，其可以综合计及平均应、应梯度和尺寸效应的影响，并以TC4钛合材料缺试样的疲劳试验数据验证该法的有效性和精准性；（3）利材料的基础试验数据确定材料的疲劳参数，并在此基础上，利用能够综合考虑平均应力、应力梯度以及尺寸效应影响的缺口疲劳寿命模型对涡轮盘的疲劳寿命进预测评估，以期建可供程应用的涡轮盘寿命评价方法。

# 1.2 总应变寿命程参数的确定法

# 1.2.1 材料试验数据

为检验材料疲劳参数的准确性，在材料数据册中选取3种航空发动机常用材料TC4、GH4169和GH901合进验证分析。材料数据册给出的室温条件下TC4钛合金、 $6 5 0 \mathrm { \% }$ 条件下GH4169合金和 $5 0 0 \%$ 条件下GH901合的材料性能参数见表1-1，对应条件下3种合光滑试样对称循环加载下的疲劳试验数据见表1-2\~表1-4。

表1-1几种合金材料的性能参数[9,14,15]  

<table><tr><td rowspan=1 colspan=1>参数</td><td rowspan=1 colspan=1>钛合金TC4，室温</td><td rowspan=1 colspan=1>高温合金GH4169，650℃C</td><td rowspan=1 colspan=1>高温合金GH901，500%C</td></tr><tr><td rowspan=1 colspan=1>弹性模量E/MPa</td><td rowspan=1 colspan=1>109000</td><td rowspan=1 colspan=1>153000</td><td rowspan=1 colspan=1>170000</td></tr><tr><td rowspan=1 colspan=1>循环强度系数K&#x27;/MPa</td><td rowspan=1 colspan=1>1420</td><td rowspan=1 colspan=1>1481</td><td rowspan=1 colspan=1>2220</td></tr><tr><td rowspan=1 colspan=1>循环应变硬化指数n</td><td rowspan=1 colspan=1>0.07</td><td rowspan=1 colspan=1>0.098</td><td rowspan=1 colspan=1>0.151</td></tr><tr><td rowspan=1 colspan=1>疲劳强度系数σ</td><td rowspan=1 colspan=1>1564</td><td rowspan=1 colspan=1>1229</td><td rowspan=1 colspan=1>2140</td></tr><tr><td rowspan=1 colspan=1>疲劳强度指数b</td><td rowspan=1 colspan=1>-0.07      7</td><td rowspan=1 colspan=1>-0.065     1</td><td rowspan=1 colspan=1>-0.13</td></tr><tr><td rowspan=1 colspan=1>疲劳延性系数ε</td><td rowspan=1 colspan=1>2.69</td><td rowspan=1 colspan=1>0.138</td><td rowspan=1 colspan=1>0.218</td></tr><tr><td rowspan=1 colspan=1>疲劳延性指数c</td><td rowspan=1 colspan=1>-0.96</td><td rowspan=1 colspan=1>-0.657</td><td rowspan=1 colspan=1>-0.74</td></tr><tr><td rowspan=1 colspan=1>强度极限σ/MPa</td><td rowspan=1 colspan=1>969</td><td rowspan=1 colspan=1>1155</td><td rowspan=1 colspan=1>1067</td></tr><tr><td rowspan=1 colspan=1>断面收缩率ψ/%</td><td rowspan=1 colspan=1>45.5</td><td rowspan=1 colspan=1>38</td><td rowspan=1 colspan=1>24</td></tr></table>

表1-2室温条件下TC4钛合金光滑试样的疲劳试验数据[9,14]  

<table><tr><td rowspan=1 colspan=1>总应变范围Δε</td><td rowspan=1 colspan=1>反向数2N</td><td rowspan=1 colspan=1>应力幅σ/MPa</td></tr><tr><td rowspan=1 colspan=1>0.08568</td><td rowspan=1 colspan=1>95</td><td rowspan=1 colspan=1>1092</td></tr><tr><td rowspan=1 colspan=1>0.07774</td><td rowspan=1 colspan=1>113</td><td rowspan=1 colspan=1>1064</td></tr><tr><td rowspan=1 colspan=1>0.06576</td><td rowspan=1 colspan=1>143</td><td rowspan=1 colspan=1>1037</td></tr><tr><td rowspan=1 colspan=1>0.04572</td><td rowspan=1 colspan=1>294</td><td rowspan=1 colspan=1>1005</td></tr><tr><td rowspan=1 colspan=1>0.0259</td><td rowspan=1 colspan=1>765</td><td rowspan=1 colspan=1>1022</td></tr><tr><td rowspan=1 colspan=1>0.02156</td><td rowspan=1 colspan=1>1443</td><td rowspan=1 colspan=1>957</td></tr><tr><td rowspan=1 colspan=1>0.01736</td><td rowspan=1 colspan=1>2720</td><td rowspan=1 colspan=1>932</td></tr><tr><td rowspan=1 colspan=1>0.013758①</td><td rowspan=1 colspan=1>10000</td><td rowspan=1 colspan=1>740</td></tr><tr><td rowspan=1 colspan=1>0.011766①</td><td rowspan=1 colspan=1>20000</td><td rowspan=1 colspan=1>640</td></tr><tr><td rowspan=1 colspan=1>0.0116</td><td rowspan=1 colspan=1>29482</td><td rowspan=1 colspan=1>666</td></tr><tr><td rowspan=1 colspan=1>0.008624①</td><td rowspan=1 colspan=1>100000</td><td rowspan=1 colspan=1>470</td></tr><tr><td rowspan=1 colspan=1>0.007798①</td><td rowspan=1 colspan=1>200000</td><td rowspan=1 colspan=1>425</td></tr><tr><td rowspan=1 colspan=1>0.006514①</td><td rowspan=1 colspan=1>100000</td><td rowspan=1 colspan=1>355</td></tr><tr><td rowspan=1 colspan=1>0.006422①</td><td rowspan=1 colspan=1>2000000</td><td rowspan=1 colspan=1>350</td></tr><tr><td rowspan=1 colspan=3>①在材料数据册中总应变数据并未给出，是利册中的循环应应变曲线和对称循环应幅确定的[9]。</td></tr></table>

表1-3 ${ \bf 6 5 0 9 C }$ 条件下GH4169高温合金光滑试样的疲劳试验数据[9,15]  

<table><tr><td rowspan=1 colspan=1>总应变范围Δε</td><td rowspan=1 colspan=1>反向数2N</td><td rowspan=1 colspan=1>应力幅σ/MPa</td></tr><tr><td rowspan=1 colspan=1>0.04236</td><td rowspan=1 colspan=1>30</td><td rowspan=1 colspan=1>985</td></tr><tr><td rowspan=1 colspan=1>0.02526</td><td rowspan=1 colspan=1>100</td><td rowspan=1 colspan=1>911</td></tr><tr><td rowspan=1 colspan=1>0.01754</td><td rowspan=1 colspan=1>300</td><td rowspan=1 colspan=1>848</td></tr><tr><td rowspan=1 colspan=1>0.01318</td><td rowspan=1 colspan=1>1000</td><td rowspan=1 colspan=1>784</td></tr><tr><td rowspan=1 colspan=1>0.01094</td><td rowspan=1 colspan=1>3000</td><td rowspan=1 colspan=1>730</td></tr><tr><td rowspan=1 colspan=1>0.00944</td><td rowspan=1 colspan=1>10000</td><td rowspan=1 colspan=1>675</td></tr><tr><td rowspan=1 colspan=1>0.008749①</td><td rowspan=1 colspan=1>20000</td><td rowspan=1 colspan=1>640</td></tr><tr><td rowspan=1 colspan=1>0.0085</td><td rowspan=1 colspan=1>30000</td><td rowspan=1 colspan=1>629</td></tr><tr><td rowspan=1 colspan=1>0.00772</td><td rowspan=1 colspan=1>100000</td><td rowspan=1 colspan=1>582</td></tr><tr><td rowspan=1 colspan=1>0.007055①</td><td rowspan=1 colspan=1>200000</td><td rowspan=1 colspan=1>535</td></tr><tr><td rowspan=1 colspan=1>0.006498①</td><td rowspan=1 colspan=1>1000000</td><td rowspan=1 colspan=1>495</td></tr><tr><td rowspan=1 colspan=1>0.006295①</td><td rowspan=1 colspan=1>2000000</td><td rowspan=1 colspan=1>480</td></tr><tr><td rowspan=1 colspan=3>①在材料数据册中总应变数据并未给出，是利用册中的循环应力应变曲线和对称循环应幅确定的[9]。O</td></tr></table>

表1-4 $5 0 0 \mathrm { ‰}$ 条件下GH901温合光滑试样的疲劳试验数据[9,14]  

<table><tr><td rowspan=1 colspan=1>总应变范围Δ</td><td rowspan=1 colspan=1>反向数2N</td><td rowspan=1 colspan=1>应力幅σ/MPa</td></tr><tr><td rowspan=1 colspan=1>0.00804</td><td rowspan=1 colspan=1>8447</td><td rowspan=1 colspan=1>690</td></tr><tr><td rowspan=1 colspan=1>0.00770</td><td rowspan=1 colspan=1>10000</td><td rowspan=1 colspan=1>620</td></tr><tr><td rowspan=1 colspan=1>0.007</td><td rowspan=1 colspan=1>12772</td><td rowspan=1 colspan=1>633</td></tr><tr><td rowspan=1 colspan=1>0.006514①</td><td rowspan=1 colspan=1>20000</td><td rowspan=1 colspan=1>540</td></tr><tr><td rowspan=1 colspan=1>0.00604</td><td rowspan=1 colspan=1>70502</td><td rowspan=1 colspan=1>538</td></tr><tr><td rowspan=1 colspan=1>0.004606①</td><td rowspan=1 colspan=1>100000</td><td rowspan=1 colspan=1>390</td></tr><tr><td rowspan=1 colspan=1>0.00482</td><td rowspan=1 colspan=1>141408</td><td rowspan=1 colspan=1>440</td></tr><tr><td rowspan=1 colspan=1>0.004126①</td><td rowspan=1 colspan=1>200000</td><td rowspan=1 colspan=1>350</td></tr><tr><td rowspan=1 colspan=1>0.003532①</td><td rowspan=1 colspan=1>10000</td><td rowspan=1 colspan=1>300</td></tr><tr><td rowspan=1 colspan=1>0.003308①</td><td rowspan=1 colspan=1>20000</td><td rowspan=1 colspan=1>281</td></tr><tr><td rowspan=1 colspan=3>①在材料数据册中总应变数据并未给出，是利册中的循环应应变曲线和对称循环应幅确定的[9]</td></tr></table>

# 1.2.2 确定材料疲劳参数的传统方法

为考察传统的参数确定法获得总应变寿命程参数的准确性，本节选通斜率法、四点相关法、修正的通斜率法和修正的四点相关法来确定航空发动机常材料TC4钛合、GH4169合和GH901合的疲劳参数。由各种传统法及其确定的总应变寿命程表达式，可得到各种法确定的总应变寿命程中4个参数的值。

1.2.2.1 通用斜率法（universal slope method，USM）

通用斜率法[10]认为控制弹性 $\Delta \varepsilon _ { \mathrm { e } }$ 线和塑性 $\Delta \varepsilon _ { \mathrm { { p } } }$ 线的指数 $b$ 和 $c$ 与材料类型关，疲劳强度系数 $\sigma _ { \mathrm { ~ f ~ } } ^ { \prime }$ 和疲劳延性系数 $ { \varepsilon } _ { \mathrm { f } } ^ { \prime }$ 采下式确定

$$
\sigma _ { \mathrm { f } } ^ { \prime } = 1 . 9 0 8 \sigma _ { \mathrm { b } } , \varepsilon _ { \mathrm { f } } ^ { \prime } = 0 . 7 5 7 9 \varepsilon _ { \mathrm { f } } ^ { 0 . 6 }
$$

式中， $\sigma _ { \mathrm { ~ b ~ } }$ 为材料的强度极限，断裂真应变 $\varepsilon _ { \mathrm { f } }$ 与试样断收缩率关系为

$$
\varepsilon _ { \mathrm { f } } = \ln \left( { \frac { 1 } { 1 - \psi } } \right)
$$

疲劳强度指数和疲劳延性指数分别为 $b = - 0 . 1 2$ 和 $c = - 0 . 6$

1.2.2.2 四点相关法(four-point -correlation method，FPCM)

曼森（Manson）基于分别表征弹性线和塑性线的弹性应变和塑性应变值提出了四点相关法，弹性线和塑性线各由两个点确定，其中弹性线用1/4次循环和 $1 0 ^ { 5 }$ 次循环时的弹性应变分量来确定，塑性线用10次循环和 $1 0 ^ { 4 }$ 次循环时的塑性应变分量来确定[10]。四点相关法中，总应变寿命程中参数可由如下关系式确定

$$
\sigma _ { \mathrm { f } } ^ { \prime } = \frac { E } { 2 } \times 1 0 ^ { b \times 1 } \mathrm { g } ^ { 2 } \mathrm { + I g } \left[ \frac { 2 . 5 \sigma _ { \mathrm { b } } ( 1 + \varepsilon _ { \mathrm { f } } ) } { E } \right] , \varepsilon _ { \mathrm { f } } ^ { \prime } = \frac { 1 } { 2 } \times 1 0 ^ { c \times 1 } \mathrm { g } _ { 2 0 } ^ { \mathrm { + } 1 } \mathrm { j g } \left( \frac { 1 } { 4 } \varepsilon _ { \mathrm { f } } ^ { \mathrm { + } } \right)
$$

$$
b = \frac { \mathrm { l g } \left[ \cfrac { 2 . 5 ~ \left( 1 + \varepsilon _ { \mathrm { f } } \right) } { 0 . 9 ~ } \right] } { \mathrm { l g } \left( \cfrac { 1 } { 4 \times 1 0 ^ { 5 } } \right) } , ~ c = \frac { 1 } { 3 } \mathrm { l g } \left( \cfrac { 0 . 0 1 3 2 - \Delta \varepsilon _ { \mathrm { e } } ^ { * } } { 1 . 9 1 } \right) - \frac { 1 } { 3 } \mathrm { l g } \left( \frac { 1 } { 4 } \varepsilon _ { \mathrm { f } } ^ { \frac { 3 } { 4 } } \right)
$$

式中， $E$ 为材料的弹性模量， $\Delta \varepsilon _ { \mathrm { e } } ^ { * }$ 为 $1 0 ^ { 4 }$ 次循环时的弹性应变范围，可以表示为

$$
\Delta \varepsilon _ { \mathrm { e } } ^ { * } = 1 0 ^ { b \times \log ( 4 \times 1 0 ^ { 4 } ) + \log \left[ \frac { 2 . 5 \sigma _ { \mathrm { b } } ( 1 + \varepsilon _ { \mathrm { f } } ) } { E } \right] }
$$

1.2.2.3 修正的通用斜率法(modified universal slope method，MUSM)

如前所述，修正的通斜率法[11]同样认为疲劳强度指数 $b$ 和疲劳延性指数 $c$ 与材料类型无关，而疲劳强度系数 $\sigma _ { \mathrm { ~ f ~ } } ^ { \prime }$ 和疲劳延性系数 $\varepsilon _ { \mathrm { f } } ^ { \prime }$ 的确定修正为

$$
\sigma _ { \mathrm { f } } ^ { \prime } = E \times 0 . 6 2 3 \times \left( \frac { \sigma _ { \mathrm { b } } } { E } \right) ^ { 0 . 8 3 2 } , \varepsilon _ { \mathrm { f } } ^ { \prime } = 0 . 0 1 9 6 \times \varepsilon _ { \mathrm { f } } ^ { 0 . 1 5 5 } \times \left( \frac { \sigma _ { \mathrm { b } } } { E } \right) ^ { - 0 . 5 3 2 }
$$

式中， $\varepsilon _ { \mathrm { f } }$ 采式（1-2）确定，而疲劳强度指数和疲劳延性指数分别修正为 $b = - 0 . 0 9$ 和 $c = - 0 . 5 6$

1.2.2.4 修正的四点相关法(modified four- point-correlation method，MFPCM)

修正的四点相关法[12]由翁（ $\mathrm { O n g }$ ）提出，其与Manson提出的四点相关法稍有不同。修正的四点相关法认为应变疲劳曲线通过计算 $1 0 ^ { \circ }$ 次和 $1 0 ^ { 6 }$ 次载荷反向时的弹性应变幅值以及 $1 0 ^ { \circ }$ 次和 $1 0 ^ { 4 }$ 次载荷反向时的塑性应变幅值来确定。基于该修正法的总应变寿命程中4个参数采用下式确定

$$
\sigma _ { \mathrm { f } } ^ { \prime } = \sigma _ { \mathrm { b } } \left( { 1 + \varepsilon _ { \mathrm { f } } } \right) , \varepsilon _ { \mathrm { f } } ^ { \prime } = \varepsilon _ { \mathrm { f } }
$$

$$
b = \frac { 1 } { 6 } \left\{ \log \left[ 0 . 1 6 \left( \frac { \sigma _ { \mathrm { b } } } { E } \right) ^ { 0 . 8 1 } \right] - \log \left( \frac { \sigma _ { \mathrm { f } } } { E } \right) \right\}
$$

$$
c = { \frac { 1 } { 4 } } \mathrm { l g } \left( { \frac { 0 . 0 0 7 3 7 - { \frac { \Delta \varepsilon _ { \mathrm { e } } ^ { * } } { 2 } } } { 2 } } \right) - { \frac { 1 } { 4 } } \mathrm { l g } \varepsilon _ { \mathrm { f } }
$$

式中， $\sigma _ { \mathrm { f } }$ 为材料断裂真应力， $\varepsilon _ { \mathrm { f } }$ 由式（1-2）确定，而载荷反向数 $1 0 ^ { 4 }$ 次时的弹性应变范围 $\Delta \varepsilon _ { \mathrm { e } } ^ { \ast }$ 由下式确定

$$
\frac { \Delta \varepsilon _ { \mathrm { e } } ^ { * } } { 2 } = \frac { \sigma _ { \mathrm { f } } } { E } \times 1 0 ^ { \frac { 2 } { 3 } \left\{ 1 { \mathrm { g } } \left[ 0 . 1 6 \times \left( \frac { \sigma _ { \mathrm { b } } } { E } \right) ^ { 0 . 8 1 } \right] - 1 { \mathrm { g } } \left( \frac { \sigma _ { \mathrm { f } } } { E } \right) \right\} }
$$

1.2.2.5 传统方法确定的总应变寿命方程参数的对比

采前述4种传统法的参数表达式结合材料单轴试验数据确定的TC4钛合、GH4169合及GH901合的材料疲劳参数见表 $1 - 5 \sim$ 表1-7，表中一并给出了材料数据册中的对应参数以做对。由这些确定的参数得到的3种材料的疲劳曲线与试验结果的对比如图1-1\~图1-3所。

表1-5 4种传统法与材料数据册确定的TC4钛合金疲劳参数  

<table><tr><td rowspan=1 colspan=1>方法</td><td rowspan=1 colspan=1>o{f}$</td><td rowspan=1 colspan=1>b</td><td rowspan=1 colspan=1>}$</td><td rowspan=1 colspan=1>c</td></tr><tr><td rowspan=1 colspan=1>通用斜率法</td><td rowspan=1 colspan=1>1842.84</td><td rowspan=1 colspan=1>-0.120</td><td rowspan=1 colspan=1>0.562</td><td rowspan=1 colspan=1>-0.600</td></tr><tr><td rowspan=1 colspan=1>四点相关法</td><td rowspan=1 colspan=1>1796.09</td><td rowspan=1 colspan=1>-0.116</td><td rowspan=1 colspan=1>0.684</td><td rowspan=1 colspan=1>-0.692</td></tr><tr><td rowspan=1 colspan=1>修正的通用斜率法</td><td rowspan=1 colspan=1>1334.74</td><td rowspan=1 colspan=1>-0.090</td><td rowspan=1 colspan=1>0.222</td><td rowspan=1 colspan=1>-0.560</td></tr><tr><td rowspan=1 colspan=1>修正的四点相关法</td><td rowspan=1 colspan=1>1557.15</td><td rowspan=1 colspan=1>-0.112</td><td rowspan=1 colspan=1>0.607</td><td rowspan=1 colspan=1>-0.613</td></tr><tr><td rowspan=1 colspan=1>材料数据手册[14]</td><td rowspan=1 colspan=1>1564</td><td rowspan=1 colspan=1>-0.07</td><td rowspan=1 colspan=1>2.69</td><td rowspan=1 colspan=1>-0.96</td></tr></table>

表1-64种传统方法与材料数据手册确定的GH4169合金疲劳参数  

<table><tr><td rowspan=1 colspan=1>方法</td><td rowspan=1 colspan=1>$σ}$</td><td rowspan=1 colspan=1>b</td><td rowspan=1 colspan=1>8</td><td rowspan=1 colspan=1>c</td></tr><tr><td rowspan=1 colspan=1>通用斜率法</td><td rowspan=1 colspan=1>2196.58</td><td rowspan=1 colspan=1>-0.120</td><td rowspan=1 colspan=1>0.487</td><td rowspan=1 colspan=1>-0.600</td></tr><tr><td rowspan=1 colspan=1>四点相关法</td><td rowspan=1 colspan=1>1977.96</td><td rowspan=1 colspan=1>-0.109</td><td rowspan=1 colspan=1>0.429</td><td rowspan=1 colspan=1>-0.596</td></tr><tr><td rowspan=1 colspan=1>修正的通用斜率法</td><td rowspan=1 colspan=1>1635.25</td><td rowspan=1 colspan=1>-0.090</td><td rowspan=1 colspan=1>0.233</td><td rowspan=1 colspan=1>-0.56</td></tr><tr><td rowspan=1 colspan=1>修正的四点相关法</td><td rowspan=1 colspan=1>1707.13</td><td rowspan=1 colspan=1>-0.100</td><td rowspan=1 colspan=1>0.478</td><td rowspan=1 colspan=1>-0.575</td></tr><tr><td rowspan=1 colspan=1>材料数据手册[15]</td><td rowspan=1 colspan=1>1229</td><td rowspan=1 colspan=1>-0.065</td><td rowspan=1 colspan=1>0.138</td><td rowspan=1 colspan=1>-0.657</td></tr></table>

表1-7 4种传统方法与材料数据手册确定的GH901合金疲劳参数  

<table><tr><td rowspan=1 colspan=1>方法</td><td rowspan=1 colspan=1>σ$</td><td rowspan=1 colspan=1>b</td><td rowspan=1 colspan=1>81}$</td><td rowspan=1 colspan=1>c</td></tr><tr><td rowspan=1 colspan=1>通用斜率法</td><td rowspan=1 colspan=1>2029.22</td><td rowspan=1 colspan=1>-0.120</td><td rowspan=1 colspan=1>0.349</td><td rowspan=1 colspan=1>-0.600</td></tr><tr><td rowspan=1 colspan=1>四点相关法</td><td rowspan=1 colspan=1>1588.15</td><td rowspan=1 colspan=1>-0.098</td><td rowspan=1 colspan=1>0.206</td><td rowspan=1 colspan=1>-0.490</td></tr><tr><td rowspan=1 colspan=1>修正的通用斜率法</td><td rowspan=1 colspan=1>1588.25</td><td rowspan=1 colspan=1>-0.090</td><td rowspan=1 colspan=1>0.236</td><td rowspan=1 colspan=1>-0.560</td></tr><tr><td rowspan=1 colspan=1>修正的四点相关法</td><td rowspan=1 colspan=1>1359.82</td><td rowspan=1 colspan=1>-0.083</td><td rowspan=1 colspan=1>0.274</td><td rowspan=1 colspan=1>-0.505</td></tr><tr><td rowspan=1 colspan=1>材料数据手册[14]</td><td rowspan=1 colspan=1>2140</td><td rowspan=1 colspan=1>-0.13</td><td rowspan=1 colspan=1>0.218</td><td rowspan=1 colspan=1>-0.74</td></tr></table>

由图1-1\~图1-3可以看出，对于TC4钛合，4种传统法中，通用斜率法、四点相关法和修正的四点相关法获得的疲劳曲线与试验结果均较为接近，表明此3种法对TC4钛合金疲劳参数的拟合较为合适，修正的通用斜率法在高循环疲劳范围内与试验结果也较为接近，但低循环疲劳范围内偏差较，而材料数据册给出的疲劳参数确定的疲劳曲线在低循环疲劳范围内与试验结果较为接近，高循环疲劳范围的预测结果与试验相偏差较。对于GH4169合，4种传统法确定的疲劳曲线与试验数据相比，在循环疲劳寿命范围均具有相对好的预测精度，而在低循环疲劳寿命范围预测偏差较，精度降低，相之下，利材料数据册给出的参数确定的疲劳曲线在整个寿命范围内与试验数据吻合很好。对于GH901合，4种传统法确定的疲劳曲线在整个寿命范围内均明显于试验数据，偏差较大，采用材料数据册给出的参数确定的疲劳曲线虽低于4种传统法确定的疲劳曲线，但是其预测精度仍相对较低，且采该疲劳曲线确定的寿命均于试验数据，这势必对程中实际结构件的寿命评估带来定的风险。

![](images/0e81160e88457486fae420f47d822ef9ec2fbd433e959c4ca1327a85c90ebbfd.jpg)  
图1-1 传统法得到的TC4钛合疲劳曲线

![](images/c47ceb0f0b54ef05eaa8709ad4179fe1636ab7a2f740a0b0cbecf253d82e5157.jpg)  
图1-2 传统法得到的GH4169合疲劳曲线

![](images/d99d7b0f2f29e2aa5a289f4cbd40aae5148f313e862221d7c3b0f76a190d29e5.jpg)  
图1-3传统方法得到的GH901合疲劳曲线

综上所述，从以上对3种材料不同温度下疲劳参数的分析结果来看，对TC4钛合而，4种传统方法确定的疲劳曲线与试验结果吻合程度尚可，但是对GH4169和GH901合却偏差较大，材料数据册给出的参数确定的疲劳曲线预估的寿命也并不理想，不能满足工程要求，因而急需发展一种满工程精度要求的确定材料疲劳参数的方法。

# 1.2.3 确定总应变寿命程参数的种新法

t

前述多种方法给出的材料疲劳参数难以满足提高寿命预测精度的需要，为了使总应变寿命程能够在较寿命范围内具有理想的预测精度且其参数物理意义明确，本节基于总应变寿命方程中疲劳强度系数与疲劳延性系数的物理意义，发展了一种确定总应变寿命程参数的法，并对TC4、GH4169和GH901合材料进参数拟合和寿命评估。

# 1.2.3.1总应变寿命方程参数的确定

由单调拉伸和循环加载的关系可知，一次单调拉伸可以认为是循环加载时的1/4个循环，即次单调拉伸断裂的疲劳寿命为1/4个循环数[9]，分别可得如下关系

$$
\sigma _ { \mathrm { f } } = \sigma _ { \mathrm { f } } ^ { \prime } ( 0 . 5 ) ^ { b }
$$

式中： $\sigma _ { \mathrm { ~ f ~ } }$ (d 次单调拉伸时的断裂真应；

$\sigma _ { \mathrm { ~ f ~ } } ^ { \prime }$ (id:) 疲劳强度系数。

$$
\varepsilon _ { \uparrow } = \varepsilon _ { \uparrow } ^ { \prime } ( 0 . 5 ) ^ { \circ }
$$

式中： $ { \varepsilon } _ { \mathrm { f } }$ (id:) 一次单调拉伸时的断裂真应变；$ { \varepsilon } _ { \mathrm { f } } ^ { \prime }$ (id:) 疲劳延性系数。

同时，式（1-11）和式（1-12）中的断裂真应力 $\sigma _ { \mathrm { { f } } }$ 和断裂真应变 $\varepsilon _ { \mathrm { f } }$ 还可表示为

$$
\sigma _ { \mathrm { f } } = { \frac { P } { A _ { \mathrm { f } } } }
$$

$$
\varepsilon _ { \mathrm { f } } = \ln { \left( A _ { 0 } / A _ { \mathrm { f } } \right) }
$$

式中： $A _ { 0 }$ (id:) 材料试样的初始截面面积；

$A _ { \mathrm { f } }$ (id) 材料试样拉伸断裂时的截积；

$P$ 施加载荷。

由材料力学可知，上述 $A _ { 0 }$ 和 $A _ { \mathrm { f } }$ 者之间的关系可以由断收缩率来表

$$
\psi = \frac { A _ { 0 } - A _ { \mathrm { f } } } { A _ { 0 } }
$$

并可由拉伸强度极限 $\sigma _ { \mathrm { ~ b ~ } }$ 和断面收缩率 $\psi$ 来描述次单调拉伸时的断裂真应 $\sigma _ { \mathrm { ~ f ~ } }$ 和断裂 真应变 $\varepsilon _ { \mathrm { f } }$

$$
\sigma _ { \mathrm { f } } = { \frac { P } { A _ { \mathrm { f } } } } { \approx } { \frac { \sigma _ { \mathrm { b } } A _ { 0 } } { A _ { \mathrm { f } } } } = { \frac { \sigma _ { \mathrm { b } } } { 1 - \psi } }
$$

$$
\varepsilon _ { \mathrm { f } } = \ln \left( A _ { 0 } / A _ { \mathrm { f } } \right) = \ln \left( \frac { 1 } { 1 - \psi } \right)
$$

对于式（1-16）值得说明的点是，断裂真应的定义为材料试样断裂时的载荷与断裂时的积之比，该值由试验测定。从材料拉伸试验曲线上看，当材料达到强度极限时，此时载荷 $P$ 最大，其应力值为 $\sigma _ { \mathrm { ~ b ~ } }$ ，然后随着材料出现颈缩，载荷下降最后直断裂，材料断裂时的载荷 $P$ 值会低于材料达到强度极限时的载荷值，因式（1-16）中令 $P { \approx } \sigma _ { \mathrm { b } } A _ { 0 }$ 会造成计算得到的断裂真应存在定偏差，但为了充分合理利材料数据册现有数据（材料数据册中缺乏断裂真应力 $\sigma _ { \mathrm { ~ f ~ } }$ 的试验值），而做此适当近似，些材料试验数据也表明[16]，对于偏于脆性的材料，其差别较，对于塑性材料，其差别也在可接受范围内。

通过式（1-16）和式（1-17）结合式（1-11）和式（1-12）可得

$$
\sigma _ { \mathrm { f } } ^ { \prime } = \frac { \sigma _ { \mathrm { f } } } { \left( 0 . 5 \right) ^ { b } } = \frac { \sigma _ { \mathrm { b } } } { \left( 1 - \psi \right) \left( 0 . 5 \right) ^ { b } }
$$

$$
\varepsilon _ { \mathrm { f } } ^ { \prime } = { \frac { \varepsilon _ { \mathrm { f } } } { ( 0 . 5 ) ^ { c } } } = { \frac { - \ln { \bigl ( } 1 - \psi { \bigr ) } } { ( 0 . 5 ) ^ { c } } }
$$

则总应变寿命方程可写为

$$
\frac { \Delta \varepsilon _ { \mathrm { t } } } { 2 } = \frac { \sigma _ { \mathrm { b } } } { E \mathrm { ~ } \left( 1 - \psi \right) \mathrm { ~ } \left( 0 . 5 \right) { } ^ { b } } ( 2 N _ { \mathrm { f } } ) { } ^ { b } + \frac { - \mathrm { l n ~ } \left( 1 - \psi \right) } { ( 0 . 5 ) { } ^ { c } } ( 2 N _ { \mathrm { f } } ) { } ^ { c }
$$

式中的参数 $b$ 和 $c$ 可通过试验数据利用非线性拟合获得，从而得到总应变寿命方程和应变一疲劳寿命曲线，采用上式拟合的好处是，一方面材料数据手册中现有的数据可以得到充分利；另总应变寿命程中相关参数的物理意义可以得到较好的保证[9]。

1.2.3.2 典型合金材料疲劳参数的拟合

采用表1-2\~表1-4中的TC4钛合、GH4169和GH901高温合金材料疲劳试验数据，采用式（1-20）拟合得到给定温度条件下3种材料的疲劳曲线如图1-4\~图1-6所示，拟合结果见表1-8。由图 $1 - 4 \sim$ 图1-6的拟合结果可以看出，3种材料的拟合曲线与试验数据点吻合得非常好，表明由拟合得到的材料参数确定的疲劳曲线能很好地描述相应材料的疲劳性能。

![](images/84abbd9b7a1b33887d5139aa1f5704e46e9213dac38b422ecae7b790d8a69c15.jpg)  
图1-4TC4钛合金疲劳试验数据的拟合结果

![](images/cd76ce5e493609c502de831e471200ec51b78b236bc36c4400beaf9ce48406dd.jpg)  
图1-5 GH4169合疲劳试验数据的拟合结果

表1-8中括号内的数值为断裂真应力（近似值）或断裂真应变，可见，由于有式（1-11）和式（1-12）的控制，采用本文发展的参数确定方法，得到的疲劳强度系数 $\sigma _ { \mathrm { ~ f ~ } } ^ { \prime }$ 和单调拉伸时的断裂真应 $\sigma _ { \mathrm { ~ f ~ } }$ 、疲劳延性系数 $\varepsilon _ { \mathrm { ~ f ~ } } ^ { \prime }$ 和断裂真应变 $\varepsilon _ { \mathrm { f } }$ 都吻合得较好，且具有较明显的物理意义[9]，如表1-1中材料数据册中给出的TC4钛合的疲劳延性系数 $\mathcal { E } _ { \mathrm { f } } ^ { \prime } = 2 . 6 9$ ，其断裂真应变为 $\varepsilon _ { \mathrm { f } } = 0 . 6 0 7$ ，而本文方法确定的疲劳延性系数 $\varepsilon _ { \mathrm { f } } ^ { \prime } = 0 . 3 9 1 8$ ；再如手册中给出的疲劳延性指数 $c$ 为－0.96，本文方法确定的 $c$ 为-0.63159，疲劳强度指数 $b$ 和疲劳延性指数 $c$ 也基本在通常取值范围内（ $b \in$ $[ \ : - 0 . 0 5 , - 0 . 1 2 ]$ , $c \in [ - 0 . 5$ ，-0.7），因而采用本文发展的总应变寿命程参数确定方法对材料疲劳试验数据的拟合结果较为理想。

![](images/59c4004ee2a39b5dd51682bccce53578fbb6e6ba1066b14af5b2edd680007597.jpg)  
图1-6 GH901合疲劳试验数据的拟合结果

表1-8本文方法确定的TC4、GH4169及GH901合金的材料疲劳参数  

<table><tr><td rowspan=1 colspan=1>参数</td><td rowspan=1 colspan=1>TC4钛合金，室温</td><td rowspan=1 colspan=1>GH4169合金，650℃</td><td rowspan=1 colspan=1>GH901合金，500℃</td></tr><tr><td rowspan=1 colspan=1>σ{(σ) /MPa</td><td rowspan=1 colspan=1>1646.75（1777.98)</td><td rowspan=1 colspan=1>1747.42（1862.9）</td><td rowspan=1 colspan=1>1302.82（1403.95）</td></tr><tr><td rowspan=1 colspan=1>b i</td><td rowspan=1 colspan=1>-0.11046</td><td rowspan=1 colspan=1>-0.09282</td><td rowspan=1 colspan=1>-0.1081</td></tr><tr><td rowspan=1 colspan=1>fεi)</td><td rowspan=1 colspan=1>0.3918（0.607）</td><td rowspan=1 colspan=1>0.2587（0.478）</td><td rowspan=1 colspan=1>0.1852（0.2744）</td></tr><tr><td rowspan=1 colspan=1>c</td><td rowspan=1 colspan=1>-0.63159</td><td rowspan=1 colspan=1>-0.88588</td><td rowspan=1 colspan=1>-0.5673</td></tr></table>

# 1.2.3.3 采用新确定材料参数的疲劳寿命预测

为考核新确定的材料疲劳参数方法的有效性，利用上述确定的新的材料参数，通过总应变寿命程对TC4钛合、GH901和GH4169合的材料疲劳试验结果进了寿命预测，并与材料数据册给出的参数确定的总应变寿命程预测结果进了对[9]，如图1-7\~图1-9所。对于TC4、GH4169和GH901三种合，与基于材料数据册中提供的参数的寿命预测结果相，册中参数的预测结果偏差较，尤其是当循环数大于 $1 0 ^ { 4 }$ 时，难以满实际工程设计的要求；而基于本发展的材料参数确定法的总应变寿命程的预测结果在较寿命范围内都较理想，其寿命基本在两倍分散带以内[1,9]。

![](images/6c1fdb18f16e622adb10359ec5e6b2b6efefa4dbd7f6709b4f3fab6515657e8b.jpg)  
图1-7 两种参数总应变寿命程对TC4钛合的预测结果对

![](images/567663b8e173b85c05baf7e3a23cc10dfd0ee497e7df76ad19e1fb7abab80e16.jpg)  
图1-8 两种参数总应变寿命程对GH4169合的预测结果对

![](images/7e9b5409e0e47932a077d622b81ce2079d2d1f3187a7c34fc9969807252ad608.jpg)  
图1-9 两种参数总应变寿命程对GH901合的预测结果对

# 1.2.4 材料疲劳参数的对比分析

为进一步明确各材料疲劳参数的物理意义及其对疲劳寿命曲线的影响，本节对前述法获得的3种材料的4个参数进了对分析，对结果如图1-10\~图1-13所。

![](images/bfe2bca83b92cf54db273dd4d50683e6fb11e1240359dc205d807b11c657e3e5.jpg)  
图1-10 疲劳强度系数的对

![](images/b780dcd28c17b984d97aeb6e92b052918ec36b5acc78550f5f8808d0a6603a9a.jpg)  
图1-11 疲劳强度指数的对

![](images/600abe7483190c87e41c6b8378bb3ecf17a7858544e920ea9f439751561183fb.jpg)  
图1-12 疲劳延性系数的对

![](images/733e35d4bb404c7d34f794b7cabd01431021d5657b2246925274c90bb41bbc04.jpg)  
图1-13 疲劳延性指数的对比

1.2.4.1决定高循环疲劳曲线部分的疲劳强度系数 $\boldsymbol { \sigma } _ { \mathrm { ~ f ~ } } ^ { \prime }$ 和疲劳强度指数 $b$

由图1-10和图1-11可以看出：

（1）对于TC4钛合，通用斜率法（USM）、四点相关法（FPCM）、修正的通用斜率法（MUSM）和修正的四点相关法（MFPCM）确定的疲劳强度系数 $\sigma _ { \mathrm { ~ f ~ } } ^ { \prime }$ 与材料的断裂真应力相对接近，且疲劳强度指数 $b$ 也较为合适，因这4种法在TC4钛合循环疲劳范围内确定的疲劳曲线与试验吻合相对较好；材料数据册给出的疲劳强度系数$\sigma _ { \mathrm { ~ f ~ } } ^ { \prime }$ 与断裂真应相对接近，但是其确定的疲劳强度指数 $b$ 明显较大（绝对值小），因而其确定的疲劳曲线在循环疲劳部分明显于试验数据（如图1-1所示），因偏差较大；由本文提出的方法确定的疲劳强度系数 $\boldsymbol { \sigma } _ { t } ^ { \prime }$ 略低于材料断裂真应，符合材料次拉伸与循环加载的关系，物理意义明确，且疲劳强度指数 $b$ 也较为合适，因而通过该方法确定的TC4循环疲劳部分的疲劳曲线与试验数据吻合常好，如图1-4所。

（2）对于GH4169合，通斜率法、四点相关法、修正的通斜率法、修正的四点相关法、材料数据册和本文发展的方法确定的疲劳强度系数 $\sigma _ { \mathrm { ~ f ~ } } ^ { \prime }$ 和疲劳强度指数 $b$ 均较为合理，因这种法确定的GH4169合疲劳曲线的循环疲劳部分与试验数据的吻合程度都相对较好，其中尤以材料数据册和本发展的法更优。

（3）对于GH901合，通斜率法、四点相关法、修正的通斜率法、修正的四点相关法、材料数据手册和本文发展的方法确定的疲劳强度指数 $b$ 相差不大，但是与本文发展的法相，通斜率法、四点相关法、修正的通斜率法、修正的四点相关法和材料数据手册确定的疲劳强度系数 $\sigma _ { \mathrm { ~ f ~ } } ^ { \prime }$ 要明显高于本文确定的疲劳强度系数，甚至远远超过材料断裂真应力，导致其背离了参数的物理意义，因而这几种法确定的疲劳曲线高循环疲劳部分均显著偏离了试验数据（如图1-3所），不能准确描述材料的疲劳性能。

1.2.4.2 决定低循环疲劳曲线部分的疲劳延性系数 $\varepsilon _ { \mathrm { f } } ^ { \prime }$ 和疲劳延性指数 $c$

（1）对于TC4钛合，通斜率法、四点相关法和修正的四点相关法确定的疲劳延性系数 $\varepsilon _ { \mathrm { f } } ^ { \prime }$ 与断裂真应变 $\varepsilon _ { \mathrm { f } }$ 较为接近，且疲劳延性指数 $c$ 也较为合理，因而这3种方法确定的疲劳曲线低循环疲劳部分与试验数据吻合相对较好；修正的通斜率法确定的疲劳延性指数 $c$ 虽然较为合理，但是其疲劳延性系数 $\varepsilon _ { \mathrm { f } } ^ { \prime }$ 显著低于断裂真应变，因而其确定的疲劳曲线低循环疲劳部分明显低于试验数据，偏离较，如图1-1所；材料数据册给出的材料参数确定的疲劳曲线低循环疲劳部分虽然与试验结果吻合很好，但是其确定的参数仅具有数值精度，而疲劳延性系数 $\varepsilon _ { \mathrm { f } } ^ { \prime }$ 远远背离了该参数的物理意义；本发展的法则很好地避免了这问题，确定的参数既具有明显的物理意义，且采优化段保证了拟合精度，因而确定的疲劳曲线与试验数据吻合很好。

（2）对于GH4169合，通斜率法、四点相关法、修正的通斜率法和修正的四点相关法确定的疲劳延性系数虽与断裂真应变接近，但其明显高于材料数据手册和本文发展的方法确定的相应值，且4种传统方法确定的 $c$ 值又相对偏大（绝对值偏小），因而对于GH4169合，4种传统方法确定的疲劳曲线低循环疲劳部分与试验数据差别较，材料数据册和本发展法确定的疲劳曲线与试验结果吻合较好。

（3）对于GH901合，通斜率法确定的疲劳延性系数 $ { \varepsilon } _ { f } ^ { \prime }$ 太，四点相关法确定的疲劳延性系数 $ { \varepsilon } _ { \mathrm { f } } ^ { \prime }$ 相对合适，其确定的疲劳延性指数 $c$ 值却过大（绝对值小），修正的通用斜率法与通用斜率法一样确定的疲劳延性系数 $ { \varepsilon } _ { i } ^ { \prime }$ 过大，修正的四点相关法确定的疲劳延性系数 $\varepsilon _ { f } ^ { \prime }$ 过，同时疲劳延性指数 $c$ 值也相对较大（绝对值小），而材料数据手册确定的疲劳延性系数 $\varepsilon _ { \mathrm { f } } ^ { \prime }$ 虽然稍一些，但是通过疲劳延性指数 $c$ 值的调整，其确定的疲劳曲线低循环疲劳部分相前4种法要好，但精度仍不能满要求。本发展的法，则在明确疲劳延性系数物理意义的基础上，采用非线性优化，通过调整疲劳延性指数 $c$ 值，实现了拟合曲线与试验结果很好的吻合。

以上仅是分别就4个疲劳参数对应变疲劳曲线的循环疲劳部分（弹性部分）和低循环疲劳部分（塑性部分）的单独影响分析，而总应变方程是这两部分的结合，这种结合会导致更为复杂的线性影响，造成拟合曲线与试验结果更的偏离或者降低这种偏离程度。因此，本文在保证总应变寿命程参数物理意义的基础上，采用线性优化的段很好地解决了保证物理意义和精度两的要求，为总应变寿命程参数的确定提供了一条可借鉴的途径。

# 1.3 考虑应梯度影响的缺疲劳寿命预测法

# 1.3.1 TC4钛合金材料数据

由航空发动机材料数据册[14]以及1.2节中发展的总应变寿命程参数获取法，可得到TC4钛合材料室温条件下的材料参数，见表1-9。TC4钛合材料的循环应应变曲线如图1-14所示。

表1-9室温条件下TC4钛合金材料的力学性能参数[14]  

<table><tr><td rowspan=1 colspan=1>参数</td><td rowspan=1 colspan=1>数值</td></tr><tr><td rowspan=1 colspan=1>E/MPa</td><td rowspan=1 colspan=1>109000</td></tr><tr><td rowspan=1 colspan=1>K&#x27;/MPa</td><td rowspan=1 colspan=1>1420</td></tr><tr><td rowspan=1 colspan=1>n′</td><td rowspan=1 colspan=1>0.07</td></tr><tr><td rowspan=1 colspan=1>σ/MPa</td><td rowspan=1 colspan=1>1646.75</td></tr><tr><td rowspan=1 colspan=1>b</td><td rowspan=1 colspan=1>-0.11</td></tr><tr><td rowspan=1 colspan=1>cf}$</td><td rowspan=1 colspan=1>0.3918</td></tr><tr><td rowspan=1 colspan=1>c</td><td rowspan=1 colspan=1>-0.632</td></tr></table>

![](images/5bd2444c0c727509798f322ecaa92dd806d310ff053e22a4395ebbf663ccc9c0.jpg)  
图1-14 室温条件下TC4钛合材料的循环应应变曲线

航空发动机材料数据册给出的TC4钛合材料光滑试样及理论应集中系数为$K _ { 1 } = 3$ 和 $K _ { \iota } = 5$ 的两种缺口试样的疲劳强度见表1-10，对应的应力寿命（S-N）曲线如图1-15所。

表1-10室温下TC4钛合金棒材的疲劳强度[14]   

<table><tr><td colspan="1" rowspan="3">Nr</td><td colspan="6" rowspan="1">Omax/MPa</td></tr><tr><td colspan="2" rowspan="1">$K₁ =1</td><td colspan="2" rowspan="1">K₁=3</td><td colspan="2" rowspan="1">K₁=5</td></tr><tr><td colspan="1" rowspan="1">R =0.1</td><td colspan="1" rowspan="1">$R = -1}$</td><td colspan="1" rowspan="1">R=0.1</td><td colspan="1" rowspan="1">$R = -1</td><td colspan="1" rowspan="1">R=0.1</td><td colspan="1" rowspan="1">R = -1</td></tr><tr><td colspan="1" rowspan="1">5×10^{$</td><td colspan="1" rowspan="1">945</td><td colspan="1" rowspan="1">740</td><td colspan="1" rowspan="1">580</td><td colspan="1" rowspan="1">395</td><td colspan="1" rowspan="1">410</td><td colspan="1" rowspan="1">300</td></tr><tr><td colspan="1" rowspan="1">104</td><td colspan="1" rowspan="1">845</td><td colspan="1" rowspan="1">640</td><td colspan="1" rowspan="1">480</td><td colspan="1" rowspan="1">330</td><td colspan="1" rowspan="1">360</td><td colspan="1" rowspan="1">250</td></tr><tr><td colspan="1" rowspan="1">5×104</td><td colspan="1" rowspan="1">670</td><td colspan="1" rowspan="1">470</td><td colspan="1" rowspan="1">315</td><td colspan="1" rowspan="1">220</td><td colspan="1" rowspan="1">245</td><td colspan="1" rowspan="1">150</td></tr><tr><td colspan="1" rowspan="1">105$</td><td colspan="1" rowspan="1">620</td><td colspan="1" rowspan="1">425</td><td colspan="1" rowspan="1">280</td><td colspan="1" rowspan="1">190</td><td colspan="1" rowspan="1">205</td><td colspan="1" rowspan="1">120</td></tr><tr><td colspan="1" rowspan="1">5×10{$</td><td colspan="1" rowspan="1">550</td><td colspan="1" rowspan="1">355</td><td colspan="1" rowspan="1">260</td><td colspan="1" rowspan="1">150</td><td colspan="1" rowspan="1">135</td><td colspan="1" rowspan="1">80</td></tr><tr><td colspan="1" rowspan="3">Ni</td><td colspan="6" rowspan="1">Omax/MPa</td></tr><tr><td colspan="2" rowspan="1">K=1</td><td colspan="2" rowspan="1">K₁=3</td><td colspan="2" rowspan="1">$K₁=5</td></tr><tr><td colspan="1" rowspan="1">R =0.1</td><td colspan="1" rowspan="1">R=-1</td><td colspan="1" rowspan="1">R =0.1</td><td colspan="1" rowspan="1">R = -1</td><td colspan="1" rowspan="1">R =0.1</td><td colspan="1" rowspan="1">R = -1</td></tr><tr><td colspan="1" rowspan="1">10 $</td><td colspan="1" rowspan="1">540</td><td colspan="1" rowspan="1">350</td><td colspan="1" rowspan="1">260</td><td colspan="1" rowspan="1">150</td><td colspan="1" rowspan="1">115</td><td colspan="1" rowspan="1">72</td></tr><tr><td colspan="1" rowspan="1">$10{$</td><td colspan="1" rowspan="1">540</td><td colspan="1" rowspan="1">346</td><td colspan="1" rowspan="1">258</td><td colspan="1" rowspan="1">148</td><td colspan="1" rowspan="1">109</td><td colspan="1" rowspan="1">68</td></tr></table>

![](images/a2c9c36ccb35996edf66e62da1facf53cf7f6ed451fbd5fbd643563dda97f77c.jpg)  
图1-15 室温下TC4钛合棒材的光滑及缺试样 $S { - } N$ 曲线

# 1.3.2 局部应力/应变法

局部应/应变法计算简单，在程中被泛采，本节即采局部应/应变法对室温条件下TC4钛合缺口试样进疲劳寿命预测。

1.3.2.1 诺伊贝尔（Neuber） 法求解局部应力/应变

在缺口局部应/应变的诸多数值计算法中，Neuber法由于简单实，在工程中被泛应用，采Neuber法进缺构件局部应/应变计算涉及的公式如下

$$
\sigma \varepsilon = \frac { K _ { \mathrm { t } } ^ { 2 } \left( \sigma _ { n } \right) ^ { 2 } } { E }
$$

$$
\varepsilon = \frac { \sigma } { E } + \left( \frac { \sigma } { K ^ { \prime } } \right) ^ { \frac { 1 } { n ^ { \prime } } }
$$

$$
\Delta \sigma \Delta \varepsilon = \frac { K _ { 1 } ^ { 2 } ( \Delta \sigma _ { \circ } ) ^ { 2 } } { E }
$$

$$
\Delta \varepsilon = \frac { \Delta \sigma } { E } + 2 \left( \frac { \Delta \sigma } { 2 K ^ { \prime } } \right) ^ { \frac { 1 } { n ^ { \prime } } }
$$

式中： $\sigma$ (id:) 缺局部应； $\varepsilon$ 缺口局部应变； $\sigma _ { n }$ (id:) 名义应力； $\Delta \sigma$ (id:) 缺口局部应力范围； $\Delta \varepsilon$ (i:) 缺口局部应变范围。

其中，式（1-21）和式（1-22）于确定局部危险点的最应/应变，式（1-23）和式(1-24）用于确定局部危险点的应/应变范围。局部应/应变求解过程如图1-16所。

![](images/e3117a2a17332c960a8003bcff268ba8497e95848359acca1a96d12e329f71b4.jpg)  
图1-16 Neuber法求解缺局部应/应变[17]

根据实际程使经验，Neuber法对缺局部应/应变的估计略偏，为了提寿命预测精度，将Neuber公式中的理论应集中系数 $K _ { \iota }$ 用疲劳缺系数 $K _ { f }$ 替代，得到修正的Neuber公式如下

$$
\sigma \varepsilon = \frac { K _ { \mathrm { f } } ^ { 2 } \left( \sigma _ { \mathrm { n } } \right) ^ { 2 } } { E }
$$

$$
\varepsilon _ { \mathrm { a } } = \frac { \sigma _ { \mathrm { a } } } { E } + \left( \frac { \sigma _ { \mathrm { a } } } { K ^ { \prime } } \right) ^ { \frac { 1 } { n ^ { \prime } } }
$$

$$
\Delta \sigma \Delta \varepsilon = \frac { K _ { \mathrm { f } } ^ { 2 } \ ( \Delta \sigma _ { \mathrm { n } } ) ^ { 2 } } { E }
$$

$$
\Delta \varepsilon = \frac { \Delta \sigma } { E } + 2 \left( \frac { \Delta \sigma } { 2 K ^ { \prime } } \right) ^ { \frac { 1 } { n ^ { \prime } } }
$$

由上式可以看出，采修正的Neuber法计算缺局部应/应变，需要确定缺构件的疲劳缺系数 $K _ { \mathrm { f } }$ ，对于 $K _ { \mathrm { f } }$ 的确定，程上常的有著名的诺伊贝尔-库恩（Neuber-Kuhn）公式[17]

$$
K _ { t } = 1 + { \frac { K _ { t } - 1 } { 1 + { \sqrt { a / \rho } } } }
$$

以及彼得森（Peterson）公式[18]

$$
K _ { \mathrm { f } } = 1 + { \frac { K _ { \mathrm { t } } - 1 } { 1 + a / \rho } }
$$

式中， $\rho$ 为缺口半径， $a$ 为材料常数，查表获得。

对于以上两式，有计算表明Peterson公式计算出来的 $K _ { \mathrm { f } }$ 值偏于保守，因而本文选用Neuber-Kuhn公式计算 $K _ { \mathrm { f } }$ 。机械程册[19]推荐的 $a$ 值曲线如图1-17所。结合TC4钛合的拉伸强度得到TC4钛合的 $a ^ { 1 / 2 }$ 值为0.23。

![](images/4837b6a8e842733a210607721597adac0e04634bfc578f18c55270a35de3c8f7.jpg)  
图1-17 Neuber-Kuhn公式中的 $a ^ { 1 / 2 }$ 值

对于 $K _ { 1 } = 3$ 和 $K _ { \mathrm { t } } = 5$ 的缺口试样，缺口半径 $\rho$ 分别为 $0 . 3 4 \mathrm { m m }$ 和 $0 . 1 \mathrm { m m }$ ，因而所得两种试样的疲劳缺系数 $K _ { i }$ 分别为2.43和3.32。结合表1-10和式 $( 1 - 2 1 ) \sim$ 式（1-24）以及式（1-25） $\sim$ 式（1-28），可采Neuber法和修正Neuber法计算得到两种缺试样的局部应/应变，见表1-11和表1-12。

表1-11 Neuber法获得的TC4钛合缺口试样的局部应/应变  

<table><tr><td colspan="1" rowspan="1">缺口试样</td><td colspan="1" rowspan="1">外载应力比R</td><td colspan="1" rowspan="1">寿命N</td><td colspan="1" rowspan="1">8=1%</td><td colspan="1" rowspan="1">0max/MPa</td><td colspan="1" rowspan="1">局部应力比R'</td></tr><tr><td colspan="1" rowspan="8">K₁=3</td><td colspan="1" rowspan="4">0.1</td><td colspan="1" rowspan="1">5×103</td><td colspan="1" rowspan="1">0.00727</td><td colspan="1" rowspan="1">1064.59605</td><td colspan="1" rowspan="1">-0.454</td></tr><tr><td colspan="1" rowspan="1">104</td><td colspan="1" rowspan="1">0.00595</td><td colspan="1" rowspan="1">1022.82705</td><td colspan="1" rowspan="1">-0.265</td></tr><tr><td colspan="1" rowspan="1">5×104</td><td colspan="1" rowspan="1">0.0039</td><td colspan="1" rowspan="1">884.26204</td><td colspan="1" rowspan="1">0.038</td></tr><tr><td colspan="1" rowspan="1">105$</td><td colspan="1" rowspan="1">0.00347</td><td colspan="1" rowspan="1">819.15304</td><td colspan="1" rowspan="1">0.077</td></tr><tr><td colspan="1" rowspan="4">-1</td><td colspan="1" rowspan="1">5×10{3$</td><td colspan="1" rowspan="1">0.01327</td><td colspan="1" rowspan="1">970.70705</td><td colspan="1" rowspan="1">-1.000</td></tr><tr><td colspan="1" rowspan="1">104</td><td colspan="1" rowspan="1">0.00993</td><td colspan="1" rowspan="1">905.61604</td><td colspan="1" rowspan="1">-1.000</td></tr><tr><td colspan="1" rowspan="1">5×104</td><td colspan="1" rowspan="1">0.006065</td><td colspan="1" rowspan="1">658.97903</td><td colspan="1" rowspan="1">-1.000</td></tr><tr><td colspan="1" rowspan="1">$10{$</td><td colspan="1" rowspan="1">0.00523</td><td colspan="1" rowspan="1">569.78803</td><td colspan="1" rowspan="1">-1.000</td></tr><tr><td colspan="1" rowspan="1">缺口试样</td><td colspan="1" rowspan="1">外载应力比R</td><td colspan="1" rowspan="1">寿命N</td><td colspan="1" rowspan="1">8_1%</td><td colspan="1" rowspan="1">0max/MPa</td><td colspan="1" rowspan="1">局部应力比R</td></tr><tr><td colspan="1" rowspan="8">K₁ =5</td><td colspan="1" rowspan="4">0.1</td><td colspan="1" rowspan="1">5×103$</td><td colspan="1" rowspan="1">0.00895</td><td colspan="1" rowspan="1">1097.08105</td><td colspan="1" rowspan="1">-0.590</td></tr><tr><td colspan="1" rowspan="1">104</td><td colspan="1" rowspan="1">0.00756</td><td colspan="1" rowspan="1">1071.52905</td><td colspan="1" rowspan="1">-0.486</td></tr><tr><td colspan="1" rowspan="1">5×104</td><td colspan="1" rowspan="1">0.00506</td><td colspan="1" rowspan="1">980.56705</td><td colspan="1" rowspan="1">-0.124</td></tr><tr><td colspan="1" rowspan="1">$10\$</td><td colspan="1" rowspan="1">0.00423</td><td colspan="1" rowspan="1">920.13904</td><td colspan="1" rowspan="1">-0.002</td></tr><tr><td colspan="1" rowspan="4">-1</td><td colspan="1" rowspan="1">5×103</td><td colspan="1" rowspan="1">0.019995</td><td colspan="1" rowspan="1">1032.37505</td><td colspan="1" rowspan="1">-1.000</td></tr><tr><td colspan="1" rowspan="1">104</td><td colspan="1" rowspan="1">0.014535</td><td colspan="1" rowspan="1">986.33305</td><td colspan="1" rowspan="1">-1.000</td></tr><tr><td colspan="1" rowspan="1">5×104</td><td colspan="1" rowspan="1">0.00693</td><td colspan="1" rowspan="1">744.56704</td><td colspan="1" rowspan="1">-1.000</td></tr><tr><td colspan="1" rowspan="1">$10\$</td><td colspan="1" rowspan="1">0.005505</td><td colspan="1" rowspan="1">599.66603</td><td colspan="1" rowspan="1">-1.000</td></tr></table>

表1-12 修正Neuber法获得的TC4钛合金缺口试样的局部应/应变  

<table><tr><td rowspan=1 colspan=1>缺口试样</td><td rowspan=1 colspan=1>外载应力比R</td><td rowspan=1 colspan=1>寿命N</td><td rowspan=1 colspan=1>81%</td><td rowspan=1 colspan=1>σmax/MPa</td><td rowspan=1 colspan=1>局部应力比R</td></tr><tr><td rowspan=8 colspan=1>K=3</td><td rowspan=4 colspan=1>0.1</td><td rowspan=1 colspan=1>5×103$</td><td rowspan=1 colspan=1>0.005825</td><td rowspan=1 colspan=1>1017.65</td><td rowspan=1 colspan=1>-0.245</td></tr><tr><td rowspan=1 colspan=1>104</td><td rowspan=1 colspan=1>0.004815</td><td rowspan=1 colspan=1>965.82</td><td rowspan=1 colspan=1>-0.087</td></tr><tr><td rowspan=1 colspan=1>5×104</td><td rowspan=1 colspan=1>0.00316</td><td rowspan=1 colspan=1>758.41</td><td rowspan=1 colspan=1>0.092</td></tr><tr><td rowspan=1 colspan=1>10\</td><td rowspan=1 colspan=1>0.00281</td><td rowspan=1 colspan=1>678.88</td><td rowspan=1 colspan=1>0.098</td></tr><tr><td rowspan=4 colspan=1>-1</td><td rowspan=1 colspan=1>$5×10{$</td><td rowspan=1 colspan=1>0.00948</td><td rowspan=1 colspan=1>891.68</td><td rowspan=1 colspan=1>-1.000</td></tr><tr><td rowspan=1 colspan=1>104</td><td rowspan=1 colspan=1>0.00747</td><td rowspan=1 colspan=1>789.50</td><td rowspan=1 colspan=1>-1.000</td></tr><tr><td rowspan=1 colspan=1>5×10+</td><td rowspan=1 colspan=1>0.004905</td><td rowspan=1 colspan=1>534.45</td><td rowspan=1 colspan=1>-1.000</td></tr><tr><td rowspan=1 colspan=1>$10\$</td><td rowspan=1 colspan=1>0.004235</td><td rowspan=1 colspan=1>461.58</td><td rowspan=1 colspan=1>-1.000</td></tr><tr><td rowspan=8 colspan=1>K₁=5</td><td rowspan=4 colspan=1>0.1</td><td rowspan=1 colspan=1>5×103$</td><td rowspan=1 colspan=1>0.005625</td><td rowspan=1 colspan=1>1009.02</td><td rowspan=1 colspan=1>-0.213</td></tr><tr><td rowspan=1 colspan=1>104</td><td rowspan=1 colspan=1>0.004935</td><td rowspan=1 colspan=1>973.30</td><td rowspan=1 colspan=1>-0.105</td></tr><tr><td rowspan=1 colspan=1>5×104</td><td rowspan=1 colspan=1>0.00336</td><td rowspan=1 colspan=1>798.78</td><td rowspan=1 colspan=1>0.084</td></tr><tr><td rowspan=1 colspan=1>105</td><td rowspan=1 colspan=1>0.00281</td><td rowspan=1 colspan=1>679.08</td><td rowspan=1 colspan=1>0.098</td></tr><tr><td rowspan=4 colspan=1>-1</td><td rowspan=1 colspan=1>5×103$</td><td rowspan=1 colspan=1>0.01002</td><td rowspan=1 colspan=1>908.22</td><td rowspan=1 colspan=1>-1.000</td></tr><tr><td rowspan=1 colspan=1>104</td><td rowspan=1 colspan=1>0.007785</td><td rowspan=1 colspan=1>811.68</td><td rowspan=1 colspan=1>-1.000</td></tr><tr><td rowspan=1 colspan=1>5×104</td><td rowspan=1 colspan=1>0.00457</td><td rowspan=1 colspan=1>497.88</td><td rowspan=1 colspan=1>-1.000</td></tr><tr><td rowspan=1 colspan=1>$10\$</td><td rowspan=1 colspan=1>0.003655</td><td rowspan=1 colspan=1>398.26</td><td rowspan=1 colspan=1>-1.000</td></tr></table>

# 1.3.2.2 局部应力/应变法寿命预测

基于前述所得的TC4钛合两种缺试样的缺口局部应/应变，采用局部应/应变法开展寿命预测，由表1-11和表1-12可知，不同外载条件下试样缺局部的应不同，因此，选用可考虑平均应影响的寿命预测法对缺口试样进寿命预测，包括史密斯-沃森-托佩尔（ $\mathrm { S m i t h - W a t s o n - T o p e r }$ ，SWT）寿命预测法和莫罗（Morrow）平均应力修正的寿命预测方法。

（1）基于SWT法的疲劳寿命预测

将表1-9材料参数代下式可得室温条件下TC4钛合材料的总应变寿命程

$$
\frac { \Delta \varepsilon _ { \mathrm { t } } } { 2 } = \frac { \sigma _ { \mathrm { f } } ^ { \prime } } { E } ( 2 N _ { \mathrm { f } } ) ^ { 6 } + \varepsilon _ { \mathrm { f } } ^ { \prime } ( 2 N _ { \mathrm { f } } ) ^ { c }
$$

式（1-31）的总应变寿命程是针对应比 $R = - 1$ 时建的，为进对称循环条件下的寿命预测，对上述程进修正，得到SWT程[4]

$$
\varepsilon _ { \mathrm { a } } \sigma _ { \mathrm { m a x } } = \frac { ( \sigma _ { \mathrm { f } } ^ { \prime } ) ^ { 2 } } { E } ( 2 N _ { \mathrm { f } } ) ^ { 2 b } + \sigma _ { \mathrm { f } } ^ { \prime } \varepsilon _ { \mathrm { f } } ^ { \prime } ( 2 N _ { \mathrm { f } } ) ^ { b + c }
$$

式中： $\varepsilon _ { \mathrm { a } }$ -考核点的应变幅值；

$\sigma _ { \mathrm { { m a x } } }$ 考核点的最大应力。

此式则可对对称循环和对称循环载荷条件下的疲劳试样进寿命预测。将表1-11和表1-12中采Neuber法和修正Neuber法计算所得的缺局部应/应变结果代式（1-32），预测得到的TC4钛合材料缺试样的疲劳寿命结果如图1-18所。

![](images/639b8fbb80133e95c1b7c3a5325c03f24637312a86c373dd5be3774f5710102c.jpg)  
图1-18采SWT法的缺疲劳寿命预测

由图1-18可见，采局部应/应变法，基于Neuber法所得的缺口局部应/应变计算结果，考虑平均应影响的SWT法得出的寿命预测结果过于保守，寿命分散带较，最达50倍；基于修正Neuber法所得的局部应/应变的SWT法的寿命预测结果优于基于Neuber法的预测，分散带在10倍左右，但预测寿命同样偏于保守。

(2）基于Morrow平均应修正的疲劳寿命预测对TC4钛合材料的总应变寿命程，进Morrow平均应修正后可得

$$
\varepsilon _ { \mathrm { a } } = \frac { \sigma _ { \mathrm { f } } ^ { \prime } - \sigma _ { \mathrm { m } } } { E } ( 2 N _ { \mathrm { f } } ) ^ { b } + \varepsilon _ { \mathrm { f } } ^ { \prime } ( 2 N _ { \mathrm { f } } ) ^ { b }
$$

式中： $\sigma _ { \mathrm { { m } } }$ (id -考核点平均应。

此式同样可对对称循环和对称循环载荷条件下的试样进寿命预测。将表1-9、表1-11和表1-12中结果代式（1-33），预测得到的TC4钛合材料缺试样疲劳寿命结果如图1–19所。

由图1-19可以看出，采局部应/应变法，无论是基于Neuber法还是修正Nue-ber法计算所得的缺局部应/应变结果，Morrow平均应修正法给出的TC4钛合缺口试样疲劳寿命预测结果均优于SWT法所得的相应寿命预测结果，但基于Neu-ber法局部应/应变结果的寿命预测分散带仍有39倍，而基于修正Neuber法局部应/应变结果的寿命预测分散带也有5倍左右，总体来看仍是过于保守。

综上所述，可以看出，基于Neuber法计算得到的局部应/应变，进TC4钛合缺口试样疲劳寿命预测，寿命预测分散带为 $4 0 \sim 5 0$ 倍。基于修正的Neuber法局部应/应变计算结果，寿命预测精度得到一定程度的改善，但寿命分散带仍有5\~10倍，寿命预测结果偏于保守。虽然保守的预测结果有利于保证结构的安全性，但是过于保守势必导致材料潜力不能充分发挥，不能满足准确评估构件预期使用寿命的需要。

![](images/0ec38bb6d4d4db33aa94c3b69cd8115e8bcd7a05a61f3963b23ae8a578815860.jpg)  
（a）基于Neuber法获得的局部应力/应变的寿命预测

![](images/a51926ec05ba08e706f46f207615bb006edf9250e05b04a39efa4efdadf11be1.jpg)  
图1-19 采Morrow平均应修正法的缺口疲劳寿命预测

# 1.3.3 考虑应力梯度影响的缺口疲劳寿命预测

前述工程中常用的局部应力/应变法难以满准确预测构件疲劳寿命的需要，为了既能适合工程应用，又可以提疲劳寿命预测精度，本节在局部应力/应变法计算分析的基础上，结合缺试样弹性有限元分析，根据试样缺口根部区域应分布规律，综合考虑平均应力、应力梯度和尺寸效应的影响，发展了一种考虑应力梯度影响的缺口疲劳寿命预测法。以TC4钛合材料含两种形式缺( $K _ { 1 } = 3$ 和 $K _ { \ast } = 5$ ）的试样为例，求得应梯度与尺寸效应的影响因，然后对缺试样开展了疲劳寿命预测[。

# 1.3.3.1 缺口疲劳寿命预测模型的构建

总应变寿命程是应变疲劳寿命预测的基本程[9]，既能描述低循环疲劳特征，又能描述循环疲劳特征，但该程是针对对称循环载荷（即应比 $R = - 1$ ）的光滑试样试验数据建的，因而需针对缺口疲劳影响因素，如平均应力、应力梯度和尺寸效应，将其引总应变寿命程中，建种新的考虑多种影响因素的疲劳寿命预测模型。

# (1）平均应力的影响

缺口构件的局部区域由于应集中会导致应。在相对不是很的外载荷下，虽然构件主体仍处于弹性状态，但是缺的局部区域可能已进了塑性状态，尤其是对称循环载荷情况下，外载荷（应）已不能表征缺处的局部应，有必要在疲劳寿命预测程中引缺口处的局部应的影响[1]。

关于在循环载荷作用下平均应对构件疲劳寿命的影响，前的研究已清楚表明平均应会对裂纹萌寿命产重要影响。基于此众多研究者如Morrow[20]、Smith-Watson–Toper[4]和沃克（Walker)[5]等，发展了多种关于平均应修正的寿命预测模型，并泛应于疲劳寿命预测，道林（Dowling)[21]对分析了4种可考虑平均应影响的寿命预测模型，结果表明，Walker寿命模型中的 $\gamma$ 项可对平均应进调整，其寿命预测的精度较好。因此，本采Walker寿命预测模型[ll以考虑缺处局部平均应的影响，其寿命程形式如下

$$
\varepsilon _ { \mathrm { a } } = \frac { \sigma _ { \mathrm { f } } ^ { \prime } } { E } \Big [ 2 N _ { \mathrm { f } } \left( \frac { 1 - R } { 2 } \right) ^ { ( 1 - \gamma ) / b } \Big ] ^ { b } + \varepsilon _ { \mathrm { f } } ^ { \prime } \Big [ 2 N _ { \mathrm { f } } \left( \frac { 1 - R } { 2 } \right) ^ { ( 1 - \gamma ) / b } \Big ] ^ { c }
$$

(2）应梯度的影响

随着对结构疲劳问题研究的深，表明应力梯度显著影响缺口处疲劳强度，因而应将其引到寿命预测模型，研究其对缺口疲劳寿命的影响，这也是目前寿命研究的一个热点[1】。尽管前发展的多种寿命预测法中已经可以考虑应梯度的影响，诸如泰勒（Taylor）的临界距离法、应力场强法和修正的体积法等 $[ 1 , 2 2 \sim 2 4 ]$ ，可是上述法或者需要繁琐复杂的计算过程，或者需要大量的材料宏观和微观试验数据，因而对于实际程中结构件的寿命预测，应这些法还存在着些困难。为此，本对缺局部的应梯度进了相关分析以明确其影响。

为考察缺局部应梯度变化规律，先需明确缺局部坐标系，如图1-20所，然后将不同缺试样在单调拉伸载荷条件下，沿缺平分线上进应和距离的归化处理。图1-21给出了当应集中系数 $K _ { \mathrm { r } } = 3$ 和 $K _ { \mathrm { t } } = 5$ 时，V形缺口试样的应力分布，其中 $\sigma / \sigma _ { \operatorname* { m a x } }$ 为缺口平分线上不同距离处应力与缺口根部最大应力之比， $x / r$ 为距缺口根部的距离和缺口半径之比[1]。

![](images/dfa717efd99331b9667c63e01f7b29764ef8790b341919b2eaa1e3d488956bc8.jpg)  
图1-20 缺局部坐标系及应力分布示意图

![](images/e2d2516fce6323d4440d5a408ee2eb84f35152bc025dc378be67095be783b72c.jpg)  
图1-21 不同缺归化应沿缺平分线归化距离上的分布

图1-21表明在对缺口平分线上的应力和距离进行归一化后，当缺口根部处的归一化距离小于0.5时，即使试样的应力集中系数不同，其缺口平分线上的归一化应力也基本相同，因而本文提出的应力梯度影响因子 $Y$ 的定义[]为

定义1

$$
Y = \frac { 1 } { 2 S _ { 0 . 5 } }
$$

式中， $S _ { 0 . 5 }$ 表示在 $0 \leqslant x / r \leqslant 0 . 5$ 区间上归化应曲线和坐标轴所围成的积（积分）。采用这样定义的好处是：首先当应均匀分布（没有应集中）时，此时无梯度影响，因而应力梯度影响因子等于1；其次采用积分法求面积而不是直接计算应力梯度，可以避免因为数值求导导致精度降低。采用此因子 $Y$ 修正了缺口处的局部应/应变，进而建了缺与光滑试样之间的对应关系，修正的疲劳寿命程[为

$$
\varepsilon _ { \mathrm { a } } = Y ^ { m } \biggl \{ \frac { \sigma _ { \mathrm { f } } ^ { \prime } } { E } \biggl [ 2 N _ { \mathrm { f } } \left( \frac { 1 - R ^ { \prime } } { 2 } \right) ^ { ( 1 - \gamma ) / b } \biggr ] ^ { b } + \varepsilon _ { \mathrm { f } } ^ { \prime } \biggl [ 2 N _ { \mathrm { f } } \left( \frac { 1 - R ^ { \prime } } { 2 } \right) ^ { ( 1 - \gamma ) / b } \biggr ] ^ { c } \biggr \} ,
$$

式中， $R ^ { \prime }$ 是缺口局部应力比，表征了缺口局部应力比的影响程度， $m$ 是应力梯度影响指数，表征了应力梯度的影响，在研究分析航空发动机材料数据册中多种材料的试验数据基础上，发现 $m$ 与试验疲劳寿命的关系[]为

$$
m = A \ ( 2 N _ { \mathrm { f } } ) ^ { B }
$$

式中，A和 $B$ 均为材料常数，可采取拟合材料试验数据获得。

(3）尺寸效应的影响

当构件处于非均匀应力状态，即使危险点处有相同的应力值，但因其应力梯度的不同，也会造成构件疲劳失效区范围以及疲劳寿命的不同，从而导致处于均匀应力场中的构件的尺寸效应[。但是，前有关构件均匀应场的尺寸效应研究较少，因研究均匀应力场带来的尺寸效应影响，并引到寿命预测模型中，势必会推动寿命预测方法的进步发展。为此，图1-22给出了 $K _ { \mathrm { r } } = 3$ 和 $K _ { \iota } = 5$ 两种V形缺口试样缺口平分线上仅应归一化的分布规律，表征非均匀应场的尺寸效应影响

![](images/0c9688d9d9ec579084506e7ba900d012f089591637ca50850a91b9bde7eb44d9.jpg)  
图1-22 不同缺归化应沿缺口平分线的分布

由图1-22可见：应集中程度不同将导致其影响疲劳寿命的距离和应梯度也不同；为此，引入平均应力梯度 ${ { \boldsymbol { g } } _ { \mathrm { ~ c ~ } } } ^ { r }$ （以缺口根部平分线上两点归一化应力 $\sigma _ { \mathrm { n o m } }$ 之差与对应两点距离比值来定义），进而用 $g _ { \mathrm { ~ e ~ } }$ 来描述尺寸效应的影响[1]。

定义2

$$
\displaystyle \boldsymbol { g } _ { \mathrm { c } } = \frac { \boldsymbol { \sigma } _ { \mathrm { n o m } } \mid _ { \boldsymbol { x } = r / 2 } - \boldsymbol { \sigma } _ { \mathrm { n o m } } \mid _ { \boldsymbol { x } = 0 } } { r / 2 }
$$

考虑到材料册中通常给出应集中系数 $K _ { \mathrm { t } } = 3$ 的缺口试样的试验数据，因而以$K _ { \mathrm { t } } = 3$ 缺口试样缺口处的平均应力梯度 $g _ { 3 }$ 为参考来定义尺寸影响因子 $C ^ { [ 1 ] }$ o

定义3

$$
C = \frac { g _ { \mathrm { ~ c ~ } } } { g _ { 3 } }
$$

这里为了确定尺寸影响因子 $C$ ，定义的平均应力梯度 ${ \boldsymbol { g } } _ { \mathrm { c } }$ 是在缺口平分线上选取 $r / 2$ 距离所对应的应力梯度，其原因是，一是当 $x$ 不超过 $r / 2$ 时，尺寸影响因子 $C$ 变化微，相对稳健；是更便于与应梯度影响因中的归化距离0.5相统。尺寸影响因与应梯度影响因共同来修正缺口处的局部应变，可获得考虑平均应力、应梯度及尺寸效应综合影响的缺疲劳寿命预测程[1]为

$$
\varepsilon _ { \mathrm { a } } = Y ^ { m C ^ { \alpha } } \biggl \{ \frac { \sigma _ { \mathrm { f } } ^ { \prime } } { E } \biggl [ 2 N _ { \mathrm { f } } \left( \frac { 1 - R ^ { \prime } } { 2 } \right) ^ { ( 1 - \gamma ) / b } \biggr ] ^ { b } + \varepsilon _ { \mathrm { f } } ^ { \prime } \biggl [ 2 N _ { \mathrm { f } } \left( \frac { 1 - R ^ { \prime } } { 2 } \right) ^ { ( 1 - \gamma ) / b } \biggr ] ^ { c } \biggr \}
$$

式中， $\alpha$ 为尺寸效应影响指数，可通过试验数据拟合获得。至此，便构建了完整的考虑梯度影响的缺口疲劳寿命预测模型。

（4）寿命模型中局部应力/应变的获取

前述已完成寿命预测模型的构建，如何快速有效获得缺口局部应力/应变以便开展寿命预测便成为个关键问题。通过1.3.2节Neuber法和修正Neuber法计算分析可知，需要获得缺的理论应集中系数和疲劳缺系数，这对于标准试样相对简单，而对于实际复杂结构件却难以准确获得；而采用有限元法，本章引也已提及对于缺口局部产塑性变形时，弹性计算不能反映局部真实应/应变，而弹塑性计算对于复杂结构件的计算却过程复杂且耗时较长，具有定的难度，因本将弹性有限元计算分析和Neuber法结合起来，通过复杂构件的弹性有限元分析，将获得的最应/应变和应/应变范围结合式（1-21） $\sim$ 式（1-24）估算缺口构件的局部弹塑性应/应变。此法解决了难以确定真实复杂构件理论应力集中系数和疲劳缺口系数的困难，特别适于结构案的初始设计阶段，简便有效地获得构件的应/应变，并可进步预测构件的疲劳寿命，缩短产品设计研制周期。

1.3.3.2 基于考虑应力梯度影响的寿命预测方法的TC4钛合金缺口试样寿命预测

本节采TC4钛合缺口试样疲劳试验数据对所发展的考虑应力梯度影响的寿命预测方法进预测精度评估，以考察其准确性[1]。

（1）确定平均应力修正参数

根据表1-9和表1-10中TC4钛合材料的疲劳试验数据及不同应下光滑试样的疲劳试验数据，并利式（1-34）得到缺局部平均应修正的Walker寿命程中的参数（见表1–13)。

表1-13 TC4钛合金材料Walker寿命程中的参数  

<table><tr><td rowspan=1 colspan=1>σ/ Pa</td><td rowspan=1 colspan=1>b</td><td rowspan=1 colspan=1>8}$</td><td rowspan=1 colspan=1>C</td><td rowspan=1 colspan=1>Y</td></tr><tr><td rowspan=1 colspan=1>1646.75</td><td rowspan=1 colspan=1>-0.11</td><td rowspan=1 colspan=1>0.3918</td><td rowspan=1 colspan=1>-0.632</td><td rowspan=1 colspan=1>0.499</td></tr></table>

图1-23给出了基于Walker平均应修正的寿命程的预测结果，图中 $N _ { _ { \mathrm { ~ w ~ } } } ^ { \ast }$ 为平均应修正后的Walker等效寿命，其表达式为

$$
N _ { \mathrm { v } } ^ { \ast } = N _ { \mathrm { f } } \left( { \frac { 1 - R } { 2 } } \right) ^ { \frac { ( 1 - \gamma ) } { b } }
$$

可见，在不同应条件下，对于TC4钛合光滑试样，采Walker寿命程预测的结果与试验吻合得很好，表明Walker寿命程可以较好的适于考虑平均应的影响[1]。

![](images/6518bbd4094006d1deecb84a8174a63a08138b26a497b9617c23cb92e0ee8d87.jpg)  
图1-23 Walker平均应修正的寿命预测曲线

（2）确定应力梯度影响因

先对缺试样进弹性有限元分析，以确定应梯度影响因，并得到缺平分线上的局部应分布。图1–24给出了TC4钛合圆棒缺试样的有限元分析结果，按照缺平分线上的归化应与归化距离的关系，计算出式（1-35）的应梯度影响因子 $Y ^ { [ 1 ] }$ 为

$$
Y = \frac { 1 } { 2 S _ { 0 . 5 } } = 1 . 4 4
$$

利用 $K _ { \mathrm { r } } = 3$ 缺试样的试验数据拟合得到应梯度影响指数 $m$ ，这是按照关系式（1-37）拟合了 $K _ { \mathrm { t } } = 3$ , $R = - 1$ 和 $R = 0 . 1$ 条件下的缺口试样的试验数据，其结果如图1-25所示，其中 $A = 1 5 , 3 2 2$ , $B = - 0 . 2 5 8$

![](images/a0ee04583e1ae11434701a37b42cbf5bc8b1d021a4350bf88c10178e6ffa4ff1.jpg)  
图1-24 $K _ { \ast } = 3$ 缺口试样的弹性应力分布

![](images/9bd679b8204d14eab85060c987f956564066c395c4e9d81e22bcdbccff9c802a.jpg)  
图1-25 应梯度影响指数 $m$ 与 $2 N _ { \mathrm { f } }$ 的拟合关系

（3）确定尺寸影响因子

图1-26给出了TC4钛合材料 $K _ { \mathrm { t } } = 3$ 和 $K _ { \mathrm { r } } = 5$ 缺口试样在缺口平分线上的归一化应随距离的分布规律，表1-14给出了根据式（1-38）计算得到的距缺口根部不同距离处的 ${ \boldsymbol { g } } _ { \mathrm { c } }$ 值和尺寸影响因子 $C$ ,表明在 $x \leqslant r / 2$ 时， $C$ 值的变化微，此结论进步说明选取缺口平分线上距离 $x = r / 2$ 来计算平均应力梯度的合理性[1]。

当计算出尺寸影响因 $C$ 以后，采用 $K _ { \mathrm { t } } = 5$ , $R = { \bf \nabla } - 1$ 和 $R = 0 , 1$ 条件下缺口试样的疲劳试验数据，根据式（1-40）来确定尺寸效应影响指数 $\alpha ^ { [ 1 ] }$ 。根据前述 $K _ { \mathrm { t } } = 5$ 的TC4钛合缺试样的试验数据、计算的应梯度影响因 $Y$ 和应梯度影响指数 $m$ ,进而计算确定影响指数 $\alpha$ 值（见表1-15），再求算术平均值可得 $\alpha = 0 . 3 1 8$

![](images/3c18aa3db59cb9a1c5758695a27968381af58fe67106413075710db2a2406f3e.jpg)  
图1-26 TC4钛合缺试样缺平分线归化应分布

表1-14 缺口平分线上不同距离的 $g _ { \mathrm { c } }$ 值  

<table><tr><td rowspan=1 colspan=1>Bc</td><td rowspan=1 colspan=1>8值</td><td rowspan=1 colspan=1>gc</td><td rowspan=1 colspan=1>g值</td></tr><tr><td rowspan=1 colspan=1>3 |r/4</td><td rowspan=1 colspan=1>-3.929</td><td rowspan=1 colspan=1>831+/2</td><td rowspan=1 colspan=1>-2.883</td></tr><tr><td rowspan=1 colspan=1>85 |r/4</td><td rowspan=1 colspan=1>-13.185</td><td rowspan=1 colspan=1>851 +/2</td><td rowspan=1 colspan=1>-9.698</td></tr><tr><td rowspan=1 colspan=1>$C.r/4}$</td><td rowspan=1 colspan=1>3.356</td><td rowspan=1 colspan=1>Cr/2$</td><td rowspan=1 colspan=1>3.364</td></tr></table>

表1-15 尺寸效应影响指数 $_ \alpha$ 值  

<table><tr><td rowspan=1 colspan=1>K</td><td rowspan=1 colspan=1>R</td><td rowspan=1 colspan=1>N</td><td rowspan=1 colspan=1>$C_$</td><td rowspan=1 colspan=1>α</td></tr><tr><td rowspan=8 colspan=1>5</td><td rowspan=4 colspan=1>-1</td><td rowspan=1 colspan=1>5000</td><td rowspan=1 colspan=1>3.588</td><td rowspan=1 colspan=1>0.620</td></tr><tr><td rowspan=1 colspan=1>10000</td><td rowspan=1 colspan=1>4.365</td><td rowspan=1 colspan=1>0.613</td></tr><tr><td rowspan=1 colspan=1>50000</td><td rowspan=1 colspan=1>4.951</td><td rowspan=1 colspan=1>0.326</td></tr><tr><td rowspan=1 colspan=1>100000</td><td rowspan=1 colspan=1>4.948</td><td rowspan=1 colspan=1>0.157</td></tr><tr><td rowspan=4 colspan=1>0.1</td><td rowspan=1 colspan=1>5000</td><td rowspan=1 colspan=1>1.592</td><td rowspan=1 colspan=1>-0.050</td></tr><tr><td rowspan=1 colspan=1>10000</td><td rowspan=1 colspan=1>2.273</td><td rowspan=1 colspan=1>0.075</td></tr><tr><td rowspan=1 colspan=1>50000</td><td rowspan=1 colspan=1>5.182</td><td rowspan=1 colspan=1>0.363</td></tr><tr><td rowspan=1 colspan=1>100000</td><td rowspan=1 colspan=1>6.957</td><td rowspan=1 colspan=1>0.437</td></tr></table>

（4）TC4钛合缺试样寿命预测

前述确定了TC4钛合材料考虑应梯度影响的疲劳寿命预测模型中的全部参数，基于此，对试验条件下TC4钛合两种缺试样开展了疲劳寿命预测。利前节表1-11中Neuber法获得的局部应/应变及局部应结果，代修正的考虑应梯度影响的疲劳寿命预测模型，即式（1–40），寿命预测结果如图1-27所。可以看出：所发展的考虑应梯度影响的疲劳寿命预测法对TC4钛合材料两种缺试样的疲劳寿命预测结果基本在两倍分散带以内，预测精度较为理想。

![](images/085213448df47cb4ddc7bbd4946c90bb829379ec74c627fbc08a31b6831178ba.jpg)  
图1-27 TC4钛合材料缺试样疲劳寿命预测

# 1.4 涡轮盘结构疲劳寿命评估流程及法

# 1.4.1 涡轮盘结构疲劳寿命评估流程

在较的离和温度载荷作下，涡轮盘结构的作应平般较，旦发生破坏，其后果往往是灾难性的。前，国内外均广泛开展了关于涡轮盘强度及寿命预测的法研究，弹塑性应/应变计算和寿命模型的建是涡轮盘寿命预测作的前提和基础。基于前两节所发展的寿命模型进步建了涡轮盘结构疲劳寿命评估流程如图1–28所，其主要实施步骤如下。

（1）开展弹性状态下的涡轮盘应有限元计算分析，获得关键部位的应和应变等，作为基础数据；

（2）利弹性分析得到的应/应变结果采Neuber法计算得到考虑塑性变形影响的应力和应变，作为寿命方程中的计算参数；

（3）利材料数据册中光滑和缺试样的疲劳试验数据拟合得到所发展的寿命方程参数（详见1.2节和1.3节)；

（4）基于步骤（1）中的计算分析结果设计涡轮盘考核部位的模拟试验件，其中着重模拟其应力状态特征；

（5）利用所建的寿命预测模型和应/应变数据进涡轮盘的寿命预测；

![](images/5d75366414a2ed0ed51c712d4c0abc0bb0549f8c14175b68c50f83266e638b0f.jpg)  
图1-28 涡轮盘结构疲劳寿命评估流程

（6）开展模拟试验件的疲劳试验，验证寿命预测结果，同时考核涡轮盘关键部位的寿命。

涡轮盘寿命评估流程涉及的主要技术如下。

（1）寿命方程中材料参数的确定：式（1-20）利断裂真应力、真应变与次拉伸断裂的关系，给出了种新的总应变寿命程参数的确定法，程的未知参数减少为两个（ $b$ 和 $c$ ），可以利用材料数据册中的疲劳试验数据拟合得到。该方法可保证总应变寿命方程中的参数具有明确的物理意义，且对不同材料的拟合结果均十分理想，因本节采这种法确定材料的疲劳参数。

(2）寿命模型的选择：影响涡轮盘低循环疲劳寿命的因素很多，这也是制约寿命模型预测精度的关键。一般认为，平均应、应力梯度及尺寸效应是影响缺口件疲劳寿命的关键因素。1.3节提出了种能够综合考虑上述因素的疲劳寿命预测模型，其寿命模型见式（1-40）。该模型是基于Walker寿命程建的，由于其中含有关于平均应力的可调整的 $\gamma$ 指数项，可以考虑平均应力的影响，并通过引应梯度影响因子与尺寸影响因来考虑应梯度及尺效应的影响。

(3）涡轮盘应/应变参数的获取：准确获得结构件的应/应变参数是进结构疲劳寿命预测的基础。涡轮盘的危险部位如过渡圆角、孔边以及盘心等处由于应力集中的影响，局部区域往往已经进塑性变形。在求解缺局部应/应变的诸多数值计算法中，Neuber法由于简单实，在程中应泛。采Neuber法进缺构件局部应/应变计算涉及的表达式见式(1-21） $\tilde { }$ 式(1-24)。

# 1.4.2 涡轮盘结构的应力/应变分析

# 1.4.2.1 轴对称模型的计算分析

基于上述建立的寿命评估流程，以一个涡轮转子模型为例来说明整个寿命评估的过程及实施步骤。该涡轮转模型由封严盘和涡轮叶/盘组成，首先进轴对称模型的计算分析，所建的有限元模型如图1-29所示，其中包括封严盘、涡轮盘、鼓筒、后轴以及前后挡板等结构件，叶的离心载荷等效为拉应力施加于轮盘相应部位。封严盘和鼓筒的材料取为高强GH4169，前后轴的材料选为优质GH4169，前后挡板的材料取粉末冶FGH95，涡轮盘材料采直接时效GH4169。

![](images/761525f66d44ea0cbae9ab55c46064c045391623fe53c1441815c42facd88a0d.jpg)  
图1-29 涡轮转的轴对称有限元模型

利用涡轮转结构何模型和相关材料数据，得到涡轮叶和轮缘凸块部分的离力，将其等效为拉应力作为有限元计算的应力边界条件。需要说明的是，由于涡轮盘榫槽两对榫齿所承受的离心载荷并不完全相等，通常可认为第一榫齿承受的叶片离心力要于第齿。因此，这将叶载荷的 $60 \%$ 与轮缘凸块载荷的 $40 \%$ 由第一对榫齿承担，将叶载荷的 $40 \%$ 与轮缘凸块载荷的 $60 \%$ 由第二对榫齿承担。

施加的计算边界条件为：

（1）位移约束：约束鼓筒轴前端轴向位移；

(2）离心负荷：取 $100 \%$ 转速的载荷；

（3）盘腔压和温度场：取设计点状态的稳态值；

（4）轮缘应边界条件：轮缘处施加上述等效的离载荷；

（5）转零件间连接式通过定义耦合由度和建接触对来实现，如图1-30所示。

![](images/7b010e5bf0620381b342bfe13eb312492fe29b80ebaca98abc07de0d287b3a68.jpg)  
图1-30 涡轮转构件之间的协调关系

采用有限元法首先计算分析得到涡轮转子结构的温度场，如图1-31所示；而后得到其变形与应，构件的径向应和周向应分布如图1-32所。为了考察关键部位的应平，图1-33给出了各危险部位的编号，不同部位的应见表1-16。由计算结果可知，轮盘靠近轮缘的盘颈处（位置3和4）径向应力较，辐板过渡圆处（位置5和6）的径向应较，而封严盘与涡轮盘的盘心均存在较大的周向应力，这几处高应力区是涡轮盘结构需要重点关注的（危险）区域。

![](images/88510fcf3e358768486470e0742262269d2e25a27deed0a472d29000e7cc8c90.jpg)  
图1-31 涡轮转温度分布

# 1.4.2.2 循环对称模型的计算分析

尽管轴对称模型能够获得整个涡轮转子结构的变形与应平，并降低有限元计算规模，但轴对称模型不能刻画榫槽、螺栓孔等部位的局部应特征。因此，有必要进步开展三维循环对称模型的有限元分析。轮盘上共装有72叶，建其1/72扇区有限元模型如图1-34（a）所，其中节点数为63654，单元数为52535。对于封严盘，其盘沿周向分布有134个通孔，鼓筒和封严盘通过52个周向螺栓孔连接，通孔与螺栓孔数量比为67:26，如果严格按照该例应建1/2扇区模型，格数量将很，为此简化建其1/26扇区模型，每个扇区5个通孔，2个螺栓孔，简化后封严盘的有限元模型如图1-34（b）所，其中有限元节点数为45919，单元数为36556。

![](images/7f753f4b0023d448ae65ecfa6e0e00a884885a047bfd05c1f4c173a781085bab.jpg)  
(a）径向应力

![](images/2e521b1a48e461d7f9e5a3b968c0c3b30e0dae72e98f4c7186c7382d5985b967.jpg)  
图1-32 涡轮转应分布

![](images/9b532064e11706932a2756b5dc9f208012666d21b72039b8030fcfa08cb7bc55.jpg)  
图1-33 涡轮转子危险部位示意图

表1-16 涡轮转子组件危险点应力计算结果  

<table><tr><td rowspan=1 colspan=1>位置</td><td rowspan=1 colspan=1>温度/℃</td><td rowspan=1 colspan=1>径向应力/MPa</td><td rowspan=1 colspan=1>周向应力/MPa</td><td rowspan=1 colspan=1>第一主应力/MPa</td><td rowspan=1 colspan=1>等效应力/MPa</td></tr><tr><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>645.2</td><td rowspan=1 colspan=1>640.78</td><td rowspan=1 colspan=1>0.0000</td><td rowspan=1 colspan=1>665.68</td><td rowspan=1 colspan=1>639.01</td></tr><tr><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>645.6</td><td rowspan=1 colspan=1>890.44</td><td rowspan=1 colspan=1>0.0000</td><td rowspan=1 colspan=1>927.18</td><td rowspan=1 colspan=1>887.90</td></tr><tr><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>603.4</td><td rowspan=1 colspan=1>996.02</td><td rowspan=1 colspan=1>644.56</td><td rowspan=1 colspan=1>1022.4</td><td rowspan=1 colspan=1>892.18</td></tr><tr><td rowspan=1 colspan=1>4</td><td rowspan=1 colspan=1>561.5</td><td rowspan=1 colspan=1>1147.6</td><td rowspan=1 colspan=1>773.92</td><td rowspan=1 colspan=1>1179.8</td><td rowspan=1 colspan=1>1022.8</td></tr><tr><td rowspan=1 colspan=1>5</td><td rowspan=1 colspan=1>585.4</td><td rowspan=1 colspan=1>1024.5</td><td rowspan=1 colspan=1>574.20</td><td rowspan=1 colspan=1>1059.4</td><td rowspan=1 colspan=1>928.04</td></tr><tr><td rowspan=1 colspan=1>6</td><td rowspan=1 colspan=1>529.8</td><td rowspan=1 colspan=1>982.29</td><td rowspan=1 colspan=1>710.64</td><td rowspan=1 colspan=1>1016.6</td><td rowspan=1 colspan=1>895.02</td></tr><tr><td rowspan=1 colspan=1>7</td><td rowspan=1 colspan=1>496.9</td><td rowspan=1 colspan=1>905.63</td><td rowspan=1 colspan=1>797.12</td><td rowspan=1 colspan=1>918.13</td><td rowspan=1 colspan=1>846.66</td></tr><tr><td rowspan=1 colspan=1>8</td><td rowspan=1 colspan=1>517.1</td><td rowspan=1 colspan=1>828.77</td><td rowspan=1 colspan=1>678.19</td><td rowspan=1 colspan=1>829.57</td><td rowspan=1 colspan=1>755.20</td></tr><tr><td rowspan=1 colspan=1>9</td><td rowspan=1 colspan=1>481.7</td><td rowspan=1 colspan=1>13.511</td><td rowspan=1 colspan=1>955.77</td><td rowspan=1 colspan=1>955.77</td><td rowspan=1 colspan=1>1109.2</td></tr><tr><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>605.0</td><td rowspan=1 colspan=1>644.41</td><td rowspan=1 colspan=1>446.33</td><td rowspan=1 colspan=1>645.21</td><td rowspan=1 colspan=1>585.34</td></tr><tr><td rowspan=1 colspan=1>11</td><td rowspan=1 colspan=1>602.9</td><td rowspan=1 colspan=1>778.41</td><td rowspan=1 colspan=1>507.02</td><td rowspan=1 colspan=1>779.92</td><td rowspan=1 colspan=1>702.05</td></tr><tr><td rowspan=1 colspan=1>12</td><td rowspan=1 colspan=1>656.6</td><td rowspan=1 colspan=1>739.41</td><td rowspan=1 colspan=1>321.98</td><td rowspan=1 colspan=1>753.13</td><td rowspan=1 colspan=1>668.53</td></tr><tr><td rowspan=1 colspan=1>13</td><td rowspan=1 colspan=1>643.0</td><td rowspan=1 colspan=1>631.01</td><td rowspan=1 colspan=1>317.91</td><td rowspan=1 colspan=1>667.93</td><td rowspan=1 colspan=1>567.01</td></tr><tr><td rowspan=1 colspan=1>14</td><td rowspan=1 colspan=1>475.8</td><td rowspan=1 colspan=1>2.8681</td><td rowspan=1 colspan=1>991.14</td><td rowspan=1 colspan=1>991.14</td><td rowspan=1 colspan=1>986.66</td></tr></table>

三维有限元分析选八节点六体单元进分析，计算中的位移边界条件取轴对称模型的位移分析结果，同时采设计点状态的温度场和盘腔压分布。计算得到涡轮盘和封严盘的径向应分布如图1-35所。由计算结果可知，循环对称模型与轴对称模型的计算结果相近，应危险位置与应力平均比较接近，表明所施加的边界条件是合理的。此外，涡轮盘螺栓孔边（位置15）的径向应为 $1 2 3 0 . 2 \mathrm { M P a }$ ，封严盘螺栓孔边（位置16）的径向应力为 $1 0 0 2 . 6 \mathrm { M P a }$ 。轮盘的高应力区主要集中在孔边、圆过渡处以及盘位置，在寿命预测分析时应给予重点关注。

![](images/86757f6d79543675053af6bd96cdf7bfb74b60b7ac53db174d37585681199e04.jpg)  
图1-34 涡轮转结构的三维有限元模型

![](images/378b57039b6f7665e183a4f4c0d0d40ff895f5a55d6092582179e48a4eaa9a4a.jpg)  
(a)涡轮盘

![](images/9a6594a941e2a29d829dfcc55704bac83cbae9dbfd81249936cab9cef1f0b9e0.jpg)  
图1-35 涡轮盘和封严盘径向应分布

# 1.4.3涡轮盘结构的疲劳寿命预测

1.4.3.1 寿命方程中材料疲劳参数的确定

进涡轮盘疲劳寿命预测，先需要确定寿命模型中的材料疲劳参数。利材料数据册中的试验数据[14]结合1.2节和1.3节中的参数确定法，先拟合材料（直接时效GH4169和强GH4169）在不同温度下的寿命程参数。两种材料在不同温度下( $5 0 0 ^ { \circ } \mathrm { C } / 6 5 0 ^ { \circ } \mathrm { C }$ ）的光滑疲劳试验数据见表1-17和表1-18，表中给出了总应变范围、应幅值与光滑疲劳试样反向数的对应关系。利表中的试验数据拟合得到总应变寿命程中的4个材料参数，拟合结果如图1-36和图1-37所。由图中可以看出，两种材料在不同温度下的拟合结果均分理想。利用所获得的总应变寿命程参数对试验数据进验证，总应变寿命程给出的寿命预测结果如图1-38和图1-39所，从寿命预测结果可以看出，预测寿命的分散带基本在两倍以内，进步验证了所发展的总应变寿命方程参数确定方法具有较高的精度。

表1-17直接时效GH4169材料 $5 0 0 ^ { \circ } \mathrm { C } / 6 5 0 ^ { \circ } \mathrm { C }$ 条件下光滑试样的疲劳试验数据 $( R = - 1 ) ^ { [ 9 ] }$   

<table><tr><td colspan="3" rowspan="1">500℃温度条件下</td><td colspan="3" rowspan="1">650℃温度条件下</td></tr><tr><td colspan="1" rowspan="1">总应变范围Δε</td><td colspan="1" rowspan="1">反向数2N</td><td colspan="1" rowspan="1">试验应力幅值$/MPa$</td><td colspan="1" rowspan="1">总应变范围Δε</td><td colspan="1" rowspan="1">反向数2N</td><td colspan="1" rowspan="1">试验应力幅值/MPa$</td></tr><tr><td colspan="1" rowspan="1">0.03000</td><td colspan="1" rowspan="1">492</td><td colspan="1" rowspan="1">1089</td><td colspan="1" rowspan="1">0.02626</td><td colspan="1" rowspan="1">160</td><td colspan="1" rowspan="1">833</td></tr><tr><td colspan="1" rowspan="1">0.02612</td><td colspan="1" rowspan="1">458</td><td colspan="1" rowspan="1">1048</td><td colspan="1" rowspan="1">0.02606</td><td colspan="1" rowspan="1">188</td><td colspan="1" rowspan="1">897</td></tr><tr><td colspan="1" rowspan="1">总应变范围Δ</td><td colspan="1" rowspan="1">反向数2N</td><td colspan="1" rowspan="1">试验应力幅值$σ/MPa$</td><td colspan="1" rowspan="1">总应变范围Δ</td><td colspan="1" rowspan="1">反向数2N</td><td colspan="1" rowspan="1">试验应力幅值$$/MPa$</td></tr><tr><td colspan="1" rowspan="1">0.02006</td><td colspan="1" rowspan="1">1662</td><td colspan="1" rowspan="1">981</td><td colspan="1" rowspan="1">0.01804</td><td colspan="1" rowspan="1">414</td><td colspan="1" rowspan="1">826</td></tr><tr><td colspan="1" rowspan="1">0.01602</td><td colspan="1" rowspan="1">2362</td><td colspan="1" rowspan="1">939</td><td colspan="1" rowspan="1">0.02006</td><td colspan="1" rowspan="1">708</td><td colspan="1" rowspan="1">890</td></tr><tr><td colspan="1" rowspan="1">0.01202</td><td colspan="1" rowspan="1">6872</td><td colspan="1" rowspan="1">856</td><td colspan="1" rowspan="1">0.016</td><td colspan="1" rowspan="1">741</td><td colspan="1" rowspan="1">800</td></tr><tr><td colspan="1" rowspan="1">0.02153①</td><td colspan="1" rowspan="1">10000</td><td colspan="1" rowspan="1">1008</td><td colspan="1" rowspan="1">0.012</td><td colspan="1" rowspan="1">2988</td><td colspan="1" rowspan="1">767</td></tr><tr><td colspan="1" rowspan="1">0.01405①</td><td colspan="1" rowspan="1">20000</td><td colspan="1" rowspan="1">903</td><td colspan="1" rowspan="1">0.01635①</td><td colspan="1" rowspan="1">10000</td><td colspan="1" rowspan="1">804</td></tr><tr><td colspan="1" rowspan="1">0.01000</td><td colspan="1" rowspan="1">22174</td><td colspan="1" rowspan="1">817</td><td colspan="1" rowspan="1">0.00904</td><td colspan="1" rowspan="1">10914</td><td colspan="1" rowspan="1">662</td></tr><tr><td colspan="1" rowspan="1">0.01000</td><td colspan="1" rowspan="1">20578</td><td colspan="1" rowspan="1">892</td><td colspan="1" rowspan="1">0.00902</td><td colspan="1" rowspan="1">19808</td><td colspan="1" rowspan="1">699</td></tr><tr><td colspan="1" rowspan="1">0.00902</td><td colspan="1" rowspan="1">31710</td><td colspan="1" rowspan="1">816</td><td colspan="1" rowspan="1">0.01287①</td><td colspan="1" rowspan="1">20000</td><td colspan="1" rowspan="1">753</td></tr><tr><td colspan="1" rowspan="1">0.00862①</td><td colspan="1" rowspan="1">100000</td><td colspan="1" rowspan="1">699</td><td colspan="1" rowspan="1">0.00802</td><td colspan="1" rowspan="1">84046</td><td colspan="1" rowspan="1">642</td></tr><tr><td colspan="1" rowspan="1">0.00757①</td><td colspan="1" rowspan="1">200000</td><td colspan="1" rowspan="1">626</td><td colspan="1" rowspan="1">0.00919①</td><td colspan="1" rowspan="1">100000</td><td colspan="1" rowspan="1">647</td></tr><tr><td colspan="1" rowspan="1">0.00579①</td><td colspan="1" rowspan="1">1000000</td><td colspan="1" rowspan="1">484</td><td colspan="1" rowspan="1">0.00837①</td><td colspan="1" rowspan="1">200000</td><td colspan="1" rowspan="1">607</td></tr><tr><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1">0.00700①</td><td colspan="1" rowspan="1">1000000</td><td colspan="1" rowspan="1">522</td></tr><tr><td colspan="6" rowspan="1">①材料数据册中并未直接给出总应变数据，该数据是利册中循环应应变曲线和对称循环试验应力幅来确定的。</td></tr></table>

表1-18高强GH4169材料 $5 0 0 ^ { \circ } \mathrm { C } / 6 5 0 ^ { \circ } \mathrm { C }$ 条件下光滑试样的疲劳试验数据（ $R = - 1$ [9]  

<table><tr><td colspan="3" rowspan="1">500℃温度条件下</td><td colspan="3" rowspan="1">650℃温度条件下</td></tr><tr><td colspan="1" rowspan="1">总应变范围Δε</td><td colspan="1" rowspan="1">反向数2N</td><td colspan="1" rowspan="1">试验应力幅值σ/MPa</td><td colspan="1" rowspan="1">总应变范围Δet</td><td colspan="1" rowspan="1">反向数2N</td><td colspan="1" rowspan="1">试验应力幅值σ_/MPa$</td></tr><tr><td colspan="1" rowspan="1">0.02996</td><td colspan="1" rowspan="1">288</td><td colspan="1" rowspan="1">983</td><td colspan="1" rowspan="1">0.03000</td><td colspan="1" rowspan="1">208</td><td colspan="1" rowspan="1">876</td></tr><tr><td colspan="1" rowspan="1">0.02402</td><td colspan="1" rowspan="1">1018</td><td colspan="1" rowspan="1">928</td><td colspan="1" rowspan="1">0.02400</td><td colspan="1" rowspan="1">486</td><td colspan="1" rowspan="1">789</td></tr><tr><td colspan="1" rowspan="1">0.02002</td><td colspan="1" rowspan="1">1768</td><td colspan="1" rowspan="1">934</td><td colspan="1" rowspan="1">0.02000</td><td colspan="1" rowspan="1">570</td><td colspan="1" rowspan="1">809</td></tr><tr><td colspan="1" rowspan="1">0.01608</td><td colspan="1" rowspan="1">3082</td><td colspan="1" rowspan="1">870</td><td colspan="1" rowspan="1">0.01802</td><td colspan="1" rowspan="1">798</td><td colspan="1" rowspan="1">762</td></tr><tr><td colspan="1" rowspan="1">0.01200</td><td colspan="1" rowspan="1">8114</td><td colspan="1" rowspan="1">843</td><td colspan="1" rowspan="1">0.01600</td><td colspan="1" rowspan="1">1358</td><td colspan="1" rowspan="1">708</td></tr><tr><td colspan="1" rowspan="1">0.01304①</td><td colspan="1" rowspan="1">10000</td><td colspan="1" rowspan="1">857</td><td colspan="1" rowspan="1">0.01398</td><td colspan="1" rowspan="1">2652</td><td colspan="1" rowspan="1">679</td></tr><tr><td colspan="1" rowspan="1">0.01100</td><td colspan="1" rowspan="1">11743</td><td colspan="1" rowspan="1">794</td><td colspan="1" rowspan="1">0.01200</td><td colspan="1" rowspan="1">3958</td><td colspan="1" rowspan="1">639</td></tr><tr><td colspan="1" rowspan="1">0.01078①</td><td colspan="1" rowspan="1">20000</td><td colspan="1" rowspan="1">812</td><td colspan="1" rowspan="1">0.01100</td><td colspan="1" rowspan="1">6658</td><td colspan="1" rowspan="1">642</td></tr><tr><td colspan="1" rowspan="1">0.01000</td><td colspan="1" rowspan="1">25016</td><td colspan="1" rowspan="1">782</td><td colspan="1" rowspan="1">0.01000</td><td colspan="1" rowspan="1">7952</td><td colspan="1" rowspan="1">638</td></tr><tr><td colspan="1" rowspan="1">0.00900</td><td colspan="1" rowspan="1">23204</td><td colspan="1" rowspan="1">738</td><td colspan="1" rowspan="1">0.01492①</td><td colspan="1" rowspan="1">10000</td><td colspan="1" rowspan="1">721</td></tr><tr><td colspan="1" rowspan="1">0.00881①</td><td colspan="1" rowspan="1">100000</td><td colspan="1" rowspan="1">722</td><td colspan="1" rowspan="1">0.00902</td><td colspan="1" rowspan="1">13646</td><td colspan="1" rowspan="1">653</td></tr><tr><td colspan="1" rowspan="1">0.00832①</td><td colspan="1" rowspan="1">200000</td><td colspan="1" rowspan="1">687</td><td colspan="1" rowspan="1">0.0122①</td><td colspan="1" rowspan="1">20000</td><td colspan="1" rowspan="1">689</td></tr><tr><td colspan="1" rowspan="1">总应变范围Δε</td><td colspan="1" rowspan="1">反向数2N</td><td colspan="1" rowspan="1">试验应力幅值σa/MPa</td><td colspan="1" rowspan="1">总应变范围Δe</td><td colspan="1" rowspan="1">反向数2N</td><td colspan="1" rowspan="1">试验应力幅值$/MPa$</td></tr><tr><td colspan="1" rowspan="1">0.00744①</td><td colspan="1" rowspan="1">100000</td><td colspan="1" rowspan="1">617</td><td colspan="1" rowspan="1">0.008</td><td colspan="1" rowspan="1">38542</td><td colspan="1" rowspan="1">591</td></tr><tr><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1">0.00907①</td><td colspan="1" rowspan="1">100000</td><td colspan="1" rowspan="1">623</td></tr><tr><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1">0.00835①</td><td colspan="1" rowspan="1">200000</td><td colspan="1" rowspan="1">598</td></tr><tr><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1">0.00734①</td><td colspan="1" rowspan="1">100000</td><td colspan="1" rowspan="1">550</td></tr><tr><td colspan="6" rowspan="1">①材料数据册中并未直接给出总应变数据，该数据是利用册中循环应力应变曲线和对称循环试验应力幅来确定的。</td></tr></table>

![](images/c5f0caf57a57e08a8087dd06ce49f4fe5bc19e5155d5b33a8aa1df5b4cc07871.jpg)  
图1-36 直接时效GH4169材料 $5 0 0 \mathrm { \% }$ 和 $6 5 0 \%$ 光滑试样的疲劳试验数据的拟合结果

![](images/15777846f3b94bedee2b379a558ab31118c9c3b3d715555167db58596ac2df30.jpg)  
图1-37 高强GH4169材料 $5 0 0 \mathrm { { ^ { q } C } }$ 和 $6 5 0 \mathrm { { ^ { \circ } C } }$ 光滑试样的疲劳试验数据的拟合结果

在获得总应变寿命程中的4个材料参数后，进步利缺试样的疲劳试验数据回归得到考虑应梯度的寿命模型所需的材料参数，表1-19和表1-20列出了不同应力比（ $R = - 1$ 、0.1和0.5）下两种材料的缺口试样（ $K _ { \mathrm { r } } = 3$ ）的试验数据，寿命区间为 $5 0 0 0 \sim 5 0 0 0 0 0$ 次循环，利用1.3节提出的寿命预测方法，首先计算出缺口试样的应力梯度影响因子 $Y$ ，进而利用试验数据拟合得到参数 $m$ 与反向数 $2 N _ { \mathrm { f } }$ 的关系如图1-40和图1-41所。最终得到直接时效GH4169和强GH4169在不同温度条件下寿命程中的材料疲劳参数见表1-21。

![](images/6a0d3f7ac53f48a862a30d37bcca07eadca06d5deaa7a44324428605d04ff4bf.jpg)  
图1-38直接时效GH4169材料 $5 0 0 \mathrm { { ^ \circ C } }$ 和 $6 5 0 \mathrm { { ^ { \circ } C } }$ 光滑试样的疲劳试验数据与寿命预测结果对

![](images/1d1810e0c74b8543788a970fc9fdfc5d0112702291f1d32f90a21ec6bd23bdd5.jpg)  
图1-39 高强GH4169材料 $5 0 0 \%$ 和 $6 5 0 \mathrm { { ‰} }$ 光滑试样的疲劳试验数据与寿命预测结果对

表1-19直接时效GH4169材料 ${ 5 0 0 } \mathrm { \textbar { C } }$ 和 $\bf 6 5 0 \mathrm { ‰}$ 下缺口试样的疲劳试验数据 $\vert K _ { \mathrm { t } } = 3$ ))  

<table><tr><td rowspan=2 colspan=1>温度</td><td rowspan=2 colspan=1>应力比R</td><td rowspan=1 colspan=5>0max</td></tr><tr><td rowspan=1 colspan=1>$ _=5×10{3$</td><td rowspan=1 colspan=1>$ =104</td><td rowspan=1 colspan=1>$ =5x10+$</td><td rowspan=1 colspan=1>$ =105$</td><td rowspan=1 colspan=1>$ _ =5x10{$</td></tr><tr><td rowspan=3 colspan=1>500℃</td><td rowspan=1 colspan=1>0.5</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>1152</td><td rowspan=1 colspan=1>841</td><td rowspan=1 colspan=1>755</td><td rowspan=1 colspan=1>626</td></tr><tr><td rowspan=1 colspan=1>0.1</td><td rowspan=1 colspan=1>888</td><td rowspan=1 colspan=1>693</td><td rowspan=1 colspan=1>481</td><td rowspan=1 colspan=1>442</td><td rowspan=1 colspan=1>399</td></tr><tr><td rowspan=1 colspan=1>-1</td><td rowspan=1 colspan=1>461</td><td rowspan=1 colspan=1>395</td><td rowspan=1 colspan=1>295</td><td rowspan=1 colspan=1>267</td><td rowspan=1 colspan=1>226</td></tr><tr><td rowspan=3 colspan=1>650℃</td><td rowspan=1 colspan=1>0.5</td><td rowspan=1 colspan=1>1142</td><td rowspan=1 colspan=1>1049</td><td rowspan=1 colspan=1>870</td><td rowspan=1 colspan=1>806</td><td rowspan=1 colspan=1>682</td></tr><tr><td rowspan=1 colspan=1>0.1</td><td rowspan=1 colspan=1>738</td><td rowspan=1 colspan=1>678</td><td rowspan=1 colspan=1>562</td><td rowspan=1 colspan=1>520</td><td rowspan=1 colspan=1>441</td></tr><tr><td rowspan=1 colspan=1>-1</td><td rowspan=1 colspan=1>407</td><td rowspan=1 colspan=1>374</td><td rowspan=1 colspan=1>310</td><td rowspan=1 colspan=1>287</td><td rowspan=1 colspan=1>243</td></tr></table>

表1-20高强4169材料在 $5 0 0 \mathrm { ‰}$ 和 $6 5 0 \mathrm { \% }$ 下缺口试样的疲劳试验数据（ $K _ { \mathrm { t } } = 3$ ))  

<table><tr><td rowspan=2 colspan=1>温度</td><td rowspan=2 colspan=1>应力比R</td><td rowspan=1 colspan=5>Omax</td></tr><tr><td rowspan=1 colspan=1>$ =5x103$</td><td rowspan=1 colspan=1>$ =104$</td><td rowspan=1 colspan=1>$ =5×104$</td><td rowspan=1 colspan=1>$ =105$</td><td rowspan=1 colspan=1>$N₁=5x105$</td></tr><tr><td rowspan=3 colspan=1>500℃</td><td rowspan=1 colspan=1>0.5</td><td rowspan=1 colspan=1>1130</td><td rowspan=1 colspan=1>1018</td><td rowspan=1 colspan=1>808</td><td rowspan=1 colspan=1>735</td><td rowspan=1 colspan=1>600</td></tr><tr><td rowspan=1 colspan=1>0.1</td><td rowspan=1 colspan=1>730</td><td rowspan=1 colspan=1>658</td><td rowspan=1 colspan=1>522</td><td rowspan=1 colspan=1>475</td><td rowspan=1 colspan=1>388</td></tr><tr><td rowspan=1 colspan=1>-1</td><td rowspan=1 colspan=1>404</td><td rowspan=1 colspan=1>364</td><td rowspan=1 colspan=1>289</td><td rowspan=1 colspan=1>263</td><td rowspan=1 colspan=1>214</td></tr><tr><td rowspan=3 colspan=1>650℃</td><td rowspan=1 colspan=1>0.5</td><td rowspan=1 colspan=1>1020</td><td rowspan=1 colspan=1>958</td><td rowspan=1 colspan=1>839</td><td rowspan=1 colspan=1>796</td><td rowspan=1 colspan=1>714</td></tr><tr><td rowspan=1 colspan=1>0.1</td><td rowspan=1 colspan=1>669</td><td rowspan=1 colspan=1>632</td><td rowspan=1 colspan=1>556</td><td rowspan=1 colspan=1>527</td><td rowspan=1 colspan=1>465</td></tr><tr><td rowspan=1 colspan=1>&#x27;-1</td><td rowspan=1 colspan=1>372</td><td rowspan=1 colspan=1>330</td><td rowspan=1 colspan=1>264</td><td rowspan=1 colspan=1>245</td><td rowspan=1 colspan=1>216</td></tr></table>

表1-21 不同温度下GH4169合金材料的疲劳参数  

<table><tr><td rowspan=2 colspan=1>参数</td><td rowspan=1 colspan=2>直接时效GH4169</td><td rowspan=1 colspan=2>高强GH4169</td></tr><tr><td rowspan=1 colspan=1>500℃</td><td rowspan=1 colspan=1>650℃</td><td rowspan=1 colspan=1>500℃</td><td rowspan=1 colspan=1>650℃</td></tr><tr><td rowspan=1 colspan=1>E/MPa</td><td rowspan=1 colspan=1>167500</td><td rowspan=1 colspan=1>150500</td><td rowspan=1 colspan=1>166000</td><td rowspan=1 colspan=1>155000</td></tr><tr><td rowspan=1 colspan=1>K&#x27;/MPa</td><td rowspan=1 colspan=1>1749</td><td rowspan=1 colspan=1>1412</td><td rowspan=1 colspan=1>1224</td><td rowspan=1 colspan=1>1195</td></tr><tr><td rowspan=1 colspan=1>n&#x27;</td><td rowspan=1 colspan=1>0.103</td><td rowspan=1 colspan=1>0.096</td><td rowspan=1 colspan=1>0.054</td><td rowspan=1 colspan=1>0.086</td></tr><tr><td rowspan=1 colspan=1>σ/MPa$</td><td rowspan=1 colspan=1>1901.81</td><td rowspan=1 colspan=1>1956.71</td><td rowspan=1 colspan=1>1761.57</td><td rowspan=1 colspan=1>1744.45</td></tr><tr><td rowspan=1 colspan=1>8}$</td><td rowspan=1 colspan=1>0.2857</td><td rowspan=1 colspan=1>0.3025</td><td rowspan=1 colspan=1>0.2749</td><td rowspan=1 colspan=1>0.3072</td></tr><tr><td rowspan=1 colspan=1>b</td><td rowspan=1 colspan=1>-0.0837</td><td rowspan=1 colspan=1>-0.09144</td><td rowspan=1 colspan=1>-0.08126</td><td rowspan=1 colspan=1>-0.0867</td></tr><tr><td rowspan=1 colspan=1>c</td><td rowspan=1 colspan=1>-0.5923</td><td rowspan=1 colspan=1>-0.80272</td><td rowspan=1 colspan=1>-0.59585</td><td rowspan=1 colspan=1>-0.6861</td></tr><tr><td rowspan=1 colspan=1>γ</td><td rowspan=1 colspan=1>0.6265</td><td rowspan=1 colspan=1>0.589</td><td rowspan=1 colspan=1>0.5967</td><td rowspan=1 colspan=1>0.7598</td></tr><tr><td rowspan=1 colspan=1>A</td><td rowspan=1 colspan=1>25.4935</td><td rowspan=1 colspan=1>3.827</td><td rowspan=1 colspan=1>1.6469</td><td rowspan=1 colspan=1>1.4854</td></tr><tr><td rowspan=1 colspan=1>B</td><td rowspan=1 colspan=1>-0.3591</td><td rowspan=1 colspan=1>-0.127</td><td rowspan=1 colspan=1>-0.1386</td><td rowspan=1 colspan=1>-0.0695</td></tr></table>

![](images/8cb7c94966af9e02916ba248be048c359172739f96aa71da46b0de7beb5adfc9.jpg)  
图1-40 应梯度影响指数 $m$ 与 $2 N _ { \mathrm { f } }$ 的关系（直接时效GH4169)

![](images/640e8c99b3d5fa0c9d44a95cac84cc5e184dbc99e165a6a45843ddf51c32d063.jpg)  
图1-41 应梯度影响指数 $m$ 与 $2 N _ { r }$ 的关系（强GH4169)

# 1.4.3.2 轮盘结构疲劳寿命预测分析

涡轮盘的寿命考核部位主要包括3处：盘缘过渡圆处（位置4）、盘（位置9）以及榫槽螺栓孔边（位置15）。封严盘的寿命考核部位主要包括两处：盘（位置14）和螺栓孔边（位置16）。如图1-33所。采所发展的基于Walker平均应修正的寿命模型进寿命预测，封严盘及涡轮盘关键部位的寿命预测结果见表1-22。

表1-22涡轮盘/封严盘危险部位的寿命预测结果  

<table><tr><td rowspan=1 colspan=1>部位</td><td rowspan=1 colspan=1>σ/MPa</td><td rowspan=1 colspan=1>Y</td><td rowspan=1 colspan=1>∆8/%</td><td rowspan=1 colspan=1>$R^$</td><td rowspan=1 colspan=1>Ni</td></tr><tr><td rowspan=1 colspan=1>4</td><td rowspan=1 colspan=1>1147.6（径向）</td><td rowspan=1 colspan=1>1.37</td><td rowspan=1 colspan=1>0.613</td><td rowspan=1 colspan=1>-0.137</td><td rowspan=1 colspan=1>521486</td></tr><tr><td rowspan=1 colspan=1>9</td><td rowspan=1 colspan=1>955.77（周向）</td><td rowspan=1 colspan=1>1.16</td><td rowspan=1 colspan=1>0.592</td><td rowspan=1 colspan=1>-0.118</td><td rowspan=1 colspan=1>516287</td></tr><tr><td rowspan=1 colspan=1>14</td><td rowspan=1 colspan=1>991.14（周向）</td><td rowspan=1 colspan=1>1.25</td><td rowspan=1 colspan=1>0.594</td><td rowspan=1 colspan=1>-0.142</td><td rowspan=1 colspan=1>422078</td></tr><tr><td rowspan=1 colspan=1>15</td><td rowspan=1 colspan=1>1230.2（径向）</td><td rowspan=1 colspan=1>1.29</td><td rowspan=1 colspan=1>0.774</td><td rowspan=1 colspan=1>-0.349</td><td rowspan=1 colspan=1>331638</td></tr><tr><td rowspan=1 colspan=1>16</td><td rowspan=1 colspan=1>1002.6（径向）</td><td rowspan=1 colspan=1>1.34</td><td rowspan=1 colspan=1>0.625</td><td rowspan=1 colspan=1>-0.309</td><td rowspan=1 colspan=1>2330509</td></tr></table>

# 1.5小结

本章以航空发动机中结构件的疲劳寿命预测分析为研究的出发点，旨在建立适于航空发动机结构件疲劳寿命预测的流程及方法。主要研究工作及结论如下。

（1）分别采用通用斜率法、四点相关法、修正的通用斜率法和修正的四点相关法确定了3种合金（TC4钛合金、GH4169合金和GH901合）的材料疲劳参数，并将由其给出的疲劳曲线与试验结果进了对比。在此基础上，建了总应变寿命程中材料的疲劳强度系数 $\sigma _ { \mathrm { { f } } \setminus } ^ { \prime }$ 疲劳延性系数 $ { \varepsilon } _ { f } ^ { \prime }$ 与材料单调拉伸的强度极限 $\sigma _ { \mathrm { ~ b ~ } }$ 、断面收缩率 $\psi$ 的关系，进发展了种确定总应变寿命程参数的新法，并通过3种合材料光滑试样的对称循环疲劳的试验数据对该方法进了验证。表明在较大的寿命范围内，采用所发展的总应变寿命方程进行寿命预测，其分散带基本在两倍以内，预测结果较为准确，从而为本所发展的总应变寿命程参数确定方法的实际应用奠定了程基础，具有重要的实用价值。

（2）分析了影响缺口结构件疲劳寿命的主要因素，通过采用Neuber法和修正Neuber法确定缺口试样的局部应力/应变，基于Walker寿命方程通过引入应力梯度影响因和尺寸效应影响因发展了种可以考虑平均应、应梯度和尺寸效应综合影响的新的缺口疲劳寿命预测模型，并采用航空发动机常用的TC4钛合材料的缺口疲劳试验数据进了验证。结果表明，在一定的循环载荷作用下，缺口处局部会产塑性应变，使得外部施加的应（载荷）比已不能表征缺处局部应。与仅需要光滑试样应寿命曲线的传统寿命预测法相比，所发展的新的法因为综合考虑了不同因素的影响，还需要进材料光滑试样对称与对称循环疲劳试验，以及两种缺试样（不同应力集中系数）的疲劳试验。此外，该新方法只需进弹性分析得到应力集中局部区域的应、应变及其梯度，避免了程结构的应集中系数 $K _ { r }$ 和疲劳缺口系数 $K _ { t }$ 难以确定的问题，验证了利用现有材料数据册中的试验数据进工程结构件疲劳寿命预测的可行性和有效性。

（3）基于所发展的总应变寿命方程参数确定法和寿命预测模型建了较为完整的涡轮盘等结构件的疲劳寿命评估流程及方法，并以个涡轮转子模型的计算分析为例说明了其实施步骤。计算结果表明：所建的结构件（如涡轮盘）疲劳寿命评估流程及方法能够充分有效地利用材料数据手册中给出的试验数据，得到一组物理意义明确的寿命模型参数，所发展的基于Walker寿命程的改进模型可考虑平均应、应梯度以及尺寸效应等的影响，实现了涡轮盘等结构件的疲劳寿命预测设计。

# 参考文献

[1] 王延荣，李宏新，袁善虎，等.考虑应梯度的缺口疲劳寿命预测法[J.航 空动力学报，2013，28（6）：1208-1214.   
[2宋兆泓．航空燃涡轮发动机强度设计M]．北京：北京航空学院出版社，1988.   
[3] Morow J D. Cyclic plastic strain energy and fatigue of metals [S]. In Internal Friction, Damping, and Cyclic Plasticity, ASTM, 1965: 45–86.   
[4] Smith K N, Watson P, Topper T H. A stress – strain function for the fatigue of metals [J], Journal of Materials, 1970, 5 (4): 767–778.   
[5] Walker K. The effect of stress ratio during crack propagation and fatigue for 2024–T3 and 7075–T6 aluminum [S]. American Society for Testing and Materials, 1970, 462: $1 - 1 4$ .   
[6] Susmel L, Taylor D. An elasto - plastic reformulation of the theory of critical distances to estimate lifetime of notched components failing in the low/medium- cycle fatigue regime [J]. Journal of Engineering Materials and Technology, 2010, 132 (2): 021002, 1 –8.   
[7] Shang D G, Wang D K, Li M, et al. Local stress – strain field intensity approach to fatigue life prediction under random cyclic loading [J]. International Journal of Fatigue, 2001,23:903–910.   
[8] Li J, Zhang Z P, Sun Q, et al. A new multiaxial fatigue damage model for various metallic materials under the combination of tension and torsion loadings [J]. International Journal of Fatigue, 2009, 31: 776–781.   
[9] 王延荣，李宏新，袁善虎，等.确定总应变寿命程参数的种新法[J].航 空动力学报，2014，29（4）：881-886.   
[10] Manson S. Fatigue: a complex subject - some simple approximate [J]. Experiment Mechanics, 1965; 5(4): 193-226.   
[11] Muralidharan U, Manson S. A modified universal slopes equation for estimation of fatigue characteristics of metals [J]. Journal of Engineering Materials and Technology, 1988,110:55-58.   
[12] Ong J H. An improved technique for the prediction of axial fatigue life from tensile data [J]. International Journal of Fatigue, 1993, 15: 213–219.   
[13] Draper J. Morden metal fatigue anaysis [M]. Sheffield, UK: EMAS Publishing Company, 1999.

北京：航空工业出版社，2010.

[15]中国航空材料册编辑委员会．中国航空材料册[M．北京：中国标准出版 社，1988.   
[16] ASM Metals Handbook. Fatigue and Fracture, vol. 19. [M]. 2nd printing. ASM International, 1997.   
[17] Neuber H. Theory of notch stresses: principles for exact calculation of strength with reference to structural form and material [M]. 2nd ed. Berlin: Springer Verlag, 1958: 292.   
[18] Waisman J L. Metal Fatigue [M]. New York: McGraw Hill, 1959.   
[19]机械程册编辑委员会．机械程册[M．北京：机械业出版社，1997.   
[20] Morw J D. Fatigue design handbook section 3.2 [M]. SAE Advances in Engineering, Society for Automotive Engineers, 1968, 4: 21 –29.   
[21] Dowling N E. Mean Stress efects in stress – life and strain – life fatigue [R]. Society of Automotive Engineers, Inc., Technical Paper F2004/51, 2004.   
[22] Taylor D, Bologna P, Knani K B. Prediction of fatigue location on a component using a critical distance method [J]. International Journal of Fatigue, 2000, 22(9): 735– 742.   
[23] Adib – Ramezani H, Jeong J. Advanced volumetric method for fatigue life prediction using stress gradient efects at notch roots [J]. Computational Materials Science, 2007,39：694-663.   
[24] Yao Weixing, Xia Kaiquan, Gu Yi, On the fatigue notch factor, $K _ { f }$ [J]，International Journal of Fatigue, 1995, 17 (4): 245–251.

# 第2章 高温结构蠕变设计分析方法

# 2.1引言

蠕变变形是温下作的结构件必须面临的重要问题。蠕变与温度密切相关，一般当温度达到构件材料熔点温度 $T _ { m }$ 的 $30 \%$ 以上时，蠕变变形将较为明显，故此工程设计中当绝对温度 $T \geqslant 0 . 5 T _ { m }$ 时，必须考虑蠕变变形的影响[1,2]。航空发动机中热端构件长期工作在温环境下，将发蠕变变形，导致结构件因塑性变形过大而发蠕变应断裂，特别是随着性能发动机涡轮前温度的逐渐提，蠕变引起的故障更为突出。为此，航空发动机温结构件热强度设计中需要研究蠕变变形规律，以保证使用安全性。

工程设计中，蠕变变形数值模拟是蠕变研究的一项重要内容。航空发动机中工作在燃环境中的涡轮叶和涡轮盘受蠕变变形的影响较，涡轮盘采的材料多是各向同性材料，而涡轮叶采用的材料除了各向同性材料之外，还包括定向结晶和单晶等各向异性材料。众多学者[1.2\~7]对不同材料的叶模型进了蠕变变形的数值模拟和试验研究，发现由于材料在晶界处产生空洞、截面积减小、颈缩等原因，会导致试样在蠕变的第3阶段快速失效[8.9]，正因为此特点，实际程上更为关注蠕变发的前两个阶段。前期建的蠕变模型也多是描述这两个阶段的，如幂率蠕变模型描述的是稳态蠕变速率与应的关系，安德雷德（Andrade）提出的恒温恒载下的蠕变程仅能模拟蠕变的前两个阶段。 $\theta$ 投射法虽然可以模拟完整的蠕变变形，但它忽视了蠕变速率为常数的稳态蠕变阶段。些黏塑性本构模型[10\~12]虽然可以较好地描述循环载荷下的塑性变形，但必须引损伤参量修正模型才能描述蠕变的第3阶段。对于试样在试验载荷下的蠕变变形，这些模型法通常较准确，但因为计算较为复杂，难以在实际中于涡轮叶和盘等结构件的蠕变分析。这些蠕变模型尚不能较好地模拟完整的3个阶段的蠕变变形。

从相关材料数据册中可以发现，当前些常用工程材料的蠕变曲线的第1阶段并不明显，而第2阶段和第3阶段所占比例非常（如DZ125、DD6合等），利用常用的只能描述前两阶段的蠕变模型对这些曲线进拟合时误差较。同时，由于实际结构件的使寿命都限定在蠕变的第3阶段之前，所以当前程中所使的计算蠕变变形的法也只能计算蠕变的前两个阶段，却不能预测结构是否处于较为危险的第3阶段。当构件处于第3阶段时，会产较大蠕变变形甚至断裂，理想的蠕变模型既能准确地描述蠕变前两个阶段，又具备描述第3阶段蠕变变形的能力，以便判断结构件是否处于较为危险的加速蠕变阶段。此外，蠕变模型还要能够模拟任意温度和应下的蠕变变形，具有内插和外推的功能。

航空发动机中的涡轮盘和叶片在高温环境下高速转动，蠕变问题特别突出。轮盘和叶若产过大的蠕变变形将导致叶与机匣碰磨，影响发动机的安全，甚至发生灾难性故障。为此涡轮盘有严格的抗蠕变设计要求，在严苛的温度和应条件下，轮盘关键尺寸的变化不能超过规定的允许值。在翻修期内，允许更换变形过的零组件。温下作时，涡轮叶的变形限制包括：（1）叶型的恢复扭转不会引起叶冠的松动或者性能的恶化；（2）叶尖不能出现严重磨损；（3）不会使冷叶的冷却效果恶化等[1\~3]。

本章先提出了种可完整描述3个阶段蠕变变形的法，并采归化参数作为模型程的变量[13-15]；然后采所提出的基于归化参数的蠕变模型，在通有限元程序ANSYS环境下，通过编写usercreep程序实现了对实际构件的蠕变分析[14\~16]；并在已有的两种变载理论模型的基础上提出了种介于其间的法，将这3种模型在所发展的子程序中进行了程序实现，使所发展的归一化参数蠕变模型能够按照不同的变载理论模型对实际结构进有限元计算分析[14,15]；最后对涡轮盘和叶等实际温结构件的三维有限元模型进行了分析，利用所发展的一种能完整描述3个阶段蠕变变形的归一化参数蠕变模型[13,14]编写的usercreep程序进蠕变分析，重点考察了涡轮盘和涡轮叶危险点的蠕变为，并分析蠕变变形和危险点区域的应松弛效应及其规律。

# 2.2种基于归化参数的蠕变模型

本节提出了种可完整描述3个阶段蠕变变形的法，并采归一化参数作为模型程的变量[13\~15]。通过参数归化处理，将不同温度和不同应平下的蠕变规律置于同的时间轴下分析，容易找到定的规律，同时避免系数值相差过。最后利用直接时效GH4169G材料的蠕变试验曲线对所发展的蠕变模型进了验证。

# 2.2.1 基于归一化参数蠕变模型的构造

本所发展的基于归化参数的模型将蠕变应变表达为

$$
\varepsilon _ { \mathrm { c } } = \eta _ { 1 } \zeta ^ { \eta _ { 4 } } + \eta _ { 2 } \zeta + \eta _ { 3 } \zeta ^ { \eta _ { 5 } }
$$

式中, $\zeta = t / t _ { \mathrm { c } }$ 为无量纲时间， $\zeta \in \left[ 0 , \ 1 \right]$ , $t _ { \mathrm { c } }$ 为给定温度和应力下的持久寿命；$\eta _ { i }$ （ $i = 1$ ，2，3，4，5）为无量纲温度 $T / T _ { m }$ 与无量纲应力 $\sigma / \sigma _ { 0 . 2 }$ 的函数， $T _ { \mathrm { m } }$ 为熔点温度， $\sigma _ { 0 . 2 }$ 为屈服应力，且 $0 < \eta _ { 4 } < 1$ , $\eta _ { 5 } > 1$ ；蠕变变形试验若试断裂，则 $t _ { \mathrm { c } }$ 为蠕变曲线断裂时对应的时间，否则可根据持久试验得到该温度和应下的持久寿命，不同温度和应下的持久寿命可通过持久程求得[13\~15] 0

从材料数据册中所给出的持久寿命数据可以看出，对于大部分各向同性材料来说，持久程使用拉森-米勒（Larson-Miller，L-M）方程，如GH4169、K417G等，对于部分各向异性材料持久程使曼森-萨科普（Manson-Succop，M-S）程，如DD6等。

所发展的模型是以归一化时间为自变量，用3项幂函数来描述蠕变应变。在区间[0，1]上幂函数 $y = x ^ { m }$ 当指数 $m$ 取不同值时的曲线如图2-1所示。由图中可知，在区间[0，1]上，当 $m < 1$ 时， $y = x ^ { m }$ 的曲线和蠕变第1阶段相似；当 $m = 1$ 时，即$y = x$ 可表示蠕变第2阶段；当 $m > 1$ 时， $y = x ^ { m }$ 的曲线与蠕变第3阶段相似。因此，式（2-1）在归化时间区间[0，1上具有完整模拟蠕变各阶段的能。

![](images/025d7c1707ab700f0f3112d1f8b3e27fb60f5a94ec0a2f0d5ba124d92009d9ca.jpg)  
图2-1 当 $m$ 取不同值时 $y = x ^ { m }$ 在区间[0，1]上的曲线

当蠕变曲线的时间坐标对持久寿命 $t _ { \mathrm { c } }$ 归一化之后，模型中的参数 $\eta _ { 1 }$ , $\eta _ { 2 }$ , $\eta _ { 3 }$ 有明确的物理意义，如图2-2所示，纵坐标 $\varepsilon _ { \mathrm { c } }$ 为蠕变应变（不含瞬时应变），具体意义如下。

![](images/ee275a9e18262ed3e7d1659d518adcae2502c598ea330a073487c73a6c2cd56e.jpg)  
图2-2 蠕变模型中各系数的物理意义

(1）当 $\zeta = 1$ 时， $\boldsymbol { \varepsilon } _ { \mathrm { r } } = \boldsymbol { \eta } _ { 1 } + \boldsymbol { \eta } _ { 2 } + \boldsymbol { \eta } _ { 3 }$ , $\varepsilon _ { \mathrm { { r } } }$ 为到持久寿命时断裂的蠕变应变。

（2）式（2-1）中的3项分别描述蠕变的3个阶段，参数 $\eta _ { 1 }$ , $\eta _ { 2 }$ , $\eta _ { 3 }$ 分别为蠕变3个阶段的蠕变量，其中 $\eta _ { 2 }$ 也是第2阶段的直线斜率，表时间归化后的稳态蠕变应变率。

(3） $\eta _ { 1 }$ 等于第2阶段的直线在应变轴（ $\zeta = 0$ ）上的截距， $\eta _ { 3 }$ 等于第2阶段直线和$\zeta = 1$ 的交点与持久寿命断裂点之间的距离。

（4） $\eta _ { 4 }$ , $\eta _ { 5 }$ 分别描述蠕变第1阶段和蠕变第3阶段曲线的曲率变化，反映各阶段蠕变应变变化的快慢。

# 2.2.2 基于归一化参数蠕变模型的验证

本节应所提出的归化参数模型，对等温锻造后直接时效GH4169G合的蠕变试验曲线进了拟合，以验证该模型的可性。图2-3示出了GH4169G合的蠕变试验曲线[16]。在 $6 8 0 \mathrm { ‰}$ 下施加不同应的蠕变寿命分别为： $7 0 0 \mathrm { M P a }$ 时为 $5 6 \mathrm { h }$ , $6 5 0 \mathrm { { M P a } }$ 时为 $1 2 3 \mathrm { h }$ ,$6 3 0 \mathrm { M P a }$ 时为 $1 7 8 \mathrm { h }$ 。在不同温度下施加 $6 5 0 \mathrm { M P a }$ 应力时的持久寿命分别为： $6 6 0 \%$ 时为$2 9 5 \mathrm { h }$ , $6 7 0 \%$ 时为 $1 7 8 \mathrm { h }$ $6 8 0 \%$ 时为 $1 2 3 \mathrm { h }$ 。该合熔点为 $1 2 6 0 \sim 1 3 2 0 ^ { \circ } \mathrm { C }$ ，本文计算中取$1 2 9 0 \mathrm { { \mathrm C } }$ 。在 $6 5 0 \mathrm { { ^ \circ C } }$ 、 $6 8 0 \mathrm { ‰}$ 和 $7 0 0 \%$ 下该材料的屈服应力分别为 $1 0 7 0 \mathrm { M P a }$ (id:) $1 0 2 0 \mathrm { M P a }$ $9 5 0 \mathrm { { M P a } }$ ，可插值得到 $6 6 0 \mathrm { { ^ { \circ C } } }$ 和 $6 7 0 \mathrm { ‰}$ 下的屈服应分别为1053MPa和 $1 0 3 7 \mathrm { M P a }$

![](images/fe7572fa85bfd58abc7c9244af552de70328cc219d8ab3d03507ff4b5879c143.jpg)  
图2-3 直接时效GH4169G的蠕变曲线[16]

对上述的试验曲线应归化参数的蠕变模型进拟合，3个参数 $\eta _ { 1 }$ , $\eta _ { 2 }$ , $\eta _ { 3 }$ 按其物理意义取值，然后对指数 $\eta _ { 4 }$ 和 $\eta _ { 5 }$ 的值进调整。表2-1列出了单独拟合得到的5个参数的结果。

表2-1不同温度和应力载荷下的蠕变模型参数  

<table><tr><td rowspan=1 colspan=1>温度/℃</td><td rowspan=1 colspan=1>应力/MPa</td><td rowspan=1 colspan=1>71%</td><td rowspan=1 colspan=1>n2/%</td><td rowspan=1 colspan=1>13/%</td><td rowspan=1 colspan=1>74</td><td rowspan=1 colspan=1>15</td></tr><tr><td rowspan=1 colspan=1>680</td><td rowspan=1 colspan=1>630</td><td rowspan=1 colspan=1>0.66</td><td rowspan=1 colspan=1>1.66</td><td rowspan=1 colspan=1>5.97</td><td rowspan=1 colspan=1>0.04</td><td rowspan=1 colspan=1>11.00</td></tr><tr><td rowspan=1 colspan=1>680</td><td rowspan=1 colspan=1>650</td><td rowspan=1 colspan=1>0.93</td><td rowspan=1 colspan=1>1.79</td><td rowspan=1 colspan=1>4.45</td><td rowspan=1 colspan=1>0.05</td><td rowspan=1 colspan=1>14.34</td></tr><tr><td rowspan=1 colspan=1>680</td><td rowspan=1 colspan=1>700</td><td rowspan=1 colspan=1>1.23</td><td rowspan=1 colspan=1>1.50</td><td rowspan=1 colspan=1>4.83</td><td rowspan=1 colspan=1>0.07</td><td rowspan=1 colspan=1>8.62</td></tr><tr><td rowspan=1 colspan=1>660</td><td rowspan=1 colspan=1>650</td><td rowspan=1 colspan=1>0.68</td><td rowspan=1 colspan=1>1.82</td><td rowspan=1 colspan=1>10.04</td><td rowspan=1 colspan=1>0.03</td><td rowspan=1 colspan=1>9.00</td></tr><tr><td rowspan=1 colspan=1>670</td><td rowspan=1 colspan=1>650</td><td rowspan=1 colspan=1>0.80</td><td rowspan=1 colspan=1>1.55</td><td rowspan=1 colspan=1>5.95</td><td rowspan=1 colspan=1>0.05</td><td rowspan=1 colspan=1>8.50</td></tr><tr><td rowspan=1 colspan=1>680</td><td rowspan=1 colspan=1>650</td><td rowspan=1 colspan=1>0.90</td><td rowspan=1 colspan=1>1.54</td><td rowspan=1 colspan=1>4.73</td><td rowspan=1 colspan=1>0.06</td><td rowspan=1 colspan=1>13.42</td></tr></table>

模型中的5个参数与归化温度 $T / T _ { \mathrm { m } }$ 和归一化应力 $\sigma / \sigma _ { 0 . 2 }$ 有如下关系

$$
\eta _ { i } = a _ { i } + b _ { i } { \frac { T } { T _ { \mathrm { m } } } } + c _ { i } { \frac { \sigma } { \sigma _ { 0 , 2 } } } + d _ { i } { \frac { T } { T _ { \mathrm { m } } } } { \frac { \sigma } { \sigma _ { 0 , 2 } } }
$$

式中： $a _ { i }$ , $b _ { i }$ , $c _ { i }$ , $d _ { i }$ $i = 1$ ，2，3，4，5）——常数，可通过不同温度和应力下 $\eta _ { i }$ 拟合得到；

$\sigma _ { 0 , 2 }$ -屈服应力；

$T _ { m }$ (id:) 熔点温度。

式（2-2）认为蠕变3个阶段所对应的蠕变应变参数值 $\eta _ { i }$ （ $i = 1$ ，2，3）分别随归化温度 $T / T _ { \mathrm { m } }$ 和归一化应力 $\sigma / \sigma _ { 0 . 2 }$ 呈线性变化[13,14]。采归化参数有两个好处：是表达式中的系数 $a _ { i }$ , $b _ { i }$ , $c _ { i }$ , $d _ { i }$ （ $i = 1$ ，2，3，4，5）为无量纲的；二是系数 $a _ { i }$ , $b _ { i }$ ,(id:) $c _ { i }$ , $d _ { i }$ （ $i = 1$ ，2，3，4，5）可统一用表2-1中的数据由最小二乘法拟合得到。 $6 8 0 \mathrm { ‰}$ 、$6 5 0 \mathrm { M P a }$ 下的试验曲线在两幅图中均出现，可能由于原献中的绘图误差及本在取点过程中产的误差，单独对两条曲线拟合时，得到的这5个参数值有定的差别，在此忽略其差别，直接用最乘法拟合，拟合的系数值见表2-2。将系数值代式（2-2），计算任意温度和应力下式（2-1）中各蠕变参数值，从而得到模拟的蠕变曲线。利用计算得到的蠕变曲线与试验数据对比，验证了该模型对各条试验曲线的模拟结果均较好，如图2-4所示。

表2-2 蠕变模型中各参数的系数  

<table><tr><td rowspan=2 colspan=1>参数</td><td rowspan=1 colspan=4>系数</td></tr><tr><td rowspan=1 colspan=1>ai</td><td rowspan=1 colspan=1>bi</td><td rowspan=1 colspan=1>i</td><td rowspan=1 colspan=1>di</td></tr><tr><td rowspan=1 colspan=1>71</td><td rowspan=1 colspan=1>-144.3</td><td rowspan=1 colspan=1>229.9</td><td rowspan=1 colspan=1>231.7</td><td rowspan=1 colspan=1>-367.3</td></tr><tr><td rowspan=1 colspan=1>72</td><td rowspan=1 colspan=1>1118.1</td><td rowspan=1 colspan=1>-1828.1</td><td rowspan=1 colspan=1>-1798.9</td><td rowspan=1 colspan=1>2945.8</td></tr><tr><td rowspan=1 colspan=1>73</td><td rowspan=1 colspan=1>1349.3</td><td rowspan=1 colspan=1>-2195.6</td><td rowspan=1 colspan=1>-1838.1</td><td rowspan=1 colspan=1>2999.2</td></tr><tr><td rowspan=1 colspan=1>74</td><td rowspan=1 colspan=1>-56.2</td><td rowspan=1 colspan=1>91.8</td><td rowspan=1 colspan=1>90.1</td><td rowspan=1 colspan=1>-147.1</td></tr><tr><td rowspan=1 colspan=1>75</td><td rowspan=1 colspan=1>189.6</td><td rowspan=1 colspan=1>-236.4</td><td rowspan=1 colspan=1>-662.2</td><td rowspan=1 colspan=1>1000.0</td></tr></table>

![](images/1f803cb81f3d19244d531c131dde1078a4b7ade0e9e9d78f431713a96c4257be.jpg)  
图2-4 不同条件下的蠕变试验曲线和拟合曲线的对比

# 2.2.3 基于归一化参数蠕变模型的改进

由图2-4中可以发现，所发展的归化参数蠕变模型的第项 $\eta _ { 1 } \zeta ^ { \eta _ { 4 } }$ 描述蠕变第1阶段的效果还不够理想，主要是由于幂函数本特点，当参数 $\eta _ { 4 } < 1$ 时，幂函数的导数值在 $\zeta = 0$ 处为穷，也就是幂函数在 $\zeta = 0$ 附近不能准确地描述蠕变应变率。为此对其进改进以期更好地描述蠕变应变

$$
\begin{array} { r l } { \varepsilon _ { \mathrm { c } } = \eta _ { 1 } } & { { } \mathrm { ( } 1 - \mathrm { e } ^ { - \eta _ { 4 } \zeta } \mathrm { ) } + \eta _ { 2 } \zeta + \eta _ { 3 } \zeta ^ { \eta _ { 5 } } } \end{array}
$$

式中，仅将式（2-2）中的第1项幂函数改进为指数形式， $\eta _ { 1 }$ , $\eta _ { 2 }$ , $\eta _ { 3 }$ 和 $\eta _ { 5 }$ 所代表的意义不变，蠕变应变第1阶段的为仍参数 $\eta _ { 4 }$ 来描述，但含义有所不同。当 $\eta _ { 4 }$ 的值稍大时， $\mathrm { ~ e ~ } ^ { - \eta _ { 4 } }$ 接近于0，在 $0 \leqslant \zeta \leqslant 1$ 的范围内，第项的导数递减，仍能模拟蠕变第1阶段，同时各参数的物理意义相同。

仍利献[16中GH4169G试验数据验证改进模型的可性。由于改进模型只改进了第一项，则参数 $\eta _ { 1 }$ , $\eta _ { 2 }$ , $\eta _ { 3 }$ 和 $\eta _ { 5 }$ 的意义不变，数值也不变，对每条曲线单独拟合所得到的 $\eta _ { 4 }$ 值见表2-3，由改进模型拟合得到的蠕变曲线见图2-5。由图中可以看出，改进模型能更好地描述蠕变试验曲线的第1阶段。

表2-3 改进模型中参数 $\pmb { \eta } _ { 4 }$ 的拟合结果  

<table><tr><td rowspan=1 colspan=1>温度/℃</td><td rowspan=1 colspan=1>应力/MPa</td><td rowspan=1 colspan=1>7.1%</td><td rowspan=1 colspan=1>$121%</td><td rowspan=1 colspan=1>n3/%</td><td rowspan=1 colspan=1>74</td><td rowspan=1 colspan=1>75</td></tr><tr><td rowspan=1 colspan=1>680</td><td rowspan=1 colspan=1>630</td><td rowspan=1 colspan=1>0.66</td><td rowspan=1 colspan=1>1.66</td><td rowspan=1 colspan=1>5.97</td><td rowspan=1 colspan=1>100.01</td><td rowspan=1 colspan=1>11.00</td></tr><tr><td rowspan=1 colspan=1>680</td><td rowspan=1 colspan=1>650</td><td rowspan=1 colspan=1>0.93</td><td rowspan=1 colspan=1>1.79</td><td rowspan=1 colspan=1>4.45</td><td rowspan=1 colspan=1>85.09</td><td rowspan=1 colspan=1>14.34</td></tr><tr><td rowspan=1 colspan=1>680</td><td rowspan=1 colspan=1>700</td><td rowspan=1 colspan=1>1.23</td><td rowspan=1 colspan=1>1.50</td><td rowspan=1 colspan=1>4.83</td><td rowspan=1 colspan=1>44.47</td><td rowspan=1 colspan=1>8.62</td></tr><tr><td rowspan=1 colspan=1>660</td><td rowspan=1 colspan=1>650</td><td rowspan=1 colspan=1>0.68</td><td rowspan=1 colspan=1>1.82</td><td rowspan=1 colspan=1>10.04</td><td rowspan=1 colspan=1>95.06</td><td rowspan=1 colspan=1>9.00</td></tr><tr><td rowspan=1 colspan=1>670</td><td rowspan=1 colspan=1>650</td><td rowspan=1 colspan=1>0.80</td><td rowspan=1 colspan=1>1.55</td><td rowspan=1 colspan=1>5.95</td><td rowspan=1 colspan=1>64.57</td><td rowspan=1 colspan=1>8.50</td></tr><tr><td rowspan=1 colspan=1>680</td><td rowspan=1 colspan=1>650</td><td rowspan=1 colspan=1>0.90</td><td rowspan=1 colspan=1>1.54</td><td rowspan=1 colspan=1>4.73</td><td rowspan=1 colspan=1>44.67</td><td rowspan=1 colspan=1>13.42</td></tr></table>

![](images/546ab28688883868d2e37909afd225cac6f2f54f52b4de34eda5224f9e498131.jpg)  
图2-5 用改进蠕变模型对每条试验曲线单独拟合的效果

参数归化后，温度和应的变化范围不，而模型中的5个参数（特别是 $\eta _ { 4 }$ )变化相对较，并依赖于温度和应力，对其取然对数，并认为具有如下形式

$$
\ln \eta _ { i } = a _ { i } + b _ { i } { \frac { T } { T _ { \mathrm { m } } } } + c _ { i } { \frac { \sigma } { \sigma _ { 0 , 2 } } } + d _ { i } { \frac { T } { T _ { \mathrm { m } } } } { \frac { \sigma } { \sigma _ { 0 , 2 } } }
$$

式中： $\eta _ { i }$ （ $i = 1$ ,2，3，4，5）代表5个参数， $a _ { i }$ , $b _ { i }$ , $c _ { i }$ , $d _ { i }$ 为5组待定的常系数。通过数据拟合，得到蠕变模型中各参数的系数值见表2–4。改进模型的模拟效果如图2–6所。

表2-4 改进模型中各参数的系数  

<table><tr><td rowspan=2 colspan=1>参数</td><td rowspan=1 colspan=4>系数</td></tr><tr><td rowspan=1 colspan=1>ai</td><td rowspan=1 colspan=1>bi</td><td rowspan=1 colspan=1>ci</td><td rowspan=1 colspan=1>di</td></tr><tr><td rowspan=1 colspan=1>71</td><td rowspan=1 colspan=1>-13.12</td><td rowspan=1 colspan=1>12.92</td><td rowspan=1 colspan=1>6.268</td><td rowspan=1 colspan=1>2.766</td></tr><tr><td rowspan=1 colspan=1>72</td><td rowspan=1 colspan=1>-3.567</td><td rowspan=1 colspan=1>7.774</td><td rowspan=1 colspan=1>14.78</td><td rowspan=1 colspan=1>-26.1</td></tr><tr><td rowspan=1 colspan=1>13</td><td rowspan=1 colspan=1>-23.55</td><td rowspan=1 colspan=1>43.85</td><td rowspan=1 colspan=1>46.03</td><td rowspan=1 colspan=1>-79.31</td></tr><tr><td rowspan=1 colspan=1>74</td><td rowspan=1 colspan=1>16.99</td><td rowspan=1 colspan=1>-21.70</td><td rowspan=1 colspan=1>-21.22</td><td rowspan=1 colspan=1>35.91</td></tr><tr><td rowspan=1 colspan=1>775</td><td rowspan=1 colspan=1>21.08</td><td rowspan=1 colspan=1>-30.44</td><td rowspan=1 colspan=1>-34.69</td><td rowspan=1 colspan=1>56.84</td></tr></table>

![](images/8ee21c66ee169d54153c81cf047e018496c75ca951e60e0832c3bfad5ab1a790.jpg)  
图2-6 改进模型的拟合效果

可见，改进模型的拟合曲线与试验数据符合性较好，前两个阶段近于重合，表明所发展的蠕变模型适于描述蠕变应变曲线。同时，通过式（2-3）得到任意温度和应力下的蠕变参数，具有内插和外推的能力，尽管缺乏试验数据，但仍可看出该模型在一定范围内有较好的适性，并可与有限元程序结合，于实际程结构的蠕变分析[13,14]。

# 2.2.4 各向异性材料的归化参数蠕变模型

在实际结构的分析中一般采用有限元法进行数值计算：将蠕变计算过程中的时间历程分为时间间隔 $\Delta t _ { 1 }$ , $\Delta t _ { 2 }$ ，…，根据当前状态计算得到每时间间隔 $\Delta t _ { i }$ 对应的蠕变应变增量，所有时间间隔的蠕变应变增量的累计即为整个时间的蠕变量[17]。每时间间

隔 $\Delta t _ { i }$ 对应的蠕变应变增量由蠕变应变的表达式得到，一般来说，蠕变应变是时间、应力和温度的函数

$$
\boldsymbol { \varepsilon } _ { \mathrm { { c } } } = \boldsymbol { f } \left( \begin{array} { l l } { t , \ \sigma , \ T } \end{array} \right)
$$

式中：——时间；T 温度；$\sigma$ 等效应力。

等效应力由应力的各个分量求得，若是各向同性材料，则 $\sigma$ 为冯·米塞斯（VonMises）等效应；若是正交各向异性材料，则 $\sigma$ 为希尔（Hill）等效应力。

对于各向同性材料，其各个方向的特性相同；而对于各向异性材料，各方向上的特性并不一样，例如，航空发动机中常用的定向结晶和单晶均为正交各向异性材料，具有三个互相垂直坐标轴的对称性。将适于各向同性材料的VonMises屈服准则推到适于正交各向异性材料的Hil屈服准则，Hill等效应表达式为[1\~3,20,21]

$$
\begin{array} { r l } { \tau _ { \mathrm { H i l } } = } & { { } \big [ ( F ( \sigma _ { \gamma } - \sigma _ { z } ) ^ { 2 } + G ( \sigma _ { z } - \sigma _ { x } ) ^ { 2 } + H ( \sigma _ { x } - \sigma _ { y } ) ^ { 2 } + 2 L \sigma _ { y z } ^ { 2 } + 2 M \sigma _ { z x } ^ { 2 } + 2 N \sigma _ { x y } ^ { 2 } ) \big ] ^ { \frac { 1 } { 2 } } } \end{array}
$$

式中， $F$ , $G$ , $H$ , $L$ , $M$ , $N$ 为材料参数，表达式为

$$
\begin{array} { r l } & { F - \frac { 1 } { 2 } \left( \frac { 1 } { R _ { y } ^ { 2 } } + \frac { 1 } { R _ { z } ^ { 2 } } - \frac { 1 } { R _ { x } ^ { 2 } } \right) } \\ & { G = \frac { 1 } { 2 } \left( \frac { 1 } { R _ { z } ^ { 2 } } + \frac { 1 } { R _ { x } ^ { 2 } } - \frac { 1 } { R _ { y } ^ { 2 } } \right) } \\ & { H = \frac { 1 } { 2 } \left( \frac { 1 } { R _ { x } ^ { 2 } } + \frac { 1 } { R _ { y } ^ { 2 } } - \frac { 1 } { R _ { x } ^ { 2 } } \right) } \\ & { L = \frac { 3 } { 2 } \left( \frac { 1 } { R _ { x } ^ { 2 } \alpha } \right) } \\ & { M = \frac { 3 } { 2 } \left( \frac { 1 } { R _ { y } ^ { 2 } \alpha } \right) } \\ & { N = \frac { 3 } { 2 } \left( \frac { 1 } { R _ { x } ^ { 2 } \alpha } \right) } \end{array}
$$

式中， $R _ { x } = \frac { \sigma _ { x } ^ { \mathrm { y } } } { \sigma ^ { \mathrm { y } } } , R _ { y } = \frac { \sigma _ { y } ^ { \mathrm { y } } } { \sigma ^ { \mathrm { y } } } , R _ { z } = \frac { \sigma _ { z } ^ { \mathrm { y } } } { \sigma ^ { \mathrm { y } } } , R _ { x y } = \sqrt { 3 } ~ \frac { \sigma _ { x y } ^ { \mathrm { y } } } { \sigma ^ { \mathrm { y } } } , R _ { y z } = \sqrt { 3 } ~ \frac { \sigma _ { y z } ^ { \mathrm { y } } } { \sigma ^ { \mathrm { y } } } , R _ { z x } = \sqrt { 3 } ~ \frac { \sigma _ { z x } ^ { \mathrm { y } } } { \sigma ^ { \mathrm { y } } } ;$ 分别表各个方向的屈服应力比， $\boldsymbol { \sigma } _ { x } ^ { \gamma }$ , $\boldsymbol { \sigma } _ { \gamma } ^ { \gamma }$ , $\boldsymbol { \sigma } _ { z } ^ { \ y }$ , $\boldsymbol { \sigma } _ { x y } ^ { y }$ , $\boldsymbol { \sigma } _ { y z } ^ { y }$ , $\sigma _ { z x } ^ { \mathrm { y } }$ 分别为各个向的屈服应，上标y表示屈服， $\sigma ^ { \gamma }$ 表示当Hill等效应力 $\sigma _ { \mathrm { H i l l } }$ 大于 $\sigma ^ { \gamma }$ 时产屈服。

根据流动法则可计算得到

$$
\begin{array} { r } { \begin{array} { l } { \mathrm { d } \varepsilon _ { x } = \mathrm { d } \lambda \left[ H \left( \sigma _ { x } - \sigma _ { y } \right) + G \left( \sigma _ { x } - \sigma _ { z } \right) \right] } \\ { \mathrm { d } \varepsilon _ { y } = \mathrm { d } \lambda \left[ F \left( \sigma _ { y } - \sigma _ { z } \right) + H \left( \sigma _ { y } - \sigma _ { x } \right) \right] } \\ { \mathrm { d } \varepsilon _ { z } = \mathrm { d } \lambda \left[ G \left( \sigma _ { z } - \sigma _ { x } \right) + F \left( \sigma _ { z } - \sigma _ { y } \right) \right] } \\ { \mathrm { d } \varepsilon _ { y z } = \mathrm { d } \lambda \left( 2 L \sigma _ { y z } \right) } \\ { \mathrm { d } \varepsilon _ { x } = \mathrm { d } \lambda \left( 2 M \sigma _ { x x } \right) } \\ { \mathrm { d } \varepsilon _ { x y } = \mathrm { d } \lambda \left( 2 N \sigma _ { x y } \right) } \end{array} } \end{array}
$$

式中： $\mathrm { d } \lambda = \frac { \mathrm { d } { \varepsilon _ { \mathrm { { c } } } } } { \sigma _ { \mathrm { { H i l l } } } }$

由式（2-8）即可通过单轴的蠕变变形表达式扩展到多轴应状态。

# 2.2.5 归一化参数蠕变模型中相应参数的确定法

所发展的蠕变模型需用到的材料数据有：（1）材料的熔点温度；（2）屈服应力随温度的变化；（3）持久寿命参数（L-M)；（4）材料的蠕变曲线。通过蠕变曲线拟合得到系数 $a _ { i }$ , $b _ { i }$ , $c _ { i }$ , $d _ { i }$ 的法有两种：（1）蠕变参数总体拟合法；（2）基于物理意义拟合方法。

2.2.5.1 蠕变参数的总体拟合方法

将归化时间、归化温度、归化应视为变量，蠕变应变视作因变量，式(2-3）和式(2-4）可写为 $\varepsilon _ { \mathrm { c } } = f \left( { \frac { t } { t _ { \mathrm { c } } } } , \ { \frac { T } { T _ { \mathrm { m } } } } , \ { \frac { \sigma } { \sigma _ { 0 . 2 } } } \right)$ 根据蠕变曲线取点得到的数据进最乘法拟合可得系数 $a _ { i }$ , $b _ { i }$ , $c _ { i }$ , $d _ { i }$ ( $i = 1$ ,2,3，4,5)。

现对GH907材料进拟合，GH907的蠕变曲线取参考献[21]，如图2-7所。

![](images/5ec0b04a63560452a2f02707dbb2a8d640e9b1300f29bb4c4195a84a98dd3fd1.jpg)  
图2-7 GH907的蠕变曲线[21]

除了蠕变曲线还需用到的材料数据有：（1）持久寿命参数（L-M），数据均取自参考献[21；（2）屈服应力随温度的变化；（3）材料的熔点。

根据持久寿命程（L-M程）可计算得到持久寿命，其表达式为

$$
\mathrm { l g } t _ { \mathrm { c } } = g _ { 1 } + g _ { 2 } { \frac { 1 } { T } } + g _ { 3 } { \frac { x } { T } } + g _ { 4 } { \frac { x ^ { 2 } } { T } } + g _ { 5 } { \frac { x ^ { 3 } } { T } }
$$

式中： $t _ { \mathrm { c } }$ 为持久寿命， $x = \lg \sigma , T = 9 \theta / 5 + 4 9 2$ , $\theta$ 为摄氏温度。

对于GH907，持久寿命程中系数值分别为： $g _ { \mathrm { ~ I ~ } } = \mathrm { ~ - ~ } 1 8 . 6 4 8$ , $g _ { 2 } \ = \ 6 7 2 4 4$ ,$g _ { 3 } = - 4 7 2 6 5 . 9$ , $g _ { 4 } = 2 6 0 1 8 . 1$ , $g _ { 5 } = - 4 8 2 2 . 6$ ，由L-M方程计算得到的各温度和应力下的持久寿命见表2-5。

表2-5 GH907在不同温度和应载荷下的持久寿命  

<table><tr><td rowspan=1 colspan=1>温度/℃</td><td rowspan=1 colspan=1>应力/MPa</td><td rowspan=1 colspan=1>持久寿命/h</td></tr><tr><td rowspan=1 colspan=1>600</td><td rowspan=1 colspan=1>380</td><td rowspan=1 colspan=1>10988.03</td></tr><tr><td rowspan=1 colspan=1>600</td><td rowspan=1 colspan=1>440</td><td rowspan=1 colspan=1>4304.023</td></tr><tr><td rowspan=1 colspan=1>600</td><td rowspan=1 colspan=1>460</td><td rowspan=1 colspan=1>3149.295</td></tr><tr><td rowspan=1 colspan=1>650</td><td rowspan=1 colspan=1>290</td><td rowspan=1 colspan=1>2403.611</td></tr><tr><td rowspan=1 colspan=1>650</td><td rowspan=1 colspan=1>330</td><td rowspan=1 colspan=1>1351.043</td></tr><tr><td rowspan=1 colspan=1>650</td><td rowspan=1 colspan=1>390</td><td rowspan=1 colspan=1>942.125</td></tr></table>

由于屈服应随温度变化而变化，这可近似用线性关系表示屈服应随归化温度的变化

$$
\sigma _ { 0 . 2 } = f _ { 1 } + f _ { 2 } \frac { T } { T _ { _ m } }
$$

不同温度下的屈服应见表 $2 - 6$ ，根据式（2-10）进拟合，可以得到 $f _ { 1 } =$ 844.9, $f _ { 2 } = - 3 6 8 . 8$ ,由 $f _ { 1 }$ 和 $f _ { 2 }$ 可计算得到不同温度下的屈服应见表2-6中的第3列，误差为拟合后的屈服应力与拟合前的屈服应力的差值相对于拟合前的屈服应力的百分比。最大误差为 $5 . 1 \%$ ，在可接受的范围之内。

表2-6 不同温度下GH907屈服应和拟合屈服应的较  

<table><tr><td rowspan=1 colspan=1>温度/℃</td><td rowspan=1 colspan=1>屈服应力/MPa</td><td rowspan=1 colspan=1>拟合后的屈服应力/MPa</td><td rowspan=1 colspan=1>误差/%</td></tr><tr><td rowspan=1 colspan=1>20</td><td rowspan=1 colspan=1>805</td><td rowspan=1 colspan=1>777.87792</td><td rowspan=1 colspan=1>3.37</td></tr><tr><td rowspan=1 colspan=1>300</td><td rowspan=1 colspan=1>685</td><td rowspan=1 colspan=1>713.8623</td><td rowspan=1 colspan=1>4.21</td></tr><tr><td rowspan=1 colspan=1>400</td><td rowspan=1 colspan=1>670</td><td rowspan=1 colspan=1>690.9996</td><td rowspan=1 colspan=1>3.13</td></tr><tr><td rowspan=1 colspan=1>500</td><td rowspan=1 colspan=1>645</td><td rowspan=1 colspan=1>668.1369</td><td rowspan=1 colspan=1>3.59</td></tr><tr><td rowspan=1 colspan=1>600</td><td rowspan=1 colspan=1>680</td><td rowspan=1 colspan=1>645.2741</td><td rowspan=1 colspan=1>5.11</td></tr><tr><td rowspan=1 colspan=1>650</td><td rowspan=1 colspan=1>645</td><td rowspan=1 colspan=1>633.8428</td><td rowspan=1 colspan=1>1.73</td></tr></table>

将不同温度、应下的数据按照式（2-3）和式（2-4）处理成归化时间、归化温度和归一化应力为自变量，蠕变应变为因变量的形式，利用所发展的模型进拟合，拟合得到的 $a _ { i }$ , $b _ { i }$ , $c _ { i } , \ d _ { i }$ $i = 1$ ，2，3，4，5）见表2-7，拟合曲线如图2-8所示。

表2-7 GH907材料拟合得到的各参数（总体拟合）  

<table><tr><td rowspan=2 colspan=1>参数</td><td rowspan=1 colspan=4>系数</td></tr><tr><td rowspan=1 colspan=1>ai</td><td rowspan=1 colspan=1>bi</td><td rowspan=1 colspan=1>ci</td><td rowspan=1 colspan=1>di</td></tr><tr><td rowspan=1 colspan=1>n1</td><td rowspan=1 colspan=1>-1386.3</td><td rowspan=1 colspan=1>3144.5</td><td rowspan=1 colspan=1>4065.1</td><td rowspan=1 colspan=1>-7504.4</td></tr><tr><td rowspan=1 colspan=1>72</td><td rowspan=1 colspan=1>88.7</td><td rowspan=1 colspan=1>-190.8</td><td rowspan=1 colspan=1>-150.4</td><td rowspan=1 colspan=1>263.2</td></tr><tr><td rowspan=1 colspan=1>73</td><td rowspan=1 colspan=1>15.0</td><td rowspan=1 colspan=1>17.8</td><td rowspan=1 colspan=1>-18.7</td><td rowspan=1 colspan=1>-59.0</td></tr><tr><td rowspan=1 colspan=1>74</td><td rowspan=1 colspan=1>12.9</td><td rowspan=1 colspan=1>12.4</td><td rowspan=1 colspan=1>-10.1</td><td rowspan=1 colspan=1>-13.9</td></tr><tr><td rowspan=1 colspan=1>15</td><td rowspan=1 colspan=1>505.5</td><td rowspan=1 colspan=1>-195.6</td><td rowspan=1 colspan=1>-171.6</td><td rowspan=1 colspan=1>307.7</td></tr></table>

![](images/271312d51733cc13df95a51937ef3567c60c26e24512a00e219cff3bab68bdd5.jpg)  
图2-8 GH907材料蠕变曲线拟合结果的对（总体拟合）

参数总体拟合的优点为：参数处理法较为简单，进次拟合就可得到20个系数值。其缺点是：参数处理根据最乘法拟合，蠕变第1阶段数据点的值较，可能造成拟合结果的第阶段不明显，当蠕变曲线的第3阶段不明显时，拟合结果近似为直线；同时参数范围不易控制，例如，根据系数值算出的某个温度和应下的 $\eta _ { 5 }$ 可能会于1或常；在取点时，若某些曲线较长，则得到的数据点也会较多，进最乘法拟合时数据点较多的曲线会拟合得较好，其他数据点少的曲线的拟合效果会较差，在取点时，每条曲线上取点的数量不宜差别过大。

# 2.2.5.2基于物理意义拟合方法

归化蠕变模型中的参数 $\eta _ { i }$ d $i = 1$ ，2，3，4，5）具有明确的物理意义，根据其物理意义，用该蠕变模型对实际材料的一组蠕变曲线进拟合的步骤为：

（1）按持久断裂时间对蠕变曲线进归化，所有曲线的时间坐标范围均为[0,1];

（2）对每条曲线第2阶段进拟合（程为 $y = k x + b$ )，得到不同应和温度下的一组 $\eta _ { 2 }$ 值（ $k$ 值）， $\eta _ { 2 }$ 为归化坐标下的稳态蠕变应变率或最蠕变率；

(3）步骤（2）中得到的 $b$ 值即为 $\eta _ { 1 }$ , $\eta _ { 3 } = \varepsilon _ { \mathrm { r } } - \eta _ { 1 } - \eta _ { 2 }$ , $\varepsilon _ { r }$ 为断裂时的蠕变应变；

（4）然后根据所得的参数 $\eta _ { 1 }$ , $\eta _ { 2 }$ , $\eta _ { 3 }$ ，用式（2-3）对每条曲线进拟合，得到$\eta _ { 4 }$ , $\eta _ { 5 }$ ;

(5）最后将 $\eta _ { i }$ $i = 1$ ，2，3，4，5）表示为无量纲应力 $\sigma / \sigma _ { 0 . 2 }$ 与量纲温度 $T / T _ { \mathrm { m } }$ 的函数。

现基于物理意义对GH907材料的蠕变曲线进拟合。将各个温度和应下的蠕变曲线进归化，先，对各条曲线的第阶段进拟合，得到的直线程的斜率即$\eta _ { 2 }$ ，与纵轴的交点即 $\eta _ { 1 }$ ，如图2-9所，由各条曲线可得到不同温度和应下的 $\eta _ { 2 }$ ,见表2-8中的前3列。由表2-8中的前3列根据式（2-4）拟合得到系数a2，b₂，C2，$d _ { 2 }$ ，再根据系数值反算出各个温度和应力下的 $\eta _ { 2 }$ 值，见表2-8中第4列。

![](images/191d7bc901d4d4fd176522075686f5188da052fad688934c307da1876b000c26.jpg)  
图2-9 对GH907材料蠕变曲线第阶段进拟合( $6 0 0 \mathrm { { ‰} }$ )

表2-8不同温度和应力下对 $\mathbf { G H 9 0 7 }$ 材料蠕变曲线拟合得到的 $\pmb { \eta } _ { 2 }$ 值  

<table><tr><td rowspan=1 colspan=1>温度/℃C</td><td rowspan=1 colspan=1>应力/MPa</td><td rowspan=1 colspan=1>$n_21%</td><td rowspan=1 colspan=1>拟合后$n_2/%</td></tr><tr><td rowspan=1 colspan=1>600</td><td rowspan=1 colspan=1>380</td><td rowspan=1 colspan=1>7.5293</td><td rowspan=1 colspan=1>6.4324</td></tr><tr><td rowspan=1 colspan=1>600</td><td rowspan=1 colspan=1>440</td><td rowspan=1 colspan=1>2.5479</td><td rowspan=1 colspan=1>2.0081</td></tr><tr><td rowspan=1 colspan=1>600</td><td rowspan=1 colspan=1>460</td><td rowspan=1 colspan=1>2.3183</td><td rowspan=1 colspan=1>1.3622</td></tr><tr><td rowspan=1 colspan=1>650</td><td rowspan=1 colspan=1>290</td><td rowspan=1 colspan=1>0.7632</td><td rowspan=1 colspan=1>1.0430</td></tr><tr><td rowspan=1 colspan=1>650</td><td rowspan=1 colspan=1>330</td><td rowspan=1 colspan=1>2.72233</td><td rowspan=1 colspan=1>1.0717</td></tr><tr><td rowspan=1 colspan=1>650</td><td rowspan=1 colspan=1>390</td><td rowspan=1 colspan=1>1.0945</td><td rowspan=1 colspan=1>1.1162</td></tr></table>

基于物理意义得到 $\eta _ { \mathrm { j } }$ 和 $\eta _ { 2 }$ ，由式（2-4）拟合得到系数 $a _ { 1 }$ , $b _ { 1 }$ , $c _ { 1 }$ , $d _ { \parallel }$ 和 $a _ { 2 }$ , $b _ { 2 }$ ,$c _ { 2 }$ , $d _ { 2 }$ ，由于GH907的材料数据乎只有前两个阶段，并不能从物理意义中得到 $\eta _ { 3 }$ ,可将 $\eta _ { 3 }$ , $\eta _ { 4 }$ 和 $\eta _ { 5 }$ 看作未知数，根据每条曲线的数据点拟合得到。再由式（2-4）拟合得到各的系数，5个参数 $\eta _ { i }$ $\begin{array} { r l } { \dot { \iota } } & { { } = 1 } \end{array}$ ，2，3，4，5）的值见表2-9，拟合结果见图2-10。

表2-9 GH907蠕变模型中的参数值（基于物理意义拟合）  

<table><tr><td rowspan=2 colspan=1>参数</td><td rowspan=1 colspan=4>系数</td></tr><tr><td rowspan=1 colspan=1>ai</td><td rowspan=1 colspan=1>bi</td><td rowspan=1 colspan=1>Ci</td><td rowspan=1 colspan=1>di</td></tr><tr><td rowspan=1 colspan=1>71</td><td rowspan=1 colspan=1>-2707.5</td><td rowspan=1 colspan=1>4991.3</td><td rowspan=1 colspan=1>6452.6</td><td rowspan=1 colspan=1>-11911.7</td></tr><tr><td rowspan=1 colspan=1>72</td><td rowspan=1 colspan=1>173.2</td><td rowspan=1 colspan=1>-302.9</td><td rowspan=1 colspan=1>-238.7</td><td rowspan=1 colspan=1>417.8</td></tr><tr><td rowspan=1 colspan=1>73</td><td rowspan=1 colspan=1>-9.7</td><td rowspan=1 colspan=1>11.6</td><td rowspan=1 colspan=1>-12.2</td><td rowspan=1 colspan=1>38.3</td></tr><tr><td rowspan=1 colspan=1>74</td><td rowspan=1 colspan=1>8.4</td><td rowspan=1 colspan=1>8.1</td><td rowspan=1 colspan=1>-6.6</td><td rowspan=1 colspan=1>-9.0</td></tr><tr><td rowspan=1 colspan=1>15</td><td rowspan=1 colspan=1>174.6</td><td rowspan=1 colspan=1>-310.4</td><td rowspan=1 colspan=1>-272.4</td><td rowspan=1 colspan=1>488.3</td></tr></table>

![](images/650fd43c63da26cfea5e9fb1c10d5ece34a2784b727aee0d36b9bb04a1068514.jpg)  
图2-10 GH907材料蠕变曲线拟合结果的对（基于物理意义拟合)

图2-10中 $6 5 0 \%$ 、 $2 9 0 \mathrm { M P a }$ 下的拟合曲线和试验曲线有较差别，这是由于$6 5 0 \mathrm { { ^ \circ C } }$ , $2 9 0 \mathrm { M P a }$ 下参数 $\eta _ { 2 }$ 很，在拟合中并不能较好地符合每个温度和应下的参数值，拟合后得到的参数 $\eta _ { 2 }$ 较大，因而 $2 9 0 \mathrm { M P a }$ 下的拟合曲线比试验曲线得多。总体来说，基于物理意义拟合的效果比总体拟合法的好，能更准确地描述每个阶段。

基于物理意义拟合时所求得的参数值范围可控，不会出现特别大或特别的情况。但该法也存在定缺点：拟合过程比较繁琐，须对每条曲线进取值，然后根据物理意义进参数提取和拟合；不同温度和应下拟合得到的参数 $\eta _ { i }$ 值与严格按照物理意义得到的值有时可能相差较，只能通过其他参数进调整，须对已拟合过的参数进多次拟合调整。2.3节和2.4节均采基于物理意义拟合的法，对于蠕变曲线较少的情况该法拟合得到的值也能符合要求。

# 2.3 归化参数蠕变模型的程序实现及验证

本节采前节所提出的基于归化参数的蠕变模型，在通有限元程序ANSYS环境下，通过编写usercreep程序实现了对实际构件的蠕变分析[14\~16]，并在已有的两种变载理论模型基础上提出了种介于其间的法，然后将这3种模型在所发展的程序中进了程序实现，使所发展的归化参数蠕变模型能够按照不同的变载理论模型对实际结构进有限元计算分析[14,15]。通过建带孔平板结构的有限元模型，应3种变载理论模型对其进有限元分析，得到了模型中不同位置的应与应变等随时间的变化规律。

# 2.3.1 归化参数蠕变模型的程序实现

基于通有限元程序ANSYS中的UserProgrammable Features（UPFs）具，将前节发展的基于归化参数的蠕变模型应于结构件的有限元分析。按UPFs所提供的usercreep程序接要求进程序代码编写，通过户程序与主程序的编译连接，得到可于计算分析实际构件3个阶段蠕变变形的程序软件。

在ANSYS程序中UPFs具提供了多种程序接，户可以按照实际需要选择满足其使用要求的程序接，比如定义新的材料属性、创建新单元、优化设计算法等。UPFs是用户在ANSYS程序提供的FORTRAN代码基础上，修改其可编程程序，并需在相应的FORTRAN编译器持下，将修改后的程序与ANSYS库相连接形成户版本的ANSYS可执件。下对与蠕变有关的程序接进简要介绍。

ANSYS中可于蠕变编程的相关程序接有3个：usermat、usercr和usercreep。3个程序接都属于本构模型程序，每个单元的每个积分点在每个载荷步的每次迭代都将调用该子程序[14,16,17]。

usermat是使用范围较的程序，其主要任务是定义材料应应变关系，由给定的应变增量 $\Delta \varepsilon$ 计算得到应力增量 $\Delta \sigma$ ，从而得到新的应 $\sigma$ ；还需给出雅可比矩阵$D = \frac { \partial \Delta \sigma } { \partial \Delta \varepsilon }$ (id) 定义材料的应力应变关系时，根据主程序传的应变、应变分量的增量、应、温度等参数，利弹性、塑性、蠕变等关系，用户定义应增量，对应进更新。

usercr和usercreep可来模拟材料与时间相关的蠕变为，其中usercreep采隐式积分算法计算蠕变应变，稳定精确且条件收敛；usercr采显式积分算法计算蠕变应变，需要采较小的时间步长以使求解收敛。

与usermat程序相，usercreep的使相对较为便，其计算速度也比较快，且只需在主程序中定义即可，不用在子程序中判断材料类型（各向同性材料、正交各向异性等）、应力状态（平面应力、平面应变等）、是否进塑性等情况。因此，本中采usercreep进户程序编制。

般地，材料的应变由3部分组成，弹性应变 $\dot { \varepsilon } _ { \mathrm { ~ e ~ l ~ } }$ 、塑性应变 $\dot { \varepsilon } _ { \mathrm { \scriptsize ~ p l } }$ 和蠕变应变 $\dot { \varepsilon } _ { \mathrm { c r } }$ ,userereep程序仅计算其中的蠕变应变，户须根据需要来定义材料的弹、塑性为。

现将2.2节中所发展的基于归化参数的蠕变模型编写为usercreep程序，蠕变应变的表达式为

$$
\varepsilon _ { \mathrm { c } } = \eta _ { 1 } ( 1 - \mathrm { e } ^ { - \eta _ { 4 } \zeta } ) + \eta _ { 2 } \zeta + \eta _ { 3 } \zeta ^ { \eta _ { 5 } }
$$

$$
\ln \eta _ { i } = a _ { i } + b _ { i } { \frac { T } { T _ { \mathrm { m } } } } + c _ { i } { \frac { \sigma } { \sigma _ { 0 , 2 } } } + d _ { i } { \frac { T } { T _ { \mathrm { m } } } } { \frac { \sigma } { \sigma _ { 0 , 2 } } }
$$

式中： $\zeta = t / t _ { \mathrm { c } }$ 为无量纲时间， $t _ { \mathrm { c } }$ 为给定温度和应下的持久寿命， $\sigma _ { 0 . 2 }$ 为屈服应， $T _ { \mathrm { m } }$ 为熔点温度， $\eta _ { i }$ $i = 1$ ，2，3，4，5）代表5个参数， $a _ { i }$ , $b _ { i }$ , $c _ { i }$ , $d _ { i }$ 为与各参数对应的常数（ $i = 1$ ，2，3，4，5)，模型中的参数均无量纲。

usercreep户程序的输变量包括等效应、等效蠕变应变、时间、温度、屈服应等。其输出变量有：（1）蠕变应变增量（程序中变量名为delcr）；（2）蠕变应变增量对等效应的导数（程序中变量名为dcrda（1））；（3）蠕变应变增量对蠕变应变的导数（程序中变量名为dcrda（2））。

可由式（2-1）计算得到3个输出变量。

（1）蠕变应变增量

$$
\dot { \varepsilon } _ { \mathrm { ~ c ~ } } \Delta t = \frac { 1 } { t _ { \mathrm { c } } } ( \eta _ { \mathrm { _ l } } \eta _ { \mathrm { 4 } } \mathrm { e } ^ { - \eta _ { 4 } \zeta } + \eta _ { \mathrm { _ 2 } } + \eta _ { \mathrm { 3 } } \eta _ { \mathrm { _ 5 } } \zeta ^ { \eta _ { \mathrm { 5 } } - 1 } ) \Delta t
$$

（2）蠕变应变增量对等效应的导数

$$
\frac { \partial ( \hat { \varepsilon } _ { \mathrm { c } } \Delta t ) } { \partial \sigma } = \frac { 1 } { t _ { \mathrm { c } } } \frac { 1 } { \sigma _ { _ { 0 . 2 } } } \left[ \eta _ { 1 } \eta _ { 4 } { \mathrm e } ^ { - \eta _ { 4 } \zeta } ( { q } _ { 1 } + { q } _ { 4 } - { q } _ { 4 } \eta _ { 4 } \zeta ) + { q } _ { 2 } { \eta } _ { 2 } + { q } _ { 3 } { \eta } _ { 4 } \zeta \right] ,
$$

$$
\eta _ { 3 } \eta _ { 5 } \zeta ^ { \eta _ { 5 } - 1 } \left( q _ { 3 } + q _ { 5 } + q _ { 5 } \eta _ { 5 } \mathrm { l n } \zeta \right) \bigr ] \Delta t
$$

式中： $q _ { i }$ 为中间变量， $q _ { i } = c _ { i } + d _ { i } \frac { T } { T _ { m } } \left( i = 1 , \ 2 , \ 3 , \ 4 , \ 5 \right) _ { \circ }$

（3）蠕变应变增量对蠕变应变的导数

$$
\frac { \partial \big ( \dot { \varepsilon } _ { \mathrm { c } } \Delta t \big ) } { \partial \varepsilon _ { \mathrm { c } } } = \frac { \mathrm { d } \dot { \varepsilon } _ { \mathrm { c } } } { \mathrm { d } t } \left( \frac { 1 } { \mathrm { d } \varepsilon _ { \mathrm { c } } } \right) \Delta t = \frac { - \eta _ { 1 } \eta _ { 4 } ^ { 2 } \mathrm { e } ^ { - \eta _ { 4 } \xi } + \eta _ { 3 } \eta _ { 5 } \left( \eta _ { 5 } - 1 \right) \zeta ^ { \eta _ { 5 } - 2 } } { t _ { \mathrm { c } } \left( \eta _ { 1 } \eta _ { 4 } \mathrm { e } ^ { - \eta _ { 4 } \zeta } + \eta _ { 2 } + \eta _ { 3 } \eta _ { 5 } \zeta ^ { \eta _ { 5 } - 1 } \right) } \Delta t
$$

由于屈服应随温度改变变化，这近似线性关系表示屈服应随归化温度的变化

$$
\sigma _ { 0 , 2 } = f _ { 1 } + f _ { 2 } \frac { T } { T _ { \mathrm { m } } }
$$

持久寿命也是随应和温度的变化变化的，采前一节中的持久寿命程（L-M程）将持久断裂寿命表示为应力和温度的函数

$$
\mathrm { l g } t _ { \mathrm { c } } = g _ { 1 } + g _ { 2 } \frac { 1 } { T } + g _ { 3 } \frac { x } { T } + g _ { 4 } \frac { x ^ { 2 } } { T } + g _ { 5 } \frac { x ^ { 3 } } { T }
$$

式中： $t _ { \mathrm { c } }$ 为持久寿命， $x = \lg \sigma , T = 9 \theta / 5 + 4 9 2$ , $\theta$ 为摄氏温度。

式（2-15）中， $f _ { 1 }$ , $f _ { 2 }$ 均为待定常数，可通过材料数据拟合得到。式（2-16）中$g _ { 1 }$ , $g _ { 2 }$ ,…, $g _ { 5 }$ 亦为常数，可由材料数据册中的持久试验数据得到相关数值，或者根据试验数据拟合得到。

可按式（2-12）\~式（2-16）归化参数蠕变模型编写usercreep程序，参数的输通过TBDATA命令输，程序参数输顺序见表2-10，表中的符号对应于式（2-12）～式（2-16）中各符号，需要注意的是usercreep程序要求TBDATA，13不能使。

表2-10 usercreep程序参数输列表  

<table><tr><td colspan="1" rowspan="1">n</td><td colspan="1" rowspan="1">ci</td><td colspan="2" rowspan="1">2</td><td colspan="2" rowspan="1">3</td><td colspan="2" rowspan="1">4</td><td colspan="2" rowspan="1">5</td><td colspan="1" rowspan="1">6</td></tr><tr><td colspan="1" rowspan="1">含义</td><td colspan="1" rowspan="1">$\\}$</td><td colspan="2" rowspan="1">$b\fa}$</td><td colspan="2" rowspan="1">ci}$</td><td colspan="2" rowspan="1">$d_1}$</td><td colspan="2" rowspan="1">$a2r}$</td><td colspan="1" rowspan="1">$b2}$</td></tr><tr><td colspan="1" rowspan="1">n</td><td colspan="1" rowspan="1">7</td><td colspan="2" rowspan="1">8</td><td colspan="2" rowspan="1">9</td><td colspan="2" rowspan="1">10</td><td colspan="2" rowspan="1">1</td><td colspan="1" rowspan="1">12</td></tr><tr><td colspan="1" rowspan="1">含义</td><td colspan="1" rowspan="1">$c2r}$</td><td colspan="2" rowspan="1">$d_2}$</td><td colspan="2" rowspan="1">$a3</td><td colspan="2" rowspan="1">b3</td><td colspan="2" rowspan="1">C3</td><td colspan="1" rowspan="1">d3</td></tr><tr><td colspan="1" rowspan="1">n</td><td colspan="1" rowspan="1">13</td><td colspan="2" rowspan="1">14</td><td colspan="2" rowspan="1">15</td><td colspan="2" rowspan="1">16</td><td colspan="2" rowspan="1">17</td><td colspan="1" rowspan="1">18</td></tr><tr><td colspan="1" rowspan="1">含义</td><td colspan="1" rowspan="1">一</td><td colspan="2" rowspan="1">a4</td><td colspan="2" rowspan="1">b4</td><td colspan="2" rowspan="1">C4</td><td colspan="2" rowspan="1">d4}$</td><td colspan="1" rowspan="1">$a5</td></tr><tr><td colspan="1" rowspan="1">n</td><td colspan="1" rowspan="1">19</td><td colspan="2" rowspan="1">20</td><td colspan="2" rowspan="1">21</td><td colspan="2" rowspan="1"></td><td colspan="2" rowspan="1"></td><td colspan="1" rowspan="1"></td></tr><tr><td colspan="1" rowspan="1">含义</td><td colspan="1" rowspan="1">b5</td><td colspan="2" rowspan="1">$c5$</td><td colspan="2" rowspan="1">ds</td><td colspan="2" rowspan="1"></td><td colspan="2" rowspan="1"></td><td colspan="1" rowspan="1"></td></tr><tr><td colspan="1" rowspan="1">n</td><td colspan="10" rowspan="1">22</td></tr><tr><td colspan="1" rowspan="1">含义</td><td colspan="10" rowspan="1">Tm</td></tr><tr><td colspan="1" rowspan="1">n</td><td colspan="5" rowspan="1">23</td><td colspan="5" rowspan="1">24</td></tr><tr><td colspan="1" rowspan="1">含义</td><td colspan="5" rowspan="1">f</td><td colspan="5" rowspan="1">$f_2a}$</td></tr><tr><td colspan="1" rowspan="1">n</td><td colspan="2" rowspan="1">25</td><td colspan="2" rowspan="1">26</td><td colspan="2" rowspan="1">27</td><td colspan="2" rowspan="1">28</td><td colspan="2" rowspan="1">29</td></tr><tr><td colspan="1" rowspan="1">含义</td><td colspan="2" rowspan="1">1</td><td colspan="2" rowspan="1">$2$</td><td colspan="2" rowspan="1">B3</td><td colspan="2" rowspan="1">4</td><td colspan="2" rowspan="1">5</td></tr></table>

按式（2-12）\~式（2-16）即可实现usercreep程序的编写，然后将所编制的usercreep程序与ANSYS主程序进编译连接，即可将所发展的归化参数蠕变模型应用于实际结构件的蠕变计算分析。

编译连接的步骤为：

（1）由于usercreep程序是Fortran语编写的，因此编译连接还需安装相关编译器软件，包括Visual Studio和IntelFortran Composer，对于不同的ANSYS版本，这两个软件也需安装相应的版本以保证其兼容性。

（2）再将户程序usercreep.F存对应的安装录下，进编译连接，成户版本的ANSYS可执行件。

（3）通过Customzation/Preferences指向上步成的可执件启动ANSYS，在TB，CREEP命令中令 $\mathrm { T B O P T } = 1 0 0$ 即可调usercreep程序。计算过程中需输“RATE，ON”打开时间相关选项开关来进蠕变计算分析。

Usercreep程序中，主程序传的并不是各个应分量，是等效应（程序中变量名为sequ），当采用默认设置时，传的等效应为VonMises等效应，适用于各向同性材料。当输入“TB，HILL，MAT，NTEMP，6，”命令后，传入到子程序中的等效应即为Hill等效应，适于正交各向异性材料。“TB，HIL，MAT，NTEMP，6,”命令中，MAT为设置的材料号，NTEMP为需输的温度的数量，由“TBDATA，1, $R _ { x }$ , $R _ { y }$ , $R _ { z }$ , $R _ { x y }$ , $R _ { y z }$ , $R _ { z x }$ ”输Hill准则相关的6个参数，其中 $R _ { x }$ , $R _ { y }$ , $R _ { z }$ , $R _ { x y }$ ,$R _ { y z }$ , $R _ { z x }$ 即为式（2-7）各个向的屈服应： $R _ { x } = \frac { \sigma _ { x } ^ { y } } { \sigma ^ { y } } , R _ { y } = \frac { \sigma _ { y } ^ { y } } { \sigma ^ { y } } , R _ { z } = \frac { \sigma _ { z } ^ { y } } { \sigma ^ { y } } , R _ { x y } = \sqrt { 3 }$ ${ \frac { \sigma _ { x y } ^ { y } } { \sigma ^ { y } } } , \ R _ { y z } = { \sqrt { 3 } } \ { \frac { \sigma _ { y z } ^ { y } } { \sigma ^ { y } } } , \ R _ { z x } = { \sqrt { 3 } } \ { \frac { \sigma _ { z x } ^ { y } } { \sigma ^ { y } } }$ bid 通过相应的设置可实现对各向同性或正交各向异性材料进设置。对于航空发动机常用的定向结晶和单晶材料，在ANSYS中输相应材料参数，通过“TB，HIL，MAT，NTEMP，6，”命令即可用所编写的子程序对定向结晶和单晶材料结构进行蠕变计算分析。

# 2.3.2 归化参数蠕变模型的usercreep程序的考核验证

利所编写的usercreep程序与ANSYS程序带的模型进计算对，以验证程序前两个阶段模拟蠕变变形的正确性[14\~16〕。通过编写应变硬化模型的程序和程序带模型对正交各向异性材料进蠕变计算的结果对，以表明usercreep程序可适于定向结晶材料和单晶材料的蠕变变形的数值模拟。

ANSYS程序中提供了应变硬化蠕变分析模型，本先根据应变硬化模型编写其户程序usercreep，分别采所编写的应变硬化模型程序和ANSYS带的应变硬化模型分别计算分析蠕变变形，对所得结果以验证usercreep程序计算结果的正确性。另面由于归化参数模型能描述3个阶段的蠕变变形，通过参数拟合，使应变硬化模型的蠕变曲线和归化参数模型的蠕变曲线的前两个阶段尽可能相同，来表征归化参数蠕变模型的程序描述前两个阶段的正确性，同时可具备描述第3阶段蠕变为的能力。

应变硬化模型表达式为

$$
\dot { \varepsilon } _ { \mathrm { ~ c ~ } } = A \sigma ^ { n } \varepsilon _ { \mathrm { ~ c ~ } } ^ { m } \mathrm { e } ^ { - Q / R T }
$$

式中：A, $n$ , $m$ , $Q / R$ 分别为材料常数。

编写应变硬化模型的usercreep程序所需的3个输出变量如下。

(1）蠕变应变增量delcr

$$
\mathrm { d e l c r } = \dot { \varepsilon } _ { \mathrm { ~ e ~ } } \Delta t = A \sigma ^ { n } \varepsilon _ { \mathrm { ~ e ~ } } ^ { m } \mathrm { e } ^ { - Q / R T } \Delta t
$$

(2）蠕变应变增量对应的导数dcrda (1)

$$
\mathrm { d c r d a } \left( 1 \right) = \frac { \partial \left( \dot { \varepsilon } _ { \mathrm { c } } \Delta t \right) } { \partial \sigma } = n \frac { \mathrm { d e l c r } } { \sigma } \Delta t
$$

(3）蠕变应变增量对蠕变应变的导数derda(2)

$$
\mathrm { { d c r d a } } \left( 2 \right) = \frac { \partial \left( \begin{array} { l } { \dot { \varepsilon } _ { \mathrm { c } } \Delta t } \end{array} \right) } { \partial \varepsilon _ { \mathrm { c } } } = m \frac { \mathrm { { d e l c r } } } { \varepsilon _ { \mathrm { c } } } \Delta t
$$

采所发展的归化参数蠕变模型与应变硬化模型对直接时效GH4169G材料在 $6 8 0 \mathrm { { ^ \circ C } }$ , $6 5 0 \mathrm { M P a }$ 下的蠕变曲线进拟合，归一化参数模型的参数值即2.2节中的拟合值，应变硬化模型的参数值为： $A = 4 . 8 2 \times 1 0 ^ { - 1 1 }$ , $n = 1 . 0 0 3 5 6 9$ , $m \ =$ -2.0692, $Q / R = 9 9 1 . 9 7 3 1$ ，拟合结果如图2-11所。由图中可以看出，归化参数蠕变模型的前两个阶段的曲线和应变硬化模型曲线较为接近，拟合结果较为理想。

现采3种式（所编写的应变硬化模型程序、ANSYS程序带应变硬化模型和基于归化参数蠕变模型编写的程序）对有限元模型进蠕变计算分析，以考察usercreep程序计算构件的蠕变法是否可，同时验证所编写的归化参数蠕变模型的程序是否正确。于usercreep程序考核计算的有限元模型如图2-12所示，其中采八节点六体单元类型，即ANSYS中的solid185号单元，在 $x = 0 , y = 0 , z = 0$ 的面上分别约束各节点的 $x$ ,y, $z$ 方向的位移，在 $x = 5 , y = 4$ 的面上分别施加 $7 0 0 \mathrm { M P a }$ , $1 0 0 \mathrm { M P a }$ 的应。3种式计算得到的该有限元模型的蠕变变形结果如图2-13所。

![](images/e6f97b7b9a29a76eb228ef98be9ccf4f41173e6b7f64067c2e78821fce86ebb2.jpg)  
图2-11 归化参数蠕变模型与应变硬化模型的拟合结果

![](images/9bdaf04973d5e5d32ed9901aed88785967bf1f6dd508feaccadc4270f7dcdcba.jpg)  
图2-12 于程序考核的有限元模型

![](images/1787da8e49171828a1df793b8154393915f068e2a5287cf46ce2d808833ce28a.jpg)

![](images/215804c90efdb0d8aaa90bfe6ea7bf2e6153270de81b7dd1418961e8ad593f1a.jpg)  
图2-13 3种式计算得到的蠕变应变

由图2-13中可知：对应变硬化模型，由程序编写模型计算获得的结果与ANSYS程序带模型的计算结果致，并且与归化参数蠕变模型的前半部分基本重合，说明采用归化参数蠕变模型的程序计算蠕变前两个阶段的变形精度合适，且同时具备模拟蠕变第3阶段变形的能，采基于归化参数蠕变模型编写usercreep程序的法计算蠕变变形是可的。

航空发动机中常用的定向结晶材料为横观各向同性材料，单晶材料为正交各向异性材料。对于横观各向同性材料，假设 $z$ 轴为对称轴（材料数据册中的纵向，柱晶长向），oxy平面为各向同性平面（横向，垂直于柱晶生长方向），需提供对称轴向和各向同性平面上的弹性模量 $E _ { \mathrm { { L } } }$ $E _ { \mathrm { { T } } }$ ，泊松比 $\upsilon _ { \mathrm { L } }$ (i:) $\upsilon _ { \mathrm { T } }$ 和剪切模量 $G _ { \mathrm { { L } } }$ (: $G _ { \mathrm { r } }$ ，这下标 $\mathrm { L }$ 表示纵向，下标T表示横向。由于横向为各向同性平，则横向各向同性平面的剪切模量满G=2(1+v) 因此共需要5个参数来定义横观各向同性材料的应/应变矩阵。正交各向异性材料需定义3个对称轴向上的弹性模量、泊松和剪切模量，共9个材料参数，单晶材料3个对称轴向上的材料参数相同，因单晶材料仅需定义3个材料参数。ANSYS中提供的材料模型有各向同性材料、正交各向异性材料和各向异性材料3种模型，通过对比横观各向同性和单晶材料的应/应变矩阵，横观各向同性材料的参数可通过正交各向异性材料模型进输。

通常，应力/应变关系为式中： $C$ i: 柔度矩阵；

$\pmb { D }$ 刚度矩阵。

$\varepsilon$ 和 $\sigma$ 分别表示应变和应力矢量

$$
\begin{array} { r } { \varepsilon = \left[ \begin{array} { l } { \varepsilon _ { x } } \\ { \varepsilon _ { y } } \\ { \varepsilon _ { z } } \\ { \varepsilon _ { x } } \\ { \varepsilon _ { y } } \\ { \varepsilon _ { y z } } \\ { \varepsilon _ { z x } } \end{array} \right] , \qquad \pmb { \sigma } = \left[ \begin{array} { l } { \sigma _ { x } } \\ { \sigma _ { y } } \\ { \sigma _ { z } } \\ { \sigma _ { x y } } \\ { \sigma _ { y z } } \\ { \sigma _ { z x } } \end{array} \right] } \end{array}
$$

正交各向异性材料的柔度矩阵为[22]

$$
C = \left[ \begin{array} { l l l l l l l } { \frac { 1 } { E _ { x } } } & { - \frac { v _ { x } } { E _ { y } } } & { - \frac { v _ { x } } { E _ { z } } } & { 0 } & { 0 } & { 0 } \\ { 0 } & { 0 } & { - \frac { v _ { y } } { E _ { z } } } & { 0 } & { 0 } & { 0 } \\ { - \frac { v _ { x } } { E _ { x } } } & { \frac { 1 } { E _ { y } } } & { - \frac { v _ { y } } { E _ { z } } } & { 0 } & { 0 } & { 0 } \\ { 0 } & { 0 } & { \frac { v _ { x } } { E _ { x } } } & { 0 } & { 0 } & { 0 } \\ { 0 } & { 0 } & { 0 } & { \frac { 1 } { G _ { y } } } & { 0 } & { 0 } \\ { 0 } & { 0 } & { 0 } & { 0 } & { \frac { 1 } { G _ { z } } . 0 } \\ { 0 } & { 0 } & { 0 } & { 0 } & { 0 } & { \frac { 1 } { G _ { z } } . } \end{array} \right]
$$

若为单晶材料，3个对称轴方向上的材料参数相同，则Ex=E =E₂，xy =v=x，$G _ { x y } = G _ { y z } = G _ { x z 0 }$

横观各向同性材料的柔度矩阵为[22]

$$
\begin{array} { r } { { \boldsymbol { C } } = \left[ \begin{array} { l l l l l l } { \frac { 1 } { E _ { x } } } & { - \frac { v _ { y } } { E _ { x } } } & { \frac { 1 } { E _ { x } } } & { 0 } & { 0 } & { 0 } \\ { - \frac { v _ { y } } { E _ { x } } } & { \frac { 1 } { E _ { x } } } & { - \frac { v _ { \mathrm { i } } } { E _ { z } } } & { 0 } & { 0 } & { 0 } \\ { - \frac { v _ { \mathrm { i } } } { E _ { x } } } & { \frac { 1 } { E _ { x } } } & { \frac { 1 } { E _ { x } } } & { 0 } & { 0 } & { 0 } \\ { \frac { 1 } { E _ { x } } } & { - \frac { v _ { \mathrm { i } } } { E _ { x } } } & { \frac { 1 } { E _ { x } } } & { 0 } & { 0 } & { 0 } \\ { 0 } & { 0 } & { 0 } & { \frac { 1 } { G _ { x } } } & { 0 } & { 0 } \\ { 0 } & { 0 } & { 0 } & { 0 } & { \frac { 1 } { G _ { z } } } & { 0 } \\ { 0 } & { 0 } & { 0 } & { 0 } & { \frac { 1 } { G _ { z } } } \end{array} \right] } \end{array}
$$

对横观各向同性材料和正交各向异性材料的柔度矩阵，令 $E _ { \mathrm { T } } = E _ { x } = E _ { y } , E _ { \mathrm { L } } = E _ { z }$ ,$\nu _ { \mathrm { { T } } } = \nu _ { x y } , \ \nu _ { \mathrm { { L } } } = \nu _ { x z } = \nu _ { y z } , \ G _ { \mathrm { { T } } } = G _ { x y } , \ G _ { \mathrm { { L } } } = G _ { y z } = G _ { x z }$ 可在正交各向异性材料模型中设置横观各向同性材料参数。

本节采所编写的应变硬化模型的程序和ANSYS带应变硬化模型的两种式对正交各向异性材料进蠕变变形计算分析，并对两种式的所得结果，以验证usercreep程序计算结果是否正确。

应变硬化模型的程序已在上节中详述，程序中的输输出变量均不变，现验证利usercreep程序能否对各向异性材料进蠕变计算分析。由于ANSYS主程序传到usercreep程序中为等效应，本节中将等效应保存到状态变量（程序中变量名为ustatev，程序会保存每个时间步的状态变量，同时能够输出）中，通过输出状态变量可察看每个时间步主程序传的等效应的数值。计算所采的有限元模型及应变硬化模型的参数数值与上一节相同，其中材料按照正交各向异性材料进设置，输Hill屈服准则相关参数： $R _ { x } = 0 . 9 5$ , $R _ { y } = 1 . 1 7$ , $R _ { z } = 0 . 9 7$ $R _ { x y } = 0 . 9 8$ , $R _ { y z } = 0 . 9 7$ , $R _ { z x } =$ 1.2，相关命令为“TB，HILL，1，1，6；TBDATA，1，0.95，1.17，0.97，0.98，0.97，1.2"。

计算设置与上节相同，状态变量输出的结果与式（2-6）计算得到的Hill等效应结果相同，均为 $7 0 4 . 2 3 \mathrm { M P a }$ 。图2-14为两种式计算得到的各个向蠕变应变，可以看出编写的应变硬化模型usercreep程序和ANSYS程序带模型，这两种式对正交各向异性材料进计算的结果样，说明对于定向结晶和单晶材料可usercreep子程序进蠕变计算分析。

![](images/c09623ae9bc9f3bf4640ac5a7ed6570ba278ce23bdcf33110f322e5926f2b110.jpg)  
图2-14 两种模型式对正交各向异性材料的蠕变计算结果对

# 2.3.3 Usercreep程序计算精度和时间的对分析

蠕变变形是在定温度和应作下材料与结构产的渐变塑性变形，采有限元法计算蠕变需对载荷步的时间步长进选择和控制。时间步长过长，计算的误差可能太大；而时间子步过小时，计算所需的子步数较多，蠕变计算中所消耗的物理时间（计算机时）可能会常长，特别是当单元数较多时，计算速度常缓慢。这就时间步长对计算精度的影响和计算耗时进行分析[14-16]。

# 2.3.3.1时间步长对计算精度的影响

先考察时间步长对计算精度的影响。采归化参数蠕变模型进计算，其中有限元模型如图2-12所，加载与边界条件同前节，计算过程中控制初始步长与最步长，开启动时间步选项，图2-15给出了各种步长条件对精度影响的计算结果。

![](images/5496bd5794dfdf99234631e7f2e4e8f00b2cf1703d1c860af26b1b5615f8cf97.jpg)  
图2-15 时间步长对计算精度的影响

图2-15（a）给出了最大步长为1，初始步长分别为0.01，0.0001，0.000001的计算结果，图中采用不同初始步长计算得到的计算点几乎重合，因而初始步长的大对计算精度影响不[14,16]。由计算的步记录来看，即使采不同的初始步长，由于通过自动时间步的调整，程序在计算过程中经过较短的时间后时间步长就以最大步长为1开始递增，除去前个步的步长不样，之后的步长均为1。

图2-15（b）给出了具有相同初始步长0.001，最步长分别为0.1和1的计算结果，可看到最步长为0.1的精度非常接近试验值，比最大步长为1的精度有幅提[14,16]。在计算蠕变第1阶段时可以采较的步长进计算，因为蠕变第1阶段的应变率比第2阶段大，并且随着蠕变变形，应在开始时松弛的幅值较，较的步长可保证较高的计算精度。随着蠕变计算的进，可适当增大时间步长，因为蠕变第2阶段近乎为直线，同时应松弛的幅值较，较大的步长可减少计算时间[14,16]。

# 2.3.3.2 计算耗时的对比分析

通过对不同格数的有限元模型进蠕变计算分析，以考察所编制的归化参数蠕变模型的子程序计算所需时间的长短。所建的长方体模型、尺寸与边界条件同前例，区别在于长方体模型的每条边上所均匀划分的格，建的3个不同单元数的有限元模型如下[14.16]：

(1) $L _ { n } \times W _ { \mathrm { n } } \times H _ { \mathrm { n } } = 5 \times 4 \times 3 = 6 0 ;$ (2) $L _ { \mathrm { n } } \times W _ { \mathrm { n } } \times H _ { \mathrm { n } } = 3 0 \times 2 0 \times 1 0 = 6 0 0 0$ ;(3) $L _ { n } \times W _ { n } \times H _ { n } = 5 0 \times 4 0 \times 2 0 = 4 0 0 0 0$ id上述 $L _ { n }$ , $W _ { n }$ , $H _ { n }$ 分别表实体模型长、宽、各边上的单元数。

采用计算机（配置为：CPU主频 $3 , 2 \mathrm { G H z }$ ，四核，内存8GB）进数值模拟计算，由不同单元数的有限元模型计算得到的蠕变曲线如图2-15所示，计算耗时见表2-11。

表2-11 不同蠕变模型和不同计算条件下的机时对[14,16]  

<table><tr><td rowspan=2 colspan=1>模型</td><td rowspan=2 colspan=1>单元数</td><td rowspan=2 colspan=1>最大子步</td><td rowspan=2 colspan=1>总子步数</td><td rowspan=1 colspan=2>耗时</td></tr><tr><td rowspan=1 colspan=1>前两阶段</td><td rowspan=1 colspan=1>第3阶段</td></tr><tr><td rowspan=3 colspan=1>程序自带应变硬化模型（非子程序）</td><td rowspan=1 colspan=1>60</td><td rowspan=1 colspan=1>4.5</td><td rowspan=1 colspan=1>97</td><td rowspan=1 colspan=1>&lt;1min</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>6000</td><td rowspan=1 colspan=1>4.5</td><td rowspan=1 colspan=1>97</td><td rowspan=1 colspan=1>3min</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>40000</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>1637</td><td rowspan=1 colspan=1>27min</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=3 colspan=1>所编写应变硬化模型（子程序)</td><td rowspan=1 colspan=1>60</td><td rowspan=1 colspan=1>4.5</td><td rowspan=1 colspan=1>97</td><td rowspan=1 colspan=1>&lt;1min</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>6000</td><td rowspan=1 colspan=1>4.5</td><td rowspan=1 colspan=1>97</td><td rowspan=1 colspan=1>3min</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>40000</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>1637</td><td rowspan=1 colspan=1>30min</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=3 colspan=1>归一化参数模型子程序</td><td rowspan=1 colspan=1>60</td><td rowspan=1 colspan=1>4.5</td><td rowspan=1 colspan=1>97</td><td rowspan=1 colspan=1>&lt;1min</td><td rowspan=1 colspan=1>2min</td></tr><tr><td rowspan=1 colspan=1>6000</td><td rowspan=1 colspan=1>4.5</td><td rowspan=1 colspan=1>97</td><td rowspan=1 colspan=1>10min</td><td rowspan=1 colspan=1>52min</td></tr><tr><td rowspan=1 colspan=1>40000</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>1637</td><td rowspan=1 colspan=1>78min</td><td rowspan=1 colspan=1>10h</td></tr></table>

对于归一化参数蠕变模型，由于有蠕变第3阶段，蠕变应变率较大，为保证程序收敛，般计算第3阶段蠕变的时间步长须较。因此，计算前两个阶段的蠕变变形耗时较少，第3阶段计算耗时所占的例较。当单元数为40000时完整地计算蠕变3个阶段需耗时 $1 0 \mathrm { { h } }$ ，其中前两个蠕变阶段耗时 $7 8 \mathrm { m i n }$ ，在可接受的范围内，可有效应用于实际工程结构设计中的蠕变分析。

# 2.3.4变载条件下的蠕变行为

采用有限元法进实际结构的蠕变计算分析时，蠕变应变是通过每个载荷子步计算得到的蠕变应变增量累计得到的，在每个步中需根据新的应变进应的更新，高应区会产应松弛效应。因此，应松弛效应与各步的蠕变应变的变化有关。

应（载荷）逐渐变化（减小）的蠕变为对应力松弛的结果影响较大，这属于变载条件下的蠕变，当前对于载荷发变化的处理（应、温度由（ $\sigma _ { 1 }$ , $T _ { 1 }$ ）变化到i $( \sigma _ { 2 } , \ T _ { 2 } )$ )，般采两种变载理论模型，本对比分析了两种理论模型计算结果的差异，并提出种新的理论模型，给出了不同的计算结果。

2.3.4.1时间硬化和应变硬化理论

种蠕变理论认为：当应、温度在 $t$ 时刻由（ $\sigma _ { 1 }$ , $T _ { \parallel }$ ）变化到（ $\sigma _ { 2 }$ , $T _ { 2 }$ ）之后，蠕变应变将按照在（ $\sigma _ { 2 }$ , $T _ { 2 }$ ）状态下的 $t$ 时刻后蠕变应变曲线变化。如图2-16所，在时刻 $t$ 发生变载， $t$ 时刻之后的曲线由（ $\sigma _ { 2 }$ , $T _ { 2 }$ ）状态下位于 $t$ 时刻之后的蠕变曲线沿纵向平移得到，称之为时间硬化理论[14,16]。另种蠕变理论认为：当应、温度在 $t$ 时刻由（ $\sigma _ { 1 }$ , $T _ { 1 }$ )d)变化到 $( \sigma _ { 2 } , \ T _ { 2 } )$ , $t$ 时刻之后的蠕变曲线由（ $\sigma _ { 2 }$ , $T _ { 2 }$ ）状态下与（ $\sigma _ { 1 }$ , $T _ { 1 }$ ）状态下产相同应变所对应时间之后的曲线沿横向平移得到，称之为应变硬化理论[14,16]，如图2-17所示。

![](images/05998e66517023f2469c184da3792d4697ae7f7370ada65af503b6482efae451.jpg)  
图2-16 时间硬化理论

![](images/8da4056775e7b8bea2244a820e102eb774d547147b146f4c687e63c4fe8f2f9a.jpg)  
图2-17 应变硬化理论

当前的有限元分析中，两种变载理论体现在所采的蠕变模型不同，例如，在通用有限元程序ANSYS中，应变硬化模型采用的是应变硬化理论。

应变硬化模型的表达式为

$$
\dot { \varepsilon } _ { c } = A \sigma ^ { n } \varepsilon _ { \mathrm { { c } } } ^ { m } \mathrm { e } ^ { - Q / R T }
$$

式中：A, $n$ , $m$ ，Q/R均为材料常数。

应变硬化模型的蠕变应变率是蠕变应变的函数 $\dot { \varepsilon } _ { \mathrm { ~ c ~ } } = f \left( \varepsilon _ { \mathrm { ~ c ~ } } , \ \sigma , \ T \right) ,$

假设 $0 \sim t$ 时刻之前的应力、温度均为 $( \sigma _ { 1 } , \ T _ { 1 } )$ ，则 $t$ 时刻已产的蠕变应变 $ { \varepsilon } _ { c } ^ { \prime }$ 由$0 \sim t$ 时刻之间的时间增量对应的应变增量的累加得到，蠕变应变曲线沿( $\sigma _ { 1 }$ , $T _ { \parallel }$ ）状态下的蠕变曲线变化。

当载荷在 $t$ 时刻变为 $\left( \sigma _ { 2 } , \ T _ { 2 } \right)$ ，下一个时间步长 $\Delta t$ 产生的蠕变应变增量为

$$
\Delta \varepsilon _ { \mathrm { c } } = \dot { \varepsilon } _ { \mathrm { c } } \Delta t = f ( \varepsilon _ { \mathrm { c } } ^ { t } , \sigma _ { 2 } , T _ { 2 } ) \Delta t
$$

时间步结束时的蠕变应变即为

$$
\varepsilon _ { \mathrm { c } } ^ { t + \Delta t } = \varepsilon _ { \mathrm { c } } ^ { t } + \Delta \varepsilon _ { \mathrm { c } } = \varepsilon _ { \mathrm { c } } ^ { t } + \dot { \varepsilon } _ { \mathrm { c } } \Delta t = \varepsilon _ { \mathrm { c } } ^ { t } + f \ \left( \varepsilon _ { \mathrm { c } } ^ { t } , \ \sigma _ { 2 } , \ T _ { 2 } \right) \Delta t
$$

$\Delta \varepsilon _ { \mathrm { c } }$ 对应于图2-17中由（ $\sigma _ { 2 }$ , $T _ { 2 }$ ）状态下的曲线计算得到的蠕变增量，而后每步的时间增量对应的蠕变应变增量均由（ $\sigma _ { 2 }$ , $T _ { 2 }$ ）状态下的曲线计算得到，因此变载后的蠕变曲线可看作（ $\sigma _ { 2 }$ , $T _ { 2 }$ ）状态下产应变 $\varepsilon _ { \mathrm { ~ c ~ } } ^ { \prime }$ 所对应的时间之后的曲线沿横向平移得到[14,16]

2.3.4.2 相对时间硬化（理论）模型

在时间硬化和应变硬化理论的基础上，本发展了种称为相对时间硬化的理论模型，如图2-18所示，令=\$ $\zeta = \frac { t } { t _ { \mathrm { c } , 1 } } = \frac { t _ { 2 } } { t _ { \mathrm { c } , 2 } }$ (id:) $t _ { \mathrm { c } , 1 }$ 和 $t _ { \mathrm { c } , 2 }$ 分别为（ $\sigma _ { 1 }$ , $T _ { 1 }$ ）和（ $\sigma _ { 2 }$ , $T _ { 2 }$ ）状态下(id:)的持久寿命，变载后的蠕变曲线则由( $\sigma _ { 2 }$ , $T _ { 2 }$ ）状态下在 $t _ { 2 }$ 时刻之后的蠕变曲线平移得到，相当于在时间归化坐标中，变载后曲线在 $\zeta$ 时刻沿纵向平移得到，为时间归化坐标中的时间硬化理论，因可称为相对时间硬化（理论）模型[14,16]。

![](images/4f102f02d46e0abf26c56192fddbfb30031a204de55f4ad55ddd90430ffc63d9.jpg)  
图2-18 相对时间硬化（理论）模型

相对时间硬化（理论）模型也可理解为等寿命理论，在（ $\sigma _ { 1 }$ , $T _ { \parallel }$ ）状态下 $t$ 时刻占持久寿命 $t _ { \mathrm { c } , 1 }$ 的例和（ $\sigma _ { 2 }$ , $T _ { 2 }$ ）状态下 $t _ { 2 }$ 时刻占持久寿命 $t _ { \mathrm { c } , 2 }$ 的例相同，相当于在两种状态下均消耗了相同百分的寿命，剩余寿命所占的百分也相同[14,16]。

在结构件的有限元计算分析中，蠕变变形处于前两个阶段较为安全，初期应力松弛幅度较。对于变载情况， $t$ 时刻后时间硬化理论与应变硬化理论对应（ $\sigma _ { 2 }$ , $T _ { 2 }$ ）状态下蠕变曲线的时间分别为 $t$ 和 $t _ { 2 } ^ { \prime }$ ，在前两个阶段蠕变变形中，蠕变应变率随着时间减，在相同时间增量 $\Delta t$ 下，两个时间所对应的蠕变应变增量 $\Delta \varepsilon$ 和 $\Delta \varepsilon ^ { \prime }$ ，有 $\Delta \varepsilon > \Delta \varepsilon ^ { \prime }$ ，就是说时间硬化理论对应的蠕变应变增量较应变硬化理论的[14.16]，因时间硬化理论的应松弛速度应变硬化理论的要快。对于实际构件采时间硬化理论数值模拟来说，以为构件更长时间作在较低应平，其实是偏危险的。相对时间硬化（理论）模型介于时间硬化理论和应变硬化理论之间，应松弛的速度也介于两者之间。故相对时间硬化（理论）模型和应变硬化理论的结果要偏于安全。

# 2.3.4.3 硬化理论模型在子程序中的实现

基于前章所发展的归化参数蠕变模型，编写了usercreep程序，并将其应于构件的有限元计算分析[14,16]，由于归化参数蠕变模型的蠕变应变率表达式在程序中是时间的函数： $\dot { \varepsilon } _ { \mathrm { ~ c ~ } } = f ( t )$ ，因此程序默认变载时采的是时间硬化理论。

对于应变硬化理论，通过得到主程序返回的应变值 $\varepsilon _ { \mathrm { c } }$ ，根据归一化参数蠕变模型的表达式，可迭代求得在（ $\sigma _ { 2 }$ , $T _ { 2 }$ ）状态下的蠕变应变 $\varepsilon _ { \mathrm { c } }$ 对应的时间 $t _ { 2 } ^ { \prime }$ 。迭代采对分法，已知当前的蠕变应变 $\varepsilon _ { \mathrm { c } }$ ，通过归一化参数蠕变模型的表达式 $\varepsilon _ { \mathrm { c } } = f ( t , \ \sigma , \ T$ ）可求得 $t _ { 2 } ^ { \prime }$ ，具体算法如下：

令 $\begin{array} { c l } { \varphi ( t ) } & { = f ( t , \ \sigma , \ T ) - \varepsilon _ { \mathrm { c } } = 0 } \end{array}$ ，定义两个时间 $t _ { 1 } , \ t _ { 2 }$ ，初始时令 $t _ { 1 } = 0 , t _ { 2 } = t _ { \mathrm { c } }$ ,满足 $\varphi ( t _ { 1 } ) < 0 , \varphi ( t _ { 2 } ) > 0$ ，当 $\varphi ( t _ { k } ) > 0$ ，则令 $t _ { 2 } = t _ { k }$ ，否则 $t _ { 1 } = t _ { k }$ ,令 $t _ { k + 1 } = { \frac { t _ { 1 } + t _ { 2 } } { 2 } }$ ，再判断 $\varphi ( t _ { k + 1 } )$ ）是否于0，进循环迭代。

对于相对时间硬化（理论）模型，令 $\zeta = \frac { t } { t _ { \mathrm { c } , 1 } } = \frac { t _ { 2 } } { t _ { \mathrm { c } , 2 } }$ 在程序中只需通过该比值关系得到 $t _ { 2 }$ 即可，但需使状态变量将上步计算得到的 $t _ { \mathrm { c } , 2 }$ 保存下来，同时由于主程序只传当前的时间（时间子步累加的时间），还需保存上一步计算得到的相对时间 $t _ { 2 }$ ，然后在每个步的计算结束时更新这两个状态变量[14,16]

# 2.3.5 应力松弛效应的计算分析示例

由于带孔平板存在应力集中，孔边应力大于其他周边的应力，孔边大应力区域的蠕变变形也较大，因而孔边存在明显的应力松弛效应，本节建立了带孔平板的三维有限元模型，利用3种硬化理论模型分别进行了蠕变计算分析，以考察应力集中点处的应力松弛规律。

图2-19所为建的带孔平板一半的有限元模型，下端限制 $y$ 方向位移，上端施加200MPa的拉应力。

采用上述3种理论模型分别对带孔平板进了蠕变变形分析，选取图2-19中平板上A， $B$ , $C$ , $D$ 这4个点作为参考点，各点的应力和应变的变化如图 $2 - 2 0 \sim$ 图2-23所，孔边应随着时间增加而降低，在刚开始时应力减小较快，随后应力减小速度变缓。

![](images/a97bfe7b420347cf3b94c04a1d76d2996c0ec3a2b18283816b947e17c7cf59eb.jpg)  
图2-19 带孔平板半的有限元模型

![](images/e7e3292d1c1796a55b385245d8ea3194d3612bf4b8f0501664e3677b932c8a41.jpg)  
图2-20 $A$ 点的应力和蠕变应变随时间的变化

![](images/1846429efa55f0da5dd8e255fc3c883fef5f1fade6adeb3be687b206491947ec.jpg)  
图2-21 $B$ 点的应力和蠕变应变随时间的变化

![](images/6df715a216b882512315d7b35bea7441c8cc6fecad3cfd251dd727f8c27b3f9f.jpg)  
图2-22 $C$ 点的应力和蠕变应变随时间的变化

![](images/5530ad44a0659f61823a50c28e5338beb0e1f5d0e27f517da80bdb8b9f08f572.jpg)  
图2-23 $D$ 点的应力和蠕变应变随时间的变化

随着时间的增加，各点的应力逐渐减小。高应力区的A和 $B$ 两点应力下降明显； $C$ 和 $D$ 两点的应也会随着变化，但变化幅度不，表明所发展的程序能够模拟应松弛效应，其中相对时间硬化（理论）模型和应变硬化理论的计算结果较为接近，时间硬化理论的应松弛速度较快，相对时间硬化（理论）模型的结果介于两者之间[14\~17]

对于实际应来说，时间硬化理论和应变硬化理论模型与试验的对比研究还较少，仅参考献[23对时间硬化理论和应变硬化理论与试验符合情况有所述及，中指出：般情况下根据应变硬化得到的预测结果和试验结果符合得较好，但该参考献并未给出与试验结果的对。由于不易获得应集中区域的应随时间的变化曲线，因而结构件应松弛为数值模拟的准确性尚未得到试验验证[14\~17]。然从数值计算结果来说，由应变硬化理论和相对时间硬化（理论）模型计算得到的高应力区的应力松弛幅度相对较，因与时间硬化理论相，应变硬化理论和相对时间硬化（理论）模型的计算结果相对偏于安全，可用于实际结构的蠕变分析。

在所发展的子程序中，需要进多次迭代求得应变硬化（理论）模型中的 $t _ { 2 } ^ { \prime }$ ，而相对时间硬化（理论）模型的 $t _ { 2 }$ 只需通过次求解计算。由于相对时间硬化（理论）模型和应变硬化理论的计算结果较为接近，因而模拟实际结构的应力松弛效应时可选用相对时间硬化（理论）模型替代应变硬化理论，这样可在定程度上提计算效率与计算精度。

# 2.4 涡轮盘与叶结构的蠕变分析

本节首先对涡轮盘和叶等实际温结构件的三维有限元模型进了静力分析，明确构件中应较大的区域，然后利所发展的一种能完整描述3个阶段蠕变变形的归化参数蠕变模型[13,14]编写的usercreep程序进蠕变分析，重点考察了涡轮盘和涡轮叶危险点的蠕变为，并分析蠕变变形和危险点区域的应松弛效应及其规律[15]。

# 2.4.1 涡轮盘的蠕变分析

2.4.1.1 涡轮盘有限元模型及材料参数

选取涡轮盘结构模型的1/72扇区建有限元模型，如图2-24所示。对比单扇区模型采八节点六体单元进有限元网格划分，单元数为19970，节点数为25065。

![](images/a4cbf376e4621f0d3793ca1e591a93a50598b9580417845a9195533f4b781a33.jpg)  
图2-24 涡轮盘1/72扇区的有限元模型

轮盘材料为直接时效GH4169，材料性能数据见表2-12。

# 表2-12直接时效GH4169的材料力学性能数据[21]

<table><tr><td rowspan=1 colspan=1>温度/℃</td><td rowspan=1 colspan=1>20</td><td rowspan=1 colspan=1>300</td><td rowspan=1 colspan=1>400</td><td rowspan=1 colspan=1>500</td><td rowspan=1 colspan=1>600</td><td rowspan=1 colspan=1>650</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>弹性模量/GPa</td><td rowspan=1 colspan=1>193.5</td><td rowspan=1 colspan=1>185.5</td><td rowspan=1 colspan=1>177.0</td><td rowspan=1 colspan=1>167.5</td><td rowspan=1 colspan=1>158.0</td><td rowspan=1 colspan=1>150.5</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>温度/℃</td><td rowspan=1 colspan=1>20</td><td rowspan=1 colspan=1>300</td><td rowspan=1 colspan=1>400</td><td rowspan=1 colspan=1>500</td><td rowspan=1 colspan=1>600</td><td rowspan=1 colspan=1>650</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>屈服应力/MPa</td><td rowspan=1 colspan=1>1320</td><td rowspan=1 colspan=1>1190</td><td rowspan=1 colspan=1>1210</td><td rowspan=1 colspan=1>1170</td><td rowspan=1 colspan=1>1130</td><td rowspan=1 colspan=1>1090</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>温度/℃</td><td rowspan=1 colspan=1>20</td><td rowspan=1 colspan=1>100</td><td rowspan=1 colspan=1>200</td><td rowspan=1 colspan=1>300</td><td rowspan=1 colspan=1>418</td><td rowspan=1 colspan=1>500</td><td rowspan=1 colspan=1>600</td><td rowspan=1 colspan=1>700</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>泊松比</td><td rowspan=1 colspan=1>0.30</td><td rowspan=1 colspan=1>0.30</td><td rowspan=1 colspan=1>0.30</td><td rowspan=1 colspan=1>0.30</td><td rowspan=1 colspan=1>0.31</td><td rowspan=1 colspan=1>0.32</td><td rowspan=1 colspan=1>0.32</td><td rowspan=1 colspan=1>0.33</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>温度/℃</td><td rowspan=1 colspan=1>100</td><td rowspan=1 colspan=1>200</td><td rowspan=1 colspan=1>300</td><td rowspan=1 colspan=1>400</td><td rowspan=1 colspan=1>500</td><td rowspan=1 colspan=1>600</td><td rowspan=1 colspan=1>700</td><td rowspan=1 colspan=1>800</td><td rowspan=1 colspan=1>900</td><td rowspan=1 colspan=1>1000</td></tr><tr><td rowspan=1 colspan=1>线膨胀系数/（10-5/℃)</td><td rowspan=1 colspan=1>1.18</td><td rowspan=1 colspan=1>1.30</td><td rowspan=1 colspan=1>1.35</td><td rowspan=1 colspan=1>1.41</td><td rowspan=1 colspan=1>1.44</td><td rowspan=1 colspan=1>1.48</td><td rowspan=1 colspan=1>1.54</td><td rowspan=1 colspan=1>1.70</td><td rowspan=1 colspan=1>1.84</td><td rowspan=1 colspan=1>1.87</td></tr><tr><td rowspan=1 colspan=1>温度/℃</td><td rowspan=1 colspan=1>100</td><td rowspan=1 colspan=1>200</td><td rowspan=1 colspan=1>300</td><td rowspan=1 colspan=1>400</td><td rowspan=1 colspan=1>500</td><td rowspan=1 colspan=1>600</td><td rowspan=1 colspan=1>700</td><td rowspan=1 colspan=1>800</td><td rowspan=1 colspan=1>900</td><td rowspan=1 colspan=1>1000</td></tr><tr><td rowspan=1 colspan=1>热导率/W/(m·℃)</td><td rowspan=1 colspan=1>14.7</td><td rowspan=1 colspan=1>15.9</td><td rowspan=1 colspan=1>17.8</td><td rowspan=1 colspan=1>18.3</td><td rowspan=1 colspan=1>19.6</td><td rowspan=1 colspan=1>21.2</td><td rowspan=1 colspan=1>22.8</td><td rowspan=1 colspan=1>23.6</td><td rowspan=1 colspan=1>27.6</td><td rowspan=1 colspan=1>30.4</td></tr><tr><td rowspan=1 colspan=1>密度/(kg/m³)</td><td rowspan=1 colspan=1>8240</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>熔点/℃</td><td rowspan=1 colspan=1>1290</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr></table>

2.4.1.2 涡轮盘结构静应力分析

先，采通有限元程序ANSYS对涡轮盘结构进静应与变形分析，计算中采八节点六体（solid185）单元，并选默认单元设置，所施加的与位移边界条件如下。

# （1）力边界条件

将涡轮转叶产的离等效为涡轮盘榫槽作上的法向压，在榫齿表面上施加压力边界条件，将叶片 $60 \%$ 的离施加于第1对榫齿的接触上，而将其 $40 \%$ 施加于第对榫齿的接触上，如图2-25所。涡轮叶的离计算如下。

涡轮叶材料为DZ125，材料质量密度为 $8 . 5 7 \times 1 0 ^ { 3 } \mathrm { k g / m } ^ { 3 }$ ；涡轮叶的体积为$1 7 8 0 5 . 2 0 \mathrm { m m } ^ { 3 }$ ；叶质所在的半径为 $3 1 8 . 6 7 \mathrm { m m }$

涡轮叶离 $F$

$$
F = m \omega ^ { 2 } r = 8 . 5 7 \times 1 0 ^ { 3 } \times 1 7 8 0 5 . 2 0 \times 1 0 ^ { - 9 } \times
$$

$$
( 1 4 6 7 5 \times 6 . 2 8 / 6 0 ) ^ { 2 } \times 3 1 8 . 6 7 \times 1 0 ^ { - 3 } = 1 1 4 8 3 7 . 1 3
$$

第1对榫齿的接触面积 $S _ { \imath }$

$$
S _ { 1 } = 2 \times 3 1 . 6 1 9 \times 1 . 7 9 6 = 1 1 3 . 5 7 5 ( \mathrm { m m } ^ { 2 } )
$$

第2对榫齿的接触积 $S _ { 2 }$

$$
S _ { 2 } = 2 \times 3 1 . 8 \times 1 . 6 1 8 = 1 0 2 . 9 0 5 ( \mathrm { m m } ^ { 2 } )
$$

第1对榫齿接触上的压应 $p _ { 1 }$

$$
p _ { 1 } = 0 . 6 F / S _ { 1 } = 0 . 6 \times 1 1 4 8 3 7 . 1 3 \div 1 1 3 . 5 7 5 \div \mathrm { c o s } 4 2 . 5 ^ { \circ } = 8 2 2 . 8 4 9 ( \mathrm { M P a } )
$$

第2对榫齿接触上的压应 $p _ { 2 }$

$$
p _ { 2 } = 0 . 4 F / S _ { 2 } = 0 . 4 \times 1 1 4 8 3 7 . 1 3 \div 1 0 2 . 9 0 5 \div \cos 4 2 . 5 ^ { \circ } = 6 0 5 . 4 4 5 ( \mathrm { ~ M P a } )
$$

(2）位移边界条件

先，由涡轮盘与封严盘组合状态下的轴对称模型计算得到涡轮盘结构相关部位的变形（位移）值，对涡轮盘结构1/72扇区三维模型施加位移边界条件时，取轴对称模型计算的位移结果或由其插值得到，所施加的位移边界条件如图2-25所示。

![](images/fa18b53a15b4837067403ac9dbffad5bd3f78652a86bc61b41f00d35ee59f21a.jpg)  
图2-25 涡轮盘结构1/72扇区模型的位移边界条件

(3）温度场

所施加的涡轮盘结构模型的温度场如图2-26所。

![](images/4789a7413fe188bd27e571d6924068c030aefb638cbd6004642e14246c99eebf.jpg)  
图2-26 涡轮盘结构的温度分布（温度单位： $\mathcal { C }$ )

(4）其他边界条件

给定涡轮盘前、后两个盘腔的气体压力值，分别为 $1 . 2 6 2 \mathrm { M P a }$ 和 $0 . 5 0 7 \mathrm { M P a }$ ，以及转速和扇区循环对称模型两侧的边界条件。为了避免出现周向刚体转动，约束涡轮盘与后轴颈连接处的周向位移。

按照上述设置的力与位移边界条件及温度场进静分析求解，计算得到的应分布如图2-27\~图2-29所，径向与轴向的变形（位移）如图2-30所示。

![](images/788ef1db128d7f0af8b6a986f468a6f8fb20b6c75a812ba094ac7a7b5337691c.jpg)  
图2-27 涡轮盘径向应分布

提取涡轮盘径向与周向应，以及第主应和VonMises等效应的最值，各危险部位及其应计算结果见表2-13。周向应最点出现在盘处，VonMises等效应最点出现在螺栓孔边，径向应力和第一主应最大点均出现在轮缘和辐板的过渡区域。

![](images/341a66e8ab4f6e87cffce05da4c3a8981f9d9d4ad080876794a01a94703e5e36.jpg)  
图2-28 涡轮盘周向应与轴向应分布

![](images/078932947b97eeef75acf142cc7cd09ebe49599567860eb9b0671b0376bd83b9.jpg)  
图2-29 涡轮盘第主应和VonMises等效应分布

![](images/f2e9e41dc593ed9a2b2921e17b1d57b30298a9ff67976f569eedbaa952700f03.jpg)  
图2-30 涡轮盘径向与轴向变形（位移）分布

表2-13 涡轮盘危险点及应力计算结果  
MPa   

<table><tr><td rowspan=1 colspan=1>危险部位</td><td rowspan=1 colspan=1>温度/℃</td><td rowspan=1 colspan=1>径向应力</td><td rowspan=1 colspan=1>周向应力</td><td rowspan=1 colspan=1>第一主应力</td><td rowspan=1 colspan=1>等效应力</td></tr><tr><td rowspan=1 colspan=1>盘心</td><td rowspan=1 colspan=1>482.0</td><td rowspan=1 colspan=1>11.1</td><td rowspan=1 colspan=1>953.6</td><td rowspan=1 colspan=1>952.4</td><td rowspan=1 colspan=1>1110.6</td></tr><tr><td rowspan=1 colspan=1>螺栓孔边</td><td rowspan=1 colspan=1>613.5</td><td rowspan=1 colspan=1>1117.8</td><td rowspan=1 colspan=1>61.2</td><td rowspan=1 colspan=1>1152.1</td><td rowspan=1 colspan=1>1133.4</td></tr><tr><td rowspan=1 colspan=1>轮缘辐板过渡区</td><td rowspan=1 colspan=1>561.6</td><td rowspan=1 colspan=1>1170.4</td><td rowspan=1 colspan=1>758.1</td><td rowspan=1 colspan=1>1192.2</td><td rowspan=1 colspan=1>1025.3</td></tr></table>

2.4.1.3涡轮盘材料的蠕变模型参数及计算中所采取的假设

进涡轮盘蠕变及应松弛效应的计算分析时，先进涡轮盘模型的静应分析，以确定应危险点，这重点考察了危险点处的蠕变变形及应松弛情况。所施加的与位移边界条件与静分析的相同，即在涡轮盘模型的安装边处施加周向和轴向位移，与涡轮叶离心载荷等效的榫齿接触上的压应、轮盘转速，以及其温度场等。根据计算分析结果，盘、螺栓孔边、盘缘辐板过渡处的应较，因重点考察了这3处的蠕变变形与应松弛效应。

蠕变分析中采2.2节所发展的基于归化参数的蠕变模型，利所发展的usercreep程序进计算。基于归化参数的蠕变模型中的常数 $a _ { i }$ , $b _ { i }$ , $c _ { i }$ , $d _ { i }$ $i = 1$ ,2,3，4,5）采2.2节中拟合得到的数值；参数 $\eta _ { i }$ （ $i = 1$ ，2，3，4，5）是温度和应力的函数，且温度和应力分别对材料的熔点和屈服应力进了归化，而屈服应认为是温度的函数，利式（2-15）对材料试验数据进拟合，可以得到 $f _ { 1 } = 1 3 9 2 . 3 0$ , $f _ { 2 } = - 5 4 9 . 3 8$ 表2-14中的第3列为代 $f _ { 1 }$ 和 $f _ { 2 }$ 的值计算得到的屈服应，“误差”为拟合后的屈服应力与屈服应力的差值相对屈服应力的百分比，误差最大为 $4 , 5 \%$ ,在可接受的范围内。

表2-14涡轮盘材料的屈服应力随温度的变化  

<table><tr><td rowspan=1 colspan=1>温度/℃</td><td rowspan=1 colspan=1>屈服应力/MPa</td><td rowspan=1 colspan=1>拟合后的屈服应力/MPa</td><td rowspan=1 colspan=1>误差/%</td></tr><tr><td rowspan=1 colspan=1>20</td><td rowspan=1 colspan=1>1320</td><td rowspan=1 colspan=1>1289.270</td><td rowspan=1 colspan=1>2.3</td></tr><tr><td rowspan=1 colspan=1>300</td><td rowspan=1 colspan=1>1190</td><td rowspan=1 colspan=1>1190.862</td><td rowspan=1 colspan=1>0.072</td></tr><tr><td rowspan=1 colspan=1>400</td><td rowspan=1 colspan=1>1210</td><td rowspan=1 colspan=1>1155.717</td><td rowspan=1 colspan=1>4.5</td></tr><tr><td rowspan=1 colspan=1>500</td><td rowspan=1 colspan=1>1170</td><td rowspan=1 colspan=1>1120.571</td><td rowspan=1 colspan=1>4.2</td></tr><tr><td rowspan=1 colspan=1>600</td><td rowspan=1 colspan=1>1130</td><td rowspan=1 colspan=1>1085.425</td><td rowspan=1 colspan=1>3.9</td></tr><tr><td rowspan=1 colspan=1>650</td><td rowspan=1 colspan=1>1090</td><td rowspan=1 colspan=1>1067.852</td><td rowspan=1 colspan=1>2.0</td></tr></table>

利用所发展的基于归一化参数的蠕变模型及其用户子程序对涡轮盘结构进行了蠕变分析，计算载荷步的设置见表2-15。蠕变计算中的时间历程为不同时间间隔的累加，按2.3节中的方法，合理地确定子步步长，并设置载荷步，以及选用合适的单元网格数量。由于应在初期松弛较快，而经历段时间的蠕变变形之后松弛速度降低，应基本“稳定”。因此，载荷步的设置是取前10h的最大步长均为0.1h，之后的最步长为1h。

表2-15 计算中所设置的时间步长  

<table><tr><td rowspan=1 colspan=1>载荷步结束时间/h</td><td rowspan=1 colspan=1>初始步长/h</td><td rowspan=1 colspan=1>最大步长/h</td></tr><tr><td rowspan=1 colspan=1>1×10-6</td><td rowspan=1 colspan=1>$1×10-6</td><td rowspan=1 colspan=1>$1×10-6</td></tr><tr><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>$1×10-5</td><td rowspan=1 colspan=1>0.1</td></tr><tr><td rowspan=1 colspan=1>60</td><td rowspan=1 colspan=1>0.001</td><td rowspan=1 colspan=1>1</td></tr><tr><td rowspan=1 colspan=1>300</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>1</td></tr></table>

蠕变分析中使用的蠕变模型参数为2.2节拟合得到的数值，按照蠕变模型的物理意义进拟合，具体的参数值详见表2-4。由于材料数据册中所给的蠕变试验温度范围和应力范围均较窄，而实际构件的温度和应力范围很宽，需进行内插和外推。因此，对于超过蠕变试验范围的数据需要做出合理的假设

$$
\sigma _ { \mathrm { 1 } } = { \bigg ( } h _ { \mathrm { 1 } } { \frac { T } { T _ { \mathrm { m } } } } + h _ { \mathrm { 2 } } { \bigg ) } \sigma _ { \mathrm { 0 . 2 } } , \sigma _ { \mathrm { h } } = { \bigg ( } h _ { \mathrm { 3 } } { \frac { T } { T _ { \mathrm { m } } } } + h _ { \mathrm { 4 } } { \bigg ) } \sigma _ { \mathrm { 0 . 2 } }
$$

当应力 $\sigma < \sigma _ { 1 }$ ，可认为该应和温度下不产蠕变；当 $\sigma > \sigma _ { \mathrm { h } }$ ，则认为此时产生的蠕变应变与（ $T , \ \sigma _ { \mathrm { h } } )$ ）状态下对应的蠕变应变相同，在程序中可令其蠕变参数一致，产生的蠕变应变即为（ $T$ , $\sigma _ { \mathrm { ~ b ~ } }$ ）状态下对应的蠕变应变。若 $h _ { 1 }$ ,…, $h _ { 4 }$ 为0，则程序中不包含该假设。这种假设有两个的便利之处：是避免外推的参数值误差过或参数值失去意义，如 $\eta _ { 5 } < 1$ ；是避免由蠕变参数计算得到的某一应值下的蠕变应变率过大，致使程序计算难以收敛。 9

本节所计算的涡轮盘温度范围为： $4 7 5 . 5 \sim 6 7 1 . 0 ^ { \circ } \mathrm { C }$ ，最大等效应力 $1 1 3 3 . 4 \mathrm { M P a }$ 。为了避免程序在外推参数值时发异常，因而在蠕变分析中，当等效应于 $4 0 0 \mathrm { M P a }$ 时，认为不产生蠕变应变，当应力大于 $8 0 0 \mathrm { M P a }$ 时，产生的蠕变应变是该温度下应力为$8 0 0 \mathrm { M P a }$ 时对应的蠕变应变。由于高应力区的应力松弛很快，在较短时间内就会降低到$8 0 0 \mathrm { M P a }$ 以下，因而这里所做的假设是可行的。

# 2.4.1.4涡轮盘蠕变计算结果分析

涡轮盘蠕变分析中共计算了424个时间步，计算耗时6h左右。图2-31为轮盘不同时刻的VonMises等效应分布，分别给出了 $1 \times 1 0 ^ { - 6 } \mathrm { h }$ , $1 0 \mathrm { { h } }$ , $1 0 0 \mathrm { h }$ 和 $3 0 0 \mathrm { h }$ 蠕变后涡轮盘的等效应力分布，图2-32\~图2-34为 $3 0 0 \mathrm { h }$ 时轮盘的径向应力、周向应力和轴向应的分布。计算中从第1个时间步就开始计算蠕变，因读取第1个时间步 $t \ = 1 \times$ $1 0 ~ ^ { - 6 } \mathrm { h }$ 的结果，各向的应力与静分析结果相差不，绝对数值稍低一些，由图2-31（a）可以看出，其计算过程是可信的。

由于轮盘结构上的蠕变应变不均匀，应力将重新分布，较大的应力部位出现了应力松弛现象。对比经蠕变后不同时刻的轮盘等效应力分布，总体上，其应力分布因蠕变而更加均匀，除盘心处以外，基本上不再出现局部应力很大的区域，特别是螺栓孔边及盘缘与辐板的过渡区等局部应力较大的区域，经过一段时间的蠕变变形后，其应分布变得较为均匀[14.16]。

![](images/85174754c7e86d58fbfd1d98c7533e3af8fc79c89208402ce1f16ee8dd7c7499.jpg)  
图2-31 涡轮盘经蠕变后不同时刻的等效应分布

![](images/c6cf45c08e74ef651fed89eda6a913477601639b79bb47cd066e16fc01713244.jpg)  
图2-32 涡轮盘 $3 0 0 \mathrm { { h } }$ 时的径向应力分布

![](images/3fb175178b6d79daf80eb68ea2772f7926d150cb560bf7f490f50a4af3799a2d.jpg)  
图2-33 涡轮盘 $3 0 0 \mathrm { h }$ 时的周向应力分布

![](images/f46cdb6521d9d9c9fe18a58b2dd33ecfaa62248603ccd31d0a320bf52b212a0e.jpg)  
图2-34 涡轮盘 $3 0 0 \mathrm { h }$ 时的轴向应力分布

将盘心、螺栓孔边以及盘缘辐板过渡区3处作为考察点，提取这3处的应力和蠕变应变随时间的变化，如图2-35\~图2-37所示。

![](images/4b444f8b7afa049b0e40cf6506fff30e7814b1eaea79895cf6c64b78fa0975ec.jpg)  
图2-35 涡轮盘盘处应和蠕变应变随时间的变化

![](images/c3186fce420f4272de78baaad87681852668e8a380845a66b9ba2c6a070e62dc.jpg)  
图2-36 涡轮盘螺栓孔边处应和蠕变应变随时间的变化

![](images/43ba48dca19f7bdd1b745a84dde51b23a75284b3a1d5f08912d0892da20a5214.jpg)  
图2-37 涡轮盘轮缘辐板过渡区应和蠕变应变随时间的变化

盘心、螺栓孔边和盘缘辐板过渡区的温度分别为 $4 8 2 . 0 \mathrm { { ^ { \circ } C } }$ , $6 1 3 . 4 \mathrm { { } ^ { \circ } C }$ 和561. $6 \%$ ，这3处当中，螺栓孔边的温度最高，同时等效应力也最大，其蠕变应变也会大一些，因而该处的应力松弛速度比其他两处的更快。轮盘辐板过渡区的应力松弛大小次之。盘心处因温度较低，其蠕变变形较小，因而应力松弛的幅度也较小。然而，由于该盘心区域长时间处于应力状态下，与其他区域相比可能更加危险，在轮盘结构设计中对此应予以重点关注[14,16]。

图2-38给出了轮盘经过 $3 0 0 \mathrm { h }$ 蠕变后得到的等效蠕变应变分布。由图2-38（b）中可以看出，蠕变应变最大点出现在轮盘第一对榫齿的接触上，蠕变应变最大点的等效应与蠕变应变随时间的变化如图2-39所示。由于该点的蠕变应变，因而应松弛的幅度大，松弛的速度也比较快。

# 2.4.2 涡轮转子叶的蠕变分析

# 2.4.2.1涡轮转子叶片的有限元模型及材料参数

对涡轮转叶建的有限元模型如图2-40所，其中选节点六体单元进格划分，共9759个单元，12982个节点。

![](images/3133ab620f6c67580265fb852a045b2ace572b4ef63d6975bacccb083184eec3.jpg)  
图2-38 涡轮盘300h时后的等效蠕变应变分布

![](images/3cf5fdd56ea53eaafc9c7fb8f66357c362039ae7c83aa17ff5b035b7180b953d.jpg)  
图2-39 涡轮盘蠕变应变最大点处的等效应和蠕变应变随时间的变化

![](images/0330530ec7579d6bffbe8d9d50eec02b4c254f186c5a5dcd12f50297e96fa018.jpg)  
图2-40 涡轮转叶的有限元模型

涡轮转叶的材料为铸造合K417G，其材料学性能参数见表2-16。这认为叶材料是各向同性的，且3个向上的弹性模量、泊松比、剪切模量以及线膨胀系数相同： $E _ { x } = E _ { y } = E _ { z } , \psi _ { x y } = \upsilon _ { y z } = \upsilon _ { x z } , G _ { x y } = G _ { y z } = G _ { x z } , \alpha _ { x } = \alpha _ { y } = \alpha _ { z } \circ$

表2-16K417G合金的材料数据[21]  

<table><tr><td rowspan=1 colspan=1>温度/℃</td><td rowspan=1 colspan=1>20</td><td rowspan=1 colspan=1>500</td><td rowspan=1 colspan=1>600</td><td rowspan=1 colspan=1>700</td><td rowspan=1 colspan=1>800</td><td rowspan=1 colspan=1>900</td><td rowspan=1 colspan=1>950</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>弹性模量/GPa</td><td rowspan=1 colspan=1>207.5</td><td rowspan=1 colspan=1>168.5</td><td rowspan=1 colspan=1>158.0</td><td rowspan=1 colspan=1>149.5</td><td rowspan=1 colspan=1>140.0</td><td rowspan=1 colspan=1>130.5</td><td rowspan=1 colspan=1>127.5</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>温度/℃</td><td rowspan=1 colspan=1>20</td><td rowspan=1 colspan=1>500</td><td rowspan=1 colspan=1>600</td><td rowspan=1 colspan=1>700</td><td rowspan=1 colspan=1>800</td><td rowspan=1 colspan=1>900</td><td rowspan=1 colspan=1>950</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>屈服应力/MPa</td><td rowspan=1 colspan=1>775</td><td rowspan=1 colspan=1>815</td><td rowspan=1 colspan=1>790</td><td rowspan=1 colspan=1>795</td><td rowspan=1 colspan=1>820</td><td rowspan=1 colspan=1>580</td><td rowspan=1 colspan=1>470</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>温度/℃</td><td rowspan=1 colspan=1>20</td><td rowspan=1 colspan=1>100</td><td rowspan=1 colspan=1>200</td><td rowspan=1 colspan=1>300</td><td rowspan=1 colspan=1>400</td><td rowspan=1 colspan=1>500</td><td rowspan=1 colspan=1>600</td><td rowspan=1 colspan=1>700</td><td rowspan=1 colspan=1>800</td><td rowspan=1 colspan=1>900</td></tr><tr><td rowspan=1 colspan=1>泊松比</td><td rowspan=1 colspan=1>0.26</td><td rowspan=1 colspan=1>0.27</td><td rowspan=1 colspan=1>0.27</td><td rowspan=1 colspan=1>0.28</td><td rowspan=1 colspan=1>0.27</td><td rowspan=1 colspan=1>0.27</td><td rowspan=1 colspan=1>0.28</td><td rowspan=1 colspan=1>0.29</td><td rowspan=1 colspan=1>0.3</td><td rowspan=1 colspan=1>0.32</td></tr><tr><td rowspan=1 colspan=1>温度/℃</td><td rowspan=1 colspan=1>100</td><td rowspan=1 colspan=1>200</td><td rowspan=1 colspan=1>300</td><td rowspan=1 colspan=1>400</td><td rowspan=1 colspan=1>500</td><td rowspan=1 colspan=1>600</td><td rowspan=1 colspan=1>700</td><td rowspan=1 colspan=1>800</td><td rowspan=1 colspan=1>900</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>线膨胀系数/(10-6/℃）</td><td rowspan=1 colspan=1>10.71</td><td rowspan=1 colspan=1>11.89</td><td rowspan=1 colspan=1>12.92</td><td rowspan=1 colspan=1>13.51</td><td rowspan=1 colspan=1>14.03</td><td rowspan=1 colspan=1>14.24</td><td rowspan=1 colspan=1>14.51</td><td rowspan=1 colspan=1>14.77</td><td rowspan=1 colspan=1>15.16</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>温度/℃</td><td rowspan=1 colspan=1>200</td><td rowspan=1 colspan=1>300</td><td rowspan=1 colspan=1>400</td><td rowspan=1 colspan=1>500</td><td rowspan=1 colspan=1>600</td><td rowspan=1 colspan=1>700</td><td rowspan=1 colspan=1>800</td><td rowspan=1 colspan=1>900</td><td rowspan=1 colspan=1>1000</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>热导率/(W/(m·℃))</td><td rowspan=1 colspan=1>13.86</td><td rowspan=1 colspan=1>14.40</td><td rowspan=1 colspan=1>15.28</td><td rowspan=1 colspan=1>16.83</td><td rowspan=1 colspan=1>18.80</td><td rowspan=1 colspan=1>21.35</td><td rowspan=1 colspan=1>23.86</td><td rowspan=1 colspan=1>24.91</td><td rowspan=1 colspan=1>25.25</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>密度/(kg/m³)</td><td rowspan=1 colspan=1>7850</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>≥</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>熔点/℃</td><td rowspan=1 colspan=1>1300</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr></table>

# 2.4.2.2 涡轮转子叶片的静应力分析

先，采通有限元程序ANSYS对涡轮转叶模型进静分析，计算中采用的是八节点六面体（solid185）单元，选用默认单元设置。

所分析的涡轮转叶共有3对榫齿，在榫齿上施加的位移边界条件为：约束第1对榫齿接触面上的法向位移；在第2和第3对榫齿的接触面上施加压应力，每对榫齿所承受的压应力的径向分量之和为整个叶离心力的 $30 \%$ ，即第1对榫齿承受叶的$40 \%$ 离心力。

涡轮叶材料的质量密度为 $7 . 8 5 \times 1 0 ^ { 3 } \mathrm { k g / m } ^ { 3 }$ ；涡轮叶的体积为 $1 3 5 4 4 . 8 8 \mathrm { m m } ^ { 3 }$ ；质所在半径为 $3 1 4 . 3 0 \mathrm { m m }$

涡轮叶的离 $F$

$$
F = m \omega ^ { 2 } r = 7 . 8 5 \times 1 0 ^ { 3 } \times 1 3 5 4 4 . 8 8 \times 1 0 ^ { - 9 } \times
$$

$$
( 1 0 9 3 5 \times 6 . 2 8 / 6 0 ) ^ { 2 } \times 3 1 4 . 3 0 \times 1 0 ^ { - 3 } = 4 3 8 1 5 . 6 4
$$

叶榫齿接触面的表面积 $S$

$$
S = 2 \times 2 0 \times 1 . 5 1 = 6 0 . 4 0 ( \ m m ^ { 2 } )
$$

叶榫齿接触表压 $p$

$$
p = F \times 0 . 3 \div S \div \mathrm { c o s } 3 7 . 5 1 ^ { \circ } =
$$

43815.64×0.33÷60.4÷cos37.51°=274.311(MPa)

涡轮转叶的第3对榫齿比第2对榫齿要长一些，伸长段于轴向定位，因而对第2对和第3对榫齿在相同的轴向长度上施加相同的压应 $2 7 4 . 3 1 1 \mathrm { M P a }$ ，同时对第3对榫齿伸长段上一点的轴向位移进约束，所施加的与位移边界条件如图2-41所。

计算中，涡轮转叶模型的温度分布如图2–42所。

![](images/95437c2c61a30e339bbeb905a659ba1be889f8f046151159786291875defa067.jpg)  
图2-41 涡轮转叶所施加的与位移边界条件

![](images/1a03137f6e070a98cbdc6a77894426bb8d1be654e43e214256e0969caa16b72a.jpg)  
图2-42 涡轮转子叶的温度分布（温度单位： $\mathcal { C }$ )

按上述设置的边界条件对涡轮转子叶片进行静应力求解。由于榫头处所施加的边界条件将使榫头部位的局部应力过大，因而这里仅提取叶身及叶冠的静力分析结果，其径向应力、第一主应力和等效应力的分布如图2-43～图2-45所示，径向位移分布如图2-46所示。

![](images/1571affd3fa6291aa754d8bd7b9a641ad208d0a14ee9200e360db98e280be844.jpg)  
图2-43 涡轮转叶径向应分布

![](images/0b873715400ec6fa20fac9b7781423d36734b7179fb7c242a54ccbd3a98f0cc0.jpg)  
图2-44 涡轮转叶第主应分布

![](images/a8e7ea1b5b1185d6c0137c656c653eefcb777ca299b12acb1e0f610d14806a9d.jpg)  
图2-45 涡轮转叶VonMises等效应分布

![](images/60dfe90c07acdcee5d2f87fc150f8601ee0484a14c5a7db495b4c91dbbe33298.jpg)  
图2-46 涡轮转叶径向位移分布

由图 $2 - 4 3 \sim$ 图2-46中可以看出，叶根部附近的径向应、第主应和VonMises等效应力均较大，其最大值分别为 $4 1 6 . 2 9 5 \mathrm { { M P a } }$ ,417.446MPa，412.207MPa;叶冠处的最大径向变形（位移）为 $1 . 7 2 6 \mathrm { m m }$

2.4.2.3涡轮转子叶片材料蠕变模型中的参数及计算中所采取的假设

叶的材料选为K417G，其蠕变数据取参考献[21，不同温度和应下的蠕变曲线如图2-47所示。

![](images/19c9d0782b57d241444114feed3b914fbca5b1fd266a7bda48981a8fff9f2a72.jpg)  
图2-47 K417G合的蠕变曲线[21]

按所发展的基于归化参数的蠕变模型及其材料参数的识别法对K417G材料的蠕变曲线进拟合，得到的各参数的材料系数值见表2-17，拟合结果的对如图2-48所。

表2-17 K417G材料拟合得到的蠕变模型中的系数值  

<table><tr><td rowspan=2 colspan=1>参数</td><td rowspan=1 colspan=4>系数</td></tr><tr><td rowspan=1 colspan=1>ai</td><td rowspan=1 colspan=1>bi</td><td rowspan=1 colspan=1>Ci</td><td rowspan=1 colspan=1>di</td></tr><tr><td rowspan=1 colspan=1>n1</td><td rowspan=1 colspan=1>-12.91</td><td rowspan=1 colspan=1>12.37</td><td rowspan=1 colspan=1>17.10</td><td rowspan=1 colspan=1>-22.09</td></tr><tr><td rowspan=1 colspan=1>$72</td><td rowspan=1 colspan=1>21.13</td><td rowspan=1 colspan=1>-28.73</td><td rowspan=1 colspan=1>-31.09</td><td rowspan=1 colspan=1>42.62</td></tr><tr><td rowspan=1 colspan=1>$73</td><td rowspan=1 colspan=1>338.18</td><td rowspan=1 colspan=1>-451.07</td><td rowspan=1 colspan=1>-509.30</td><td rowspan=1 colspan=1>670.64</td></tr><tr><td rowspan=1 colspan=1>74</td><td rowspan=1 colspan=1>-8.66</td><td rowspan=1 colspan=1>15.03</td><td rowspan=1 colspan=1>23.87</td><td rowspan=1 colspan=1>-29.71</td></tr><tr><td rowspan=1 colspan=1>75</td><td rowspan=1 colspan=1>-5.06</td><td rowspan=1 colspan=1>6.51</td><td rowspan=1 colspan=1>0.79</td><td rowspan=1 colspan=1>0.96</td></tr></table>

![](images/8248ac30f381217a79ace78d3949d3866fa39c7eca301e518e6f6bddf11b63dc.jpg)  
图2-48 K417G材料不同温度和应下蠕变曲线的拟合结果对

K417G材料的熔点为 $1 3 0 0 \mathrm { { ^ \circ C } }$ 。屈服应力与温度之间关系可认为由式（2-15）确定，对材料数据进行拟合可以得到： $f _ { 1 } = 9 3 9 . 4 6$ , $\cdot f _ { 2 } = - 3 7 7 . 4 4$ 。持久寿命与应、温度之间的关系采用持久寿命程，见式（2-16），材料数据册[21]中给出了持久程中的系数值：$g _ { 1 } = - 1 6 . 3 7$ , $g _ { 2 } = 5 9 7 . 5 0$ , $g _ { 3 } = 5 0 6 6 4 . 2 2$ , $g _ { 4 } = - 1 7 2 2 8 . 1 0$ , $g _ { 5 } = 1 2 3 3 . 3 3$

对于各向异性材料的蠕变分析需提供式（2-7）中的各个向的屈服应比，由于K417G在3个向上的材料性能相同，并且材料数据册中未给出该材料的剪切强度，因其各个向的屈服应取为 $R _ { x } = 1$ , $R _ { y } = 1$ , $R _ { z } ~ = ~ 1$ , $R _ { x y } = 1$ , $R _ { y z } = 1$ ,$R _ { z x } = 1$ 。计算中由于材料数据册中所给出的蠕变试验温度和应的范围均较窄，叶的温度和应范围很宽，需进外推和内插，为了避免参数值外推不合理，这对参数做出如下的限定： $\eta _ { 1 } { \leqslant } 0 . 0 1$ , $\eta _ { 2 } { \leqslant } 0 . 0 5$ , $\eta _ { 3 } { \leqslant } 0 . 0 5$ , $\eta _ { 4 } \leqslant 1 0 0$ , $\eta _ { 5 } \geqslant 1$

# 2.4.2.4 涡轮转子叶片蠕变计算结果分析

采所发展的基于归化参数的蠕变模型及其户程序[14,15]对涡轮转叶结构进了蠕变分析。提取不同时刻涡轮转叶的径向应分布，如图2-49所，分别给出了 $1 \times 1 0 ^ { - 6 } \mathrm { h }$ , $1 0 \mathrm { h }$ , $1 0 0 \mathrm { h }$ 蠕变后的涡轮转叶的径向应分布。由于产的蠕变应变不均匀，叶上的应力将重新分布，由不同时刻涡轮转子叶的径向应分布可以看出，叶身根部附近的最大应力逐渐减小，应力分布趋于更为均匀。图2-50为涡轮转子叶片 $1 0 0 \mathrm { h }$ 时的径向蠕变应变分布。蠕变应变的大小与温度和应力有关，由于叶身中部的温度较，应力较低，而叶身根部的应较，产生最大蠕变应变的部位约在1/3叶高附近。

![](images/704a74fbc78b9619c7f91d5c92abc318852f2e14e7d519965cdd320a12026fbc.jpg)  
图2-49 不同时刻叶经蠕变后的径向应分布

![](images/af291ad3ccd2adbbc14846f2fb115050d6f0566cb8a5cb0fd695a7c30066e4c5.jpg)  
图2-50 涡轮转叶100h时的等效蠕变应变分布

图2-51给出了叶根最应处的径向应和蠕变应变随时间的变化，随着时间增加，应力逐渐松弛，但因该点温度较低，蠕变应变小，应力松弛幅度相对较小。

![](images/304682f106c0fb060cb4596a2175e7c4f0c2cdc173b44bd60a6c170cd17de060.jpg)  
图2-51 涡轮叶叶根部径向应与径向蠕变应变随时间的变化

图2-52给出了叶身中部蠕变应变最大点处的径向应力和蠕变应变随时间的变化。因叶身中部温度，蠕变应变较，应力松弛相对较为明显，刚开始时应松弛速度较快，随后逐渐变得平缓。

![](images/e1caccc8400c66084bce0ace26c5e4b27c6df0bf9533571229aa3a2a6e7562ac.jpg)  
图2-52 叶中部蠕变应变最点处的径向应与径向蠕变应变随时间的变化

图2-53给出了涡轮转叶 $1 0 0 \mathrm { h }$ 时的径向位移分布。由于蠕变变形，叶片径向位移随之增加，叶冠处径向位移最大，由 $1 . 7 2 6 \mathrm { m m }$ 增至 $1 . 9 4 5 \mathrm { m m }$ 。径向变形的增加可能导致叶冠与机匣碰磨，因在涡轮转叶的结构设计中应考虑因蠕变使径向变形增加而带来的问题。

![](images/629efbf1763425e066f5870471dcb5225ce0f23ca0c9a4efeafca7d4480304e6.jpg)  
图2-53 涡轮转叶经 $1 0 0 \mathrm { { h } }$ 蠕变后的径向位移（变形）分布

# 2.5小结

本章针对程中常的蠕变模型不能模拟蠕变第3阶段的问题，发展了种能够完整描述蠕变3个阶段变形的模型，结论如下。

（1）基于归化参数发展了种蠕变模型。它基于量纲参数，其中在归化的时间坐标下采用简单的三项幂函数分别描述蠕变的3个阶段。该模型以归一化时间（对持久断裂时间归一）为变量，以归一化的应力和温度（分别对屈服应力和熔点温度归）为参数，能够完整地描述蠕变变形3个阶段的特征。模型中的参数为应和温度的函数，因而能够模拟任意温度和应力载荷下的蠕变变形，且具有内插和外推的能力。所发展的模型不仅可于各向同性材料蠕变变形的描述，还可于描述定向结晶和单晶等各向异性材料的蠕变变形。

（2）利用所发展的蠕变模型对直接时效GH4169G合材料的蠕变试验数据进了模拟，给出了所发展模型中各相应参数与量纲变量 $T / T _ { \mathrm { m } }$ 和 $\sigma / \sigma _ { 0 . 2 }$ 之间的函数关系，获得了较好的效果。针对幂函数形式描述蠕变第1阶段能的限制，采用指数函数对模型做了改进，并直接时效GH4169G试验数据对改进模型进了验证，结果表明，改进模型能更好地描述蠕变变形为，且能与有限元程序结合，用于实际工程结构的预测设计分析。

（3）对比了两种蠕变参数拟合方法：参数总体拟合方法和基于物理意义的拟合方法。采这两种法对GH907材料的蠕变曲线进了模拟，结果表明，总体拟合法较为方便简单，但拟合的效果比基于物理意义拟合的方法差，且拟合过程中参数的取值可能出现特别大或特别小的情况，而基于物理意义的拟合能更为准确地描述每个阶段，但拟合过程有时需要对已拟合的参数进多次调整或修正。

然后，将所发展的归化参数蠕变模型[13,14]在通有限元程序ANSYS中利user-creep程序接完成了程序实现，并对程序计算准确性、步长大等进了分析。总结了相应的变载理论，在对分析的基础上提出了种新的变载（理论）模型，使所编写的程序能较好地模拟应松弛效应[14,16,17]。具体结论如下。

（1）在有限元程序ANSYS环境下，利用其提供的用户可编程特性UPFs具，将所发展的归化参数模型编制成了usercreep户程序，完整地描述了蠕变3个阶段的变形特征。

（2）利算例对所编写的usercreep程序进了考核验证。针对给定的结构有限元模型，采应变硬化模型（程序和程序带模型两种式）和所编写的归化参数蠕变模型的usercreep程序，验证了程序计算结果的正确性，表明所编写的归化参数蠕变模型的子程序既能准确地模拟构件蠕变变形的前两个阶段，又能描述较为危险的第3阶段（加速蠕变阶段）。同时还对程序应于各向异性材料与结构的蠕变分析进行了验证。

（3）通过考察所发展的程序计算的准确性、时间步长对精度的影响，以及有限元模型格规模的计算耗时对，结果表明所编写的程序在相对较短的时间内可实现蠕变第3阶段的计算分析，验证了程序的可性和有效性。

（4）对比分析了当前常的两种不同变载理论（时间硬化和应变硬化）模型，基于等损伤（相对寿命）的观点，发展了种新的相对时间硬化（理论）模型，并与时间硬化和应变硬化模型进了计算结果对比，表明新模型的计算结果介于前两者之间，但与应变硬化模型的更为接近。

（5）计算分析例表明，所发展的usercreep程序实现了对实际结构应松弛效应的数值模拟，同时在usercreep程序中实现了3种变载理论模型，并均可应于实际结构的计算分析。带孔平板例表明程序能较好地模拟应力松弛效应，与时间硬化模型相比，应变硬化和所发展的相对时间硬化模型两者的计算结果偏于安全，可用于实际结构件的蠕变分析。

最后，利前所发展的基于归化参数的蠕变模型及据此所编制的usercreep户子程序，对涡轮盘和涡轮转子叶结构进了蠕变变形和应力松弛效应分析，其主要结论如下。

（1）对给定的涡轮盘进了其1/72扇区的有限元建模，静分析结果表明：盘、螺栓孔边及盘缘与辐板过渡区3处的应较，在结构设计中应重点关注这些部位的蠕变行为。

（2）应所发展的基于归化参数的蠕变模型及其usercreep程序，对涡轮盘模型进行了蠕变分析。经过一定时间的蠕变变形，涡轮盘上的高应力区会出现应力松弛，总体上应力分布将更加均匀，除盘心外，几乎不再有局部区域应力很大的情况。同时考察了高应力区域的应力随时间的变化，应力集中处的应力均出现了一定程度的松弛，应梯度有所减缓[14,15]。仅就疲劳，结构件因蠕变变形使其应平下降对其循环寿命来说是有利的。由于盘心处的温度较低，其应力松弛幅度相对较，并因其长时间处于高应力状态，相对较为危险，应作为涡轮盘结构设计中的重点考核部位[15]。

（3）涡轮转叶结构的静分析结果表明，叶根部的应较。应所发展的基于归化参数的蠕变模型及其户程序usercreep对涡轮转叶进了蠕变分析。蠕变应变最大点出现在温度较高的叶身中部附近。随着蠕变变形的增加，总体上叶片的应力分布将更加均匀，最大应力值逐渐降低，但叶尖的径向位移逐渐增大，涡轮叶结构设计中，应考虑其长时间作后由蠕变变形引起的叶尖径向变形（位移）增而带来的不利影响。

# 参考文献

[1饶寿期，孟春玲.单晶材料涡轮叶的循环蠕变分析[J．航空动学报，1998，13（1）:30-32.  
[2]爱梅，饶寿期.定向结晶冷叶的蠕变分析法[J．燃涡轮试验与研究，1998，11（2）:47-50.  
[3]饶寿期，吴斌，孟春玲，单晶涡轮叶的蠕变计算分析[J．燃涡轮试验与研究，1998,11（4）:30-33.  
[4]黎学，饶寿期．单晶叶的热弹性蠕变分析[C//全国第届热疲劳学术会议论文集，北京：中国属学会，2000：132-136.  
[5] 赵爱红，饶寿期.涡轮叶的循环蠕变分析[J]．航空动学报，1995，10(1)：5-8.  
[6孟春玲，吴斌，饶寿期．单晶叶材料蠕变试验研究[J．北京航空航天学学报，

1998,24（1）：21-23.[7] 孟春玲，饶寿期．涡轮叶蠕变寿命预测法研究[J．北京商学学报，2002，20（2）：52-55.[8]张俊善．材料的温变形与断裂[M．北京：科学出版社，2007.[9] Sawada K, Tabuchi M, Kimura K. Analysis of long -term creep curves by constitutive e-quations [J]. Materials Science and Engineering: A, 2009, 510: 190–194.[10] Miller A K. Modelling of cyclic plasticity with unified constitutive equations: improve-ments in simulating normal and anomalous bauschinger effects [J]. Journal of Engineer-ing Materials and Technology, 1980, 102 (2): 215–222.[11] Chaboche J L. Constitutive equations for cyclic plasticity and cyclic viscoplasticity [J].International Journal of Plasticity, 1989, 5(3):247–302.[12] Bodner S R, Partom Y. Constitutive equations for elastic–viscoplastic strain –hardeningmaterials [J]. Journal of Applied Mechanics, 1975, 42 (2): 385–389.[13] 王延荣，程域钊，李宏新，等.种基于归化参数的蠕变模型[J．航空动学报，2017，32（3）：683-688.[14]程域钊．蠕变建模及叶盘结构应分析[D]．北京：北京航空航天学，2015.[15]李宏新，王延荣，程域钊.基于归化参数模型的涡轮盘和涡轮叶蠕变分析[J].航空发动机，2016，42（5）：48-54.[16]程域钊，王延荣，李宏新，等.归化参数蠕变模型的程序实现与验证[J]．航空动力学报，2017，32（3）：697-703.[17] 刘姣，李振荣，王欣，等.种GH4169G合的组织与蠕变为[J]．材料热处理学报，2013,34（8）：74-79.[18]饶寿期.航空发动机的温蠕变分析[J]．航空发动机，2004，30（1）：10-13.[19]周柏卓，聂景旭.正交各向异性材料屈服准则研究[J．航空发动机，1996(3)：30-37.[20]赵萍，何清华，李维，等．DD3单晶的Hill屈服准则应研究[J．航空材料学报，2010，30(3）：70-73.[21航空发动机设计材料数据册委员会.航空发动机设计材料数据册[M].北京：航空工业出版社，2010.[22] 陈惠发.弹性与塑性学[M].北京：中国建筑业出版社，2004.[23 王勖成.有限单元法[M].北京：清华学出版社，2003.

# 第3章 空风扇叶结构优化设计法

# 3.1引

风扇/压机是涡轮风扇发动机的关键结构件之一，推重比的设计指标要求风扇/压机的增压比更、结构更加紧凑、质量更轻的同时要有好的动稳定性。在发动机设计早期，风扇叶一般为实心、带阻尼凸台、展弦比较大的窄弦结构，这种早期的风扇叶设计存在很多固有的动和结构缺陷。近年来，以凸肩涵道比为特征的先进风扇设计技术得到快速发展，实叶已经难以满宽弦、轮毂的风扇设计要求，因不得不采空叶或复合材料叶，其中采超塑性成形/扩散连接艺（SPF/DB）制造的钛合宽弦空风扇叶以其良好的动、结构强度以及抗疲劳性能，在世界先进涡扇发动机的设计中得到了泛应。当前正在使的PW4084、GE90、TRENT800、F119、EJ200等军民涡扇发动机均采了这种结构设计。相对于国外发动机中已经泛采宽弦空风扇叶，国内研制空风扇叶起步较晚，虽然经过多年的发展也取得了一些有益的结果，但关于空风扇叶的结构设计理论和设计法仍缺乏深的研究和认识。这是由于空风扇叶的结构设计是个综合了多学科、多准则、多约束以及多标的问题，设计中般存在多个设计变量、约束条件和优化标，需要综合考虑具体的设计学科来得到可解。随着数值模拟技术和优化理论的臻成熟，基于有限元分析的优化设计技术在程中得到了泛的应用，因而有必要探索结构优化设计技术在空风扇叶设计中的应流程、策略和实施法。

# 3.2 空扇叶结构设计流程

# 3.2.1设计框架

开展空风扇叶的结构设计先需要确定其初始叶型，确定叶型的般流程是先按照叶的动性能要求设计出叶的热态叶型，但该热态叶型并不能直接作为叶的加工叶型。这是由于叶在实际作中受离和动等作会产变形，使叶的热态叶型（作状态）与冷态叶型（艺状态）并不相同。因此，叶的加叶型需要由热态叶型进逆向设计确定，即进空心风扇叶的结构设计先需要确定其对应的冷态叶型作为初始叶型，然后进内部结构的设计。

空心风扇叶片结构设计的关键在于确定合适的内部空腔结构，在满足叶片强度、刚度以及疲劳可靠性的前提下尽量降低其重量。现有的空心风扇叶结构设计普遍是在“固化”的叶型上开展[1,2]，由于发动机对叶动性能的要求越来越，风扇叶的几何外形也愈加复杂，若直接“固化”叶型而仅对内部结构进设计可能难以满足设计要求。此外，由于叶片的弯掠造型和内部加强筋板的存在，容易导致叶盆与叶背间的应力水平相差较大而降低其强度性能。因此，对于空心风扇叶的结构设计而，不仅需要优化叶片的内部结构，同样有必要对其叶型进行合理设计以提高其强度。正如前文所述，空心风扇叶的叶型主要以气动设计为主，结构设计一般是在气动叶型基础上对叶基元叶型沿径向的积叠规律进适当调整，以改善叶的应分布。对于基于有限元分析的优化过程，若同时对叶片的内部结构和叶型进行设计，由于描述空心叶片内部结构和叶型积叠的设计参数较多，且各个参数并不独，势必存在设计规模庞的限制，降低优化设计的效率甚法获得满意的结果。鉴于此，为了提优化设计分析的效率，提出“区域分解，分级优化”的顺序优化设计思路，将以降低叶重量为目标的内部结构设计和以改善叶身应力分布为目标的叶身设计分步实施：首先进叶的内部结构设计，获得满一定设计约束的最优空腔布局；然后对叶型的径向积叠规律进优化，进步改善叶的应分布。完整的空风扇叶结构设计流程如图3-1所示。

![](images/bfb048584a6f839e46c7e2646f9b5df994fdb89235e414fe41f41ca6aee6e4ea.jpg)  
图3-1 空风扇叶设计流程

该优化流程按照分析对象可以分为实叶设计和空叶设计，实叶设计（确定冷态叶型）的在于根据动热态叶型确定空心风扇叶的初始叶型，即由给出的动热态叶型进逆向设计得到对应的工艺叶型（冷态叶型），以此叶型为基础进空风扇叶的结构设计。空风扇叶的设计流程按照不同区域（部位）由两级模块顺序完成：1级优化模块针对其内部结构进优化，以降低叶的重量为优化标；2级优化模块对叶的径向积叠规律进优化，以改善叶应分布为优化标。

# 3.2.2冷态叶型的迭代解法

空叶的设计先需要由动热态叶型确定其对应的冷态叶型，作为空心风扇叶的初始设计叶型。求解冷态叶型的基本思想是由热态叶型进多次逆向迭代[3]，即先计算热态叶型在作状态下的变形量 $d _ { 1 }$ ，由初始热态叶型减去这个变形量 $d _ { 1 }$ 得到一个新叶型，然后计算新叶型的变形量 $d _ { 2 }$ ，并由初始叶型减去 $d _ { 2 }$ ，得到第二个新叶型，如此多次迭代后，叶的变形量逐渐收敛于一个定值，此时的叶型即为对应的冷态叶型。叶的迭代过程可以图3-2说明，编号1\~4为叶型的迭代过程，其中1号叶型为动热态叶型，2号、3号叶型为迭代过程中的叶型，4号叶型为对应的冷态叶型。具体的计算过程如下：

（1）以1号叶型为计算叶型，将1号动热态叶型与其的位移变形量求差得到2号叶型；

(2）以2号叶型为分析叶型，由1号热态叶型与2号叶型的变形量求差得到3号叶型；

（3）以3号叶型为分析叶型，由1号热态叶型与3号叶型的变形量求差，经过多次迭代计算后，最终收敛到4号冷态叶型。

由上述冷态叶型的迭代求解过程可知，在冷态叶型的求解过程中需要多次进有限元模型的更新和计算，本文采ANSYS的APDL语编写了冷态叶型的求解程序，程序的实现流程如图3-3所示。

![](images/7c621c15625a97539fd21e0cfedf801a38937d704924929ea11d547c2a202e45.jpg)  
图3-2 热态叶型迭代到冷态叶型的意图

![](images/c683ad1b5c671072a8bf003d346948e25323bb360f99832e491ed1c481e8e036.jpg)  
图3-3 叶冷态叶型求解流程图

# 3.3空腔结构优化设计技术及算例

# 3.3.1 优化策略与关键技术

对于个优化设计问题，设计变量、约束条件、标函数以及优化算法是它的个关键要素。设计变量决定了一个优化问题的设计自由度和计算规模，而约束条件、目标函数的确定则关系到能否获得理想的优化结果，优化算法以及相应的优化策略则关系到优化分析的效率和稳健性。对于基于有限元分析的结构优化过程，通常需要进多次模型的更新、有限元计算以获取目标函数和约束函数信息，这是一个非常耗时的过程。目前主要有两种解决的技术途径，即采用并计算或近似替代模型。虽然并计算能够在定程度上提计算效率，但并不能从根本上解决计算规模过于庞的问题。近似替代模型则是建优化标函数、约束条件与设计变量之间的显式函数关系，将优化过程从耗时的有限元分析中解脱出来，是目前应用最为泛的一种方法，但要求替代模型具有足够的精度，否则可能得到失真的模拟结果。

3.3.1.1基于疲劳约束的组合优化策略

图3-4给出了基于疲劳约束的组合优化策略。涉及的主要技术包括近似替代模型的构建、优化算法的组合以及约束条件的给定。为了降低优化的分析规模，在优化分析任务开始前进参数敏感性分析，保留关键参数，剔除部分次要设计变量。该优化策略的实施步骤如下。

![](images/439c3659ed4725612ea12f06ed41bdcccb642ae3fc2de466bb50dd3a47bcae67.jpg)  
图3-4 基于组合优化法的结构优化设计流程

首先，进空风扇叶的参数化建模，根据叶的内部拓扑结构确定离散设计变量；其次，为了提高优化分析的效率，采用正交试验设计方法对设计参数进行敏感性分析，剔除对约束条件、标函数影响致的设计变量，保留关键设计变量作为优化参数；进一步地，采用中心组合设计方法构建样本点数据库，根据试验设计结果进有限元分析获得样本点的响应信息，采最乘回归法构建次多项式响应替代模型，并对该替代模型进精度考核，若替代模型不满精度要求，则增加新的样本点重新构建响应面模型，直至精度满足要求；最后，利用全局寻优的多岛遗传算法（multi-islandgenetic algorithm，MIGA）结合所构建的替代模型进优化。尽管这个优化过程是一个效的过程，但其结果仍是近似的。因此，将获得的最优解作为设计初值，继续采用序列二次规划算法（non-Ilinear programming by quadratic lagrangian，NLPQL）调有限元分析程序进优化，最终获得全局的真实最优解。特别地，尽管在数学上获得一个问题的最优解也是困难的，但对于工程实际问题，能否得到一个工程设计的可行解，很大程度上更依赖于约束条件的给定。空心风扇叶片不仅需要满足静强度的要求，还要防止其在实际工作过程中出现高循环疲劳失效。工程中广泛采用古德曼（Godman）曲线作为叶循环疲劳设计的具，因可利叶材料的Goodman曲线给出叶片设计的疲劳约束。

该优化设计策略的关键技术包括试验设计与近似技术、优化算法以及疲劳约束条件的确定。

# 3.3.1.2试验设计与近似技术

目前，工程中比较常用的试验设计方法包括正交试验设计、均匀设计、拉丁方设计、中心组合设计等。利用这些试验设计方法合理安排一定数量的试验，能够明晰地分析设计参数对目标响应的影响规律。采用试验设计方法进数据判断的方法分为直观分析法和差分析法[4]。直观分析法泛采平均值图和极差分析法对各因的影响程度大小进分析，水平均值图是将每个因子不同水平的均值画成一张图，以此表征因子对目标函数的影响效应，也称为主效应图。极差是指目标响应在某个因子取最大水平与最小水平时的差值，极差大小可以反映因子变化对结果影响的大小，从而判断因素对结果影响的主次顺序。方差分析是依据数理统计理论来讨论哪些因素对试验指标有显著影响，但是这种方法依赖于给定的显著性水平。

正交试验设计法是通过合理的试验组合代替全因试验。正交试验过程一般包括确定因素及相应水平，并根据设计变量特征进试验方案设计以及数据处理和分析几个步骤。在进析因分析时，选用较少的水平就能够判断因素对目标响应的影响趋势和大小，通常取3个水平已经足够。正交表是正交试验设计最重要的工具，根据因素、水平的数量选择合适的正交表进设计，正交表般表示为 $L _ { n }$ （ $q ^ { p }$ )，称为 $q$ 水平、 $p$ 因素的正交表。

另种泛应的试验设计法是中组合设计（centralcompositedesign，CCD），又称次回归旋转设计，总试验次数 $n$ 可以表示为 $n = 2 ^ { p } + 2 p + m _ { 0 }$ ，每个因可以取5个平，保证所布的试验点范围够宽。由于案中存在两个待定参数 $m _ { 0 }$ （中心点的试验次数）和 $\gamma$ （星点的位置），所以中心组合设计可以更加灵活。

优化分析中常用的代理模型包括多项式响应面法、克格（Kriging）法、径向基函数法、神经络、持矢量机等法。这些法各有特点，其中响应法(responsesurfacemethod，RSM）是研究最早、应用最为广泛的一种代理模型。它是在试验设计的基础上，建显式的设计变量与标值的多项式函数关系，由Box和 $\mathbb { W } \mathrm { i l s o n } ^ { [ s ] }$ 于1951年提出。其中阶多项式回归模型的应用最，对于有 $n$ 个设计变量的情况，响应模型为[6]

$$
y = \beta _ { 0 } + \sum _ { i = 1 } ^ { n } \beta _ { i } x _ { i } + \sum _ { j = 1 } ^ { n } \beta _ { j j } x _ { j } ^ { 2 } + \sum _ { i = 1 } ^ { n - 1 } \sum _ { j = i + 1 } ^ { n } \beta _ { i j } x _ { i } x _ { j }
$$

# 3.3.1.3优化算法

当前常用的优化算法以序列二次规划算法为代表的数学规划类算法，以及以遗传算法为代表的现代智能优化算法为主，这两类优化算法各有优势，需要根据分析问题的需要加以选择。

遗传算法（geneticalgorithm，GA）是种结构化的随机搜索技术，由美国的Holland等在1975年先提出并进研究[7]。它的基本思想是达尔的“优胜劣汰”生物进化理论，在个体进化的过程中那些适应性强的个体得以生存。遗传算法包括三个基本操作：选择、交叉和变异。选择是根据个体的适应度选择当前代中的部分个体产下代个体。交叉是对代中的个体进定的操作产代的过程，模拟物界的繁衍过程，用交叉操作产的新代代替当前代中适应度低的个体，从而保证了个体的适应度随着进化次数的增加逐渐提。为了避免过早地收敛到局部的最优个体，变异操作是必不可少的，它是通过对子代的基因进随机扰动来实现。

为了实现遗传算法的这些操作，先需要对设计问题的候选解进编码，前最常用的编码式是二进制串。对于连续变量而，可以根据式（3-2）确定二进制串长

$$
{ \frac { x ^ { \mathrm { u } } - x ^ { \mathrm { L } } } { \varepsilon _ { i } } } \leqslant 2 ^ { \lambda }
$$

式中： $x ^ { \mathrm { U } }$ : $x ^ { \mathrm { L } }$ 设计变量边界约束的上界和下界；

$\varepsilon _ { i }$ 连续设计变量的拟增量（取决于要求的精度）；

$\lambda$ (id:) 表达设计变量所使用的串长。

离散变量的编码过程与连续变量基本相同，但编码时串的长度根据离散变量的个数给出。

完成对设计问题的编码转换后，还需要确定个体的选择评价机制。遗传算法采用适应度函数作为依据，适应度函数需要能够反映求解问题的特征，一般是由优化问题的目标函数映射得到。常用的映射方式包括：（1）直接将待求解的目标函数转换为适应度函数；（2）界限构造法。对于求解问题的约束条件，遗传算法采用惩罚函数法处理，给违反约束的个体添加惩罚项，使其适应值降低。遗传算法还需要解决的一个关键问题是选择算的确定，当前常的选择算法，如例选择（又称赌轮或蒙特卡罗选择）、最佳个体保存等。比例选择的基本思想是个体的选择概率与其适应度成例，该法是目前遗传算法中最常用的方法，最佳个体保存则是对适应度高的个体不进交叉操作而使其直接进下代。这些法虽然形式不同，但初衷均是希望选择更加优良的后代进入下一代。

标准遗传算法具有编码简单、易操作、适性强等特点，但它是将种群作为个整体进选择、交叉、变异等操作，种群的多样性难以保证[⁸]。当存在多个个体并寻优时，单一种群中的个体容易出现局部相似性，有可能在没有达到最优之前即收敛到个局部最优解，导致交叉算和变异算失效，从产“早熟现象”，法得到全局最优解。为了克服早熟现象，研究者提出并遗传算法的思想，多岛遗传算法正是在标准遗传算法基础上发展而来的并遗传算法。它是将整个进化群体划分为若个群体，称为“岛屿”，每个岛屿上的群体独地进选择、交叉、变异等遗传操作。同时，各个岛屿（群体）上的个体进周期性的“迁移”，然后继续按照标准遗传算法进物进化，采这种式保持种群的多样性，从避免早熟现象。多岛遗传算法采两个参数，即迁移间隔和迁移率来控制迁移过程。

遗传算法虽然具有全局寻优的能，但对于基于有限元分析的优化设计过程，采遗传算法的计算量会大大增加。对于单目标的优化设计问题，序列二次规划算法可以通过较少的有限元分析获得标函数以及约束条件的导数信息，因此具有较的局部寻优效率。

线性约束优化问题的般形式为

$$
g _ { i } ( X ) \geqslant 0 ( i = 1 , 2 , \cdots , m )
$$

$$
h _ { j } ( X ) \ = 0 ( j = 1 , 2 , \cdots , l ) 
$$

序列次规划算法的基本思想是：在每个迭代点 $X ^ { ( k ) }$ 构造式（3-3）的一个二次规划子问题，以这个子问题的解作为迭代的搜索方向 $S ^ { ( k ) }$ 并沿该方向做一维搜索，即

$$
\mathbf { { X } } ^ { ( k + 1 ) } \ = \mathbf { { X } } ^ { ( k ) } \ + \alpha ^ { ( k ) } \ S ^ { ( k ) }
$$

得到 $X ^ { ( k + 1 ) }$ ，令 $k = k + 1$ ，重复上述迭代过程，直点列 $\left| X ^ { ( k ) } \left( k = 0 , 1 , 2 , \cdots \right) \right.$ 最终逼近原问题式的近似约束最优点 $X ^ { * }$ 。若 $X ^ { * }$ 是式（3-3）的一个可解，且目标函数$f ( X )$ 、约束函数 $\boldsymbol { g } _ { i } ( \boldsymbol { X } )$ 和 $h _ { j } ( X )$ 在该解处可微， $\nabla g _ { i } \left( \boldsymbol { X } \right)$ 和 $\nabla h _ { j } \left( { \cal X } \right)$ 线性无关，则存在 $\lambda _ { i }$ 及 $\mu _ { j }$ 使

$$
\begin{array} { r } { \left\{ \nabla f ( \pmb { X } ^ { * } ) - \displaystyle \sum _ { i = 1 } ^ { m } \lambda _ { i } \nabla g _ { i } ( \pmb { X } ^ { * } ) - \displaystyle \sum _ { j = 1 } ^ { l } \mu _ { j } \nabla h _ { j } ( \pmb { X } ^ { * } ) = 0 \right. } \\ { \left. \lambda _ { i } \geqslant 0 , \lambda _ { i } g _ { i } ( \pmb { X } ^ { * } ) = 0 \right. } \end{array}
$$

称为库恩·塔克（Kuhn-Tucker，K-T）条件[9]，K-T条件是确定某点为极值点的必要条件，但般来说并不是充分条件。

序列次规划算法就是将个约束优化设计问题，在可解处对标函数和约束函数进泰勒展开，转化为正定二次规划问题，通过一系列的二次规划问题来逼近原始问题的最优解。将原问题式进泰勒展开，得到

$$
f ( { \pmb X } ^ { k + 1 } ) \ = f ( { \pmb X } ^ { k } ) \ + \nabla f ( { \pmb X } ^ { k } ) ^ { \mathrm { T } } ( { \pmb X } ^ { k + 1 } - { \pmb X } ^ { k } ) \ + \frac { 1 } { 2 } ( { \pmb X } ^ { k + 1 } - { \pmb X } ^ { k } ) \ \nabla ^ { 2 } f ( { \pmb X } ^ { k } ) ( { \pmb X } ^ { k + 1 } - { \pmb X } ^ { k } )
$$

$$
\begin{array} { l } { { g _ { i } \bigl ( X ^ { k + 1 } \bigr ) \ = \ g _ { i } \bigl ( X ^ { k } \bigr ) \ + \nabla g _ { i } \bigl ( X ^ { k } \bigr ) ^ { \mathrm { T } } \bigl ( X ^ { k + 1 } - X ^ { k } \bigr ) \bigl ( i \ = 1 , 2 , \cdots , m \bigr ) } } \\ { { h _ { j } \bigl ( X ^ { k + 1 } \bigr ) \ = \ h _ { j } \bigl ( X ^ { k } \bigr ) \ + \nabla h _ { j } \bigl ( X ^ { k } \bigr ) ^ { \mathrm { T } } \bigl ( X ^ { k + 1 } - X ^ { k } \bigr ) \bigl ( j \ = 1 , 2 , \cdots , l \bigr ) } } \end{array}
$$

由于是求标函数在约束条件下的极值，因此，必然要求 $f$ $X ^ { k + 1 }$ ) $- f$ ( $X ^ { k }$ ）取极小值，令 $\mathbf { \boldsymbol { X } } ^ { k + 1 } - \mathbf { \boldsymbol { X } } ^ { k } = \boldsymbol { d }$ ，则有等价的约束优化问题

$$
Q ( d ) \ = \nabla f ( X ^ { k } ) ^ { \mathrm { T } } d + \frac { 1 } { 2 } d ^ { \mathrm { T } } \nabla ^ { 2 } f ( X ^ { k } ) d
$$

$$
g _ { i } ( X ^ { k } ) \ + \nabla g _ { i } ( X ^ { k } ) ^ { \mathrm { T } } d \geq 0
$$

$$
h _ { j } ( X ^ { k } ) \ + \nabla h _ { j } ( X ^ { k } ) ^ { \top } d \ = 0
$$

如果是正定矩阵，则构成了一个在 $X ^ { k }$ 点处的正定二次规划问题。对于正定二次规划问题可以采用有效集法求解。在基于有限元分析的优化过程中，目标函数和约束函数的梯度信息般通过有限差分法获得，海塞矩阵般通过BFGS算法在迭代过程中实现更新。

# 3.3.1.4疲劳约束条件

高循环疲劳失效是航空发动机叶尤为突出的问题，其中很大一部分是由其自身振动引起的，例如由上游叶片排尾迹、来流畸变等作用导致的强迫振动。叶片在设计阶段必须同时考虑叶的静强度及可能存在的循环疲劳失效问题。叶的静强度设计准则如屈服准则或者持久极限准则都不能充分考虑因振动引起的循环疲劳失效问题。对于循环疲劳失效问题，传统的设计法是通过绘制叶的坎贝尔（Gampbell）图来避开其共振频率，但由于叶盘耦合振动的复杂性以及流激励的多频性，完全避开共振是不可能的。因此，叶在设计阶段需要留有够的振动应裕度。Goodman曲线被泛于叶片的高循环疲劳设计中，如图3-5所示，横坐标代表平均应力，纵坐标为交变应幅值。Goodman曲线与横轴、纵轴的截距分别为拉伸强度 $\sigma _ { \mathrm { ~ b ~ } }$ 和疲劳极限 $\sigma _ { - 1 }$ 。在应用Goodman曲线进设计时，常采用寿命数为 $1 0 ^ { 7 }$ 的试验点进绘制。应Goodman曲线进循环疲劳设计时横坐标对应稳态（由离、动载荷等引起）应，纵坐标对应振动应，通过限定最的允许振动应给出叶的安全设计区域（图3-5中阴影区域)。

![](images/2f633231a8cab5ee8e4ea4c57e605ae9ecaa6a6c9626fe59e8d8b6e467bf8fc1.jpg)  
图3-5 Goodman 曲线示意图

Goodman曲线的表达式为

$$
\frac { \sigma _ { \mathrm { { a } } } } { \sigma _ { \mathrm { { - } 1 } } } + \frac { \sigma _ { \mathrm { { - } } m } } { \sigma _ { \mathrm { { b } } } } = 1
$$

空风扇叶的材料常选钛合（如TC4等），利应和疲劳强度可以计算得到应力幅 $\sigma _ { \mathrm { a } }$ 与平均应力 $\sigma _ { \mathrm { { m } } }$ 。应幅值、平均应与应 $R$ 的关系为： $\sigma _ { \mathrm { { a } } } =$ $\frac { \sigma _ { \mathrm { m a x } } } { 2 } , \ \sigma _ { \mathrm { m } } = \frac { \sigma _ { \mathrm { m a x } } \ ( 1 + R ) } { 2 } \circ$ i

材料数据册[10]给出了不同寿命循环数下的Goodman曲线如图3-6（a）所。通常取寿命循环数为 $1 0 ^ { 7 }$ 作为限寿命设计，如图3-6（b）所示，图中实线为式（3-8）所对应的直线，虚线为材料数据册所给出的试验拟合曲线。可以看出，采式（3-8）所给出的安全区域相对保守且应更加简便，因而在优化分析中采该曲线给出疲劳约束条件。

![](images/1dd46c25693acbfe87a1bffd243e027ea44580f1f45fee50354b40161f8c97ac.jpg)  
（a）不同寿命循环数下的Goodman曲线

![](images/43502c61fa0af14cde33c12849777b22916b79f39311d1891c3c966be47b5ce1.jpg)  
图3-6 TC4棒材Goodman曲线

# 3.3.2 空心风扇叶初始叶型的确定

开展空叶的结构优化设计先需要确定其初始叶型，即由动热态叶型求解对应的冷态叶型。本节采图3-3给出的设计流程确定初始设计叶型（冷态叶型）。

根据所给的动叶型数据建其实体模型和有限元模型如图3-7所，叶最旋转半径为 $9 7 5 \mathrm { m m }$ , $100 \%$ 设计转速为 $3 8 6 5 \mathrm { r / m i n }$ 。叶有限元模型的节点数为2976，单元数为1860，计算单元选六体节点单元（ANSYS中的solid185）。叶材料为TC4，材料参数如下：密度为 $4 4 4 0 \mathrm { k g / m } ^ { 3 }$ ，弹性模量为 $1 0 9 \mathrm { G P a }$ ，泊松比为0.34。计算边界条件为叶根部固支，转速为 $100 \%$ 设计转速，叶表施加体压，计算时考虑何非线性效应。

![](images/9f1c53565ff1c59f9824f612c755fe12c418803f77dce2854203f70dc196df54.jpg)  
图3-7 空风扇叶初始热态叶型

由冷态叶型迭代求解过程可知，冷态叶型的迭代求解需要进多次有限元计算，直前后两次叶的变形量满收敛条件才可认为此时的叶型为冷态叶型。图3-7所给叶的最周向位移随迭代次数的变化如图3–8所，当进到第8次迭代时，叶的最周向位移趋于定值，即可近似认为此时得到的叶型为对应的冷态叶型。需要说明的是，该叶型进8次迭代求解即可获得对应的冷态叶型，对于其他叶型所需的迭代求解次数与其叶型特征有关，弯掠程度的叶型所需迭代次数般也更多。获得叶的冷态叶型后，仍需要对冷态叶型进有限元分析，以检验冷态叶型变形后的叶型是否与动设计的热态叶型重合。

图3-9给出了热态叶型与冷态叶型的对，其中包括初始热态叶型，进迭代求解后得到的冷态叶型，该冷态叶型在作状态下变形后的叶型。可以看出，初始热态叶型与变形后的叶型重合，表明采迭代求解得到的冷态叶型在作状态下与动设计的热态叶型相符。

![](images/d33a1050464bc8d1ec729f7b4f44e892d6435e44b07c58b41ea34be19123ff11.jpg)  
图3-8叶最大周向位移随迭代次数的变化

![](images/e0ea467d4901a90f06ed64a39420d64ec665e53166f257bb9264ac970ca93085.jpg)  
图3-9 叶冷热态叶型对比

# 3.3.3 空心风扇叶的参数化建模

基于有限元分析的结构优化过程需要多次更新有限元模型，因开展空风扇叶的优化分析先需要进参数化建模。第代宽弦空风扇叶采超塑性成形/扩散焊接（superplastic forming and diffusion bonding，SPF/DB）工艺加而成，它是由两层变厚度的壁板与层薄芯板经扩散焊接后在内部通定压的体形成空腔，但整个叶并不都是空（撑开）的，靠近叶根、叶尖处的钛合板均焊接在起。因此，在空腔段与实段之间存在两个过渡区，过渡区是指叶由实段向空段过渡的区域。过渡区内由于截拓扑结构的改变容易产应集中，且由于承载积的减使叶片的应力水平增大，与靠近叶尖处的过渡区相比，靠近叶根处的过渡区承载的离心力更，过渡区还需要远离叶的弯振型节线位置[11]。研究表明过渡区的壁板、芯板厚度对叶应平的影响也分显著[12]。空风扇叶过渡区的设计是结构设计的关键部位之，空风扇叶的参数化模型需要准确描述叶该部位的何特征。

基于参考献[2，12中提出的组特征参数来描述空风扇叶的内部结构，叶截的拓扑构型如图3-10所。空风扇叶可由6个结构特征参数确定，分别为壁板厚度 $D$ ，芯板厚度 $d$ ，芯板个数 $N$ ，扩散连接部位长度S，空腔至叶尖部、根部距离 $H _ { 1 }$ 、 $H _ { 2 }$ 。关于这6个特征参数的详细介绍请参见参考献[2，12。

![](images/d5253c9b32c0432645da95db1207435788fab5b694a9957009a280a12556f31c.jpg)  
图3-10 空风扇叶截拓扑构型

基于上述结构特征参数进参数化建模，考虑到过渡区的何特征，将叶划分为空腔段、实段和过渡段，在集成单元时依据不同的何拓扑结构分别集成，空心风扇叶的建模流程如图3-11所。具体的建模过程为：

(1）将叶沿叶向划分为71个截，根据8个等距离分布的壁板厚度 $D _ { \scriptscriptstyle 1 } \sim D _ { \scriptscriptstyle 8 }$ 插值得到其他截面的壁板厚度；

（2）利叶型数据、壁板厚度 $D$ 、芯板厚度比 $C$ ，以及扩散连接比率 $L$ 确定空腔的几何参数，并对每个叶截划分维（平）格，将平单元的有限元节点信息写入节点文件；

(3）读单元集成程序，判断节点所属区域（空腔段、实段与过渡段），由叶根至叶尖逐层集成六面体单元，完成有限元模型的建。

采该流程建的空风扇叶模型如图3-12所，叶共有41898个节点，成30450个六体单元。

![](images/c8a4a3d44f672bec66716295251a8bd4810e8020e09260bd5c05e13cb0d5409e.jpg)  
图3-11 空风扇叶建模流程

![](images/e38aabcbb3c63b0acb0578f7e6fb789b7f1d7e94e196cede8711d83f520b357f.jpg)  
图3-12 空风扇叶有限元模型

# 3.3.4 基于组合优化策略的优化分析

# 3.3.4.1基于正交试验设计的参数敏感性分析

利用正交试验的直观分析可以很好地研究设计变量的变化如何影响目标函数和约束函数，有助于获取设计空间的性质。通过对参数进敏感性分析，可以从量输变量中筛选对目标函数影响最大的设计变量，同时可以判断设计变量对约束条件的影响，抓住主要盾。进正交试验设计，先需要确定因平，根据空风扇叶的结构连续性及艺可性要求，给定各个优化设计变量的取值区间（见表3-1）。选 $L _ { 2 7 }$ $3 ^ { 1 3 }$ ）构造正交表，设计变量的离散取值平见表3-2，通过有限元计算得到叶最等效应及重量（见表3-3）。

表3-1优化设计变量取值区间  

<table><tr><td rowspan=1 colspan=1>区间</td><td rowspan=1 colspan=1>D1/mm</td><td rowspan=1 colspan=1>$D 2/mm</td><td rowspan=1 colspan=1>D₃/mm</td><td rowspan=1 colspan=1>$D$/mm</td><td rowspan=1 colspan=1>D_/mm</td><td rowspan=1 colspan=1>$D /mm</td><td rowspan=1 colspan=1>$D_/mm</td><td rowspan=1 colspan=1>Dg/mm</td><td rowspan=1 colspan=1>C</td><td rowspan=1 colspan=1>L</td></tr><tr><td rowspan=1 colspan=1>下限</td><td rowspan=1 colspan=1>3.0</td><td rowspan=1 colspan=1>3.0</td><td rowspan=1 colspan=1>2.8</td><td rowspan=1 colspan=1>2.8</td><td rowspan=1 colspan=1>2.6</td><td rowspan=1 colspan=1>2.4</td><td rowspan=1 colspan=1>2.2</td><td rowspan=1 colspan=1>2.0</td><td rowspan=1 colspan=1>0.2</td><td rowspan=1 colspan=1>0.2</td></tr><tr><td rowspan=1 colspan=1>上限</td><td rowspan=1 colspan=1>4.4</td><td rowspan=1 colspan=1>4.2</td><td rowspan=1 colspan=1>4.0</td><td rowspan=1 colspan=1>4.0</td><td rowspan=1 colspan=1>3.6</td><td rowspan=1 colspan=1>3.0</td><td rowspan=1 colspan=1>2.8</td><td rowspan=1 colspan=1>2.4</td><td rowspan=1 colspan=1>0.4</td><td rowspan=1 colspan=1>0.6</td></tr></table>

表3-2 设计变量离散水平  

<table><tr><td rowspan=1 colspan=1>水平</td><td rowspan=1 colspan=1>D$/mm</td><td rowspan=1 colspan=1>D2/mm</td><td rowspan=1 colspan=1>$D₃/mm</td><td rowspan=1 colspan=1>$D/mm</td><td rowspan=1 colspan=1>Ds/mm</td><td rowspan=1 colspan=1>$D/mm</td><td rowspan=1 colspan=1>D_/mm</td><td rowspan=1 colspan=1>Dg/mm</td><td rowspan=1 colspan=1>C</td><td rowspan=1 colspan=1>L</td></tr><tr><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>3.0</td><td rowspan=1 colspan=1>3.0</td><td rowspan=1 colspan=1>2.8</td><td rowspan=1 colspan=1>2.8</td><td rowspan=1 colspan=1>2.6</td><td rowspan=1 colspan=1>2.4</td><td rowspan=1 colspan=1>2.2</td><td rowspan=1 colspan=1>2.0</td><td rowspan=1 colspan=1>0.2</td><td rowspan=1 colspan=1>0.2</td></tr><tr><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>3.7</td><td rowspan=1 colspan=1>3.6</td><td rowspan=1 colspan=1>3.4</td><td rowspan=1 colspan=1>3.4</td><td rowspan=1 colspan=1>3.1</td><td rowspan=1 colspan=1>2.7</td><td rowspan=1 colspan=1>2.5</td><td rowspan=1 colspan=1>2.2</td><td rowspan=1 colspan=1>0.3</td><td rowspan=1 colspan=1>0.4</td></tr><tr><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>4.4</td><td rowspan=1 colspan=1>4.2</td><td rowspan=1 colspan=1>4.0</td><td rowspan=1 colspan=1>4.0</td><td rowspan=1 colspan=1>3.6</td><td rowspan=1 colspan=1>3.0</td><td rowspan=1 colspan=1>2.8</td><td rowspan=1 colspan=1>2.4</td><td rowspan=1 colspan=1>0.4</td><td rowspan=1 colspan=1>0.6</td></tr></table>

表3-3不同设计变量组合下的叶身最大等效应力及叶片重量  

<table><tr><td colspan="1" rowspan="1">试验号</td><td colspan="1" rowspan="1">$D1mm</td><td colspan="1" rowspan="1">$D21}$mm</td><td colspan="1" rowspan="1">$D3mm</td><td colspan="1" rowspan="1">$D41$mm</td><td colspan="1" rowspan="1">Ds1mm</td><td colspan="1" rowspan="1">$D/mm</td><td colspan="1" rowspan="1">$D_/}$mm</td><td colspan="1" rowspan="1">D mm</td><td colspan="1" rowspan="1">C</td><td colspan="1" rowspan="1">L</td><td colspan="1" rowspan="1">SearlMPa</td><td colspan="1" rowspan="1">质量/kg</td></tr><tr><td colspan="1" rowspan="1">1</td><td colspan="1" rowspan="1">3</td><td colspan="1" rowspan="1">3</td><td colspan="1" rowspan="1">2.8</td><td colspan="1" rowspan="1">2.8</td><td colspan="1" rowspan="1">2.6</td><td colspan="1" rowspan="1">2.4</td><td colspan="1" rowspan="1">2.2</td><td colspan="1" rowspan="1">2</td><td colspan="1" rowspan="1">0.2</td><td colspan="1" rowspan="1">0.2</td><td colspan="1" rowspan="1">468.13</td><td colspan="1" rowspan="1">7.47</td></tr><tr><td colspan="1" rowspan="1">2</td><td colspan="1" rowspan="1">3</td><td colspan="1" rowspan="1">3.6</td><td colspan="1" rowspan="1">3.4</td><td colspan="1" rowspan="1">3.4</td><td colspan="1" rowspan="1">3.1</td><td colspan="1" rowspan="1">2.7</td><td colspan="1" rowspan="1">2.5</td><td colspan="1" rowspan="1">2.2</td><td colspan="1" rowspan="1">0.2</td><td colspan="1" rowspan="1">0.4</td><td colspan="1" rowspan="1">509.75</td><td colspan="1" rowspan="1">7.92</td></tr><tr><td colspan="1" rowspan="1">3</td><td colspan="1" rowspan="1">3</td><td colspan="1" rowspan="1">4.2</td><td colspan="1" rowspan="1">4</td><td colspan="1" rowspan="1">4</td><td colspan="1" rowspan="1">3.6</td><td colspan="1" rowspan="1">3</td><td colspan="1" rowspan="1">2.8</td><td colspan="1" rowspan="1">2.4</td><td colspan="1" rowspan="1">0.2</td><td colspan="1" rowspan="1">0.6</td><td colspan="1" rowspan="1">592.86</td><td colspan="1" rowspan="1">8.33</td></tr><tr><td colspan="1" rowspan="1">4</td><td colspan="1" rowspan="1">3.7</td><td colspan="1" rowspan="1">3</td><td colspan="1" rowspan="1">3.4</td><td colspan="1" rowspan="1">3.4</td><td colspan="1" rowspan="1">3.6</td><td colspan="1" rowspan="1">3</td><td colspan="1" rowspan="1">2.5</td><td colspan="1" rowspan="1">2.4</td><td colspan="1" rowspan="1">0.2</td><td colspan="1" rowspan="1">0.2</td><td colspan="1" rowspan="1">468.95</td><td colspan="1" rowspan="1">8.04</td></tr><tr><td colspan="1" rowspan="1">5</td><td colspan="1" rowspan="1">3.7</td><td colspan="1" rowspan="1">3.6</td><td colspan="1" rowspan="1">4</td><td colspan="1" rowspan="1">4</td><td colspan="1" rowspan="1">2.6</td><td colspan="1" rowspan="1">2.4</td><td colspan="1" rowspan="1">2.8</td><td colspan="1" rowspan="1">2</td><td colspan="1" rowspan="1">0.2</td><td colspan="1" rowspan="1">0.4</td><td colspan="1" rowspan="1">431.61</td><td colspan="1" rowspan="1">8.06</td></tr><tr><td colspan="1" rowspan="1">6</td><td colspan="1" rowspan="1">3.7</td><td colspan="1" rowspan="1">4.2</td><td colspan="1" rowspan="1">2.8</td><td colspan="1" rowspan="1">2.8</td><td colspan="1" rowspan="1">3.1</td><td colspan="1" rowspan="1">2.7</td><td colspan="1" rowspan="1">2.2</td><td colspan="1" rowspan="1">2.2</td><td colspan="1" rowspan="1">0.2</td><td colspan="1" rowspan="1">0.6</td><td colspan="1" rowspan="1">417.68</td><td colspan="1" rowspan="1">7.86</td></tr><tr><td colspan="1" rowspan="1">7</td><td colspan="1" rowspan="1">4.4</td><td colspan="1" rowspan="1">3</td><td colspan="1" rowspan="1">4</td><td colspan="1" rowspan="1">4</td><td colspan="1" rowspan="1">3.1</td><td colspan="1" rowspan="1">2.7</td><td colspan="1" rowspan="1">2.8</td><td colspan="1" rowspan="1">2.2</td><td colspan="1" rowspan="1">0.2</td><td colspan="1" rowspan="1">0.2</td><td colspan="1" rowspan="1">460.72</td><td colspan="1" rowspan="1">8.18</td></tr><tr><td colspan="1" rowspan="1">8</td><td colspan="1" rowspan="1">4.4</td><td colspan="1" rowspan="1">3.6</td><td colspan="1" rowspan="1">2.8</td><td colspan="1" rowspan="1">2.8</td><td colspan="1" rowspan="1">3.6</td><td colspan="1" rowspan="1">3</td><td colspan="1" rowspan="1">2.2</td><td colspan="1" rowspan="1">2.4</td><td colspan="1" rowspan="1">0.2</td><td colspan="1" rowspan="1">0.4</td><td colspan="1" rowspan="1">417.42</td><td colspan="1" rowspan="1">7.98</td></tr><tr><td colspan="1" rowspan="1">9</td><td colspan="1" rowspan="1">4.4</td><td colspan="1" rowspan="1">4.2</td><td colspan="1" rowspan="1">3.4</td><td colspan="1" rowspan="1">3.4</td><td colspan="1" rowspan="1">2.6</td><td colspan="1" rowspan="1">2.4</td><td colspan="1" rowspan="1">2.5</td><td colspan="1" rowspan="1">2</td><td colspan="1" rowspan="1">0.2</td><td colspan="1" rowspan="1">0.6</td><td colspan="1" rowspan="1">360.75</td><td colspan="1" rowspan="1">8.01</td></tr><tr><td colspan="1" rowspan="1">10</td><td colspan="1" rowspan="1">3</td><td colspan="1" rowspan="1">3</td><td colspan="1" rowspan="1">3.4</td><td colspan="1" rowspan="1">4</td><td colspan="1" rowspan="1">3.1</td><td colspan="1" rowspan="1">3</td><td colspan="1" rowspan="1">2.2</td><td colspan="1" rowspan="1">2</td><td colspan="1" rowspan="1">0.3</td><td colspan="1" rowspan="1">0.4</td><td colspan="1" rowspan="1">507.17</td><td colspan="1" rowspan="1">8.04</td></tr><tr><td colspan="1" rowspan="1">11</td><td colspan="1" rowspan="1">3</td><td colspan="1" rowspan="1">3.6</td><td colspan="1" rowspan="1">4</td><td colspan="1" rowspan="1">2.8</td><td colspan="1" rowspan="1">3.6</td><td colspan="1" rowspan="1">2.4</td><td colspan="1" rowspan="1">2.5</td><td colspan="1" rowspan="1">2.2</td><td colspan="1" rowspan="1">0.3</td><td colspan="1" rowspan="1">0.6</td><td colspan="1" rowspan="1">506.31</td><td colspan="1" rowspan="1">8.08</td></tr><tr><td colspan="1" rowspan="1">12</td><td colspan="1" rowspan="1">3</td><td colspan="1" rowspan="1">4.2</td><td colspan="1" rowspan="1">2.8</td><td colspan="1" rowspan="1">3.4</td><td colspan="1" rowspan="1">2.6</td><td colspan="1" rowspan="1">2.7</td><td colspan="1" rowspan="1">2.8</td><td colspan="1" rowspan="1">2.4</td><td colspan="1" rowspan="1">0.3</td><td colspan="1" rowspan="1">0.2</td><td colspan="1" rowspan="1">482.45</td><td colspan="1" rowspan="1">8.03</td></tr><tr><td colspan="1" rowspan="1">13</td><td colspan="1" rowspan="1">3.7</td><td colspan="1" rowspan="1">3</td><td colspan="1" rowspan="1">4</td><td colspan="1" rowspan="1">2.8</td><td colspan="1" rowspan="1">2.6</td><td colspan="1" rowspan="1">2.7</td><td colspan="1" rowspan="1">2.5</td><td colspan="1" rowspan="1">2.4</td><td colspan="1" rowspan="1">0.3</td><td colspan="1" rowspan="1">0.4</td><td colspan="1" rowspan="1">439.38</td><td colspan="1" rowspan="1">7.99</td></tr><tr><td colspan="1" rowspan="1">14</td><td colspan="1" rowspan="1">3.7</td><td colspan="1" rowspan="1">3.6</td><td colspan="1" rowspan="1">2.8</td><td colspan="1" rowspan="1">3.4</td><td colspan="1" rowspan="1">3.1</td><td colspan="1" rowspan="1">3</td><td colspan="1" rowspan="1">2.8</td><td colspan="1" rowspan="1">2</td><td colspan="1" rowspan="1">0.3</td><td colspan="1" rowspan="1">0.6</td><td colspan="1" rowspan="1">430.83</td><td colspan="1" rowspan="1">8.11</td></tr><tr><td colspan="1" rowspan="1">15</td><td colspan="1" rowspan="1">3.7</td><td colspan="1" rowspan="1">4.2</td><td colspan="1" rowspan="1">3.4</td><td colspan="1" rowspan="1">4</td><td colspan="1" rowspan="1">3.6</td><td colspan="1" rowspan="1">2.4</td><td colspan="1" rowspan="1">2.2</td><td colspan="1" rowspan="1">2.2</td><td colspan="1" rowspan="1">0.3</td><td colspan="1" rowspan="1">0.2</td><td colspan="1" rowspan="1">421.14</td><td colspan="1" rowspan="1">8.29</td></tr><tr><td colspan="1" rowspan="1">试验号</td><td colspan="1" rowspan="1">$D_/}$mm</td><td colspan="1" rowspan="1">$D₂21$mm</td><td colspan="1" rowspan="1">$D3/mm</td><td colspan="1" rowspan="1">$D41$mm</td><td colspan="1" rowspan="1">D5/mm</td><td colspan="1" rowspan="1">D6/mm</td><td colspan="1" rowspan="1">$D_1$mm</td><td colspan="1" rowspan="1">Dg/mm</td><td colspan="1" rowspan="1">C</td><td colspan="1" rowspan="1">L</td><td colspan="1" rowspan="1">MPa</td><td colspan="1" rowspan="1">质量/kg</td></tr><tr><td colspan="1" rowspan="1">16</td><td colspan="1" rowspan="1">4.4</td><td colspan="1" rowspan="1">3</td><td colspan="1" rowspan="1">2.8</td><td colspan="1" rowspan="1">3.4</td><td colspan="1" rowspan="1">3.6</td><td colspan="1" rowspan="1">2.4</td><td colspan="1" rowspan="1">2.8</td><td colspan="1" rowspan="1">2.2</td><td colspan="1" rowspan="1">0.3</td><td colspan="1" rowspan="1">0.4</td><td colspan="1" rowspan="1">434.51</td><td colspan="1" rowspan="1">8.10</td></tr><tr><td colspan="1" rowspan="1">17</td><td colspan="1" rowspan="1">4.4</td><td colspan="1" rowspan="1">3.6</td><td colspan="1" rowspan="1">3.4</td><td colspan="1" rowspan="1">4</td><td colspan="1" rowspan="1">2.6</td><td colspan="1" rowspan="1">2.7</td><td colspan="1" rowspan="1">2.2</td><td colspan="1" rowspan="1">2.4</td><td colspan="1" rowspan="1">0.3</td><td colspan="1" rowspan="1">0.6</td><td colspan="1" rowspan="1">381.05</td><td colspan="1" rowspan="1">8.20</td></tr><tr><td colspan="1" rowspan="1">18</td><td colspan="1" rowspan="1">4.4</td><td colspan="1" rowspan="1">4.2</td><td colspan="1" rowspan="1">4</td><td colspan="1" rowspan="1">2.8</td><td colspan="1" rowspan="1">3.1</td><td colspan="1" rowspan="1">3</td><td colspan="1" rowspan="1">2.5</td><td colspan="1" rowspan="1">2</td><td colspan="1" rowspan="1">0.3</td><td colspan="1" rowspan="1">0.2</td><td colspan="1" rowspan="1">374.01</td><td colspan="1" rowspan="1">8.31</td></tr><tr><td colspan="1" rowspan="1">19</td><td colspan="1" rowspan="1">3</td><td colspan="1" rowspan="1">3</td><td colspan="1" rowspan="1">4</td><td colspan="1" rowspan="1">3.4</td><td colspan="1" rowspan="1">3.6</td><td colspan="1" rowspan="1">2.7</td><td colspan="1" rowspan="1">2.2</td><td colspan="1" rowspan="1">2</td><td colspan="1" rowspan="1">0.4</td><td colspan="1" rowspan="1">0.6</td><td colspan="1" rowspan="1">502.60</td><td colspan="1" rowspan="1">8.21</td></tr><tr><td colspan="1" rowspan="1">20</td><td colspan="1" rowspan="1">3</td><td colspan="1" rowspan="1">3.6</td><td colspan="1" rowspan="1">2.8</td><td colspan="1" rowspan="1">4</td><td colspan="1" rowspan="1">2.6</td><td colspan="1" rowspan="1">3</td><td colspan="1" rowspan="1">2.5</td><td colspan="1" rowspan="1">2.2</td><td colspan="1" rowspan="1">0.4</td><td colspan="1" rowspan="1">0.2</td><td colspan="1" rowspan="1">491.37</td><td colspan="1" rowspan="1">8.16</td></tr><tr><td colspan="1" rowspan="1">21</td><td colspan="1" rowspan="1">3</td><td colspan="1" rowspan="1">4.2</td><td colspan="1" rowspan="1">3.4</td><td colspan="1" rowspan="1">2.8</td><td colspan="1" rowspan="1">3.1</td><td colspan="1" rowspan="1">2.4</td><td colspan="1" rowspan="1">2.8</td><td colspan="1" rowspan="1">2.4</td><td colspan="1" rowspan="1">0.4</td><td colspan="1" rowspan="1">0.4</td><td colspan="1" rowspan="1">480.60</td><td colspan="1" rowspan="1">8.20</td></tr><tr><td colspan="1" rowspan="1">22</td><td colspan="1" rowspan="1">3.7</td><td colspan="1" rowspan="1">3</td><td colspan="1" rowspan="1">2.8</td><td colspan="1" rowspan="1">4</td><td colspan="1" rowspan="1">3.1</td><td colspan="1" rowspan="1">2.4</td><td colspan="1" rowspan="1">2.5</td><td colspan="1" rowspan="1">2.4</td><td colspan="1" rowspan="1">0.4</td><td colspan="1" rowspan="1">0.6</td><td colspan="1" rowspan="1">439.52</td><td colspan="1" rowspan="1">8.15</td></tr><tr><td colspan="1" rowspan="1">23</td><td colspan="1" rowspan="1">3.7</td><td colspan="1" rowspan="1">3.6</td><td colspan="1" rowspan="1">3.4</td><td colspan="1" rowspan="1">2.8</td><td colspan="1" rowspan="1">3.6</td><td colspan="1" rowspan="1">2.7</td><td colspan="1" rowspan="1">2.8</td><td colspan="1" rowspan="1">2</td><td colspan="1" rowspan="1">0.4</td><td colspan="1" rowspan="1">0.2</td><td colspan="1" rowspan="1">427.87</td><td colspan="1" rowspan="1">8.28</td></tr><tr><td colspan="1" rowspan="1">24</td><td colspan="1" rowspan="1">3.7</td><td colspan="1" rowspan="1">4.2</td><td colspan="1" rowspan="1">4</td><td colspan="1" rowspan="1">3.4</td><td colspan="1" rowspan="1">2.6</td><td colspan="1" rowspan="1">3</td><td colspan="1" rowspan="1">2.2</td><td colspan="1" rowspan="1">2.2</td><td colspan="1" rowspan="1">0.4</td><td colspan="1" rowspan="1">0.4</td><td colspan="1" rowspan="1">412.78</td><td colspan="1" rowspan="1">8.38</td></tr><tr><td colspan="1" rowspan="1">25</td><td colspan="1" rowspan="1">4.4</td><td colspan="1" rowspan="1">3</td><td colspan="1" rowspan="1">3.4</td><td colspan="1" rowspan="1">2.8</td><td colspan="1" rowspan="1">2.6</td><td colspan="1" rowspan="1">3</td><td colspan="1" rowspan="1">2.8</td><td colspan="1" rowspan="1">2.2</td><td colspan="1" rowspan="1">0.4</td><td colspan="1" rowspan="1">0.6</td><td colspan="1" rowspan="1">420.43</td><td colspan="1" rowspan="1">8.18</td></tr><tr><td colspan="1" rowspan="1">26</td><td colspan="1" rowspan="1">4.4</td><td colspan="1" rowspan="1">3.6</td><td colspan="1" rowspan="1">4</td><td colspan="1" rowspan="1">3.4</td><td colspan="1" rowspan="1">3.1</td><td colspan="1" rowspan="1">2.4</td><td colspan="1" rowspan="1">2.2</td><td colspan="1" rowspan="1">2.4</td><td colspan="1" rowspan="1">0.4</td><td colspan="1" rowspan="1">0.2</td><td colspan="1" rowspan="1">377.39</td><td colspan="1" rowspan="1">8.37</td></tr><tr><td colspan="1" rowspan="1">27</td><td colspan="1" rowspan="1">4.4</td><td colspan="1" rowspan="1">4.2</td><td colspan="1" rowspan="1">2.8</td><td colspan="1" rowspan="1">4</td><td colspan="1" rowspan="1">3.6</td><td colspan="1" rowspan="1">2.7</td><td colspan="1" rowspan="1">2.5</td><td colspan="1" rowspan="1">2</td><td colspan="1" rowspan="1">0.4</td><td colspan="1" rowspan="1">0.4</td><td colspan="1" rowspan="1">401.38</td><td colspan="1" rowspan="1">8.48</td></tr></table>

各个设计变量的主效应图如图3-13所。图中横坐标为设计变量平，纵坐标为标函数的响应，从图中可以看出以下点。

（1）设计变量对叶重量的影响：壁板厚度 $D _ { 1 } \sim D _ { 8 }$ 、芯板与壁板厚度比 $C$ 越大，叶重量越，扩散连接比率 $L$ 对叶片重量影响不显著。

(2）设计变量对叶径向变形的影响呈现出3种规律：壁板厚度 $D _ { 1 } \sim D _ { 4 }$ 与叶片的径向变形负相关，随着壁板厚度的增大，叶径向变形减；壁板厚度 $D _ { s }$ 与芯板扩散连接比率 $L$ 对叶径向变形影响很，曲线近似为条平线；壁板厚度 $D _ { 6 } \sim D _ { 8 }$ 以及芯板厚度比 $C$ 与径向变形正相关，其值增大时，叶的径向变形也增大。

（3）设计变量对叶等效应的影响：各个设计变量对叶等效应的影响有所不同，壁板厚度 $D _ { 4 } \sim D _ { 8 }$ 增加，叶最等效应呈现增的趋势，且叶的重量也增（如图3-13（a）所示），因此在后续的优化分析中，可以将这5个设计变量作为常量对待。壁板厚度 $D _ { 1 } \sim D _ { 3 }$ 的增加会降低叶片的最大等效应力但同时也会增大叶重量，理论上存在组最优解组合在满叶强度要求的条件下使叶的重量最。芯板与壁板厚度比 $C$ 增大时，叶等效应力降低，芯板扩散连接比率 $L$ 增大使叶等效应力总体呈增大的趋势。

# 3.3.4.2优化分析结果

采用中心组合设计方法生成样本点，由上一小节的参数敏感性分析结果可知，壁板厚度 $D _ { 4 } \sim D _ { 8 }$ 增时，叶的应平、重量均增，在优化时这5个变量取其下限值。将变量 $D _ { 1 } \sim D _ { 3 }$ 、 $C$ 、 $L$ 作为设计变量，每个变量取5个平，因此总的试验次数 $n = 4 3$ ( $p = 5$ )。设计变量的离散平见表3–4。对每组设计变量组合进有限元分析。

![](images/d1c4e0e5496ad6a3b8c445e1ba4c213c2c55433852cdbeb89d45b7365090466d.jpg)  
图3-13 设计变量的主效应图

表3-4设计变量离散水平  

<table><tr><td rowspan=1 colspan=1>水平</td><td rowspan=1 colspan=1>D_/m</td><td rowspan=1 colspan=1>D 2/mm</td><td rowspan=1 colspan=1>D₃/mm</td><td rowspan=1 colspan=1>C</td><td rowspan=1 colspan=1>L</td></tr><tr><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>3.0</td><td rowspan=1 colspan=1>3.0</td><td rowspan=1 colspan=1>2.8</td><td rowspan=1 colspan=1>0.2</td><td rowspan=1 colspan=1>0.2</td></tr><tr><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>3.14</td><td rowspan=1 colspan=1>3.12</td><td rowspan=1 colspan=1>2.92</td><td rowspan=1 colspan=1>0.22</td><td rowspan=1 colspan=1>0.24</td></tr><tr><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>3.7</td><td rowspan=1 colspan=1>3.6</td><td rowspan=1 colspan=1>3.4</td><td rowspan=1 colspan=1>0.3</td><td rowspan=1 colspan=1>0.4</td></tr><tr><td rowspan=1 colspan=1>4</td><td rowspan=1 colspan=1>4.26</td><td rowspan=1 colspan=1>4.08</td><td rowspan=1 colspan=1>3.88</td><td rowspan=1 colspan=1>0.38</td><td rowspan=1 colspan=1>0.56</td></tr><tr><td rowspan=1 colspan=1>5</td><td rowspan=1 colspan=1>4.4</td><td rowspan=1 colspan=1>4.2</td><td rowspan=1 colspan=1>4.0</td><td rowspan=1 colspan=1>0.4</td><td rowspan=1 colspan=1>0.6</td></tr></table>

利用中组合设计的43个样本点构造含交叉项的二次多项式响应面模型，输变量为5个设计变量，输出变量为叶的重量、最径向位移以及叶身等效应，每个响应模型包含21项拟合系数（5个输参数)。为了考察响应模型的精度，随机选取10组设计变量的组合进精度验证，有限元计算结果与响应面预测结果，及与响应面模型的预测对比如图3-14所。从结果可以看出，响应面模型的预测精度较，叶重量的最大预测误差仅为 $0 . 1 2 \%$ ，叶等效应的最预测误差为 $2 . 3 6 \%$ ，在可接受范围内。

![](images/0c4d665e6d5b0d48b5963a676a003a08f185e4e6f595d1def109c564755dd935.jpg)  
图3-14 有限元结果与响应预测结果对

利用所构建的多项式响应面模型，采用多岛遗传算法进优化，优化的目标函数为叶重量最，约束条件根据Goodman曲线给定，利疲劳寿命为 $1 0 ^ { 7 }$ 的光滑试样等寿命曲线，约束条件给定为振动应力不于 $2 0 0 \mathrm { M P a }$ ，对应的稳态应力为 $4 1 0 . 6 \mathrm { M P a }$ 。于是，该优化设计问题可以描述为

$$
\begin{array} { r } { \left\{ \begin{array} { l l } { \mathrm { F i n d } } & { X = ( D _ { 1 } , D _ { 2 } , D _ { 3 } , C , L ) } \\ { \mathrm { m i n } } & { M ( X ) } \\ { \mathrm { s . t . } } & { S _ { \mathrm { e q v } } ( X ) \leqslant \sigma _ { \mathrm { m a x } } } \\ & { X _ { \mathrm { l o w e r } } \leqslant X \leqslant X _ { \mathrm { u p p e r } } } \end{array} \right. } \end{array}
$$

其中： $X$ —设计变量空间；

$M ( X )$ bcid:) 空心风扇叶的质量；  
$S _ { \mathrm { { e q v } } } ( X )$ 叶身最大等效应力；  
$\sigma _ { \mathrm { m a x } }$ 最大稳态等效应力( $\sigma _ { \operatorname* { m a x } } = 4 1 0 . 6 \mathrm { M P a } )$ ;  
$X _ { \mathrm { u p p e r } }$ , $X _ { \mathrm { l o w e r } }$ (id:) 设计变量的上、下界。

首先在次多项式响应面模型上利用多岛遗传算法进优化，获得全局最优解后，将其作为设计变量的初值，继续采用序列二次规划算法并调用有限元分析进优化，最终的优化结果见表3-5。从优化结果可以看出，采序列次规划算法优化得到的叶重量略有降低，但叶的最等效应也有所增加。与实叶的重量( $1 0 . 2 8 \mathrm { k g }$ )相，空风扇叶的重量下降了26. $1 \%$ 。从设计变量的取值来看，除壁板厚度 $D _ { 1 }$ 外，其他4个参数的取值非常接近，这也再次验证了靠近叶根处的壁板设计是叶减重的关键。

表3-5设计变量最优解  

<table><tr><td rowspan=1 colspan=1>优化算法</td><td rowspan=1 colspan=1>$D$/mm$</td><td rowspan=1 colspan=1>$D 2/mm</td><td rowspan=1 colspan=1>D₃/mm</td><td rowspan=1 colspan=1>C</td><td rowspan=1 colspan=1>L</td><td rowspan=1 colspan=1>质量/kg</td><td rowspan=1 colspan=1>Sa/ Pa</td></tr><tr><td rowspan=1 colspan=1>MIGA</td><td rowspan=1 colspan=1>4.06</td><td rowspan=1 colspan=1>3.03</td><td rowspan=1 colspan=1>2.8</td><td rowspan=1 colspan=1>0.2</td><td rowspan=1 colspan=1>0.23</td><td rowspan=1 colspan=1>7.59</td><td rowspan=1 colspan=1>405.6</td></tr><tr><td rowspan=1 colspan=1>NLPQL</td><td rowspan=1 colspan=1>3.76</td><td rowspan=1 colspan=1>3.0</td><td rowspan=1 colspan=1>2.8</td><td rowspan=1 colspan=1>0.2</td><td rowspan=1 colspan=1>0.24</td><td rowspan=1 colspan=1>7.56</td><td rowspan=1 colspan=1>410.6</td></tr></table>

# 3.4 叶径向积叠优化

般情况下，叶的造型设计采将若个基元叶型沿径向线按某种设计规律进积叠的式。在将基元叶型积叠成三维叶型的过程中，积叠控制点可以选择二维叶型的重心、前缘点、尾缘点等部位，通过控制积叠点的周向和轴向位置实现叶的弯掠造型。由于叶的积叠方式主要由气动设计决定，结构设计的裕度很小，通常的做法是对动设计给出的叶型积叠线进少量的调整，如图3-15所示。图中实线与虚线分别代表由动设计确定的积叠线和经结构设计改型后的积叠线，对于图中所的积叠线形式可以通过参数 $L _ { y }$ δ1、δ2控制[13]

![](images/85a636eb227c5b53ae11e487af9ca7611de29c68ad23fb92fecf30837be12d81.jpg)  
图3-15 叶积叠线的结构设计示意图

进积叠线的结构优化设计时，由于对叶的动外形进了调整，有可能影响叶的动性能。理想的设计过程是通过动和结构设计之间的叶型数据交换，经结构改型后对叶的动性能进再校验，通过多次动、结构间的设计改型最终获得气动性能优良且满足强度要求的叶型设计。但这种设计式效率比较低，甚可能无法得到满意的结果。不仅如此，由于需要进行多次不同设计系统之间的数据交换，模型的精度也不易保证。因此，针对叶型积叠线的设计目前更多采用的是“单向”耦合的方法，即首先由动设计确定初始叶型后，结构设计在该叶型的基础上进少量的调整，尽量减小对叶气动性能的影响。普遍采用的方法是保证叶的基元叶型不变，仅将叶的基元流面进一定范围内的周向旋转和必要的轴向平移。

# 3.4.1优化设计方法及策略

对叶积叠线的设计可以采两种式：是直接对叶型线（积叠线）进设计；是对原始叶型线附加修改量。附加量的含义是在叶原始积叠线的基础上将叶片各基元流面进行相对周向旋转。这样，通过对周向旋转角沿叶高的分布曲线进行设计实现对叶积叠线的设计。对于空心风扇叶的结构设计，显然更适合采第二种式。在确定了径向积叠线设计方式的基础上，还需要确定设计参数。参数的数量决定了一个优化设计问题的维度，设计变量越多代表设计的由度越，但过多的设计变量也会增加寻优时间。可见，对模型进参数化并确定合适的设计变量是开展优化分析的前提和基础。进积叠线的参数化首先需要确定离散设计变量，即用若干个设计参数描述叶的径向积叠形式。设计变量的确定需要考虑两的因素：是希望利尽可能少的设计变量保证叶的光顺性和够的设计由度；是叶型的结构设计需以动叶型为基础，并尽量减对动性能的影响，实际上可供结构设计的空间常有限。

数学上，空间中的一条曲线可以用函数 $y = f$ $x$ ）来描述，但基于有限元的结构分析，设计曲线都是通过一组离散的数据点来确定的，这就需要通过这些离散的数据点来构造函数 $f$ ( $x$ ）的近似表达式，即插值过程。常的插值法有代数插值、样条插值等法。结合本的实际问题，分别采用以下三种常的插值法：分段线性插值、三次样条插值和B样条曲线插值。采这三种插值曲线进积叠设计时，先需要给出叶型积叠线的离散控制点。假设空风扇叶沿叶向共划分有 $n$ 层有限元节点，通过控制每层节点沿周向的偏移，即可实现对叶径向积叠规律的设计。以本的叶型为例，叶沿叶共有71层有限元节点，如图3-16所。若将各层节点都作为优化变量势必因设计变量过多导致优化难以进，选择的节点层过少则容易造成叶不光顺，这以每隔7层节点确定个设计变量为例说明叶型的设计过程。为了尽量保证叶光顺，将叶尖处节点的周向旋转作为设计变量，其他层节点的周向旋转占叶尖旋转的百分比作为设计变量。

![](images/e11b61b5b3b39b786945bc24e7dbafcc30f0601d82a073e32cca29c7dceddb48.jpg)  
图3-16 空风扇叶截意图

设计变量的确定和参数化建模是开展结构优化设计的前提和基础，而优化算法则决定了求解一个优化问题时的效率。由前可知，不同的优化算法各有特点，而采用何种优化法（算法）则更多依赖于分析问题的本。对于多标优化问题当前更多采帕累托（Pareto）解的概念来处理[14]。针对空风扇叶径向积叠的优化设计问题，分别采用不同的优化方法开展分析，设计流程如图3-17所示，主要过程为：

（1）利动叶型数据建空风扇叶的参数化模型，给出叶型径向积叠设计的法，即保持叶的基元叶型不变，将叶的各个叶型截面进相对的周向偏移；

（2）确定积叠线的参数化设计法，分别采分段线性插值、三次样条插值和B样条曲线来描述旋转随叶的变化曲线，将叶尖处的周向旋转 $\theta$ 作为设计变量，其他层节点的周向旋转占叶尖旋转角的百分比 $R _ { i }$ 作为设计变量；

（3）根据设计变量的取值进正交试验设计，对试验结果进直观分析，确定各个设计变量对目标函数、约束条件的影响规律；

（4）采序列次规划算法开展单标优化分析，并对不同积叠线设计法对优化结果的影响趋势，确定最优的设计变量组合；

（5）开展空风扇叶径向积叠的多标优化分析，先构建标函数、约束条件与设计变量之间的近似替代模型，采用中心组合设计法成样本点，采用最二乘法回归构建次多项式响应模型，进采用带精英策略的NSGA-Ⅱ算法进优化分析。

![](images/202df33d9c2c88f4aba991b2a650b01a83ab35c8ce185921713a3189c03d5b20.jpg)  
图3-17 空风扇叶径向积叠优化设计流程

# 3.4.2 单目标下的径向积叠优化

# 3.4.2.1 基于正交试验设计的径向积叠规律分析

为了减叶径向积叠设计对叶动性能的影响，需对叶各基元流的周向旋转进严格的限制，给定各个优化参量的取值区间（见表3-6）。表中的设计变量$R _ { i }$ $i = 1$ ，2，…，10）分别代表不同叶所在截沿周向旋转的百分，例如，变量$R _ { \mathrm { 1 } }$ 的上限为0.02，则代表该截沿周向的旋转为 $0 . 0 2 \theta$ , $\theta$ 为叶尖实际旋转。选$L _ { 2 7 }$ d $3 ^ { 1 3 }$ ）正交表进设计变量的试验设计，每个设计变量取3个平，设计变量的离散取值见表3–7。

表3-6 优化设计变量取值区间  

<table><tr><td rowspan=1 colspan=1>区间</td><td rowspan=1 colspan=1>$R_1}$</td><td rowspan=1 colspan=1>$R2}$</td><td rowspan=1 colspan=1>$R{3}$</td><td rowspan=1 colspan=1>$R }$</td><td rowspan=1 colspan=1>$Rs</td><td rowspan=1 colspan=1>$R }$</td><td rowspan=1 colspan=1>Rq}$</td><td rowspan=1 colspan=1>$R}$</td><td rowspan=1 colspan=1>$Rg}$</td><td rowspan=1 colspan=1>R10</td></tr><tr><td rowspan=1 colspan=1>上限</td><td rowspan=1 colspan=1>0.02</td><td rowspan=1 colspan=1>0.04</td><td rowspan=1 colspan=1>0.08</td><td rowspan=1 colspan=1>0.16</td><td rowspan=1 colspan=1>0.3</td><td rowspan=1 colspan=1>0.5</td><td rowspan=1 colspan=1>0.6</td><td rowspan=1 colspan=1>0.7</td><td rowspan=1 colspan=1>0.9</td><td rowspan=1 colspan=1>1.0</td></tr><tr><td rowspan=1 colspan=1>下限</td><td rowspan=1 colspan=1>0.01</td><td rowspan=1 colspan=1>0.02</td><td rowspan=1 colspan=1>0.04</td><td rowspan=1 colspan=1>0.08</td><td rowspan=1 colspan=1>0.16</td><td rowspan=1 colspan=1>0.3</td><td rowspan=1 colspan=1>0.5</td><td rowspan=1 colspan=1>0.6</td><td rowspan=1 colspan=1>0.7</td><td rowspan=1 colspan=1>0.9</td></tr></table>

表3-7设计变量的3个水平  

<table><tr><td rowspan=1 colspan=1>水平</td><td rowspan=1 colspan=1>$R{}$</td><td rowspan=1 colspan=1>$R^2}$</td><td rowspan=1 colspan=1>$R{3}$</td><td rowspan=1 colspan=1>$R4}$</td><td rowspan=1 colspan=1>$R }$</td><td rowspan=1 colspan=1>$R6}$</td><td rowspan=1 colspan=1>$R{}$</td><td rowspan=1 colspan=1>$R{$</td><td rowspan=1 colspan=1>$Rq$</td><td rowspan=1 colspan=1>R10</td></tr><tr><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>0.02</td><td rowspan=1 colspan=1>0.04</td><td rowspan=1 colspan=1>0.08</td><td rowspan=1 colspan=1>0.16</td><td rowspan=1 colspan=1>0.3</td><td rowspan=1 colspan=1>0.5</td><td rowspan=1 colspan=1>0.6</td><td rowspan=1 colspan=1>0.7</td><td rowspan=1 colspan=1>0.9</td><td rowspan=1 colspan=1>1.0</td></tr><tr><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>0.015</td><td rowspan=1 colspan=1>0.03</td><td rowspan=1 colspan=1>0.06</td><td rowspan=1 colspan=1>0.12</td><td rowspan=1 colspan=1>0.23</td><td rowspan=1 colspan=1>0.4</td><td rowspan=1 colspan=1>0.55</td><td rowspan=1 colspan=1>0.65</td><td rowspan=1 colspan=1>0.8</td><td rowspan=1 colspan=1>0.95</td></tr><tr><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>0.01</td><td rowspan=1 colspan=1>0.02</td><td rowspan=1 colspan=1>0.04</td><td rowspan=1 colspan=1>0.08</td><td rowspan=1 colspan=1>0.16</td><td rowspan=1 colspan=1>0.3</td><td rowspan=1 colspan=1>0.5</td><td rowspan=1 colspan=1>0.6</td><td rowspan=1 colspan=1>0.7</td><td rowspan=1 colspan=1>0.9</td></tr></table>

利用正交表的设计组合计算得到27组有限元结果，可以得到各个因（设计变量）对响应的主效应，即因子在某个平时所有试验中响应的平均值。各个设计变量的主效应图如图3-18所示。图中分别给出了叶的最等效应 $S _ { \mathrm { e q v } }$ 、最大径向位移 $U _ { x }$ 以及等效应力差 $\Delta S$ ，等效应力差 $\Delta S$ 定义为叶背与叶盆相同叶处的VonMises等效应差，这个参数主要用来描述叶的应力均匀性特征。

从设计变量的主效应图变化可以看出以下点。

（1）设计变量对叶等效应的影响：从总体上来看，靠近叶根的设计变量$( R _ { 1 } \sim R _ { 5 }$ ）对叶等效应的影响规律并不致， $R _ { 3 }$ : $R _ { 4 }$ 增大时叶片的等效应力降低，$R _ { 1 }$ 、 $R _ { 5 }$ 增时叶身应增大，而叶身的等效应随 $R _ { 2 }$ 的变化体现出先增后减的趋势；叶身中部及靠近叶尖处的设计变量（ $R _ { 6 } \sim R _ { 9 }$ ）对叶身应力的影响规律较为致，均体现出随设计变量的增大应上升的趋势， $R _ { 1 0 }$ 对叶的应影响较。

（2）设计变量对叶叶盆、叶背间等效应力差 $\Delta S$ 的影响：叶片的各个设计变量（除 $R _ { 3 }$ 外）增时，叶盆与叶背相同叶处的等效应差也增大，这表明将叶各基元流面由叶盆向叶背旋转时会加剧整个叶身的应不均匀趋势。

（3）设计变量对叶变形的影响：各个设计变量对叶径向变形呈现出不同的影响规律。靠近叶根处的基元流( $R _ { 1 } \sim R _ { 3 }$ ）对叶的径向变形影响很，乎呈现条水平线；设计变量 $R _ { 4 } \sim R _ { 6 }$ 与叶的径向变形负相关，随着设计变量 $R _ { 4 } \sim R _ { 6 }$ 的增大，叶径向变形减小；而设计变量 $R _ { 7 } \sim R _ { 1 0 }$ 增时，叶径向变形增。

![](images/d142200bf83c555a50bf1c5ea0e1f218ea5511868b1863ae34f8416895a9df57.jpg)  
图3-18 设计变量的主效应图

# 3.4.2.2 基于序列二次规划算法的径向积叠优化

由上述正交试验分析可以初步得到各个设计变量对标函数的影响规律，但由于这种法主要由设计员观察分析完成，设计效率和精度均较难保证。特别是对于多变量、多标的优化问题，其效、直观的优势就很难体现出来。因此，对于实际的优化问题，仍需要寻求效的优化算法来完成优化分析。序列次规划算法是当前泛应的梯度类算法之，能够有效地求解线性约束最优化问题。因此，本节采该算法进空风扇叶的径向积叠优化，并对积叠线的不同参数化法对设计结果的影响。

有限元计算的边界条件为叶片根部固支，施加工作转速，叶片表面施加气体压力，计算时考虑何线性效应。优化的约束条件仍为最等效应不超过 $4 1 0 . 6 \mathrm { M P a }$ （由Goodman曲线给定）。优化的标函数为叶相同叶处叶盆与叶背间的应差 $\Delta S$ 最，设计变量为叶不同叶处沿周向的旋转。

于是，该优化问题的数学模型可以表示为

$$
\begin{array} { r l } & { \mathrm { F i n d } \quad Y = ( R _ { 1 } , R _ { 2 } , R _ { 3 } , R _ { 4 } , R _ { 5 } , R _ { 6 } , R _ { 7 } , R _ { 8 } , R _ { 9 } , R _ { 1 0 } , \theta ) } \\ & { \mathrm { m i n } \quad \operatorname* { m a x } \left| \Delta S _ { \mathrm { c l } } , \Delta S _ { \mathrm { c 2 } } , \cdots , \Delta S _ { \mathrm { c v } } \right| } \\ & { \mathrm { s . t . } \quad S _ { \mathrm { e q v } } ( Y ) \leqslant \sigma _ { \mathrm { m a x } } } \\ & { \quad \quad Y _ { \mathrm { l o w e r } } \leqslant Y \leqslant Y _ { \mathrm { u p p e r } } } \end{array}
$$

其中：Y——优化变量设计空间；

$R _ { i }$ $i = 1$ ，2，…，10）不同叶截的周向旋转所占叶尖旋转的百分；  
$\theta ^ { \smash { \cdot } }$ —叶尖处周向旋转度；  
$\Delta S _ { \mathrm { c } j }$ (d:) $j = 1$ ,2，…, $N$ ）—叶盆、叶背等叶处等效应差的绝对值；  
$Y _ { \mathrm { u p p e r } }$ , $Y _ { \mathrm { l o w e r } }$ —设计变量的上、下界。

优化设计变量共11个，即 $R _ { i }$ （ $i = 1$ ，2，…，10）和叶尖处周向旋转角 $\theta$ ，其中 $R _ { 1 }$ 为叶根处的设计变量， $R _ { 1 0 }$ 为叶尖处的设计变量。各层截旋转的百分比取值区间在表3–7中给出，叶尖处实际旋转角 $\theta$ 的取值区间为 $[ - 1 . 5 ^ { \circ } , 1 . 5 ^ { \circ } ]$ o

根据11个设计变量的取值即可实现对叶积叠线的控制，分别采用分段线性插值、三次样条曲线和B样条曲线描述旋转角沿叶高的分布曲线，值得注意的是，积叠线的设计是通过在基础叶型上添加附加量的法，因此得到的最优曲线（分段线性插值、三次样条、B样条）为旋转的变化曲线，叶的径向积叠线形状。

采序列次规划算法进优化设计，结果见表3-8。表中分别给出了三种设计曲线的最优结果，设计变量的初值均相同。不同设计曲线的最优结果见表3-9，表中同时给出了优化分析的收敛步数信息。从优化结果可以看出，三次样条曲线给出的标函数值最小，叶身最大应力差为 $1 0 9 . 9 \mathrm { M P a }$ ，比优化前降低约 $2 1 . 3 \%$ ，但叶身的最大VonMises等效应也其他两种曲线的结果略。图3-19和图3-20分别给出了旋转角 $\theta$ 和标函数（应差ΔS）的迭代过程曲线，三种插值曲线的迭代过程相似。从收敛速度来看，三次样条曲线收敛最慢，B样条曲线所需的迭代次数最少，分段线性插值曲线介于两者之间。

表3-8不同叶型参数化的最优解  

<table><tr><td rowspan=1 colspan=1>方法</td><td rowspan=1 colspan=1>$R{a}$</td><td rowspan=1 colspan=1>$R2}$</td><td rowspan=1 colspan=1>$R3}$</td><td rowspan=1 colspan=1>R4}</td><td rowspan=1 colspan=1>$Rs}</td><td rowspan=1 colspan=1>$Rf}$</td><td rowspan=1 colspan=1>$Rr}$</td><td rowspan=1 colspan=1>$R}$</td><td rowspan=1 colspan=1>$R }$</td><td rowspan=1 colspan=1>R10</td><td rowspan=1 colspan=1>0</td></tr><tr><td rowspan=1 colspan=1>初值</td><td rowspan=1 colspan=1>0.01</td><td rowspan=1 colspan=1>0.02</td><td rowspan=1 colspan=1>0.04</td><td rowspan=1 colspan=1>0.08</td><td rowspan=1 colspan=1>0.16</td><td rowspan=1 colspan=1>0.3</td><td rowspan=1 colspan=1>0.5</td><td rowspan=1 colspan=1>0.6</td><td rowspan=1 colspan=1>0.7</td><td rowspan=1 colspan=1>0.9</td><td rowspan=1 colspan=1>1°</td></tr><tr><td rowspan=1 colspan=1>分段直线</td><td rowspan=1 colspan=1>0.014</td><td rowspan=1 colspan=1>0.020</td><td rowspan=1 colspan=1>0.071</td><td rowspan=1 colspan=1>0.144</td><td rowspan=1 colspan=1>0.239</td><td rowspan=1 colspan=1>0.407</td><td rowspan=1 colspan=1>0.554</td><td rowspan=1 colspan=1>0.654</td><td rowspan=1 colspan=1>0.767</td><td rowspan=1 colspan=1>0.933</td><td rowspan=1 colspan=1>-0.668°</td></tr><tr><td rowspan=1 colspan=1>三次样条</td><td rowspan=1 colspan=1>0.020</td><td rowspan=1 colspan=1>0.020</td><td rowspan=1 colspan=1>0.076</td><td rowspan=1 colspan=1>0.151</td><td rowspan=1 colspan=1>0.222</td><td rowspan=1 colspan=1>0.397</td><td rowspan=1 colspan=1>0.577</td><td rowspan=1 colspan=1>0.628</td><td rowspan=1 colspan=1>0.764</td><td rowspan=1 colspan=1>0.927</td><td rowspan=1 colspan=1>-0.756°</td></tr><tr><td rowspan=1 colspan=1>B样条</td><td rowspan=1 colspan=1>0.016</td><td rowspan=1 colspan=1>0.020</td><td rowspan=1 colspan=1>0.069</td><td rowspan=1 colspan=1>0.148</td><td rowspan=1 colspan=1>0.230</td><td rowspan=1 colspan=1>0.403</td><td rowspan=1 colspan=1>0.566</td><td rowspan=1 colspan=1>0.663</td><td rowspan=1 colspan=1>0.829</td><td rowspan=1 colspan=1>0.951</td><td rowspan=1 colspan=1>-0.615°</td></tr></table>

表3-9不同叶型积叠线参数化方法的优化结果对比  

<table><tr><td rowspan=1 colspan=1>方法</td><td rowspan=1 colspan=1>Seqv/MPa</td><td rowspan=1 colspan=1>∆S/MPa</td><td rowspan=1 colspan=1>U2/mm</td><td rowspan=1 colspan=1>收敛步数</td></tr><tr><td rowspan=1 colspan=1>初始叶型</td><td rowspan=1 colspan=1>410.8</td><td rowspan=1 colspan=1>139.7</td><td rowspan=1 colspan=1>1.83</td><td rowspan=1 colspan=1>一</td></tr><tr><td rowspan=1 colspan=1>分段直线</td><td rowspan=1 colspan=1>394.6</td><td rowspan=1 colspan=1>117.2</td><td rowspan=1 colspan=1>2.04</td><td rowspan=1 colspan=1>163</td></tr><tr><td rowspan=1 colspan=1>三次样条</td><td rowspan=1 colspan=1>401.8</td><td rowspan=1 colspan=1>109.9</td><td rowspan=1 colspan=1>2.14</td><td rowspan=1 colspan=1>184</td></tr><tr><td rowspan=1 colspan=1>B样条</td><td rowspan=1 colspan=1>393.1</td><td rowspan=1 colspan=1>118.9</td><td rowspan=1 colspan=1>1.99</td><td rowspan=1 colspan=1>129</td></tr></table>

![](images/c1d1ba02df904b8fab4987e28ccb78bac00b9862059707783e63009fdb3249fa.jpg)  
图3-19 设计变量随迭代次数的变化

![](images/439080e98747761f7518c66655c56efc422117db05204ed0c61e792923456366.jpg)  
图3-20 标函数随迭代次数的变化

图3-21给出了最优设计参数沿叶高的分布，图中横坐标为叶的截面号（叶根至叶尖），纵坐标分别为截面旋转的百分（图3-21（a））和真实旋转（图3-21（b）），从图中可以看出，由叶根至叶尖向，叶型截面的旋转逐渐增且旋转为负值，这代表叶型截由叶背向叶盆向偏转时有利于减缓叶盆、叶背间的应力不均匀性。对比图3-21（a）和图3-21（b）的分布规律可知，尽管叶型截面调节的百分比相似（各截相对偏移量相似），但由于实际叶尖旋转 $\theta$ 的最优值有较大差异，三种曲线描述式给出的最优 $\theta$ 角分别为 $- 0 . 6 6 8 ^ { \circ }$ , $- 0 . 7 5 6 ^ { \circ }$ 和 $- 0 . 6 1 5 ^ { \circ }$ ，图3-21（b）所示的叶各截面的旋转有差异，其中三次样条曲线的旋转最大，分段线性插值曲线次之，B样条曲线的旋转角最小。

![](images/fc1e4d39a1d7110cc6aeb98d1ef2f8da71df58783ded3c19c08d41629b5b053c.jpg)  
图3-21 不同积叠曲线的最优结果对

图3-22给出了优化前后叶型的对结果，包括未进积叠线优化设计的初始叶型，Ⅰ号叶型为采分段线性插值描述的最优叶型，Ⅱ号叶型为采三次样条曲线描述的最优叶型，Ⅲ号叶型为采B样条曲线描述的最优叶型，可以看出，4个叶型在靠近叶根部位的区域基本重合，在靠近叶尖处，优化后的叶型与初始叶型相，整个叶型由叶背向叶盆向进了旋转。为了更加清晰地察看优化前后叶型的区别，图3-23分别给出了不同叶叶前、尾缘处的叶型轮廓线对比，从图中可以看出，在 $2 5 \%$ 叶处，4种叶型基本重合在一起，随着叶截度的增加，在 $50 \%$ 叶处，初始叶型与优化后的叶型轮廓线已经明显分开，但不同插值曲线的结果差异并不明显，在 $7 5 \%$ 叶处，叶型轮廓线的差异已常明显。

图3-24给出了优化前后叶的VonMises应分布对，从图中可以看出，未进径向积叠设计的初始叶型，其叶盆、叶背间的应力分布差别较大，应力不均匀性比较明显，叶背侧的应区要于叶盆侧的应区，优化后，叶盆侧的应区有所扩，叶背侧的应区缩，但相同叶处的应差异减。

![](images/87cf7ca69cec85758f47d9cbd660d05504de718777440a9e0a9307d7d7222a1a.jpg)  
图3-22 优化前后叶型的对

![](images/9b8a77f95e2aacbd7b3c303da4b38d1b6ae5287ff29ea2e03607bcdad386260b.jpg)  
(a）前缘

![](images/f95571795dcd8ec04405b9b2ec8ba005d3f2e384c65e2d24ae4a2ac5ad8489c5.jpg)  
图3–23 优化前后叶不同叶处叶型截对

![](images/1c9ff6c862af965b69bac2ffa1e0c66e2246a4411524b9b9921238f7c3cb4740.jpg)  
图3-24 优化前后叶 $\mathrm { V o n \ M i s e s }$ 等效应力对比

# 3.4.3 多目标下的径向积叠优化

3.4.3.1多目标优化设计模型

对于实际的工程设计问题，往往需要考虑多个因素的限制和要求，优化设计的目标也需要是多个标的综合最优，即多标优化问题。不妨假设求标函数的最值，则可用如下的数学模型进行描述[15]

$$
\begin{array} { r l } & { \{ f _ { 1 } ( X ) , f _ { 2 } ( X ) , \cdots , f _ { m } ( X ) \} } \\ & { g _ { i } ( X ) \leqslant 0 , \quad i = 1 , 2 , \cdots , p } \\ & { h _ { j } ( X ) = 0 , \quad j = 1 , 2 , \cdots , q } \\ & { X _ { \mathrm { l o w e r } } \leqslant X \leqslant X _ { \mathrm { u p p e r } } , \quad X = [ x _ { 1 } , x _ { 2 } , \cdots , x _ { n } ] ^ { \top } } \end{array}
$$

其中： $f _ { i } ( X )$ 优化标函数；

$m$ id: 标函数的个数 $m \geq 2$ );  
$g _ { i } ( X )$ , $h _ { j } ( X )$ -不等式约束和等式约束条件；  
$p$ , $q$ —约束条件的个数；  
$X$ (i: 设计变量；  
$n$ id: 设计变量个数；  
$X _ { \mathrm { u p p e r } }$ , $X _ { \mathrm { l o w e r } }$ (id:) 设计变量的上、下界。

多标优化问题要求多个标都达到最优，如果能够获得组这样的解，当然是最理想的。然而，对于实际工程问题，这些设计目标之间往往是互相矛盾的，这使得多目标优化很难获得组绝对的最优解，只能得到问题的劣解，且劣解不个。

多标优化法体上可以分为间接法和直接求解法。间接法是对多标优化问题进适当处理，将多标问题转换为单标函数（评价函数）的类法，需要由决策者预先给出各个标的优劣，如加权准则法、主要标法等。对于实际程问题，确定目标函数之间的优劣往往是非常困难的。近年来，借鉴生物学、物理学发展起来的智能优化算法在处理多标优化问题中得到了很好的应用。这其中以由德布（Deb）及其学生提出的带精英策略的NSGA-Ⅱ算法应用最为广泛，他们在非支配排序遗传算法（nondominated sorting genetic algorithm，NSGA）的基础上引“拥挤度距离排序”的思想，即对相同Pareto顺序层内的个体进排序，以保证解的宽性和均匀性。由于该法是求解多个标函数的Pareto解集，不需要对标函数进量纲化和分配权重的处理，使得NSGA-Ⅱ算法的应范围十分宽。

基于NSGA-Ⅱ的良好处理多标优化问题的能，本节采该算法进空风扇叶的多标优化。优化分析仍以叶的最等效应作为约束条件，优化的标函数为叶的应差和叶的径向位移最，则叶的多标优化问题可以表为

$$
\{ \Delta S ( Y ) , U ( Y ) \}
$$

$$
S _ { \mathrm { e q v } } ( Y ) \leqslant \sigma _ { \mathrm { m a x } }
$$

$$
Y _ { \mathrm { l o w e r } } \leqslant Y \leqslant Y _ { \mathrm { u p p e r } }
$$

式中：ΔS- -叶盆、叶背对应位置处的应差；

$U ^ { . }$ (c 叶的最大径向位移。

# 3.4.3.2 近似替代模型的构建

近似替代模型是利少量的有限元分析结果构建设计变量与标响应之间的显式关系，从避免在优化分析时反复进耗时的有限元计算。设计变量的数量对于近似替代模型的精度以及优化设计效率均有较影响，过多的设计变量容易降低响应面模型的近似精度，因而选取对目标函数影响显著的设计参数，剔除一些次要参数在优化分析中是十分必要的。由正交试验的分析结果可知，靠近叶根处的设计变量 $R _ { 1 } \sim R _ { 3 }$ 对叶径向变形的影响并不分明显，靠近叶根处的叶型截周向移动的范围有限，另一方面叶靠近叶根处的弯扭程度较小，对叶的径向变形影响较。因此，在进多标优化分析时将这3个设计变量作为常量对待，这样设计变量减少为 $R _ { 4 } \sim R _ { 1 0 }$ 共7个设计变量，叶尖处的实际旋转初始给定。叶的径向积叠规律由B样条曲线控制。

根据前述分析，7个输变量的阶响应模型包含36项拟合系数，输出变量为应力差ΔS、叶最大等效应 $S _ { \mathrm { e q v } }$ 以及叶最径向位移 $U _ { x }$ 。采中组合设计法成143个初始样本点，构建得到3个输出变量的阶响应模型，复相关系数 $R ^ { 2 }$ 分别为0.966，0.998和0.997。为了进步考察近似替代模型的精度，随机产10个样本考核点，有限元计算结果与近似替代模型的对结果在表3-10中给出，从计算结果可以看出，替代模型的预测结果与实际有限元解比较接近，应差 $\Delta S$ 的最大相对误差为$2 . 3 \%$ ，叶最VonMises等效应和叶径向位移的最相对误差更，分别为$0 . 2 2 \%$ 和 $0 . 0 3 \%$ 。这说明所构造的近似替代模型具有较精度，可以将其应于后续的多标优化分析中。

表3-10 有限元计算结果与替代模型预测值对比  

<table><tr><td rowspan=2 colspan=1>序号</td><td rowspan=1 colspan=3>有限元计算结果</td><td rowspan=1 colspan=3>替代模型预测结果</td><td rowspan=1 colspan=3>相对误差/%</td></tr><tr><td rowspan=1 colspan=1>ΔS/MPa</td><td rowspan=1 colspan=1>Seq/ Pa</td><td rowspan=1 colspan=1>$U2/mm</td><td rowspan=1 colspan=1>ΔS/MPa</td><td rowspan=1 colspan=1>Seqy/MPa</td><td rowspan=1 colspan=1>$U₂/mm</td><td rowspan=1 colspan=1>ΔS</td><td rowspan=1 colspan=1>Senr</td><td rowspan=1 colspan=1>Ux</td></tr><tr><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>122.86</td><td rowspan=1 colspan=1>401.34</td><td rowspan=1 colspan=1>1.93</td><td rowspan=1 colspan=1>121.92</td><td rowspan=1 colspan=1>400.78</td><td rowspan=1 colspan=1>1.93</td><td rowspan=1 colspan=1>0.76</td><td rowspan=1 colspan=1>0.14</td><td rowspan=1 colspan=1>0.01</td></tr><tr><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>120.80</td><td rowspan=1 colspan=1>398.58</td><td rowspan=1 colspan=1>1.97</td><td rowspan=1 colspan=1>118.03</td><td rowspan=1 colspan=1>399.45</td><td rowspan=1 colspan=1>1.97</td><td rowspan=1 colspan=1>2.29</td><td rowspan=1 colspan=1>0.22</td><td rowspan=1 colspan=1>0.00</td></tr><tr><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>120.61</td><td rowspan=1 colspan=1>397.18</td><td rowspan=1 colspan=1>2.01</td><td rowspan=1 colspan=1>120.95</td><td rowspan=1 colspan=1>397.75</td><td rowspan=1 colspan=1>2.01</td><td rowspan=1 colspan=1>0.28</td><td rowspan=1 colspan=1>0.14</td><td rowspan=1 colspan=1>0.02</td></tr><tr><td rowspan=1 colspan=1>4</td><td rowspan=1 colspan=1>123.83</td><td rowspan=1 colspan=1>391.80</td><td rowspan=1 colspan=1>2.00</td><td rowspan=1 colspan=1>123.73</td><td rowspan=1 colspan=1>392.40</td><td rowspan=1 colspan=1>2.00</td><td rowspan=1 colspan=1>0.07</td><td rowspan=1 colspan=1>0.15</td><td rowspan=1 colspan=1>0.02</td></tr><tr><td rowspan=1 colspan=1>5</td><td rowspan=1 colspan=1>128.76</td><td rowspan=1 colspan=1>399.25</td><td rowspan=1 colspan=1>2.00</td><td rowspan=1 colspan=1>127.68</td><td rowspan=1 colspan=1>398.90</td><td rowspan=1 colspan=1>2.00</td><td rowspan=1 colspan=1>0.84</td><td rowspan=1 colspan=1>0.09</td><td rowspan=1 colspan=1>0.02</td></tr><tr><td rowspan=1 colspan=1>6</td><td rowspan=1 colspan=1>119.22</td><td rowspan=1 colspan=1>393.69</td><td rowspan=1 colspan=1>1.99</td><td rowspan=1 colspan=1>118.09</td><td rowspan=1 colspan=1>394.13</td><td rowspan=1 colspan=1>1.99</td><td rowspan=1 colspan=1>0.95</td><td rowspan=1 colspan=1>0.11</td><td rowspan=1 colspan=1>0.01</td></tr><tr><td rowspan=1 colspan=1>7</td><td rowspan=1 colspan=1>119.65</td><td rowspan=1 colspan=1>390.43</td><td rowspan=1 colspan=1>1.94</td><td rowspan=1 colspan=1>118.99</td><td rowspan=1 colspan=1>390.44</td><td rowspan=1 colspan=1>1.94</td><td rowspan=1 colspan=1>0.55</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.02</td></tr><tr><td rowspan=1 colspan=1>8</td><td rowspan=1 colspan=1>123.22</td><td rowspan=1 colspan=1>402.32</td><td rowspan=1 colspan=1>2.01</td><td rowspan=1 colspan=1>120.85</td><td rowspan=1 colspan=1>401.82</td><td rowspan=1 colspan=1>2.01</td><td rowspan=1 colspan=1>1.92</td><td rowspan=1 colspan=1>0.13</td><td rowspan=1 colspan=1>0.03</td></tr><tr><td rowspan=1 colspan=1>9</td><td rowspan=1 colspan=1>130.24</td><td rowspan=1 colspan=1>388.64</td><td rowspan=1 colspan=1>1.99</td><td rowspan=1 colspan=1>128.15</td><td rowspan=1 colspan=1>388.62</td><td rowspan=1 colspan=1>1.99</td><td rowspan=1 colspan=1>1.61</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.03</td></tr><tr><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>121.81</td><td rowspan=1 colspan=1>396.45</td><td rowspan=1 colspan=1>2.02</td><td rowspan=1 colspan=1>122.21</td><td rowspan=1 colspan=1>396.92</td><td rowspan=1 colspan=1>2.02</td><td rowspan=1 colspan=1>0.33</td><td rowspan=1 colspan=1>0.12</td><td rowspan=1 colspan=1>0.02</td></tr></table>

# 3.4.3.3 多目标下的径向积叠优化

利用所建的阶多项式响应面模型和NSGA-Ⅱ遗传算法进优化分析，初始种群数给定为12，交叉概率取0.9，经过100代的遗传运算，优化结果如图3–25所示。图中块点为得到的组分布均匀的Pareto解，这组解中的任何个都不代表它优于其他解，这些解在两个不同设计标上都具有各的优势。Pareto前沿的存在进步说明并不存在一个最优设计组合能够使所有目标函数均达最优，还需要设计人员根据实际工程需要加以选择。优化标的历程曲线如图3–26所。

![](images/0424d3d7f54b3f5f013716708906f1211e059477401af47579d7c9acabd3e18a.jpg)  
图3-25 多标优化的Pareto前沿

![](images/be92b1753ad4257b43475158d57b4eddbd9a5a04b04ccee1719edf3f938ca000.jpg)  
图3-26 径向位移和应差的优化历程曲线

# 参考文献

[1刚铁．宽弦空风扇叶结构设计及强度分析研究[D．南京：南京航空航天学，2005.

[2]杨剑秋，基于应有限元分析的空风扇叶结构优化研究D．北京：北京航空航天大学，2011.

[3] Mahajan A J, Stefko G L. An iterative multidisciplinary analysis for rotor blade shape de-termination [R]. AIAA -93-2085, 1993.  
[4] 茆诗松，周纪芗，陈颖.试验设计 [M．北京：中国统计出版社，2004.  
[5] Box G E P, Wilson K B. On the experiment attainment of optimum conditions [J]. Jour-nal of Royal Statistical Society, 1951, 13: 1–45.  
[6] Vafaeesefat A. Optimization of composite pressure vessels with metal liner by adaptive re-sponse surface method [J]. Journal of Mechanical Science and Technology, 2011, 25（11）：2811-2816.  
[7]新理.结构优化设计[M]．郑州：黄河利出版社，2008.  
[8] 王四春.遗传程序设计技术及应研究[M].长沙：中南学出版社，2006.  
[9] 唐焕，秦学志.实最优化法[M]．连：连理学出版社，2007.  
[10]北京航空材料研究院．航空发动机设计材料数据册[M]．北京：中国航空发动机总公司，1989.  
[11]郝勇，李志强，杜发荣，等．涵道涡扇发动机的宽弦空风扇叶技术研究[C]．型飞机关键技术层论坛暨中国航空学会2007年学术年会，2007.  
[12]杨剑秋，王延荣，基于正交试验设计的空叶结构优化设计[J．航空动学报，2011，26（2)：376-384.  
[13] Jang C M, Kim K Y. Optimization of a stator blade using response surface method in a sin-gle- stage transonic axial comopressor [C]//Proceedings of the Institution of MechanicalEngineers, Part A: Journal of Power and Energy, 2005, 219 (8): 595–604.  
[14] Kalyanmoy D, Amrit P, Sameer A, et al. A fast and elitist multiobjective genetic al-gorithm: NSGA–Ⅱ [J]. IEEE Transactions on Evolutionary Computation, 2002, 6(2）:182-197.  
[15陈国栋.基于代理模型的多标优化法及其在车设计中的应[D]．长沙：

湖南大学,2012.

# 第4章 圆弧形榫连结构接触分析及寿命预测

# 4.1引言

榫连结构是航空发动机中常用的连接结构，叶片榫头和轮盘榫槽在接触面上存在较大的接触应力，受发动机工况和振动的影响，榫头/榫槽间会出现较小的相对滑移，由此引起的接触疲劳、微动疲劳是常见的造成榫连结构破坏的形式[1.2]。圆弧形榫连结构是前宽弦空风扇叶泛采用的连接结构，在叶数定的前提下，榫头的圆弧形设计有助于减轮毂直径，从而实现发动机的减重。

开展榫连结构的微动疲劳试验，探索微动载荷下结构的失效机理，是解决微动疲劳问题的基础。由于影响微动疲劳的因素繁多，诸如接触几何特征、载荷条件、材料等，这增加了榫连结构微动疲劳失效研究的难度，也促使研究针对特定的关键因素展开，并进恰当的简化和假设。在试验研究方面，根据试验件的形式不同可以划分为两类：是以研究微动疲劳失效机理为的的简化试验件，典型的试验装置是“桥式”微动试验装置及其改型装置，如圆柱形冲头/平板接触、带圆平板/平板接触等，尽管这类试验装置与榫连结构的受状态有定的相似性，但与真实结构仍有不差距；第种试验研究则采榫连结构的模拟件，鲁伊斯（Ruiz）等[3]较早地设计了双轴拉伸试验装置来模拟叶的离和轮盘的周向载荷。近年来，拉贾斯卡兰（Rajasckaran）和诺埃尔（Nowell)[4]采了类似的试验装置，并且可以实现振动载荷的模拟，这类试验的特征是采用真实的榫连结构设计，对载荷条件进一定的等效和简化。国外在榫连结构及其微动疲劳已经开展了量的研究，相对国内对于榫连结构的设计和研究起步较晚，特别是相关试验数据及理论研究还比较缺乏，所开展的研究工作普遍针对平直型榫连结构进。

由于微动疲劳问题的重要性和复杂性，微动疲劳的数值模拟研究同样至关重要，数值模拟先需要准确获得接触应力并据此建合适的失效分析模型。接触问题的求解大体上可以分为解析法和数值求解两大类。总体上来说，解析法对于解决实际结构的接触问题还是比较困难的，实际问题更多地应用数值方法进分析，其中以有限元方法应最为泛，但有限元格的疏密对接触应求解的精度具有重要影响。Rajasckaran和Nowell[5]采模型法对经典的卡塔内奥-明德林（Cattaneo-Mindlin）接触问题进了研究，并对了不同接触算法对该问题的求解精度。魏盛等[6]则对榫连结构接触分析中的网格要求进了比较细致的研究，这些数值研究工作都极具借鉴意义。

# 4.2 圆弧形榫连结构低循环疲劳试验

# 4.2.1试验件设计

针对涵道比涡扇发动机的风扇叶/盘圆弧形榫连结构，设计了圆弧形榫头试验件及其试验夹具装置，以考察圆弧形榫连结构的疲劳特性。采用航空发动机广泛应用的钛合TC4作为试验件材料，相近牌号为 $\mathrm { T i } - 6 \mathrm { A l } - 4 \mathrm { V } _ { \mathrm { \Omega } }$ TC4是一种中等强度的 $\alpha - \beta$ 型两相钛合金，含有 $6 \% \mathrm { ~ d ~ }$ 稳定元素Al和 $4 \% \beta$ 稳定元素 $\mathrm { V }$ ，晶粒尺寸在 $1 0 \sim 2 0 \mu \mathrm { m }$ 。材料性能如下：弹性模量为 $1 0 9 \mathrm { G P a }$ ，泊松比为0.34，密度为 $4 4 4 0 \mathrm { k g / m } ^ { 3 }$ ，屈服强度$8 8 0 \mathrm { M P a }$ ,拉伸强度 $9 3 8 \mathrm { M P a }$

为简化试验过程的复杂性，暂不考虑温度载荷，并假定叶的离心弯矩与气动弯矩相抵消，仅考虑叶离心载荷的径向分量。因此，圆弧形榫连结构低循环疲劳试验可简化为拉伸疲劳试验。榫头试验件的设计尺寸如图4-1所，榫头试验件度为 $1 6 0 \mathrm { m m }$ ,榫头轴向长度为 $9 6 \mathrm { m m }$ ，轴向圆弧半径为 $1 3 2 \mathrm { m m }$ ，接触面倾为 $5 5 ^ { \circ }$ 。

![](images/87c306d6b8c6b0189fa4b3a68ca0051288a8b8d4b58fd4a494e9ff8d463aa978.jpg)  
图4-1 圆弧形榫头试验件及其设计尺寸

# 4.2.2 试验过程及结果

众所周知，榫连结构的微动损伤主要由以下两种载荷引起：一是与叶片的离心载荷变化有关，当叶片、轮盘的转速逐渐升高时，由于离心力的变化导致榫头与榫槽接触面间出现相对滑动，转速的变化主要发生在飞机起飞或降落阶段，离心载荷主要引起低循环疲劳问题；第二类载荷是叶所承受的振动负荷，主要包括由上游叶片排尾迹或来流畸变等引起的强迫振动，高频的振动应力容易造成结构的高循环疲劳失效。因此，试验装置设计的关键是准确模拟叶的惯性力以及振动载荷，一些试验研究均取得了较为满意的模拟效果。然而，过于复杂的试验装置设计也可能对试验结果的分析带来困难，例如，在试验中同时存在离载荷与振动载荷时，往往难以区分导致试件失效的关键因素。

因此，为了简化试验的复杂性，本仅针对榫连结构的低循环疲劳问题展开研究，仅考虑离心载荷的作用，则试验装置可以设计为拉伸试验。为了最大程度地消除试验中

的不利因素影响，再现榫连结构实际工作状态下的微动特征，试验采用双榫头的拉伸试验件，试验装置如图4-2所示，圆弧榫头试验件为双榫头模型，榫槽与试验机由一对耳片和一对方向正交的销钉连接，这样设计的一个优点是可以减小附加弯矩的影响。此外采用双榫头设计避免了在试件叶身上打孔，有效防止因应力集中导致叶打孔处发破坏，这样设计的另一个优点是双榫头试件在一次试验时可以完成

![](images/887767b80c1999a86db298cda237e814c0a49e88be0fb721fe0c1c43fe188a51.jpg)  
图4-2 圆弧形榫连结构试验装置

两个部位的试验，缩短了试验时间，并且试件的两个榫头是在相同的试验条件下进试验便于进对比分析。

榫连结构疲劳试验采用Instron8802电液伺服疲劳试验机进，伺服试验系统最大载荷为 $2 5 0 \mathrm { k N }$ ，最大行程为 $5 0 \mathrm { m m }$ 。试验加载波形选梯形波，载荷谱如图4-3所。梯形波的加载时间参数为：加载时间 $\Delta t _ { 1 } = 2 \mathrm { s }$ ，峰值保载时间 $\Delta t _ { 2 } = 2 \mathrm { s }$ ，卸载时间 $\Delta t _ { 3 } =$ 2s，值保载时间 $\Delta t _ { 4 } = 0 . 5 \mathrm { s }$ ，单个低循环疲劳试验的时间周期为6.5s。试验加、卸载的载荷比为 $1 / 1 6$ ，最大试验拉伸载荷分别为16.5t、19.5t和21.5t。试验开始前先对榫头及榫槽进表面清洁，在叶身表面贴应变，然后在榫头、榫槽工作面均匀涂抹润滑剂（二硫化钼），并进装配。将榫槽、榫头与试验机连接后进弯曲程度测量，使得弯曲百分比符合HB52871996试验要求后开始试验，细微调整连接位置，设置试验机试验参数及限位参数，全检查后开始试验。

![](images/242e213777187b123fa2c3972412ee7ee80e2f5e20025c77bee49189a5ac521e.jpg)  
图4-3 试验加载的载荷谱

批完成8件的低循环疲劳试验，其中件试验件为探索试验，分三种载荷平加载，其中有件试验件在试验过程中出现异常，故有效试验件为6件。试验件的试验结果见表4-1。由表4-1可知，从裂纹出现的位置来划分，裂纹出现在上侧榫头的占$60 \%$ ，出现在下侧榫头的占 $40 \%$ 。而从裂纹出现的几何面来划分，凹面与凸面产疲劳裂纹各占 $50 \%$ ，并没有明显区别。

表4-1圆弧形榫头试件低循环疲劳试验数据  

<table><tr><td rowspan=1 colspan=1>序号</td><td rowspan=1 colspan=1>载荷/</td><td rowspan=1 colspan=1>峰值载荷/kN</td><td rowspan=1 colspan=1>谷值载荷/kN…</td><td rowspan=1 colspan=1>疲劳寿命</td><td rowspan=1 colspan=1>裂纹位置</td><td rowspan=1 colspan=1>裂纹长度/mm</td><td rowspan=1 colspan=1>萌生寿命</td></tr><tr><td rowspan=3 colspan=1>1</td><td rowspan=1 colspan=1>16.5</td><td rowspan=1 colspan=1>161.7</td><td rowspan=1 colspan=1>10.11</td><td rowspan=1 colspan=1>60612</td><td rowspan=3 colspan=1>凸面上接触面凸面下接触面</td><td rowspan=3 colspan=1>2268</td><td rowspan=3 colspan=1>83948</td></tr><tr><td rowspan=1 colspan=1>19.5</td><td rowspan=1 colspan=1>191.7</td><td rowspan=1 colspan=1>11.94</td><td rowspan=1 colspan=1>20001</td></tr><tr><td rowspan=1 colspan=1>21.5</td><td rowspan=1 colspan=1>210.7</td><td rowspan=1 colspan=1>13.17</td><td rowspan=1 colspan=1>4436</td></tr><tr><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>21.5</td><td rowspan=1 colspan=1>210.7</td><td rowspan=1 colspan=1>13.17</td><td rowspan=1 colspan=1>39025</td><td rowspan=1 colspan=1>凸面下接触面</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>36500</td></tr><tr><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>19.5</td><td rowspan=1 colspan=1>191.7</td><td rowspan=1 colspan=1>11.94</td><td rowspan=1 colspan=1>2940</td><td rowspan=1 colspan=1>/</td><td rowspan=1 colspan=1>异常</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>4</td><td rowspan=1 colspan=1>19.5</td><td rowspan=1 colspan=1>191.7</td><td rowspan=1 colspan=1>11.94</td><td rowspan=1 colspan=1>62408</td><td rowspan=1 colspan=1>凹面下接触面</td><td rowspan=1 colspan=1>56</td><td rowspan=1 colspan=1>56400</td></tr><tr><td rowspan=1 colspan=1>5</td><td rowspan=1 colspan=1>16.5</td><td rowspan=1 colspan=1>161.7</td><td rowspan=1 colspan=1>10.11</td><td rowspan=1 colspan=1>74700</td><td rowspan=1 colspan=1>凹面下接触面</td><td rowspan=1 colspan=1>61</td><td rowspan=1 colspan=1>68700</td></tr><tr><td rowspan=1 colspan=1>6</td><td rowspan=1 colspan=1>16.5</td><td rowspan=1 colspan=1>161.7</td><td rowspan=1 colspan=1>10.11</td><td rowspan=1 colspan=1>101193</td><td rowspan=1 colspan=1>凹面上接触面</td><td rowspan=1 colspan=1>76</td><td rowspan=1 colspan=1>93690</td></tr><tr><td rowspan=1 colspan=1>7</td><td rowspan=1 colspan=1>19.5</td><td rowspan=1 colspan=1>191.7</td><td rowspan=1 colspan=1>11.94</td><td rowspan=1 colspan=1>44403</td><td rowspan=1 colspan=1>凸面上接触面</td><td rowspan=1 colspan=1>58</td><td rowspan=1 colspan=1>38790</td></tr><tr><td rowspan=1 colspan=1>8</td><td rowspan=1 colspan=1>21.5</td><td rowspan=1 colspan=1>210.7</td><td rowspan=1 colspan=1>13.17</td><td rowspan=1 colspan=1>42550</td><td rowspan=1 colspan=1>凹面上接触面</td><td rowspan=1 colspan=1>49</td><td rowspan=1 colspan=1>38000</td></tr></table>

加载载荷与疲劳寿命的关系（ $S - N$ 曲线）如图4-4所示，程的拟合形式为：$S _ { \mathrm { a } } = A N _ { \mathrm { f } } ^ { \mathrm { B } }$ ，其中 $S _ { \mathrm { a } }$ 为载荷幅， $N _ { \mathrm { f } }$ 为寿命循环数，A、 $B$ 为拟合参数。以1号试验件为例，在试验件两侧榫头均出现了裂纹，其中上侧榫头处裂纹长度约为 $2 2 \mathrm { m m }$ ，下侧裂纹的轴向长度约为 $6 8 \mathrm { m m }$ ，如图4-5所示。

![](images/7ac0ee7647d82aa180e5e8e68775218d5e3fa4497d0fe88297541724e213f287.jpg)  
图4-4 试验加载幅值与疲劳寿命的关系

![](images/173fe6564a6608de75dae5034744cfe22fcf0f13d3f776591ec7af3187c41239.jpg)  
图4-5 1号试验件裂纹位置

# 4.3榫连结构接触有限元分析

# 4.3.1有限元建模

为了获得榫头表面的应力分布特征及其在循环加载下的应力演化规律，首先需要开展榫连结构的接触有限元分析。研究表明接触区边缘存在较大的应力梯度，且网格密度对应的收敛性影响分显著，接触区典型的网格尺寸在微量级，如此细密的网格对于三维模型的计算量是非常巨大的，甚至可能导致计算无法进行，因而现有的研究普遍采维模型（基于平面应或平面应变假设）进分析。

由所设计的榫头试验件结构可知，上下两端榫头完全对称，且单侧榫头在轴向向也存在一个对称面，满足平面应变假设。因此，可以切割该平面作为二维分析模型，利模型的对称性，选取1/2模型进有限元建模，如图4-6（a）所示。接触区内的网格进行细分，网格尺寸为 $8 \mu \mathrm { m } \times 8 \mu \mathrm { m }$ ，与TC4材料的晶粒尺寸在同量级。接触区向接触区的过渡网格进平滑处理，有限元模型共有90156个节点成88918个四节点四边形单元。计算采用平面应变单元，榫头、榫槽的接触表定义为接触对。为便于刻画榫头接触边缘的接触状态特征，图4-6（b）给出了榫头接触上边缘部分区域的节点编号，图中所示区域由沿接触面切向的20个单元（切向长度为 $1 6 0 \mu \mathrm { m }$ )、法向的6个单元组成。在榫头接触区定义局部坐标系， $X ^ { \prime }$ 和 $Y ^ { \prime }$ 分别代表接触表面的切向和法向。接触区边缘的高应力容易使其产生塑性变形，计算时采用 $\mathrm { V o n \ M i s e s }$ 各向同性强化模型作为材料的本构模型。

![](images/3d6b7505eba846a9fed7652e8282354065d781f63430b10ac04f71422a2ad77e.jpg)  
图4-6维有限元分析模型

模型的边界条件为：在对称上的节点施加对称边界条件，榫槽底部节点约束Y向位移，榫头上表面施加试验的拉伸载荷。由于接触分析的非线性特征，加载时需设置足够小的载荷增量以保证收敛性。

# 4.3.2 接触应力分布特征

榫连结构接触区内存在典型的多轴应力状态，为了获得沿接触面表面以及接触面内部的应力分布规律，重点关注垂直于接触表面的应力梯度特征，定义沿接触面的应力分布路径1和路径2如图4-7所，路径1为沿接触面的切向向，起点位于直线段与圆弧段转接处，路径2为沿接触面法线方向（指向榫头内部），起点位于接触表面。

不同试验载荷下（16.5tf/19.5tf/21.5tf）沿路径1的应力分布如图4-8所示，图中分别给出了切向正应力 $\sigma _ { \iota }$ 、法向正应力 $\sigma _ { n }$ 以及剪切应力 $\tau$ 的分布规律，由图中可以看出不同载荷平下的应力分布趋势基本一致，呈现出多轴应力特征：在接触区上边缘切向正应力 $\sigma _ { \scriptscriptstyle 1 }$ 由拉应力突变为压应力，这与冲头/平板接触的应力特征相似，不同试验载荷下的最切向正应分别为 $6 0 4 . 7 \mathrm { M P a } ,$ 704.6MPa和 $7 8 9 . 3 \mathrm { M P a }$ ；法向正应力的分布可以表征接触区域的大小，从图中可以看出，沿榫头接触面的接触区长度约为 $5 \mathrm { m m }$ ；剪切应力水平较低，在 $4 0 \sim$ 50MPa之间，这与表面较低的摩擦因数有关，但在接触区边缘存在剪应力的突变。

![](images/ab20839758b70f3b83f9d5a22d6b602d1abdfe9f9d8e2c2d83e4658cda325dec.jpg)  
图4-7 应分布路径的定义（路径1/路径2)

![](images/c45bc3acfcf9b87da050903b06da73a66f5e49eae364185b85319d87d37e43bf.jpg)  
图4-8 沿路径1的应力分布

图4-9给出了沿路径2（接触面法向）的应分布规律，起点位于接触表（距路径1起点的距离约为 $0 . 9 6 \mathrm { m m }$ )。从图中可以看出，接触区边缘存在高应力梯度特征，随着指向表面内部深度的增加，切向正应力逐渐减小并逐渐趋于一个定值；表面的法向正应力和剪切应力均为0，随着距离的增加而逐渐增大，最大的剪切应力出现在榫头内部，这与赫兹（Hertz）接触形式的剪切应分布类似[7]。

![](images/26f7454321248415348d91cac5ce87b3d72f9407ccb87aec7af8ee8373fb91ad.jpg)  
图4-9 沿路径2的应分布

# 4.3.3 接触状态特征

由上述分析可知，榫连结构接触区存在复杂的多轴应状态，接触区边缘的峰值应和应梯度特征均对其疲劳寿命具有重要影响。此外，在加载、卸载过程中，由于接触面的法向压力以及摩擦力的变化，接触面间容易出现相对滑动，这也是微动疲劳与常规疲劳问题的关键区别之。在循环加载过程中，接触区域特别是接触边缘会出现接触状态的变化，这的接触状态指的是接触体的接触和分离两种状态。接触状态的变化会导致应的峰值点的移动，并最终影响裂纹萌位置的变化，另接触问题伴有微动磨损的影响是典型的需要考虑时间历程的疲劳问题。

法向正应的变化是表征接触状态（接触、分离）的理想参量，接触体发接触时，由于相互的压紧作用，接触表面的法向正应力为压应力，而当接触体分离时，其接触面成为由表，法向正应减为零。这以16.5tf的试验载荷平分析为例，计算试验件在单调拉伸载荷下的应/应变响应。计算的终时间为1，加载过程中固定时间步长并划分为30个步，计算得到榫头接触区上边缘处部分节点的法向正应随加载步的变化如图4-10所。从图中可以看出，节点8715在加载过程中法向应基本为0，表明该节点始终未与榫槽发接触，节点8716随着外载荷的升，压应先增后减最后趋近于0，可以判断其为初始接触边缘，节点8717与8718表现出类似的应变化特征，不同点在于法向应减为0的时间不同。节点8719与节点8720在加载时刻为1时的法向正应力并不为0，表明该位置是接触的，因而可以判断节点8719为载荷最时的上接触边缘。由上述分析不难发现，榫头接触表的初始接触位置（节点8716）并不是最终的接触位置（节点8719）。

![](images/fc20cf8a705639882194a536efe6d32a13a90066aea0142fce460c7730069051.jpg)  
图4-10 不同节点处的法向正应力随加载时间的变化

为了更形象地说明接触状态的变化，图4-11给出了接触状态变化的示意图，初始接触边缘为节点8716，接触体发变形后，最终接触边缘变为节点8719，而节点8716已经滑出榫头/榫槽接触区外部，成为自由表面。可以看出，榫头表面滑出榫槽段长度约 $2 4 \mu \mathrm { m }$ ，体现出微动特征。出现这种接触状态变化的原因在于榫头与榫槽接触间存在两种作用，即相互压紧和滑动的运动趋势，当外部拉伸载荷增大时，榫头与榫槽的接触面相互压紧，同时，摩擦阻力也增大；同时，由于拉力的作用，榫头出现滑出榫槽的趋势。当切向拉分量于摩擦阻时，榫头表现出滑出榫槽的趋势，若切向拉分量于摩擦阻时，榫头与榫槽表现出压紧的状态。需要说明的是接触区域的小不仅受接触状态的影响，同时接触体的形变也会影响接触区域的大，如接触边缘的圆角发生变形使接触区增大，若接触面为直线段即完全接触状态，如平角冲头/平板接触模型，那么接触体的形变将不会影响接触区域的大小。

![](images/6d82acf46cb1b98ddf7ab80cf4203752584c7a96cd2870c6c3107ab6d2fd51a1.jpg)  
图4-11 接触区接触状态变化示意图

加载过程中的切向正应力与剪切应力的变化如图4-12所示。从切向正应力变化过程来看，在初始载荷较小的情况下，榫头接触边缘切向正应力为压应力（节点8715除外），随着载荷的增大切向压应先增后减，当拉伸载荷进一步增时切向正应最终转为拉应。出现这种分布趋势的原因是在载荷较的情况下，榫头与榫槽之间先压紧，在短的时间历程内由于载荷的增大，其接触切向正应力和法向应力都增大，但随着载荷的继续增，榫头与榫槽之间出现相对滑动，榫头靠近接触边缘的区域逐渐滑出榫槽，而与榫槽不再接触，因此会出现切向正应力逐渐变为拉应力，并随着加载的进一步增大，拉应力也达到最大值，而法向正应力由于榫头滑出榫槽外，其接触压最终接近于0。剪切应在加载过程中存在向变化，主要是由接触区边缘的接触状态变化所引起。

![](images/473e22ea9fec6c5ebfeb0170d638524e91a4a91902be50611a4e67664d93b5aa.jpg)  
图4-12 接触区边缘切向正应与剪切应随加载时间的变化

# 4.3.4 循环加载下的接触分析

从接触区的应力分布特征和接触状态变化的分析可以看出，榫连结构接触表面在加载过程中体现出应平和复杂接触状态的特征。一些研究指出，控制结构疲劳寿命的参量并不仅是最应/应变，个循环内的应/应变变程对微动疲劳寿命的影响同样分显著[8,9]。因此，有必要对榫连结构在循环加载下的应、应变响应进模拟分析。

为了考察在循环加载条件下的应变化特征，开展了循环载荷下的接触分析，有限元计算施加的载荷谱如图4–13所。计算分为3个循环，每个载荷步划分为60个步共180个步，根据试验加载条件，最大载荷分别为16.5tf、19.5tf和21.5tf，载荷为1/16。

计算得到圆弧榫接触上边缘处节点的应随加载子步的变化如图4-14所，加载载荷为16.5tf。由图4-14（a）中不

![](images/b84485ec9a7c07bb27d2ef448c80873826df3b644c8df99e7e6ba086314a752d.jpg)  
图4-13 加载载荷谱

同节点位置的应力变化规律可以看出，节点位置越靠近接触区内部，其最大切向正应力（拉应力）越小，而最小切向正应力（压应力）则增大；此外，节点的应力变化均表现为先压后拉的总体趋势，这与单调拉伸载荷下的应演变规律相一致（见图4-12（a））。图4-14（b）给出的法向正应力变化与单调拉伸载荷作用下的应力变化规律致，即随着外载增，法向正应逐渐增同时伴有接触间的相对滑动，当载荷达到最大时，靠近接触上边缘的部分结点滑出接触区不再接触；卸载时，滑出接触区的节点又重新滑接触区，此时的法向正应不再为0，节点8715的应演化规律与其他节点不同，主要是由于该节点始终与榫槽表未接触（法向正应始终为0）。图4-14（c）给出了接触区边缘剪切应的变化规律，可以看出在加载、卸载过程中剪切应力存在应力方向的转变，这主要是由于摩擦力总是阻碍接触的相对运动，加载时，榫头呈现出滑出榫槽的趋势，即摩擦向为沿接触切向指向榫槽内侧，而在卸载时，摩擦力方向转变为沿接触面切向指向榫槽外侧，即在个循环中存在着应向的转换。

![](images/74eb3245a66746879be85793df6ed22feca95a2fdeae86a77dc6311d1ebcb178.jpg)  
图4–14 接触区边缘应随加载步的变化

研究表明结构件在个加载循环内所经历的应/应变变程对其疲劳寿命具有重要影响，因而有必要关注榫连结构的应/应变变程分布，为其疲劳寿命预测奠定基础。这里重点关注接触区边缘位置的应力变程变化特征，选取节点编号为 $8 7 1 5 \sim 8 7 3 3$ 共19个节点进应变程分析，利用有限元的分析结果可以计算得到每个节点在一个循环内的应力变程 $\Delta \sigma = \sigma _ { \operatorname* { m a x } } \mathbf { \Sigma } - \sigma _ { \operatorname* { m i n } }$ 。其中 $\sigma _ { \mathrm { m a x } }$ (i:) $\sigma _ { \mathrm { m i n } }$ 分别为个循环内的最应和最应。图4-15给出了16.5tf试验载荷下榫头接触区边缘的应变程分布。

![](images/c2d4566b07a85fdc52e5bdaa1b89776b57a73a43d479d02f4da778c68a00e9ca.jpg)  
图4-15 接触区边缘的应变程分布（16.5tf)

从图中可以看出，不同向的应分量变化规律不同，其中切向正应变程呈现出先增后减小的趋势，应变程最大点位于节点8718，其值为 $1 0 0 7 . 9 \mathrm { M P a }$ ，由前述的接触状态分析可知，节点8718既不是初始接触位置（节点8716）也不是最终的接触边缘（节点8719），而是位于初始接触边缘和最载荷状态下接触边缘之间，这说明在确定裂纹萌生位置时，仅以最大载荷下的峰值应力点作为判断依据是不准确的。法向正应变程与剪切应变程同样体现出先增大后减的变化趋势，最法向正应变程位于节点8726（ $\Delta \sigma _ { \mathfrak { n } } = 7 8 1 . 2 \mathrm { M P a } \ $ ，距离最大切向正应力变程位置的距离为 $6 4 \mu \mathrm { m }$ 。最剪切应变程点位于节点8728（ $\Delta \tau = 3 1 7 . 2 \mathrm { M P a } )$ 。由前述分析可知，最大法向正应变程和剪切应变程所在的位置在加载、卸载过程中始终处于接触状态。

图4-16给出了不同载荷平下的应变程分布，由图中可以看出，当载荷平升高时各应力变程的最大值增大，同时出现的位置也发生移动。以切向正应力变程的分布为例，载荷升高时最大应力变程位置向接触区内部方向移动，这是由于当载荷水平升高时，沿榫头表面切向的拉力增大，榫头滑出榫槽的距离增大所导致。法向正应变程与剪切应变程随加载平的变化规律也基本相同，载荷增时，应变程的最值增，同时最大点的位置向接触区内部移动。

![](images/08633e04088a539e3d0633db769d6adc4860a6ffd4b0de9938c80a6a0977a63a.jpg)  
图4-16 不同载荷下接触区边缘的应变程分布

# 4.4 圆弧形榫连结构疲劳寿命预测法

# 4.4.1 基于临界面法的疲劳寿命预测

临界面思想是处理多轴疲劳的一种常用方法，根据失效准则的不同，可以基于应力、应变以及能量参数来确定临界面，这种方法的思想在于将个多轴应力状态等效为单轴参数。基于临界法的准则能够计算疲劳寿命同时获得断裂平的位，失效准则的选取则需要考虑裂纹的类型，如常见的将裂纹划分为Ⅰ型（法向载荷）、Ⅱ型（剪切载荷）以及混合型裂纹。

根据材料的性能、应力状态的不同，不同失效准则可以选择不同的临界面及损伤参量，这些损伤参量可以划分为应力准则、应变准则以及能量准则。由于临界面法在多轴疲劳寿命预测中泛应用，Szolwinski等[10]将临界法的思想应于微动疲劳寿命当中。本先采临界法开展疲劳寿命预测。应临界面法时，首先需要将应力、应变分量转换到任意平面内，临界面度的意如图4–17所。任意平的位可以由度 $\theta$ 唯一确定，由图中可知， $\theta$ 的取值范围为 $- 9 0 ^ { \circ } \sim$ id:$9 0 ^ { \circ }$ 。利坐标转换公式即可得到在任意平( $\theta$ 定义）内的应/应变分量见式（4-1)。采用式（4-1）的转换公式，以0.1°作为搜索步长， $\theta$ 角的搜索范围为 $\pm 9 0 ^ { \circ }$

![](images/ff0851745ee246fa551ac0880fb2c65df4022825215f1f678662cf06975ed612.jpg)  
图4-17 接触区临界定义意图

$$
\begin{array} { r l } & { \displaystyle { \sigma _ { \theta } } = \frac { \displaystyle { \sigma _ { x } } + \sigma _ { y } } { \displaystyle 2 } + \frac { \displaystyle { \sigma _ { x } } - \sigma _ { y } } { \displaystyle 2 } \mathrm { c o s } 2 \theta + \tau _ { x y } \mathrm { s i n } 2 \theta } \\ & { \displaystyle { \tau _ { \theta } } = - \frac { \displaystyle { \sigma _ { x } } - \sigma _ { y } } { \displaystyle 2 } \mathrm { s i n } 2 \theta + \tau _ { x y } \mathrm { c o s } 2 \theta } \\ & { \displaystyle { \varepsilon _ { \theta } } = \frac { \displaystyle { \varepsilon _ { x } } + \varepsilon _ { y } } { \displaystyle 2 } + \frac { \varepsilon _ { x } - \varepsilon _ { y } } { \displaystyle 2 } \mathrm { c o s } 2 \theta + \frac { \displaystyle { \gamma _ { x y } } } { \displaystyle 2 } \mathrm { s i n } 2 \theta } \\ & { \displaystyle { \gamma _ { \theta } } = - \left( \varepsilon _ { x } - \varepsilon _ { y } \right) \mathrm { s i n } 2 \theta + \gamma _ { x y } \mathrm { c o s } 2 \theta } \end{array}
$$

榫连结构接触区内的应状态为典型的多轴应状态，本节分别采基于临界法的两种常寿命模型SWT程和Fatemi-Socie（F-S）程开展圆弧榫的寿命预测，程参数在参考献[11中给出。F-S模型适于剪应主导Ⅱ型裂纹的破坏模式，在剪切加载过程中，不规则形状的裂纹表会产摩擦阻并因此减裂纹尖端的应力，进而阻碍裂纹的扩展使寿命增加，而拉伸应力以及拉伸应变则使裂纹面分离导致摩擦阻减。SWT程则主要适于由拉伸应（应变）引起，裂纹早期主要在垂直于最主应或主应变的平内扩展。需要说明的是这两个经典的寿命预测模型均能够考虑平均应的影响且适于例和例加载。

F-S模型的预测参数包括循环剪应变变程和面内的最大法向正应力，定义具有最剪应变变程的平作为临界平，该平上一个循环周期内的最法向应对裂纹萌生具有强化作用，F-S寿命方程形式为[12]

$$
P _ { \mathrm { F S } } = \frac { \Delta \gamma } { 2 } \bigg ( 1 + k \frac { \sigma _ { { n , \mathrm { m a x } } } } { \sigma _ { y } } \bigg ) = \mathrm { c o n s t a n t }
$$

$$
\frac { \Delta \gamma } { 2 } \bigg ( 1 + k \frac { \sigma _ { n , \mathrm { m a x } } } { \sigma _ { y } } \bigg ) = \frac { \tau _ { f } ^ { \prime } } { G } ( 2 N _ { \mathrm { f } } ) ^ { b _ { 0 } } + \gamma _ { \mathrm { f } } ^ { \prime } ( 2 N _ { \mathrm { f } } ) ^ { c _ { 0 } }
$$

式中： $\Delta \gamma$ (:) 最大剪应变变程；$\sigma _ { n , \mathrm { m a x } }$ id: 最大剪切应变平面上的最大法向应力；$\sigma _ { y }$ bcid:) 屈服强度；$k$ (id:) 多轴材料常数；$\tau _ { f } ^ { \prime }$ (id:) 扭转疲劳强度系数；$b _ { 0 }$ (id:) 扭转疲劳强度指数；$\gamma _ { \mathrm { f } } ^ { \prime } -$ (id) 扭转疲劳延性系数；$c _ { 0 }$ 扭转疲劳延性指数；$G$ (id:) 剪切模量。

材料对法向正应力的敏感性由 1的值表征，对于试验参数不时，可以采如下近0似关系式[13]： $\tau _ { \mathrm { f } } ^ { \prime } = \frac { \sigma _ { \mathrm { f } } ^ { \prime } } { \sqrt { 3 } } , \gamma _ { \mathrm { f } } ^ { \prime } = \sqrt { 3 } \varepsilon _ { \mathrm { f } } ^ { \prime } , b _ { 0 } = b , c _ { 0 } = c , \frac { k } { \sigma _ { \gamma } } = \frac { 1 } { \sigma _ { \mathrm { f } } ^ { \prime } } \mathrm { o }$

SWT寿命方程主要适用于Ⅰ型裂纹的寿命预测，方程参数主要包括循环应变变程和最应，SWT模型最初是应于考虑平均应的单轴加载问题，与临界思想结合后使SWT模型能够应于多轴疲劳问题的分析中，并定义具有最SWT参数的平为临界平。SWT寿命程的形式为

$$
P _ { \mathrm { S W T } } = \sigma _ { \mathrm { m a x } } \varepsilon _ { a } = \frac { ( \sigma _ { \mathrm { f } } ^ { \prime } ) ^ { 2 } } { E } ( 2 N _ { \mathrm { f } } ) ^ { 2 b } + \sigma _ { \mathrm { f } } ^ { \prime } \varepsilon _ { \mathrm { f } } ^ { \prime } ( 2 N _ { \mathrm { f } } ) ^ { b + c }
$$

图4-18给出了接触区上边缘节点的剪应变幅 z与F-S参数随平度的变化，从图中的变化规律可以看出，剪应变幅与F-S参数均存在两个峰值，剪应变幅的两个峰值完全相等，但在接触区的不同位置（不同节点）处，最剪应变幅所在的平度并不相同。由F-S参数随不同平面度的变化可以看出，F-S参数同样存在两个峰值，且其中个峰值（平度约为 $4 0 ^ { \circ }$ ）明显于另个峰值，即裂纹更容易在该度下萌。

图4-19给出了接触区上边缘节点的法向正应变幅及SWT参数随平面度的变化。从图中的分布规律可以看出，法向正应变幅与SWT参数均只有个单峰值，且平的角度更加接近于 $0 ^ { \circ }$ ，这说明F-S模型和SWT模型的临界面度差别很。

采上述两种模型进寿命预测时，先需要利有限元计算得到的应/应变数据确定可能的裂纹萌生位置，进而确定该位置的损伤参数（ $P _ { \mathrm { F S } }$ 或 $P _ { \mathrm { S W T } }$ ）结合式(4-3)

![](images/15377f8726889292f42f9f976f204b7a0dde7ee64525030328e2853d49487ae8.jpg)  
图4-18 剪应变幅与F-S参数随度的变化（16.5tf）

![](images/4cd45f4a901c6c57131ef5eff3a0979b0db1b974566961e06a4326fb5e1568bc.jpg)  
图4-19 法向应变幅与SWT参数随度的变化（16.5tf）

和式（4-4）计算裂纹的萌寿命。接触上边缘的不同参数（剪应变幅 $\frac { \Delta \gamma } { 2 }$ 、F-S参数、法向应变幅 $\displaystyle { \frac { \Delta \varepsilon _ { n } } { 2 } }$ SWT参数）分布如图4-20所示。从图中的参数分布趋势可以看出，不同参数均呈现出先增然后迅速降低的分布规律，剪应变幅与F-S参数的最值均出现在8719节点，剪应变幅为0.00593，F-S参数为 $0 . 0 0 6 6 6$ 。法向应变幅与SWT参数的最大值所在位置并不一致，这主要是由于SWT参数中的法向正应力的影响更大。最大法向应变幅位于节点8719，应变幅为 $0 . 0 0 3 6 7$ 。最SWT参数位于节点8717，其值为 $2 . 0 4 \mathrm { M P a }$

利用所确定的不同试验载荷下的损伤参数结合寿命方程即可预测试验件的疲劳寿命，预测结果在表4-2中给出。表中给出了裂纹可能的萌位置及损伤参数，尽管剪应变幅具有两个相等的峰值，临界面角度分别在 $- 5 0 ^ { \circ }$ 和 $4 0 ^ { \circ }$ 附近，但由于面内法向正应力并不相等，通常选取具有更大法向正应力的平面作为临界面。从表中的预测结果可以看出，F-S参数的预测寿命偏于保守，这主要是由于该模型未考虑应梯度的影响。从预测的裂纹萌度来看，F-S模型的预测结果与试验结果同样有定偏差，由图4-5（a）可知，裂纹的扩展向主要沿接触的法向，F-S模型的预测与接触法向的夹在 $4 0 ^ { \circ }$ 左右。

![](images/9ea893b74158bf858c1a2b4d6ff6c33211e1073e5677a3b99de974faba1dde19.jpg)  
图4-20 接触区上边缘处的参数分布（16.5tf)

表4-2 不同试验载荷下的寿命预测结果(F-S模型）  

<table><tr><td rowspan=1 colspan=1>参数</td><td rowspan=1 colspan=2>16.5tf</td><td rowspan=1 colspan=2>19.5f</td><td rowspan=1 colspan=2>21.5tf</td></tr><tr><td rowspan=1 colspan=1>节点号</td><td rowspan=1 colspan=2>8719</td><td rowspan=1 colspan=2>8720</td><td rowspan=1 colspan=2>8721</td></tr><tr><td rowspan=1 colspan=1>临界面角度0</td><td rowspan=1 colspan=1>-50.30</td><td rowspan=1 colspan=1>39.7°</td><td rowspan=1 colspan=1>-50.1{$</td><td rowspan=1 colspan=1>39.9°</td><td rowspan=1 colspan=1>-49.3°</td><td rowspan=1 colspan=1>40.7°</td></tr><tr><td rowspan=1 colspan=1>Δγ</td><td rowspan=1 colspan=1>0.0119</td><td rowspan=1 colspan=1>0.0119</td><td rowspan=1 colspan=1>0.0132</td><td rowspan=1 colspan=1>0.0132</td><td rowspan=1 colspan=1>0.0140</td><td rowspan=1 colspan=1>0.0140</td></tr><tr><td rowspan=1 colspan=1>σn</td><td rowspan=1 colspan=1>-75.6</td><td rowspan=1 colspan=1>141.6</td><td rowspan=1 colspan=1>-28.3</td><td rowspan=1 colspan=1>204.3</td><td rowspan=1 colspan=1>-8.66</td><td rowspan=1 colspan=1>192.5</td></tr><tr><td rowspan=1 colspan=1>F-S参数</td><td rowspan=1 colspan=1>0.0056</td><td rowspan=1 colspan=1>0.0065</td><td rowspan=1 colspan=1>0.0065</td><td rowspan=1 colspan=1>0.0075</td><td rowspan=1 colspan=1>0.0069</td><td rowspan=1 colspan=1>0.0079</td></tr><tr><td rowspan=1 colspan=1>预测寿命N</td><td rowspan=1 colspan=1>282805</td><td rowspan=1 colspan=1>88173</td><td rowspan=1 colspan=1>91946</td><td rowspan=1 colspan=1>31652</td><td rowspan=1 colspan=1>53984</td><td rowspan=1 colspan=1>22668</td></tr></table>

采用SWT模型的寿命预测结果在表4-3中给出，临界面为具有最大SWT参数的平面。与F-S模型的寿命预测结果类似，由于未考虑应力梯度的影响，SWT模型给出的寿命预测结果同样偏于保守，但SWT模型预测的裂纹萌（扩展）度与试验结果常吻合。

表4-3 不同试验载荷下的寿命预测结果 (SWT模型)  

<table><tr><td rowspan=1 colspan=1>参数</td><td rowspan=1 colspan=1>16.5tf</td><td rowspan=1 colspan=1>19.5tf</td><td rowspan=1 colspan=1>21.5f</td></tr><tr><td rowspan=1 colspan=1>节点号</td><td rowspan=1 colspan=1>8717</td><td rowspan=1 colspan=1>8718</td><td rowspan=1 colspan=1>8719</td></tr><tr><td rowspan=1 colspan=1>临界面角度θ</td><td rowspan=1 colspan=1>-4.4</td><td rowspan=1 colspan=1>-4.2</td><td rowspan=1 colspan=1>-4.6</td></tr><tr><td rowspan=1 colspan=1>∆ε</td><td rowspan=1 colspan=1>0.00679</td><td rowspan=1 colspan=1>0.00798</td><td rowspan=1 colspan=1>0.00898</td></tr><tr><td rowspan=1 colspan=1>σmax/MPa</td><td rowspan=1 colspan=1>601.9</td><td rowspan=1 colspan=1>701.9</td><td rowspan=1 colspan=1>784.4</td></tr><tr><td rowspan=1 colspan=1>SWT参数/MPa</td><td rowspan=1 colspan=1>2.04</td><td rowspan=1 colspan=1>2.80</td><td rowspan=1 colspan=1>3.52</td></tr><tr><td rowspan=1 colspan=1>预测寿命N</td><td rowspan=1 colspan=1>51247</td><td rowspan=1 colspan=1>14560</td><td rowspan=1 colspan=1>6419</td></tr></table>

# 4.4.2考虑应力梯度影响的寿命预测

大量研究表明由于高应力梯度影响，应力最大位置处的裂纹萌生参数（如SWT、F-S参数）通常给出偏于保守的预测结果。随着对应力梯度影响认识的深，研究者提出了多种不同的寿命修正模型来考虑应梯度的影响。如Heredia等[14]提出了个“第主应力-权函数”的修正模型，该方法是通过引一个依赖于应力分布特征的权函数实现对寿命模型的修正。其他考虑应梯度的法如体积平均法[15,16]，该法的思想是将裂纹萌参数或者应/应变参数在个临界体积内进平均。应体积平均法的个困难是需要事先确定个临界体积尺寸，这个尺寸的通常与材料的晶粒尺度在个量级[15,16]，但毫疑问的是损伤参数的均值随着体积尺寸的增减。本节基于权函数修正的思想发展了一种考虑应力梯度的寿命预测模型。

标量函数 $X = f ( \textbf { \em x } , \textbf { \em y } , \textbf { \em z } )$ 梯度的模可以表示为

$$
\left| { \nabla \ X } \right| = \sqrt { \left( { \frac { \partial X } { \partial x } } \right) ^ { 2 } + \left( { \frac { \partial X } { \partial y } } \right) ^ { 2 } + \left( { \frac { \partial X } { \partial z } } \right) ^ { 2 } }
$$

实际榫连结构的复杂结构形式导致解析求解接触应力场比较困难，普遍采用有限元法进分析，因此应梯度的定义式常采离散化的式给出。为了更好地刻画榫头接触表面不同向的高应力梯度特征，榫头接触表面的局部坐标系定义如图4-21所示，接触表面切向为 $X$ 方向，垂直表面指向内部方向为 $Y$ 方向。

![](images/75cdd00ba05b1ae20e3be56d7fbeb7867b317392b0ffa884faf08a08953e6c63.jpg)  
图4-21 接触区SWT参数平均梯度定义

根据SWT参数的分布规律，SWT参数的局部梯度可以通过下式近似得到

$$
\nabla P _ { \mathrm { s w r } } = \frac { \mathrm { d } P _ { \mathrm { s w r } } } { \mathrm { d } Y ^ { \prime } } = \frac { ( P _ { \mathrm { s w r } } ) _ { i } - ( P _ { \mathrm { s w r } } ) _ { i + 1 } } { s }
$$

其中：（ $P _ { \mathrm { { s w r } } }$ )i——第 $i$ 个节点处的SWT参数；

S 相邻节点间的距离。

图4-22给出SWT参数沿梯度向的分布，可以看到SWT参数随着深度的增加迅速减，体现出显著的梯度变化特征，SWT参数剧烈的变化主要是由接触区边缘的应/应变梯度引起，因此，采局部最损伤参数的寿命模型给出的预测结果均不分理想。图4-23给出了由式（4-6）计算得到的SWT参数的局部梯度分布，可以看出SWT参数的梯度逐渐减，个有趣的现象是SWT参数的梯度值在距离约为 $6 4 \mu \mathrm { m }$ 处减小为零，该尺度为7\~8个TC4的晶粒大小。

![](images/e457a0ff725f3d48b7562995c7470dcf6187bc15cce23935ab7c5ca3463798a5.jpg)  
图4-22 SWT参数沿路径2的分布

![](images/b45bd3132df5a48ec55fd6568840034dc5f2ccbddad47d93b27e4f9d43e09b41.jpg)  
图4-23 SWT参数局部梯度沿路径2的分布

为了考虑应梯度的影响，引权函数W对SWT程进修正，得到

$$
\mathrm { S W T } _ { \mathrm { g r a d } } \ = \ { \frac { 1 } { W } } P _ { \mathrm { S W T } }
$$

上式中引入的权函数 $W$ 是为了考虑应梯度的影响，依赖于SWT参数的平均梯度$\overline { { \nabla { P _ { \mathrm { s w r } } } } }$ ，即 $W = f ( \overline { { \nabla { P } } } _ { \mathrm { s w T } } )$ ，权函数需要满足：（1） $\mathbb { W } = f ( \overline { { \nabla { P } } } _ { \mathrm { S W T } } = 0 ) = 1$ ，对应梯度的情形，权函数 $W = 1$ ；（2） $W = f ( \overline { { \nabla { P } } } _ { \mathrm { s w r } } \not = 0 ) > 1$ ，应梯度越，构件的疲劳寿命越长。选择建立权函数与SWT参数的平均梯度而非局部梯度的关系，是由于对于一些接触构型局部的应力梯度可能趋于无穷[17]。此外，局部应力梯度的确定往往需要更加严格的数学推导，采用有限元法较难准确获得局部应力梯度的精确解。SWT参数的平均梯度定义为接触表与某个临界距离 $d$ 之间的SWT参数差 $\Delta P _ { \mathrm { s w r } }$ 与距离 $d$ 的比

$$
\overline { { \nabla P } } _ { \mathrm { s w r } } = \frac { \Delta P _ { \mathrm { { S W T } } } } { d } = \frac { P _ { \mathrm { { S W T } , m a x } } ~ | _ { \gamma = 0 } - P _ { \mathrm { { S W T } } } ~ | _ { \gamma = d } } { d }
$$

其中： $\overline { { \nabla { P _ { \mathrm { s w r } } } } }$ (id:) -SWT参数的平均梯度；

∆PswT -定距离范围内SWT参数的变化量；

$d$ i 梯度特征距离。

如何确定该特征距离 $d$ 是基于权函数法的个普遍难点，当前的体积平均法或者权函数法均没有个统的确定这个区域尺的定义[14\~17]。总体来看，该特征尺寸与载荷条件以及材料性能相关。尽管些研究是通过试验数据反推可以确定这个特征尺寸，但这极地增加了试验成本。因此，本假设这个特征尺寸与应梯度特征或者接触何相关，特征尺寸 $d$ 定义为表最SWT参数位置与试件内部梯度为零处的距离。根据图4-23所给出的SWT参数梯度分布规律，特征尺 $d$ 取为 $6 4 \mu \mathrm { m }$

为了建权函数W与SWT参数平均梯度 $\overline { { \nabla { P _ { \mathrm { s w r } } } } }$ 之间的关系，已有的研究[14,17]表明线性规律可以描述这种关系。然，由于SWT参数与最应以及应变幅相关，次线性关系可能并不能够很好地描述，因采如下的多项式形式

$$
\overline { { { W } } } ~ = f ( \overline { { { \nabla } P } } _ { \mathrm { s w r } } ) ~ = 1 ~ + ~ \sum _ { i = 1 } ^ { m } a _ { i } ~ ( \overline { { { \nabla } P } } _ { \mathrm { s w r } } ) ^ { i }
$$

式中， $a _ { i }$ 为常数，可以利试验数据进拟合得到。如果 $m = 1$ ，则上式简化为次线性关系，与Fouvry等人[17]的法相似。

采用上述发展的考虑应力梯度的寿命预测方法，计算过程包括榫连结构接触区局部应力/应变参数的获取和寿命方程参数的确定，主要的计算流程如下：

（1）建结构的有限元模型，结合试验载荷条件及材料性能参数开展循环加载条件下的弹塑性接触有限元分析，获得榫头表危险区域随加载时间变化的应、应变响应；

（2）采式（4-1）给出的转换公式计算不同节点 $i$ 处在任意平面 $j$ 内的应力/应变张量 $\sigma _ { i j } ^ { \prime }$ $\mathcal { E } _ { i j } ^ { ' }$ ，以 $0 . 1 ^ { \circ }$ 为搜索步长；

（3）计算各个节点 $i$ 处在第 $j$ 平内的SWT参数，假设个循环包含 $k$ 个计算子步，则SWT参数 $( P _ { \mathrm { S W T } } ) _ { i j } = \sigma _ { \operatorname* { m a x } } \varepsilon _ { \mathrm { a } }$ ，其中 $\sigma _ { \operatorname* { m a x } } = \operatorname* { m a x } _ { 1 \leqslant p \leqslant k }$ $\varepsilon _ { \mathrm { a } } = \operatorname* { m a x } _ { 1 \leqslant p \leqslant k } \left\{ { \begin{array} { l l } { \big | \varepsilon _ { x } ^ { \prime } ( p ) } & { - \varepsilon _ { x } ^ { \prime } ( q ) \big | \big | / \ / 2 ; } \\ { p + 1 \leqslant q \leqslant k } \end{array} } \right.$ (id:)

（4）重复步骤（2）和步骤（3）计算所有节点在任意平内的SWT参数，确定SWT参数最大的位置及其临界面角度；

（5）计算梯度路径上各节点的SWT参数值 $P _ { \mathrm { S W T } }$ ，确定SWT参数的梯度分布规律；

（6）利SWT参数的梯度分布特征计算平均梯度 $\overline { { \nabla { P _ { \mathrm { s w r } } } } }$ ，进而确定权函数的表达式，采用修正的SWT寿命模型进寿命预测。

# 4.4.3 基于二维有限元分析的寿命预测

# 4.4.3.1 平面应变模型的寿命预测

利榫连结构的有限元接触分析结果，采修正的SWT寿命程开展寿命预测。先采用临界面法计算接触表面的损伤参数分布，确定表面的裂纹萌位置，进步计算沿接触面法向的SWT参数分布。图4-24给出了SWT参数沿整个接触表面的分布，可以看出SWT参数最大值点位于接触区的上边缘。图4-25给出了基于式（4-9）确定的权函数W与SWT参数平均梯度V $\overline { { P } } _ { \mathrm { s w r } }$ 的关系曲线，从图中可以看出，采用二次多项式（ $m = 2$ ）的拟合结果明显优于次多项式（ $m = 1$ ）的拟合结果。

![](images/db41e092cf147fc6148e03fb08f25ac2b76873db2249b2e93793eb6975eb921e.jpg)  
图4-24 SWT参数沿接触表面的分布

![](images/c50ee89b128583a67ad379e53d06e628ee837bc9b603ba731fa7f2bb9382ed83.jpg)  
图4-25 权函数 $W$ 与SWT参数平均梯度 $\overline { { P } } _ { \mathrm { s w r } }$ 的关系(平应变模型)

采用所发展的寿命预测模型式（4-7）进寿命预测，图4-26给出了寿命预测结果的相关性，图中横坐标为试验寿命，纵坐标为预测寿命，中间 $4 5 ^ { \circ }$ 对线代表试验寿命与预测寿命相等，对角线两侧实线为2倍分散带，虚线为5倍分散带。图中对比了采用传统SWT模型（未考虑应力梯度影响）和考虑应力梯度影响后的预测结果，从图中可以看出，不考虑应力梯度影响而以接触表面上的最大损伤点作为寿命考核位置的预测结果偏于保守，其分散带在5倍左右。考虑应力梯度的影响对寿命方程进修正后，寿命预测精度得到提高，分散带在2倍左右。采次多项式权函数关系的预测结果优于次多项式。与传统的临界距离法相比，该方法可以避免难以确定临界距离带来的困难，具有一定的工程实用性。

![](images/4ac5321bc23b6a4107a9cd9372e11852133788d9858ff262c27896ec984b6fa5.jpg)  
图4-26 平应变模型寿命预测结果

# 4.4.3.2 平面应力模型的寿命预测

上述计算结果均是基于平面应变假设，这是由于榫连结构的轴向长度远于接触区内其他两个向的尺度，这种假设对于分析榫连结构的般学特征是合适的，且基于平面假设的维分析模型有效地降低了格规模，因在榫连结构的接触分析中般均采平应变假设。然，真实三维榫连结构的两侧端为由表，其应状态更加接近平应的假设，因而有必要对这两种不同假设（平应变/平应）模型的计算结果进对比，以考察其应差异。平面应假设与平应变假设的最大区别在于认为作于结构件的外和约束不沿厚度变化，相应的应分量和变形只是内坐标 $x$ 和$y$ 的函数，而不随第三方向变化，即在平面应力问题中，第三方向的应力为零。

采与上述平应变模型完全相同的有限元格，材料特性参数及计算边界条件也相同，仅将单元属性改为平应模型，计算得到榫头表面的应力/应变的对比如图4-27所。从图中可以看出，平应变假设与平应假设下的应计算结果比较接近，沿接触表面的分布形式相同，但接触区内的应变在接触区下边缘存在定的差别。

![](images/afa553d0ed15e11024690e06e4664989fc6c3b5dfc05c36ee2374fe283925391.jpg)  
(a）切向正应力与切向正应变

![](images/e7662fe46b96e07c1ea8c1e241bce40ed354e4f4c8c95b6bbc571734a0f74626.jpg)  
图4-27 接触表面应、应变分布对

与平应变模型的分析过程类似，利平应计算结果开展榫连结构的寿命预测分析，以对比两种模型的寿命预测精度。利用个循环内的应/应变数据，结合式（4-4）计算得到沿接触表的SWT参数分布（如图4-28所）。不难看出，与平应变模型的SWT参数分布相似，最点仍位于接触区上边缘，不同试验载荷对应的SWT参数值分别为 $2 . 4 1 \mathrm { M P a }$ (id:) $3 . 3 6 \mathrm { M P a }$ 和 $3 . 9 7 \mathrm { M P a }$ 。与平应变模型相，平应模型的预测寿命更加保守。图4-29给出了SWT参数沿接触法向的分布，利SWT参数的梯度分布，可计算得到SWT参数的局部梯度分布如图4-30所。

采用相同的分析流程，先拟合权函数 $\mathbb { W }$ 与SWT参数平均梯度V $\overline { { P } } _ { \mathrm { s w r } }$ 的函数关系，如图4-31所。预测寿命与试验结果的相关性如图4–32所。从预测结果可以看出，未考虑应力梯度时，预测寿命偏于保守，考虑应力梯度的影响后，寿命预测的精度显著提，预测寿命的分散带由5倍减为2倍。

由上述寿命预测结果可以看出，所发展的考虑应梯度的寿命预测模型能够显著提高SWT模型的预测精度，引的权函数能够考虑应/应变梯度的影响。然而，由于试验件数量及载荷平的限制（3种载荷、6件有效试验件），这些结果尚不以深入研究权函数与梯度特征之间的关系。因此采了多项式的函数形式来描述它们之间的关系，值得注意的是由于权函数W需要通过部分试验数据来回归，因此，选择合适数量的试验点对于确定权函数中的拟合参数常关键。当然，多项式的函数关系式是较简单的，但并不是唯一的表达式形式，将来的研究也可以进一步考察其他函数形式的适用性。

![](images/808414d0f9f49436869f35e1d858e49e996af1894482ac55acf6c831d3d851bb.jpg)  
图4-28 SWT参数沿接触的分布

![](images/2c6bf30feb4ce56025f04d503d7c14ff128ee962afd0f9f98cb4f928cd929ba0.jpg)  
图4-29 SWT参数沿接触面法向的分布

![](images/c5f67af54a6e015c880a806eab67f854344b4ecf5291722b7f11c9da5cff421b.jpg)  
图4-30 SWT参数局部梯度沿接触面法向的分布

![](images/f06d102b6a17ceb095818e0cbc60ec61fb1d707a485040a4a5b4e010be2485c7.jpg)  
图4-31 权函数 $W$ 与SWT参数平均梯度∇ $\overline { { P } } _ { \mathrm { s w r } }$ 的关系(平应模型)

![](images/c16f273244b80971c2d911780376e1d071db6ca21ae4fe5af1db8e2978f2cc6f.jpg)

![](images/5daedc8669548a76f07a82450332ae7ec9cbe2aa01b541b1b543d00b1454eae6.jpg)  
图4-32 平应模型寿命预测结果

# 4.4.4 基于三维有限元分析的寿命预测

# 4.4.4.1 有限元模型

以所设计的圆弧形榫连结构试验件为研究对象，为了兼顾计算规模与计算精度的要求，分别建了不同格密度的有限元模型，即格较为粗糙的整体模型和格精细的子模型。整体模型尽管不能准确获得局部的峰值应，但可以从宏观上直观地获取接触应力沿整个接触面的分布趋势，对比不同接触区的应力特征，这对初步确定榫连结构的危险区域以及后续模型的建是分必要的。从前面的分析不难看出，榫连结构接触区局部（接触区上、下边缘）是（微动）疲劳失效的关键部位，大量研究表明该位置需要极为精细的网格才能获得较为准确的应状态。而对于三维模型而，如此细密的网格（网格尺寸在微量级）对计算机的内存及计算时间需求都分巨，因模型法被泛应于接触分析当中[18,19]。模型的基本思想是将模型的局部区域单独切割出来作为计算模型，其计算的边界条件由初始格较为稀疏的整体模型插值得到。子模型法是获得局部准确应常有效的法，特别是对于非线性的接触问题。

采用子模型分析先需要建网格较为稀疏的整体模型并开展有限元分析，为子模型的分析提供位移插值边界条件，同时利用整体模型的分析可以获取整个接触面的应力状态，初步确定可能的裂纹萌生位置。榫连结构的拉伸试验装置为对称结构，上下两端榫头/榫槽的结构尺寸完全相同，通过呈交叉 $9 0 ^ { \circ }$ 的销钉与试验机相连，这样设计的一个好处是有助于消除试验过程中可能存在的附加弯矩。圆弧形榫连结构的整体何模型如图4-33所示，圆弧形榫头关于中心对称面对称，因而在进有限元计算时可以仅建其1/2模型进行分析。

![](images/c877ec08164281614ecbeae24bedb281bc128ee01bae7f49f14f72dfc2ddf4fb.jpg)  
图4-33 榫头接触局部坐标定义

利用模型的对称性，建其1/2有限元模型如图4-34所示，榫头与榫槽接触区局部网格进加密，有限元模型的单元数为443338，节点数为475532，计算单元采用三维实体单元（ANSYS中的solid185）。接触对将榫槽接触定义为标，榫头接触表面定义为接触面。摩擦模型采用库伦摩擦模型，最大容许剪切应力采用缺省值，接触算法采用拉格朗法，计算步数由程序动控制。

![](images/04d81c96acd797a1153e755ef6f721d643e5f7f99b97bbf7368f45eecd3bde6f.jpg)  
图4-34 榫连结构整体三维有限元模型

榫连结构的材料为TC4，材料参数与二维分析模型相同，计算时采用多线性弹塑性本构模型。有限元分析的边界条件为：榫头上表施加试验拉伸载荷，榫槽底位移全约束，模型对称面施加对称位移约束。

为保证位移插值的精度，模型与整体模型在切割边界处的节点完全对应，这样只需要提取整体有限元模型切割边界上节点的位移作为模型分析的边界条件即可。由于榫连结构呈圆弧形特征，因在不同弦长处的应特征并不相同，为了考察不同位置处的应特征及其疲劳寿命，分别建两个模型，位于榫头对称和由端处。对称处定义为模型1，由端处为模型2，如图4-35（a）所。

![](images/8d07263c4cb5c65d4c9ab2b7820f985de0471f494ba1cd95518e3319829e8e1e.jpg)  
图4-35 子模型的建立

子模型的厚度远小于其高度和宽度，为具有燕尾形特征面构型的“薄”，有限元模型如图4-35（b）所。对所关注的区域进网格细分，榫头接触面上边缘的网格细分区域的大小为 $0 . 8 8 \mathrm { m m } \times 0 . 3 2 \mathrm { m m } \times 0 . 1 \mathrm { m m }$ ，格尺寸为 $0 . 0 0 8 \mathrm { m m } \times 0 . 0 0 8 \mathrm { m m } \times 0 . 0 0 8 \mathrm { m m }$

4.4.4.2 圆弧形榫连结构的三维应力分布特征

由前述二维分析模型可以看出，榫连结构接触区边缘存在高峰值应力，并体现出高应力梯度特征。尽管一些研究认为对榫连结构破坏起主要作用的为面内的两向应力，即沿接触面的切向和法向应力，而通常忽略第三方向应力（轴向应力）的影响。但由于圆弧形榫连结构具有三维特征，其接触区内必然为多轴应状态，而维模型并不能得到接触面沿轴向的应力分布特征。因此，有必要给出榫连结构接触面内的应力分布特征，为榫连结构的寿命预测提供基础数据。

首先采用所建立的三维整体模型进行接触计算，计算得到16.5tf载荷条件下的圆弧榫头应力分布如图4-36所示。其中 $X$ 方向垂直于榫头长度方向， $Y$ 方向为试验拉伸载荷的加载方向， $Z$ 向为榫头长度方向。由图中可以看出，圆弧榫头接触面上下边缘存在比较大的 $X$ 方向和Y方向的压应力，这主要是由榫头接触面内的挤压作用产生，在榫头两侧接触面上端的圆弧过渡区存在较大的拉伸应力，特别是 $Y$ 方向的最大拉伸应力为$6 2 7 . 6 \mathrm { M P a }$ ，从整体上来看，榫头轴向的应力分量不大，说明轴向应力对圆弧榫失效的贡献有限。最大第一主应力和VonMises等效应力点位于榫头接触大圆弧面的上边缘，分别为858.1MPa和953.9MPa，该区域在寿命预测时需要重点关注。

![](images/54e366a173df9bf95787651c8db112b83d2377acebe833e67a70c48cfcdc7b48.jpg)  
(a）x方向应力分布

![](images/59f7b5964a88efcde85ae8f0be3158329aafdcd522a7d998b396ee61aeac4e0c.jpg)  
（b）Y方向应力分布

![](images/4b38d2986c1085c4027668638d29816e67bf32e5f24af631929f2fde40ebce97.jpg)

![](images/8af5f08614158e4dcf4c40a4045e0edd187181044a526c78e5d37ff9ebede6c3.jpg)  
（c）Z方向应力分布  
（d）第一主应力分布

![](images/ce41fc21863ae1649e0343c59ee086a0e93fd5bb906b9dca7806370224e8eb21.jpg)  
图4-36 榫头表面应分布（ $F = 1 6$ 5tf，总体坐标系)

需要说明的是，图4-36所给出的应力分布是在总体坐标系下的结果，由于榫头接触面法向与总体坐标系存在一定的夹角，而在失效分析时需要关注榫头切向和法向的应力状态，因而为了进一步直观地描述榫头表面的应力分布状态，沿榫头接触面建局部坐标系，图4-37给出了沿榫头表面的局部坐标系定义方式。接触面切向为 $X$ 向，接触面法向为 $Y$ 向，轴线方向为 $Z$ 向。由于榫头表面为圆弧面，不同位置处的坐标方向沿轴向会发旋转，因此在提取有限元结果时需要在每个节点处单独建局部坐标系。图4-38给出了在局部坐标系下的榫头表应分布，横坐标分别为距榫头过渡圆弧与接触直线段切点的距离和轴向截面编号 $i$ （ $i = 0$ ，1，2，3，…，40），截面编号为0的截面代表对称面，截面编号为40的截代表由端。由图4-38中的应分布规律不难发现，对于第 $i$ 截面内的应，其分布趋势与二维模型的分布规律相似：（1）切向正应力峰值（拉应力）位于榫头接触区上边缘，距离切点距离约为 $1 \mathrm { m m }$ ，在接触区上边缘存在应力状态的突变（拉应力转为压应力），自由端面（ $i = 4 0$ ）处的切向压应力大于对称面（ $i = 0$ ）处；（2）法向正应力特征表现为在接触面上下边缘处的压应力要明显于接触区中部的应力水平，自由端面处（ $i = 4 0$ ）的压应力峰值要于接触区榫头内部的压应力峰值；（3）轴向正应力的分布与切向正应力类似，接触区上边缘存在应力状态的转变，但应力水平小于切向正应力；（4）剪切应力同样在接触上下边缘有突变，而在接触区内部应平较低，这与材料的表面摩擦性能相关。

![](images/dcd3be44313914241cfd4dc9ebf1b2b8d0a5cac9db7927a139f5022a1b924af0.jpg)  
图4-37 榫头接触局部坐标定义

![](images/efaefaa4abb6efeb531c32c72a31e97813d1d49951b5db72026d71789afcd37a.jpg)  
图4-38 榫头表应分布( $F = 1 6 , 5 { \mathrm { t } }$ ，局部坐标系下)

上述分析给出了榫头表应的分布趋势，需要说明的是尽管三维整体模型在内的格够细密，但在长度向（轴向）的格仍较为稀疏（单元边长约为 $1 , 2 \mathrm { m m }$ ),因此，三维整体模型并不能准确获得接触区局部的应值。本节将模型1作为计算模型，接触区域的单元尺度为 $0 . 0 0 8 \mathrm { m m }$ ，与前的维分析模型致。为了考察不同计算模型（维/三维模型）的应差异，并验证维简化模型分析的有效性，先对比维模型与三维模型计算结果的差异。由于维模型是基于平面应变假设，而三维模型的1/2弦长位置处接近平应变假设，即模型1处的应状态。

计算得到16.5tf载荷条件下，维平应变模型与模型1的计算结果对如图4-39所示。图中分别给出了接触区内的切向正应、法向正应、剪切应以及轴向应的对比。图中横坐标为距离过渡圆弧与接触直线段连接切点的距离，纵坐标为应力分量，单位为 $\mathrm { M P a }$ 。从图中可以看出，在接触区上边缘（距切点距离约为 $1 \mathrm { m m }$ ）两种模型的计算结果常接近，且该位置的切向正应和轴向应为拉应，般认为较的拉伸应容易造成裂纹的初始萌，因而在寿命预测时需要重点关注该区域。接触区上边缘与下边缘均存在较的峰值应和应梯度，由于模型1接触下边缘的格未进细分，维平应变模型在整个接触区内的格尺寸均为 $0 . 0 0 8 \mathrm { m m }$ ，导致该位置（接触下边缘）的应计算结果差异常，这也表明接触区局部格对于计算精度有常的影响。在接触区内部，应平相对接触边缘处较，维模型与三维模型的计算结果比较接近。

![](images/dca9acc827db8d23857871f62b5ed2ec7b93940087eb0c7e199338684dfac413.jpg)  
图4-39维/三维模型计算结果对比

# 4.4.4.3 传统寿命模型的预测结果

榫连结构的接触区内为多轴应状态，常见的多轴寿命预测法包括采多轴损伤参量作为寿命预测参数和基于临界法的寿命预测模型。临界法由于具有定的物理意义且可以预测裂纹扩展的方向，因此在工程中得到了比较广泛的应用。临界面法的基本思想是选取某个平面内的损伤参数最大作为临界，根据裂纹类型的不同可以选择不同的损伤参数作为寿命预测参数。对于三维应力状态，任意平内的应/应变可以通过转换矩阵计算得到。通常采用两个角度 $\theta$ 和 $\phi$ 定义任意平面 $\varGamma$ 的方位，并假定坐标轴 $Y ^ { \prime }$ 与平面 $\boldsymbol { { \cal T } }$ 和 $X - Y$ 平面的交线平，如图4-40所，则任意平内的应/应变分量可由式（4-10）计算得到[20]

$$
\begin{array} { r } { \boldsymbol { \sigma } _ { i j } ^ { \prime } = \boldsymbol { M } \boldsymbol { \sigma } _ { i j } \boldsymbol { M } ^ { \mathrm { r } } , \quad \boldsymbol { \varepsilon } _ { i j } ^ { \prime } = \boldsymbol { M } \boldsymbol { \varepsilon } _ { i j } \boldsymbol { M } ^ { \mathrm { r } } } \end{array}
$$

其中： $\sigma _ { i j }$ , $\varepsilon _ { i j }$ 总体坐标系下的应力、应变分量；

(id $\sigma _ { i j } ^ { \prime }$ , $\mathcal { E } _ { i j } ^ { ' }$ (id:) 由 $\theta$ 和 $\phi$ 所确定平面内的应力、应变分量。

转换矩阵 $M$ 的表达式为

$$
M = \left[ \begin{array} { c c c } { { \cos \theta { \sin \phi } } } & { { \sin \theta { \sin \phi } } } & { { \cos \phi } } \\ { { - \sin \theta } } & { { \cos \theta } } & { { 0 } } \\ { { - \cos \theta { \cos \phi } } } & { { - \sin \theta { \cos \phi } } } & { { \sin \phi } } \end{array} \right]
$$

传统的基于临界面法的多轴寿命预测模型主要选取局部危险点作为寿命考核点，并不能考虑应力梯度的影响，首先采用传统的寿命预测模型开展分析，对比其与二维简化模型的差异。在此基础上，进步采本所发展的考虑应梯度的疲劳寿命预测法进寿命预测，并考察三维应状态的影响。

采与前述维模型的分析流程类似的过程进行寿命预测，主要关注的位置为圆弧榫头中对称（模型1）以及由端处（模型2）的疲劳寿命，分别计算得到不同试验载荷条件下的SWT参数沿接触表的分布如图4-41和图4-42所。图中的横坐标为距离接触直线段和过渡圆弧切点的距离，纵坐标为SWT参数，由图中的分布规律可以得出以下点结论：（1）模型1与模型2沿接触的SWT参数分布规律相似，随着距离的增加，SWT参数表现为先增然后迅速降低的分布趋势，峰值点均位于接触面上边缘（距切点约 $0 . 9 5 \mathrm { m m }$ ),而整个接触区内部的SWT参数显著低于接触边缘的峰值，这与接触区内的应力分布特征密切相关；（2）同个试验载荷条件下，模型2的SWT参数峰值于模型1，这表明圆弧榫头自由端面处的预测寿命要低于对称处；（3）SWT参数的峰值随载荷的增而升，以模型1的计算结果为例，16.5tf、19.5tf和21.5tf试验载荷条件下的SWT参数分别为 $1 . 6 4 \mathrm { M P a }$ $2 . 3 6 \mathrm { M P a }$ 和 $3 . 0 9 \mathrm { M P a }$ 。载荷的增幅为 $1 8 . 2 \%$ 、 $10 . 3 \%$ ,而对应SWT参数增幅为 $4 3 . 9 \%$ 和 $3 0 . 9 \%$

![](images/52f78f660120f6e483523562a8fdbdf767fc475a3f1d498bac38a7dfce425cbc.jpg)  
图4-40 临界面角度的定义

![](images/7c1fa6150a3ecd93b82be390efec4e9d69707b9b900429f90a0dde3c4605caec.jpg)  
图4-41 SWT参数沿榫头接触表的分布（模型1）

![](images/f47040ab476ce3eca9c9fb4c1a310f6f90f14508b9696d2e11ceb36cd99f985c.jpg)  
图4-42 SWT参数沿榫头接触表的分布（模型2)

图 $4 - 4 3 \sim$ 图4-45给出了寿命预测参数随临界位的变化（模型1，19.5tf)。图4-43为SWT参数随临界面角度 $\theta$ 和 $\phi$ 的变化，从图中可以看出，SWT参数存在一个比较明显的单峰值，峰值点位于角度 $\theta$ 和 $\phi$ 分别为54.1°和 $9 0 ^ { \circ }$ 所确定的平面内，当角度 $\phi$ 为 $9 0 ^ { \circ }$ 时，表明该临界面的法向与圆弧榫头的轴向( $Z$ 向）垂直。图4-44给出了一个循环内的最大法向正应力 $\sigma _ { \mathrm { m a x } }$ 随临界度的变化，由图中可知，与SWT参数的变化相似，最法向正应也存在一个单峰值，峰值点位于度 $\theta$ 和 $\phi$ 分别为 $5 8 . 1 ^ { \circ }$ 和$9 0 ^ { \circ }$ 所确定的平面内，最大法向正应力为 $6 4 2 . 1 \mathrm { M P a }$ 。图4-45给出了一个循环内的法向应变变程 $\Delta \varepsilon _ { n }$ ( $\mathcal { E } _ { n , \mathrm { m a x } } - \mathcal { E } _ { n , \mathrm { m i n } }$ ）随临界面角度的变化，从图中可以看出，法向应变变程存在双峰值，最大峰值点位于角度 $\theta$ 和 $\phi$ 分别为51. $2 ^ { \circ }$ 和 $9 0 ^ { \circ }$ 所确定的平面内，应变变程为0.00744，第二峰值点位于角度 $\theta$ 和 $\phi$ 分别为 $1 4 3 . 5 ^ { \circ }$ 和 $9 0 ^ { \circ }$ 所确定的平面内，应变变程为0.00398，应变变程存在两个峰值点的原因在于法向应变变程是计算个循环内的应变差，若某平面内的法向压应变较，则其应变变程同样可以较，这与最法向正应力是不同的，由两个峰值点的平面角度（51. $2 ^ { \circ }$ 和143. $5 ^ { \circ }$ ）可知，两个峰值点所在平面的法线方向分别接近接触面的切向和法向。

![](images/a7206545bbf94dd456cc6cf67bb60536ef24c6cb7e6dab3699c73811c9a87546.jpg)  
图4-43 SWT参数随临界度的变化

![](images/d3347f61d79b6aa2e557c72d5d6affe20d3a778718e121394686c779bfd1a855.jpg)  
图4-44 法向正应力 $\sigma _ { \mathrm { { m a x } } }$ 随临界面度的变化

![](images/73003752376b0430bdb45a01a8bc8aae93c2dd25343dd0022d7efedff15e6539.jpg)  
图4-45 法向应变变程随临界面度的变化

表4-4给出了基于临界面法的SWT方程的寿命预测结果。由表中的预测结果可以看出，由于未考虑应力梯度的影响，不同计算模型给出的寿命结果均偏于保守。子模型1位于圆弧榫的对称面，该位置更加接近平应变状态，预测结果也表明模型1的预测寿命与二维平面应变模型接近。子模型2位于圆弧榫的自由端面，更接近于平面应力状态，因此，子模型2的寿命预测结果与平面应力模型的预测结果相近。同样地，子模型2处的预测寿命低于模型1处。

表4-4二维与三维模型寿命预测结果对比  

<table><tr><td colspan="1" rowspan="1">载荷/f</td><td colspan="1" rowspan="1">参数</td><td colspan="1" rowspan="1">二维模型（平面应变）</td><td colspan="1" rowspan="1">二维模型（平面应力）</td><td colspan="1" rowspan="1">三维模型（子模型1）</td><td colspan="1" rowspan="1">三维模型(子模型2)</td></tr><tr><td colspan="1" rowspan="3">16.5</td><td colspan="1" rowspan="1">SWT/MPa</td><td colspan="1" rowspan="1">2.04</td><td colspan="1" rowspan="1">2.41</td><td colspan="1" rowspan="1">1.64</td><td colspan="1" rowspan="1">2.57</td></tr><tr><td colspan="1" rowspan="1">临界面角度(α)或(θ，φ)</td><td colspan="1" rowspan="1">-4.40</td><td colspan="1" rowspan="1">-4.6°</td><td colspan="1" rowspan="1">(54.8°,90°)</td><td colspan="1" rowspan="1">(127.4°，109.5°)</td></tr><tr><td colspan="1" rowspan="1">预测寿命N</td><td colspan="1" rowspan="1">51247</td><td colspan="1" rowspan="1">25969</td><td colspan="1" rowspan="1">131320</td><td colspan="1" rowspan="1">20185</td></tr><tr><td colspan="1" rowspan="1">载荷/tf</td><td colspan="1" rowspan="1">参数</td><td colspan="1" rowspan="1">二维模型（平面应变）</td><td colspan="1" rowspan="1">二维模型（平面应力）</td><td colspan="1" rowspan="1">三维模型（子模型1)</td><td colspan="1" rowspan="1">三维模型（子模型2）</td></tr><tr><td colspan="1" rowspan="3">19.5</td><td colspan="1" rowspan="1">SWT/MPa</td><td colspan="1" rowspan="1">2.80</td><td colspan="1" rowspan="1">3.36</td><td colspan="1" rowspan="1">2.36</td><td colspan="1" rowspan="1">2.95</td></tr><tr><td colspan="1" rowspan="1">临界面角度(α) 或(θ,φ)</td><td colspan="1" rowspan="1">-4.9°</td><td colspan="1" rowspan="1">-2.30</td><td colspan="1" rowspan="1">(54.1°,90°)</td><td colspan="1" rowspan="1">(128.4°，108.9°)</td></tr><tr><td colspan="1" rowspan="1">预测寿命N</td><td colspan="1" rowspan="1">14560</td><td colspan="1" rowspan="1">7534</td><td colspan="1" rowspan="1">28230</td><td colspan="1" rowspan="1">11996</td></tr><tr><td colspan="1" rowspan="3">21.5</td><td colspan="1" rowspan="1">SWT/MPa</td><td colspan="1" rowspan="1">3.52</td><td colspan="1" rowspan="1">3.97</td><td colspan="1" rowspan="1">3.09</td><td colspan="1" rowspan="1">3.81</td></tr><tr><td colspan="1" rowspan="1">临界面角度(α) 或(θ，φ)</td><td colspan="1" rowspan="1">-4.6°</td><td colspan="1" rowspan="1">-4.0°</td><td colspan="1" rowspan="1">(54.2°，90°)</td><td colspan="1" rowspan="1">(126.2°，108.4°)</td></tr><tr><td colspan="1" rowspan="1">预测寿命N</td><td colspan="1" rowspan="1">6419</td><td colspan="1" rowspan="1">4304</td><td colspan="1" rowspan="1">10134</td><td colspan="1" rowspan="1">4923</td></tr></table>

从临界的预测度来看，模型1（对称）的预测结果与维平应变模型比较接近，由于维模型的临界度是在局部坐标下定义，而三维模型是通过在整体直坐标系内定义平面法向矢量与各坐标轴的夹来确定。为了直观地对临界面的预测度，图4-46给出了平定义的对意图，二维模型与模型1的临界在榫头左侧端定义，子模型2的临界面在榫头右侧端定义，定义 $\alpha$ 为维模型所定义的临界平面与局部坐标系 $Y ^ { \prime }$ 轴的夹角。由图4-40可知，三维临界面的方位由变量 $\theta$ 和 $\phi$ 唯一确定，当 $\theta$ 为 $9 0 ^ { \circ }$ 时，即平面的法向与 $Z$ 轴垂直（位于 $X Y$ 平面内），则三维临界面的方位可由矢量 $\pmb { n }$ 与 $X$ 坐标轴的夹角为 $\theta$ 所确定。以16.5tf载荷的预测结果为例，二维平面应变模型的临界面角度 $\alpha$ 为 $- 4 . 4 ^ { \circ }$ ，三维子模型1的临界面度 $\theta$ 和 $\phi$ 分别为 $5 4 . 8 ^ { \circ }$ 和$9 0 ^ { \circ }$ ，换算的 $\alpha$ 为 $- 0 . 2 ^ { \circ }$ ，与二维平面应变模型的角度误差为 $4 . 2 ^ { \circ }$ 。类似地，子模型2的临界面角度 $\theta$ 和 $\phi$ 分别为127. $4 ^ { \circ }$ 和 $1 0 9 . 5 ^ { \circ }$ ，换算的 $\alpha$ 为 $- 2 . 4 ^ { \circ }$ ，与平面应力模型的角度预测误差为 $2 . 2 ^ { \circ }$ 。值得注意的是模型2的临界面度 $\phi$ 为 $1 0 9 . 5 ^ { \circ }$ ，与对称处的角度 $9 0 ^ { \circ }$ ）相差 $1 9 . 5 ^ { \circ }$ ，这与圆弧榫头的中有关，由圆弧榫头的设计尺寸可知圆弧榫头中心弧线的半径为 $1 3 2 \mathrm { m m }$ ，弦长为 $9 6 \mathrm { m m }$ ，对应的1/2圆心角为 $2 1 . 3 ^ { \circ }$ ，因此模型2与平面应模型的 $\phi$ 角误差为 $1 , 8 ^ { \circ }$ 。为了便于对种计算模型预测的临界度，不妨将三维模型的预测度换算为临界与接触法向的夹 $\alpha$ 见表4-5，结果表明不同计算模型预测的临界与接触法向的夹范围在-5°， $0 ^ { \circ }$ 内，这与圆弧榫头的试验结果是比较吻合的。

![](images/c48319353549a698600e5532d1a0be7a0c32d36917d1bf127b0a324913460176.jpg)  
图4-46 维/三维临界位对示意图

表4-5二维与三维模型临界面角度对比  

<table><tr><td rowspan=2 colspan=1>计算模型</td><td rowspan=1 colspan=3>临界面与接触面法向的夹角(α)</td></tr><tr><td rowspan=1 colspan=1>16.5f</td><td rowspan=1 colspan=1>19.5tf</td><td rowspan=1 colspan=1>21.5tf</td></tr><tr><td rowspan=1 colspan=1>二维模型（平面应变）</td><td rowspan=1 colspan=1>-4.4°</td><td rowspan=1 colspan=1>-4.9°</td><td rowspan=1 colspan=1>-4.6</td></tr><tr><td rowspan=1 colspan=1>二维模型（平面应力）</td><td rowspan=1 colspan=1>-4.60</td><td rowspan=1 colspan=1>-2.3°</td><td rowspan=1 colspan=1>-4.0</td></tr><tr><td rowspan=1 colspan=1>三维模型（模式1)</td><td rowspan=1 colspan=1>-0.20</td><td rowspan=1 colspan=1>-0.9</td><td rowspan=1 colspan=1>-0.8°</td></tr><tr><td rowspan=1 colspan=1>三维模型（子模式2)</td><td rowspan=1 colspan=1>-2.4°</td><td rowspan=1 colspan=1>-3.4°</td><td rowspan=1 colspan=1>-1.20</td></tr></table>

# 4.4.4.4 改进寿命模型的预测结果

上述寿命预测结果表明，采传统的基于临界面法的寿命预测结果偏于保守，这与维模型的寿命预测规律致，主要是由于榫头接触区边缘存在较的应梯度，仅选择表面局部的危险位置作为寿命考核点未能考虑应梯度的影响。本节采考虑应梯度的寿命预测法进寿命预测，以考察该法在三维模型中的适用性。

图4-47给出16.5tf载荷条件下模型1计算得到的各个应分量沿接触法向（路径2）的分布，由图中可以看出，随着距接触区表面距离的增加，切向正应力 $\sigma _ { x }$ 迅速降低，并逐渐趋于稳定；法向正应力 $\sigma _ { y }$ 与切向正应力的变化规律有所不同，随着距离的增加，法向正应力有增大的趋势，但其应力梯度要小于切向正应力，接触表面的法向正应分布表征了该点的接触状态特征（接触/分离），图中的应分布特征表明在最载荷状态下，该位置已经基本滑出接触区（靠近表处的 $\sigma _ { y }$ 较）；剪切应 $\tau _ { x y }$ 表现出随距离的增大增的分布趋势，这与维模型的计算规律也是一致的；值得注意的是与其他应力分量相比，轴向应力 $\sigma _ { z }$ 较小，但呈现出表面为拉应力而内部逐渐转变为压应力的变化趋势。

![](images/4024f4d996c3022bf52c1c7d1f552806487f178b56948473f2548fb6a790b2ef.jpg)  
图4-47 沿接触法向（路径2）的应分布（模型 $1 , F = 1 6 . 5 { \mathrm { t f } }$ )

利所发展的考虑应梯度的寿命预测模型进寿命预测时，先需要利有限元分析结果计算局部的SWT参数梯度分布，分别计算得到模型1、模型2在试验载荷下榫头接触区上边缘局部的SWT参数分布规律（如图4-48所示）。沿表法向的最计算距离为 $9 6 \mu \mathrm { m }$ ，由SWT参数的分布可以看出，与维模型的计算结果致，靠近接触区表的SWT参数变化常显著，随着向接触区内部逐渐深，SWT参数逐渐趋于定值，不同试验载荷的参数分布规律相似。

![](images/36e6968c6c44091f0db18ce696adc80b6cc22b6bf7651e5ff9eaa2154f06b48b.jpg)  
图4-48 SWT参数沿接触法向（路径2）的分布

根据SWT参数沿接触面法向的分布，求得SWT参数的局部梯度V $P _ { \mathrm { S W T } }$ 分布如图4-49所示。由图中可以看出， $\nabla \mathcal { P } _ { \mathrm { s w r } }$ 随距离的增而逐渐减小，并逐渐趋于零，在特征尺寸为$6 4 \mu \mathrm { m }$ 处， $\nabla \mathcal { P } _ { \mathrm { s w r } }$ 减小为零。因此，与二维模型的分析方法一致，三维模型同样选取 $6 4 \mu \mathrm { m }$ 作为梯度特征尺寸。利用试验数据即可拟合得到权函数 $W$ 与SWT参数平均梯度的关系，分别采次多项式和次多项式进拟合，结果如图4-50和图4-51所。可以看出，次多项式权函数（ $m = 2$ ）的拟合结果要明显优于一次多项式（ $m = 1$ )，但一次多项式仅有项拟合常数，次多项式包含两项拟合常数，所需的试验点更多。

拟合得到权函数的关系后即可利用SWT参数进考虑应梯度的寿命预测，不同模型的寿命预测结果与试验寿命的相关性如图4–52所。图中横坐标为试验寿命，纵坐标为预测寿命，可以看出，未考虑梯度的SWT模型寿命预测结果偏于保守，考虑应梯度的影响后，寿命预测结果较为理想，分散带基本在两倍以内。此外，从寿命预测结果不难发现权函数的拟合效果对其预测精度影响分明显，权函数采用次多项式( $m = 2$ ）的预测精度明显优于一次多项式（ $m = 1$ )。对模型1和模型2的预测结果，模型2给出的寿命预测精度更更为理想。试验件的裂纹也在该位置萌，与试验结果较为符合。

![](images/cd4e87bfff53345d4bbae73180863c762548d06df72e1761f235d119154e93c7.jpg)  
图4-49 ∇ $P _ { \mathrm { s w r } }$ 沿接触法向（路径2）的分布

![](images/3ec3354c3bc8b7a4458047ce1ecf1167254b9ae0accceb4acf55783df348b51b.jpg)  
图4-50 权函数拟合结果（模型1)

![](images/cbe341ad7f0f302033be7e2d3533accbb8cca1f4c3b5d9cda494616ab5428053.jpg)  
图4-51 权函数拟合结果(模型2)

由前文分析可知，二维平面模型可以提供主要的接触特征参数（如应力、接触状态等），且计算效率显著于三维模型。因此，在榫连结构的初步设计阶段，采维简化模型具有很好的应前景。但维平应变模型并不能准确刻画第三向的应状态，因而对于存在由第三向应力主导的失效问题，三维模型计算仍是必要的。

![](images/c8eeac4f0b9254c328782be5316eee33dc5a1516b7c8650c4353f40e0101a5f2.jpg)  
图4-52 寿命预测的相关性

# 参考文献

[1] 何明鉴．机械构件的微动疲劳[M．北京：国防业出版社，1994.   
[2] Liang Shi, Da –Sheng Wei, Yan – Rong Wang,et al. An investigation of fretting fatigue in a circular arc dovetail assembly [J]. International Journal of Fatigue, 2016, 82:226– 237.   
[3] Ruiz C, Boddington P H B, Chen K C. An investigation of fatigue and fretting in a dovetail joint [J]. Experimental Mechanics, 1984, 24 (3): 208–17.   
[4] Rajasckaran R, Nowell D. Fretting fatigue in dovetail roots: experiment and analysis [J]. Tribology International, 2006, 39: 1277–1285.   
[5] Rajasekaran R, Nowell D. On the finite element analysis of contacting bodies using submodelling [J] The Journal of Strain Analysis for Engineering Design, 2005, 40(2): 95-106.   
[6] Wei D S, Wang Y R, Yang X G. Analysis of failure behaviors of dovetail assemblies due to high gradient stress under contact loading [J]. Engineering Failure Analysis, 2011, 18：314-324.   
[7] JohnsonKL.接触学[M]．北京：等教育出版社，1992.   
[8] Jayaprakash M, Mutoh Y, Asai K, et al. Effect of contact pad rigidity of fretting fatigue behavior of nicrmov turbine steel [J]. International Journal of Fatigue, 2010, 32 (11）：1788-1794.   
[9] Mutoh Y, Jayaprakash M. Tangential stress range -compressive stress range diagram for fretting fatigue ddesign curve [J]. Tribology International, 2011, 44(11): 1394–1399.   
[10] Szolwinski M, Farris TN. Mechanics of fretting fatigue crack formation [J]. Wear, 1996,198：93–107.   
[11亮．空风扇叶结构优化及圆弧榫微动疲劳研究[D]．北京：北京航空航天 大学，2016.   
[12] Fatemi A, Kurath P. Multiaxial fatigue life predictions under the influence of mean - stresses [J]. Journal of Engineering Materials & Technology, 1988, 110: 380– 388.   
[13] Neu R W, Pape J A, Swalla DR. Methodologies for inking nucleation and propagation approached for predicting life under fretting fatigue [J ]. Fretting Fatigue: Current Technology and Practices, ASTM STP 1367, 2000: 369–388.   
[14] Heredia S, Fouvry S, Berthelet B, et al. Introduction of a "principal stress – weight function" approach to predict the crack nucleation risk under freting fatigue using FEM modeling [J]. International Journal of Fatigue, 2014, 61:191 –201.   
[15] Swalla D R, Neu R W. Characterization of fretting fatigue process volume using finite element analysis [J]. Fretting fatigue: advances in basic understanding and application. West Conshohocken: ASTM International, 2003, $8 1 - 1 0 7$   
[16] Naboulsi S, Mall S. Fretting fatigue crack initiation behavior using process volume approach and finite element analysis [J]. Tribology International, 2003, 36:121 –131.   
[17]Amargier R, Fouvry S, Chambon L, et al. Stress gradients effect on crack initiation in fretting fatigue using multiaxial fatigue framework [J]. International Journal of Fatigue, 2010，32：1904-1912.   
[18] Cormier N G, Smallwood B S, Sinclair G B, et al. Aggressive submodeling of stress concentration [J]. International Journal of Numerical Methods in Engineering, 1999, 46:889–909.   
[19] Kim H S, Mall S. Investigation into three – dimensional effects of finite contact width on fretting fatigue [J]. Finite Elements in Analysis and Design, 2005, 41: 1140– 1159.   
[20] Socie D F, Marquis G B. Multiaxial fatigue [M]. USA: SAE Publication Press, 2000.

# 第5章 动弹性稳定性预测设计的能量法

随着航空叶轮机械性能的提，动弹性稳定性问题已经严重影响到航空发动机的可靠性。同时，动载荷的复杂性使得解析法求解很难于实际分析，传统的经验法需要量的试验数据，耗资巨。因此，发展数值预测法具有重要的意义。

本章基于成熟的计算流体学和计算结构学段，发展了种流固耦合数值法于预测叶轮机械叶的动弹性稳定性。借助有限元形函数的概念，基于恒定位置矢量差法（invariant distance vectors，IDV）发展了种数据传递算法，将结构模态分析得到的节点振动位移插值到流固耦合交界的流体域格点上，采发展的种多层动格技术来实时更新可动域格点坐标，并通过有限体积法求解了通过 $k - \varepsilon$ 湍流模型封闭的雷诺平均纳维-斯托克斯（Navier-Stokes）程（RANS程），定常分析得到不同时刻的振动位移和对应的动载荷，进而得到个周期内的定常气动功，并基于能量法，推导出于预测动弹性稳定性的模态动阻尼比。

将发展的数值预测法分别应用于NASA67转叶和某压机第级转叶，计算了不同况下的模态动阻尼，在压机特性图上插值得到叶的颤振边界，给出了压机在整个工作范围内的颤振特性，并与试验结果进对比，验证了数值预测法的有效性。

# 5.1 叶动弹性稳定性理论模型- 能量法

基于能量法的流固耦合数值预测法包括了叶动弹性稳定性计算分析（含计算结构学和计算流体学两个）、界信息传递与多层动格技术，以及动等效的模态阻尼。

# 5.1.1 叶动弹性稳定性计算模型

众所周知，目前采用最多的流体控制方程组是N-S方程，它是从质量、动量和能量三大守恒定律出发而得到的。在实际的流动问题中，流动状态大多都是湍流，此时流动在时间和空间上都存在着很不规则的脉动。从工程角度考虑，所关心的往往只是在湍流时间尺度上平均的湍流流场，所以当前程上于研究湍流流动的数学物理模型绝多数仍然是RANS程。另外，在跨声速流动中，由于出现了激波和激波边界层（曾称附面层）的重叠，流场计算会产线性效应，而非定常RANS程能够较精确地模拟流场的这些非线性因素。因此，选取RANS方程作为计算流体力学数值模拟的控制程。

RANS程组的详细推导过程可参见参考献[1，这只给出其最终形式。在三维笛卡儿坐标系下，RANS方程组可表示为

$$
\left\{ \begin{array} { l } { { \displaystyle { \frac { \partial \rho } { \partial t } } + { \frac { \partial } { \partial x _ { j } } } \left( \rho u _ { j } \right) = 0 } } \\ { ~ } \\ { { \displaystyle { \frac { \partial } { \partial t } } \left( \rho u _ { i } \right) + { \frac { \partial } { \partial x _ { j } } } \left( \rho u _ { j } u _ { i } \right) = { \frac { \partial p } { \partial x _ { i } } } + { \frac { \partial \tau _ { j i } } { \partial x _ { j } } } } } \\ { { } } \\ { { \displaystyle { \frac { \partial } { \partial t } } \left( \rho e \right) + { \frac { \partial } { \partial x _ { j } } } \left( \rho u _ { j } H \right) = { \frac { \partial q _ { j } } { \partial x _ { j } } } + { \frac { \partial } { \partial x _ { j } } } \left( u _ { i } \tau _ { i j } \right) } } \end{array} \right. 
$$

式中： $u _ { i }$ , $u _ { j }$ 速度分量；

$\rho$ 流体密度；  
$p$ 流体压力；  
(id $H \cdot$ 总焓；  
e 内能；  
$\tau _ { i j }$ 笛卡儿坐标系下的黏性应力张量，包括黏性应力和雷诺应力；  
$q _ { j }$ 热通量。

RANS程引了湍流脉动速度，当对非定常N-S程组采用时间平均时，产生了未知的附加雷诺应项，须通过湍流模型来解决RANS程组的封闭问题，这湍流模型选取标准的 $k - \varepsilon$ 湍流模型。标准的 $k - \varepsilon$ 湍流模型包括湍动能 $k$ 的输运方程和湍动能耗散率 $\varepsilon$ 的输运方程

$$
\frac { \partial } { \partial t } \left( \rho k \right) + \frac { \partial } { \partial x _ { j } } \left( \rho u _ { j } k \right) = \frac { \partial } { \partial x _ { j } } \Bigg ( \frac { \mu _ { t } \partial k } { \sigma _ { k } \partial x _ { j } } \Bigg ) + G = \rho \varepsilon
$$

$$
\frac { \partial } { \partial t } \left( \rho \varepsilon \right) + \frac { \partial } { \partial x _ { j . } } \left( \rho u _ { j } \varepsilon \right) = \frac { \partial } { \partial x _ { j } } \left( \frac { \mu _ { t } \partial \varepsilon } { \sigma _ { \varepsilon } \partial x _ { j } } \right) + C _ { \varepsilon 1 } G \frac { \varepsilon } { k } - \rho C _ { \varepsilon 2 } \frac { \varepsilon ^ { 2 } } { k }
$$

其中

$$
G = \mu _ { i } \left( \frac { \partial u _ { i } } { \partial x _ { j } } + \frac { \partial u _ { j } } { \partial x _ { i } } \right) \frac { \partial u _ { i } } { \partial x _ { j } }
$$

式中： $\mu _ { t }$ (c 涡黏性系数，=ρC $\mu _ { t } = \rho C _ { \mu } \frac { k ^ { 2 } } { \varepsilon }$ 该模型的拟合常数为 $C _ { \mu } = 0 . 0 9$ , $\sigma _ { k } = 1 . 0$ , $\sigma _ { \varepsilon } = 1 , 3$ , $C _ { \varepsilon 1 } = 1 . 4 4$ , $C _ { \varepsilon 2 } = 1 . 9 2$

在计算流体力学分析中，选用通用软件CFX，从基于 $k - \varepsilon$ 湍流模型封闭的RANS程出发，采有限体积法对叶轮机械的离散域进数值求解，其中，空间采阶迎风格式，时间采阶欧拉向后差分格式，并通过CFX中的JunctionBox模块来控制格的变形。

在叶轮机械中，通常认为各叶的学特性相同，叶之间的运动规律通过叶间相位来相互联系。因此，整个转叶可简化为单叶进分析，其离散形式的系

统振动方程为

$$
M \ddot { x } + C \dot { x } + K x = F _ { \mathrm { ~ a ~ } }
$$

其中

$$
M = M _ { \mathrm { { m e c h } } } + M _ { \mathrm { { a e r o } } }
$$

$$
C = C _ { \mathrm { { m e c h } } } + C _ { \mathrm { { a e r o } } }
$$

$$
K = K _ { \mathrm { m e c h } } + K _ { \mathrm { a e r o } }
$$

式中： $M _ { \mathrm { { m e c h } } }$ (id:) 结构质量矩阵；

$M _ { \mathrm { a e r o } }$ 附加的流体质量矩阵；  
$C _ { \mathrm { m e c h } }$ 结构机械阻尼矩阵；  
$C _ { \mathrm { a e r o } }$ 气动阻尼矩阵；  
$K _ { \mathrm { { m e c h } } }$ (id:) 结构刚度矩阵；  
$K _ { \mathrm { a e r o } }$ 附加的流体刚度矩阵；  
$F _ { a }$ (id:) 作在叶表的动载荷矢量；  
$x$ 位移矢量。

在叶轮机械叶振荡过程中，由于体的密度远小于固体结构的密度，可以忽略气体附加质量的影响；由于气体具有可压缩性，气体引起的附加刚度远小于结构刚度，可以忽略体附加刚度的影响；对于阻尼项，由于机械阻尼与结构材料、结构形式等很多因素相关，很难表达，且基尔布（Kielb）和强（Chiang）[2]指出，叶轮机械结构的机械阻尼远于动阻尼，这忽略机械阻尼仅仅考虑动阻尼的作。另外，莫法特（Moffatt）和 $\mathrm { H e } ^ { [ 3 ] }$ 指出，叶轮机械叶的模态振型和固有频率基本不受动载荷的影响，在结构动学分析中只需考虑由振动，即 $F _ { \mathrm { a } } = 0$ 。基于上述的简化后，方程（5-4）可以改写为

$$
M _ { \mathrm { m e c h } } \ddot { x } + C _ { \mathrm { a e r o } } \dot { x } + K _ { \mathrm { m e c h } } x = 0
$$

李（Li）和何（He）[4]通过对跨声速风扇动阻尼的研究指出，在小振幅作用下，与叶振动相关的动阻尼具有线性性质。特弗德（Gottfried）和弗雷特（Fleeter)[5]、Moffatt和 $\mathrm { H e } ^ { [ 6 ] }$ 在颤振和强迫响应等相关领域的研究中，给定叶片最大振幅不超过叶片弦长的 $1 \%$ ，因为在这个幅值范围内，流场及非定常动力的变化线性较好，可以忽略流场线性的影响。程上采某些近似的处理法使系统的阻尼矩阵实现对化，并通过质量归一化处理得到正则坐标系下的自由振动方程

$$
\ddot { q } \ + 2 \zeta \omega \dot { q } \ + \omega ^ { 2 } q = 0
$$

式中： $q$ (id) 正则化模态振幅；$\zeta$ (id 模态阻尼比；$\omega$ (id -阻尼固有频率，当叶在旋转状态时对应为阻尼动频。

# 5.1.2界面信息传递与多层动网格技术

# 5.1.2.1数据传递

般情况下，固体域格流体域格稀疏得多，这两套格在边界上不能完全重合。因此，在通过模态分析得到固体域单元节点的振动位移以后，需要将其插值到流固耦合交界的流体域格点上；通过流场分析得到流体域格点的动载荷后，需要将其插值到流固耦合交界的固体域单元节点上。

如图5-1所，假设 $F$ 为一个流体节点，单元 $m$ 为离 $F$ 点最近的结构单元，点$F ^ { \prime }$ 为 $F$ 点在单元 $m$ 上的投影点， $F$ 到 $F ^ { \prime }$ 之间的坐标差是由于流体格和固体格对原始何构型的不同精度产的。采萨迪吉（Sadeghi）等[7]提出的恒定位置矢量差法，使流体格点的函数值（动载荷和振动位移）始终等于其投影点的函数值，虽然这会在流体网格上造成一定的横向剪切变形，但是该方法的计算效率较高。

![](images/59ebb5b3ef9e1381c737baeb6996447ff651a7849003396224fe34673922c3da.jpg)  
图5-1 流体节点与结构单元

采用有限元中局部坐标形式的形函数进三维线性单元插值，给出流体网格点坐标与对应固体单元节点坐标间的关系

$$
x _ { 0 i } = N _ { j } ( \xi , ~ \eta , ~ \zeta ) x _ { i j } ( i = 1 , ~ 2 , ~ 3 ; ~ j = 1 , ~ \cdots , ~ 8 )
$$

式中： $x _ { 0 i }$ ( $i = 1$ ，2，3)— -流体域中网格点的三个坐标值；

$x _ { i j }$ ( $i = 1$ ,2,3; $j = 1$ ，…，8）—固体域中最外层节点实体六体单元节点的三个坐标值；

$N _ { j }$ (ξ, $\eta$ , $\zeta$ ) $( j = 1$ ,…,8)— 固体域中节点实体六面体单元在局部坐标系中的8个形函数；

$\xi$ , $\eta$ , $\zeta$ —三个向的局部坐标。

其形函数的具体形式为

$$
N ( \xi , \eta , \zeta ) = \frac { 1 } { 8 } \left( 1 \pm \xi \right) \left( 1 \pm \eta \right) \left( 1 \pm \zeta \right)
$$

求解程（5-7）即可得到局部坐标值（ $\xi$ ,n, $\zeta )$ )，并通过三个局部坐标值来判断流体格点是否在相应的固体单元内。

得到流体格点在对应固体单元内的局部坐标值后，由位移插值可以得到流固耦合交界面上每个流体格点的位移值。具体的位移插值为

$$
{ \pmb u } _ { 0 i } = N _ { j } ( \xi , ~ \eta , ~ \zeta ) { \pmb u } _ { i j } ~ ( i = 1 , ~ 2 , ~ 3 ; ~ j = 1 , ~ \cdots ,
$$

式中： ${ \pmb u } _ { 0 i }$ $i = 1$ ，2，3）插值得到的流体格点的移矢量；

$\boldsymbol { u } _ { i j }$ （ $i = 1$ ,2，3; $j = 1$ ，…，8）固体域中最外层节点实体六体单元个节点的位移矢量。

另，通过坐标关系得到各流体格点对应的局部坐标值后，由动载荷插值可以将流体格点的动载荷分配到对应固体单元的每个节点上，即

$$
F _ { \mathrm { { S } } } = N _ { \mathrm { { F } } } ( \xi , \ \eta , \ \zeta ) F
$$

式中： $F _ { \mathrm { s } }$ (id:) 插值得到的固体单元节点上的动载荷矢量；

$N _ { \mathrm { { F } } } ( \xi , \ \eta ,$ (id: $\zeta$ )) 流体格点在对应固体单元内的形函数；

$F _ { \ l }$ (d 流体格点的动载荷矢量。

采用有限元局部坐标形式表示的形函数可以借助于流体格点坐标和固体单元节点坐标之间的关系得到对应的局部坐标值，进而得到流体域中各网格点对应的形函数，方便地将固体单元节点位移插值到流体格点上或将流体格点的动载荷分配到固体单元节点上，图5–2所示为数据传递算法的流程图。

# 5.1.2.2 多层动网格技术

叶轮机械中的叶振动会引起流体域形状的改变，计算流体学需要实时更新流体域格点坐标，但是如果采全域格更新的话，计算所消耗的时间很多，效率太低。因此，一为了能够反映振荡叶栅对流场的作，另也为了保证计算效率，斯隆（Slone）等[⁸]考虑将流体域分为固定域和可动域，如图5-3所。

对在振荡叶栅作用下的定常流场进分析时，仅将振荡叶附近的流体域指定为可动域，0形格来实现，0形可动域的格点坐标在每个求解时刻均随叶的振荡实时更新；远离叶的外围区域均被定义为固定域，H形格来实现，在叶振荡过程中，H形固定域的网格点坐标始终保持不变。在可动域和固定域的重叠表，即0形格和H形格的交界上，格点坐标也始终保持不变。在振荡叶栅作用下的流场分析中，将每个叶栅通道的流体域网格划分为叶表附近的0形格和外围的H形格，如图5-4所。叶表附近的0形可动域网格面便于后续对相应格点的搜索，另通过控制振荡叶表面层网格的 $y ^ { + }$ 和边界层格点密度可以得到较好的近场分辨率，便于更精确地计算叶表压[9]，这对采能量法进叶轮机械叶动弹性稳定性分析关重要。

通过发展的数据传递算法将固体域中表面单元节点位移插值到流固耦合交界面上的流体格点后，在流场分析的每求解时刻都要对可动域格点坐标进更新。在对流体域进网格划分时，设定可动域中的格为O形格，固定域的格为H形格。从格点的编号来看，0形域的各层格点编号规律相同，而且对应格点均位于同格径向线上。如图5-5所，当固体域振动时，流体域中固体边界附近的格点坐标均会按法向距离的大小比例变化，且始终保证流体域表面一层网格的尺寸大小满足精度要求，这有利于更准确地计算定常动。

![](images/d3b262d2fe990aacba38af1083909c458f05d6592d3e68899b0c9925c45f12f6.jpg)  
图5-2 数据传递算法

![](images/003533a444440832f8e05d6572dbc35d54c768c65417e09a16725944c11c8cc9.jpg)  
图5-3 格运动区域

![](images/e0bdd4ec0e76f93734f97a4a500069eeacdbe32042a6f8be066655f31c763bd5.jpg)  
图5-4 叶栅的可动域和固定域

![](images/8edba4102b73ec09456b133d3e4ac28458eaa92f9e285e890dc0d01dd6eafe35.jpg)  
图5-5 多层动格意图

在振荡叶栅作下的每时刻，格点坐标更新的过程如下：

（1）根据流体域中格点编号顺序，沿0形域格的法向逐层递推搜索，得到可动域中与叶表面格点编号顺序相同的其余各层格点；

（2）给定流固耦合交界面上格点的振幅为插值得到的流体格点的位移幅值，并指定可动域和固定域交界上的格点振幅为0，可动域中流固耦合交界与可动域和固定域交界之间的其他格点振幅按照各层格点之间法向距离的值来线性插值得到；

（3）在得到可动域中网格点振幅后，假设叶振动为正弦简谐振动，其振动频率为叶的某阶固有频率，设定格振动个周期的时间步数，由可动域中各层格点的振幅可以得到可动域中各格点在不同时间步的坐标值，进得到全域（可动域和固定域）在个周期内各不同时刻实时更新的格点坐标值。

在叶轮机械叶动弹性稳定性分析中，当考虑叶间相位的影响时，需要对全环叶栅进叶振荡作下的定常流场分析，此时给定各叶附近的0形网格均为可动域，外围的H形格仍然为固定域。全环叶栅的流体域格点坐标在个周期内的每个时间步上均实时更新，其中每叶对应的0形可动域的格点坐标均按照上述的方法来得到。

# 5.1.3 气动等效的模态阻尼

叶振动系统中存在着阻尼，而黏性阻尼的数学描述比较复杂，远不如黏性阻尼那样容易处理。因此，在定的条件下，为了便于研究，通常将动阻尼简化为等效黏性阻尼。动阻尼能否作为等效黏性阻尼来考虑，主要是由流场的性质来决定的。当流场绕流情况较好时，没有旋涡、分离区等强线性特征时，流场中的线性影响可以忽略，此时动阻尼可以按照等效黏性阻尼来处理。

振荡叶栅的动阻尼是由于流场的非定常气动引起的，该气动力是位移独立的分量，与叶振荡速度成正。般来说，叶轮机械中叶的机械阻尼远于动阻尼。因此，为了使得对于颤振发作的程预估略偏于安全，在预测叶轮机械叶动弹性稳定性时，常常略去机械阻尼对动弹性稳定性的影响，而以动阻尼是否于或等于0作为判断叶颤振发作与否的依据。

为了便于叶轮机械叶动弹性稳定性分析，应能量法来定义稳态振动的动阻尼，具体的定义方法是：非定常气动力在一个周期内对叶所做的功等于动阻尼在一个周期内所消耗的能量。

当给定叶按照简谐规律振动时，叶施加给流场的激励（压强）可表为

$$
p = p ( x , \ y , \ z , \ t ) = p ( x , \ y , \ z , \ t + T )
$$

式中：T— 叶振动的时间周期。

该激励在个周期内对流场所做的功为

$$
W = \int _ { 0 } ^ { T } \int _ { S } p \boldsymbol { n } \cdot \boldsymbol { v } \mathrm { d } S \mathrm { d } t
$$

式中： $_ { n }$ (id:) 叶片表面的外法向矢量；

$v$ 叶片振动的速度；

$S$ (d 叶的表积。

通过计算流体学进定常分析，得到流场中叶表面所有格点在各个不同时间步在 $x$ , $y$ , $z$ 三个方向上的动力 $F _ { x }$ , $F _ { y }$ , $F _ { z }$ ，以及对应时刻的所有格点在三个向上的位移 $D _ { x }$ , $D _ { y }$ , $D _ { z }$ ，设叶表格点总数为 $n _ { d }$ ，一个周期内的时间步为 $n _ { t }$ ,对任意节点 $i$ 来说，在任一时间步 $n$ 上，气动功可表示为

$$
w _ { i } ^ { n } = \frac { 1 } { 2 } ~ \left[ ~ ( F _ { x i } ^ { n } + F _ { x i } ^ { n - 1 } ) ~ ( D _ { x i } ^ { n } - D _ { x i } ^ { n - 1 } ) ~ + ~ ( F _ { y i } ^ { n } + F _ { y i } ^ { n - 1 } ) ~ ( D _ { y i } ^ { n } - D _ { y i } ^ { n - 1 } ) ~ + ~ ( F _ { x i } ^ { n } + F _ { y i } ^ { n } ) ~ ( D _ { x i } ^ { n } - D _ { y i } ^ { n - 1 } ) ~ \right]
$$

$$
( F _ { z i } ^ { n } + F _ { z i } ^ { n - 1 } ) ( D _ { z i } ^ { n } - D _ { z i } ^ { n - 1 } ) ]
$$

则个周期内叶表上的激振对流场所做的总功可表示为

$$
\boldsymbol { W } = \sum _ { i = 1 } ^ { n _ { d } } \sum _ { n = 2 } ^ { ( n _ { t } + 1 ) } \boldsymbol { w } _ { i } ^ { n }
$$

另一方面，由于动阻尼较，这里假设在简谐激励作用下阻尼系统对应某模态的稳态振动仍然是简谐振动，即

$$
d = d ^ { \mathrm { c f d } } \sin { \left( \omega t - \varphi \right) }
$$

式中： $\boldsymbol { d } ^ { \mathrm { { c f d } } }$ bid: 给定的叶振幅（矢量）；

$\omega$ (id 无阻尼固有频率；

$\varphi$ 相位差。

在正则坐标下，对应模态下的简谐振动可以表示为

$$
q = q ^ { \mathrm { c f d } } \sin \ ( \omega t - \varphi )
$$

式中： $q ^ { \mathrm { c f d } }$ -正则坐标系下的模态振幅。

当对振动程采质量归化处理时，某阶模态对应的动阻尼满

$$
c _ { \mathrm { a e r o } } = 2 \zeta _ { \mathrm { a e r o } } \omega
$$

式中： $c _ { \mathrm { a e r o } }$ (cid:) 经过近似处理后的某阶模态对应的动阻尼；

Saero -对应模态下的动阻尼。

在某阶模态下经过近似处理后的动阻尼在个周期内所消耗的能量可以表为

$$
W _ { \mathrm { a e r o } } ^ { } = \oint c _ { \mathrm { a e r o } } \dot { q } \mathrm { d } q = 2 \zeta _ { \mathrm { a e r o } } \omega \int _ { 0 } ^ { T } \dot { q } ^ { 2 } \mathrm { d } t = 2 \pi \zeta _ { \mathrm { a e r o } } \omega ^ { 2 } ( q ^ { \mathrm { e f f } } ) ^ { 2 }
$$

式中： $q ^ { \mathrm { c f d } }$ 正则坐标系下该振型的模态振幅。

在主质量归化处理时，物理坐标和模态坐标之间的坐标变换为

$$
d ^ { \mathrm { c f d } } = q ^ { \mathrm { c f d } } \phi
$$

式中： $\phi$ -对应的振型。

由等效黏性阻尼的定义，有

$$
- \ W = W _ { \mathrm { a e r o } }
$$

即

$$
- \ W = 2 \pi \zeta _ { \mathrm { a e r o } } \omega ^ { 2 } \ ( \ q ^ { \mathrm { c f d } } ) ^ { 2 }
$$

因此，模态动阻尼可以表为

$$
\zeta _ { \mathrm { a e r o } } = \frac { - W } { 2 \pi \omega ^ { 2 } ( q ^ { \mathrm { c f d } } ) ^ { 2 } }
$$

式中： $q ^ { \mathrm { c f d } }$ (id:) 正则坐标系下该振型的模态振幅；

Saero 模态动阻尼；  
$\omega$ 阻尼固有频率。

从式（5-22）可以看出，基于能量法推导的模态动阻尼与非定常动功的负值成正比，与叶振动的幅值及固有频率的平成反比，也就是说，当叶的振幅和固有频率定时，模态动阻尼比随非定常动功的增加减；当叶的定常动功保持不变时，模态动阻尼随叶振幅或固有频率的增加减。

# 5.2 能量法的叶颤振边界预测—NASA67转算例

将所发展的基于能量法的流固耦合数值方法应用于NASA67转子叶，在叶的不同模态下，通过定义的模态动阻尼的正负预测了叶的动弹性稳定性，并与试验结果进对比，验证了数值预测法的可性。进一步地，在叶的一阶弯曲模态下，通过叶振荡作下的非定常分析得到不同转速下、不同出反压对应不同况的模态动阻尼，并插值得到压机整个作范围内的模态动阻尼，在压机特性图上得到叶的颤振边界，可以于判断转叶在整个作范围内是否会出现颤振。

# 5.2.1 计算模型

NASA67转叶的何参数及试验结果可以参见参考献[10，11，基本的何参数及设计状态的动参数见表5-1。NASA67转叶的流场试验激光测速位置及动参数测量站的位置如图5-6所。

表5-1 NASA67转子基本设计参数  

<table><tr><td rowspan=1 colspan=1>叶片数</td><td rowspan=1 colspan=1>22</td></tr><tr><td rowspan=1 colspan=1>设计转速/(r/min)</td><td rowspan=1 colspan=1>16043</td></tr><tr><td rowspan=1 colspan=1>设计流量/(kg/s)</td><td rowspan=1 colspan=1>33.25</td></tr><tr><td rowspan=1 colspan=1>设计压比</td><td rowspan=1 colspan=1>1.63</td></tr><tr><td rowspan=1 colspan=1>叶尖速度/(m/s)</td><td rowspan=1 colspan=1>429</td></tr><tr><td rowspan=1 colspan=1>设计转速下的叶尖间隙/mm</td><td rowspan=1 colspan=1>0.61</td></tr><tr><td rowspan=1 colspan=1>叶尖入口相对Ma</td><td rowspan=1 colspan=1>1.38</td></tr><tr><td rowspan=1 colspan=1>展弦比（平均叶片度/叶根轴向弦长）</td><td rowspan=1 colspan=1>1.56</td></tr></table>

表5-1(续)  

<table><tr><td rowspan=2 colspan=1>稠度</td><td rowspan=1 colspan=1>叶根</td><td rowspan=1 colspan=1>3.11</td></tr><tr><td rowspan=1 colspan=1>叶尖</td><td rowspan=1 colspan=1>1.29</td></tr><tr><td rowspan=2 colspan=1>叶尖直径/mm</td><td rowspan=1 colspan=1>进口</td><td rowspan=1 colspan=1>514</td></tr><tr><td rowspan=1 colspan=1>出口</td><td rowspan=1 colspan=1>485</td></tr><tr><td rowspan=2 colspan=1>轮毂比</td><td rowspan=1 colspan=1>进口</td><td rowspan=1 colspan=1>0.375</td></tr><tr><td rowspan=1 colspan=1>出口</td><td rowspan=1 colspan=1>0.478</td></tr></table>

![](images/dfe894db913d1166c8d56a319a9954caf246fcb22cfa6e63fc80cfd83e7087b3.jpg)  
图5-6 NASA67转流场测量位置

针对给定的几何模型，在有限元通用软件ANSYS中，选取八节点实体六面体单元，建立NASA67转子叶的有限元模型如图5-7所示，其中实体单元总数为880个，节点总数为1449个。给定叶的材料为钛合，其中，弹性模量为112GPa，密度为 $4 4 4 0 \mathrm { k g }$ $\mathrm { m } ^ { 3 }$ ，泊松比为0.3。

另一方面，在流场分析中，忽略叶间相位角的影响，建立单扇区的流体域计算模型，如图5-8所示，其中叶片表面附近的可动域网格划分为0形网格，其外围的固定域格划分为H形格。在计算流体学分析中，进给定总温288.15K，总压$1 \mathrm { a t m } ^ { \mathrm { ( D ) } }$ ，出口给定平均反压，叶表面、轮缘和轮毂均给定绝热、无滑移、光滑壁面边界条件，循环对称面指定为周期对称边界条件。值得注意的是，单扇区的流体域模型未考虑叶尖间隙的影响。另外，流体域网格疏密满网格关性要求；同时，为了保证动载荷的计算精度，流场中叶片表面一层网格点的划分需要能够较好地保证网格近壁面区域的 $y ^ { + }$ 值满足湍流模型的要求。

![](images/7c8255d35bde3c42607291bfb556b4f7ba997b6dad3e0ccb38a587910e477f2e.jpg)  
图5-7 叶有限元模型

![](images/92b811ecb7447c45567af6b453c7309fc83c2a4c3e18b7a5ed9655ef6d5e64ba.jpg)  
图5-8 单扇区流体域模型

# 5.2.2 叶模态分析

在NASA67转子叶的模态分析中，给定叶根固，叶绕旋转轴旋转，在设计转速（ $1 6 0 4 3 \mathrm { r / m i n }$ ）下，含预应的模态分析得到叶各阶模态及相应的固有频率。图5-9所为叶的前4阶模态及其对应的固有频率（动频）。

在某选定的模态下，给定叶的最大振幅，通过发展的数据传递算法可以将叶固体单元节点的振动位移插值到流固耦合交界的流体域叶表格点上。图5-10所为NASA67转叶的第三阶模态（阶扭转模态），其中，图5-10（a）为ANSYS模态分析得到的固体单元节点的振动位移，图5-10（b）为数据传递算法插值得到的流体域叶表格点的振动位移。从图中的对可以看出，由于固体域格和流体域格对原始何构型的不同，在数据传递算法中采恒定位置矢量差法会引起交界面上产一定的横向剪切变形，但是对于流固耦合问题来说，所发展的数据传递算法能够便地实现流固耦合交界面上的数据交换，并且能够较好地保证计算精度。

固体域单元节点振动位移传递到流固耦合交界上的流体域格点后，采所发展的多层动格技术可以实现叶栅振荡作下的定常流场分析。由于流场从初始振荡状态到最终的稳定状态需要经过定的收敛时间，为了加快定常流场的计算收敛速度，在定常分析前可以先不考虑叶栅振荡作，对流场进定常分析，然后将定常分析的结果作为叶栅振荡作下定常分析的初始条件插值到定常分析中去。

![](images/3feb03ebfc4d83e4a654b616c799bf510cfac2b29cc5c405d570bc9cd238d1f2.jpg)  
图5-9 叶的前四阶模态

![](images/8b641cf97c2ed6fb0be1acd743ead6dc4512c037dd4ed12c878af4570ac356a2.jpg)  
图5-10 流固耦合交界上振动位移对比

# 5.2.3 定常流场分析

在NASA67转子叶的设计状态下，对单扇区模型进定常流场分析，得到设计状态下的流量为33. $2 4 \mathrm { k g / s }$ ，与试验测得的流量 $3 3 . 2 5 \mathrm { k g / s }$ 几乎相等，另外，数值计算得到的绝热效率为0.933，比试验测得的绝热效率0.93略[12]，但均在可接受的误差范围内。

在设计状态下，NASA67转子叶在叶栅槽道中间形成一道正激波，激波强度较大，激波使叶片表面的边界层逐渐增厚，至激波后在叶片尾缘前方出现较小的分离区，流体分离后沿吸在下游会重新附着在叶表面。另外，在分离区附近的波后区域有“形”超声区，波后“形”超声区以外的其他区域均为亚声区，图5-11所示为数值计算中叶栅通道激波与边界层相互作用的关系图。

![](images/fc2088609357bc869677f5834121efae59051acfe13f38dbebbbe1b803fc83c4.jpg)  
图5-11 叶栅通道激波与边界层相互作

图5-12给出了设计状态下吸面的压分布以及流线图。从图中可以看出，在设计状态下，吸力面上的激波波脚呈明显的 $\lambda$ 形。边界层内的径向潜流主要发生在沿流向速度较小的区域，对应为叶根附近无激波区域以及波后区域，而且径向潜流一直持续到流离开叶尾缘。流在吸激波后发了分离，在经过定的弦向距离后流又重新附体。

另外，在设计状态下，图 $5 - 1 3 \sim$ 图5-15分别对了试验和计算得到的叶栅马赫数分布。在 $90 \%$ 叶高处，进口相对马赫数大于1，对应为跨声速基元级，此时激波位于叶栅槽道中，激波使边界层逐渐增厚，激波后在叶背向上出现了边界层分离，且波后分离区附近存在局部超声区，如图5-13所。

在 $70 \%$ 叶处，仍为跨声速基元级，此时由于进口相对马赫数比 $90 \%$ 叶高处的小，激波在槽道中前移至叶栅前缘，对应激波强度降低，波后分离区相对较小，至尾缘处，由于流的攻较，产了定的流分离，如图5-14所。

![](images/dc6c018e0421118ef5d453675b16b00b69f337b6a54f0d45549d7990fa5169cd.jpg)  
图5-12 设计点处叶叶背压分布以及流线图

![](images/8aa780f9498eeee34f26f5a312e696b8e388b3664308199c705f836dfc7c75e8.jpg)  
图5-13 $90 \%$ 叶的相对马赫数等值线图

![](images/6c5aff8f98371b41aee5c13778de3a74d42602fbde056da7e70764b1bdc3ff5b.jpg)  
图5-14 $70 \%$ 叶的相对马赫数等值线图

在 $30 \%$ 叶高处，切线速度相对较小，对应为亚声基元级，进口相对马赫数小于1，在叶栅槽道中激波消失，但是由于该基元级的气流攻较大，在叶栅前缘会出现一个局部超声区，之后在吸上流会发较的分离，如图5-15所。

![](images/ca49decf922536cd3e9235d1c6371027cd326ee4e0f9605c5480f1ff07bcfd46.jpg)  
图5-15 $3 0 \%$ 叶的相对马赫数等值线图

从不同叶处相对马赫数的对比中可以看出，数值计算得到的激波系与试验测得的激波系大致相似，且计算的波后马赫数均偏低，即计算的激波强度比试验得到的激波强度要大，这对计算的绝热效率有一定的影响作用；同时由于数值计算模型中并未计及叶尖间隙的影响，忽略了叶尖泄漏等次流引起的气流损失。因此，对压气机转子叶的流场特性以及绝热效率也均会产生一定的影响。

# 5.2.4 非定常流场分析

定常分析后，引叶片的振荡作用进行非定常流场分析，其中将定常分析的结果插值到非定常分析中作为初始条件。给定叶表面附近的0形网格为可动域，其余部分的H形格为固定域。在设计状态下，建单扇区流场模型，指定叶表面格点坐标按照正弦规律振动，振动频率为叶的固有频率，且个振动周期给定60个时间步，通过多层动格技术实现振荡作下格坐标的实时更新。在叶不同模态下，网格的变形方式也相应不同，而且变形量随叶振幅的不同而改变。在振荡位移最值对应的时刻，不同模态下叶前缘和尾缘处的网格变形量均较，叶振幅越，格畸变越，而且在叶振幅最的位置处格变形量也达到最大值。图5-16（a）、（b）分别为一阶弯曲模态下T/4和 $3 T / 4$ 时刻 $90 \%$ 叶高处的网格点位置；图5-17（a）、（b）分别为一阶扭转模态下T/4和 $3 T / 4$ 时刻 $90 \%$ 叶高处的网格点位置。另外，由于可动域中网格变形的位移量是比例增加的，因此，在叶振荡作用下，当网格节点移动时，仍能够保证叶表面附近的网格较密，而远离叶表的格相对较稀疏，这在定程度上能够减少由于动格作带来的计算误差。

![](images/57c525407ccde46c1aef1b7e87cf71651816126749eabfb2fefdfb2a0781b2e9.jpg)  
图5-16阶弯曲模态下 $90 \%$ 叶处的格变形

这需要说明的是，在不同叶振动模态下，分别计算了叶尖振幅为 $0 . 2 \sim 2 . 0 \mathrm { m m }$ 的定常动功和模态气动阻尼比，结果表明，当叶在定范围内做幅振荡时，模态动阻尼与振幅关。因此，以下定常流场分析中均假定叶尖振幅为 $1 \mathrm { m m }$

![](images/c9be430f4ec878d199bdbec2a2cd9acb2ee2cd53f20688e21c9deb7c7f903552.jpg)  
图5-17一阶扭转模态下 $90 \%$ 叶处的格变形

叶的振荡作用会引起流场参数的振荡，激波位置和激波强度也会随着网格的运动而呈现振荡现象，且随模态不同，气动参数的振荡规律也会产一定的变化。在叶不同模态的振荡作用下，叶栅中的气动参数经过一段时间后均会近似地按照正弦规律振荡，并且振荡幅值最终保持恒定。在非定常流场分析中，设定叶片吸力面、叶片压力面，以及叶前、尾缘共4个典型位置的监视点，通过每个监视点在不同时刻的压力值可以清楚地看到各特征位置处压振荡的时间历程。图5-18所示为一阶弯曲模态下的压振荡历程。

![](images/79131e0a4df256269b637475ac6c0c6b9c03859c971b1cff369b352e0b34acaf.jpg)  
图5-18阶弯曲模态下各监视点的压振荡历程

当流场流参数振荡稳定后，选取个周期内各时间步的计算结果，读取流场中叶表所有格点在每时间步的定常动和对应格点的振动位移，进步地，计算得到叶表格点在个周期内的定常动功以及模态动阻尼。表5-2分别给出了单扇区模型在叶前4阶模态下的定常动功和模态动阻尼。由能量法的定义，负的动功表在个振荡周期内叶对流场做功，即叶的能量不断地释放到流中，系统动弹性稳定；正的模态动阻尼表作在叶表的动阻尼在耗功，叶振动的能量不断地减，系统动弹性稳定，且正的模态动阻尼越，叶在对应模态的振荡作下动弹性越稳定。从表中可以看出，叶在各阶模态下的动阻尼均为正，即NASA67转叶不会发动弹性失稳现象；另，叶第3阶模态（阶扭转模态）对应的模态动阻尼较，第2阶模态和第4阶模态对应的模态动阻尼相对较，因叶在扭转模态振荡作下的动弹性更稳定些。

表5-2 非定常动功和模态动阻尼  

<table><tr><td rowspan=1 colspan=1>模态</td><td rowspan=1 colspan=1>气动力总功/(103)</td><td rowspan=1 colspan=1>模态气动阻尼比/%</td></tr><tr><td rowspan=1 colspan=1>一阶</td><td rowspan=1 colspan=1>-6.6622</td><td rowspan=1 colspan=1>0.434</td></tr><tr><td rowspan=1 colspan=1>二阶</td><td rowspan=1 colspan=1>-5.9713</td><td rowspan=1 colspan=1>0.163</td></tr><tr><td rowspan=1 colspan=1>三阶</td><td rowspan=1 colspan=1>-14.797</td><td rowspan=1 colspan=1>0.596</td></tr><tr><td rowspan=1 colspan=1>四阶</td><td rowspan=1 colspan=1>-14.799</td><td rowspan=1 colspan=1>0.174</td></tr></table>

# 5.2.5 叶颤振边界预测

给定NASA67转叶进口总压1atm和总温288.15K，分别选取 $50 \%$ , $60 \%$ ,$70 \%$ , $80 \%$ , $90 \%$ 和 $100 \%$ 等不同的工作转速，并在每一工作转速下给定不同的出反压，定常分析可以得到不同转速下流量和压比的对应关系，图5-19所为NASA67转子叶的特性图。从图中可以看出，在一定的工作转速下，随着出口平均反压的增加，进出口压比逐渐增加，增加趋势逐渐平缓，同时，压气机流量逐渐减少，当流量减小到某一值时总压比将不再增加，此时流过压机的流会产脉动，压机进了不稳定的作边界，即喘振边界；另一方面，随着出口平均反压的减小，进出口压比逐渐减，同时，压气机流量逐渐增加，当总压比减小到某一值时流量将不再增加，此时压气机达到了堵塞边界。

在一阶弯曲模态下，给定振荡叶叶尖的最大振幅为 $1 \mathrm { m m }$ ，在不同的工作转速下，对定常分析的每一个工况，进叶振荡作用下的非定常流场分析，其中分别将对应工况的定常分析结果作为初始条件插值到非定常分析中。值得注意的是，不同转速下，叶离载荷作下的固有频率和振动模态均会有定的变化。

![](images/469f2f6342bd78d436d9530b31d0f486d57fcb6da9a1d2f50327d920f82cb994.jpg)  
图5-19 NASA67转特性图

当流参数达到稳定振荡后，选取个周期内每时间步的计算结果，通过定常动和对应的振动位移计算不同况下的定常动功，进而通过能量法得到一阶弯曲模态下不同况的模态动阻尼。

图5-20给出了模态动阻尼与NASA67转叶流量之间的关系。从图中可以看出，模态动阻尼随流量的变化因作转速的不同呈现不同的规律。当转速较( $100 \%$ , $90 \%$ , $80 \%$ ）时，模态动阻尼随流量的增加呈现先增加后减的趋势，且整个等转速线上的模态动阻尼比都较； $70 \%$ 等转速线可以视为个过渡，该转速线上，模态气动阻尼比的变化规律开始逐渐变得平缓，且随着流量的增加，模态气动阻尼比逐渐增加，整个变化过程中出现了拐点，最大模态动阻尼比出现在堵塞边界附近；当转速较低（ $60 \%$ , $50 \%$ ）时，模态动阻尼随流量的变化直呈增趋势，但变化量均较小。

图5-21给出了模态动阻尼比与进出总压比的关系。从图中可以看出，模态动阻尼随总压的变化因转速的不同也呈现不同的规律。当转速较( $100 \%$ , $90 \%$ , $80 \%$ ）时，模态动阻尼比随总压的增加呈现先增后减的趋势，且在整个等转速线上模态动阻尼变化量均较； $70 \%$ 等转速线可以视为个过渡，模态动阻尼在整个作范围内的变化量逐渐变，且随着总压的增加，模态动阻尼比单调减，在整个作范围内出现了拐点，最值出现在总压比最的位置，即堵塞边界附近；当转速较低（ $60 \%$ , $50 \%$ ）时，在整个工作范围内，模态动阻尼变化范围均较，且模态动阻尼随着总压的增加均逐渐减。

![](images/8b1459f9c10c019ca2d12c0c2d6c8b69c8b3f58dd35e1915b5b3ecd82bc76afb.jpg)  
图5-20 模态动阻尼与流量的关系

![](images/0d42c811c2993bb5a162dfc75d093916d8e4ae06017acd3da35ae997839619e5.jpg)  
图5-21 模态动阻尼与总压的关系

从图5-20和图5-21可以看出，模态动阻尼比随流量和总压的变化均会产定的变化。因此，将模态动阻尼表示在NASA67转叶的级特性图上，并通过三维曲拟合后投射到压机级特性图上得到模态动阻尼的等值线图，如图5-22所，其中模态动阻尼比为0的曲线对应该转叶的颤振边界。从图中可以看出，在各不同作转速下，NASA67转叶级特性图中的喘振边界和堵塞边界均在模态动阻尼比于0的范围内，即颤振边界位于转叶的作范围以外。因此，NASA67转叶在整个作范围内均动弹性稳定，这与试验结果是吻合的。

![](images/d16e2bca6084a95c378918a40cd623d0a899303b6787c8c84457a4c87bd8855e.jpg)  
图5-22 NASA67转叶的颤振特性图

# 5.3 能量法的叶颤振边界预测—某压机第级转算例

将发展的基于能量法的流固耦合数值法应于某型发动机第级压机转叶，通过定常分析的流体域格点动和振动位移计算得到定常动功，基于能量法获得叶阶弯曲模态下的动阻尼，在压机转特性图上获得该转叶的颤振边界，并与试验结果进对比，以验证数值预测方法的准确性。

# 5.3.1 叶片颤振试验简介

由于压机性能不断提，超、跨声速叶在动性能上设计不良，某型发动机第级压机转叶在台架试车和飞使中均发过叶失速颤振引起的折断故障。因此，为了摸清叶失速颤振的过程和特性，开展了多次失速颤振试验。在颤振试验中，除进叶振动测试外，还进了常规的性能参数测试，并采热线风速仪进失速测量[13,14]

整级叶盘耦合振动试验的试验件为该型发动机第级压机转。该级压机转共有31叶，螺钉沿径向顶紧在轮盘上的燕尾槽中，整个转靠转接座螺钉固定在个笨重的架上。在盘上粘贴压电晶体来激振整个叶盘转。

叶盘振动试验采用时间平均法，即用比物体振动周期长得多的时间进行连续曝光，并记录振动物体的全息图。试验件转子及光学元件牢固地固定在防振平台上，激光源为氨氖体激光器。

压气机叶失速颤振试验中，采用应变片-引电器-应变仪测量及数据记录系统。在全部31叶上均粘贴应变，其粘贴位置为叶盘根部排边处。应变采用玻璃丝布浸胶，其基栅为 $3 \mathrm { m m } \times 7 \mathrm { m m }$ 。测试系统的引电器采72点刷环式引电器（YZ6-950）。

试验发现，改变压气机转速和流量，叶均会发生强烈的振动，对应振动频率均与叶片的一阶弯曲频率相近，振动具有明显的失速颤振特征，振动应力随压气机流量的减迅速增，并伴有种哨声。将试车时磁带记录仪的信号在CF-920动态信号分析仪上进谱分析，得到叶振动应力值，表5-3所示为试验的测试结果。从表中可以看出，在 $\overline { { n } } = 0 , 8$ 时，失速颤振状态下各叶均以 $2 5 0 \mathrm { H z }$ 的频率振动，其中，最大振动应力值达到 $2 9 2 \mathrm { M P a }$ ，最小振动应力值仅为 $7 0 \mathrm { M P a }$ 左右，其余叶片的振动应力值均在$1 1 8 \sim 2 5 0 \mathrm { M P a }$ 之间，颤振时叶的最大和最小振动应力之比为4左右；在 $\overline { { n } } = 0 , 9$ 时，全级叶均以 $2 7 5 \mathrm { H z }$ 的频率振动，其中，最大振动应力值达到 $2 6 2 \mathrm { M P a }$ ，最小振动应力值仅为 $6 6 \mathrm { M P a }$ ，其余叶的振动应力值均在 $7 9 \sim 2 3 9 \mathrm { M P a }$ 之间，最大与最小应力之比也为4左右。在不同转速下，最振动应和最振动应值对应的叶也会发变化。

表5-3小频差转颤振状态下叶振动的频率和应力值   

<table><tr><td rowspan=2 colspan=2>状态</td><td rowspan=1 colspan=17>叶片</td></tr><tr><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>5</td><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>11</td><td rowspan=1 colspan=1>14</td><td rowspan=1 colspan=1>17</td><td rowspan=1 colspan=1>18</td><td rowspan=1 colspan=1>19</td><td rowspan=1 colspan=1>20</td><td rowspan=1 colspan=1>22</td><td rowspan=1 colspan=1>23</td><td rowspan=1 colspan=1>26</td><td rowspan=1 colspan=1>28</td><td rowspan=1 colspan=1>29</td><td rowspan=1 colspan=1>31</td></tr><tr><td rowspan=2 colspan=1>n=0.8近失速点</td><td rowspan=1 colspan=1>频率f/H₂$</td><td rowspan=1 colspan=1>250</td><td rowspan=1 colspan=1>250</td><td rowspan=1 colspan=1>250</td><td rowspan=1 colspan=1>250</td><td rowspan=1 colspan=1>250</td><td rowspan=1 colspan=1>250</td><td rowspan=1 colspan=1>250</td><td rowspan=1 colspan=1>250</td><td rowspan=1 colspan=1>250</td><td rowspan=1 colspan=1>250</td><td rowspan=1 colspan=1>250</td><td rowspan=1 colspan=1>250</td><td rowspan=1 colspan=1>250</td><td rowspan=1 colspan=1>250</td><td rowspan=1 colspan=1>250</td><td rowspan=1 colspan=1>250</td><td rowspan=1 colspan=1>250</td></tr><tr><td rowspan=1 colspan=1>应力σ/MPa</td><td rowspan=1 colspan=1>144</td><td rowspan=1 colspan=1>154</td><td rowspan=1 colspan=1>208</td><td rowspan=1 colspan=1>198</td><td rowspan=1 colspan=1>292</td><td rowspan=1 colspan=1>248</td><td rowspan=1 colspan=1>174</td><td rowspan=1 colspan=1>135</td><td rowspan=1 colspan=1>73</td><td rowspan=1 colspan=1>68</td><td rowspan=1 colspan=1>160</td><td rowspan=1 colspan=1>208</td><td rowspan=1 colspan=1>161</td><td rowspan=1 colspan=1>118</td><td rowspan=1 colspan=1>164</td><td rowspan=1 colspan=1>170</td><td rowspan=1 colspan=1>183</td></tr><tr><td rowspan=2 colspan=1>n=0.9近失速点</td><td rowspan=1 colspan=1>频率Jf/Hz$</td><td rowspan=1 colspan=1>275</td><td rowspan=1 colspan=1>275</td><td rowspan=1 colspan=1>275</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>275</td><td rowspan=1 colspan=1>275</td><td rowspan=1 colspan=1>275</td><td rowspan=1 colspan=1>275</td></tr><tr><td rowspan=1 colspan=1>应力σ/MPa</td><td rowspan=1 colspan=1>142</td><td rowspan=1 colspan=1>105</td><td rowspan=1 colspan=1>148</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>239</td><td rowspan=1 colspan=1>236</td><td rowspan=1 colspan=1>262</td><td rowspan=1 colspan=1>211</td></tr></table>

可以认为，叶失速颤振时全级叶都在振动，每叶都在向其余叶传递能量，这种耦合系统中能量的传递和交换作使耦合的叶只能在一个共同的频率下持续振动。叶失速颤振时不管同级叶之间是否存在频差，都会以相同的频率振动，即整级叶的振动是相互关联的。颤振发生时各叶间的应力是按区分布的，而且应力的分散度很大。

为了搞清颤振时叶间的振动相位问题，在CF-920分析仪上做了所有叶对第叶的互谱分析，从相频上可以读出度值，如表5-4所示。另外，为了更直观地表现叶颤振的过程，图5-23给出了 $\overline { { n } } = 0 , 8$ 时叶片颤振的三维图形。

表5-401次试验颤振状态下各叶对 $\mathbf { 1 }$ 号叶片的相位差   

<table><tr><td rowspan=2 colspan=1>状态</td><td rowspan=1 colspan=10>叶片编号</td></tr><tr><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>5</td><td rowspan=1 colspan=1>8</td><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>11</td><td rowspan=1 colspan=1>14</td><td rowspan=1 colspan=1>17</td><td rowspan=1 colspan=1>18</td><td rowspan=1 colspan=1>19</td></tr><tr><td rowspan=1 colspan=1>$n=0.8近失速点</td><td rowspan=1 colspan=1>-79.2</td><td rowspan=1 colspan=1>-38.5</td><td rowspan=1 colspan=1>-96.9</td><td rowspan=1 colspan=1>-156.8</td><td rowspan=1 colspan=1>-13.3</td><td rowspan=1 colspan=1>109.2</td><td rowspan=1 colspan=1>-77.2</td><td rowspan=1 colspan=1>-97.9</td><td rowspan=1 colspan=1>-70.5</td><td rowspan=1 colspan=1>-91.3</td></tr><tr><td rowspan=1 colspan=1>$n =0.9近失速点</td><td rowspan=1 colspan=1>-40.1</td><td rowspan=1 colspan=1>131.2</td><td rowspan=1 colspan=1>-68.2</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>158.7</td><td rowspan=1 colspan=1>-18.4</td><td rowspan=1 colspan=1>-123.5</td><td rowspan=1 colspan=1>-76.6</td><td rowspan=1 colspan=1>-129.7</td><td rowspan=1 colspan=1>148.6</td></tr></table>

![](images/b5f09a0211947a247960e5dfb453bc5842541e13e6ccb30b7c1dd3a83de8810f.jpg)  
图5-23 $\overline { { n } } = 0 , 8$ 时各叶的颤振过程

# 5.3.2 计算模型

在有限元软件ANSYS中建该型压机第级转叶的有限元模型，如图5-24所，其中，单元选节点实体六体单元，单元总数1536个，节点总数2475个。给定叶材料为合钢，弹性模量为 $2 1 0 \mathrm { G P a }$ ，密度为 $7 8 0 0 \mathrm { k g / m } ^ { 3 }$ ，泊松比0.3。

另一方面，忽略叶间相位角对动弹性稳定性的影响，建单扇区的流体域模型，如图5-25所，其中叶表附近的可动域格划分为0形格，其外围的固定域格划分为H形网格。在计算流体学分析中，指定进口为标准，即总温288.15K、总压1atm，出口给定不同的平均反压，叶表面、轮缘和轮毂均给定绝热、无滑移、光滑壁边界条件，在循环对称指定周期对称边界条件。

值得注意的是，流场分析中忽略了叶尖间隙的影响，因而在建立单扇区计算流体力学模型时未考虑叶尖间隙。另外，为了保证动载荷的计算精度，流场中叶表的格点划分需要能够较好地保证格近壁区域的 $y ^ { + }$ 满足湍流模型的要求。

![](images/2bff71f492a3a886ceb1bb6051f8a2711592740801de84a375f369bf1fff3697.jpg)  
图5-24 压机第级转叶片的有限元模型

![](images/8f0385ebe0e5865b68c5dd4950cb3c103a0ae67664173a020574461a084294cb.jpg)  
图5-25 单扇区流体域模型

# 5.3.3 叶片模态分析

在 $100 \%$ 转速下，给定叶根固支，有限元模型绕旋转轴旋转，通过含预应力的模态分析得到叶的各阶模态和固有频率。图5-26所分别为叶前三阶模态及其对应的固有频率（动频）。

![](images/36bd48369162cda4a097880d6c9d6c4e23abef27ec1d1a9e3d7fb709679407bb.jpg)  
图5-26 叶的振动模态

在各阶模态下，给定有限元模态分析得到的叶模态的振幅，通过前面所发展的数据传递算法将固体域表面单元节点的振动位移插值到流固耦合交界面的流体域叶表面格点上，得到叶振荡作下定常分析的格点振幅。图5-27所为该压机转叶的第三阶模态（阶扭转模态），其中，图5-27（a）为ANSYS模态分析得到的固体单元节点的振动位移；图5-27（b）为插值到流固耦合交界上流体域格点振动位移。从图中的对比可以看出，采用所发展的数值传递算法能够在一定的精度范围内很好地实现流体域与固体域之间的数据传递。

![](images/065da56551967dcb9210056b50e2dd4adc247c758c8b94dbaec59d61cf8d93af.jpg)  
图5-27 流固耦合交界的振动位移

# 5.3.4定常流场分析

在标准大气进口条件下，压气机转子分别在 $70 \%$ , $80 \%$ , $90 \%$ 和 $100 \%$ 等不同的工作转速下运转，给定不同的出平均反压，通过定常分析可以得到不同转速下折合流量和总压的对应关系，即该压机转叶的级特性图，如图5-28所。从图中可以看出，对于某转速，随着压机折合流量的降低，进出总压比逐渐增加，但增加趋势逐渐平缓，当折合流量减到某值后，总压将不再增加，此时流过压机的流会产生脉动，压气机进了不稳定的工作边界，即喘振边界；随着进出口总压比的降低，压气机折合流量逐渐增加，但增加趋势也逐渐平缓，当总压比减小到某一值时，折合流量将不再增加，此时压气机达到了堵塞边界。

另一方面，在 $100 \%$ 工作转速线上，选取不同出口平均反压对应的工况进行分析。随着出口平均反压的增加，工况逐渐从堵塞边界过渡到失速边界，如图5-29～图5-31所。当出平均反压较低（出口平均反压为 $9 0 \mathrm { k P a }$ ）时，工况位于堵塞边界附近。在$50 \%$ 叶处，叶栅前缘存在道脱体激波，叶栅槽道中出现道较弱的正激波，气流在叶片尾缘处分离；在 $90 \%$ 叶处，叶前缘出现了道斜激波，打到相邻叶吸靠近尾缘的区域，同时在叶栅槽道中的激波被推到了吸尾缘，较强的槽道弓形波在槽道中弯成道正激波打在相邻叶的压上，并在压发反射，如图5-29所示。

![](images/7923d0555bfaa4bb56af7e0137fb1a2e468cf614c03cdc6e05caa08055f668c6.jpg)  
图5-28 压机第级转级特性图

![](images/cf33aa54ead5e8ef9963faba4b9d66df29d31c9c04fa8322efe6f6572f953ae0.jpg)  
图5-29 近堵塞点马赫数等值线图

当出口平均反压增加（出口平均反压为 $1 0 0 \mathrm { k P a }$ ）时，气流位于设计点附近的况。在 $50 \%$ 叶处，槽道激波几乎消失，前缘激波强度减弱，波前马赫数相应减小，但是由于进口气流的增加，在叶的吸面上依然存在一定的分离；在 $90 \%$ 叶高处，槽道激波由强的弓形波逐渐向正激波过渡，并与前缘斜激波形成槽道三角区，槽道激波强度减弱，压力面波后附体较好，如图5-30所示。

![](images/407b7ef6b4a6fb470aa55bcb5dfe06afe21116a157a9857c2b11d43ad88373f0.jpg)  
图5-30 近设计点马赫数等值线图

当出口平均反压进步增加（出口平均反压 $1 1 5 \mathrm { k P a }$ ）时，气流达到了失速边界附近的工况。在 $50 \%$ 叶高处，槽道激波和前缘激波消失，由于气流进口攻角较大，在前缘出现一个局部超声区，之后边界层逐渐增厚直至气流分离；在 $90 \%$ 叶高处，叶栅槽道激波逐渐沿槽道从前缘被推出了槽道，与前缘激波汇合，形成了一道强的脱体激波，垂直打在叶吸上，之后，波后边界层逐渐加厚形成分离区，如图5-31所示。

![](images/419dfd103342d60e775802bde467e0c9de5be808a8a51b6a43efb976e28a0067.jpg)  
图5-31 近失速点马赫数等值线图

# 5.3.5叶颤振边界预测

试验测定该转子叶颤振发作时对应的叶振动频率与叶片的一阶弯曲模态固有频率相近，本节选取叶片在一阶弯曲模态的振荡作用下进行非定常流场分析。由于流场从初始状态到稳定状态需要经过一定的振荡时间，因而为了加快非定常流场的计算收敛速度，将对应况下的定常分析结果作为振荡作用下非定常分析的初始条件。值得注意的是，不同转速下叶的各阶模态和固有频率均有一定的变化。

在不同的工作转速下，给定进口总压 $1 \mathrm { a t m }$ 、总温288.15K，改变出口平均反压，对不同况下的流场进定常分析。在阶弯曲模态的振荡作下，当流参数达到稳定振荡后，选取一个周期内各时间步的计算结果，通过非定常气动力及其对应的振动位移计算不同况下的动功，并基于能量法计算不同况的模态动阻尼比。

图5-32所给出了模态动阻尼比与流量的关系，其中模态动阻尼为0的平线表了动弹性稳定和动弹性失稳的分界线。从图中可以看出，随着作转速的降低，模态动阻尼比在整个作范围内的变化量有减的趋势。在不同的作转速下，随着流量的增加，模态动阻尼比均呈现先增大后减的变化规律，且模态气动阻尼比的最大值随工作转速的降低呈现减的趋势。另一面， $70 \%$ 和 $80 \%$ 工作转速线对应况范围内的模态动阻尼比均为正，而 $90 \%$ 和 $100 \%$ 的工作转速线对应工况范围内的模态动阻尼出现了负值，即某些况下，该压机第级转叶会发动弹性失稳现象，此时对应的工况靠近喘振边界。

![](images/60355fede01b45f576344ca7f9c852d6eeee76bad69504ae47283f9072379ff6.jpg)  
图5-32 模态动阻尼与折合流量的关系

在不同的工作转速下，不同出口平均反压对应的不同工况下的模态气动阻尼比随进出口总压比的变化规律如图5-33所示。从图中可以看出，随着工作转速的降低，模态动阻尼在整个作范围内的变化范围有减的趋势。在不同的作转速下，随着进出总压比的增加，模态动阻尼均呈现先增后减的变化规律，且模态动阻尼的最值随着作转速的降低呈现减的趋势，这与模态动阻尼比随流量的变化规律相同。另一， $70 \%$ 和 $80 \%$ 工作转速线对应工况范围内的模态气动阻尼比均为正，而 $90 \%$ 和 $100 \%$ 的工作转速线对应工况范围内的模态动阻尼比出现了负值，即某些工况下，该级转叶会发动弹性失稳现象，此时对应的况靠近喘振边界。

![](images/ff2536efe73a2e9d266d5cc35df9d878a423bf818fa0038bb07255964a1aaa75.jpg)  
图5-33 模态动阻尼与总压的关系

对图5-32和图5-33可以看出，模态动阻尼随折合流量的变化规律与模态动阻尼比随进出总压比的变化规律相似。在不同作转速下，共同作线附近的模态气动阻尼比均较大，相应工况的气动弹性稳定性较好，而当工况向喘振边界靠近时，叶的模态动阻尼迅速减，在某些转速下甚出现了负值，此时叶发阶弯曲模态下的失速颤振；另一方面，当工况向堵塞边界靠近时，叶的模态气动阻尼比逐渐减，但是在堵塞边界前均未出现负的模态动阻尼，即该压机第级转叶不会发阶弯曲模态下的堵塞颤振。

将各不同况下的模态动阻尼比表示在压机转特性图上，可以得到模态动阻尼比与折合流量、压比的三维关系图，并通过曲面拟合得到整个工作范围内的模态动阻尼分布，投影到压机转特性图上得到模态动阻尼的等值线图，图5-34所示为该压机第级转子叶的颤振特性图，其中模态动阻尼比为0的曲线为压机转叶的颤振边界，模态动阻尼于0对应为动弹性稳定的况，模态动阻尼比小于0对应为动弹性失稳的况。

从图中可以看出，该发动机第级压机转叶的模态动阻尼最值出现在共同作线附近，对应模态动阻尼比均为正值，共同作线附近的况均动弹性稳定，且随着作转速的降低，模态动阻尼比最值逐渐减。当况向堵塞边界靠近时，模态动阻尼呈现比较平缓的减趋势，在堵塞边界附近的模态动阻尼比均为正值，即该发动机第级压机转叶不会发一阶弯曲模态下的堵塞颤振；当况向喘振边界靠近时，模态气动阻尼比迅速减小，在 $90 \%$ 和 $100 \%$ 工作转速，喘振边界前的模态动阻尼比出现了负值，该发动机第一级压气机转叶的颤振边界位于喘振边界前，即叶会出现阶弯曲模态下的失速颤振。另外，图中给出了试验测得的颤振边界，可与数值方法预测的颤振边界进行对比。由于数值计算中忽略了机械阻尼，因而在大部分转速范围内，数值方法预测的颤振边界均较试验测得的颤振边界保守，尤其在$80 \%$ 转速线附近，但整个工作范围内误差均较小。同时，该压气机转子叶片在 $80 \%$ \~$8 5 \%$ 工作转速线范围内的颤振边界距共同工作线较近，容易发生动弹性失稳现象。

![](images/56eb2b12737f42bd9deb51a45388b42322e521ba36a0ee9ad336d903d4eeb3a9.jpg)  
图5-34 压机转颤振特性图

# 5.4小结

本章发展了一种流固弱耦合数值预测方法，其中分别对固体域和流体域单独求解，并借助于有限元形函数的概念将叶的振动位移插值到流体域的流固耦合交界面上，实现计算结构力学和计算流体力学之间的耦合，并进行了计算程序实现。在叶的振荡作用下，采用时间推进法求解由 $k - \varepsilon$ 湍流模型封闭的RANS方程，其中叶的振荡作用通过设计的多层动网格技术来实现，达到计算精度和计算效率的平衡。进一步地，通过非定常分析在一个稳定振荡周期内各不同时刻的非定常动和振动位移得到非定常气动功，并基于能量法得到模态动阻尼。

以NASA67转子叶为例，通过发展的数值预测法计算了不同叶模态、不同工况的模态气动阻尼比，验证了基于能量法发展的气动弹性稳定性数值预测方法的有效性，并给出了模态气动阻尼比与工作范围内的折合流量和总压比的关系，通过三维曲面拟合可以得到叶的颤振特性图，并插值得到叶的颤振边界，可以便地用于描述叶轮机械叶的动弹性稳定性。

进一步地，以某压机第一级转子叶为例，计算了叶在一阶弯曲模态振荡作用下不同工况的模态气动阻尼比，插值得到压机整个工作范围内的模态气动阻尼比，进而得到压气机转子叶的颤振特性图，并与试验结果进了对比，吻合较好。

# 参考文献

[1陈懋草.粘性流体动刀字基础[M．北：高等教育出版社，2002.   
[2] Kielb R E, Chiang H D. Recent advancements in turbomachinery forced response analysis [R]. AIAA Paper92-0012, 1992.   
[3] Moffatt S, He L. Blade forced response prediction for industrial gas turbines, part I: Methodologies [R]. ASME GT 2003-38640, 2003.   
[4] Li H D, He L. Single - passage analysis of unsteady flows around vibrating blades of a transonic fan under inlet distortion [J]. ASME Journal of Turbomachinery, 2002, 124: 285-292.   
[5] Gottfried D A, Fleeter A. Aerodynamic damping predictions for turbomachine blade rows using a three - dimensional time marching simulation [R]. AIAA Paper 99 –2810, 1999.   
[6] Moffatt S, He L. On decoupled and fully– coupled methods for blade forced response prediction [J]. Journal of Fluids and Structures, 2005, 20: 217–234.   
[7] Sadeghi M, Liu F, Lai K L, et al. Application of three –dimensional interfaces for data transfer in aeroelastic computations [R]. AIAA Paper 2004–5376, 2004.   
[8] Slone A K, Pericleous K, Bailey C, et al. A finite volume unstructured mesh approach to dynamic fluid - structure interaction: an assessment of the challenge of predicting the onset of flutter [J]. Appl. Math. Modelling, 2004, 28:211 –239.   
[9] Hsiao C, Bendiksen O O. Finite element calculations of transonic flutter in cascades [R]. AIAA 93-2083, 1993.   
[10] Strazisar A J, Wood J R, Hathaway M D, et al. Laser anemometer measurement in a transonic axial–flow fan rotor [R], NASA TP 2879, 1989.   
[11] Fottner L. Test cases for computation of internal flows in aero engine components [R], AGARD-AR-275,1990.   
[12] Sadeghi M, Liu F. Coupled fluid – structure simulation for turbomachinery blade rows [R].AIAA2005–0018,2005.   
[13]吴秋芳，杨杰，段连丰．协调与协调叶/盘失速颤振试验研究[R].航空 工业部第六0六研究所，1987.   
[14]宋兆泓．航空发动机典型故障分析[M]．北京：北京航空航天学出版社， 1993.

# 第6章 叶颤振机制及其影响参数分析

将所发展的基于能量法的流固耦合数值法[1.2]应于某型发动机第级压机转叶，明确了些影响颤振的重要结构参数和动参数，包括叶模态、叶间相位、进口流攻、折合频率、进口相对马赫数，以及激波与波流分离等，研究了不同的颤振影响参数对叶轮机械叶动弹性稳定性的影响规律，并从叶吸激波及波后分离流动的度初步探讨了叶轮机械叶颤振机制[3,4]。进步地，采基于能量法的动弹性稳定性数值预测方法，探讨了某双级压气机试验件的颤振特性，并与研究所试验获得的该双级压机试验件的颤振特性进比较，通过叶表面非定常动功分布与叶表的激波和波后流分离的对应关系，进步探讨多级压机叶颤振发作的机理[1]。

# 6.1 叶结构参数

# 6.1.1叶片模态

有限元模态分析得到叶的前三阶模态，在每阶模态的振荡作下，分别对压机在近设计点和近失速点两个况进定常分析。

当流场参数达到稳定振荡后，通过个周期内各时间步的定常动及其对应的振动位移，可以得到一个周期内的非定常气动功，进而得到相应的模态气动阻尼比，表6-1所为不同况、叶不同模态振荡作下的定常动功和模态动阻尼。从表中可以看出，近设计点工况下（出口平均反压 $1 0 0 \mathrm { k P a }$ )，叶前三阶模态的非定常气动功均为负，模态气动阻尼比均为正，而在近失速点工况下（出口平均反压$1 1 5 \mathrm { k P a }$ )，叶仅在一阶弯曲模态下的非定常动功为正，模态动阻尼比为负，而其他模态下的非定常动功均为负，模态动阻尼比均为正。能量法分析中，正的非定常动功和负的模态动阻尼比表明，叶在振荡过程中不断从流中吸收能量，叶发动弹性失稳现象，即该发动机第级压机转叶将发阶弯曲失速颤振。

表6-1 非定常气动功和模态气动阻尼  

<table><tr><td rowspan=1 colspan=2>模态</td><td rowspan=1 colspan=1>一阶</td><td rowspan=1 colspan=1>二阶</td><td rowspan=1 colspan=1>三阶</td></tr><tr><td rowspan=1 colspan=2>固有频率（动频）/Hz</td><td rowspan=1 colspan=1>340.50</td><td rowspan=1 colspan=1>693.70</td><td rowspan=1 colspan=1>1026.9</td></tr><tr><td rowspan=2 colspan=1>近失速点（反压115kPa)</td><td rowspan=1 colspan=1>气动功/(10-3J)</td><td rowspan=1 colspan=1>1.5227</td><td rowspan=1 colspan=1>-7.4518</td><td rowspan=1 colspan=1>-2.1332</td></tr><tr><td rowspan=1 colspan=1>模态动阻尼比/%</td><td rowspan=1 colspan=1>-0.1033</td><td rowspan=1 colspan=1>0.5057</td><td rowspan=1 colspan=1>0.4968</td></tr><tr><td rowspan=2 colspan=1>近设计点（反压100kPa）</td><td rowspan=1 colspan=1>气动功/(10-3J)</td><td rowspan=1 colspan=1>-4.3625</td><td rowspan=1 colspan=1>-6.7801</td><td rowspan=1 colspan=1>-1.7804</td></tr><tr><td rowspan=1 colspan=1>模态气动阻尼比/%</td><td rowspan=1 colspan=1>0.2960</td><td rowspan=1 colspan=1>0.4601</td><td rowspan=1 colspan=1>0.4147</td></tr></table>

另一方面，在 $100 \%$ 工作转速下，选取近失速点工况（出口平均反压 $1 1 5 \mathrm { k P a }$ )，在叶阶弯曲模态和阶扭转模态下，进定常流场分析，并通过个稳定振荡周期内的定常动和振动位移给出了叶表的定常动功，图6-1和图6-2所分别为叶在阶弯曲模态和阶扭转模态下的定常动功分布，其中，图6-1（a）表吸面定常动功分布，图6-1（b）表示压定常动功分布。从图中可以看出，在相同况下，不同模态的叶表面非定常动功分布有很大差别。在弯曲模态下，吸面的波后区域存在一个高梯度的正功区，波前存在一个较高梯度的负功区，而压力面上的非定常气动功分布均较小，几乎没有较高的集中区；在扭转模态下，吸力面和压力面节线位置附近的定常动功为零，吸面在节线前后均存在个梯度较的定常动功区域，其正负取决于激波位置，而压力面上节线前后均存在两个相对较集中的负功区。

![](images/bc5f172b278d192adf32bd03888a38b46d861bdb26f4e9236a2384f7a9f37933.jpg)  
图6-1 阶弯曲模态

另外，为了研究叶表面正的非定常动功区域与叶表面分离流动的对应关系，在 $100 \%$ 转速、近失速点况下，对比了叶在阶弯曲模态和阶扭转模态下 $90 \%$ 叶位置处非定常动功沿弦向位置的分布，如图6-3所。从图中可以看出，吸面的非定常气动功变化较剧烈，对压气机失速颤振起主要影响作用，而压力面的非定常气动功对压机的颤振影响相对较。在叶的阶弯曲模态下，激波区域对应着负的定常动功区域，波后分离区对应着正的定常动功区域；在叶的阶扭转模态下，由于节线位于波后的叶弦中位置，因节线前的激波区域对应为正的定常动功区域，而节线后的分离区对应为负的非定常动功区域。

在同况下，叶不同模态的振荡作导致叶表的定常动功分布出现很的差异，且叶表的定常动总功也变化较，可以认为：叶模态和激波是影响叶失速颤振的两个关键因素，其中，叶模态对定常动功分布起着决定性的作，对叶轮机械叶的动弹性稳定性有很的影响。

![](images/45e2137dcfd670ba33606634ef37b614157b628308651aa3d820c3bc90a2da47.jpg)  
图6-2 一阶扭转模态

![](images/7e62d39b95908a265488a7f051a8564bca55e5294f5998f632b838eeb65252a9.jpg)  
图6-3 $90 \%$ 叶非定常动功的弦向分布

下在研究颤振的其他影响因素时，均考虑叶在阶弯曲模态下的振荡作。

# 6.1.2叶间相位角

叶振荡会引起流体域和固体域之间的耦合作用，而振荡叶栅之间非定常流动的相互作用对叶轮机械叶的气动弹性稳定性有很大影响。为了研究叶间相位角对叶栅动弹性稳定性的影响，考虑到振荡叶之间的相互作用对流场的影响，建全环叶栅模型用于非定常流场的分析。

在全环叶栅中，各叶片的振幅均给定为 $1 \mathrm { m m }$ ，叶片之间的相位角则通过全环叶栅的节径数和对应的行波形式来确定。这里假设各片叶片之间均超前或滞后相同的相位角，且不同的节径数对应不同的叶间相位，即给定节径数为 $n$ ，全环叶数为 $N$ ，则各相邻叶片之间的相位角为 $2 \pi n / N$ ，在成格件时需要分别考虑每叶表附近的可动域，通过多层动网格技术得到一个振荡周期内各可动域在不同叶间相位角情况下的格点坐标，并进步得到计及叶间相位的全环流体域的格点坐标。

某型发动机第级压机转叶全环叶栅流体域模型如图6-4所，其中每个叶扇区的固定域和可动域的格划分为叶表附近的0形可动域和远离叶表面的H形固定域。选取近失速点况，出平均反压为 $1 1 4 \mathrm { k P a }$ ，对全环流体域模型进定常分析，得到叶表面的压力分布，如图6-5所示。

![](images/0daf597caac30121617a7c0f4b647390bdedaf2e0675b31c71b70b4910d36d45.jpg)  
图6-4 全环叶栅模型

![](images/02e96ca2725f4474604bb5754a68407562f546150ba296b73e16384a44ce2f3f.jpg)  
图6-5 全环流体域叶表静压分布

在定常流场分析中，考虑叶在第阶弯曲模态下的振荡作用。由于各叶均给定相同的振幅，且各叶片之间的振荡相位角为常数，全环叶栅振动运动的非定常流场分析中各叶对应位置的振幅均对应相等，而振动相位滞后则相应为常数。在不同叶间相位情况下，分别分析了叶振荡对流场的影响，并计算了全环叶栅的非定常动功，基于能量法计算了稳态振荡的模态动阻尼比，并得到了模态动阻尼随叶间相位的变化规律，如图6–6所。从图中可以看出，模态动阻尼随叶间相位近似为简谐规律变化，且在近失速点况下，个振荡周期内动对叶所做的定常动功在绝多数节径范围内均为负值，振荡叶栅的能量不断耗散，模态动阻尼均为正，而当节径数为0\~9时，对应为前行波，非定常气动功为正值，此时振荡叶栅不断从流场中吸收能量，模态动阻尼为负值。因此，可以认为，在近失速点况下，该发动机第级压机转叶在第阶弯曲模态下有发动弹性失稳的可能性，这与颤振试验测得的结果是吻合的（详见第5章）。

![](images/5bd74c6cb9503b5a4114e66e25bbff9039746231d13d5dbc62ef831f7d3218a6.jpg)  
图6-6 模态动阻尼随叶间相位的变化规律

# 6.2 叶动参数

# 6.2.1进口气流攻角

在不同况下，叶模态振荡作下的定常流场分析可以得到整叶表面的流参数分布。本文选取 $7 5 \%$ 叶处的特征截面，在进口绝对马赫数保持不变的情况下，考察了不同况下模态动阻尼随进流攻的变化规律，如图6–7所。从图中可以看出，在给定的进口气流相对马赫数下，随着进口气流攻角的增大，模态气动阻尼比迅速减小，当进口气流攻角达到 $1 1 ^ { \circ }$ 左右时，模态动阻尼变为负值，此时叶发动弹性失稳，即该压机转子叶将发失速颤振。

![](images/211fac1020e18a3013537c510219a3ec75e4d5f3022e5e1ffd2b01ff74b8db4f.jpg)  
图6–7 模态动阻尼随进流攻的变化规律

另一方面，分别选取进口流攻为 $7 . 2 3 ^ { \circ }$ 和 $1 2 . 9 6 ^ { \circ }$ 对应的况进分析。图6-8分别出了不同进流攻下 $7 5 \%$ 叶截的马赫数等值线图。从图中可以看出，当进流攻较时，激波乎消失，但是在叶前缘出现了局部超声区，波后流附体较好；当进口流攻较大时，激波强度明显增加，激波从槽道被推到了叶前缘成为脱体激波，此时波后出现了较的分离区，对应为失速点附近的况。

![](images/a2bcfcd7341e793c9ee5e9275e59a9416ea0a7819945c25e326d5ee30cb93c06.jpg)  
图6-8 $\mathit { M a }$ 等值线图

# 6.2.2折合频率

折合频率是流体质点流过半弦长的时间与叶个振动周期的时间之。在某叶截面处，设叶型半弦长为 $b$ ，叶片振动角速度为 $\omega$ ，进口流相对速度为V，则折合频率可以表为 $k = b \omega / V$ ，而折合速度为 $\overline { { V } } = V / \left( \ b \omega \right)$ ，即在叶的某阶模态下，振动频率保持不变，进口流速度越大，对应的折合速度也越大。

在不同的转速下，改变叶栅出平均反压，叶阶弯曲模态振荡作下的定常流场分析得到不同况下的模态动阻尼，进插值得到不同作转速下模态动阻尼为零对应的况。在模态动阻尼为零的况下，可以便地给出折合速度与进流攻之间的关系。图6-9所为 $7 5 \%$ 叶处折合速度与进流攻共同确定的颤振边界。从图中可以看出，当进流攻较时，在叶振动频率保持不变的情况下，进流速度在很范围内对应的况均动弹性稳定，但是随着进流攻的增，较的进流速度也会导致叶的动弹性失稳；另，当进流速度较时，进流攻在很范围内对应的况也能保持动弹性稳定，但是随着进流速度的增，较的进流攻也会导致动弹性失稳。

![](images/e58c1d282c531c9d06a69d5c3411c4ece5065cc99c2ac60d95a284abef32ad3f.jpg)  
图6-9 折合速度与进流攻之间的关系

# 6.2.3进口相对马赫数

在不同进口流攻的情况下，计算得到不同进口相对马赫数对应的模态气动阻尼比，并考察了进口相对马赫数对叶动弹性稳定性的影响。图6-10所示为 $7 5 \%$ 叶高处进流攻分别为 $9 ^ { \circ }$ 和 $1 1 ^ { \circ }$ 时模态动阻尼随进相对马赫数的变化规律。从图中可以看出，当进流攻为 $9 ^ { \circ }$ 时，随着进相对马赫数的增，模态动阻尼在经过定量的减后会显著增加，在整个相对马赫数范围内，模态动阻尼始终于零，即动弹性稳定；当进流攻增 $1 1 ^ { \circ }$ 时，模态动阻尼随进相对马赫数的增呈现相反的变化规律，即当进相对马赫数逐渐增时，模态动阻尼首先会呈现小量的增加，在 $M a 0 , 9$ 左右达到最大值，之后，迅速下降，在 $M a 1 . 0$ 附近为临界动弹性稳定，当马赫数继续增时，模态动阻尼为负值，动弹性失稳。因此，随着进流攻角的增，进相对马赫数的增会导致叶有动弹性失稳的趋势，且进流攻越，动弹性失稳对应的进相对马赫数相应越。

![](images/c693373eebe8a9c4e5eadf768c30ec42b110a530cc2fdc77e6a32fdbe843b8fd.jpg)  
图6-10 进相对马赫数和攻对模态动阻尼的影响

# 6.2.4激波与波后流分离

在不同工况下，叶栅吸力面的激波强度以及波后的分离流动会有很大的区别，而且叶表面的定常动功分布在很程度上依赖于激波位置和波后流分离，换句话说，激波位置以及波后流分离对叶栅的动弹性稳定性有决定性的影响。另外，由于在不同模态、不同况下，叶压面的非定常动功相对吸面的定常动功均较，不存在定常动功较集中的区域。因此，本节考虑激波与波后流分离对动弹性稳定性的影响时均仅关注叶吸力面的非定常气动功分布。

在进口总温、总压一定的情况下，随着叶栅出口平均反压的变化，叶片吸力面的激波位置和激波强度也会改变。在 $100 \%$ 转速下，计算不同出口平均反压对应的工况，图6–11所示为叶吸的静压分布及其对应的流线图。当出平均反压为 $9 0 \mathrm { k P a }$ 时，如图6-11（a）所，工况为近堵塞点，叶吸力面的激波较弱，波后气流有较的径向潜流，但是并未出现流分离的区域；随着出口平均反压的增加，如图6-11（b）所示，出口平均反压达到 $1 0 5 \mathrm { k P a }$ ，工况为近设计点，激波位置几乎不变，但是激波强度明显增大，波后气流出现了较大的径向潜流，而且在叶尖附近出现了较小的逆流区，即吸在叶尖附近的波后区域开始出现了定的流分离；当出平均反压进步增加，如图6-11（c）所示，出口平均反压达到 $1 1 5 \mathrm { k P a }$ ，工况为近失速点，激波被推到了叶前缘成为脱体激波，该激波打在叶吸上，引起波后较的潜流，并在吸波后定的区域内出现了明显的逆流，即吸波后出现了较的流分离区。

![](images/b465ad099d5300129aa1b42d7319f57ed8938a9875d9e1acf495ebece4c6bfca.jpg)  
图6-11 吸静压分布及其流线图

对图6-11所的三种不同工况分别进叶振荡作下的非定常流场分析。图6-12所示为一个稳定振荡周期内叶吸力面的非定常气动功分布。从图中可以看出，在近堵塞点，叶吸力面没有较大的正功集中区，而且正功区相对靠后；增加出口平均反压，当工况达到近设计点时，叶片尾缘附近的吸力面出现了较为明显的正功集中区，且沿吸力面逐渐前移；进一步增加出口平均反压，当工况达到近失速点时，正功区梯度进一步增，且沿吸面前移弦中位置，出现了个较的正功集中区，该正功区前后区域的非定常气动功均为负值。

![](images/b65407295c9fe3ea7635d78d9a9de883acee00c5663cb734740294d479487f67.jpg)  
图6-12 吸定常动功分布

另一方面，图6-13给出了 $90 \%$ 叶高位置处叶吸力面定常动功沿弦向位置的分布。从图中可以看出，在近堵塞点和近设计点工况下，激波位于 $90 \%$ 弦向位置附近，且激波位置几乎保持不变，叶吸面的非定常动功分布在波前几乎一致，且均为负值，对叶片的气动弹性起稳定的作用，在激波弦向位置以后，近堵塞点工况的非定常气动功仍然为负，对应激波较弱，波后并未出现气流分离，而近设计点工况出现了正的非定常气动功，对应激波强度增大，较大的径向潜流导致波后出现了一定的气流分离；在近失速点工况下，激波前移至 $2 5 \%$ 弦向位置处，激波前的非定常气动功为负，而激波后定常动功急剧增加较的正值，此时，波后出现了较的流分离。

对比图6-11中的吸静压分布与图6-12中的吸面非定常动功的分布，以及与图6-13中 $90 \%$ 叶处吸力面非定常气动功沿弦向位置的分布，可以发现，激波和波后流分离是导致正的定常动功区域的主要因素，正负定常动功分界线乎与激波位置相对应，波前为负功区，波后逆流区为正功区。当波后分离区较小时，正的非定常气动功值相应较小；当波后分离区较大时，波后较大的正的非定常气动功也相应集中在逆流区内。因此，可以认为：激波和波后流分离是引起叶动弹性失稳的重要原因。

![](images/29a1172027699c1a7d7b45c4a13ae15a86761ad3c9a61248b800971b185109be.jpg)  
图6-13 $90 \%$ 叶吸定常动功的弦向分布

另一方面，叶片的振荡会引起激波位置和激波强度的振荡，进而引起波后分离区的变化；同时，非定常分析中，波后分离区的旋涡脱落会带来波后压力的改变，反过来也会引起激波位置和激波强度的振荡。选取平均出口反压为 $1 1 5 \mathrm { k P a }$ 对应的近失速点工况，在非定常流场分析的一个稳定振荡周期内，不同时刻的流场流参数也会发生振荡。图6-14所示为 $90 \%$ 叶处一个周期内不同时刻的马赫数等值线图。从图中可以看出，近失速点况下，脱体激波打在了靠近叶前缘的吸面上，且波后出现了明显的流分离区。另外，一个振荡周期内，激波强度先增大后减小，且当激波强度增大时，激波会相应前移，波后分离区相应增；反之，当激波强度减时，激波会相应后移，波后分离区相应减。因此，可以认为：激波和波后流分离的共同作会带来叶振动能量的不同变化规律，对叶轮机械叶的动弹性稳定性起着常重要的作。

![](images/eb74cd15b3e5760ba64c590cea35625d2a4673ace7bbeb27f7046c6e17ec66bd.jpg)  
(a)0   
( b) T/4

![](images/ab33c6e45630b8dd23c195509d6bdcd0443b40b6a0e716b220930c848c65ae52.jpg)  
图6-14 $\mathit { M a }$ 等值线图分布

# 6.3 双级压机叶颤振

# 6.3.1叶颤振试验简介

# 6.3.1.1试验件

为了研究某双级压气机试验件的颤振特性，研究所在原结构的基础上改装设计，得到双级压气机试验件，图6-15所示为该双级压气机试验件的结构图。试验是在研究所的全台压机试验器上完成的。由于该双级压机试验件在不同转速范围内均发生过第二级转子叶的颤振现象，因而试验时重点关注第二级转子叶，而且动态压力测量也在该级转子叶上进。图6-16所示为该试验件的第二级转子叶，其中，7号、8号和9号共3叶与其他叶不同。在第级转叶 $90 \%$ 叶高的吸力面表面，分别在轴向距前缘 $30 \%$ 左右以及距尾缘 $20 \%$ 左右各布置只传感器，如图6–17所。在静子叶表面 $90 \%$ 叶高的压力面，分别在轴向距前缘 $20 \%$ 左右以及距前缘$50 \%$ 左右各布置一只传感器，另外，在静叶 $50 \%$ 叶高、距前缘 $20 \%$ 位置处布置一只传感器，如图6-18所示。为了提传感器安装的可靠性，保证安装不影响测量表的流分布，采用背面打台阶的异形孔法。

![](images/548cf5280dac77d77465787e79b8a408cd059478569a3a3ee7e090b4a58eda71.jpg)  
图6-15 试验件结构图

![](images/4da074271e680b33b94fadbb8fdde1a758bb9b539954cefe925ce11255512b35.jpg)  
图6-16 试验件的第级转叶

![](images/84e17f520d2c3f97fe9d3692bc0a70240200c8301b429e7eb479b23150ac0ee2.jpg)  
图6-17 第级转叶的测点分布

![](images/930aef515f3814af76f3234802b87a9523781ab852a7e2bb8c7a186de91ce834.jpg)  
图6-18 静叶的测点分布

值得注意的是，为了测得叶的颤振边界，指定叶进颤振时的叶振幅，在试验中叶旦进颤振就退出，而没有进深度的持续颤振，以保证试验安全。

6.3.1.2 颤振试验及其测试结果

该试验遵守相似准则，压机试验沿等转速线进，按试验时温度及需要试验的换算转速计算出压机的物理转速，换算到标准海平静状态的进条件下，压机1.0换算转速对应 $1 1 1 5 6 \mathrm { r / \mathrm { m i n } }$ 。动装置将压机驱动到试验转速后，调节节门开度，改变压机出口反压，进而达到改变试验状态的的。在各试验状态下进动态压测量、振动应测量以及叶振幅测量，得到相应状态点的性能参数，当叶振动发出叶颤振超限报警时，打开节门迅速退颤。

对该双级压机试验件分别进了 $0 . 8 , \ 0 . 9$ 和1.0三个换算转速状态下的试验测试。分别在不同的换算转速状态下，逐渐关闭节气门，当况从堵塞点向喘振点变化时，第二级转叶的振动应力会出现明显的变化。为了保证试验测试工作的安全，试验过程中，采光纤传感器实时监测第级转叶的振动，并通过实测整级叶的振动，考察了叶颤振的规律和特征。测试中规定叶振幅的预警值为 $8 \mathrm { m m }$ 。试验中分别在第级转叶同叶的前尾缘位置以及对应相隔两个转叶间隔的叶前缘位置各安排个测点，布置光纤传感器。

分别在0.8、0.9和1.0换算转速状态下，测量每条等转速线上从堵塞点到喘振点的动态压力、振动应力和振幅等参数，获得不同转速下从最大流量状态到颤振状态的不同试验状态点的压机特性。在不同的换算转速下，调节节门，当况从堵塞点向失速点靠近时，均发现第级转叶叶尖振幅超过预警值，图6-19所为0.8、0.9和1.0换算转速下光纤传感器测得的第级转叶振幅的变化情况，通过给定的预警值获得叶的颤振边界，并进步获得双级压机试验件的颤振边界，如图6-20所。

![](images/468e132b26715b72e15a4bd305d8c7e60f05a70efd094c4d04507f4fabaedbe3.jpg)  
图6-19 第级转叶的颤振边界

这里以0.9换算转速状态为例，在工况变化过程中，各测点的动态压力信号时域波形如图6-21所示。从图中可以看出，在转速一定的情况下，随着压气机节气门的逐渐关闭，双级压气机试验件的工况逐渐从堵塞边界向失速边界过渡。过程中，双级压气机试验件的进出口总压比逐渐增大，各测试点的动态压力信号振荡的平衡位置和幅值均不同，但是其变化规律相同，幅值均逐渐增大，并且有较为明显的周期性振荡特征，当叶片颤振超限报警时，打开节气门迅速退颤，此时各测试点的动态压力信号的平衡位置迅速改变，而幅值则呈现明显的减小。

![](images/1474e13ab635c786e03e6e95daaad5a657f7fa22a374549220747b05de2267e4.jpg)  
图6-20 双级压气机试验件性能曲线

![](images/936b72f7cc45616683b686f676157fd3825e8fc6399fdc8d71dd46a3c54ed2d6.jpg)  
图6-21 0.9换算转速状态下的信号时域波形

另方面，对各测点测得的动态压信号进频谱分析，研究动态压信号的频谱特性。双级压机试验件处于正常作状态时，从动态压信号的频谱分析中发现，动态压信号主要是以转速为基频的信号和以叶通过频率为主的信号，其他信号并明显的规律；随着压气机节气门的逐渐关闭，各频率分量均有所增加，以转速为基频的信号和以叶通过频率为主的信号仍为压信号的主要成分，但在转速对应的频率和叶通过频率附近有转速的整阶次信号产，且信号的幅值有较大的增长。以第级转叶为例，转叶两测点的第级静叶通过频率和转速基频较明显，但在 $3 8 8 \mathrm { H z }$ 处，压力信号也较强，且以第级静叶的通过频率为中，左右各存在个与中频率相差$3 8 8 \mathrm { H z }$ 的谱峰，如图6-22所示。另一面，从图6-23给出第二测点的瀑布图可以看出，$3 8 8 \mathrm { H z }$ 是随着压气机状态的变化而产生的，可以认为，该频率值与叶的振动有关。

![](images/e02b31a3ecaa04dc4115711c19f57d66f3f049c00b91b20bb39c3094875d2dec.jpg)  
图6-22 0.9换算转速某状态第级转叶测点频谱图

![](images/888bb8df9ffcb6484f0e96f1920620ec7d32f098d47b07cc9225ccc8abd79ce7.jpg)  
图6-23 0.9换算转速某状态第级转叶第测点的瀑布图

# 6.3.2 叶模态分析

在有限元软件ANSYS中建该双级压机试验件第级转叶的有限元模型，如图6-24所示，其中，选取八节点实体六面体单元，单元总数1680个，节点总数2697个，给定钛合金材料，弹性模量为 $1 1 4 \mathrm { G P a }$ ，密度为 $4 4 8 0 \mathrm { k g / m } ^ { 3 }$ ，泊松比为0.3。

在有限元分析中，给定叶根固支，整个模型绕旋转轴旋转。分别在0.8、0.9和1.0换算转速对应的物理转速下，通过含预应力的模态分析得到不同转速下该第二级转子叶的各阶模态和固有频率。图6-25所分别为该转子叶的阶弯曲和阶扭转振动模态。

![](images/8a6c9a60fa028e0de34621518635d91da40cff5de2533988001e44027ff4e5f7.jpg)  
图6-24第二级转子叶片有限元模型

![](images/9aa9a430a6cc1c2348b87ab91c6d2c2f9fa574235de6b2cc13d5df5876085605.jpg)  
图6-25 第级转叶低阶振动模态

在某阶模态下，给定有限元模态分析得到的模态振幅，将有限元模型中的节点振动位移插值到流固耦合交界的流体域叶表格点上，得到叶振荡作下定常流场分析的网格点振幅。需要说明的是，由于试验测得该双级压机试验件第级转叶颤振发作的频率与转叶的第一阶弯曲振动频率相近，本选取在第级转叶第阶弯曲模态的振荡作用下进定常流场分析。

# 6.3.3 定常流场分析

在计算流体力学分析中，忽略叶间相位的影响，建该双级压气机试验件的单扇区流体域模型，如图6-26所，其中为了保证叶表边界层格的正交性，且利于第级转叶在叶振荡作下的定常流场分析，将每个流体域中的叶表附近划分为0形格，在远离叶表的其他区域划分为H形格。

在标准进条件下，指定第级转叶的进总温288.15K、总压1atm，在第级静叶的出给定不同的平均反压，各叶表、轮缘和轮毂均给定绝热、滑移、光滑壁边界条件，在各流体域的循环对称指定周期对称边界条件，各流体域之间的交界给定转静涉边界条件。值得注意的是，计算流体学分析中，均忽略了叶尖间隙的影响，在建计算流体学模型时均未考虑叶尖间隙。

![](images/4c38af22ee05d26c8c71e364bf45448a7254d5f4a19fe46630902a7adacfb4d7.jpg)  
图6-26 双级压机试验件的流体域模型(叶表格）

对该双级压机试验件分别在0.8、0.9和1.0换算转速，给定不同的出口平均反压，定常分析得到该双级压机试验件的特性，并与试验测定的结果进对，如图6-27所。从图中可以看出，不同换算转速下，压机总性能最误差对应的状态点不同。在1.0换算转速下，流量况附近（靠近堵塞边界附近）的总性能吻合较好，低流量况附近（靠近喘振边界附近）的总性能误差较，数值计算得到的总性能均偏；在0.9和0.8换算转速下，低流量况附近（靠近喘振边界附近）的总性能吻合较好，流量况附近（靠近堵塞边界附近）的总性能误差较，数值计算得到的总性能均偏低，且换算转速越，总性能的误差越大。但是总的来说，在不同换算转速下，数值计算得到的从堵塞状态到喘振状态的压气机总性能与试验测定的压气机总性能均基本吻合，且在整个工作范围内总性能的误差值在可接受的范围之内。

![](images/2dfe73af4802aed0b363f2b48f5d50439c6a9c2733f255d43747802c5be721ba.jpg)  
图6-27 双级压机试验件的特性图

以下以1.0换算转速为例，通过改变出口平均反压考察不同工况下该双级压气机试验件的流场特征。在第级转子叶进口总温、总压保持不变的情况下，逐渐增加第二级静子叶的出口平均反压，分别分析双级压气机试验件在近堵塞点工况、近设计点工况和近失速点工况下的流场特征。

当第级静叶出口平均反压较低时，双级压气机试验件处于近堵塞点况，但是由于两级匹配的问题，此时仅第级转子叶处于近堵塞点工况，而第二级转叶已经比较靠近失速点况，图6-28所示为近堵塞点况不同叶的马赫数等值线图。在 $90 \%$ 叶处，第级转叶的槽道激波位于吸面尾缘附近，并打在相邻叶压力面的弦中附近位置，波后在尾缘附近存在较小的气流分离，第二级转子叶也存在一个相对较强的正激波，该激波位于叶片前缘附近，并打在相邻叶片的吸力面弦中附近位置，同时，第一级和第二级静叶的槽道中均未出现明显的激波，流附体较好；在$30 \%$ 叶处，第二级转子叶的槽道中也存在一道激波，但转子叶上的激波均较弱，且由于第级叶流的进攻相对较，在第级叶尾缘附近也出现了定的气流分离，另外，在第一级和第二级静叶的槽道中也均出现了相对较弱的激波，而且槽道中的气流均附体较好。

![](images/547b112dfa4a6994555485adde36e1c73fa868e596bb3143a63dbaaec70f0c99.jpg)  
图6-28 近堵塞点况

随着出平均反压的增加，当流场处于近设计点况时，第级转叶处于近设计点况，但是第级转叶进步向失速点况靠近，图6-29所示为近设计点况不同叶的马赫数等值线图。在 $90 \%$ 叶处，第一级转子叶的激波沿槽道向前移动，成为槽道正激波，波后也存在一定的气流分离，第二级转子叶的激波逐渐被推出了槽道成为脱体激波，激波强度增加，叶吸面也出现了一定的流分离，同时，第级和第级静叶的槽道中均未出现明显的激波，流附体较好；在 $30 \%$ 叶高处，第转叶的弱激波强度有一定的增加，在吸面前缘附近均存在一个加速区，尾缘附近存在一定的流分离，第级转叶的激波被推出槽道成为脱体激波，另外，第级和第级静叶上的激波均消失，流速度增，流均附体较好。

当出平均反压进步增加时，况向失速点靠近，第级转叶逐渐靠近失速点况，但是第级转叶已经达到失速点况，图6-30所为近失速点况不同叶的马赫数等值线图。在 $90 \%$ 叶处，第级转叶的槽道激波进步前移至叶前缘成为正激波，并打在吸力面弦中附近位置，在波后存在一定的流分离，第二级叶的脱体激波位置几乎不变，但是激波强度增大，波后边界层增厚，并产生较大的气流分离；同时，第一级和第二级静子叶槽道中仍未出现激波，流附体较好；在$30 \%$ 叶处，第一级和第二级转叶的激波均几乎消失，但是在叶吸面前缘附近均存在个局部超声区，且由于第级转叶进流攻较，在局部超声区后存在较的流分离，但是第级叶气流依然附体较好，另外，在第级和第级静叶槽道中，流速度均进步增，但依然附体较好。

![](images/24c3b7fcb851ce5503beb8c1d774a641a567187f68bb86ce0414a7de74ab89b9.jpg)  
图6-29 近设计点况

![](images/cbe5a939e8dcb7bf4d3e6ddeb3ab91abbe3232196777e6f632136f8f98aae7cc.jpg)  
图6-30近失速点工况

# 6.3.4 非定常流场分析及颤振边界预测

定常分析后，引入第二级转子叶片一阶弯曲模态的振荡作用进行非定常流场分析，其中，将双级压气机定常分析的结果插值到第二级转子叶片的非定常分析中作为初始条件。在非定常流场分析中，指定第级转叶以第阶弯曲模态振动，表面格点坐标按照正弦规律振动，振动频率为叶的固有频率。值得注意的是，在不同转速下，第级转叶的振型和固有频率均有定的变化。

在定常流场分析中，当流场流参数达到振荡稳定后，读取流场中叶表格点在个振荡周期内各时间步的非定常动和对应格点的振动位移，进步地，计算得到叶表格点在个振荡周期内的定常动功以及模态动阻尼。表6-2分别列出了第级转叶在阶弯曲模态振荡作下不同况的定常动功和模态动阻尼。从表中可以看出，在1.0换算转速的不同况下，第级转叶的阶弯曲模态的振荡作会导致不同的动弹性稳定性。在双级压机试验件的近设计点况下，定常动功为负，模态动阻尼比为正，作在叶表的动阻尼在耗功，叶振动能量不断减少，系统的动弹性稳定；双级压机试验件在近失速点况下，定常动功为正，模态动阻尼为负，叶不断地从流中吸收能量，叶振动能量不断增加，系统动弹性失稳。因此，可以认为：该双级压机试验件第级转叶将发阶弯曲失速颤振，这与试验测得的结果相吻合。

表6-2 第级转叶的非定常动功和模态动阻尼  

<table><tr><td rowspan=1 colspan=1>工况</td><td rowspan=1 colspan=1>非定常气动功/(10-5J)</td><td rowspan=1 colspan=1>模态动阻尼比/%</td></tr><tr><td rowspan=1 colspan=1>近设计点</td><td rowspan=1 colspan=1>-5.756</td><td rowspan=1 colspan=1>0.382</td></tr><tr><td rowspan=1 colspan=1>近失速点</td><td rowspan=1 colspan=1>4.580</td><td rowspan=1 colspan=1>-0.304</td></tr></table>

另面，在1.0换算转速下，考虑第二级转叶在阶弯曲模态下的振荡作，选取该双级压机试验件的近失速点况进定常流场分析，得到个稳定振荡周期内第级转叶表各格点的定常动功分布，如图6-31所。从图中可以看出，吸力面的波后区域存在一个高梯度的正功区，波前存在一个较梯度的负功区，而相对吸力面的定常动功分布，在压面上非定常气动功分量均较，并明显的非定常动功集中区。因此，以下在分析该双级压机试验件第二级转叶的动弹性稳定性时，仅关注第二级转叶吸面的动功分布。

![](images/c4d1594d654dcfd4f5944d2cf172a56a9a040840e92608b4e2913ea36e2364ba.jpg)  
图6-31 第级转叶的定常动功分布

在多级压气机的不同工况下，各级叶栅吸力面的激波强度和波后分离流动均存在很大的变化。为了进步考察激波和波后流分离对叶动弹性稳定性的影响，本节对分析了不同工况下叶片吸力面的非定常气动功分布，并用于探讨多级压气机情况下叶颤振机理。

在1.0换算转速下，改变第二级静子叶的出口平均反压得到该双级压气机试验件的不同工况，选取出口平均反压分别为 $1 8 0 \mathrm { k P a }$ 和 $2 0 0 \mathrm { k P a }$ 对应的况，计算得到叶吸面的静压分布及其流线图，如图6-32所示。

![](images/3edb832df97d29320f9fdc6e2b7497804dfff37b96ee4f7b651bd04d6cd731d3.jpg)  
图6-32 第级转叶吸静压分布及其流线图

从图中可以看出，随着第二级静叶出口平均反压的增，该双级压机试验件第二级转子叶的激波位置沿弦向变化较小，但是激波强度有了明显的增加。当出口平均反压为 $1 8 0 \mathrm { k P a }$ 时，如图6-32（a）所示，第二级转子叶吸力面的激波相对较弱，波后流有较的径向潜流，波后流附体较差；当出平均反压进步增加并达到$2 0 0 \mathrm { k P a }$ 时，如图6-32（b）所示，第二级转子叶片吸力面的激波略有前移，但激波强度明显增加，波后气流有较大的径向潜流，吸力面波后区域有一定的气流分离。由于双级压气机试验件的多级匹配问题，在压机的整个工作范围之内，第级转叶吸力面的激波位置并未发生较大的变化，均位于叶片前缘附近。

分别对图6-32所示的两种况进非定常流场分析，得到一个稳定振荡周期内第二级转叶吸的定常动功分布，如图6-33所。从图中可以看出，当第级静子叶片出口平均反压为 $1 8 0 \mathrm { k P a }$ 时，第二级转叶吸力面没有较大的正功集中区但存在个相对较的负功集中区，同时正功区相对靠后；当第级静叶出平均反压达到$2 0 0 \mathrm { k P a }$ 时，第二级转子叶片吸力面的正功区梯度增大，且沿吸力面前移，在叶片吸力面出现了个较的正功集中区，该正功区前后区域的定常动功均为负值。对图6-32中的吸力面静压分布与图6-33中的吸力面非定常气动功分布，可以发现，正负非定常气动功集中区的分界线几乎与激波位置相对应，且波前为负功区，波后气流分离对应的区域为正功区，即激波和波后气流分离是导致正的非定常气动功区域出现的主要因素。因此，在多级压机情况下，激波和波后流分离仍然是叶动弹性失稳的重要原因。

![](images/22644f43194d3a4129ad0f2674d8d5143203b6a7af151564be8902b23441f460.jpg)  
图6-33 第级转叶吸的定常动功分布

另外，分别在0.8、0.9和1.0换算转速下，改变第二级静叶出口平均反压，对双级压机试验件进定常流场分析。当流参数达到稳定振荡后，选取个振荡周期内各不同时刻的计算结果，通过定常动及其振动位移计算定常动功，基于能量法得到第级转叶在阶弯曲模态振荡作下的模态动阻尼，并插值得到双级压机试验件整个作范围内的模态动阻尼。在压机特性图中找出模态动阻尼为0对应的况，得到双级压机转叶的颤振边界，并与试验测得的颤振边界进对比，如图6-34所。从图中可以看出，数值计算和试验测得的颤振边界基本吻合，但是数值计算得到的颤振边界相对更保守些，其中一个最主要的原因就是数值计算中忽略了包括材料阻尼、结构阻尼等在内的机械阻尼的影响。

![](images/2b12756715d0708f1344d2faf2cca0670175e2fca4b15f94d52117fa8b588901.jpg)  
图6-34 双级压机试验件颤振特性图

# 6.4小结

将所发展的流固弱耦合数值预测方法应用于某压气机第一级转子叶，对比分析了叶模态、进口流攻、折合频率、进口相对马赫数、激波与波后流分离以及叶间相位等多个参数对叶轮机械叶动弹性稳定性的影响，其中，叶间相位的影响是通过建立全环叶栅模型来分析的。分析结果表明：

（1）叶模态对叶轮机械叶动弹性稳定性起着决定性的影响，攻、折合频率，以及进口相对马赫数对叶轮机械叶动弹性稳定性也有重要的影响；

（2）叶间相位角反映了叶片振荡之间的相互作用，即相邻叶片通过槽道中的气流耦合作，对叶轮机械叶的动弹性稳定性有着显著的影响。

（3）吸力面正功区基本对应着吸力面上激波后的逆流区，因而激波与波后气流分离的共同作用是导致叶轮机械叶发动弹性失稳的重要原因，可以用于解释叶轮机械叶片的颤振发作机理；

另外，为了进步探讨多级压机匹配下叶颤振的机理和规律，在双级压机试验件上开展的颤振试验基础上，采用流固弱耦合数值预测法，分析了该双级压气机试验件第级转叶的动弹性稳定性，并进步通过多级压机情况下叶吸动功分布与激波和波后气流分离的对应关系，考察验证了激波和波后流分离是导致叶动弹性失稳的重要原因的结论，可于探讨多级压机情况下叶的颤振机理。

# 参考文献

[1]张伟．叶轮机械叶弹稳定性数值预测法研究[D．北京：北京航空航天学，2011.  
[2] X W Zhang, Y R Wang, K N Xu, Flutter prediction in turbomachinery with energymethod [J]. Proc. IMechE, Part G: Journal of Aerospace Engineering, 2011, 225(9）：995-1002.  
[3] Xiaowei Zhang,Yanrong Wang, Kening Xu, Mechanisms and key parameters for com-pressor blade stall flutter [J]. ASME Journal of Turbomachinery, 2013, 135 (2）:024501-1\~4.  
[4]李其汉，王延荣．航空发动机结构强度设计问题[M]．上海：上海交通学出版社，2014.

# 第7章 转动结构疲劳可靠性分析方法

# 7.1引信

# 7.1.1结构可靠性

航空发动机结构可靠性是指其结构件（包括叶、轮盘、机匣/燃烧室、转系统等)在规定的使用环境与载荷下，在规定的寿命期内完成工作的能力。这种能力通常要求用概率，即结构可靠度进表征。

发动机结构件的失效模式通常包括，但不限于：低循环疲劳、循环疲劳、蠕变/应断裂、氧化/腐蚀等。针对给定的失效模式，其结构可靠度应通过分析与试验的法确定。

有时不同失效模式并存，且相互影响，这种多失效模式耦合下的可靠性设计分析法还有待发展。

在不具备定量分析、评定结构件的可靠性时，应采用定性的方法对结构件的主要失效模式进设计分析，尽可能考虑结构可靠性设计要求。

# 7.1.2 结构设计的概率表征

发动机结构设计参量需要计分散性影响，通常包括（但不限于）：几何构型、材料学为及其构件状态的抗、作环境及其载荷等。此外，还要考虑些设计参量的时变影响。这些随机量需要进概率表征才能于结构概率设计分析。

原则上，可以根据参考机型、类似机型的相关统计分析，以及所设计机型的预期使环境、载荷及其材料、艺状态进概率表征，现有的技术状态要实现概率表征尚需要长期实践及其程经验的积累，并不断发展、完善概率设计分析法及其程设计体系。

（1）结构何构型的概率表征

发动机结构件的何形状与尺寸具有定的分散性，应根据结构设计公差与艺技术状态对其进概率表征。对易于形成应集中的何特征（但不限于）如：圆、孔、槽等何突变处，要给予够的重视。在条件允许的情况下，宜进定量表征；反之，至少应进行确定性分析。

原则上，可以根据结构概率设计分析来确定结构设计公差（反问题），然而在当前的技术状态下实现正问题分析仍需要量数据及其相关经验的持。

设计中，对应力集中的典型几何特征，如圆等应计其分散性的影响。

（2）材料力学为的概率表征

发动机结构件材料的力学行为有一定的分散性，这种分散性可以通过材料工艺控制使其限制在一定的范围内。此外，描述材料力学行为的参量还由服役时间、环境（热、腐蚀/氧化）等控制。

通过材料，尤其是构件的工艺状态的试验确定描述其力学为的参量，并进统计分析，实现概率表征。在条件允许的情况下，应针对给定材料工艺状态及其不同批次，进行概率表征；反之，至少应进行确定性分析。

（3）构件状态抗力的概率表征

发动机构件状态的抗力不同于材料标准试件状态的抗力，尤其表现在其分散性上，其主要影响因素包括（但不限于）：结构几何特征和工艺状态等。这种分散性可以通过结构几何特征和工艺控制使其限制在一定的范围内。此外，构件状态的抗力也由服役时间、环境（热、腐蚀/氧化）等控制。

针对给定的艺状态，通过具有结构何特征的模拟构件或实际构件的抗试验，确定描述其构件抗的参量，并进统计分析，实现概率表征。在条件允许的情况下，应针对给定工艺状态和结构几何特征，进概率表征；反之，至少应进行确定性分析。

（4）结构载荷的概率表征

发动机结构件所承受的载荷主要包括（但不限于）：机械载荷、气动载荷、热载荷等，而且并非稳态载荷；不同载荷类型，其随时间变化的非定常性不同。同时，结构载荷还随发动机功率状态的变化而变化。此外，即使同型号的发动机，由于配装飞器的不同或飞环境条件不同，其结构载荷状态会有明显的不同。这些诸多不同或变化最终导致的是结构载荷的分散性极为显著。

对于发动机结构件，载荷的概率表征极为重要，亦极为困难。这也是制约发动机结构可靠性设计的主要瓶颈之一。原则上，可用统计分析方法对结构载荷进概率表征。由于结构载荷极为复杂，基于当前的技术水平，即使在条件允许的情况下，也宜针对给定结构件的特定失效模式进其载荷的统计分析，给出概率表征（当然，准确性与合理性应经过检验）；反之，至少应进确定性分析。

（5）环境与时间历程的影响

发动机结构件材料的力学为、构件状态的抗力，以及其分散性，受环境与时间历程的影响显著。在条件允许的情况下，其概率表征应计环境与时间历程的影响；反之，至少应进行确定性分析。

# 7.1.3 结构概率响应分析

用概率设计裕度取代传统的安全系数或确定性裕度，能够准确地表示构件响应的变化。关于这些设计变量本质的理解对设计出能够满足指定要求、健壮的构件和保证可靠性是关重要的。在对最终设计有重影响的情况下，特别强调应使概率设计裕度。

概率设计要求使用分析模型和概率积分方法来预测响应的概率分布，从而确定破坏（失效）状态的概率。这种模型要求确定和验证系统中重要随机变量的敏感度。概率积分法中的输（设计）变量须按统计的模型或概率分布的形式进表征，并建变量间的统计相关性模型。获得足够多的数据后，就可确定通常所说的“最小值”（但不限于）如：均值、 $- 3 \sigma$ 或 $B _ { 0 , 1 }$ 等。将这些数据模型与经过验证的分析模型和有效的概率积分法结合起来使用，以期计算结构系统的概率响应。

用响应的概率分布和失效模式抗力的限制来确定结构破坏的概率。破坏的概率必须满给定结构件的可靠性要求。概率设计裕度应按破坏概率来规定。该裕度也应该每发动机飞时或每次任务的风险来表达。

为保证结果的置信度，应验证：个或多个随机变量组合出现的概率，或破坏限制取决于每个随机变量的概率，这些变量应在试验数据库的范围内。结果的置信度是建在充分的物理模型基础上的，这些物理模型应能实现精准的模拟。

在结构初步设计时，可以使用确定性裕度。当概率解不具有足够高的置信度时，也可使用确定性裕度。

# 7.1.4 结构可靠性设计

结构可靠性设计的理论基础是应力-强度干涉理论。对于发动机结构件，其应是指计结构几何构型、材料力学为、工作载荷及其环境与时间历程，以及其分散性影响的结构响应；其强度是指计入结构特征、工作环境与时间历程，以及其分散性影响的构件艺状态的抗。这的结构响应与抗对于不同的失效模式，甚发动机不同的结构件，具有不同的物理意义与机制。发动机结构可靠性设计就是应概率设计的法在上述结构响应与抗力间进抉择，使结构设计具有要求的可靠度。

对于航空燃涡轮发动机结构可靠性设计，当前的技术平还不以实现多构件、多模式复合失效的可靠性设计。在条件允许的情况下，应针对具体结构，如叶、轮盘、机匣/燃烧室、转系统等给定的失效模式确定概率设计裕度，实现结构可靠性设计；反之，至少应针对给定的失效模式（结构设计准则）进确定性设计分析。

这强调对结构进可靠性设计。但在初步设计时，可以采用确定性设计，或当可靠性设计不具有足够高的置信度时，也可使用确定性设计。

# 7.2 涡轮盘结构可靠性设计法

# 7.2.1 涡轮盘结构特征和载荷/环境的概率表征法

将随机参数进量化处理是进结构可靠性分析的基础作之，本节给出了航空发动机涡轮盘结构可靠性分析中种常见的结构特征和载荷/环境参数的概率表征法。

结构随机变量般可分为随机变量（简单量）、随机场、随机过程，以及随机场和

随机过程的结合。随机因素很多，如材料性能不均匀、加公差、表面完整性的差异、载荷的变化等，可以根据随机因素来源的不同，将这些随机变量分成不同的类型。根据航空发动机结构设计分析的特点，选取以下4类随机变量进研究。

（1）结构几何类随机变量建模

产生结构尺寸随机的因素较多，分析中通常是指由于加工公差的存在而产生的几何尺寸不确定性。大量统计表明，一般可将结构尺寸分布视为正态分布或近似正态分布，其数学期望为结构的名义尺寸，而标准差可以按照“ $3 \sigma$ 原则”，根据结构加公差确定[1]

$$
\sigma _ { x } = \Delta x / 3
$$

式中： $\Delta x$ − 加公差的上、下极限偏差。

当结构尺寸的分布和参数确定后，即可代尺寸参数化处理的有限元等程序中进计算，分析尺寸随机对结构的影响。

随着加工精度的提高，人们对结构加工公差的控制也更为精确。这使得在结构可靠性计算中，尤其是对于其中的结构静强度计算，结构中有些部位对于尺寸随机并不敏感，即尺寸在较小范围内变动对结构造成的影响往往可以忽略；只有在结构的局部，如出现应力集中的孔边、形状过渡用的小尺寸倒角、退刀槽、止动台处，尺寸随机的影响才较为明显。

多数情况下，尺寸随机往往只是一个输量，们关的是尺寸随机对其他参数的影响，此时可以将结构尺寸随机转换为所关心变量的随机，避免对结构进多次建模，节省计算时间。以应力计算为例，为了进尺寸随机到应力随机的转化，需要建立结构尺寸 $( x )$ 与应力 $( S )$ 的响应面函数 $S = G ( x )$ 。这的函数可选用数学多项式，且按照多项式的次数不同，可以形成以下两种不同精度的处理法。

$\textcircled{1}$ 次多项式法

采用次多项式建响应，并取3个样本点确定多项式的3个系数值。这3个样本点为尺寸分布中的 $- 3 \sigma$ ，0和 $+ 3 \sigma$ 点，由这些尺寸值和相应的应力值即可求解

$$
S ( x ) = a + b x + c x ^ { 2 }
$$

$\textcircled{2}$ 四次多项式法

为提精度，还可以采四次多项式构建响应面，并5个样本点来确定系数值，即尺寸分布中的 $- 3 \sigma$ , $- \sigma$ ，0， $+ \sigma$ 和 $+ 3 \sigma$ 点

$$
S ( x ) = a + b x + c x ^ { 2 } + d x ^ { 3 } + e x ^ { 4 }
$$

（2）加艺类随机变量建模

$\textcircled{1}$ 表完整性

表面完整性对结构寿命和可靠性的影响较大，以叶为例，排气边表面完整性较好的叶片比稍差的叶片寿命高 $2 . 8 4 \sim 4 . 7 1$ 倍，疲劳性能差异常明显[2]。

表面完整性是一个非常复杂的问题，其中涉及物理和化学的变化。目前很难用简单的运算将所有的表面完整性问题都包含进来。分析表面完整性的影响时，一般从两个考虑：种是从微观度，依次分析诸多因素对表面完整性的影响；另种被更多的人采用，即从宏观统计的角度，通过对结果的统计分析反推得到表面完整性的影响。

$\textcircled{2}$ 微观表完整性分析

结构的表面粗糙度取决于表面加工的技术条件，可以从微观角度分析其对结构应力集中的影响，并按下式分析

$$
K _ { \iota \mathrm { ~ = ~ 1 ~ } } + 2 \sqrt { \gamma h / \rho }
$$

式中： $h$ (id 微观不平的高度；

$\rho$ 波的曲率半径；

$\gamma$ 不平度间距与其度之的相关系数。

然对结构的疲劳，实际上最终起作的是有效应集中系数，即

$$
K _ { \mathrm { f } } \ = \ 1 + q ( K _ { \mathrm { t } } - 1 )
$$

式中： $q$ (id:) -材料对应集中的敏感系数[3]。

表的残余应可以由H.O.Fochs判据[41来判断疲劳载荷下是否会松弛

$$
\sigma _ { \mathrm { ~ m ~ } } + \sigma _ { \mathrm { ~ a ~ } } + \sigma _ { \mathrm { ~ r ~ } } > \sigma _ { \mathrm { ~ s ~ } }
$$

式中：σ 平均应力；

$\sigma _ { \mathrm { { a } } }$ 应力幅；

$\sigma _ { \mathrm { { \it r } } }$ 残余应力；

0 材料的屈服极限。

当发残余应松弛时，表残余应对结构疲劳寿命影响较；否则，影响较。

表面加工硬化后结构的疲劳性能变化比较复杂。这是由于表面硬度的提高和残余应的分布所造成的[5]，前尚没有更为具体的计算法。

$\textcircled{3}$ 宏观统计分析

由于影响表面完整性的因素很多，而且这些影响因素之间相互关联，不容易区分清楚，这种情况下，从整体上把握表完整性的影响，采宏观统计的法比较有效。此时可以引表面完整性因子 $\beta$ （也可称为表面加工系数），该因子作用于材料的强度，对材料强度参数（通常是强度分布的数学期望）产生影响，即

$$
\mu _ { \mathrm { ~ c ~ } } = \mu _ { \mathrm { { r } } } \beta
$$

式中： $\mu _ { r }$ (id 标准光滑试件强度的数学期望；

$\mu _ { \mathrm { ~ c ~ } }$ bcid:) 实际加工构件强度的数学期望。

参考献[6给出了些表加系数的统计值，这些值随结构的加条件（车削、热轧、锻造、抛光）和受情况（弯曲、拉压、扭转）而不同，并且也有均值和差。般情况下，相同的材料在不同加条件下其表加系数的散度变化不[12]。

表面完整性对结构寿命的影响须慎重考虑，有的情况下会促使结构的破坏，而有的情况下会增加结构的寿命，因而 $\beta$ 般情况下于1，但也可能于1。在实际机械设计中，为保守起见，一般对于 $\beta$ 于1的情况仍取其为 $1 ^ { [ 1 3 ] }$

表完整性是结构可靠性分析中的个难点，现有的计算般还未细致考虑这个因素的影响。总体上，通过微观的法来研究表完整性，是从机理上分析现象，难度较；而从统计学法描述现象，所给出的结果是比较笼统的，需要量的数据持和丰富的经验。

（3）载荷类随机变量建模

$\textcircled{1}$ 转速

对于旋转机械，转速是个重要的随机变量，一般通过转速传感器等仪表来监测转速的大小，并通过调节供油量来控制转速，使其达到一个相对稳定的值。转速一般可认为服从正态分布，其数学期望为设计转速或标转速，而其偏差由转速控制的精度和要求决定，可参照前述的尺寸标准差的做法来确定，此时Δx为转速控制的上、下极限偏差。

$\textcircled{2}$ 温度场

温度场不是个简单的随机量，而是随机场问题；而瞬态温度场属于随机过程的范畴，随时间不断发生变化。

对于稳态温度场，场中的每一点都降阶为一个单一的简单随机量，于是有一种解决方案是可以将温度场离散化，并将场中的每点处的温度都看成是简单随机量，如图7-1所示，A，B，C点均拥有各自的随机分布函数，并相互独立，其不足之处在于以下几点。

a．将个随机问题离散成为众多随机问题，增加了问题的复杂性，且难以给出各处温度的散度系数。

b.不符合温度场的自然规律，图中A，B，C点的温度尽管是随机的，但它们之间并不是孤立的，存在着相互的影响，这种影响受传热学基本定律的制约。

c.对于瞬态温度场，这种方法难以应用。

![](images/9986ae8807d3b0106ee53ffeb2934845c0791dbe0454af3620f134969725cba3.jpg)  
图7-1 温度场离散后的随机变化

温度场尽管是一个随机场和随机过程的结合，但仍可以将温度场视为结构的热边界条件发生了随机变化从而引起温度场的变化，如图7-2所示，结构区域内A，B，C等点的温度变化是由于热边界条件D点的温度发了随机变化。在实际结构中，D点是义的，可以是一个关键点温度，也可以是一个连续的边界条件，甚至可以是传热学中某些重要控制参数，如热传导系数。只要得到该边界条件的随机规律，并按传热学规律计算不同条件下的温度场分布，就可以实现温度场的随机。这种处理方法将随机场问题降阶为简单随机量问题，同时遵守热传导规律，更加符合实际。

事实上很多常见的场问题可以类似地进建模，如某些情况下应力场随机可以看作是外载随机作用下产生的变化。

![](images/1aafec80ec9448911e95541bde54fadcf14d97dad85429873ea9a10041c1d821.jpg)  
图7-2 边界条件的随机引起的温度场随机变化

（4）材料参数类随机变量建模$\textcircled{1}$ 材料弹性模量和泊松比

材料的弹性模量和泊松比一般认为服从正态分布（或对数正态分布），其均值和标准差可在材料数据册中查出，一些常材料的变异系数可参见参考献[7，8，11；有时也可以根据经过验证的经验给出这些数据。

材料弹性模量和泊松比实际上也是随机场，因为结构中每个位置都具有当地的弹性模量和泊松比，只是出于材料“均匀性”假设，当结构处于完全均温的状态时，可认为结构中所有位置处的弹性模量及泊松比都是相同的，这时便没有反映出这两个变量的“场”特征。

事实上弹性模量和泊松比都是随温度而变化的，当结构均温时，两者的“场”特征便突显出来，现以弹性模量为例说明这个问题，泊松比的性质和处理法与弹性模量的类似。

同温度场样，弹性模量的“场”问题不能采结构内任点处的弹性模量独随机的法。其随机的处理法如图7–3所，图中 $t _ { A }$ , $t _ { B }$ 两个温度下的弹性模量都是正态分布的随机量，可认为两个温度下的弹性模量在换算成标准正态量后数值相等，即

$$
{ \frac { E _ { \scriptscriptstyle A } - E _ { \scriptscriptstyle A } } { \sigma _ { \scriptscriptstyle A } } } = { \frac { E _ { \scriptscriptstyle B } - E _ { \scriptscriptstyle B } } { \sigma _ { \scriptscriptstyle B } } }
$$

式中： $\sigma _ { A }$ , $\sigma _ { B } - - t _ { A }$ , $t _ { B }$ 时弹性模量的标准差。

如果认为弹性模量的标准差不随温度变化，则上式可以简化为

$$
E _ { _ A } - \overline { { E } } _ { _ A } \ : = \ : E _ { _ B } - \overline { { E } } _ { _ B }
$$

$\textcircled{2}$ 材料强度

对于材料强度随机性，这主要考虑的是材料疲劳强度分布。对于应力疲劳，其疲劳强度分布为[9]

$$
g ( S ) \ = \frac { \mu ( S ) \sigma ^ { \prime } ( S ) \ - \mu ^ { \prime } ( S ) \sigma ( S ) \ - \sigma ^ { \prime } ( S ) \mathrm { l g } N ^ { * } } { \sqrt { 2 \pi } \sigma ^ { 2 } ( S ) } \ \exp \Big ( \ - \ \frac { [ \mathrm { l g } N ^ { * } \ - \mu ( S ) ] ^ { 2 } } { 2 \sigma ^ { 2 } ( S ) } \Big )
$$

![](images/4c23bd1bc53400259bcfbce5e83cc8f2cc5c3cc59d12d3987cc7963f59e1d681.jpg)  
图7-3 弹性模量的随机法

式中： $\mu$ (S), $\sigma$ （S）对数寿命的均值和标准差的拟合曲线；

$\mu ^ { \prime } ( S )$ , $\sigma ^ { \prime } ( S ) \mathrm { ~ } \longrightarrow \mu ( S )$ , $\sigma ( S )$ 的一阶导数。

后面的轮盘结构可靠性数值算法中提出了一种不用直接求疲劳强度而计算结构可靠性的法。应变疲劳强度分布与前者类似，具体算法可参见参考献[10。

# (5）数值算例

长、宽、厚为 $1 0 0 \mathrm { { m m } \times 1 0 0 \mathrm { { m m } \times 1 \mathrm { { m m } } } }$ 的平板，弹性模量 $E = 2 0 0 \mathrm { G P a }$ ，泊松比 $\nu =$ 0.3。现拟在平板正中开孔，孔的尺寸设定为 $\phi \ 2 0 \ _ { - 3 } ^ { + 3 } \mathrm { m m }$ ，平板两边受均匀拉力 $p =$ $1 0 \mathrm { { M P a } }$ 。孔边的应为所关心的随机量，现采直接蒙特卡罗法、次法和四次法分析孔边应力的分布情况。

直接蒙特卡罗法选用ANSYS程序的概率设计模块（PDS）来完成。根据式（7-1），孔半径服从正态分布N(10，0.5）。抽样计算1000次。图7–4给出了孔半径抽样样本的分布情况，图7–5出了孔边应的分布情况。

![](images/810aee6f5cca17ae2593fb057abf2dde60818e6d48307d45f278ffef83f21d2f.jpg)  
图7-4 孔半径随机情况

![](images/fe9afdbbad660f300fcd11d810ff7647409e10995028e7d70cf2ff7e5006b71b.jpg)  
图7-5 孔边应随机情况

采用二次法和四次法计算孔边应力分布，以PDS模块的直接蒙特卡罗抽样计算结果作为参考值。图7-6和图7–7给出了两种法得到的应分布累积概率值，可以看出，两种方法的计算结果与直接蒙特卡罗抽样的十分接近。图7-7则给出了这两种方法与直接蒙特卡罗法结果的差异，图中表明，次多项式法的计算结果已经具有较的精度，四次多项式法则基本上看不出差别。

![](images/fb31d0f58e67c940081ab18db6b7574bc6842365043addb38ed2a240f8ef5cf6.jpg)  
图7-6 尺寸随机下的可靠度

![](images/c210b2d67c2eb971b7257030fd3da24c977441fc41ba8849e2e34ee0bc21d457.jpg)  
图7-7 尺寸随机计算误差

长、宽、厚为 $2 0 \mathrm { { m m } \times 1 0 \mathrm { { m m } \times 0 . 1 \mathrm { { m m } } } }$ 的平板，弹性模量 $E = 2 0 0 \mathrm { G P a }$ ，泊松比 $\nu =$ 0.3。拟在平板两边的对称位置开孔，孔的加工尺寸设定均为 $\phi 4 \mathrm { m m }$ ，平板四边受恒幅( $\Delta \sigma = 2 0 0 \mathrm { M P a } ,$ ）对称疲劳载荷（ $R = - 1$ ）作用，其周边具有不同的表面加工系数，如图7-8所示，设 $A$ 所代表的直边表面加工系数 $\beta = 0 . 6 6$ , $B$ 孔表面 $\beta = 0 . 9 8$ , $C$ 孔表面$\beta = 0 . 9 3$ 。设平板中所有节点的应均服从正态分布，并取平板在受循环应过程中各节点的第一主应力极大值作为该节点的应力均值，标准差均取为 $1 0 \mathrm { { M P a } }$ ，其中平板在两边受最拉应时的第主应分布如图7-9所；材料的疲劳强度分布服从正态分布N（250，20）（单位：MPa）。现分析平板在随机载荷作用下的结构可靠性。

![](images/ca73120c045c97623ef441c703fa3bfa75b525400b7aec89abd4682d8147f545.jpg)  
图7-8 A，B, $C$ 在平板中的位置

![](images/10582f06f0060321d47bf9438624418107173dfaa17d3000f9577233cea646af.jpg)  
图7-9 第主应力

图7-10和图7-11给出了利ANSYS次开发计算的平板结构可靠度分布，前者比后者多考虑了表面完整性的影响。由图7-10可以看出，孔边由于受应集中的影响，结构可靠度较低；且右侧孔（孔 $C$ ）由于表面质量较左侧孔（孔 $B$ ）低，其可靠度也降到了最低值；平板四周（A边）的应力相对稍远处较小，但由于表面完整性的影响，其可靠度也偏低。所以此平板如果发破坏，最可能先会出现在右侧孔边，然后是左侧孔边，随后是四条周边。

![](images/c950cc128f9004704c37b260a0825711acfa5946c7ff2b3dab8f3f3fe9f4612e.jpg)  
图7-10 考虑表完整性的结构可靠度

![](images/5a681526ebeb04ce51262665c7bacdb1cc57ce3a398838ef06c193262a7ef198.jpg)

![](images/54c0fa46f714b928c631ebdc9e021283f619445721fcaece8245c120f3c99876.jpg)  
图7-11 不考虑表完整性的结构可靠度

# 7.2.2 涡轮盘结构单一失效模式的可靠性模型

（1）失效模式分析

失效模式分析的主要任务是根据确定性有限元计算出的结构力学参数来分析该结构可能产生的失效模式。由于受复杂载荷与环境的作用，轮盘可能发生多种失效，比较常见的失效模式为[11]： $\textcircled{1}$ 轮盘超转破裂； $\textcircled{2}$ 轮盘低循环疲劳； $\textcircled{3}$ 轮盘振动引起的循环疲劳； $\textcircled{4}$ 轮盘裂纹扩展及断裂； $\textcircled{5}$ 轮盘外径伸长变形； $\textcircled{6}$ 轮盘腹板屈曲变形。

虽然轮盘可能发生的失效模式有多种，但在一定时期或一定状态下，轮盘发生的失效模式往往又是单一的，该种模式将主导轮盘的失效。准确抓住主导失效模式及其成因，是准确分析整个轮盘失效并进行结构可靠性分析的前提。

（2）结构功能函数的建

结构失效理论中定义结构达到失效瞬间的状态为结构的极限状态。不同的极限状态是不同失效模式的具体表现。根据结构失效时所处的状态不同，一般可将极限状态分为以下三类[12]： $\textcircled{1}$ 承载能力极限状态，这种极限状态对应于结构达到最大承载能力，或达到不适于继续承载的变形； $\textcircled{2}$ 正常使用极限状态，这种极限状态对应于结构达到正常使用和耐久性的各项规定极限值； $\textcircled{3}$ 逐渐破坏极限状态，指偶然作用后产生的次生灾害限度，即结构因偶然作用造成局部破坏后，其余部分不发生连续破坏的状态。

显然结构功能函数随结构极限状态的不同而不同，如超过疲劳强度的失效与超过应力极限的失效具有不同的功能函数。同时功能函数还会因对物理现象的着眼点，或者是研究的切入点的变化而不同，如有些方法选择从名义应力的角度出发，这种情况较多出现在结构处于线弹性阶段时；有些选择从局部应力/应变的角度分析，这种情况多见于结构发了局部塑性变形；还有一些研究方法则从能量的度来考虑问题，这类研究法较前两者复杂，但在处理多轴应力情况和不同加载方式的影响等问题时具有较好的效果[13]

对于相同的失效模式，结构功能函数也可以不同，这与所关心的失效参量的选择相关，如对于疲劳失效，可以选择加载载荷大小作为失效参量，当载荷超过疲劳极限时判断失效，并以此建结构功能函数；也可以选择疲劳变形量，或者裂纹长度等其他参量来建结构功能函数。这些结构功能函数虽然具有不同的形式，但本质上应该是致的，因为不同参量只是从不同的度反映了同个结构失效的过程。然而在实际计算中，一些方法由于本身的原因，计算得到的结构可靠性结果依赖于功能函数选取，如中心点法。

尽管结构功能函数多种多样，但般都具有相同的出发点，即表征义“应”概念的 $S _ { s }$ 与义“抗”概念的 $S _ { \mathrm { r } }$ 之差来表示

$$
Z = G ( S _ { s } , S _ { r } ) = S _ { s } - S _ { r }
$$

轮盘结构可靠性分析中，较常见的结构功能函数可以归纳于表7-1中。

表7-1 轮盘结构可靠性分析中常见的结构“应”与“抗”简表  

<table><tr><td rowspan=1 colspan=1>失效方式</td><td rowspan=1 colspan=1>Ss</td><td rowspan=1 colspan=1>S.</td></tr><tr><td rowspan=1 colspan=1>断裂/破裂</td><td rowspan=1 colspan=1>结构应力S</td><td rowspan=1 colspan=1>材料强度极限S／许用应</td></tr><tr><td rowspan=1 colspan=1>裂纹萌生/扩展</td><td rowspan=1 colspan=1>裂纹J积分/K因子</td><td rowspan=1 colspan=1>Je1Ke</td></tr><tr><td rowspan=1 colspan=1>高循环疲劳</td><td rowspan=1 colspan=1>结构应力S</td><td rowspan=1 colspan=1>材料疲劳极限SN</td></tr><tr><td rowspan=1 colspan=1>低循环疲劳</td><td rowspan=1 colspan=1>结构应变范围Δε</td><td rowspan=1 colspan=1>材料应变疲劳极限△G</td></tr><tr><td rowspan=1 colspan=1>振动</td><td rowspan=1 colspan=1>强迫振动响应的放大因子β</td><td rowspan=1 colspan=1>许用放大因β[14]</td></tr></table>

表7-1中的 $S _ { N }$ 可由结构材料的 $S - N$ 曲线求得； $\Delta \varepsilon _ { \mathrm { G } }$ 可由结构材料的 $\varepsilon - N$ 曲线求得，或由材料的Manson-Coffin公式（或其修正形式）给出

$$
\frac { \Delta \varepsilon _ { \mathrm { t } } } { 2 } = \frac { \sigma _ { \mathrm { f } } ^ { \prime } - \sigma _ { \mathrm { m } } } { E } \left( 2 N _ { \mathrm { f } } \right) ^ { { \it b } } + \varepsilon _ { \mathrm { f } } ^ { \prime } ( 2 N _ { \mathrm { f } } ) ^ { { \it c } }
$$

结构功能函数有显式和隐式两种，显式功能函数可直接计算得到其函数值，计算速度通常比较快。但工程分析中显式功能函数并不多见，而且这种显式功能函数一般是在已有数据的基础上通过统计分析或以经验公式的形式给出。然，程中量存在的是隐式功能函数，实际结构分析中的有限元计算即属于这类，其功能函数是有限元模型不是显式表达式，般隐式功能函数的计算速度相对较慢。

前结构功能函数的建，主要是针对疲劳载荷谱简单且恒幅的情况。当个构件承受变幅载荷时，计算将更为复杂，般采迈因纳（Miner）累积损伤理论或其他损伤（如科尔顿-多兰（Carten-Dolan）理论、法兰肯塔尔-黑勒（Freudenthal-Heller）理论等）来考虑变幅的影响。对于从结构在有缺陷的情况下仍能作的度出发来探讨结构的可靠性，则属于损伤容限可靠性[15]（对此，这不再赘述）。

# 7.2.3 涡轮盘结构可靠性算法的程序实现

（1）轮盘应力疲劳的可靠性模型

$\textcircled{1}$ 应疲劳强度理论

根据材料疲劳强度理论，材料在给定寿命 $N ^ { * }$ 时的疲劳强度函数 $\psi ( S )$ ,其概率密度函数可以由材料的疲劳寿命分布获得[9]

$$
g ( \psi | N ^ { * } ) ~ = ~ { \frac { \mathrm { d } } { \mathrm { d } \psi } } \int _ { \phi ( N _ { \mathrm { m i n } } ) } ^ { \phi ( N ^ { * } ) } f ( \phi | S ) \mathrm { d } \phi
$$

式中： $N _ { \mathrm { m i n } }$ -最小疲劳寿命；

$f$ ${ \bf \Phi } ( \phi | S )$ − 在应力 $S$ 下的寿命分布的概率密度函数。

工程结构中，材料在给定应力 $S$ 下的对数疲劳寿命分布一般服从正态或威布尔分布。对于前者，式（7-13）可以简化为

$$
g ( S ) \ = \frac { \mu ( S ) \sigma ^ { \prime } ( S ) \ - \mu ^ { \prime } ( S ) \sigma ( S ) \ - \sigma ^ { \prime } ( S ) \mathrm { l g } N ^ { * } } { \sqrt { 2 \pi } \sigma ^ { 2 } ( S ) } \mathrm { e x p } \Big ( - \frac { [ \mathrm { l g } N ^ { * } \ - \mu ( S ) ] ^ { 2 } } { 2 \sigma ^ { 2 } ( S ) } \Big )
$$

式中： $\mu ( S )$ , $\sigma ( S )$ ——对数寿命的均值和标准差的拟合曲线，可根据各个指定应平下的疲劳寿命试验数据得到；

$\mu ^ { \prime } ( S ) , \sigma ^ { \prime } ( S ) { \mathrm { - } } \mu ( S )$ , $\sigma ( S )$ 的阶导数。

当疲劳寿命服从威布尔分布时，式（7-13）的具体形式可以表达为

$$
g ( { \psi } \vert { \cal N } ^ { * } ) = \biggl [ \frac { { \cal N } ^ { * } - { \cal N } _ { 0 } ( { \cal S } ) } { { \cal N } _ { \mathrm { a } } ( { \cal S } ) - { \cal N } _ { 0 } ( { \cal S } ) } \biggr ] ^ { b ( { \cal S } ) } \exp \Bigl \{ - \biggl [ \frac { { \cal N } ^ { * } - { \cal N } _ { 0 } ( { \cal S } ) } { { \cal N } _ { a } ( { \cal S } ) - { \cal N } _ { 0 } ( { \cal S } ) } \biggr ] ^ { b ( { \cal S } ) } \Bigr \} .
$$

$$
\bigg \{ - b ( S ) \left[ \frac { N _ { 0 } ^ { \prime } ( S ) } { N ^ { * } - N _ { 0 } ( S ) } + \frac { N _ { a } ^ { \prime } - N _ { 0 } ^ { \prime } { } ^ { \prime } ( S ) } { N _ { a } ( S ) - N _ { 0 } ( S ) } \right] + b ^ { \prime } ( S ) \ln \frac { N ^ { * } - N _ { 0 } ( S ) } { N _ { a } ( S ) - N _ { 0 } ( S ) } \bigg \}
$$

式中： $N _ { 0 } ( S )$ , $N _ { \mathrm { a } } ( S )$ , $b ( S )$ — 在应力水平 $S$ 下的最小寿命、特征寿命和威布尔形状参数，可根据各个指定应平下的疲劳寿命试验数据得到；

N(S), $N _ { \mathrm { a } } ^ { \prime } ( S )$ ,b'(S) $\mathbf { \nabla } \cdot N _ { 0 } ( S )$ , $N _ { \mathrm { a } } ( S )$ , $b ( S )$ 的阶导数。

此外， $\mu ( S )$ 和 $\sigma ( S )$ 除了可以利用疲劳试验数据通过曲线拟合求得，也可以通过$P - S - N$ 曲线求得，即

$$
\mu ( S ) \ = \log N _ { 5 0 } ( S )
$$

$$
\sigma ( S ) = \frac { 1 } { u _ { P _ { 2 } } } [ \mathrm { l g } { \cal N } _ { P _ { 2 } } ( S ) - \mathrm { l g } { \cal N } _ { 5 0 } ( S ) ]
$$

$\textcircled{2}$ 疲劳强度理论的双重积分法

双重积分法根据结构关键部位的应分布和材料的 $P - S - N$ 曲线，直接计算不同寿命下结构的可靠度。其累积失效概率计算式为

$$
P ( N \leqslant N ^ { * } ) = P \ d ( N \leqslant N ^ { * } | - \infty < N _ { 5 0 } < \infty ) =
$$

$$
P ( \underset { \sim } { A } | U ) \ = P ( \underset { \sim } { A } ) \ = \int _ { - \infty } ^ { + \infty } c ( N ^ { * } , S ) f ( S ) \mathrm { d } S
$$

结构在给定寿命 $N ^ { * }$ 时的可靠度为

$$
R ( N ^ { * } ) ~ = ~ 1 ~ - { \cal P } ( N \leqslant N ^ { * } )
$$

例如，在某结构中， $F$ 为正态分布 $\Nu ( \mu _ { s } , \sigma _ { s } )$ , $G$ 为对数正态分布，则该结构在给定寿命 $N ^ { * }$ 时的结构可靠度为（其中， $\mu _ { \mathrm { v } } = h ( S ) , \sigma _ { \mathrm { v } } = u ( S )$ )

$$
\begin{array}{c} \begin{array} { r l } { R \big ( N ^ { * } \big ) } & { = 1 - P \big ( N { \leqslant } N ^ { * } \big ) } \end{array} = 1 - \int _ { - \infty } ^ { + \infty } c \big ( N ^ { * } \big , \ S \big ) \ f ( S ) \mathrm { d } S =  \end{array}
$$

$$
1 - \int _ { - \infty } ^ { + \infty } \left[ \frac { 1 } { \bar { u } \left( S \right) \sqrt { 2 \pi } } \int _ { - \infty } ^ { \mathrm { l g } N ^ { \ast } } \mathrm { e } ^ { - \frac { \left( \bar { t } - \bar { h } \left( S \right) \right) ^ { 2 } } { 2 u ^ { 2 } \left( S \right) } } \mathrm { d } t \right] \left[ \frac { 1 } { \sigma _ { S } \sqrt { 2 \pi } } \mathrm { e } ^ { \frac { - \left( S - \mu _ { S } \right) ^ { 2 } } { 2 \sigma _ { S } } } \right] \mathrm { d } S
$$

（2）结构可靠性分析中数值抽样算法的程序实现

由于式（7-20）是一个双重积分，有时并不能得到其解析积分解。下面给出一种数值抽样方法，用以求得该式的近似值。

$\textcircled{1}$ 当应力分布已知时，直接按应力的分布抽取 $_ n$ 个应力样本 $\{ S _ { \parallel }$ , $S _ { 2 }$ ,…, $S _ { n } \}$ ，应力分布类型可以为已知的各种分布类型，如正态分布、威布尔分布等；当应力分布未知时，如只知道载荷和材料参数分布，可由结构概率响应的计算方法（如有限元法等），将随机变量输进计算并求得构件的应力样本，此时不需要再去关心应力样本的分布。

$\textcircled{2}$ 由应值 $\{ S _ { 1 }$ , $S _ { 2 }$ , $\cdots$ , $S _ { n } \}$ ，根据应与寿命均值的关系 $\mu _ { N } | _ { S _ { i } } = h ( S _ { i } )$ 得到相应的寿命均值 $\{ \mu _ { 1 }$ , $\mu _ { 2 } , \cdots$ , $\textstyle \mu _ { n } \}$ ，根据 $P - S - N$ 曲线得到寿命标准差 $\{ \sigma _ { 1 }$ , $\sigma _ { 2 }$ , $\cdots$ , $\textstyle \sigma _ { n } \left\{ \begin{array} { r l r l } \end{array} \right.$ ，从而得到以这些均值及相应标准差为参数的对数正态概率密度函数 $\{ G _ { 1 } , G _ { 2 }$ , $\cdots$ , $\textstyle G _ { n } \left. \right\}$ ，即 $\{ g ( \mu _ { 1 } , \sigma _ { 1 } )$ ,$g ( \mu _ { 2 } , \sigma _ { 2 } )$ ,…, ${  { g } } ( \mu _ { n } , \sigma _ { n } )$ }。通常，获得的材料 $S - N$ 曲线的试验数据有限，也就只能得到有限的几个温度下的 $S - N$ 关系，而结构所处的温度是变化的，当温度与试验温度不同时，就要通过对试验曲线进行插值的办法，来得到实际温度下的 $S - N$ 值。应力一对数寿命标准差的关系也类似。

$\textcircled{3}$ 在每个寿命分布函数中抽取个样本$\{ \stackrel { \sim } { N } _ { 1 }$ , $\tilde { N } _ { 2 }$ ,…, $\smash { \widetilde { N } } _ { n } \bigr \}$

$\textcircled{4}$ 可靠度 $R ^ { * }$ 即为寿命样本中于给定寿命$N ^ { * }$ 的比例。

经过上述抽样计算所得的R为式（7-19)所求可靠度的个近似值，且随着样本数 $N$ 的增加， $R ^ { * }$ 将趋近于该式的真实解，具体的程序实现流程如图7–12所。

![](images/cfda66094c5dfc5ce0630da0e8ddff75df5f027c5ce08f8dd1cf8d141ae7f762.jpg)  
图7-12 数值抽样计算结构可靠度的流程

（3）结构可靠性分析中响应面法的程序实现

对于复杂结构，常不能给出结构功能函数的显式表达式，甚即使给出了表达式，也难于求得重积分的解析解，因而发展并应用响应面法。根据响应函数的不同，常响应面法可分为如下几类[16]

$\textcircled{1}$ 基于次多项式的响应法

该法采有限的试验通过回归拟合解析表达式来代替真实响应。对 $n$ 个随机变量的情况，通常采用不含交叉项的二次多项式

$$
Z = G ( X ) = a + \sum _ { i = 1 } ^ { n } b _ { i } x _ { i } + \sum _ { i = 1 } ^ { n } c _ { i } x _ { i } ^ { 2 }
$$

式中： $a$ , $b _ { i }$ , $c _ { i }$ (id:) 选定表达式的系数。

基于二次多项式的响应面法的优点有：方法简便，且具有必要的工程精度与较高的效率；计算中可考虑基本变量之间的相关性和基本变量的不同概率分布类型，具有较强的实性。由于这些特点，现在的响应法一般多采取多项式做响应，而且多项式的阶数通常为阶（firstorder，FOR）和阶（secondorder，SOR），一般并不推荐采更高阶的多项式。

$\textcircled{2}$ 基于平因的响应法

在响应面法中，作为二级（二水平）因子设计的示例，考虑3个独立变量，用A，B，C和Y分别表示因和响应，其函数的精确拟合为[17,18]

基于平因的响应面法的优点在于可以较好地模拟结构的实际受，可以计算非线性及参数变异较大的问题。但该方法在进可靠性分析时，假设基本随机变量是统计独的，没有考虑相关性对可靠度的影响。

$\textcircled{3}$ 基于有理多项式的响应法

可靠度计算中的关键是计算 ，基于有理多项式的响应法就是通过个函数连分式来近似得到上述偏导数的值，该方法须与JC（次二阶矩）法等结合起来，通过迭代调整精度。

基于有理多项式的响应面法不仅有基于多项式响应的特点，而且该法还可以避免采用响应面中求解待定系数的过程，计算效率更高。

$\textcircled{4}$ 基于神经络模型的响应法

基于径向基神经网络模型的响应面法对线性较强、样本数有限的响应面具有较好的模拟能力，现对其程序实现流程进阐述。

a.多样本径向基神经络响应法

多样本径向基神经络响应法（multi-sample radial basis function method，MS-RBF），其主要思想是设计合适的初始样本位置和数量，利用有限元法等计算得到样本的功能函数值，再利用径向基神经网络建立结构功能函数的响应面，最后在响应面上进规模蒙特卡罗数值抽样求得结构可靠度。其基本算法流程如图7-13所示，图中 $X$ 的产可以有如下两种法：直接蒙特卡罗法和超拉丁抽样法[19]。

![](images/f41abe72c2071ed4f569cefbaea0298af0210024751b5a9d655fb7a4a5701574.jpg)  
图7-13 多样本径向基神经络响应法计算流程

b.逐步逼近响应面法

如图7-14所，精度响应的的是为了尽量准确地刻画样本在空间的分布规律。然而从另个度看，在结构可靠度计算中，响应面最重要的功能是区分样本是处于“安全”区还是“失效”区，对结果起决定性作的是响应中的失效界（简称失效面）。然而除了少数特殊情况外，失效界并不容易模拟，通常的样本般都位于$Z > 0$ 或 $Z < 0$ 的位置上，正好位于失效上的样本几乎为0。为此，需要建种将有效样本逼近失效区的算法，让样本尽量贴近失效面。

![](images/bddbcb41a746c8f0028f545d5fe3acadc9b52414651b23a50a5535cb7b71f0e5.jpg)  
图7-14 样本点的位置

逐步逼近径向基神经网络响应法正是基于上述思想，在该法的计算过程中，采用迭代寻优的方法，试图将有限的样本尽量散布在离失效面最近的位置，从而最大限度地模拟失效面，达到提可靠度计算精度的的。该法主要计算流程如图7-15所示。

![](images/a627a362909938c985f123183f71a61894127a905d1b192376365e21cddfc049.jpg)  
图7-15 逐步逼近径向基神经络响应面法计算流程

$\textcircled{5}$ 基于逐步逼近加权响应法

加权响应面法的思想是对越靠近真实失效线的样本点赋予越高的权重，即样本点对构建响应的贡献越。如图7–16所示样本点对构造响应面的权重关系为： $w ( 1 ) >$ $w ( 2 ) > w ( 3 )$ ，响应面函数可以采用一次多项式或者不含交叉项的二次多项式，当使用一般最小二乘法求系数矩阵时，求解公式为

$$
\pmb { b } \ = \ ( \pmb { X } ^ { \mathrm { T } } \pmb { X } ) ^ { - 1 } \pmb { X } ^ { \mathrm { T } } \mathbf { y }
$$

当使用加权最小乘法求系数矩阵时，求解公式为

$$
b \ = \ ( \ X ^ { \mathrm { { T } } } W X ) ^ { \ - 1 } X ^ { \mathrm { { T } } } W y
$$

式中：W 权矩阵，它是个对矩阵；

Wi 每个样本点在构造响应面时的权重，当 $w _ { i i }$ 都取1时，加权最乘法退化为普通最小二乘法。

为了保证样本点的权值不会出现太小的情况，以致对构造的响应面不起作用，有时甚至出现病态矩阵，使系数矩阵无法求解，设计权函数为

$$
\begin{array} { r } { \left\{ w _ { i i } = \mathrm { e } ^ { - m _ { i } } , t _ { i } = \frac { \displaystyle | y _ { i } | } { \displaystyle \sum _ { i = 1 } ^ { n } | y _ { i } | } , \quad \sum _ { i = 1 } ^ { n } | y _ { i } | \ne 0 \right. } \\ { \left\{ w _ { i i } = 1 , \qquad \quad \sum _ { i = 1 } ^ { n } | y _ { i } | = 0 \right. } \end{array}
$$

式中： $m$ 常数，影响权值最值以及权值随样本点离失效线距离增衰减幅度。

![](images/4818df6a63445ff283c1f5ca6dcf2fe0a2dd2239c1dbf0714150b75209a1537b.jpg)  
图7-16 样本点布置

为了使构造的响应面能更好地逼近真实失效面，采用逐步逼近加权响应面法，在逐步逼近过程中，样本点的布置方法严重影响响应面的逼近效果以及迭代步数，所以在逐步逼近加权响应面法中采用平移及旋转的方法来布置样本点，样本布置方法如图7-17所示，样本点坐标为 $P _ { \mathrm { 1 } } ( 0 , 0 )$ , $P _ { 2 } \left( f \sigma _ { 1 } , 0 \right)$ , $P _ { 3 } ( 0 , f \sigma _ { 2 } )$ , $P _ { 4 } \left( - f \sigma _ { 1 } , 0 \right)$ , $P _ { 5 } ( 0 , - f \sigma _ { 2 } )$ 。

![](images/88898d50839a13ca91d680f1eec7710e2e21405cd4b832d5bf0f59dc154e296c.jpg)  
图7-17 逐步逼近加权响应面法样本点布置法

$f$ 是控制样本点布置尺度，这第步 $f$ 取3，第二步 $f$ 取1，平移旋转过后样本点坐标为

$$
{ \left[ \begin{array} { l } { Q _ { 1 } } \\ { Q _ { 2 } } \\ { Q _ { 3 } } \\ { Q _ { 4 } } \\ { Q _ { 5 } } \end{array} \right] } = { \left[ \begin{array} { l l l } { 0 } & { 0 } & { 1 } \\ { \sigma _ { 1 } } & { 0 } & { 1 } \\ { 0 } & { \sigma _ { 2 } } & { 1 } \\ { - \sigma _ { 1 } } & { 0 } & { 1 } \\ { - \sigma _ { 2 } } & { 0 } & { 1 } \end{array} \right] } { \left[ \begin{array} { l l l } { { \sin \theta } } & { { \cos \theta } } & { 0 } \\ { - { \cos \theta } } & { { \sin \theta } } & { 0 } \\ { l } & { m } & { 1 } \end{array} \right] }
$$

式中：l， $m$ (id:) 沿平、垂直坐标轴的平移量；

$Q _ { r }$ 响应到样本中最短距离的点，它作为新的样本中。逐步逼近加权响应法主要计算流程如图7-18所。

![](images/82f31d0e3dcb848d541b745b1904c42fbda039a0e56cd480dd3c25c112071da9.jpg)  
图7-18 逐步逼近加权响应法计算流程

# 7.2.4 涡轮盘结构应力疲劳可靠性分析

现以一典型涡轮盘结构为例，通过局部应一寿命关系，考察盘身（不含榫连结构）在随机因素作用下的结构可靠性。

（1）涡轮盘失效模式分析

涡轮盘的外径 $4 0 0 \mathrm { m m }$ 、内径 $1 6 0 \mathrm { m m }$ ，有限元模型如图7-19所。涡轮盘受离载荷和瞬态温度场作用，其中最高温度时刻的温度场如图7-20所示，按脉动循环对轮盘进行循环加载计算。根据确定性计算结果，涡轮盘的周向应力较大，如图7-21所示，并可选出涡轮盘中最容易发生疲劳破坏的危险位置 $P$ 。 $P$ 点位于涡轮盘内径孔边，受恒幅疲劳载荷作用，其在循环载荷下的周向应应变曲线如图7-22所。根据以上结果，认为涡轮盘塑性应变范围不大，应力疲劳成为涡轮盘失效的主要模式，可以采用应—寿命关系（ $S - N$ 曲线）分析涡轮盘的疲劳寿命。同时，在这种条件下，忽略了涡轮盘蠕变效应。

![](images/d3b631b2031dd8e051a9bcb9ceb86847bace7876e79f32685695d0378dd07675.jpg)  
图7-19 涡轮盘轴对称有限元模型

![](images/c8f2f66761c49ab7d5d91f4a6c798b0b013d3eb5c3607290f233caf1bf474af3.jpg)  
图7-20 涡轮盘温度场（最温度状态)

![](images/c8a6437fb2a5eff499936544c8674ff807fb552aff27221ba625d92db89396b5.jpg)  
  
图7-21 涡轮盘周向应

![](images/ebd0ecd0f025679d6a21a7e79338dea5ad60af7e19c240d62af41ca8f030452e.jpg)  
图7-22 $P$ 点应力一应变曲线

(2）涡轮盘随机变量的处理

$\textcircled{1}$ 材料强度

采用疲劳强度理论与双重积分法及其数值抽样技术处理材料强度的随机变化。

$\textcircled{2}$ 结构尺寸

对涡轮盘结构可靠性产较为明显影响的随机尺寸般只存在于涡轮盘外表面中曲率较大的倒角和孔边。 $P$ 点正好处于涡轮盘的内径处，故取涡轮盘内径作为尺寸随机量，设其服从正态分布，均值为160，变异系数为0.02。

$\textcircled{3}$ 表完整性

涡轮整个外表面，由于加、热处理和受力情况等因素都存在差异，所以其表面完整性也不完全相同，但这出于简化计算以及计算数据有限的考虑，认为涡轮盘外表面加工系数 $\beta$ 服从正态分布，均值为0.95，变异系数为0.02。

$\textcircled{4}$ 转速

设转转速服从正态分布，均值 $1 2 0 0 0 \mathrm { r / m i n }$ ，变异系数为0.03。

$\textcircled{5}$ 温度场

涡轮盘的材料选用GH4169，该材料具有良好的高温疲劳性能，且高温下其疲劳性能要优于常温下的疲劳性能，产生这种结果的原因是在高温时由于残余应力作用该材料发应松弛，使其具有良好的持久塑性[3]。另外GH4169材料的疲劳性能对温度较敏感，这就要求对涡轮盘的温度场计算应准确，而在涡轮盘的疲劳寿命计算中也应该尽量准确地使用真实的温度数据。

针对涡轮前温度 $T _ { 4 } ^ { * }$ ，可以通过传热分析确定涡轮盘温度场的随机性。鉴于传热分析的复杂性，这里假设涡轮盘温度场随机性的表征方式为温度场极值采用相同的随机量进偏置，且随机量服从正态分布，变异系数均为0.02。

$\textcircled{6}$ 弹性模量和泊松

设材料的弹性模量和泊松均服从正态分布，前者变异系数为0.03，后者为0.02。

(3）简单情况下涡轮盘结构可靠度分析

先假设涡轮盘的随机变量只有两个，即转速和强度为随机变量，且涡轮盘材料处于线弹性范围，在转速随机的作用下，涡轮盘中每个节点的应值 $S _ { 1 }$ 均服从正态分布，其变异系数为0.03。下将以涡轮盘中的应极值点 $P$ 为例，分别采用疲劳强度理论、双重积分法，以及双重积分法结合数值抽样技术计算涡轮盘结构可靠度。

$\textcircled{1}$ 基于疲劳强度理论的计算

由于 $P$ 点的应分布已知，因而这里采用应强度涉模型的关键在于求得材料的疲劳强度分布。按照材料数据册[20]，先对材料 $5 0 0 \%$ 的 $S - N$ 曲线进拟合，如图7-23所示，可以得到

$$
\hat { \mu } ( S ) ~ = ~ a _ { 5 0 0 } + b _ { 5 0 0 } S ~ = ~ 1 2 . 0 8 7 - 0 . 0 0 6 2 8 S
$$

![](images/2b00165f5c500396bef238622fc548d692e920b382d0527d57d2692a62259827.jpg)  
图7-23 $5 0 0 \mathrm { { q } } \mathrm { { c } }$ 时材料寿命均值线性拟合

又由式（7-17），根据 $5 0 0 \%$ 时材料的 $P - S - N$ 曲线求得材料在不同应力下的寿命标准差样本，并进拟合，如图7-24所，可以得到

$$
\hat { \sigma } ( S ) \ = c _ { 5 0 0 } + d _ { 5 0 0 } S \ = - 0 . 1 1 5 2 3 + 0 . 0 0 0 7 2 8 S
$$

将式（7-27）和式（7-28）代式（7-14），即可得到疲劳强度分布函数，由该式和应概率密度函数即可求得应强度涉曲线，如图7-25所，最后由式（7-29)即可求得涉模型的可靠度，如图7-26所

$$
R ( N ) \ = \int _ { { \cal S } _ { \mathrm { m i n } } } ^ { { \cal S } _ { \mathrm { m a x } } } f ( { \cal S } _ { s } ) \Big [ \int _ { { \cal S } _ { s } } ^ { + \infty } g ( { \cal S } _ { \tau } ) \mathrm { d } { \cal S } _ { \tau } \Big ] \mathrm { d } { \cal S } _ { s } \ .
$$

![](images/aee8691e790a1673df9a841b3298a39b72deb303f97b854e0083b9ba27a432bc.jpg)  
图7-24 $5 0 0 \%$ 时材料寿命标准差线性拟合

![](images/d300ff5f03e8e64af3e3d92acd35d886ead2985d3e9443ae7046ea9da9a2ff0e.jpg)  
图7-25 不同寿命下 $P$ 点应力—强度干涉曲线

$\textcircled{2}$ 基于双重积分法的计算

上述计算中对材料 $S - N$ 曲线的处理采用了线性拟合代替真实曲线的法，会造成定的数值误差。下将利双重积分法，并采材料的真实试验曲线进计算。

先由材料数据册[20]可知材料 $S - N$ 曲线的拟合方程为

$$
\sigma _ { \operatorname* { m a x } } ~ = ~ 1 0 ^ { \left( { \frac { a - \log N } { b } } \right) } + c
$$

![](images/fe66e3d3629111c9ec1d9960baf66c367f2fe53dc68bc189ab32f06fec2f78ef.jpg)  
图7-26 $P$ 点结构可靠度随寿命的变化

表7-2为对材料数据册中的数据进处理后得到的不同温度下的 $a$ , $b$ , $c$ 值。 $P$ 点的温度为 $4 0 0 \%$ ，从而由式（7-16）、式（7-17）和式（7-30）可得

$$
h _ { 4 0 0 } \left( S \right) ~ = ~ a _ { 4 0 0 , 1 } ~ - ~ b _ { 4 0 0 , 1 } \mathrm { l g } ( S - c _ { 4 0 0 , 1 } )
$$

$$
\begin{array} { r } { \boldsymbol { u } _ { 4 0 0 } ( S ) \ = \ \frac { 1 } { 3 } \big \{ \big [ \ : a _ { 4 0 0 , 2 } \ : - b _ { 4 0 0 , 2 } \mathrm { l g } ( S - c _ { 4 0 0 , 2 } ) \big ] \ : = \ : \big [ a _ { 4 0 0 , 1 } \cdot b _ { 4 0 0 , 1 } \mathrm { l g } ( S - c _ { 4 0 0 , 1 } ) \big ] \big \} } \end{array}
$$

将应概率密度函数、式（7-31）和式（7-32）代式（7-20）即可求得 $P$ 点的结构可靠度，如图7–27所。

表7-2 材料的 $P - S - N$ 曲线拟合系数  

<table><tr><td rowspan=1 colspan=1>温度/℃</td><td rowspan=1 colspan=1>存活率</td><td rowspan=1 colspan=1>a</td><td rowspan=1 colspan=1>b</td><td rowspan=1 colspan=1>c</td></tr><tr><td rowspan=2 colspan=1>400</td><td rowspan=1 colspan=1>P50</td><td rowspan=1 colspan=1>400,1=29.65022</td><td rowspan=1 colspan=1>6400.1=8.24525</td><td rowspan=1 colspan=1>C400.1=84.64664</td></tr><tr><td rowspan=1 colspan=1>P99.8</td><td rowspan=1 colspan=1>0400,2=30.60368</td><td rowspan=1 colspan=1>b400.2=8.91049</td><td rowspan=1 colspan=1>400.2=0.51770</td></tr><tr><td rowspan=2 colspan=1>500</td><td rowspan=1 colspan=1>Ps0</td><td rowspan=1 colspan=1>0500.1=38.88573</td><td rowspan=1 colspan=1>b500,1=11.17506</td><td rowspan=1 colspan=1>C500,1=92.31386</td></tr><tr><td rowspan=1 colspan=1>Po9.87</td><td rowspan=1 colspan=1>0500,2=39.89479.</td><td rowspan=1 colspan=1>6500.2=12.40318</td><td rowspan=1 colspan=1>C500.2 =221.21471</td></tr><tr><td rowspan=2 colspan=1>650</td><td rowspan=1 colspan=1>P50</td><td rowspan=1 colspan=1>a650.1 =66.11.039</td><td rowspan=1 colspan=1>6650.1 = 19.86362</td><td rowspan=1 colspan=1>C650,1 =-113.41567</td></tr><tr><td rowspan=1 colspan=1>P99.87</td><td rowspan=1 colspan=1>0650,2=65.54969</td><td rowspan=1 colspan=1>6650,2=20.1215</td><td rowspan=1 colspan=1>C650,2=-284.44007</td></tr></table>

$\textcircled{3}$ 双重积分结合数值抽样的计算

按照双重积分数值抽样技术的计算流程，随着抽样的样本数 $n$ 增加，可靠度结果将收敛到精确值，如图7–28所，与解析解的对比如图7–29所。

![](images/6e216fc9d9b0cfc7fbe1c3180db8dfed0a39720624ae9df5c601f7043381022f.jpg)  
图7-27 $P$ 点的结构可靠度

![](images/abbacafec4b4a3f638bcee560d05a2d35585232a20bd10cdd843cace8f29f0a1.jpg)  
图7-28 $P$ 点可靠度随样本数增加而收敛

$\textcircled{4}$ 计算结果的对分析

表7-3给出前述结果的对比，由表中可以看出，基于疲劳强度理论、双重积分法和双重积分结合数值抽样技术，均可以对涡轮盘进行结构可靠度计算，计算结果具有一致性，其中利用疲劳强度理论进行计算时，由于对温度曲线进行了线性拟合，与其他两种方法的结果稍有差别；而双重积分结合数值抽样技术与双重积分法的结果符合很好。

![](images/44cd19047db360f434610e737b53d12ace1faf49979cf695feb8d06ed26465d1.jpg)  
图7-29 积分法与解析法结果的致性

表7-3 $P$ 点可靠度计算结果的对比  

<table><tr><td rowspan=2 colspan=1>方法</td><td rowspan=1 colspan=4>寿命</td></tr><tr><td rowspan=1 colspan=1>104</td><td rowspan=1 colspan=1>105</td><td rowspan=1 colspan=1>$10{$</td><td rowspan=1 colspan=1>$10{$</td></tr><tr><td rowspan=1 colspan=1>①</td><td rowspan=1 colspan=1>0.9933</td><td rowspan=1 colspan=1>0.6248</td><td rowspan=1 colspan=1>0.0343</td><td rowspan=1 colspan=1>0.0000</td></tr><tr><td rowspan=1 colspan=1>②</td><td rowspan=1 colspan=1>0.9922</td><td rowspan=1 colspan=1>0.6087</td><td rowspan=1 colspan=1>0.0312</td><td rowspan=1 colspan=1>0.0000</td></tr><tr><td rowspan=1 colspan=1>③</td><td rowspan=1 colspan=1>0.9922</td><td rowspan=1 colspan=1>0.6066</td><td rowspan=1 colspan=1>0.0327</td><td rowspan=1 colspan=1>0.0000</td></tr></table>

$\textcircled{5}$ 整个轮盘结构的可靠度计算

以上计算为以 $P$ 点为例的计算结果。由于此例较为简单，而且双重积分法具有非常的计算速度，所以这可以实现对整个轮盘结构的可靠度计算。图7-30所示为计算得到的涡轮盘在 $1 0 ^ { 5 }$ 次循环寿命时的可靠度分布，由该图可以常直观地了解整个涡轮盘的可靠度分布情况。

（4）复杂情况下涡轮盘结构可靠度分析

以下分析中，将采用多样本径向基神经络响应面法和逐步逼近径向基神经络响应面法分别计算涡轮盘的结构可靠度，其中考虑了材料强度、结构尺寸、表面完整性、转速、温度场、弹性模量和泊松比等的随机性。

$\textcircled{1}$ 多样本径向基神经络响应法

按照超拉丁抽样法成初始样本，样本数为30个。根据计算，可得到 $1 0 ^ { 5 }$ 循环寿命时涡轮盘 $P$ 点的可靠度为0.4782。

$\textcircled{2}$ 逐步逼近径向基神经络响应法

考虑上述7个随机变量时，采平因法产的单次计算样本数为15个。在给定精度 $\Delta R = 0 . 0 0 1$ 下，迭代共进了4步，结果见表7–4与图7–31。

![](images/25d9e60abcd2a1525c17f136fc54645a8b41896d8cfe0f79077537a1f9e03749.jpg)  
图7-30 $1 0 ^ { 5 }$ 次循环寿命时涡轮盘可靠度分布

表7-4迭代计算 $1 0 ^ { 5 }$ 循环寿命时涡轮盘 $P$ 点可靠度  

<table><tr><td rowspan=1 colspan=1>迭代步</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>4</td><td rowspan=1 colspan=1>5</td><td rowspan=1 colspan=1>6</td></tr><tr><td rowspan=1 colspan=1>可靠度</td><td rowspan=1 colspan=1>0.4757</td><td rowspan=1 colspan=1>0.4397</td><td rowspan=1 colspan=1>0.5427</td><td rowspan=1 colspan=1>0.4651</td><td rowspan=1 colspan=1>0.4661</td><td rowspan=1 colspan=1>0.4668</td></tr></table>

![](images/e3e2175ff4d338e4a1286379eecc5b5e1842dc8672c5b105f0813f5a0289aaff.jpg)  
图7-31 $1 0 ^ { 5 }$ 循环寿命时涡轮盘 $P$ 点可靠度

$\textcircled{3}$ 涡轮盘随机变量敏感性分析

随机变量的敏感度见图7-32和表7-5。敏感性分析不仅可以识别随机量重要性的差异，从而选择加以重视或可以忽略；同时，也可以对结构设计、加工和使用给予一定的指导。

![](images/01ee2a0a3073f50a35fce3e74e76d89072cb81597a0f9787ebf691de15d939b9.jpg)  
图7–32 随机变量的敏感度

表7-5 涡轮盘结构随机变量的敏感性分析  

<table><tr><td rowspan=1 colspan=1>随机变量</td><td rowspan=1 colspan=1>敏感度</td><td rowspan=1 colspan=1>提高可靠性措施</td><td rowspan=1 colspan=1>说明</td></tr><tr><td rowspan=1 colspan=1>转速</td><td rowspan=1 colspan=1>-0.153</td><td rowspan=1 colspan=1>适当降低</td><td rowspan=1 colspan=1>①转速降低，减小涡轮盘离心载荷和应力；②效果较好，但需要结合性能综合考虑</td></tr><tr><td rowspan=1 colspan=1>材料强度</td><td rowspan=1 colspan=1>0.685</td><td rowspan=1 colspan=1>增加</td><td rowspan=1 colspan=1>①疲劳强度增加，增加涡轮盘寿命；②最为有效的途径，但受限于材料研制平</td></tr><tr><td rowspan=1 colspan=1>温度</td><td rowspan=1 colspan=1>0.022</td><td rowspan=1 colspan=1>适当提高</td><td rowspan=1 colspan=1>①材料在500℃时比周围温度的疲劳强度要高，而P₂点温度为400℃；②效果较小，设计时可以放宽对其影响的考虑</td></tr><tr><td rowspan=1 colspan=1>尺寸</td><td rowspan=1 colspan=1>-0.004</td><td rowspan=1 colspan=1>适当减小内径</td><td rowspan=1 colspan=1>①内径减小，孔边应力降低；②效果甚微，设计时可以不考虑其影响</td></tr><tr><td rowspan=1 colspan=1>弹性模量</td><td rowspan=1 colspan=1>-0.003</td><td rowspan=1 colspan=1>适当降低</td><td rowspan=1 colspan=1>效果甚微，设计时可以不考虑其影响</td></tr><tr><td rowspan=1 colspan=1>泊松比</td><td rowspan=1 colspan=1>-0.003</td><td rowspan=1 colspan=1>适当降低</td><td rowspan=1 colspan=1>效果甚微，设计时可以不考虑其影响</td></tr><tr><td rowspan=1 colspan=1>表面完整性</td><td rowspan=1 colspan=1>0.130</td><td rowspan=1 colspan=1>适当增加</td><td rowspan=1 colspan=1>①表面完整性提，可以降低表面应力的集中；②效果较好，在加工条件允许的情况下，可以考虑提高孔壁的表面完整性</td></tr></table>

# 7.2.5 涡轮盘结构疲劳可靠性分析

涡轮盘作为航空发动机重要的热端结构，在实际作过程中需要承受温和机械载荷，其低循环疲劳特征明显，对涡轮盘低循环疲劳可靠性进分析有着重要的意义。

（1）涡轮盘低循环疲劳寿命预测模型

低循环疲劳寿命模型是涡轮盘低循环疲劳可靠性分析的基础。由于实际涡轮盘剖较为复杂，还可能存在冷却孔或连接孔等开孔部位，从使构件局部区域产应集

中，并有较高的应力梯度，这种应力梯度往往会促进涡轮盘的局部萌生裂纹，并进一步发展导致疲劳破坏。因此，应该选种能够考虑应梯度影响的疲劳寿命模型作为涡轮盘疲劳可靠性分析的基础。这种寿命模型可选为[21]

$$
\varepsilon _ { \mathrm { a } } = Y ^ { m } \Big \{ \frac { \sigma _ { \mathrm { f } } ^ { \prime } } { E } \Big [ 2 N _ { \mathrm { f } } \Big ( \frac { 1 - R ^ { \prime } } { 2 } \Big ) ^ { \frac { 1 - \gamma } { b } } \Big ] ^ { b } + \varepsilon _ { \mathrm { f } } ^ { \prime } \Big [ 2 N _ { \mathrm { f } } \Big ( \frac { 1 - R ^ { \prime } } { 2 } \Big ) ^ { \frac { 1 - \gamma } { b } } \Big ] ^ { c } \Big \}
$$

式中： $\varepsilon _ { \mathrm { a } }$ (id:) -应变幅；

Y- 应力梯度影响因子；   
$m$ (d 应力梯度影响指数；   
(id $\sigma _ { f } ^ { \prime } -$ (id:) 疲劳强度系数；   
$E$ 弹性模量；   
$N _ { f }$ (id) 疲劳寿命；   
$R ^ { \prime }$ bid:) 局部应力比；   
$\gamma$ (id 材料常数；   
$b$ 疲劳强度指数；   
$ { \varepsilon } _ { \mathrm { f } } ^ { \prime }$ (i:) 疲劳延性系数；   
$c$ 疲劳延性指数。

其中应梯度影响因 $Y$ 和应力梯度影响指数 $m$ 定义为

$$
Y = \frac { 1 } { 2 S _ { 0 . 5 } }
$$

$$
m \ = A \ ( 2 N _ { t } ) ^ { B }
$$

这里的 $S _ { 0 . 5 }$ 为缺处应归化曲线与坐标轴在 $0 \leqslant x / r \leqslant 0 . 5$ 区间上围成的面积，A和 $B$ 为常数，可通过试验数据拟合得到。

为了使式（7-33）中的疲劳强度系数 $\sigma _ { \mathrm { ~ f ~ } } ^ { \prime }$ 和疲劳延性系数 $\varepsilon _ { \mathrm { f } } ^ { \prime }$ 具有明确的物理意义，采参考献[22中给出的次单调拉伸时断裂真实应 $\sigma _ { \mathrm { { f } } }$ ，断裂真实应变 $\varepsilon _ { \mathrm { f } }$ 与疲劳强度系数 $\sigma _ { \mathrm { ~ f ~ } } ^ { \prime }$ 和疲劳延性系数 $\varepsilon _ { f } ^ { \prime }$ 的关系，这些参数的关系为[22]

$$
\sigma _ { \mathrm { { f } } } = \sigma _ { \mathrm { { f } } } ^ { \prime } ( 0 . 5 ) ^ { b }
$$

$$
\varepsilon _ { \mathrm { f } } = \varepsilon _ { \mathrm { f } } ^ { \prime } ( 0 . 5 ) ^ { \circ }
$$

$$
\sigma _ { \mathrm { { f } } } = { \frac { P } { A _ { \mathrm { { f } } } } }
$$

$$
\varepsilon _ { \mathrm { f } } ~ = ~ \ln ( { A _ { 0 } } / { A _ { \mathrm { f } } } )
$$

$$
\psi = \frac { A _ { 0 } - A _ { \mathrm { f } } } { A _ { 0 } }
$$

$$
\sigma _ { \mathrm { f } } = { \frac { P } { A _ { \mathrm { f } } } } \approx { \frac { \sigma _ { \mathrm { b } } A _ { 0 } } { A _ { \mathrm { f } } } } = { \frac { \sigma _ { \mathrm { b } } } { 1 - \psi } }
$$

$$
\varepsilon _ { \mathrm { f } } = \ln ( A _ { 0 } / A _ { \mathrm { f } } ) = \ln \Bigl ( \frac { 1 } { 1 - \psi } \Bigr )
$$

$$
\sigma _ { \mathrm { f } } ^ { \prime } { \approx } \frac { \sigma _ { \mathrm { b } } } { \left( 1 - \psi \right) \left( 0 . 5 \right) ^ { b } }
$$

$$
\varepsilon _ { \mathrm { f } } ^ { \prime } = { \frac { - \ln ( 1 - \psi ) } { ( 0 . 5 ) ^ { c } } }
$$

式中： $P$ ——施加载荷；$A _ { 0 }$ (− -材料试样初始截面面积；$A _ { \mathrm { f } }$ 拉伸断裂时截面面积；$\sigma _ { \mathrm { ~ b ~ } }$ 拉伸强度极限；$\psi$ —断收缩率。

将式（7-43）和式（7-44）代式（7-33）得到最终寿命模型为

$$
\dot { \bar { \mathbf { \xi } } } _ { \mathrm { a } } = Y ^ { m } \bigg \{ \frac { \sigma _ { \mathrm { b } } } { E ( 1 - \psi ) \left( 0 . 5 \right) ^ { b } } \left[ 2 N _ { \mathrm { f } } \left( \frac { 1 - R ^ { \prime } } { 2 } \right) ^ { \frac { 1 - \gamma } { b } } \right] ^ { b } + \frac { - \ln ( 1 - \psi ) } { \left( 0 . 5 \right) ^ { c } } \left[ 2 N _ { \mathrm { f } } \left( \frac { 1 - R ^ { \prime } } { 2 } \right) ^ { \frac { 1 - \gamma } { b } } \right] ^ { c } \bigg \}
$$

为了验证寿命模型式（7-45）预测寿命的能，以GH901缺口圆棒 $5 0 0 \mathrm { { ^ \circ C } }$ 下疲劳寿命为例，使式（7-45）进寿命预测。参考献[23]给出GH901在 $5 0 0 \%$ 下的材料参数见表7-6，疲劳试验数据见表7-7。计算得出GH901在 $5 0 0 \mathrm { { ^ \circ C } }$ 下的光滑疲劳试件的应变范围见表7-8，再根据表7-8中的数据确定带有拉伸强度极限 $\sigma _ { \mathrm { { b } } }$ 和断面收缩率 $\psi$ 的Walker平均应修正寿命程中的参数，见表7–9。

表7-6GH901合金试件在 ${ 5 0 0 } \mathrm { \textbar { C } }$ 下的材料参数[23]  

<table><tr><td rowspan=1 colspan=1>E/GPa</td><td rowspan=1 colspan=1>$σ/MPa$</td><td rowspan=1 colspan=1>4</td><td rowspan=1 colspan=1>K/MPa</td><td rowspan=1 colspan=1>n&#x27;</td></tr><tr><td rowspan=1 colspan=1>170</td><td rowspan=1 colspan=1>1067</td><td rowspan=1 colspan=1>0.24</td><td rowspan=1 colspan=1>2220</td><td rowspan=1 colspan=1>0.15</td></tr></table>

表7-7GH901合金试件在 ${ 5 0 0 } \mathrm { \textbar { C } }$ 下的疲劳性能[23]  

<table><tr><td rowspan=3 colspan=1>Nr</td><td rowspan=1 colspan=4> mx/MPa</td></tr><tr><td rowspan=1 colspan=2>K₁=1$</td><td rowspan=1 colspan=2>K₁ =3$</td></tr><tr><td rowspan=1 colspan=1>R =0.1</td><td rowspan=1 colspan=1>R = -1.0</td><td rowspan=1 colspan=1>R =0.1</td><td rowspan=1 colspan=1>R = -1.0</td></tr><tr><td rowspan=1 colspan=1>5×10{3$</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>620</td><td rowspan=1 colspan=1>725</td><td rowspan=1 colspan=1>470</td></tr><tr><td rowspan=1 colspan=1>104</td><td rowspan=1 colspan=1>875</td><td rowspan=1 colspan=1>540</td><td rowspan=1 colspan=1>625</td><td rowspan=1 colspan=1>390</td></tr><tr><td rowspan=1 colspan=1>5×104</td><td rowspan=1 colspan=1>665</td><td rowspan=1 colspan=1>390</td><td rowspan=1 colspan=1>405</td><td rowspan=1 colspan=1>245</td></tr><tr><td rowspan=1 colspan=1>$10\$</td><td rowspan=1 colspan=1>581</td><td rowspan=1 colspan=1>350</td><td rowspan=1 colspan=1>330</td><td rowspan=1 colspan=1>200</td></tr></table>

表7-8 GH901合金试件在 $5 0 0 \mathrm { ‰}$ 下Neuber法计算的应变范围  

<table><tr><td rowspan=1 colspan=1>Nf</td><td rowspan=1 colspan=1>5×10^3</td><td rowspan=1 colspan=1>104</td><td rowspan=1 colspan=1>104</td><td rowspan=1 colspan=1>5×104</td><td rowspan=1 colspan=1>5×104</td><td rowspan=1 colspan=1>$10\$</td><td rowspan=1 colspan=1>10\$</td></tr><tr><td rowspan=1 colspan=1>R</td><td rowspan=1 colspan=1>-1.0</td><td rowspan=1 colspan=1>0.1</td><td rowspan=1 colspan=1>-1.0</td><td rowspan=1 colspan=1>0.1</td><td rowspan=1 colspan=1>-1.0</td><td rowspan=1 colspan=1>0.1</td><td rowspan=1 colspan=1>-1.0</td></tr><tr><td rowspan=1 colspan=1>σmax/MPa</td><td rowspan=1 colspan=1>620</td><td rowspan=1 colspan=1>875</td><td rowspan=1 colspan=1>540</td><td rowspan=1 colspan=1>665</td><td rowspan=1 colspan=1>390</td><td rowspan=1 colspan=1>581</td><td rowspan=1 colspan=1>350</td></tr><tr><td rowspan=1 colspan=1>∆1</td><td rowspan=1 colspan=1>0.0077</td><td rowspan=1 colspan=1>0.0047</td><td rowspan=1 colspan=1>0.0065</td><td rowspan=1 colspan=1>0.0035</td><td rowspan=1 colspan=1>0.0046</td><td rowspan=1 colspan=1>0.0031</td><td rowspan=1 colspan=1>0.0041</td></tr></table>

表7-9 Walker寿命方程中的参数  

<table><tr><td rowspan=1 colspan=1>0&#x27;/MPa</td><td rowspan=1 colspan=1>Y</td><td rowspan=1 colspan=1>b</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>c</td></tr><tr><td rowspan=1 colspan=1>1292</td><td rowspan=1 colspan=1>0.7678</td><td rowspan=1 colspan=1>-0.1199</td><td rowspan=1 colspan=1>0.1891</td><td rowspan=1 colspan=1>-0.5372</td></tr></table>

根据参考献[21]中的法计算得到应梯度影响因Y为1.321，利 $K _ { \mathrm { t } } = 3$ 且应力比 $R = - 1 . 0$ 的试验数据来获得应力梯度影响指数 $m$ 的表达式

$$
m ~ = ~ 3 0 . 1 ~ ( 2 N _ { \mathrm { f } } ) ^ { - 0 . 2 1 8 5 }
$$

使Neuber法计算得到缺圆棒试件在不同应比条件下的局部应/应变幅值，使用式（7-45）寿命程进寿命预测，预测结果见表7-10。由表可知，其结果基本在两倍分散带以内，表明该模型具有较好的疲劳寿命预测能力，可以作为疲劳可靠性分析的基础寿命预测模型。

表7-10缺口圆棒试件寿命预测结果  

<table><tr><td rowspan=1 colspan=1>R</td><td rowspan=1 colspan=1> max/MPa</td><td rowspan=1 colspan=1>N_[23]</td><td rowspan=1 colspan=1>a</td><td rowspan=1 colspan=1>N</td></tr><tr><td rowspan=4 colspan=1>-1.0</td><td rowspan=1 colspan=1>470</td><td rowspan=1 colspan=1>5000</td><td rowspan=1 colspan=1>0.0116</td><td rowspan=1 colspan=1>5202</td></tr><tr><td rowspan=1 colspan=1>390</td><td rowspan=1 colspan=1>10000</td><td rowspan=1 colspan=1>0.0086</td><td rowspan=1 colspan=1>9612</td></tr><tr><td rowspan=1 colspan=1>245</td><td rowspan=1 colspan=1>50000</td><td rowspan=1 colspan=1>0.0046</td><td rowspan=1 colspan=1>49271</td></tr><tr><td rowspan=1 colspan=1>200</td><td rowspan=1 colspan=1>100000</td><td rowspan=1 colspan=1>0.0036</td><td rowspan=1 colspan=1>102366</td></tr><tr><td rowspan=4 colspan=1>0.1</td><td rowspan=1 colspan=1>725</td><td rowspan=1 colspan=1>5000</td><td rowspan=1 colspan=1>0.0066</td><td rowspan=1 colspan=1>12264</td></tr><tr><td rowspan=1 colspan=1>625</td><td rowspan=1 colspan=1>10000</td><td rowspan=1 colspan=1>0.0054</td><td rowspan=1 colspan=1>19944</td></tr><tr><td rowspan=1 colspan=1>405</td><td rowspan=1 colspan=1>50000</td><td rowspan=1 colspan=1>0.0033</td><td rowspan=1 colspan=1>77514</td></tr><tr><td rowspan=1 colspan=1>330</td><td rowspan=1 colspan=1>100000</td><td rowspan=1 colspan=1>0.0026</td><td rowspan=1 colspan=1>151044</td></tr></table>

设涡轮盘材料为GH901，弹性模量 $E$ 为 $1 7 0 \ \mathrm { G P a }$ ,泊松比 $\nu$ 为0.32，密度 $\rho$ 为$8 2 1 0 \mathrm { k g / m } ^ { 3 }$ 。建涡轮盘轴对称计算模型（见图7-33），轮缘施加外载荷为 $6 3 7 \ \mathrm { M P a }$ ,转速为 $100 \%$ ，对涡轮盘进弹性应/应变分析，其周向应和周向应变如图7-34和图7-35所示。

![](images/048426e6218a9fc4fb095e8d352d71b8d5193bdce8823fa75ebe99a6fac6764b.jpg)  
图7-33 涡轮盘轴对称计算模型

![](images/00a16c2bcc166f69010adc0256c46407f7c7a82ffcad42e8c95ef150e89887bb.jpg)  
图7-34 涡轮盘周向应

![](images/561baaf258e3a66856644516f4d6155e19fd7aba4a9615c654ea93d219a777f4.jpg)  
图7-35 涡轮盘周向应变

盘处周向应力局部归一化后的分布曲线如图7-36所， $L$ 代表的长度如图7-37所示，根据盘心处周向应力的局部归一化分布曲线计算得到应力梯度影响因Y为1.128，利用Neuber法计算盘心处局部应/应变结果见表7-11，根据式（7-45）预测得到涡轮盘盘处寿命为 $1 . 3 7 \times 1 0 ^ { 4 }$ o

![](images/7f221e883b2ceb1e86afb5ab08e96d32f87f0590296c1dbc4e33ee4438e7bda1.jpg)  
图7-36 盘处周向应局部归化后的分布曲线

表7-11 Neuber法计算得到盘心处局部应/应变  

<table><tr><td rowspan=1 colspan=1>R</td><td rowspan=1 colspan=1>最大周向应力/MPa</td><td rowspan=1 colspan=1>周向应变</td><td rowspan=1 colspan=1>最大应力/MPa</td><td rowspan=1 colspan=1>最大应变</td><td rowspan=1 colspan=1>应力范围MPa</td><td rowspan=1 colspan=1>应变范围</td><td rowspan=1 colspan=1>平均应力MPa</td><td rowspan=1 colspan=1>8a</td><td rowspan=1 colspan=1>$R$</td></tr><tr><td rowspan=1 colspan=1>0.1</td><td rowspan=1 colspan=1>1086.82</td><td rowspan=1 colspan=1>0.007132</td><td rowspan=1 colspan=1>925.34</td><td rowspan=1 colspan=1>0.0084</td><td rowspan=1 colspan=1>1023.1</td><td rowspan=1 colspan=1>0.0061</td><td rowspan=1 colspan=1>413.77</td><td rowspan=1 colspan=1>0.0031</td><td rowspan=1 colspan=1>-0.1057</td></tr></table>

![](images/eeb5de83f24f3746ab1fe6becb5a85bd362b476ce0987237ea7b9afc9db3794a.jpg)  
图7-37 归化中 $L$ 代表的距离

（2）涡轮盘低循环疲劳参数敏感性分析

基于式（7-45）对涡轮盘低循环疲劳参数进敏感性分析，以获得对涡轮盘低循环疲劳可靠性影响比较大的参数，将这些参数作为可靠性分析随机变量，剔除敏感性较低的随机变量影响，从提可靠性分析的针对性和效率。

先，依据式（7-45）可知应是涡轮盘寿命的重要控制量：如果应变化 $5 \%$ ,涡轮盘寿命就会变化 $1 5 \%$ 左右。而涡轮盘转速、轮缘温度、盘温度、轮缘外载及弹性模量的变化都会对涡轮盘应力产影响，可以通过应力对这些参数的敏感性分析来掌握不同参数影响程度的。计算结果见表 $7 - 1 2 \sim$ 表7-15，由表可知，转速、轮缘温度和盘心温度对涡轮盘应力水平影响较大，是相对重要的随机变量。

表7-12 转速变化对危险点应力的影响  

<table><tr><td rowspan=1 colspan=1>载荷条件</td><td rowspan=1 colspan=1>最大周向应力/MPa</td><td rowspan=1 colspan=1>最大等效应力/MPa</td></tr><tr><td rowspan=1 colspan=1>转速，100%(n)</td><td rowspan=1 colspan=1>1086.82</td><td rowspan=1 colspan=1>1327.37</td></tr><tr><td rowspan=1 colspan=1>转速， 97%(n −3σn)</td><td rowspan=1 colspan=1>1032.07</td><td rowspan=1 colspan=1>1260.18</td></tr><tr><td rowspan=1 colspan=1>相对变化率</td><td rowspan=1 colspan=1>0.050</td><td rowspan=1 colspan=1>0.051</td></tr></table>

表7-13 轮缘及盘心温度变化对危险点应力的影响  

<table><tr><td rowspan=1 colspan=1>载荷条件</td><td rowspan=1 colspan=1>最大周向应力/MPa</td><td rowspan=1 colspan=1>最大等效应力/MPa</td></tr><tr><td rowspan=1 colspan=1>轮缘温度，580℃（μr)盘心温度，480℃(T2)</td><td rowspan=1 colspan=1>1086.82</td><td rowspan=1 colspan=1>1327.37</td></tr><tr><td rowspan=1 colspan=1>轮缘温度，667℃（μT₁+3στ1）盘心温度，408℃（T2-3σr2）</td><td rowspan=1 colspan=1>1282.14</td><td rowspan=1 colspan=1>1551.49</td></tr><tr><td rowspan=1 colspan=1>相对变化率</td><td rowspan=1 colspan=1>0.180</td><td rowspan=1 colspan=1>0.169</td></tr></table>

表7-14轮缘外载变化对危险点应力的影响  

<table><tr><td rowspan=1 colspan=1>载荷条件</td><td rowspan=1 colspan=1>最大周向应力/MPa</td><td rowspan=1 colspan=1>最大等效应力/MPa</td></tr><tr><td rowspan=1 colspan=1>轮缘外载，637MPa（p）</td><td rowspan=1 colspan=1>1086.82</td><td rowspan=1 colspan=1>1327.37</td></tr><tr><td rowspan=1 colspan=1>轮缘外载，541.45MPa（p-3σp）</td><td rowspan=1 colspan=1>1080.31</td><td rowspan=1 colspan=1>1319.04</td></tr><tr><td rowspan=1 colspan=1>相对变化率</td><td rowspan=1 colspan=1>0.006</td><td rowspan=1 colspan=1>0.006</td></tr></table>

表7-15 弹性模量变化对危险点应力的影响   

<table><tr><td rowspan=1 colspan=1>载荷条件</td><td rowspan=1 colspan=1>最大周向应力/MPa</td><td rowspan=1 colspan=1>最大等效应力/MPa</td></tr><tr><td rowspan=1 colspan=1>弹性模量，17000MPa（E）</td><td rowspan=1 colspan=1>1086.82</td><td rowspan=1 colspan=1>1327.37</td></tr><tr><td rowspan=1 colspan=1>弹性模量，159800MPa（ε-3σ）</td><td rowspan=1 colspan=1>1079.8</td><td rowspan=1 colspan=1>1319.29</td></tr><tr><td rowspan=1 colspan=1>相对变化率</td><td rowspan=1 colspan=1>0.006</td><td rowspan=1 colspan=1>0.006</td></tr></table>

另一方面，由式（7-45）可知，当应力梯度影响因子 $Y$ 变化 $1 \%$ ,寿命就会变化$7 \%$ 左右，因而希望进一步明确轮缘温度、盘温度及转速的变化对应梯度影响因$Y$ 的影响。经过计算得到影响结果见表7-16。

表7-16轮缘温度、盘心温度及转速的变化对 $Y$ 的影响  

<table><tr><td rowspan=1 colspan=1>轮缘温度，580℃（(μr₁）盘心温度，480℃（T2)转速，100%（n)</td><td rowspan=1 colspan=1>轮缘温度，667℃(T₁+3σT₁)盘心温度，408℃(T2-3σr2)</td><td rowspan=1 colspan=1>转速，97%(n-3σn)</td></tr><tr><td rowspan=1 colspan=1>1.128</td><td rowspan=1 colspan=1>1.161</td><td rowspan=1 colspan=1>1.129</td></tr><tr><td rowspan=1 colspan=1>相对变化率</td><td rowspan=1 colspan=1>0.029</td><td rowspan=1 colspan=1>0.001</td></tr></table>

综上所述，在对涡轮盘低循环疲劳寿命可靠性分析中，考虑的主要随机变量有材料参数随机变量（拉伸强度极限 $\sigma _ { \mathrm { ~ b ~ } }$ 和断面收缩率 $\psi$ ）和载荷随机变量（轮缘温度 $T _ { 1 }$ 、盘心温度 $T _ { 2 }$ 和转速 $n$ )。

(3）涡轮盘低循环疲劳可靠性分析

以低循环疲劳为失效模式，根据寿命模型式（7–45）定义功能函数为

$$
G = N _ { \mathrm { f } } ( X ) - N _ { 0 }
$$

式中： $X$ 影响低循环疲劳寿命的随机变量，这代表拉伸强度极限 $\sigma _ { \mathrm { ~ b ~ } }$ 、断收缩率$\psi$ 、轮缘温度 $T _ { \parallel }$ 、盘温度 $T _ { 2 }$ 和转速 $n$ ;

$N _ { 0 }$ 给定寿命。

那么低循环疲劳失效概率为

$$
P _ { \mathrm { ~ f ~ } } = P ( G < 0 ) = P ( N _ { t } - N _ { 0 } < 0 )
$$

$\textcircled{1}$ 基于蒙特卡罗法

采用蒙特卡罗法计算涡轮盘低循环疲劳可靠度，考虑的随机变量正态分布参数见表7–17。根据随机变量分布参数成 $2 . 5 \times 1 0 ^ { 4 }$ 个样本点，分别利有限元软件和寿命程计算盘心处的寿命，以及给定寿命下的疲劳可靠度，将计算的值作为近似准确值，以此来评价基于次多项式响应面法的计算结果。

表7-17 随机变量的正态分布参数  

<table><tr><td rowspan=1 colspan=2>σ/MPa$</td><td rowspan=1 colspan=2>4/0%</td><td rowspan=1 colspan=2>T/℃</td><td rowspan=1 colspan=2>T2/℃</td><td rowspan=1 colspan=2>n</td></tr><tr><td rowspan=1 colspan=1>μ</td><td rowspan=1 colspan=1>σ</td><td rowspan=1 colspan=1>μ</td><td rowspan=1 colspan=1>σ</td><td rowspan=1 colspan=1>μ</td><td rowspan=1 colspan=1>σ</td><td rowspan=1 colspan=1>μ</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>μ</td><td rowspan=1 colspan=1>σ</td></tr><tr><td rowspan=1 colspan=1>1067</td><td rowspan=1 colspan=1>5%</td><td rowspan=1 colspan=1>24</td><td rowspan=1 colspan=1>5%μ</td><td rowspan=1 colspan=1>580</td><td rowspan=1 colspan=1>2%μ</td><td rowspan=1 colspan=1>480</td><td rowspan=1 colspan=1>2%</td><td rowspan=1 colspan=1>100%</td><td rowspan=1 colspan=1>1%</td></tr></table>

通过计算，得到盘心处周向应力、周向应变、应力梯度影响因子、应变幅，以及预测寿命直图如图 $7 - 3 8 \sim$ 图7-42所，不同给定寿命下的可靠度见表7–18。

![](images/64301410d43b3498ba483eb975f37b3de0edf09c6a7f534f886890f53d82fd8c.jpg)  
图7-38 盘处周向应

![](images/99447d3aa55e143f01eab645e675924d65cd127c29714b3cefb8336cadc85fd7.jpg)  
图7-39 盘处周向应变

![](images/13ca3a5f7662ef9daa735050b2a8d2e61ca01796cdba28766c8b62079395b158.jpg)  
图7-40盘心处应力梯度影响因子

![](images/3d4d206f212a02bd1e2328b9e0629e15483b4224c23eb1a0d3027f81859e2476.jpg)  
图7-41 盘处应变幅

![](images/80ef1fe80cf5693da9926e4180e9f27e2db7b36c0c6eb2da0851d481df2c1c0f.jpg)  
图7-42 盘处预测寿命

表7-18 基于蒙特卡罗抽样法的可靠性分析结果  

<table><tr><td rowspan=1 colspan=1>给定寿命</td><td rowspan=1 colspan=1>1×104</td><td rowspan=1 colspan=1>8×103</td><td rowspan=1 colspan=1>7×10^3</td><td rowspan=1 colspan=1>6.5×103</td><td rowspan=1 colspan=1>6×103</td></tr><tr><td rowspan=1 colspan=1>可靠度</td><td rowspan=1 colspan=1>0.95856</td><td rowspan=1 colspan=1>0.99820</td><td rowspan=1 colspan=1>0.99988</td><td rowspan=1 colspan=1>0.99992</td><td rowspan=1 colspan=1>1.00000</td></tr></table>

$\textcircled{2}$ 基于次多项式响应法

采次多项式响应法计算涡轮盘低循环疲劳可靠度，计算流程如图7-43所，考虑的随机变量正态分布参数见表7–17。

![](images/6888968d254db8ac5cbd842328f217108c586441ed638daca9ef9f39ea5343ac.jpg)  
图7-43 涡轮盘低循环疲劳可靠性分析流程

采用正交试验的方法构造最大周向应力，最大周向应变及应力梯度影响系数的响应面函数，变量为转速 $n$ 、轮缘温度 $T _ { 1 }$ 、盘温度 $T _ { 2 }$ ，每个参数选定了3个平，见表7-19，相应的正交试验设计组合及盘心处最大周向应力、最大周向应变、应力梯度影响系数响应值见表7–20。

表7-19 参数平  

<table><tr><td rowspan=1 colspan=1>水平</td><td rowspan=1 colspan=1>n</td><td rowspan=1 colspan=1>T1/℃$</td><td rowspan=1 colspan=1>$T2℃$</td></tr><tr><td rowspan=1 colspan=1>bid</td><td rowspan=1 colspan=1>97%</td><td rowspan=1 colspan=1>546</td><td rowspan=1 colspan=1>452</td></tr><tr><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>100%</td><td rowspan=1 colspan=1>580</td><td rowspan=1 colspan=1>480</td></tr><tr><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>103%</td><td rowspan=1 colspan=1>614</td><td rowspan=1 colspan=1>508</td></tr></table>

表7-20参数组合表及盘心处 $\sigma _ { z }$ , $\varepsilon _ { z }$ 和 $Y$ 响应值  

<table><tr><td rowspan=1 colspan=1>试验号</td><td rowspan=1 colspan=1>n/(r/min)</td><td rowspan=1 colspan=1>T₁/C</td><td rowspan=1 colspan=1>$T_/℃$</td><td rowspan=1 colspan=1>$^ {/MPa$</td><td rowspan=1 colspan=1>82/10-3</td><td rowspan=1 colspan=1>Y</td></tr><tr><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>97%</td><td rowspan=1 colspan=1>546</td><td rowspan=1 colspan=1>452</td><td rowspan=1 colspan=1>1025.54</td><td rowspan=1 colspan=1>6.731</td><td rowspan=1 colspan=1>1.0841</td></tr><tr><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>97%</td><td rowspan=1 colspan=1>580</td><td rowspan=1 colspan=1>480</td><td rowspan=1 colspan=1>1032.1</td><td rowspan=1 colspan=1>6.772</td><td rowspan=1 colspan=1>1.0850</td></tr><tr><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>97%</td><td rowspan=1 colspan=1>614</td><td rowspan=1 colspan=1>508</td><td rowspan=1 colspan=1>1038.45</td><td rowspan=1 colspan=1>6.814</td><td rowspan=1 colspan=1>1.0857</td></tr><tr><td rowspan=1 colspan=1>4</td><td rowspan=1 colspan=1>100%</td><td rowspan=1 colspan=1>546</td><td rowspan=1 colspan=1>480</td><td rowspan=1 colspan=1>1046.84</td><td rowspan=1 colspan=1>6.878</td><td rowspan=1 colspan=1>1.0786</td></tr><tr><td rowspan=1 colspan=1>5</td><td rowspan=1 colspan=1>100%</td><td rowspan=1 colspan=1>580</td><td rowspan=1 colspan=1>508</td><td rowspan=1 colspan=1>1052.89</td><td rowspan=1 colspan=1>6.917</td><td rowspan=1 colspan=1>1.0792</td></tr><tr><td rowspan=1 colspan=1>6</td><td rowspan=1 colspan=1>100%</td><td rowspan=1 colspan=1>614</td><td rowspan=1 colspan=1>452</td><td rowspan=1 colspan=1>1161.54</td><td rowspan=1 colspan=1>7.608</td><td rowspan=1 colspan=1>1.0943</td></tr><tr><td rowspan=1 colspan=1>7</td><td rowspan=1 colspan=1>103%</td><td rowspan=1 colspan=1>546</td><td rowspan=1 colspan=1>508</td><td rowspan=1 colspan=1>1069.77</td><td rowspan=1 colspan=1>7.035</td><td rowspan=1 colspan=1>1.0731</td></tr><tr><td rowspan=1 colspan=1>8</td><td rowspan=1 colspan=1>103%</td><td rowspan=1 colspan=1>580</td><td rowspan=1 colspan=1>452</td><td rowspan=1 colspan=1>1176.96</td><td rowspan=1 colspan=1>7.719</td><td rowspan=1 colspan=1>1.0879</td></tr><tr><td rowspan=1 colspan=1>9</td><td rowspan=1 colspan=1>103%</td><td rowspan=1 colspan=1>614</td><td rowspan=1 colspan=1>480</td><td rowspan=1 colspan=1>1183.87</td><td rowspan=1 colspan=1>7.762</td><td rowspan=1 colspan=1>1.0885</td></tr></table>

根据表7-20中的数据构造出盘心处最大周向应力、最大周向应变及应力梯度影响系数的响应面函数，响应面函数形式如下

$$
g ( n , T _ { 1 } , T _ { 2 } ) \ = \ a _ { 0 } \ + \ a _ { 1 } n \ + \ a _ { 2 } T _ { 1 } \ + \ a _ { 3 } T _ { 2 } \ + \ a _ { 4 } n ^ { 2 } \ + \ a _ { 5 } T _ { 1 } ^ { 2 } \ + \ a _ { 6 } T _ { 2 } ^ { 2 }
$$

表7-21 $\pmb { \sigma } _ { z }$ , $\varepsilon _ { z }$ 和 $Y$ 响应面函数系数  

<table><tr><td rowspan=1 colspan=1>参量</td><td rowspan=1 colspan=1>a0</td><td rowspan=1 colspan=1>$a1</td><td rowspan=1 colspan=1>$a2$</td><td rowspan=1 colspan=1>a3</td><td rowspan=1 colspan=1>a4</td><td rowspan=1 colspan=1>$a5</td><td rowspan=1 colspan=1>a6</td></tr><tr><td rowspan=1 colspan=1>σz/MPa</td><td rowspan=1 colspan=1>-31.2438</td><td rowspan=1 colspan=1>0.0219</td><td rowspan=1 colspan=1>0.832</td><td rowspan=1 colspan=1>-1.112</td><td rowspan=1 colspan=1>3.5727×10-6</td><td rowspan=1 colspan=1>3.0421×10-4</td><td rowspan=1 colspan=1>-9.9915×10-5</td></tr><tr><td rowspan=1 colspan=1>z/10-3</td><td rowspan=1 colspan=1>-0.1899</td><td rowspan=1 colspan=1>1.5075×10-4</td><td rowspan=1 colspan=1>0.0055</td><td rowspan=1 colspan=1>-0.0077</td><td rowspan=1 colspan=1>2.3244×10-8</td><td rowspan=1 colspan=1>1.7301×10-6</td><td rowspan=1 colspan=1>0.0000</td></tr><tr><td rowspan=1 colspan=1>Y</td><td rowspan=1 colspan=1>1.1296</td><td rowspan=1 colspan=1>-4.5343×10-6</td><td rowspan=1 colspan=1>1.4357×10-4</td><td rowspan=1 colspan=1>-1.8886×10-4</td><td rowspan=1 colspan=1>8.6088×10-11</td><td rowspan=1 colspan=1>1.4418×10-8</td><td rowspan=1 colspan=1>2.1259×10-8</td></tr></table>

根据构造的盘心处最大周向应力、最大周向应变及应力梯度影响系数的响应面函数，最终对涡轮盘进疲劳寿命可靠性分析，采用蒙特卡罗法计算可靠度，抽样次数为$1 0 ^ { 5 }$ ，分析结果见表7-22。

表7-22 基于二次多项式响应面法可靠性分析结果  

<table><tr><td rowspan=1 colspan=1>给定寿命</td><td rowspan=1 colspan=1>1x104</td><td rowspan=1 colspan=1>8×10^3</td><td rowspan=1 colspan=1>7×10^3</td><td rowspan=1 colspan=1>6.5×103</td><td rowspan=1 colspan=1>6×10{$</td></tr><tr><td rowspan=1 colspan=1>可靠度</td><td rowspan=1 colspan=1>0.95036</td><td rowspan=1 colspan=1>0.99748</td><td rowspan=1 colspan=1>0.99976</td><td rowspan=1 colspan=1>0.99994</td><td rowspan=1 colspan=1>1.00000</td></tr></table>

进一步研究在给定寿命为 $1 0 ^ { 4 }$ 时，随机变量对涡轮盘低循环疲劳可靠性的影响，变异系数（coeficientof variation）表示随机变量标准差与均值的比值，计算结果如图7–44所示，从计算结果可知在该计算条件下，转速 $n$ 、拉伸强度极限 $\sigma _ { \mathrm { ~ b ~ } }$ 、断面收缩率 $\psi$ 对涡轮盘低循环疲劳可靠性影响比较大。

![](images/675588888725aeeb67aa394c9daa99e4fb7fa4a97bc244f512e6f7e80148ccff.jpg)  
图7-44 随机变量对涡轮盘低循环疲劳可靠性的影响

# 7.3 涡轮叶结构可靠性试验及其评定法

前述的结构可靠性设计分析法原则上亦适于涡轮叶结构，这里不再赘述设计分析法，而是针对实际的涡轮转叶结构，给出其温低循环疲劳/蠕变寿命试验评定的具体法和流程，并利用所述的试验法确定了实际涡轮叶结构的温低循环疲劳寿命，其中计人了高温蠕变的影响。为了缩短试验时间，按照损伤等效原则，确定了等效加速试验载荷谱。具体的试验是在采感应加热、液压加载的菲利轮试验器上进的。采对数正态分布和威布尔分布对试验结果进了统计分析，给出了置信度为$9 5 \%$ 、可靠度为 $9 9 . 8 7 \%$ 的叶安全使寿命。

# 7.3.1 涡轮叶结构可靠性评定法简介

涡轮叶属于航空发动机的关键件，需要对其疲劳/蠕变寿命进评定。涡轮叶的寿命有按其蠕变伸长量来评定的，也有按其低循环疲劳寿命（次数）或飞小时数来评定的。通常涡轮叶的低循环疲劳/蠕变寿命可采用试验方法进评定。若采用定时截尾寿命试验，确定的是叶使用技术寿命；若采用断裂截尾寿命试验，则确定的是叶安全使寿命。前，对涡轮叶寿命的评定绝多数是通过低循环疲劳/蠕变试验确定其可靠性（安全使用）寿命。

针对图7-45（a）所的实际涡轮叶结构，采涡电流感应加热、成形/摩擦夹具、液压加载的方法在菲利轮试验器上对其进行了高温低循环疲劳试验，并在试验中重点考虑了温蠕变的影响。对按损伤等效的加速寿命试验结果采用对数正态分布和威布尔分布进了统计分析，给出了置信度为 $9 5 \%$ 、可靠度为99. $87 \%$ 的叶安全使用寿命。

由于对该涡轮叶结构来说，蠕变引起的损伤比低循环疲劳损伤大得多，考虑温蠕变影响的低循环疲劳寿命单纯的低循环疲劳寿命要得多，但这更符合发动机的实际情况。在叶低循环疲劳试验中强调温蠕变的影响，增加了试验难度，并使试验周期大为增加。

在低循环疲劳/蠕变寿命试验中，针对该涡轮叶结构的特点，自研制了适于温下工作的成形/摩擦夹具；采用损伤等效的加速试验载荷谱，使试验周期在实验室条件下能够接受；应统计分析法给出了带有置信度的叶可靠性（安全使）寿命[24]。

# 7.3.2 涡轮叶结构危险截及寿命考核点的确定

有限元分析结果表明：靠近叶尖的Ⅱ（造型）截面为该涡轮叶片的危险截面，位于该截面上的减振箍带孔边（有限元模型的节点1728）为寿命考核点，如图7-45（b）所。图中有关节点的循环（径向）应范围见表7-23。由表中可以看出，寿命考核点的应平相当，接近于叶材料的屈服应。

![](images/902dbcd7a3d54112d713691791738d88250fc18c1a9aa290881772c56bf8892f.jpg)  
图7-45 实际的涡轮叶及其危险截（ $\mathbb { I }$ 截面）与部分有限元节点号

表7-23 涡轮叶危险截上部分节点的循环（径向）应  

<table><tr><td rowspan=2 colspan=1>循环（径向）应力</td><td rowspan=1 colspan=7>节点</td></tr><tr><td rowspan=1 colspan=2>1728       1746</td><td rowspan=1 colspan=1>2136</td><td rowspan=1 colspan=1>2148</td><td rowspan=1 colspan=1>2559</td><td rowspan=1 colspan=1>43</td><td rowspan=1 colspan=1>2412</td></tr><tr><td rowspan=1 colspan=1>加载的最大应力/MPa</td><td rowspan=1 colspan=1>588.04</td><td rowspan=1 colspan=1>518.28</td><td rowspan=1 colspan=1>379.04</td><td rowspan=1 colspan=1>486.43</td><td rowspan=1 colspan=1>126.78</td><td rowspan=1 colspan=1>65.12</td><td rowspan=1 colspan=1>127.31</td></tr><tr><td rowspan=1 colspan=1>卸载的残余应力/MPa</td><td rowspan=1 colspan=1>-68.78</td><td rowspan=1 colspan=1>-24.58</td><td rowspan=1 colspan=1>0.0</td><td rowspan=1 colspan=1>10.94</td><td rowspan=1 colspan=1>0.0</td><td rowspan=1 colspan=1>0.0</td><td rowspan=1 colspan=1>0.0</td></tr></table>

为了确定试验载荷，先计算得到Ⅱ截面以上部分叶身和相应减振箍带在转子$100 \%$ 转速 $1 1 1 5 0 \mathrm { r / \mathrm { m i n } }$ 下的总质量离心力为 $F _ { 0 } = 1 6 2 4 5 \mathrm { N }$ ；然后将该分布于Ⅱ截以上叶盆与叶背两侧的节点上，经有限元计算表明，考核点的应与表 $7 - 2 3$ 中的数值非常吻合。这样做的的是为了采成形/摩擦夹具施加载荷。

# 7.3.3 试验载荷谱与等效加速试验载荷谱

分析提供的试验载荷谱，如图7-46所示，并要求：试验温度为 $8 3 2 \mathrm { { ^ \circ C } }$ ，保载时间$\Delta t _ { 2 } = 3 8 6 . 1 4 \mathrm { s }$ 。对于此载荷谱，预计断裂循环数为7952，且每2249个循环与外场1000飞小时的损伤相当。

![](images/a4dff48c40e0eee0ceeea4a28d7da29842ea737c72f7225a88be04e6c2b78026.jpg)  
图7-46 试验载荷谱

经简单计算可知：对于此载荷谱，每叶的总保载时间为 $8 5 2 . 9 4 \mathrm { h }$ , $1 2 \mathrm { h }$ 工作制则至少需要71d，而这对于要求断裂截尾的有效子样必须11个以上，出于试验时间上的考虑，是不可的。因此，必须按损伤等效的原则，制定等效加速试验载荷谱。

对于该涡轮叶结构，低循环疲劳/蠕变交互作是影响其寿命的主要因素，其中因蠕变引起的损伤占总损伤的 $7 5 . 5 \%$ ，因低循环疲劳引起的损伤为总损伤的 $2 4 . 5 \%$ 需要指出的是，其中未能真正考虑低循环疲劳与蠕变之间的交互作用，而是分别计的，理论上虽不是很严格，但在给定的条件下，此分析结果的确是确定试验载荷谱的基础，实践表明也是可的。因此，对于该涡轮叶，确定保载时间是进试验研究的关键，也是确定试验用载荷谱的关键。

按照低循环疲劳、蠕变所占损伤的比例，仅由低循环疲劳损伤导致破坏的循环次数为32451，仅由蠕变损伤导致破坏的总保载时间为 $1 1 2 9 . 7 2 \mathrm { h }$ 。此外，还知道1000飞时的低循环疲劳和蠕变损伤之和为0.29313，而 $2 2 4 9 / 7 9 5 2 = 0 . 2 8 2 8 2$ ，故知：前个循环引起的损伤后个循环的要。这主要是由于蠕变使得应得到松弛，后个循环的应比前一个循环的小，相应地，引起的损伤也。

对于该涡轮叶所采的材料GH4049合，其热强参数程可写为

$$
\mathrm { l g } \sigma = a _ { 0 } + a _ { 1 } P + a _ { 2 } P ^ { 2 } + a _ { 3 } P ^ { 3 }
$$

$$
P = 0 . 0 2 0 9 2 T + \lg t
$$

式中： $\sigma$ (i:) 一应力， $\mathrm { M P a }$

$a _ { 0 }$ , $a _ { 1 }$ , $a _ { 2 }$ , $a _ { 3 }$ 参数，见表7-24；

$T -$ (id) 绝对温度，K;

t 至断裂时间， $\mathrm { h }$

表7-24GH4049合金热强参数方程的常数项及系数  

<table><tr><td rowspan=1 colspan=1>存活率/%</td><td rowspan=1 colspan=1>a0</td><td rowspan=1 colspan=1>$a\</td><td rowspan=1 colspan=1>$a2</td><td rowspan=1 colspan=1>a3</td></tr><tr><td rowspan=1 colspan=1>中值</td><td rowspan=1 colspan=1>-0.347323×10</td><td rowspan=1 colspan=1>0.816596</td><td rowspan=1 colspan=1>-0.30828×10-1</td><td rowspan=1 colspan=1>0.31445 ×10-3</td></tr><tr><td rowspan=1 colspan=1>90</td><td rowspan=1 colspan=1>0.584697×10</td><td rowspan=1 colspan=1>-0.317388</td><td rowspan=1 colspan=1>0.15076×10-1</td><td rowspan=1 colspan=1>-0.30467×10-3</td></tr><tr><td rowspan=1 colspan=1>95</td><td rowspan=1 colspan=1>0.799062×10</td><td rowspan=1 colspan=1>-0.579322</td><td rowspan=1 colspan=1>0.25721×10-1</td><td rowspan=1 colspan=1>-0.44881×10-3</td></tr><tr><td rowspan=1 colspan=1>99.87</td><td rowspan=1 colspan=1>0.161556×102</td><td rowspan=1 colspan=1>-0.158381×10</td><td rowspan=1 colspan=1>0.66831×10-1</td><td rowspan=1 colspan=1>-0.10094×10-3</td></tr></table>

在要求的试验温度（ $8 3 2 \%$ ）下，根据上述热强程可以得到在给定的断裂寿命下，与给定存活率相对应的应，结果列于表7-25。

表7-25 给定断裂寿命下，与给定存活率相对应的应力 MPa  

<table><tr><td rowspan=2 colspan=1>断裂寿命</td><td rowspan=1 colspan=4>存活率/%</td></tr><tr><td rowspan=1 colspan=1>中值</td><td rowspan=1 colspan=1>90</td><td rowspan=1 colspan=1>95</td><td rowspan=1 colspan=1>95.87</td></tr><tr><td rowspan=1 colspan=1>28h</td><td rowspan=1 colspan=1>441.19</td><td rowspan=1 colspan=1>427.83</td><td rowspan=1 colspan=1>424.10</td><td rowspan=1 colspan=1>411.80</td></tr><tr><td rowspan=1 colspan=1>29h</td><td rowspan=1 colspan=1>439.20</td><td rowspan=1 colspan=1>425.91</td><td rowspan=1 colspan=1>422.19</td><td rowspan=1 colspan=1>409.96</td></tr><tr><td rowspan=1 colspan=1>1129h</td><td rowspan=1 colspan=1>262.71</td><td rowspan=1 colspan=1>254.11</td><td rowspan=1 colspan=1>251.69</td><td rowspan=1 colspan=1>243.15</td></tr><tr><td rowspan=1 colspan=1>1130h</td><td rowspan=1 colspan=1>262.67</td><td rowspan=1 colspan=1>254.08</td><td rowspan=1 colspan=1>251.66</td><td rowspan=1 colspan=1>243.12</td></tr></table>

对于低循环疲劳，可以采如下的应变寿命程进描述

$$
\frac { \Delta \varepsilon _ { \mathrm { t } } } { 2 } = \frac { \sigma _ { \mathrm { t } } ^ { \prime } } { E } ( 2 N _ { \mathrm { f } } ) ^ { b } + \varepsilon _ { \mathrm { j } } ^ { \prime } ( 2 N _ { \mathrm { f } } ) ^ { c }
$$

对于GH4049合，上式中的有关参数列于表7-26。

表7-26 GH4049合金低循环疲劳的有关参数  

<table><tr><td rowspan=1 colspan=1>温度/℃</td><td rowspan=1 colspan=1>E/MPa</td><td rowspan=1 colspan=1>σ1/MPa</td><td rowspan=1 colspan=1>81%</td><td rowspan=1 colspan=1>b</td><td rowspan=1 colspan=1>c</td></tr><tr><td rowspan=1 colspan=1>500</td><td rowspan=1 colspan=1>203800</td><td rowspan=1 colspan=1>1906</td><td rowspan=1 colspan=1>25.90</td><td rowspan=1 colspan=1>-0.1027</td><td rowspan=1 colspan=1>-0.8120</td></tr><tr><td rowspan=1 colspan=1>600</td><td rowspan=1 colspan=1>198200</td><td rowspan=1 colspan=1>1745</td><td rowspan=1 colspan=1>22.80</td><td rowspan=1 colspan=1>-0.1029</td><td rowspan=1 colspan=1>-0.8325</td></tr><tr><td rowspan=1 colspan=1>700</td><td rowspan=1 colspan=1>187000</td><td rowspan=1 colspan=1>2260</td><td rowspan=1 colspan=1>34.80</td><td rowspan=1 colspan=1>-0.1508</td><td rowspan=1 colspan=1>-0.9119</td></tr><tr><td rowspan=1 colspan=1>800</td><td rowspan=1 colspan=1>177700</td><td rowspan=1 colspan=1>2068</td><td rowspan=1 colspan=1>10.84</td><td rowspan=1 colspan=1>-0.1508</td><td rowspan=1 colspan=1>-0.7116</td></tr></table>

由于表中材料的试验温度最为 $8 0 0 \mathrm { { ^ \circ C } }$ ，因而 $8 3 2 \mathrm { { ^ \circ C } }$ 的有关材料参数只能通过外插得到。根据应变寿命程式（7–50）可以得到与指定循环次数（断裂寿命）对应的总应变幅 $\varepsilon _ { \mathrm { { t } } } / 2$ 列于表7-27。

表7-27 与指定循环次数对应的总应变幅   

<table><tr><td rowspan=2 colspan=1>总应变幅</td><td rowspan=1 colspan=5>循环/次</td></tr><tr><td rowspan=1 colspan=1>10000</td><td rowspan=1 colspan=1>15120</td><td rowspan=1 colspan=1>15450</td><td rowspan=1 colspan=1>32451</td><td rowspan=1 colspan=1>50000</td></tr><tr><td rowspan=1 colspan=1>(ε/2)/%</td><td rowspan=1 colspan=1>0.2631</td><td rowspan=1 colspan=1>0.2463</td><td rowspan=1 colspan=1>0.2455</td><td rowspan=1 colspan=1>0.2184</td><td rowspan=1 colspan=1>0.2042</td></tr></table>

为了缩短试验时间，必须提试验载荷。根据实验室的条件，每叶拟保载的总时间为21. $1 4 \mathrm { h }$ ( $2 8 \mathrm { h } \times 7 5 . 5 \%$ ），这是按等比例损伤折合的。相应地，此时的应力为$4 4 1 . 1 9 \mathrm { M P a }$ （中值）。试验中，对于实际的高温构件采用的是载荷控制，一般很难进行应力或应变控制。为达到此应力值，相应地液压作动筒的表压由 $2 . 3 5 4 4 \mathrm { M P a }$ 提高至$3 . 9 2 4 0 \mathrm { M P a }$ ,即 $F _ { 0 }$ 由16245N提高至 $2 7 0 7 6 \mathrm { N }$ 。每个循环保载时间为20s，预计寿命为3805次循环，亦即此等效加速试验载荷谱的每个循环引起的损伤相当于试验载荷谱每个循环的2.1倍。

需要说明的是：（1）所用的材料参数是由试验参数外插的；（2）假设每个循环所产生的损伤相同，这对于因蠕变而有应力松弛的情况在理论上是不严格的；（3）载荷加大，保证低循环疲劳和蠕变的损伤比例不变是近似的，实际上两者是交互作用的。事实上，这三个因素将使试验结果偏于保守。

# 7.3.4 试验结果及其统计分析

按上述等效加速试验载荷谱，采涡电流感应加热（温度控制在 $8 3 2 ^ { \circ } \mathrm { C } \pm 5 ^ { \circ } \mathrm { C }$ 范围内）、成形/摩擦夹具、液压加载的方法在菲利轮试验器上对分别服役 $6 9 8 \mathrm { h } ~ 8 \mathrm { m i n }$ 和 $7 4 9 \mathrm { h }$ $4 9 \mathrm { m i n }$ 的涡轮叶进了温低循环疲劳/蠕变寿命试验，结果（经断分析，确认为有效样）见表7-28，图7–47出了部分断裂的涡轮叶。

对于机械构件寿命试验数据，般认为其服从对数正态分布或威布尔（Weibull）分布[1]。正态分布和Weibull分布的概率密度函数分别可以写成式（7–51）和式（7–52)

$$
f ( \lg t ) \ = \frac { 1 } { \sqrt { 2 \pi } \sigma } \mathrm { e } ^ { - \frac { ( \lfloor \ g t - \mu ) 2 } { 2 \sigma ^ { 2 } } }
$$

表7-28 服役过的叶的试验结果（有效子样）  

<table><tr><td rowspan=1 colspan=1>服役时间</td><td rowspan=1 colspan=1>叶片编号</td><td rowspan=1 colspan=1>循环次数</td><td rowspan=1 colspan=1>折合循环数</td><td rowspan=1 colspan=1>折合小时数</td></tr><tr><td rowspan=5 colspan=1>698h 8min</td><td rowspan=1 colspan=1>1F1J120</td><td rowspan=1 colspan=1>5301</td><td rowspan=1 colspan=1>6048</td><td rowspan=1 colspan=1>5647</td></tr><tr><td rowspan=1 colspan=1>1F1J118</td><td rowspan=1 colspan=1>2288</td><td rowspan=1 colspan=1>3035</td><td rowspan=1 colspan=1>2834</td></tr><tr><td rowspan=1 colspan=1>1F5F122</td><td rowspan=1 colspan=1>3602</td><td rowspan=1 colspan=1>4349</td><td rowspan=1 colspan=1>4061</td></tr><tr><td rowspan=1 colspan=1>1F1J117</td><td rowspan=1 colspan=1>5427</td><td rowspan=1 colspan=1>6174</td><td rowspan=1 colspan=1>5765</td></tr><tr><td rowspan=1 colspan=1>1F5J57</td><td rowspan=1 colspan=1>8104</td><td rowspan=1 colspan=1>8851</td><td rowspan=1 colspan=1>8264</td></tr><tr><td rowspan=7 colspan=1>749h49min</td><td rowspan=1 colspan=1>1F0R315</td><td rowspan=1 colspan=1>6090</td><td rowspan=1 colspan=1>6893</td><td rowspan=1 colspan=1>6435</td></tr><tr><td rowspan=1 colspan=1>1F3R720</td><td rowspan=1 colspan=1>8115</td><td rowspan=1 colspan=1>8918</td><td rowspan=1 colspan=1>8325</td></tr><tr><td rowspan=1 colspan=1>1F0R326</td><td rowspan=1 colspan=1>2415</td><td rowspan=1 colspan=1>3218</td><td rowspan=1 colspan=1>3003</td></tr><tr><td rowspan=1 colspan=1>1F0R37</td><td rowspan=1 colspan=1>3336</td><td rowspan=1 colspan=1>4139</td><td rowspan=1 colspan=1>3863</td></tr><tr><td rowspan=1 colspan=1>1F3R717</td><td rowspan=1 colspan=1>5516</td><td rowspan=1 colspan=1>6139</td><td rowspan=1 colspan=1>5899</td></tr><tr><td rowspan=1 colspan=1>1F3R737</td><td rowspan=1 colspan=1>2884</td><td rowspan=1 colspan=1>3687</td><td rowspan=1 colspan=1>3441</td></tr><tr><td rowspan=1 colspan=1>1F3R77</td><td rowspan=1 colspan=1>4487</td><td rowspan=1 colspan=1>5290</td><td rowspan=1 colspan=1>4938</td></tr></table>

![](images/a864e8f0840b52dce4aea42cbb9bacd51aef3ddca7792f40768b48636180dfc2.jpg)  
图7-47 试验断裂的涡轮叶（有效样）

式中：均值 $\mu$ 为位置参数，标准差 $\sigma$ 为尺度参数。

$$
f ( t ) ~ = ~ \frac { m } { \eta } \left( { \frac { t - t _ { 0 } } { \eta } } \right) ^ { m - 1 } \mathrm { e } ^ { - \left( { \frac { t - t _ { 0 } } { \eta } } \right) ^ { n } }
$$

式中： $m$ (id:) 形状参数；$t _ { 0 }$ bcid:) 位置参数；$\eta$ (id:) 尺度参数。

当 $t _ { 0 } = 0$ 时，上式退化为两参数Weibull分布，此时的 $\eta$ 为特征寿命。

对上述12个样本进了统计分析，对数正态分布和Weibull分布的计算结果分别列于表7-29和表7-30中。

飞行小时飞行小时

表7-29 按对数正态分布计算的结果  

<table><tr><td rowspan=2 colspan=1>样本数</td><td rowspan=2 colspan=1>${2}$</td><td rowspan=2 colspan=1>0</td><td rowspan=1 colspan=2>γ=50%</td><td rowspan=1 colspan=2>γ=90%</td><td rowspan=1 colspan=2>γ=95%</td></tr><tr><td rowspan=1 colspan=1>050</td><td rowspan=1 colspan=1>09.87</td><td rowspan=1 colspan=1>050</td><td rowspan=1 colspan=1>099.87</td><td rowspan=1 colspan=1>050</td><td rowspan=1 colspan=1>099.87</td></tr><tr><td rowspan=1 colspan=1>12</td><td rowspan=1 colspan=1>0.966</td><td rowspan=1 colspan=1>5211</td><td rowspan=1 colspan=1>4902</td><td rowspan=1 colspan=1>1707</td><td rowspan=1 colspan=1>4306</td><td rowspan=1 colspan=1>1257</td><td rowspan=1 colspan=1>4153</td><td rowspan=1 colspan=1>1155</td></tr></table>

表7-30 按Weibull分布计算的结果  

<table><tr><td rowspan=1 colspan=1>样本数</td><td rowspan=1 colspan=1>三参数Weibull 分布</td><td rowspan=1 colspan=1>m</td><td rowspan=1 colspan=1>7</td><td rowspan=1 colspan=1>t0</td><td rowspan=1 colspan=1>${$</td><td rowspan=1 colspan=1>tR</td></tr><tr><td rowspan=1 colspan=1>12</td><td rowspan=1 colspan=1>γ =95%,R=99.87%</td><td rowspan=1 colspan=1>1.842</td><td rowspan=1 colspan=1>3312</td><td rowspan=1 colspan=1>1100</td><td rowspan=1 colspan=1>0.984</td><td rowspan=1 colspan=1>1190</td></tr></table>

由表中可以看出，相关系数值（ $_ { r r }$ ）是较的，说明计算结果是可信的。两种分布的处理结果很接近，对数正态分布的计算结果略低于Weibull分布的计算结果。

为安全起见，该涡轮叶叶身Ⅱ截面孔边（寿命考核点）的可靠性寿命确定为1155h（置信度为 $9 5 \%$ ，可靠度为 $9 9 . 8 7 \%$ ），考虑到裂纹扩展寿命占总寿命的比例不$5 \%$ ，进而可得其安全使用寿命为 $1 0 9 7 \mathrm { h }$

经以上试验研究和统计分析，可得如下结论。

（1）计人蠕变的影响，低循环疲劳寿命有所降低，这更符合发动机的实际情况，但增加了寿命试验的难度。因此，对于温度不太的叶，在进低循环疲劳寿命试验时般不计蠕变的影响。但是，对于温度较的涡轮叶，由于蠕变引起的损伤低循环疲劳的大得多，因而必须计蠕变的影响。

（2）试验得到的该涡轮叶寿命服从对数正态分布，经分析，确定的可靠性寿命为 $1 1 5 5 \mathrm { h }$ （置信度为 $9 5 \%$ ，可靠度为 $9 9 . 8 7 \%$ ），安全使用寿命为 $1 0 9 7 \mathrm { h }$

（3）这的寿命试验评定虽然是针对涡轮转叶进的，但其中的些观点和法对其他温构件（如涡轮盘、轴等）也有定的借鉴意义。

# 7.4 叶结构振动可靠性设计法

结构振动可靠性设计分析方法是以传统的结构振动设计方法为基础，利用应力一强度干涉理论，针对结构振动的特征，建激振力频率与结构固有频率干涉的概率模型和结构振动可靠性模型，给出导致构件损坏的强迫共振响应的概率表达式及其使条件。原则上，所发展的方法对其固有频率相对不太密集的构件更为适用，如航空叶轮机械中的叶片。

# 7.4.1 结构振动可靠性模型

结构的疲劳失效有相当部分是由其振动导致的，其中以强迫振动更为常见。传统的设计方法是使其振动应力小于构件的疲劳强度，若构件上的应力是非对称的，则要计及平均应力的影响，通常的做法是利用构件或材料的Goodman曲线进设计。例如，对于涡轮机械转叶，需要考虑质量离和体等引起的静应（亦即平均应力）的影响。为减小构件上的振动应力，则要求尽可能使构件在正常工作中避开危险的强迫共振。然而，在实际设计中完全避开共振是非常困难的，有时也是不可能的。通常的做法是避开较、较危险的共振。尽管如此，按传统法设计的构件却时常有失效现象发。对此，传统设计法很难做出合理的解释。

前，般认为可靠性设计能够对此给出合理的解释，并能给出构件的可靠性指标。因此，研究构件振动可靠性设计法以使其避开作条件下的较危险的强迫共振就显得分必要。虽然已有相当数量的关于机械可靠性的献发表，其中以阐述应强度干涉理论者居多，而一部分关于振动可靠性通常也是按该理论处理的，能够用于实际构件振动可靠性设计的则不多见。作者前期曾提出了一种进构件振动可靠性设计的法[14,25]，建了激振频率与构件固有频率涉的概率模型，给出了导致构件损坏的强迫共振响应的概率计算公式及其使条件。但是，其中没有考虑疲劳强度的分散性，现对结构振动可靠性设计分析法作进步的研究、发展和完善。

实际构件的几何形状、材料、制造工艺等均含有不确定因素，由此导致其疲劳强度和固有频率也具有不确定性；而外激振的幅值和频率在一定程度上也存在不确定性。两者将共同导致构件强迫振动响应的不确定性。这假设它们是相互独的随机变量。这种假设般认为是符合实际的，并使问题得到了简化。

（1）振动应力—疲劳强度干涉模型

仅考虑振动应随机性和构件疲劳强度的随机性，两者的概率密度函数分别记为$f _ { s }$ （s）和 $f _ { r }$ （r），应用应力一强度干涉理论，其可靠度为

$$
R \ = \ \int _ { - \infty } ^ { \infty } f _ { s } \left( s \right) \Big [ \int _ { s } ^ { \infty } f _ { r } \left( r \right) \mathrm { d } r \Big ] \mathrm { d } s
$$

(2）频率干涉模型

对于构件的某阶固有模态（或单由度系统），其稳态强迫振动响应的放因子为

$$
\beta = \frac { 1 } { \sqrt { ( 1 - \lambda ^ { 2 } ) ^ { 2 } + ( 2 \zeta \lambda ) ^ { 2 } } }
$$

式中： $\lambda$ − 频率比；

$\zeta$ id) 临界阻尼。

假设只有固有频率 $\omega$ 和激振力频率 $\omega _ { \mathrm { { e } } }$ 具有不确定性，且其概率密度函数分别为$g ( \omega )$ 和 $\varrho _ { \mathrm { e } } \left( \omega _ { \mathrm { e } } \right)$ ，则避开危险的强迫共振的可靠度 $R$ 定义为放大因子 $\beta$ 于某个给定值$\beta _ { \mathrm { G } }$ 的概率，其中 $\beta _ { \mathrm { G } }$ 由构件的Goodman曲线上的疲劳强度和激振力幅值确定。在给定 $\beta _ { \mathrm { G } }$ 和 $\zeta$ 的条件下，对应某一 $\omega _ { \mathrm { { e } } }$ ，当 $\omega _ { \mathrm { e l } } < \omega < \omega _ { \mathrm { e 2 } }$ 时，则有放因 $\beta$ 大于 $\beta _ { G }$ ，与此对应的概率值即为强迫振动的不可靠度 $F$ ，可以表达为

$$
F = P ( \omega _ { \mathrm { e l } } < \omega < \omega _ { \mathrm { e 2 } } ) = \int _ { - \infty } ^ { \infty } g _ { \mathrm { e } } ( \omega _ { \mathrm { e } } ) \biggl ( \int _ { \omega _ { \mathrm { e l } } } ^ { \omega _ { \mathrm { e 2 } } } g ( \omega ) \mathrm { d } \omega \biggr ) \mathrm { d } \omega _ { \mathrm { e } }
$$

式中： $\omega _ { \mathrm { e l } }$ 和 $\omega _ { \mathrm { e } 2 }$ 是依赖于 $\omega _ { \mathrm { { e } } }$ 的两个参数。

相应的可靠度为 $R = 1 - F$

由式（7-55）可以看出，由于此模型适合于固有频率和激振频率均为任意分布的情况，要求出其解析解通常是很困难的，故般宜采数值积分法求解，且在实际计算时，式（7-55）中的第一个积分号的上、下限不必取为无穷，应视其解有意义的具体情况而定。此外，本模型是根据单由度系统建的，原则上适合于模态不太密集的构件的任何阶模态的共振情况；对于模态密集的构件，则应视 $\omega _ { \mathrm { e l } }$ 和 $\omega _ { \mathrm { e } 2 }$ 的具体情形而定。

(3）振动可靠性模型

稳态强迫振动响应在构件上引起的振动应力 $s$ 与外激振力的幅值 $F _ { 0 }$ 和放大因子 $\beta$ 成正比，即 $s = k \beta { \cal F } _ { 0 }$ ，其中，系数 $k$ 对于给定的构件为常数，且与构件的何参数和材料参数有关。为了利用式（7-53）确定结构件的振动可靠度，需要先给出振动应力的概率密度函数 $f _ { s } ( s )$ ，般很难直接写出此概率密度函数的解析表达式，而可直接采数值法进计算。现对考虑外激振幅值的随机性和此随机性可以忽略的两种情况进行讨论。

$\textcircled{1}$ 对于外激振力幅值的随机性可以忽略的情形，例如，稳定状态下工作的涡轮机械叶可以认为符合这假设，利用式（7-55），振动应力的累积函数可以写为

$$
F _ { \mathrm { s } } ( s ) = 1 - P ( \omega _ { \mathrm { e l } } < \omega < \omega _ { \mathrm { e 2 } } ) = 1 - \int _ { - \infty } ^ { \infty } g _ { \mathrm { e } } ( \omega _ { \mathrm { e } } ) \Big ( \int _ { \omega _ { \mathrm { e l } } } ^ { \omega _ { \mathrm { e } 2 } } g ( \omega ) \mathrm { d } \omega \Big ) \mathrm { d } \omega _ { \mathrm { e } }
$$

式中： $\omega _ { \mathrm { e l } }$ 和 $\omega _ { \mathrm { e } 2 }$ 与 $s$ 是有关的，即给定个 $s$ ，就有个 $\beta _ { G }$ 与之对应。

$\textcircled{2}$ 当需要计外激振幅值的随机性时，例如，涡轮机械叶在某个转速带较宽的况下作就属于这种情况，记其概率密度函数为 $f _ { F _ { 0 } } ( F _ { 0 } )$ ，则振动应力的累积函数可以写为

$$
F _ { \mathrm { s } } ( \boldsymbol { s } ) \ = \ \int _ { - \infty } ^ { \infty } f _ { F _ { 0 } } ( F _ { 0 } ) \Big [ 1 \ - \int _ { - \infty } ^ { \infty } g _ { \mathrm { e } } ( \omega _ { \mathrm { e } } ) \Big ( \int _ { \omega _ { \mathrm { e } } 1 } ^ { \omega _ { \mathrm { e } 2 } } g ( \omega ) \mathrm { d } \omega \Big ) \mathrm { d } \omega _ { \mathrm { e } } \Big ] \mathrm { d } F _ { 0 }
$$

式中： $\omega _ { \mathrm { e l } }$ 和 $\omega _ { \mathrm { e } 2 }$ 是与 $s$ 和 $F _ { 0 }$ 有关的，即给定个 $s$ ，就有不同的 $F _ { 0 }$ 和与 $F _ { 0 }$ 相对应的一个 $\beta _ { \mathrm { c } }$

利用数值微分法可以分别求出上两式的导数，即 $f _ { s } \left( s \right)$ ，将其代入式（7-53），并进行数值积分便可以求出可靠度 $R$ 。需要说明的是，具体计算时，上述公式中积分的上、下限可用有实际意义的值替代正、负无穷。

应该指出的是，以上没有计及构件平均应力的影响，这主要是为了突出重点，当然也是为了使问题得到简化。此外，对于构件的疲劳强度和固有频率，以及外激振力的幅值和频率的概率密度函数的确定法参见参考献[25。

# （4）应用示例

实际使中，有许多按传统法（Goodman图）设计的本应“安全”的程结构却出现了振动疲劳失效，因而在设计中必须对其振动可靠性进评定。

现以某叶结构为例，设其给定阶模态的临界阻尼比 $\zeta = 0 . 0 1$ ，振动应力公式$s = k \beta { \cal F } _ { 0 }$ 中的 $k = 5 \mathrm { M P a } / \mathrm { N }$ ，激振力幅值 $F _ { 0 } = 2 \mathrm { N }$ ，激振力频率和固有模态频率的概率密度函数为三参数威布尔分布 $\mathbb { W } ( \omega _ { 0 } , \ \eta , \ m )$ 或正态分布 $N ( \omega _ { 0 } , \sigma )$ ，利用所提出的概率模型计算公式编制的计算机程序，计算得到考虑疲劳强度分散性（设其为正态分布$N$ $2 0 0 \mathrm { M P a } , 1 0 \mathrm { M P a } )$ ）和不考虑疲劳强度分散性（设其疲劳强度为 $2 0 0 \mathrm { M P a }$ ）情况下的不可靠度 $F$ ，见表7-31。为了考核所提出的方法和所发展的计算程序，对疲劳强度的不同概率分布情况进了计算，表7-32给出了疲劳强度为三参数威布尔分布和正态分布情况下的结构振动的不可靠度。

表7-31 疲劳强度分散性对结构振动不可靠度的影响  

<table><tr><td rowspan=1 colspan=2>频率分布</td><td rowspan=1 colspan=2>不可靠度F</td><td rowspan=1 colspan=2>频率分布</td><td rowspan=1 colspan=2>不可靠度F</td></tr><tr><td rowspan=1 colspan=1>激振频率</td><td rowspan=1 colspan=1>固有频率</td><td rowspan=1 colspan=1>N(200,0)</td><td rowspan=1 colspan=1>N(200,10)</td><td rowspan=1 colspan=1>激振频率</td><td rowspan=1 colspan=1>固有频率</td><td rowspan=1 colspan=1>N(200,0)</td><td rowspan=1 colspan=1>N(200,10)</td></tr><tr><td rowspan=1 colspan=1>N(520,10)</td><td rowspan=1 colspan=1>N(520,10)</td><td rowspan=1 colspan=1>0.600748</td><td rowspan=1 colspan=1>0.601530</td><td rowspan=1 colspan=1>N(500,10)</td><td rowspan=1 colspan=1>W(540,30,3)</td><td rowspan=1 colspan=1>0.000016</td><td rowspan=1 colspan=1>0.000017</td></tr><tr><td rowspan=1 colspan=1>N(520,10)</td><td rowspan=1 colspan=1>N(530,10)</td><td rowspan=1 colspan=1>0.504117</td><td rowspan=1 colspan=1>0.505182</td><td rowspan=1 colspan=1>N(520,10)</td><td rowspan=1 colspan=1>W(540,30,3)</td><td rowspan=1 colspan=1>0.006063</td><td rowspan=1 colspan=1>0.006214</td></tr><tr><td rowspan=1 colspan=1>N(520,10)</td><td rowspan=1 colspan=1>N（540,10）</td><td rowspan=1 colspan=1>0.285392</td><td rowspan=1 colspan=1>0.286680</td><td rowspan=1 colspan=1>N（540,10）</td><td rowspan=1 colspan=1>W（540,30,3)</td><td rowspan=1 colspan=1>0.162209</td><td rowspan=1 colspan=1>0.163413</td></tr><tr><td rowspan=1 colspan=1>N(520,10)</td><td rowspan=1 colspan=1>N(550,10)</td><td rowspan=1 colspan=1>0.107835</td><td rowspan=1 colspan=1>0.108766</td><td rowspan=1 colspan=1>W(540,30,3)</td><td rowspan=1 colspan=1>N（520,10)</td><td rowspan=1 colspan=1>0.005201</td><td rowspan=1 colspan=1>0.005313</td></tr><tr><td rowspan=1 colspan=1>N(520,10)</td><td rowspan=1 colspan=1>N(560,10)</td><td rowspan=1 colspan=1>0.026765</td><td rowspan=1 colspan=1>0.027158</td><td rowspan=1 colspan=1>W(540,30,3)</td><td rowspan=1 colspan=1>W(540,30,3)</td><td rowspan=1 colspan=1>0.648270</td><td rowspan=1 colspan=1>0.648953</td></tr><tr><td rowspan=1 colspan=1>N(520,10)</td><td rowspan=1 colspan=1>N（570,10)</td><td rowspan=1 colspan=1>0.004296</td><td rowspan=1 colspan=1>0.004393</td><td rowspan=1 colspan=1>W(520,30,3)</td><td rowspan=1 colspan=1>W(540,30,3)</td><td rowspan=1 colspan=1>0.303206</td><td rowspan=1 colspan=1>0.304570</td></tr></table>

表7-32 疲劳强度的不同概率分布对结构振动不可靠度的影响  

<table><tr><td rowspan=1 colspan=2>频率分布</td><td rowspan=1 colspan=2>不可靠度F</td><td rowspan=1 colspan=2>频率分布</td><td rowspan=1 colspan=2>不可靠度F</td></tr><tr><td rowspan=1 colspan=1>激振频率</td><td rowspan=1 colspan=1>固有频率</td><td rowspan=1 colspan=1>W(200,20,3)</td><td rowspan=1 colspan=1>N(200,20)</td><td rowspan=1 colspan=1>激振频率</td><td rowspan=1 colspan=1>固有频率</td><td rowspan=1 colspan=1>W(200,20,3)</td><td rowspan=1 colspan=1>N(200,20)</td></tr><tr><td rowspan=1 colspan=1>N(520,10)</td><td rowspan=1 colspan=1>N(520,10)</td><td rowspan=1 colspan=1>0.553060</td><td rowspan=1 colspan=1>0.603506</td><td rowspan=1 colspan=1>N(500,10)</td><td rowspan=1 colspan=1>W(540,30,3)</td><td rowspan=1 colspan=1>0.000171</td><td rowspan=1 colspan=1>0.000020</td></tr><tr><td rowspan=1 colspan=1>N(520,10)</td><td rowspan=1 colspan=1>N(530,10）</td><td rowspan=1 colspan=1>0.504117</td><td rowspan=1 colspan=1>0.507957</td><td rowspan=1 colspan=1>N(520,10）</td><td rowspan=1 colspan=1>W(540,30,3)</td><td rowspan=1 colspan=1>0.004567</td><td rowspan=1 colspan=1>0.006665</td></tr><tr><td rowspan=1 colspan=1>N(520,10)</td><td rowspan=1 colspan=1>N(540,10)</td><td rowspan=1 colspan=1>0.285392</td><td rowspan=1 colspan=1>0.290166</td><td rowspan=1 colspan=1>N(540,10)</td><td rowspan=1 colspan=1>W(540,30,3)</td><td rowspan=1 colspan=1>0.139487</td><td rowspan=1 colspan=1>0.166738</td></tr><tr><td rowspan=1 colspan=1>N(520,10)</td><td rowspan=1 colspan=1>N(550,10)</td><td rowspan=1 colspan=1>0.107835</td><td rowspan=1 colspan=1>0.111372</td><td rowspan=1 colspan=1>W(540,30,3)</td><td rowspan=1 colspan=1>N（520,10)</td><td rowspan=1 colspan=1>0.004070</td><td rowspan=1 colspan=1>0.005645</td></tr><tr><td rowspan=1 colspan=1>N(520,10)</td><td rowspan=1 colspan=1>N(560,10)</td><td rowspan=1 colspan=1>0.026765</td><td rowspan=1 colspan=1>0.028291</td><td rowspan=1 colspan=1>W（540,30,3)</td><td rowspan=1 colspan=1>W(540,30,3)</td><td rowspan=1 colspan=1>0.598602</td><td rowspan=1 colspan=1>0.650631</td></tr><tr><td rowspan=1 colspan=1>N(520,10)</td><td rowspan=1 colspan=1>N(570,10)</td><td rowspan=1 colspan=1>0.004296</td><td rowspan=1 colspan=1>0.004686</td><td rowspan=1 colspan=1>W（520,30,3)W(540,30,3）</td><td rowspan=1 colspan=1>W（520,30,3)W(540,30,3）</td><td rowspan=1 colspan=1>0.268842</td><td rowspan=1 colspan=1>0.308255</td></tr></table>

由表7-31和表7-32中可以看出：疲劳强度的分散性对结构振动的可靠度是有影响的。对于正态分布，随着分散性（标准差）的增加，可靠度下降（不可靠度增加）。同时，还可以看到本算例中疲劳强度分散性不（标准差仅为10MPa或 $2 0 \mathrm { M P a }$ )，因而对可靠度的影响也相对较小。

为了考察临界阻尼比和激振幅值的影响，在激振频率和固有频率均为正态分布N（520，10）情况下，当激振力幅值 $F _ { 0 }$ 由2N降为1N时，不可靠度由0.600748降为0.217341；当临界阻尼比 $\zeta$ 由0.01增至0.02时，不可靠度由0.600748降为0.418268。

此结果表明：激振幅值减或临界阻尼增加可以提结构振动的可靠度。

采用所提出的方法对一实际发动机带凸肩风扇叶（曾出现过振动故障）进了振动可靠性评估，得其可靠度为0.794009；对改进后的风扇叶片（在随后的试验中，未出现振动故障），评估得到其可靠度为 $1 . 0 0 0 0 0 0$ 。这程研制实例表明上述法是可行的。

这需要说明的是，常的Goodman图是针对限寿命设计（循环次数等于或超过 $1 0 ^ { 7 }$ ）而绘制的，因而基于此曲线计算得到的可靠度是对应限寿命的可靠度；当然利用基于有限循环次数绘制的Goodman曲线，通过上述法也可以确定有限寿命的可靠度。

以传统的结构振动设计方法为基础，建的结构振动可靠性模型，可以给出导致构件损坏的强迫共振响应的概率表达式及其使用条件。所提出的激振力频率与构件固有频率涉的概率模型不同于通常采的应强度涉模型。能从理论上更严格地回答避开较危险的强迫共振的概率，且其数值计算的实施也是可的。数值计算结果表明：疲劳强度的分散性对结构振动的可靠度是有影响的，即随着分散性的增加，可靠度下降；激振力幅值减小或临界阻尼比增加可以提结构振动的可靠度。原则上，本模型可用于对模态“不太密集”的结构进可靠性预测，对于模态密集的结构件的预测还有待于进一步深研究其不同模态响应间的相互作。

# 7.4.2 多参数具有分散性的叶结构振动可靠性模型

在上述只考虑固有频率 $\omega$ 和激振力频率 $\omega _ { \mathrm { { e } } }$ 分散性的基础上，当考虑结构的疲劳强度 $\sigma _ { - 1 }$ 的分散性时，若振动应力和疲劳强度的概率密度函数分别为 $f ( s )$ 和 $f ( \sigma _ { - 1 } )$ ，应用应强度涉理论，其可靠度可表示为

$$
R ( \sigma _ { - 1 } , s ) ~ = ~ \int _ { - \infty } ^ { \infty } f ( \sigma _ { - 1 } ) \Bigl ( \int _ { - \infty } ^ { \sigma _ { - 1 } } f ( s ) \mathrm { d } s \Bigr ) \mathrm { d } \sigma _ { - 1 }
$$

由稳态强迫振动响应在结构上引起的振动应力 $s$ 与外激振力幅值 $F _ { 0 }$ 和放大因子 $\beta$ 成正比，即 $\boldsymbol { s } = \boldsymbol { k } \beta \boldsymbol { F } _ { 0 }$ ，其中，系数 $k$ 对于给定的结构为常数，且与结构的几何参数和材料参数有关。

当考虑激振力幅值的分散性时，若其概率密度函数为 $f ( F _ { 0 } )$ ，则振动应力累积函数可以表示为

$$
F _ { \ast } ( s ) = \int _ { - \infty } ^ { \infty } f ( F _ { 0 } ) \Big [ 1 - \int _ { - \infty } ^ { \infty } g ( \omega _ { \mathrm { e } } ) \left( \int _ { \omega _ { \mathrm { e } } 1 } ^ { \omega _ { \mathrm { e } 2 } } g ( \omega ) \mathrm { d } \omega \right) \mathrm { d } \omega _ { \mathrm { e } } \Big ] \mathrm { d } F _ { 0 }
$$

式中： $\omega _ { \mathrm { e l } }$ 和 $\omega _ { \mathrm { e } 2 }$ 与 $s$ , $F _ { 0 }$ 和 $\omega _ { \mathrm { { e } } }$ 是有关的，即给定个 $s$ ，就有不同的 $F _ { 0 }$ 和与 $F _ { 0 }$ 相对应的一个 $\beta _ { \mathrm { c } }$ ；对于不同的 $\beta _ { \mathrm { G } }$ ，给定不同的 $\omega _ { \mathrm { { e } } }$ ，有不同的 $\omega _ { \mathrm { e l } }$ 和 $\omega _ { \mathrm { e } 2 }$ 与之对应[14]。

这样，对应的结构振动可靠度可表示为

$$
R ( \sigma _ { - 1 } , F _ { 0 } , \omega _ { \mathrm { e } } , \omega ) \ = \int _ { - \infty } ^ { \infty } f ( \sigma _ { - 1 } ) \Big \{ \int _ { - \infty } ^ { \infty } f ( F _ { 0 } ) \Big [ 1 - \int _ { - \infty } ^ { \infty } g ( \omega _ { \mathrm { e } } ) \Big ( \int _ { \omega _ { \mathrm { e } } ] } ^ { \omega _ { \mathrm { e } 2 } } g ( \omega ) \mathrm { d } \omega \Big ) \mathrm { d } \omega _ { \mathrm { e } } \Big ] \mathrm { d } F _ { 0 } ,
$$

式中： $\omega _ { \mathrm { e l } }$ 和 $\omega _ { \mathrm { e } 2 }$ 是 $\sigma _ { - 1 }$ , $F _ { 0 }$ 和 $\omega _ { \mathrm { { e } } }$ 的函数，即给定不同的 $\sigma _ { - 1 }$ 和 $F _ { 0 }$ ，有不同的 $\beta _ { \mathrm { c } }$ 与之对应；对于不同的 $\beta _ { \mathrm { c } }$ ，给定不同的 $\omega _ { \mathrm { { e } } }$ ，有不同的 $\omega _ { \mathrm { e l } }$ 和 $\omega _ { \mathrm { e } 2 }$ 与之对应。

可以看出，以上所建的结构振动可靠性模型是以振动应疲劳强度涉理论为基础的，即

$$
R ( \sigma _ { - 1 } , F _ { 0 } , \omega _ { \mathrm { e } } , \omega ) = P ( s < \sigma _ { - 1 } )
$$

其等价形式为

$$
R ( \sigma _ { - 1 } , F _ { 0 } , \omega _ { e } , \omega ) = P ( \beta < \beta _ { G } )
$$

式中： $\beta = 1 / \sqrt { ( 1 - \lambda ^ { 2 } ) ^ { 2 } + ( 2 \zeta \lambda ) ^ { 2 } }$ 是固有频率 $\omega$ 和激振力频率 $\omega _ { \mathrm { { e } } }$ 的函数（临界阻尼比 $\zeta$ 为定值）， $\beta _ { \mathrm { c } } = \sigma _ { - 1 } / ( k F _ { 0 } )$ 是激振力幅值 $F _ { 0 }$ 和疲劳强度 $\sigma _ { - 1 }$ 的函数（平均应力$\sigma _ { \mathrm { { m } } }$ 为0)。

在考虑上述参数分散性的基础上，将结构的临界阻尼 $\zeta$ 和平均应力 $\sigma _ { { \mathfrak { m } } }$ 两者的分散性引到结构振动可靠性模型，则结构振动可靠度可表示为

$$
R ( \sigma _ { \mathrm { { m } } } , \sigma _ { \mathrm { - 1 } } , F _ { 0 } , \zeta , \omega _ { \mathrm { { e } } } , \omega ) = P ( s < \sigma _ { \mathrm { { a } } } )
$$

式中： $\sigma _ { \mathrm { { a } } } = \sigma _ { \mathrm { { - 1 } } } ( 1 - \sigma _ { \mathrm { { m } } } / \sigma _ { \mathrm { { b } } } )$ 为由Goodman 曲线 $\sigma _ { \mathrm { ~ a ~ } } / \sigma _ { \mathrm { ~ - ~ } 1 } + \sigma _ { \mathrm { ~ m ~ } } / \sigma _ { \mathrm { ~ b ~ } } = 1$ 确定的疲劳强度幅值。

可靠度表达式的等价形式可表示为

$$
R ( \sigma _ { \mathrm { { m } } } , \sigma _ { \mathrm { - l } } , F _ { 0 } , \zeta , \omega _ { \mathrm { { e } } } , \omega ) = P ( \beta < \beta _ { \mathrm { G } } )
$$

式中： $\beta = 1 / \sqrt { ( 1 - \lambda ^ { 2 } ) ^ { 2 } + ( 2 \zeta \lambda ) ^ { 2 } }$ 是固有频率 $\omega$ 、激振力频率 $\omega _ { \mathrm { { e } } }$ 和临界阻尼 $\zeta$ 的函数, $\beta _ { \mathrm { G } } = \sigma _ { \mathrm { a } } / k F _ { 0 }$ 是激振力幅值 $F _ { 0 }$ 、疲劳强度 $\sigma _ { - 1 }$ 和平均应力 $\sigma _ { \mathfrak { m } }$ 的函数。

于是，当可靠性模型所涉及到的这些参数相互独立时，可以建立同时考虑包括临界阻尼比和平均应在内的6个参数带有分散性的结构振动可靠性模型

$$
\begin{array} { r l } { R ( \sigma _ { \mathrm { m } } , \sigma _ { - 1 } , F _ { 0 } , \zeta , \omega _ { \mathrm { e } } , \omega ) } & { = \displaystyle \int _ { - \infty } ^ { \infty } f ( \sigma _ { \mathrm { m } } ) \left\{ \int _ { - \infty } ^ { \infty } f ( \sigma _ { - 1 } ) \left\{ \int _ { - \infty } ^ { \infty } f ( F _ { 0 } ) \left\{ \int _ { - \infty } ^ { \infty } g ( \zeta ) \right. \right. } \\ & { \qquad \left. \left[ 1 \left. - \int _ { - \infty } ^ { \infty } g ( \omega _ { \mathrm { e } } ) \left( \int _ { \omega _ { \mathrm { e } } } ^ { \infty , 2 } g ( \omega ) \mathrm { d } \omega \right) \mathrm { d } \omega _ { \mathrm { e } } \right] \mathrm { d } \zeta \right\} \mathrm { d } F _ { 0 } \right\} \mathrm { d } \sigma _ { - 1 } \right\} \mathrm { d } \sigma _ { - 1 } } \end{array}
$$

式中： $\omega _ { \mathrm { e l } }$ , $\omega _ { \mathrm { e } 2 }$ 是 $\sigma _ { { \mathfrak { m } } }$ , $\sigma _ { - 1 }$ , $F _ { 0 }$ ; $\zeta$ 和 $\omega _ { \mathrm { { e } } }$ 的函数，即给定不同的 $\sigma _ { { \mathfrak { m } } }$ , $\sigma _ { - 1 }$ 和 $F _ { 0 }$ ,有不同的 $\beta _ { \mathrm { c } }$ 与之对应；对于不同的 $\beta _ { \mathrm { G } }$ ，给定不同的 $\zeta$ 和 $\omega _ { \mathrm { { e } } }$ ，有不同的 $\omega _ { \mathrm { e l } }$ 和 $\omega _ { e 2 }$ 与之对应。

需要说明的是：上述模型建立在各随机变量之间是相互独立的假设基础之上，通常实际结构可认为满此假设；模型适合于各随机变量均为任意（常见）分布的情况；模型中认为结构的平均应力 $\sigma _ { \mathrm { { m } } }$ 小于其静拉伸强度 $\sigma _ { \mathrm { { b } } } ( \sigma _ { \mathrm { { m } } }$ 与 $\sigma _ { \mathrm { ~ b ~ } }$ 不干涉，即 $\sigma _ { \mathrm { { m } } }$ 小于 $\sigma _ { \mathrm { ~ b ~ } }$ 的概率是1）；用正、负无穷作为积分限是为了表示积分运算是在相应随机变量的整个定义域内进的，实际计算中积分上、下限可有实际意义的值来代替正、负穷。

# 7.4.3 叶结构振动可靠性分析流程与数值算法的实现

具体到实际结构的振动可靠性分析，现给出其计算分析流程如下：

（1）通过试验或有限元分析，确定结构的固有频率 $\omega$ 和平均应力 $\sigma _ { { \mathrm { ~ m ~ } } }$ ，并根据其统计特性确定相应的概率密度函数；

(2）通过试验或相关经验，确定所考察模态的临界阻尼 $\boldsymbol { \zeta }$ 的概率密度函数；

（3）通过试验，由激振力的统计特性，分别确定激振力频率 $\omega _ { e }$ 和幅值 $F _ { 0 }$ 的概率密度函数，并确定结构振动应力表达式 $s = k \beta { \cal F } _ { 0 }$ 中的系数 $k$ ;

（4）由材料的疲劳试验或直接查阅材料数据册确定材料疲劳强度 $\sigma _ { - 1 }$ 的概率密度函数，由材料的静强度试验或直接查阅材料数据册确定材料的静拉伸强度 $\sigma _ { \mathrm { ~ b ~ } }$ ;

(5）可由本模型计算出结构振动可靠度 $R$ o

当然，上述流程的先后顺序可根据实际情况进调整；另外，这一过程通常是相当复杂的，但确是可实施的。针对上述结构振动可靠性模型，编制了数值计算程序。

# 7.7.4 叶结构振动可靠性评估示例

（1）示例一

某结构的固有频率 $\omega$ 分布形式为 $\ W ( 8 3 0 , ~ 1 0 , ~ 3 ) \mathrm { H z }$ ，激振频率 $\omega _ { \mathrm { { e } } }$ 分布形式为$N ( 8 3 0 , ~ 1 0 ^ { 2 } ) \mathrm { H z }$ ，所考察阶模态临界阻尼 $\zeta$ 分布形式为 $N ( 0 . 0 2 , \ 0 . 0 0 2 ^ { 2 } )$ ,激振力幅值 $F _ { 0 }$ 分布形式为 $N ( 2 . 0 , 0 . 2 ^ { 2 } ) \mathrm { N }$ ，疲劳强度 $\sigma _ { - 1 }$ 分布形式为 $N ( 3 0 0 , ~ 2 0 ^ { 2 } ) \mathrm { { M P a } }$ ，平均应力 $\sigma _ { { \mathrm { ~ m ~ } } }$ 分布形式为 $N ( 8 0 , \ 1 0 ^ { 2 } ) \mathrm { { M P a } }$ ，静拉伸强度 $\sigma _ { \mathrm { ~ b ~ } }$ 为 $7 5 0 \mathrm { M P a }$ ，振动应表达式中系数$k = 5 \mathrm { M P a } / \mathrm { N }$ 。此时，结构振动可靠度计算结果见表7-33，其中， $R _ { 1 }$ 为根据所提出模型编制的数值积分程序计算结果， $R _ { 2 }$ 为100000次蒙特卡罗仿真结果， $\Delta R = ( R _ { 1 } - R _ { 2 } ) / R _ { 2 }$ 为两者间的相对误差，各参数抽样直图如图7–48所。

表7-33示例一计算结果  

<table><tr><td rowspan=1 colspan=1>R_}</td><td rowspan=1 colspan=1>$^2}$</td><td rowspan=1 colspan=1>∆R/%</td></tr><tr><td rowspan=1 colspan=1>0.879719</td><td rowspan=1 colspan=1>0.879110</td><td rowspan=1 colspan=1>0.069275</td></tr></table>

![](images/2938ffa07c8693f2f2a17809ff64ee1f96b4c98e7f8cd190461499673d52e193.jpg)

![](images/e8ea585aaa4bb7875e653a53f8a19f083d8e0a21dcfa0860d578ac930a636c15.jpg)

![](images/2bfa4a4930757917205e885be26e767d7eab409e06613f0d9ce7c11d68af5b72.jpg)  
图7-48 示例中各参数抽样直图

由数值积分算法计算结果与蒙特卡罗仿真结果的对可以发现两者趋于致，相对误差仅为 $0 . 0 6 9 2 7 5 \%$ ，表明了所建模型的合理性和数值计算方法的可性。

# (2）示例二

以某实际航空发动机第二级风扇叶盘结构的某阶共振点（共振转速为$n = 9 4 3 5 \mathrm { r / m i n }$ ，频率为 ${ \boldsymbol { \mathscr { f } } } = 9 4 3 . 5 \mathrm { H z }$ ）为对象考察其振动可靠性。根据固有频率 $\omega$ 的统计特性得其分布形式为 $W ( 9 3 5 , ~ 1 0 , ~ 3 ) \mathrm { H z }$ ，激振力频率 $\omega _ { \mathrm { { e } } }$ 、临界阻尼 $\zeta$ 、激振力幅值$F _ { 0 }$ 、疲劳强度 $\sigma _ { - 1 }$ 和平均应力 $\sigma _ { \mathrm { { m } } }$ 均服从正态分布，振动应力表达式中系数 $k = 5 . 5 \mathrm { M P a } / \mathrm { N } ,$ 现考察参数服从表7-34中5种不同概率分布形式下的结构振动可靠性，计算结果如图 $7 - 4 9 \sim$ 图7-53所示。

表7-34 示例二中各参数分布形式  

<table><tr><td colspan="1" rowspan="1">项目</td><td colspan="1" rowspan="1">分布形式</td></tr><tr><td colspan="1" rowspan="1">1</td><td colspan="1" rowspan="1">=913.5~973.5Hz,ζ~N(0.01,0.0012),F0~N(2.0,0.152)N,σ−1~N(520，252)MPa，σm~N(100,102)MPa</td></tr><tr><td colspan="1" rowspan="1">2</td><td colspan="1" rowspan="1">=0.01，其余同示例一</td></tr><tr><td colspan="1" rowspan="1">3</td><td colspan="1" rowspan="1">F_ =2.0N，其余同示例一</td></tr><tr><td colspan="1" rowspan="1">4</td><td colspan="1" rowspan="1">σ−1 =520MPa，其余同示例一</td></tr><tr><td colspan="1" rowspan="1">5</td><td colspan="1" rowspan="1">σm=100MPa，其余同示例一</td></tr><tr><td colspan="2" rowspan="1">注：项目2~5中σ=10Hz</td></tr></table>

![](images/68e7ba279954d989d7c223d2045933b0db0bb87166deda08b162545d7223b0a1.jpg)  
图7–49 激振力频率不同概率分布对应的结构振动可靠度

![](images/7f5066862f06dab6403e781d65049d141bd635af3f6609161de5d8b50ea5aec2.jpg)  
图7-50 临界阻尼比不同概率分布对应的结构振动可靠度

![](images/d1ea36387ac2bb7d53b6bb88353a244a2aa642409078b7a2ad2c32cf486c4275.jpg)  
图7-51 激振幅值不同概率分布对应的结构振动可靠度

![](images/5be612c0896ea651fa03e415bc07a6a73857caf87371d84b51f8b82a2fffa394.jpg)  
图7-52 疲劳强度不同概率分布对应的结构振动可靠度

![](images/2beceedc9f77d3085e11455545187c2d3feece8e712a236a85d5481ae7675c59.jpg)  
图7-53 平均应不同概率分布对应的结构振动可靠度

计算结果表明：在给定的计算条件下，激振频率及其分散性对风扇叶盘结构所考察阶模态的振动可靠性影响较显著（见图7-49），这与传统意义上频率对振动响应重要性的认识相致；其他几个参数的分散性对其影响相对来说较（见图7-50\~图7-53)。导致参数分散性对可靠性影响较的原因可能是：参数服从正态分布且分散度（正态分布体现为标准差）较小。以平均应力为例，平均应力降低，可靠度增加；平均应力增加，可靠度降低，平均应力小于其均值引起可靠度增加的程度与平均应力大于其均值引起可靠度降低的程度相当，因而当平均应力均值不变，只改变其标准差时，可靠度无显著变化。临界阻尼比、激振力幅值和疲劳强度的影响同理。

研究发展的结构振动可靠性模型，结合相关参数的分散性，给出了结构振动可靠度计算的表达式与分析流程。例一表明，所发展模型的数值算法与蒙特卡罗仿真算法的计算结果趋于一致，表明该模型的合理性和数值算法的可行性。示例二以实际航空发动机第二级风扇叶盘结构的某阶共振点为对象，就各参数的分散性对可靠性的影响进行了分析，分析结果表明，在给定的计算条件下，激振力频率及其分散性对所考察阶模态的振动可靠性影响比较显著，其他几个参数的分散性对其影响相对来说较小。

# 参考文献

[1孔瑞莲.航空发动机可靠性工程[M]．北京：航空工业出版社，1996.

[3杨茂奎，任散．加表完整性对GH4169温合疲劳寿命的影响[J．航空精密制造技术，1996，32（6）：28-31.  
[4] Fochs H O, Stephens R I. Metal fatigue in engineering [M]. Willey Interscience Publi-cation, New York, 1980: 125–147.  
[5]柴正道，姚英．各种因素对滚动接触疲劳寿命的影响J．国内外内燃机车，1996（3）:6-13.  
[6]航空发动机设计册[M]．北京：航空业出版社，2000.  
[7] DEF STAN 00–971 General specification, for aircraft gas turbine engine [S]. 1987.  
[8苏清友，孔瑞莲，陈筱雄，等．航空涡喷、涡扇发动机主要零部件定寿指南M].北京：航空工业出版社，2004.  
[9傅惠民.疲劳强度概率分布[D]．北京：北京航空航天学，1986.  
[10徐平，段建，傅惠民，应变疲劳强度概率分布[J]．应学学报，1996，13（4）:95-101.  
[11]宋兆泓，陈光，张景武，等．航空发动机典型故障分析M]．北京：北京航空航天大学出版社，1993：128-129.  
[12] 叶永，斌．结构可靠度分析法探讨[J．云南发电，2004，20（1）：48–51,55.  
[13] 姚卫星．结构疲劳寿命分析[M]．北京：国防业出版社，2004.  
[14]王延荣，爱梅．结构振动可靠性设计法研究[J].航空动学报，2003，18（2）:191-194.  
[15]洪其麟.机械结构可靠性M]．北京：航空业出版社，1993.  
[16]徐军，郑颖．响应重构的若法研究及其在可靠度分析中的应[J．计算力学学报，2002，19（2）：217-221.  
[17] Wong F S. Slope reliability and response surface method [J]. Journal of Geo technicalEngineering. 1985, 111 (1）: 32–53.  
[18张弥，沈永清.响应法分析铁路明洞结构荷载效应[J．程学报，1993,26(2):58-66.  
[19] Iman R L, Conover W J. Small sample sensitivity analysis techniques for computer mod-els, with an application to risk assessment, communications in statistics [M]. Part A-Theory and Methods, 1980, A9 (17): 1749–1842.  
[20]北京航空材料研究所．航空发动机设计材料数据册[M．北京：国防业出版社.  
[21]王延荣，李宏新，袁善虎，等.考虑应梯度的缺疲劳寿命预测法[J]．航空动力学报，2013，28（6）：1208-1214.  
[22王延荣，李宏新，袁善虎，等.确定总应变寿命程参数的种法[J．航空动力学报，2014，29（4）：0881-0886.  
[23《中国航空材料册》编辑委员会.中国航空材料册：第2卷[M．北京：中国标准出版社，2001.

[24]王延荣.涡轮叶温低循环疲劳/蠕变寿命试验评定[J．航空动学报，2002,17（4）:407-411.

[25] 田爱梅，王延荣.构件振动可靠性设计法初探[J．航空动学报，1999，14（3）：320-322.

# 第8章 含缺陷粉末盘结构疲劳设计分析法

# 8.1引

粉末高温合由于其制造加工艺，缺陷难以避免[1]。因此，在粉末高温合中允许缺陷以一定的大小和聚集程度存在，但缺陷对粉末温合材料及结构的学性能、失效机理以及疲劳寿命有着极其重要的影响，甚至是决定性的作用，因而研究缺陷对粉末温合材料及结构局部应集中和疲劳寿命的影响，对粉末温合的实际程应用有重要意义。

粉末温合中的缺陷主要有两种：孔洞和夹杂物。孔洞体积较，但是数较多，由此引起的材料致密性变化对材料性能有很影响[2]。粉末温合中较为常见的夹杂物有两类，类是脆性的氧化物陶瓷夹杂，主要成分为Al、Si、Ca、 $\mathrm { M g }$ 、0等，以 $\mathrm { A l } _ { 2 } \mathrm { O } _ { 3 }$ 、 $\mathrm { S i O } _ { 2 }$ 最为常见，它们的尺寸从几百纳米到几百微米不等，危害性较大，是夹杂物研究的主要对象，此类夹杂物来源于母合熔炼及制粉过程，可能来自生产过程中到的些设备，也可能是由母合熔炼原料不纯、脱氧不良、原始粉末处理不当、受到环境污染等所致；另一类是塑性较好的属夹杂，其主要成分为Nb、Mo、W等，它们来源于制粉过程中粉末快速凝固时遗留下来的母合金中的熔点偏析物。

缺陷对材料及结构的疲劳性能有较大影响，大量基于缺陷的疲劳性能研究表明：缺陷的成分、形状、尺寸和位置会对低循环疲劳性能产不同程度的影响[3\~6]。对N18材料的断裂试样进断相扫描发现[7]：乎所有情况下，初始裂纹均源于冶缺陷，如陶瓷夹杂或疏松孔洞；在载荷平下，表面缺陷危害最大，大约 $70 \%$ 的裂纹在这里萌生；在低载荷水平下，较大的内部夹杂物是裂纹萌生的主要原因。参考文献[8，9研究了两种粉末温合中缺陷对裂纹萌的影响，并给出了裂纹由表萌转化为由内部萌的载荷临界值。Shamblen等[10]以混夹杂物的Rene95合为研究对象在 $5 3 8 \mathrm { { ‰} }$ 条件下进了应变控制的低循环疲劳试验，研究表明：尺寸相同时，表及近表夹杂物比内部夹杂物对材料低循环疲劳性能影响更，两种情况下的寿命数相差很，其原因可能是因为表面萌的裂纹暴露在空中，而内部萌的裂纹处在真空中，空环境加速了裂纹的扩展。参考献[11，12通过试验研究了FGH95粉末温合中夹杂物特性及其对材料低循环疲劳性能的影响，认为夹杂物的维尺寸及位置是影响轴向取样试样疲劳寿命的两个重要因素，夹杂物的二维尺寸越大，距试样表面越近，疲劳寿命越短。参考献13中运因次分析法，探讨了夹杂物位置 $d$ （夹杂物距合表面距离）、夹杂物维尺寸 $S$ 、无因次量 $d ^ { 2 } / S$ 与FGH95断裂循环数 $N _ { \mathrm { f } }$ 之间的关系为 $N _ { t } = f \ ( \ d ^ { 2 } / S )$ ，结果表明，出现在表和亚表面区域的夹杂物将严重影响合的断裂寿命。参考献[14]结合扫描电镜进原位拉伸及疲劳试验，观察了夹杂物的微观学为，特别是裂纹的萌、扩展以致断裂的过程，研究指出疲劳裂纹极易在夹杂物/基体界面以及夹杂物内部萌并向基体扩展，交变载荷单轴拉伸更容易促进裂纹的萌。

本章将从缺陷的类型、位置、缺陷与基体间的相对关系等面研究缺陷对粉末温合材料及结构局部应集中和疲劳寿命的影响，并发展相关的计算分析法，为粉末温合涡轮盘的寿命预测提供一条可借鉴的途径。

# 8.2 含缺陷结构有限元数值分析的何建模

结构中微缺陷问题通常简化为包含缺陷的代表性体积单元[15]进分析，考虑图8-1（a）所的试样包含个内部缺陷，相应的代表性体积单元如图8-1（b)所示。

![](images/931a9a4c8b27a6bb500d942e95a6d79f34687bd0582fe91f65d7ed690dfc4528.jpg)  
图8-1 缺陷计算模型

根据工程实际中粉末高温合金材料所含缺陷，数值分析建模的缺陷类型分为孔洞和夹杂物，缺陷的形状采用研究中常用的球形和椭球形以考虑缺陷形状对局部应力/应变的影响。另外，考虑到粉末温合中实际缺陷尺寸般在 $5 0 \sim 1 5 0 \mu \mathrm { m }$ ，本文选取球形缺陷的半径 $r = 5 0 \mu \mathrm { m }$ ，椭球形缺陷的半长轴 $a = 1 0 0 \mu \mathrm { m }$ ，短半轴 $b = 5 0 \mu \mathrm { m }$ 。研究表明，缺陷的二维尺寸和位置对材料疲劳寿命影响较大，因而此处定义无量纲参数以反映缺陷尺寸和位置对材料局部应力/应变的影响，对于球形缺陷定义无量纲参数 $d / r$ ,对于椭球形缺陷定义无量纲参数 $d / { \sqrt { a b } }$ ,其中 $d$ 为缺陷中心距材料表面的距离，不同缺陷及位置时的量纲参数值如图8-2所。

此外，当缺陷为夹杂物时，由于夹杂物与基体为两种不同材料，弹性模量不同，因而在构件加工制造过程中，很容易发生夹杂物与基体剥离，此时夹杂物与基体关系较为特殊，一方面夹杂物包含在基体中，另一方面两者又不是固连在一起，因而本章对此开展了相关研究。为了区分上述夹杂物和基体之间的关系，在有限元计算中，对夹杂物和基体固连的情况，采夹杂物有限元模型单元节点与基体有限元模型单元节点共节点的计算式，而对夹杂物和基体剥离的情况，采夹杂物有限元模型与基体有限元模型之间设定接触的计算方式。

![](images/f7478b174468059ea06ab16411e72b5c089d1e63032141c9e78e984c1d07efc0.jpg)  
图8-2 缺陷及其位置示意图

综上所述，针对粉末高温合金材料中缺陷的有限元计算条件见表8-1，需要说明的是，在计算模型中当 $d / r = 1$ 时，即缺陷处于材料表面之下且与表面相切时，此时切点处存在零厚度，即在 $d / r = 1$ 时不予取值。事实上，从数学方面看，缺陷正好处于 $d / r = 1$ 的概率为零，从物理方面看，粉末冶金工艺（热等静压）也使得缺陷不会正好处于 $d / r = 1$ 的位置，当然这也从另一个表明，对于粉末冶材料，热等静压艺的重要性。

表8-1 针对缺陷的有限元计算条件  

<table><tr><td rowspan=1 colspan=1>类型</td><td rowspan=1 colspan=1>形状</td><td rowspan=1 colspan=1>尺寸/mm</td><td rowspan=1 colspan=1>与基体关系</td><td rowspan=1 colspan=1>位置d/r</td></tr><tr><td rowspan=2 colspan=1>孔洞</td><td rowspan=1 colspan=1>球形</td><td rowspan=1 colspan=1>R =0.05</td><td rowspan=1 colspan=1></td><td rowspan=6 colspan=1>[−1,1),(1,10]</td></tr><tr><td rowspan=1 colspan=1>椭球形</td><td rowspan=1 colspan=1>a=0.1,b=0.05</td><td rowspan=1 colspan=1>一</td></tr><tr><td rowspan=4 colspan=1>夹杂</td><td rowspan=2 colspan=1>球形</td><td rowspan=2 colspan=1>R=0.05</td><td rowspan=1 colspan=1>共节点</td></tr><tr><td rowspan=1 colspan=1>接触</td></tr><tr><td rowspan=2 colspan=1>椭球形</td><td rowspan=2 colspan=1>a=0.1,b=0.05</td><td rowspan=1 colspan=1>共节点</td></tr><tr><td rowspan=1 colspan=1>接触</td></tr></table>

# 8.3 缺陷对局部应集中影响的数值模拟

基于前述对粉末温合中缺陷计算模型和计算条件的定义，本节以FGH97粉末温合为例，采数值法研究缺陷对粉末温合材料局部应集中的影响。计算中夹杂物材料选粉末温合材料中常见的夹杂物 $\mathrm { A l } _ { 2 } \mathrm { O } _ { 3 }$ ，计算所用FGH97合和$\mathrm { A l } _ { 2 } \mathrm { O } _ { 3 }$ 的材料参数见表8–2。

表8-2计算所用FGH97合金和 $\mathbf { A l } _ { 2 } \mathbf { O } _ { 3 }$ 材料参数  

<table><tr><td rowspan=1 colspan=1>材料</td><td rowspan=1 colspan=1>成分</td><td rowspan=1 colspan=1>弹性模量E/MPa</td><td rowspan=1 colspan=1>泊松比v</td></tr><tr><td rowspan=1 colspan=1>基体</td><td rowspan=1 colspan=1>FGH97</td><td rowspan=1 colspan=1>177290.6</td><td rowspan=1 colspan=1>0.331</td></tr><tr><td rowspan=1 colspan=1>夹杂</td><td rowspan=1 colspan=1>A1203</td><td rowspan=1 colspan=1>390000</td><td rowspan=1 colspan=1>0.25</td></tr></table>

根据代表性体积单元的对称性，取其1/4模型进弹性有限元计算分析，代表性体积单元边界施加拉伸载荷 $\sigma _ { \mathrm { { P } } } = 1 0 0 \mathrm { { M P a } }$ 。基于有限元计算结果，从缺陷的类型、位置及缺陷与基体相对关系等，进了缺陷对粉末温合局部应集中影响的分析。

# 8.3.1 缺陷类型对局部应力集中影响的数值模拟

众所周知，缺陷的存在使材料出现应/应变局部化，产明显应集中，并促使疲劳裂纹的萌生和扩展，然而不同的缺陷类型对材料局部应力/应变的影响是不同的，图8-3给出了球形孔洞和夹杂物局部区域拉伸向应分布，图8-4给出了缺陷附近沿缺陷外周角的应力分布曲线，其中缺陷为孔洞时，只选取基体有限元模型上的节点数据，而缺陷为夹杂物时，则分别选取了基体和夹杂物有限元模型上的节点数据，可以看出不同缺陷类型对材料局部应集中的影响。

![](images/710b0cc66ab4a1500d98bdc241c77b5e7c4e3c2f79482bfcdc79d3af2982c0b2.jpg)  
(a）孔洞

![](images/9eb00336340e87a0086f5773922618ca12cd86940132535dbeaacecc477437a2.jpg)  
（b）夹杂与基体固连

![](images/ebdb3a3cf8f030d5d07ccae7b7089f9a21f9dcc7077e498db7df004aaf181756.jpg)

![](images/bc940284ace3a6aed28d372137157e44fa60dbf8980834499d71ce21851d1e14.jpg)  
图8-3 不同类型缺陷周围的 $S _ { 1 1 }$ 应力分布 $\sigma _ { \mathrm { { p } } } = 1 0 0 \mathrm { { M P a } ) }$   
图8-4不同类型缺陷附近沿外周角的应力分布（ $\sigma _ { \mathrm { { p } } } = 1 0 0 \mathrm { { M P a } ) }$

首先，由于缺陷的存在，在缺陷附近产生了明显的局部高应力区，在基体上随着离缺陷距离的增加，应力快速下降至施加外载荷水平。

其次，孔洞和夹杂物两种缺陷导致的局部应力集中明显不同：孔洞导致的最大应力位于基体上，如图8-3（a）所示；本章中研究的夹杂物材料为 $\mathrm { A l } _ { 2 } \mathrm { O } _ { 3 }$ ，其弹性模量高于基体材料FGH97合，相对基体材料来讲，其为硬夹杂，因其产的最应位于夹杂物上，如图8-3（b）所。图8-4也表明夹杂物上应基本保持不变，且于基体上节点的应，同时也可以看出在夹杂物和基体交界上，由于材料不连续产了应的突变，这就导致了孔洞和夹杂物在循环载荷作下裂纹萌式的不同：对于孔洞，其裂纹可能萌于垂直于载荷向的孔洞边缘最应/应变处；对于夹杂物，则会有两种破坏可能性，即由应导致的夹杂物本开裂，以及夹杂物与基体的交界相对薄弱导致的夹杂物与基体界开裂。参考献[16通过扫描电镜原位拉伸和原位疲劳试验，跟踪观察了植 $\mathrm { A l } _ { 2 } \mathrm { O } _ { 3 }$ 夹杂物的镍基粉末温合Rene95中夹杂物导致的裂纹萌扩展乃至断裂过程，便观察到了上述两种现象。

最后，由前述分析可知，夹杂物与基体界面开裂也是材料破坏的一种式，因而进步讨论夹杂物与基体的关系对局部应集中的影响，图8-3（c）给出了夹杂物与基体剥离时夹杂物局部区域的应分布，可以看出，此时应分布明显不同于夹杂物与基体固连时的情况，图8-4更为详细直观地给出了这种不同，即当夹杂物与基体剥离之后，在拉伸载荷作下，夹杂物与基体之间存在个接触区域，导致夹杂物由固连时的受拉状态转变为受压状态，最应也因此从夹杂物转移到基体上，此时基体未与夹杂物接触的部分，其应力分布类似于缺陷为孔洞时的应力分布，但是基体与夹杂物接触部分，由于夹杂物的存在，使其应平低于相同条件下的孔洞附近应。

综上可见，不同缺陷类型及缺陷与基体的关系对缺陷附近区域材料的应集中产明显不同的影响，其中以孔洞导致的应集中程度最为严重，夹杂物与基体固连导致的应集中程度最，当夹杂物与基体剥离时，由于夹杂物的承压分担作，其导致的应集中程度低于缺陷为孔洞时导致的应集中程度。

# 8.3.2 缺陷形状对局部应力集中影响的数值模拟

本节选球形缺陷和椭球形缺陷就缺陷形状对局部应集中的影响展开讨论，图8-5给出了球形和椭球形孔洞附近区域拉伸向的应分布，图8-6给出了球形和椭球形夹杂物（夹杂物与基体固连）附近区域拉伸向的应分布，图8-7详细给出了球形和椭球形缺陷附近沿缺陷外周角的应力分布。

由图8-5\~图8-7可以看出，椭球形缺陷和球形缺陷对局部应的影响存在显著差别。对于孔洞缺陷，球形孔洞导致的应力集中程度相对较小，沿缺陷圆周向应力梯度较小，但是影响区域较大；椭球形孔洞导致的应力集中程度明显增大，且沿缺陷圆周向应下降较快，梯度较大，影响区相对球形缺陷较。对于夹杂物（夹杂物与基体固连）缺陷，其影响明显不同于孔洞，由图8-7可以看出，椭球形夹杂物上的应略低于球形夹杂物上的应平，这可能是由于椭球形夹杂物有效承载积增导致，但是椭球形夹杂物导致基体上的应影响区明显于球形夹杂物。

综上所述，椭球形孔洞导致的材料局部应力集中程度明显高于球形孔洞，且应力变化更为剧烈，而另一方面，椭球形夹杂物导致的材料局部应力集中程度与球形夹杂物相近，但是其影响区域明显增，因而椭球形缺陷与球形缺陷相对材料疲劳强度的影响可能要大。

![](images/b5637e6a87f8f469286bcd42465628e80a73251110e80ab6b12969a53a82bc59.jpg)  
图8-5 不同形状孔洞缺陷附近 $S _ { \mathrm { { m } } }$ 应力分布

![](images/0b0a70e664bb57516c52ee0c7156e5eb0f20189eff6baad3190be69a099c8861.jpg)  
图8-6 不同形状夹杂物缺陷附近 $S _ { \kappa }$ 应分布（夹杂物与基体固连）

![](images/b4f29aa42ecb9204cff11eac2591d51760bdfae746ec1ac747f32d5be30771da.jpg)  
图8-7 不同形状缺陷附近沿外周的 $S _ { 1 1 }$ 应力分布 $\sigma _ { \mathrm { { p } } } = 1 0 0 \mathrm { { M P a } ) }$ (d)

# 8.3.3 缺陷位置对局部应力集中影响的数值模拟

前述分析了缺陷在材料内部时其形状和类型对周围材料局部应力的影响，本小节将对不同相对位置的缺陷对局部应集中的影响进分析。为了便于描述，图8–8给出了较为泛采的表、亚表及内部缺陷位置定义的意图，图中同时给出了相应的本章前述所定义的无量纲参数 $d / r$ 值，可以看出：缺陷2和缺陷3即位于表面位置，也就是当 $- 1 < d / r < 1$ 时缺陷对应的位置，缺陷1和缺陷4为表面区域缺陷的极限位置；缺陷5位于亚表面位置，即 $1 \leqslant d / r \leqslant 2$ 时缺陷对应的位置，缺陷4和缺陷6为亚表面区域的极限位置；缺陷7和缺陷8为内部缺陷，对应于 $d / r > 2$ 时缺陷的位置。

![](images/e40ef1df3dc2ba6f63ebf77c252534f1db2c6fa1532d63fe774889e16b4fd0b1.jpg)  
图8-8 表面、亚表面及内部缺陷位置示意图

图8-9\~图8-11分别给出了球形孔洞、球形夹杂物与基体固连以及球形夹杂物与基体剥离三种条件下缺陷局部应力分布随缺陷位置的变化规律，与前述缺陷位于材料内部时应分布相，缺陷位于表和亚表位置时应分布有明显变化。由图8-9可以看出：当孔洞位于表面（ $- 1 < d / r < 1$ )时，由于孔洞未被材料全部包裹住，其应力分布呈现明显的不对称性，最大应力大致位于孔洞与材料表面交界处；当孔洞向内部移动到达亚表面（ $1 \leqslant d / r \leqslant 2$ )时，此时孔洞全部位于材料内部，但是由于距表面非常近，其应分布同样呈现明显的不对称性，孔洞与表面之间（外周 $- 9 0 ^ { \circ }$ 处）仅有很少材料承担载荷，因产了较的应集中；随着孔洞进步移动到材料内部( $d / r > 2$ ），其应逐步变为对称分布。图8–10表明了夹杂物与基体固连时与孔洞相似的变化趋势，随着夹杂物由表位置移动到内部，其最应位于夹杂物上，且其应分布同样是呈现明显的不对称性。图8-11中由于夹杂与基体已经剥离，因法计算夹杂物位于表面时的状态，只能给出夹杂物位于亚表位置时的应分布，同样可以看出其在亚表面位置时夹杂物与基体表之间的基体材料上有显著的应集中。

![](images/2c1d395b8b7de25983d77665bec29d2792c6eb01487780915c23b0bba82a036e.jpg)  
图8-9 球形孔洞位于不同位置时的应分布

![](images/ee56199a80a4729e63c94cf274d0eb5c73acee7b2c4db8259343290adb6ba1c6.jpg)  
图8-10 球形夹杂物位于不同位置时的应分布（夹杂物与基体固连）

为了更明确地量化不同相对位置的缺陷对局部应的影响，图8-12给出了缺陷导致的局部应力集中随缺陷位置的变化规律，可以更为直观地看出前述规律，即3种不同的缺陷导致不同程度的应力集中，其中孔洞导致的应力集中程度最为严重，其次是夹杂物与基体剥离条件下导致的应力集中，而夹杂物与基体固连时导致的应集中程度最小，这也表明，孔洞对材料而是最为危险的缺陷，当夹杂物与基体固连时，其危险性相对最，但是旦在循环载荷作下，夹杂物与基体剥离开来，缺陷局部应集中便会明显增大，促进裂纹的萌生。此外，对孔洞而言，随着孔洞从表面向亚表面移动，应力集中系数逐渐增大，且在 $d / r = 1$ 时达到最大值，而随着孔洞从亚表面向材料内部移动，应力集中系数则逐渐降低，当移动至亚表面极限位置时（ $d / r = 2$ ），应力集中系数开始趋于稳定，直至材料内部不再有明显的变化，这表明当孔洞在亚表面位置时对材料来说是最为危险的。然，对于夹杂物，论是夹杂物与基体固连还是夹杂物与基体剥离，其导致的应力集中系数都是随着 $d / r$ 的增而逐渐降低，即夹杂物越靠近表对材料越危险。

![](images/5f235a8850487f17542ede84d2d4cd344ac8ca39f6f3e8966639c98ffc154544.jpg)  
图8-11 球形夹杂物位于不同位置时的应分布（夹杂与基体剥离）

![](images/6b955e3bc21a77c9b028e1a5086d1bed0738eb540fe010c377637de0d554ba6a.jpg)  
图8-12 不同缺陷导致应集中随归化距离的变化

# 8.4 缺陷对疲劳裂纹萌生寿命影响

由于制造艺的特点，粉末温合的强度和寿命对缺陷分敏感，关于缺陷对材料疲劳寿命的影响主要存在两个问题：面是单个缺陷对材料局部裂纹萌产的影响，即确定性问题；另一方面是缺陷在材料内部的分布，这是存在随机性的概率问题，其中确定性分析是概率寿命预测的前提和基础。

本节主要从裂纹萌的度出发，基于已有的疲劳寿命预测方法，研究不同位置的缺陷对疲劳寿命的确定性影响。先基于FGH97合光滑试样和缺试样低循环疲劳试验，对考虑应集中影响的寿命预测法：局部应/应变法、泰勒（Taylor）临界距离法、体积法和考虑应梯度的缺口疲劳寿命预测法进了对比分析，然后选择合适的寿命预测法考察孔洞缺陷对粉末温合材料疲劳寿命的影响。

# 8.4.1 考虑应集中影响的寿命预测法对分析

（1）FGH97合光滑试样和缺试样低循环疲劳试验

FGH97合标准光滑试样低循环疲劳试验参照《属材料轴向等幅低循环疲劳试验法》（GB/T15248）和《属材料轴向加载疲劳试验法》（HB52781996）开展，试验条件如下：试验温度为 $7 0 0 \%$ ，轴向应变控制，应变比 $R = - 1$ ，0.1，载荷波形为三波，试验结果如图8-13所。基于FGH97合光滑试样低循环疲劳试验数据，拟合得到的 $7 0 0 \mathrm { { c } }$ 条件下FGH97合应变疲劳参数见表8-3，表中， $\sigma _ { \mathrm { ~ f ~ } } ^ { \prime }$ 为疲劳强度系数， $b$ 为疲劳强度指数， $\varepsilon _ { \uparrow } ^ { \prime }$ 为疲劳延性系数， $c$ 为疲劳延性指数， $E$ 为弹性模量，$K ^ { \prime }$ 为循环强度系数， $n ^ { \prime }$ 为循环应变硬化指数。

![](images/870608aa520ddb88660e6f91d931573ab6ef22d39c21799cdceff90c9b21be62.jpg)  
图8-13 FGH97合光滑试样对称及对称循环疲劳试验结果

表8-3 $7 0 0 \mathrm { ‰}$ 条件下FGH97合金应变疲劳参数  

<table><tr><td rowspan=1 colspan=1>参数</td><td rowspan=1 colspan=1>值</td><td rowspan=1 colspan=1>参数</td><td rowspan=1 colspan=1>值</td></tr><tr><td rowspan=1 colspan=1>σ/MPa</td><td rowspan=1 colspan=1>1597.388</td><td rowspan=1 colspan=1>E/MPa</td><td rowspan=1 colspan=1>177290.6</td></tr><tr><td rowspan=1 colspan=1>b</td><td rowspan=1 colspan=1>-0.07588</td><td rowspan=1 colspan=1>K/MPa</td><td rowspan=1 colspan=1>1937.04</td></tr><tr><td rowspan=1 colspan=1>εf}$</td><td rowspan=1 colspan=1>0.16927</td><td rowspan=1 colspan=1>n&#x27;</td><td rowspan=1 colspan=1>0.0955</td></tr><tr><td rowspan=1 colspan=1>C</td><td rowspan=1 colspan=1>-0.8123</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr></table>

FGH97合缺试样低循环疲劳试验采用半圆形和半椭圆形两种缺形式的单边缺试样，试样设计尺寸及缺口形式如图8-14所，图8-15给出了采弹性有限元计算得到的半圆形和半椭圆形缺平分线上的应分布，可以得到两种缺应集中系数分别为2.91和5.05。

![](images/bcb7747d02c21fea2fa18ac72f98d8cc15ee88fa71f0d4960452574889a1d0b9.jpg)  
图8-14 缺形式及缺试样尺寸（单位： $\mathrm { m m }$ )

FGH97合缺试样疲劳试验条件如下：试验温度为 $7 0 0 \mathrm { { ^ \circ C } }$ ，应力（载荷）控制，载荷比 $R = 0 , 1$ ，频率为 $0 . 3 3 3 \mathrm { H z }$ ，载荷波形为三波。FGH97合缺试样疲劳试验结果如图8-16所。可以看出：，随着净截应的增加，FGH97合缺试样疲劳寿命逐渐降低；另，应集中对FGH97合缺试样疲劳寿命有显著影响，相同净截应平条件下，半圆形缺试样的疲劳寿命明显于半椭圆形缺试样。

（2）局部应力/应变法

局部应力/应变法重点在于确定缺口件危险点的应力/应变历程，主要有两种应力/应变计算方式： $\textcircled{1}$ 弹塑性有限元分析。弹塑性有限元法较为准确，但需要构件材料的循环本构模型，同时循环弹塑性有限元分析有时计算量很，在程中难以实际应；$\textcircled{2}$ 近似分析法，如Neuber法等。近似分析法计算简单，在程中应泛。本节采程中常的Neuber法计算缺局部应/应变，并结合两种考虑平均应影响的寿命预测方法进行寿命预测。

![](images/884b4183113dd19fd6ba4fe156cc1affc8442b2e468dcc98f05c3a6b9f5f7125.jpg)  
图8-15 缺平分线上弹性应分布

![](images/0578d295d2838c9170a23b3effbae1766f29efc14a36effeae70960241d16b3d.jpg)  
图8-16 FGH97合缺口试样疲劳试验结果

采Neuber法进缺构件局部应/应变计算涉及的公式如下

$$
\sigma \varepsilon = \frac { K _ { \mathrm { t } } ^ { 2 } \left( \sigma _ { { \mathrm { n } } } \right) ^ { 2 } } { E }
$$

$$
\varepsilon = \frac { \sigma } { E } + \left( \frac { \sigma } { K ^ { \prime } } \right) ^ { \frac { 1 } { n ^ { \prime } } }
$$

$$
\Delta \sigma \Delta \varepsilon = \frac { K _ { \mathrm { t } } ^ { 2 } ( \Delta \sigma _ { \mathrm { n } } ) ^ { 2 } } { E }
$$

$$
\Delta \varepsilon = \frac { \Delta \sigma } { E } + 2 \left( \frac { \Delta \sigma } { 2 K ^ { \prime } } \right) ^ { \frac { 1 } { n ^ { \prime } } }
$$

式中： $\sigma$ —缺局部应；

$\varepsilon$ 缺口局部应变；   
$K _ { \mathfrak { r } }$ 缺口理论应力集中系数；   
$\sigma _ { \mathfrak { n } }$ (id:) 名义应力；   
$E$ 弹性模量；   
$K ^ { \prime }$ 循环强度系数；   
$n ^ { \prime }$ (−:) 循环应变硬化指数；   
$\Delta \sigma$ (id:) 缺口局部应力范围；   
$\Delta \varepsilon$ (id:) 缺口局部应变范围。

式（8-1）和式（8-2）用于确定局部危险点的最大应/应变，式（8-3）和式（8-4）用于确定局部危险点的应力/应变范围。

进行 $7 0 0 \%$ 条件下FGH97合缺试样寿命预测时，基于前述Neuber法计算得到局部应/应变，并可采SWT程和Morrow平均应修正的总应变寿命程进寿命预测，其寿命方程如下。

SWT方程

$$
\varepsilon _ { \mathrm { a } } \sigma _ { \mathrm { m a x } } \ = \frac { \sigma _ { \mathrm { f } } ^ { \prime 2 } } { E } \left( 2 N _ { \mathrm { f } } \right) ^ { 2 b } \ + \sigma _ { \mathrm { f } } ^ { \prime } \varepsilon _ { \mathrm { f } } ^ { \prime } \left( 2 N _ { \mathrm { f } } \right) ^ { b + c }
$$

$$
\varepsilon _ { \mathrm { a } } = \frac { \sigma _ { \mathrm { f } } ^ { \prime } } { E } \bigg ( 1 - \frac { \sigma _ { \mathrm { m } } } { \sigma _ { \mathrm { f } } ^ { \prime } } \bigg ) ( 2 N _ { \mathrm { f } } ) ^ { b } + \varepsilon _ { \mathrm { f } } ^ { \prime } ( 2 N _ { \mathrm { f } } ) ^ { c }
$$

式中： 危险点的应变幅；$\sigma _ { \mathrm { m a x } }$ 危险点最大应力；0m 平均应力；$N _ { \mathrm { f } }$ —疲劳寿命；$\sigma _ { \mathrm { ~ f ~ } } ^ { \prime }$ , $b$ , $\varepsilon _ { \mathrm { f } } ^ { \prime }$ , $c$ (id:) -应变疲劳参数；$E$ − 弹性模量。

基于局部应/应变法的FGH97合缺口试样预测寿命结果如图8-17所示。可以看出，采Neuber法计算的局部最应/应变结合SWT程和Morrow平均应修正的总应变寿命程的缺试样寿命预测结果过于保守，半圆形缺试样分散带在30倍左右，半椭圆形缺试样分散带超出了70倍，其主要原因在于仅考虑危险点点的应/应变，而没有考虑缺局部应梯度的影响，应梯度越，寿命预测的误差就越。因此，对于缺疲劳寿命预测需要考虑应梯度的影响。

(3）Taylor临界距离法

临界距离理论（theory ofcritical distance，TCD）最早由Neuber[17]和Peterson[18]分别提出，其后中（Tanaka）[19]、拉扎林（Lazzrin)[20]和Taylor[21]对这种思想进了研究和发展，使TCD得以泛使用，但该理论初期基本局限于循环疲劳寿命预测，后来苏斯梅尔（Susmel）和Taylor[23]将TCD推到了低循环疲劳寿命预测，使该理论得到进步发展。

TCD法的基本假设为：当沿缺口平分线到缺口尖端一定距离处的应超过相同条件下光滑试样的材料疲劳极限时，则缺口构件发疲劳破坏，此为TCD的点法；当沿缺口平分线距离缺尖端定长度内的平均应值超过相同条件下光滑试样的疲劳极限时，缺口构件失效，此为TCD的线法。两种方法分别表述如下。

![](images/25824c0e4f8b86150e3e7ac87cf290a5996f677edae9870403c61c6687248b1f.jpg)  
图8-17 局部应/应变法预测FGH97合缺疲劳寿命

点法

$$
\sigma _ { \mathrm { e f f } } = \sigma _ { 1 } \mid _ { r = D _ { \mathrm { P M } } } = \sigma _ { \mathrm { r e f } }
$$

线法

$$
\sigma _ { \mathrm { e f f } } ^ { } ~ = ~ \frac { 1 } { D _ { \mathrm { L M } } } \int _ { 0 } ^ { D _ { \mathrm { L M } } } \sigma _ { \mathrm { r } } ( r ) \mathrm { d } r ~ = ~ \sigma _ { \mathrm { r e f } }
$$

式中： $\sigma _ { 1 }$ 一般采用最大主应力， $\sigma _ { \mathrm { r e f } }$ 为相同条件下材料的疲劳强度， $D _ { \mathrm { P M } }$ 和 $D _ { \mathrm { { L M } } }$ 分别为点法和线法的临界距离值，具有长度量纲。对于高循环疲劳，临界距离的确定来源于短裂纹扩展[24]问题研究，先由下式计算得到特征距离 $L$

$$
L = \frac { 1 } { \pi } \bigg ( \frac { \Delta K _ { \mathrm { t h } } } { \Delta \sigma _ { 0 } } \bigg )
$$

式中： $\Delta K _ { * h }$ (id:) -应力强度因子范围的门槛值；

$\Delta \sigma _ { 0 }$ -材料强度极限。

对于点法，临界距离 $D _ { \mathrm { P M } } = L / 2$ ；对于线法，临界距离 $D _ { \mathrm { { L M } } } = 2 L$ id

由于上述临界距离是基于线弹性断裂学确定的，因TCD不适于缺局部塑性应/应变较的中低循环疲劳寿命预测问题。为了使TCD能在中低循环数疲劳寿命预测中有较好的预测精度，Susmel和Taylor提出了临界距离 $D$ 与疲劳寿命 $N _ { \mathrm { f } }$ 的函数关系，即

$$
D = A \cdot N _ { \mathrm { f } } ^ { B }
$$

式中，A和 $B$ 为材料参数，由试验数据拟合得到。Susmel在参考献[22中给出了两种确定A和 $B$ 的方法：一种是采用静态拉伸强度极限和疲劳极限确定，另种是采用光滑试样和缺试样的疲劳试验数据确定，并给出了缺构件寿命预测的迭代流程，如图8-18所。

后来，Susmel和Taylor将临界距离思想与传统的总应变程及SWT程结合，将TCD进步推应用到了基于弹塑性应变或基于应变能的低循环疲劳寿命预测中，其表达式分别为：

点法

$$
\varepsilon _ { \mathrm { a } } \sigma _ { \mathrm { m a x } } \mid _ { r = D _ { \mathrm { P M } } } = \frac { \sigma _ { \mathrm { f } } ^ { \prime 2 } } { E } ( 2 N _ { \mathrm { f } } ) ^ { 2 b } + \sigma _ { \mathrm { f } } ^ { \prime } \varepsilon _ { \mathrm { f } } ^ { \prime } ( 2 N _ { \mathrm { f } } ) ^ { b + c }
$$

![](images/b43cf0d1757db00e8b2ce111df57cc675f99e5351a7fe23ef29f4ee8d95558ac.jpg)  
图8-18 TCD法预测缺口构件寿命迭代流程

线法

$$
\frac { 1 } { D _ { \mathrm { t M } } } \int _ { 0 } ^ { D _ { \mathrm { t M } } } \varepsilon _ { \mathrm { a } } \sigma _ { \mathrm { m a x } } ( r ) \mathrm { d } r = \frac { \sigma _ { \mathrm { f } } ^ { \prime \ 2 } } { E } ( 2 N _ { \mathrm { f } } ) ^ { 2 b } + \sigma _ { \mathrm { f } } ^ { \prime } \varepsilon _ { \mathrm { f } } ^ { \prime } ( 2 N _ { \mathrm { f } } ) ^ { b + c }
$$

式中： $\varepsilon _ { \mathrm { a } } \sigma _ { \mathrm { m a x } } \left( r = D _ { \mathrm { P M } } \right)$ ——临界距离 $D _ { \mathrm { P M } }$ 处的SWT参数；

$\frac { 1 } { D _ { \mathrm { L M } } } \int _ { 0 } ^ { D _ { \mathrm { L M } } } \varepsilon _ { \mathrm { a } } \sigma _ { \mathrm { m a x } } \left( r \right) \mathrm { d } r$ -临界距离 $D _ { \scriptscriptstyle { \mathrm { L M } } }$ 上的平均SWT参数；

$N _ { f }$ (id:) 疲劳寿命；

$\sigma _ { \mathrm { ~ f ~ } } ^ { \prime }$ , $b$ , $\varepsilon _ { \mathrm { f } } ^ { \prime }$ , $c$ —应变疲劳参数；

$E$ 弹性模量。

临界距离 $D _ { \mathrm { P M } }$ 和 $D _ { \mathrm { { L M } } }$ 的确定式如前所述。

根据缺口试样不同指定寿命下的净截面名义应，通过有限元计算得到缺口平分线上应/应变分布及SWT参数 $\varepsilon _ { \mathrm { a } } \sigma _ { \mathrm { m a x } }$ 分布，采式（8-11）和式（8-12）可得指定寿命下的临界距离 $D _ { \mathrm { P M } }$ 和 $D _ { \mathrm { { L M } } }$ $7 0 0 \%$ 条件下FGH97合缺试样临界距离和疲劳寿命之间的关系如图8–19所示。可以看出：对于同缺类型试样，不同指定寿命条件下，其临界距离 $D _ { \mathrm { P M } }$ 和 $D _ { { \mathrm { L M } } }$ 是不同的；对于不同类型缺试样，相同指定寿命条件下，其临界距离 $D _ { \mathrm { P M } }$ 和 $D _ { { \mathrm { L M } } }$ 也是不同的。针对这现象，Susmel和Taylor建议使尖锐缺试样作为基准试样以拟合得到式（8-10）中临界距离 $D$ 与失效循环数 $N _ { \mathrm { f } }$ 的关系。此处，选尖锐缺试样即半椭圆形缺试样作为基准，拟合得到的点法和线法临界距离与失效循环数的关系如图8-19中所的实线和虚线，所得关系表达式如下

点法

$$
D _ { \mathrm { { P M , e } } } ~ = ~ 0 . 3 6 0 1 N _ { \mathrm { { f } } } ^ { - 0 . 0 5 2 2 4 }
$$

线法

$$
D _ { \mathrm { { L M , e } } } ~ = 1 . 0 3 2 9 6 N _ { \mathrm { { t } } } ^ { - 0 . 0 4 9 3 6 }
$$

采半椭圆形缺试样拟合得到的临界距离关系式结合图8-20所流程图便可开展缺试样疲劳寿命预测，预测结果如图8-21所。可以看出，由于两种缺试样的临界距离是有差别的，因以半椭圆形缺试样作为基准试样，使得半圆形缺试样寿命预测结果超出了3倍分散带。

![](images/ba8b953d0d3db11c4266faf5332cdafa51315cb996eac011c402dae92c8fb014.jpg)  
图8-19 FGH97合临界距离与指定寿命循环数之间的关系

![](images/f846a97880466e75aae2a62d3606cfe4e0b221cd6612cb7ec5483466b3e7bdf7.jpg)  
图8-20 采临界距离法进寿命预测的流程图

![](images/adb2540d4174219193cffe21e98c7d877953273ea41e91f05e598a321fe66a9f.jpg)  
图8-21 临界距离法预测FGH97合缺疲劳寿命结果（基准试样：半椭圆形缺试样)

(4）体积法

体积法[25\~27]作为临界距离理论中的种法，同样认为缺周围区域的应/应变对缺疲劳寿命产影响，其寿命预测流程如图8-22所，该法主要是通过缺根部的应力分布计算有效距离和有效应力以进疲劳寿命预测。

![](images/111722ef5257c84ec6222352b9fd8919e33813c98678a66330d4329661cb4196.jpg)  
图8-22 体积法寿命预测流程图

在确定有效距离时，体积法从缺口根部区域弹塑性应力分布的度出发，根据缺平分线上缺疲劳裂纹张开应的变化特征将缺根部区域划分为三个部分：$\textcircled{1}$ 区域Ⅰ包含峰值应； $\textcircled{2}$ 区域Ⅱ应在对数坐标系下呈线性变化； $\textcircled{3}$ 区域Ⅲ应分布呈幂函数变化。正是由于区域Ⅱ应变化趋势分类似于裂纹尖端的应变化[28]，因将区域Ⅱ的起始点作为临界距离的基准点，并且该点的位置可以通过相对应梯度的最值点来确定，缺局部弹塑性应分布及三个区域的划分如图8-23所示。

![](images/a7cc893001491979ae81096549e24aa920bbf653404cb7508f1c6b9be088fd4c.jpg)  
图8-23 缺口弹塑性应及应力梯度的变化趋势及分区

基于确定的有效距离，可通过下式确定缺口构件的有效应力

$$
\sigma _ { \mathrm { e f f } } = \frac { 1 } { X _ { \mathrm { e f f } } } \int _ { 0 } ^ { \chi _ { \mathrm { e f f } } } \sigma _ { y y } ( x ) \varphi ( x , \chi ) \mathrm { d } x
$$

$$
\varphi ( x , \chi ) = 1 - \mid \chi \mid r
$$

$$
\chi = \frac { 1 } { \sigma _ { { } _ { y y } } ( x ) } \ : \frac { \partial \sigma _ { { } _ { y y } } ( x ) } { \partial x }
$$

式中： eff (id:) 有效应力；

$X _ { \mathrm { e f f } } .$ —有效距离；  
$\sigma _ { _ { y y } } ( x )$ 缺口平分线上不同位置 $x$ 处的缺口疲劳裂纹张开应力；  
$\varphi ( x , \chi )$ —权函数，意在反映缺口平分线上不同位置处的应对缺构件疲劳失效的贡献程度，其与相对应力梯度有关；  
$r$ 距缺口根部危险点的距离；  
$\chi$ 相对应梯度。

为了便于相对应力梯度 $\chi$ 计算，对有限元计算得到的缺口平分线上的弹塑性应力$\sigma _ { 1 1 }$ （ $x$ ）采如下多项式进拟合

$$
\sigma _ { 1 1 } ( x ) = \sum _ { i = 0 } ^ { 9 } a _ { i } x ^ { i }
$$

则相对应力梯度可以表示为

$$
\chi = { \frac { 1 } { \sigma _ { 1 1 } ( x ) } } \cdot { \frac { \mathrm { d } \sigma _ { 1 1 } ( x ) } { \mathrm { d } x } } = { \frac { \displaystyle \sum _ { i = 1 } ^ { 9 } i a _ { i } x ^ { i - 1 } } { \displaystyle \sum _ { i = 0 } ^ { 9 } a _ { i } x ^ { i } } }
$$

进而，由式（8-15）和式（8-16）得试样有效应力

$$
\sigma _ { \mathrm { e f f } } ^ { } \ = \frac { 1 } { X _ { \mathrm { e f f } } } \int _ { 0 } ^ { X _ { \mathrm { e f f } } } \sigma _ { 1 1 } ^ { } \left( x \right) \varphi \left( x , \chi \right) \mathrm { d } x \ =
$$

$$
\frac { 1 } { X _ { _ { \mathrm { e f f } } } } \int _ { 0 } ^ { X _ { _ { \mathrm { e f f } } } } \big ( \sum _ { i = 0 } ^ { 9 } a _ { i } x ^ { i } \big ) \big ( 1 - | \chi | x \big ) \mathrm { d } x \ =
$$

$$
\frac { 1 } { X _ { \mathrm { e f f } } } \sum _ { i = 0 } ^ { 9 } \ \frac { a _ { i } X _ { \mathrm { e f f } } ^ { i + 1 } } { i + 1 } - \frac { 1 } { X _ { \mathrm { e f f } } } \int _ { 0 } ^ { x _ { \mathrm { e f f } } } \Big | \ \sum _ { i = 1 } ^ { 9 } i a _ { i } x ^ { i } \Big | \ \mathrm { d } x
$$

根据式（8-20），计算有效应力 $\sigma _ { \mathrm { e f f } }$ 先需要确定有效距离 $X _ { \mathrm { e f f } }$ ，由前述有效距离的确定式可知，有效距离取为相对应力梯度最小时的距离，该最值点对应于相对应梯度多项式阶导数为零的点。对相对应梯度多项式求导

$$
\frac { \mathrm { d } \chi } { \mathrm { d } x } = \frac { 1 } { \sigma _ { \mathrm { 1 1 } } \left( x \right) } \frac { \mathrm { d } ^ { 2 } \sigma _ { \mathrm { 1 1 } } \left( x \right) } { \mathrm { d } x ^ { 2 } } - \frac { 1 } { \left( \sigma _ { \mathrm { 1 1 } } \left( x \right) \right) ^ { 2 } } \left( \frac { \mathrm { d } \sigma _ { \mathrm { 1 1 } } \left( x \right) } { \mathrm { d } x } \right) ^ { 2 } =
$$

$$
\frac { \displaystyle \sum _ { i = 2 } ^ { 9 } i ( i - 1 ) a _ { i } x ^ { i - 2 } } { \displaystyle \sum _ { i = 0 } ^ { 9 } a _ { i } x ^ { i } } - \left( \frac { \displaystyle \sum _ { i = 1 } ^ { 9 } i a _ { i } x ^ { i - 1 } } { \displaystyle \sum _ { i = 0 } ^ { 9 } a _ { i } x ^ { i } } \right) ^ { 2 }
$$

令 $\frac { \mathrm { d } \chi } { \mathrm { d } x } = 0$ ，可求得有效距离 $X _ { \mathrm { e f f } }$ ，求得的净截应为 $6 9 0 \mathrm { M P a }$ 时FGH97合半圆形和半椭圆形缺试样的有效距离如图8-24所。

![](images/82dddec24783fb1b4779e2a975b23f9460a6fd1f6fa9b862e3d12facb9f114c6.jpg)  
图8-24 净截面应力 $6 9 0 \mathrm { M P a }$ 时FGH97合缺试样相对应梯度和有效距离

此外，式（8-20）中第项为对多项式绝对值的积分，需要考察 $\sum _ { i \mathop { = } 1 } ^ { \operatorname { \diamond } } i a _ { i } x ^ { i }$ 在有效9距离 $X _ { \mathrm { e f f } }$ 上的函数值。对于FGH97合半圆形和半椭圆形缺试样， $\sum _ { i \mathop { = } 1 } i a _ { i } x ^ { i }$ 在有效距离$X _ { \mathrm { e f f } }$ 上的函数值变化如图8-25所。

由图8-25可以看出，在有效距离内 $\sum _ { i = 1 } ^ { 9 } i a _ { i } x ^ { i }$ 存在个零点，积分时应基于此零点进分段积分。根据确定的零点值 $X _ { 0 }$ ，有效应力可写为

![](images/fa0425b7be766cf34bc6b2f5dabd65f416dc63bc31dff423114e175b1eadc6e4.jpg)  
图8-25 $\sum _ { i = 0 } i a _ { i } x ^ { i }$ 在有效距离 $X _ { \mathrm { e f f } }$ 上的函数值

$$
 \sigma _ { \mathrm { e f f } } ^ { \mathrm { } } ~ = \frac { 1 } { X _ { \mathrm { e f f } } ^ { \mathrm { } } } \sum _ { i = 0 } ^ { 9 } \frac { a _ { i } X _ { \mathrm { e f f } } ^ { i + 1 } } { i + 1 } - \frac { 1 } { X _ { \mathrm { e f f } } } \int _ { 0 } ^ { X _ { \mathrm { e f f } } } \Big | \sum _ { i = 1 } ^ { 9 } i a _ { i } x ^ { i } \Big | \mathrm { d } x ~ =
$$

$$
\frac { 1 } { X _ { \mathrm { e f f } } } \sum _ { i = 0 } ^ { 9 } \frac { a _ { i } X _ { \mathrm { e f f } } ^ { i + 1 } } { i + 1 } - \frac { 1 } { X _ { \mathrm { e f f } } } \int _ { 1 } ^ { X _ { 0 } } \sum _ { i = 0 } ^ { 9 } i a _ { i } x ^ { i } \mathrm { d } x + \frac { 1 } { X _ { \mathrm { e f f } } } \int _ { X _ { 0 } } ^ { X _ { \mathrm { e f f } } } \sum _ { i = 1 } ^ { 9 } i a _ { i } x ^ { i } \mathrm { d } x =
$$

$$
\frac { 1 } { X _ { \mathrm { e f f } } } \sum _ { i = 0 } ^ { 9 } \frac { a _ { i } X _ { \mathrm { e f f } } ^ { i + 1 } } { i + 1 } + \frac { 1 } { X _ { \mathrm { e f f } } } \sum _ { i = 1 } ^ { 9 } \frac { i a _ { i } X _ { \mathrm { e f f } } ^ { i + 1 } } { i + 1 } - \frac { 2 } { X _ { \mathrm { e f f } } } \sum _ { i = 1 } ^ { 9 } \frac { i a _ { i } X _ { 0 } ^ { i + 1 } } { i + 1 }
$$

通过上式确定的每种载荷条件下半圆形和半椭圆形缺口试样的有效应，以及图8-26所FGH97合光滑试样应 $R = 0 , 1$ 条件下的应力一寿命曲线，便可开展缺口试样疲劳寿命预测，预测结果如图8-27所示。可以看出体积法对缺口试样疲劳寿命预测在3倍分散带左右，与Taylor临界距离法接近，但是总体上该法预测结果较Taylor临界距离法偏于保守。

（5）考虑应梯度的缺口疲劳寿命预测法

考虑应梯度的缺疲劳寿命预测法[29]结合缺局部区域弹性应分析，综合考虑了平均应力、应力梯度和尺寸效应的影响，为缺口疲劳寿命预测提供了一种有效途径。下简要介绍此法在FGH97合缺试样寿命预测中的应。

$\textcircled{1}$ 平均应的影响

关于平均应对疲劳寿命的影响，普遍认为在循环载荷作用下平均应会显著增加或降低构件的裂纹萌寿命，因涌现出很多平均应修正的寿命模型，参考献[30对比了前泛使的考虑平均应影响的三种寿命预测模型，即Morrow平均应修正的总应变寿命程、SWT程及Walker平均应修正的寿命程，指出：Walker平均应修正模型含有可调项 $\gamma$ ，可以获得更高的寿命预测精度。因，考虑应梯度的缺疲劳寿命预测法在考虑平均应影响时采Walker平均应修正模型，其表达式为

![](images/2d03290110ba2c416fa949ee6f795f52f8f359a68a3e0720d952c4d32512a4f4.jpg)  
图8-26 FGH97合光滑试样应 $R = 0 , 1$ 时的应力—寿命曲线

![](images/76fc705c8baecc3e5c25c61458dab7b00dadde2d817c27545ee9f5cbc6eba0c0.jpg)  
图8-27 体积法预测FGH97合缺疲劳寿命

$$
\varepsilon _ { \mathrm { a } } = \frac { \sigma _ { \mathrm { f } } ^ { \prime } } { E } \left[ 2 N _ { \mathrm { f } } \left( \frac { 1 - R } { 2 } \right) ^ { ( 1 - \gamma ) / b } \right] ^ { b } + \varepsilon _ { \mathrm { f } } ^ { \prime } \left[ 2 N _ { \mathrm { f } } \left( \frac { 1 - R } { 2 } \right) ^ { ( 1 - \gamma ) / b } \right] ^ { c }
$$

式中： 危险点应变幅；

基于FGH97合对称和对称循环条件下光滑试样低循环疲劳试验数据，拟合得

到Walker参数 $\gamma = 0 . 4 4 5 8$

$\textcircled{2}$ 应力梯度的影响

考虑应梯度的缺疲劳寿命预测法在研究应分布变化规律时发现：当缺平分线上的应力和距离均归一化后，缺口根部归一化距离小于0.5时，不同应力集中系数的试样其缺平分线上的归一化应乎相同，据此提出了应梯度影响因Y，定义如下

$$
Y = \frac { 1 } { 2 S _ { 0 . 5 } }
$$

式中： $S _ { 0 . 5 }$ (i:) -应归化曲线与坐标轴在 $0 \leqslant x / r \leqslant 0 . 5$ 区间上围成的积。

采用该应梯度影响因对局部应/应变进修正以建缺试样与光滑试样的对应关系，得到的寿命修正程为

$$
\varepsilon _ { \mathrm { a } } = Y ^ { m } \biggl \{ \frac { \sigma _ { \mathrm { f } } ^ { \prime } } { E } \left[ 2 N _ { \mathrm { f } } \left( \frac { 1 - R ^ { \prime } } { 2 } \right) ^ { ( 1 - \gamma ) / b } \right] ^ { b } + \varepsilon _ { \mathrm { f } } ^ { \prime } \left[ 2 N _ { \mathrm { f } } \left( \frac { 1 - R ^ { \prime } } { 2 } \right) ^ { ( 1 - \gamma ) / b } \right] ^ { c } \biggr \}
$$

式中： $R ^ { \prime }$ 缺口局部应力比；

$m$ -应梯度影响指数，表征应梯度的影响程度。

通过对航空材料数据册中多种材料试验数据分析发现， $m$ 与试验寿命存在如下关系

$$
m \ = A \ ( 2 N _ { \mathrm { f } } ) ^ { B }
$$

式中：A $B$ (id 材料常数，可通过试验数据拟合得到。

对于FGH97合半圆形和半椭圆形缺试样，弹性应分析结果如图8-28所，缺平分线上归化应随归化距离的变化如图8-29所。基于此，得到FGH97合半圆形和半椭圆形缺口试样的应力梯度影响因子

$$
Y = \frac { 1 } { 2 S _ { 0 . 5 } } = \binom { 1 . 4 6 ( \# [ \Re ] ) / \xi , \# \pm \Pi } { 1 . 4 3 ( \# \# [ \Xi ] ) / \xi , \# \pm \Pi }
$$

![](images/9e94d818c20a549ace1981e72c07e1da31bef738fd53c3d338cb0a1678a8c3f9.jpg)  
图8-28 FGH97合半圆形和半椭圆形缺试样弹性应分布

取两者平均值得到FGH97合缺试样的应梯度影响因 $Y = 1 , 4 4$ o

应力梯度影响指数 $m$ 采FGH97合半圆形缺口试样试验数据拟合得到，将基于Neuber法得到的半圆形缺试样局部应/应变结果代式（8-25），得到应梯度影响指数 $m$ 值与半圆形缺试样反向数 $2 N _ { t }$ 的关系如图8-30所，其关系式如下

![](images/d1a9167d7d6e7ffcb03861f5a89f75dbf05b97320c85554b99e6794ad1b73dc5.jpg)  
图8-29 FGH97合半圆形和半椭圆形缺平分线归化应-归化距离

![](images/163a186260630d2b01c807ed5197dda71e793a182ce1adbd4b447f23e5424a7e.jpg)  
图8-30 应力梯度影响指数 $m$ 与反向数 $2 N _ { \mathrm { f } }$ 的关系

$$
m = 5 . 2 3 3 \ ( 2 N _ { \mathrm { f } } ) \ ^ { - 0 . 1 7 7 7 }
$$

$\textcircled{3}$ 尺寸效应的影响

处于非均匀应力场中的不同构件，即使危险点应力相同，但如果应力梯度分布不同，其疲劳破坏区域大小和疲劳寿命也不相同，这即是导致处于非均匀应力场的构件疲劳强度尺寸效应的重要原因，因而考虑应力梯度的寿命预测方法需要考察非均匀应力场带来的尺寸效应，并将其引寿命预测模型中。

考虑应力梯度的寿命预测方法通过考察缺口局部应力分布，发现：由于应力集中程度不同，导致其影响寿命的距离和梯度也不尽相同，因提出了引平均应梯度 $\boldsymbol { g } _ { \mathrm { c } }$ 来刻画尺寸效应的影响，其表达式如下

$$
\boldsymbol { g } _ { \mathrm { c } } = \frac { \boldsymbol { \sigma } _ { \mathrm { n o m } } \mid _ { \boldsymbol { x } = r / 2 } - \boldsymbol { \sigma } _ { \mathrm { n o m } } \mid _ { \boldsymbol { x } = 0 } } { r / 2 }
$$

此处选取缺口平分线上距离为 $r / 2$ 来定义平均应力梯度 ${ \boldsymbol { g } } _ { \mathrm { c } }$ 以确定尺寸影响因子 $C$ ,是因为当 $x \leqslant r / 2$ 时， $C$ 值变化很，较稳健；另是因为应梯度影响因中选取的归化距离为0.5，便于统。

此外，考虑到材料数据手册中通常给出应力集中系数 $K _ { \mathfrak { r } } = 3$ 的缺口试样的试验数据，因而以 $K _ { \mathrm { r } } = 3$ 缺口试样缺口处的平均应力梯度为参考来定义尺寸影响因子 $C$ ,其表达式如下

$$
C = { \frac { g _ { \mathrm { c } } } { g _ { 3 } } }
$$

将尺寸影响因子引到应梯度的影响中，和应力梯度共同对缺口局部应变进修正，最终得到综合考虑平均应、应梯度和尺寸效应影响的缺疲劳寿命预测模型为

$$
\varepsilon _ { \mathrm { a } } = Y ^ { m C \alpha } \bigg \{ \frac { \sigma _ { \mathrm { r } } ^ { \prime } } { E } \left[ 2 N _ { \mathrm { f } } \left( \frac { 1 - R ^ { \prime } } { 2 } \right) ^ { ( 1 - \gamma ) / b } \right] ^ { b } + \varepsilon _ { \mathrm { f } } ^ { \prime } \left[ 2 N _ { \mathrm { f } } \left( \frac { 1 - R ^ { \prime } } { 2 } \right) ^ { ( 1 - \gamma ) / b } \right] ^ { c } \bigg \}
$$

式中： $\alpha$ 尺寸效应影响指数，可通过试验数据拟合获得；

8 危险点应变幅；  
Y 应力梯度影响因子；  
$m$ 应力梯度影响指数；  
$C$ (id:) 尺寸影响因子；  
$\alpha$ bcid:) -尺寸效应影响指数；  
$\sigma _ { \mathrm { ~ f ~ } } ^ { \prime }$ , $b$ ; $\varepsilon _ { \mathrm { \uparrow } } ^ { \prime }$ , $c$ 应变疲劳参数；  
$E$ (i: 弹性模量；  
$N _ { \mathrm { f } }$ − 疲劳寿命；  
$R ^ { \prime }$ 危险点的局部应力比；  
γ- Walker指数。

至此，便构建了完整的考虑梯度影响的缺疲劳寿命预测模型。

对于FGH97合半圆形和半椭圆形缺试样，计算得到缺平分线上归化应随距离的变化如图8-31所。基于此，求得FGH97合缺试样尺寸影响因如下

$$
C = { \frac { g _ { \mathrm { c } } } { g _ { 3 } } } = { \frac { g _ { \mathrm { e l l i p t i c a l } } } { g _ { \mathrm { c i r c u l l a r } } } } = 1 . 9 8 3
$$

将FGH97合半椭圆形缺试样试验结果代式（8-31），求得各载荷条件下尺寸效应影响指数 $\alpha$ 值，取算数平均值得 $\alpha = 1 . 1 1 8$ o

$\textcircled{4}$ 缺疲劳寿命预测

将Neuber法计算得到的FGH97合缺口试样在不同净截应平下的局部应/应变以及局部应力比代式（8-31），寿命预测结果如图8-32所示，可以看出：采用考虑应力梯度的缺口疲劳寿命预测方程对缺口试样疲劳寿命预测结果较为理想，均在2倍分散带以内。

（6）寿命预测方法对比分析

本节在FGH97合光滑试样和缺试样疲劳试验的基础上，采局部应/应变法、Taylor临界距离法、体积法和考虑应力梯度的缺口疲劳寿命预测方法进了缺口疲劳寿命预测。

![](images/544ef0efc0e8254005549d82e12d0108af611cf7e1d42e5853641330f687934f.jpg)  
图8-31 FGH97合半圆形和半椭圆形缺试样缺平分线归化应分布

![](images/e43161567ac69c2c5723c017400d6f17fc5cbd7a6d6857b00481613861f1ed08.jpg)  
图8-32 FGH97合考虑应梯度的缺试样疲劳寿命预测

通过前述寿命预测结果可以看出：由于局部应力/应变法仅考虑危险点的应力/应变，忽略了危险点附近材料的贡献，其寿命预测结果过于保守；采Taylor临界距离法考虑了缺口根部定距离内应/应变的平均值，基本符合缺疲劳失效机理，但对不同缺试样指定寿命求得的临界距离结果表明，其临界距离与缺和载荷均相关，因仅以半椭圆形缺口试样为基准，预测寿命结果不甚理想；体积法同样考虑了缺局部区域内应力/应变场的影响，且基于相对应力梯度考虑了不同位置对缺口疲劳的贡献程度，物理意义明确，但是该法基于相对应梯度确定有效距离的式较为繁琐且难以于复杂实际结构件的疲劳寿命预测；而考虑应梯度的缺疲劳寿命预测法基于弹性计算结果，结合Neuber法综合考虑了缺局部平均应、应梯度和尺寸效应等的影响，寿命预测结果较为理想，该方法可为工程研制方案设计阶段的寿命预测提供有效手段和途径。

# 8.4.2 参考试样及寿命预测模型的选取

为了考察缺陷对FGH97合疲劳寿命的影响规律，先，需选取参考试样以作对比，选取的参考试样为光滑试样疲劳试验中的试样，试验结果见表8-4，即假定该试样为不含缺陷的光滑试样，在该试样中人为设置一从表面到内部不同位置的缺陷，在包含缺陷的有限元计算模型中即按该试样的试验条件进行计算。其次，需确定分析的缺陷类型，基于8.3节缺陷对局部应力集中的影响分析，选取对材料而相对较为危险的孔洞缺陷进研究。

表8-4 选作参考试样的光滑试样试验结果  

<table><tr><td rowspan=1 colspan=1>应变比</td><td rowspan=1 colspan=1>最大应变</td><td rowspan=1 colspan=1>应变范围</td><td rowspan=1 colspan=1>最大应力/MPa</td><td rowspan=1 colspan=1>应力范围/MPa</td><td rowspan=1 colspan=1>试验寿命</td></tr><tr><td rowspan=1 colspan=1>-1</td><td rowspan=1 colspan=1>0.005</td><td rowspan=1 colspan=1>0.01</td><td rowspan=1 colspan=1>840</td><td rowspan=1 colspan=1>1690</td><td rowspan=1 colspan=1>2358</td></tr></table>

选择疲劳寿命预测模型，面需要考虑到缺陷局部应集中的影响，另一面则是希望计算相对简单，以便于在实际程中采。基于以上两面的因素及前述考虑应力集中影响的寿命预测模型对比分析结果，选用考虑应力梯度的缺口疲劳寿命预测方法来进缺陷对粉末温合疲劳寿命的影响分析。

# 8.4.3不同位置及尺寸的球形孔洞对疲劳寿命的影响

依据前述考虑应力梯度影响的疲劳寿命预测方法的计算流程，对相同尺寸、不同位置的球形孔洞缺陷开展如下计算以分析缺陷位置对疲劳寿命的影响。

（1）局部应力/应变计算。将表8-4中光滑试样的载荷条件施加到在不同位置包含球形孔洞的有限元计算模型中，并采Neuber法计算不同位置球形孔洞局部应/应变和局部应。

（2）应力梯度影响因子计算。基于8.3节对球形孔洞缺陷的有限元分析结果，得到不同位置球形孔洞局部区域归化应与归一化距离的关系如图8-33所，进而可确定不同无量纲参数 $d / r$ 条件下的应力梯度影响因子Y。值得一提的是在无量纲参数 $d / r =$ 1.25时，由于危险部位尺寸较小，图8-33中相应曲线无法给出 $x / r = 0 . 5$ 时的值，因此只能给出相应尺寸处的 $S _ { 0 . 5 }$ 值。

（3）尺寸影响因计算。考虑应梯度的缺疲劳寿命预测法中需求得尺寸影响因子 $C$ 和尺寸效应影响指数 $\alpha$ 等参数值，参考献[31和[32中TC4合和GH4169合及前中FGH97材料相关值，此处取参考值 $C ^ { \alpha } = 1 . 9 5$

（4）含缺陷材料的寿命预测。基于8.4.1节确定的 $7 0 0 \%$ 条件下FGH97合考虑应梯度的缺疲劳寿命预测程中的参数、Neuber法计算不同位置球形孔洞局部应/应变和局部应力比、确定的不同无量纲参数 $d / r$ 条件下的应力梯度影响因子 $Y$ ，以及参考的 $C ^ { \alpha }$ 值，采用考虑应梯度的缺口疲劳寿命预测方法对含缺陷材料的寿命预测结果如图8-34所示。可以看出，由于缺陷的存在，材料的疲劳寿命显著降低，且随着孔洞缺陷从材料表向内部移动，其对材料疲劳寿命的影响分显著：当孔洞缺陷从表移动至亚表面位置，即无量纲参数 $d / r$ 从-1增1时，材料疲劳寿命迅速降低；当孔洞位于亚表面极限位置，即无量纲参数 $d / r = 1$ 时，此时的缺陷最为危险，其对材料疲劳寿命的影响也最；当孔洞从亚表逐渐移动到材料内部，即 $d / r > 1$ 时，试样的疲劳寿命逐渐增，其对寿命的影响逐渐减并趋于稳定。

![](images/9bed2124b485ee8b133a866928cdf18f6ef2c4dbab2fbcb76f2d693743de7cff.jpg)  
图8-33 不同位置球形孔洞附近区域归化应与归化距离的关系

![](images/badd260da9b3e73ced83f69b631f3c1dc9dec35b960c40fb0c31de2cd38e727f.jpg)  
图8-34 不同位置球形孔洞缺陷对材料疲劳寿命的影响

为了考察不同缺陷尺寸对材料疲劳寿命的影响，按照上述式计算了包含半径 $r =$ $0 . 5 \mathrm { m m }$ 球形孔洞缺陷的材料疲劳寿命，并与包含半径 $r = 0 . 0 5 \mathrm { m m }$ 缺陷的材料疲劳寿命进了对，如图8-35所。可以看出，缺陷尺对材料疲劳寿命的影响较为显著：随着缺陷尺寸的增，试样的疲劳寿命显著降低。从另个度来看，图8-35中对疲劳寿命影响最的区域对应于图8-8中缺陷位置 $d / r = 1$ 附近的区域，此处姑且称之为最危险区域，当缺陷尺越时，其对应的危险区域的体积所占总体积的例就越，缺陷位于最危险区域的概率就越，其对寿命的影响也就越。因此，论从确定性度还是概率分布度，尽可能降低缺陷尺寸对材料及结构的疲劳寿命都是有积极意义的。

![](images/ae8c04a5fe799411a5fb4ea451eb01de7b2f21cc1473f65a37a8e7440f819963.jpg)  
图8-35 不同尺寸缺陷对疲劳寿命的影响

上述采用考虑应力梯度的疲劳寿命预测方法就缺陷对疲劳寿命的影响进了比较分析，较好地表明了缺陷对材料疲劳寿命的影响规律，且与参考献[6在试验中观察到的影响规律具有较好的一致性，表明考虑应梯度影响的寿命预测法在考虑缺陷影响的疲劳寿命预测中也具有较好的适用性。但是值得提的是，本的研究是基于参考试样为不包含任何缺陷的“理想”光滑试样的假设进的，主要于研究缺陷在不同位置时的影响规律，实际试样或结构中是很难完全避免缺陷的，且缺陷也不是唯一的，因而后续还应考虑缺陷数量和尺寸大小等的分布规律，以便更进一步为实际应服务。

# 8.5 含缺陷结构的损伤容限分析法

损伤容限分析是评价结构件容忍类裂纹缺陷的能力，即在结构件上假定存在一初始裂纹长度的类裂纹缺陷的裂纹扩展寿命分析。损伤容限分析主要考虑的是要保证无损检测中未检测到的那些缺陷或裂纹不会扩展到临界裂纹尺寸。为了进结构损伤容限分析，需要应用断裂力学分析方法，本节在合理假设的基础上，基于FGH97合金裂纹扩展试验和缺口疲劳试验，建立缺口试样裂纹扩展计算模型，对缺口试样疲劳试验中记录的裂纹扩展结果进数值模拟，初步研究适合于粉末温合金材料裂纹扩展特性的分析方法以便为含缺陷粉末盘的损伤容限分析提供分析思路和段。

# 8.5.1FGH97合金裂纹扩展试验

参照《属材料疲劳裂纹扩展速率试验法》（GB/T63982000）、ASTME647-

1995a以及《属材料温疲劳裂纹扩展速率试验方法》（HB7680—2000）在 $6 0 0 \mathrm { { ^ \circ C } }$ 条件下开展了FGH97合裂纹扩展试验，试验采标准紧凑拉伸（CT）试样，应比为 $R = 0 , 1$ 和 $R = 0 , 5$ ，试样尺寸如图8-36所，试样厚度为 $1 0 \mathrm { m m }$

图8-37给出了试验测得的 $6 0 0 \mathrm { { ^ \circ C } }$ 条件下FGH97合裂纹扩展速率 $\mathrm { d } a / \mathrm { d } N$ 与应力强度因子范围 $\Delta K$ 的关系，可以看出，应力比对裂纹扩展速率产了显著影响，应比 $R = 0 , 5$ 时的裂纹扩展速率要明显低于应力比为 $R =$ 0.1时的裂纹扩展速率。

![](images/b68ef563512c26eb8552b0cae87618bd899f455aa597e746910657f812a79a25.jpg)  
图8-36 标准紧凑拉伸（CT）试样

![](images/0291e94953f5f3b3930c9c4c0f05bcc41ef1250341b18407cd55e18ebb02c77e.jpg)  
图8-37 FGH97合金ΔK-（ ${ \mathrm { d } } a / { \mathrm { d } } N )$ 关系

由裂纹扩展速率及应力强度因子范围，采用最小二乘法拟合得到材料的帕里斯(Paris）公式 $\mathrm { d } a / \mathrm { d } N = C \Delta K ^ { m }$ 中的常数 $C$ 和 $m$ 见表8-5

表8-5 FGH97合金Pairs公式中的常数  

<table><tr><td rowspan=1 colspan=1>温度/℃</td><td rowspan=1 colspan=1>应力比</td><td rowspan=1 colspan=1>最大载荷/kN</td><td rowspan=1 colspan=1>C</td><td rowspan=1 colspan=1>m</td></tr><tr><td rowspan=1 colspan=1>600</td><td rowspan=1 colspan=1>0.1</td><td rowspan=1 colspan=1>4.8</td><td rowspan=1 colspan=1>5.269×10-9</td><td rowspan=1 colspan=1>3.31</td></tr><tr><td rowspan=1 colspan=1>600</td><td rowspan=1 colspan=1>0.5</td><td rowspan=1 colspan=1>8</td><td rowspan=1 colspan=1>2.348×10-9</td><td rowspan=1 colspan=1>3.17</td></tr></table>

Paris公式虽然能够较好地模拟裂纹扩展规律，但其不能反映平均应的影响，而由图8-37可以看出，应力比对裂纹扩展速率的影响十分明显，工程中普遍应用的是考虑平均应影响的Walker公式[33]如下

$$
\frac { \mathrm { d } a } { \mathrm { d } N } = C \left[ \left( 1 - R \right) ^ { M - 1 } \Delta K \right] ^ { n }
$$

式中： $R$ 为应力比； $C$ , $M$ , $n$ 为材料参数，由试验数据拟合得到。

采用最小二乘法对 $6 0 0 \%$ 条件下FGH97合裂纹扩展试验数据进拟合（如图8-38所示），得到Walker方程参数为： $C = 8 . 0 6 7 \times 1 0 ^ { - 9 }$ , $M = 1 .$ 6844, $n = 3 . 2 4 9 7$

![](images/9e3f82cf61cb8b4f08ed09cf9f126080c76fc4eb8c914cf33613551cb6627481.jpg)  
图8-38 考虑应比影响的裂纹扩展（Walker公式）

# 8.5.2 FGH97合金缺口试样裂纹扩展分析

本节选取前述净截面应力为690MPa和 $7 5 0 \mathrm { M P a }$ 条件下的半圆形缺口试样疲劳试验中观察到的缺试样裂纹扩展数据，两个缺试样裂纹扩展试验结果如图8-39所。为避免缺口塑性对裂纹扩展的影响，此处选取裂纹长度从 $0 . 3 \mathrm { m m }$ 扩展至 $1 . 1 \mathrm { m m }$ 的阶段进数值模拟，由图8-39可知，当裂纹长度为 $0 . 3 \mathrm { m m }$ 时，净截面应力为 $6 9 0 \mathrm { M P a }$ 的半圆形缺口试样寿命约为2950个循环，净截应为 $7 5 0 \mathrm { M P a }$ 的半圆形缺试样寿命约为5080个循环；而当裂纹长度为 $1 . 1 \mathrm { m m }$ 时，净截面应力为 $6 9 0 \mathrm { M P a }$ 的半圆形缺口试样寿命大约为3400个循环，净截面应力为 $7 5 0 \mathrm { M P a }$ 的半圆形缺口试样寿命大约为5400个循环。因而，当裂纹从 $0 . 3 \mathrm { m m }$ 扩展至 $1 . 1 \mathrm { m m }$ 时，净截面应力为 $6 9 0 \mathrm { M P a }$ 的半圆形缺试样的裂纹扩展寿命约为450个循环，净截应为 $7 5 0 \mathrm { { M P a } }$ 的半圆形缺口试样的裂纹扩展寿命约为320个循环。

![](images/317c094a3cac226764ec6e4dba0786066d5649f5b34ee579839f0706f7ba9833.jpg)  
图8-39净截面应力为690MPa和 $7 5 0 \mathrm { { M P a } }$ 时圆形缺口试样疲劳裂纹扩展数据

根据缺口试样的尺寸及裂纹长度建缺口试样裂纹扩展计算有限元模型，如图8-40所。计算时对裂纹尖端网格进了局部细化，分别定义裂纹长度 $a = 0 . 3 \mathrm { { m m } }$ , $0 . 4 \mathrm { m m }$ , $0 . 5 \mathrm { m m }$ , $0 . 7 \mathrm { m m }$ , $0 . 9 \mathrm { m m }$ $1 , 2 \mathrm { m m }$ 的6个裂纹尖端，并假设裂纹前缘为直线，计算所得净截面应力 $6 9 0 \mathrm { M P a }$ 和 $7 5 0 \mathrm { M P a }$ 条件下不同裂纹长度时的应力强度因子范围沿试样厚度方向的变化规律如图8-41所示。

由图8-41可以看出，裂纹尖端应强度因沿试样厚度向是变化的，靠近两侧表面应强度因稍低，而靠近中间时应强度因分布均匀但相对两侧稍。裂纹扩展时裂纹前缘应当与应强度因子的变化趋势相近，这种趋势表明两侧表面裂纹扩展速度稍低于中间段，即裂纹前缘应当呈“凸”字形，图8-42给出了净截面应为 $7 5 0 \mathrm { M P a }$ 时半圆形缺口试样断形貌，表明计算结果趋势与裂纹扩展区前缘较为致，这虽然与计算时假设裂纹前缘为直线不太相符，但是由于缺口试样厚度相对较薄，其裂纹前缘扩展相对较为均匀，为了便于计算，此处仍采用假设裂纹前缘为直线。此外，由于试验中记录的裂纹扩展数据均是从试样侧面观测获得，因而后续采用计算得到的侧面的应力强度因子范围进裂纹扩展寿命计算。

![](images/e0bd82643be3fecc678ca586f777d399730d3e07348b27172e0f403c983afed4.jpg)  
图8-40 半圆形缺试样裂纹扩展有限元模型

此处，计算FGH97合缺试样裂纹扩展寿命采考虑平均应影响的Walker公式，并结合参考文献[34]的方法，获得 $\Delta K - a$ 之间的关系，然后通过积分求出裂纹扩展寿命，即

![](images/c61408d41f07b972e48910ba8312c889a1fbec68ea36e0ed87e1262f45371cea.jpg)  
图8-41 不同裂纹长度时的应强度因沿试样厚度向的变化

![](images/426adae8a61dd84d829c338dc453206deafd3a306d2cd0a4a587548bd152c37b.jpg)  
图8-42 净截面应为 $7 5 0 \mathrm { M P a }$ 时半圆形缺试样疲劳断

$$
N = \int _ { a _ { 0 } } ^ { a _ { \mathrm { f } } } \frac { \mathrm { d } a } { C [ \left( 1 - R \right) ^ { M - 1 } \Delta K ] ^ { n } } = \int _ { a _ { 0 } } ^ { a _ { \mathrm { f } } } \frac { \mathrm { d } a } { C [ \left( 1 - R \right) ^ { M - 1 } f ( a ) ] ^ { n } }
$$

式中： $C$ , $M$ , $n$ (id:) Walker裂纹扩展公式中的参数；

$a _ { 0 }$ 初始裂纹长度；  
a 最终裂纹长度；  
$f ( a )$ -应力强度因子范围 $\Delta K$ 与裂纹长度 $a$ 的函数关系。

基于前文计算得到的不同裂纹长度时的应力强度因子范围，对不同裂纹长度下靠近试样侧面的应强度因子范围采用次多项式拟合，表达式如下

$$
\Delta K = f ( a ) = B _ { 1 } + B _ { 2 } a + B _ { 3 } a ^ { 2 }
$$

式中： $B _ { 1 }$ , $B _ { 2 }$ , $B _ { 3 }$ 通过试验数据拟合得到。

基于FGH97合应强度因范围和裂纹长度的关系，拟合结果如图8-43所示。

![](images/4d4ec75d1336389ff1705237d20f9302590d8c832c358d116c857b444aae8422.jpg)  
图8-43 净截应690MPa和 $7 5 0 \mathrm { { M P a } }$ 下缺口试样应力强度因子范围与裂纹长度之间的关系

将拟合结果代式（8-34），结合前述FGH97合Walker程参数计算出半圆形缺口试样分别在净截面应力为 $6 9 0 \mathrm { M P a }$ 和 $7 5 0 \mathrm { { M P a } }$ 条件下裂纹从 $0 . 3 \mathrm { m m }$ 扩展到 $1 . 1 \mathrm { m m }$ 时的循环数见表8-6，可以看出计算结果与试验结果分接近，这表明：对于含缺陷粉末盘的损伤容限分析，本节计算方法是一条可行的途径。

表8-6半圆形缺口试样裂纹从 $\mathbf { 0 . 3 m m }$ 扩展至 $1 . 1 \mathrm { m m }$ 时寿命数值模拟结果  

<table><tr><td rowspan=1 colspan=1>净截面应力/MPa</td><td rowspan=1 colspan=1>试验寿命</td><td rowspan=1 colspan=1>计算寿命</td></tr><tr><td rowspan=1 colspan=1>690</td><td rowspan=1 colspan=1>450</td><td rowspan=1 colspan=1>431</td></tr><tr><td rowspan=1 colspan=1>750</td><td rowspan=1 colspan=1>320</td><td rowspan=1 colspan=1>317</td></tr></table>

# 8.6 含缺陷FGH97粉末盘寿命预测

# 8.6.1FGH97粉末盘应力/应变分析

要准确分析涡轮盘失效机制和预测涡轮盘寿命，先需要开展涡轮盘的应/应变分析以明确涡轮盘的危险部位。本节选的FGH97粉末盘有限元模型如图8-44所示，选取整体模型的1/72扇区，计算采用八节点实体六面体单元。

涡轮盘承受的载荷主要有离载荷和热负荷，离由轮盘和叶旋转时引起，热应则是轮盘作时温度分布不均匀导致的，根据轮盘实际作状态，有限元模型施加边界条件见表8-7，值得提的是，此处将叶旋转引起的离载荷转化为均匀载荷作在榫齿与榫槽的接触面上。

![](images/353f0c2403fb0b7ff31e64487b7a2877cea0c843f0ad58d0fe8c5df1a07fbd82.jpg)  
图8-44 FGH97粉末盘有限元模型

表8-7 计算模型的边界条件  

<table><tr><td rowspan=1 colspan=1>边界条件</td><td rowspan=1 colspan=1>位置</td><td rowspan=1 colspan=1>作用</td></tr><tr><td rowspan=1 colspan=1>位移边界条件</td><td rowspan=1 colspan=1>相应安装部位</td><td rowspan=1 colspan=1>用以约束轮盘周向、轴向位移</td></tr><tr><td rowspan=1 colspan=1>循环对称条件</td><td rowspan=1 colspan=1>轮盘两侧子午面</td><td rowspan=1 colspan=1>反映轮盘的对称特性</td></tr><tr><td rowspan=1 colspan=1>离心力载荷</td><td rowspan=1 colspan=1>轮盘所有单元</td><td rowspan=1 colspan=1>反映轮盘旋转产的离场</td></tr><tr><td rowspan=1 colspan=1>温度载荷</td><td rowspan=1 colspan=1>轮盘所有单元</td><td rowspan=1 colspan=1>反映轮盘作状态的温度状况</td></tr><tr><td rowspan=1 colspan=1>榫槽压力</td><td rowspan=1 colspan=1>榫齿与榫槽接触面</td><td rowspan=1 colspan=1>反映由叶离心力产生的压应力</td></tr></table>

采用上述有限元模型及边界条件在有限元软件中计算得到FGH97涡轮盘温度场和应分布，如图8-45和图8-46所示。

![](images/cc027ee1e8a73014fe1d81e0ed34c2e16b20c8496519625f4c8977a63a1b1d20.jpg)  
图8-45 FGH97合涡轮盘温度分布

由图8-46（a）可以看出，轮盘最大等效应位于盘处，其值为 $1 2 7 8 \mathrm { M P a }$ ，辐板与轮缘交接处应力也较大，其值为 $1 2 0 9 \mathrm { M P a }$ ；图8-46（b）表明最主应位于辐板与轮缘交接处，其值为 $1 4 3 2 \mathrm { M P a }$ ；图8-46（c）表明最大径向应位于轮缘与辐板交接处，而图8-46（d）表明最周向应位于盘处。基于此，确定轮盘考核点的应特征值见表8–8。

![](images/9ccd82da4b1ee42855075a8c234de1da12afc53620295d534c2106c07c098c73.jpg)  
图8-46 FGH97合涡轮盘应分布

表8-8轮盘考核点应力  

<table><tr><td rowspan=1 colspan=1>序号</td><td rowspan=1 colspan=1>部位</td><td rowspan=1 colspan=1>应力/MPa</td></tr><tr><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>盘心处</td><td rowspan=1 colspan=1>957.8（周向应力）</td></tr><tr><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>轮缘与辐板交接处</td><td rowspan=1 colspan=1>1272（径向应力）</td></tr></table>

# 8.6.2 FGH97粉末盘低循环疲劳寿命预测

本节分别采用传统的仅考虑危险点处应力/应变的疲劳寿命预测方法和考虑应梯度的缺口疲劳寿命预测方法对粉末温合金涡轮盘进寿命预测，并进对比分析。根据FGH97合金 $7 0 0 \mathrm { { ‰} }$ 条件下对称循环疲劳试验数据建的总应变寿命预测程如下

$$
\varepsilon _ { \mathrm { { a } } } = 0 . 0 0 9 \ ( 2 N _ { \mathrm { { f } } } ) ^ { - 0 . 0 7 5 8 8 } + 0 . 1 6 9 2 7 \ ( 2 N _ { \mathrm { { f } } } ) ^ { - 0 . 8 1 2 3 }
$$

值得一提的是，上式中参数均是在 $7 0 0 \mathrm { ‰}$ 时FGH97合材料疲劳试验中获得的，而本章计算涡轮盘模型具有不均匀的温度场，关注区域的温度也略低于材料疲劳试验时温度，但是由于材料试验数据有限，因而后续寿命预测程参数仍采用 $7 0 0 \%$ 时的材料疲劳参数，虽然这样计算得到的结果会偏于保守，但是其基本趋势是合适的。

（1）传统疲劳寿命预测法

采传统的仅考虑危险点应/应变的低循环疲劳寿命预测法，如Morrow平均应修正程、SWT程和Walker程，其寿命预测模型分别为

$$
\begin{array} { r } { \varepsilon _ { \mathrm { a } } = \cfrac { 1 5 9 7 . 3 8 8 - \sigma _ { \mathrm { m } } } { 1 7 7 2 9 0 . 6 } ( 2 N _ { \mathrm { f } } ) ^ { - 0 . 0 7 5 8 8 } + 0 . 1 6 9 2 7 ( 2 N _ { \mathrm { f } } ) ^ { - 0 . 8 1 2 3 } \qquad ( 8 - 3 7  } \\ {  \varepsilon _ { \mathrm { a } } \sigma _ { \mathrm { m a x } } = 1 4 . 3 7 6 ( 2 N _ { \mathrm { f } } ) ^ { - 0 . 1 5 1 7 6 } + 2 7 0 . 3 9 ( 2 N _ { \mathrm { f } } ) ^ { - 0 . 8 8 } \qquad ( 8 - 3 8 . 3 8   } \\ {  \mathrm { a } = 0 . 0 0 9 [ ( 2 N _ { \mathrm { f } } ) ( \frac { 1 - R } { 2 } ) ^ { - 1 . 3 } ] ^ { - 0 . 0 7 5 8 8 } + 0 . 1 6 9 2 7 [ ( 2 N _ { \mathrm { f } } ) ( \frac { 1 - R } { 2 } ) ^ { - 7 . 3 } ] ^ { - 0 . 8 1 2 3 } } \end{array}
$$

考虑到轮盘关注区域进塑性，采Neuber法计算求得局部弹塑性应/应变结果，将弹塑性计算结果代式（8-37） $\sim$ 式（8-39）得到三种寿命模型的预测结果见表8-9。

表8-9三种寿命模型的预测结果  

<table><tr><td rowspan=1 colspan=1>方法</td><td rowspan=1 colspan=1>盘心处寿命</td><td rowspan=1 colspan=1>轮缘与辐板交接处寿命</td></tr><tr><td rowspan=1 colspan=1>Morrow平均应力修正方程</td><td rowspan=1 colspan=1>44791</td><td rowspan=1 colspan=1>4320</td></tr><tr><td rowspan=1 colspan=1>SWT方程</td><td rowspan=1 colspan=1>44177</td><td rowspan=1 colspan=1>6245</td></tr><tr><td rowspan=1 colspan=1>Walker方程</td><td rowspan=1 colspan=1>27001</td><td rowspan=1 colspan=1>3697</td></tr></table>

（2）考虑应梯度的缺疲劳寿命预测法

采用考虑应力梯度的疲劳寿命预测方法，需要获得轮盘关注部位的应力变化规律，基于前述轮盘应/应变分析，确定轮盘关注部位的归一化应与归一化距离的关系，如图8-47所，进而确定轮盘盘心，以及轮缘与辐板交接处应梯度影响因子 $Y$ 分别为1.12和1.2，而参数 $C$ 和 $\alpha$ 值参照8.4节采用 $C ^ { \alpha } = 1 . 9 5$ ，将各参数值代式（8-31）中，得到涡轮盘关注部位的寿命预测结果，见表8-10。

![](images/b362946af3b4879ccd5f06ea2a11209b728ed5a5f1a3f9e70669146c5ea38d37.jpg)  
图8-47 轮盘关注位置归化应与归化距离关系

表8-10基于考虑应力梯度的缺口疲劳寿命预测方法的轮盘寿命预测结果  

<table><tr><td rowspan=1 colspan=1>方法</td><td rowspan=1 colspan=1>盘心处寿命</td><td rowspan=1 colspan=1>轮缘与辐板交接处寿命</td></tr><tr><td rowspan=1 colspan=1>考虑应力梯度影响的寿命预测方法</td><td rowspan=1 colspan=1>113029</td><td rowspan=1 colspan=1>24096</td></tr></table>

通过表8-9和表8-10的对比可以看出，采用传统的疲劳寿命预测方法预测结果明显低于采用考虑应力梯度影响的寿命预测方法，而实际粉末盘设计寿命通常在万到万次循环，表8-10中结果与此更为相符，这也表明所发展的考虑应梯度影响的疲劳寿命预测方法可以为粉末高温合金材料实际应用提供一条有益的技术途径。

# 8.6.3 含缺陷FGH97粉末盘疲劳裂纹萌生寿命预测

实际结构件中缺陷难以避免，本小节基于8.4节缺陷对粉末温合金材料局部应力/应变和疲劳寿命的影响分析，将前述确定的有效方法应用于实际粉末盘结构局部应力分析及疲劳寿命预测中。

（1）含缺陷涡轮盘局部应/应变分析

为考察缺陷对实际粉末盘的影响，在含缺陷的粉末盘有限元计算模型中，将缺陷设置在重点关注的两个危险区域，即盘心位置及盘缘与轮辐交接处，但涡轮盘半径达数百毫，缺陷半径仅仅微，二者尺度相差较，同时缺陷局部格需要加密，这样就导致了整体结构网格划分困难，且计算量庞大。由于仅仅需要关注危险区域，可在有限元软件中采用子模型的方法，将关注区域切分出来单独分析，既有利于格的划分，也降低了计算作量，切分得到的模型如图8-48所示。

![](images/facff5721d25ddd196c36f689e5a259810ca53e4b3b611cf840ccffe444aa9b0.jpg)  
图8-48 涡轮盘关注部位模型

计算时除子模型切分面上施加子模型边界条件外，其余原来作用在涡轮盘整体模型上的边界条件、载荷和约束等，如果位于子模型区域之内，则在子模型中保持不变；如果位于子模型区域之外，则在子模型中不再出现。采用子模型计算关注区域结果对比如图8-49所，模型计算结果表明，盘心处周向应，以及盘缘与辐板交接处径向应与整体模型计算结果相差不，表明了模型计算式的正确性和可行性。

![](images/2d57c63502f3d125be34a449bf7312e6b11d3e1fec4d6e3e1070060e939726b4.jpg)  
（a）盘心周向应力

![](images/cff18ea155647f5417a5e64e004cbb0bc72aa97d1ec2d34c83eb88d8142e3c8d.jpg)  
图8-49 模型与整体模型计算结果对

基于以上切分的关注区域子模型，在子模型最大应处设置了球形孔洞缺陷。为考察缺陷处于不同位置对局部应的影响，按照8.2节中关于缺陷位置的无量纲定义，分析了 $d / r = 0$ , $d / r = 1 , 5$ 和 $d / r = 3$ 时缺陷对轮盘关注区域局部应力分布的影响，这也代表了表面、亚表面和内部缺陷对轮盘关注区域局部应力分布的影响。球形孔洞缺陷对盘局部周向应和主应分布影响计算结果如图8-50所示，可以看出，盘位置处缺陷附近周向应分布趋势与8.3节中孔洞缺陷分布趋势致相同， $d / r = 0 , \ d / r = 1 . 5$ 和$d / r = 3$ 的三种位置缺陷导致的应力集中系数分别是2.25，2.3和2.24。

![](images/97f828b1625a889a66d860b1ec0db2378a42ddaaaf4cd9d61c6d1ed9dd1ff7c3.jpg)  
( b)d/r=1.5

![](images/c0807ad71a3275a0583f4331cd7cf2c285a31768cd21c66021d803d37f96c4c4.jpg)  
图8-50孔洞缺陷对盘心局部周向应力和主应分布的影响

球形孔洞缺陷对盘缘与辐板交接处局部径向应力和主应力分布影响计算结果如图8-51所示，可以看出，盘缘与辐板交接处缺陷附近径向应力分布趋势与8.3节中孔洞缺陷分布趋势也大致相同， $d / r = 0 , \ d / r = 1 . 5$ 和 $d / r = 3$ 的三种位置缺陷导致的应力集中系数分别是2.34，2.2和2.26。

![](images/162df73ba1ad0c4463b2b95d913e5512f3c22319468a0a156b7aaa19ff8b6c59.jpg)  
( b)d/r=1.5

![](images/6b3a83a2135910c1ab90c7458e6f9e1c8275d205f494754ea2dd03ac1349c256.jpg)  
图8-51 孔洞缺陷对轮缘与辐板交接处局部径向应和主应分布的影响

（2）含缺陷粉末盘裂纹萌寿命预测

根据考虑应力梯度的缺口疲劳寿命预测法及分析流程，结合前述含缺陷模型有限元弹性计算结果，先，采Neuber法对孔洞缺陷局部应/应变进计算，然后，确定球形孔洞缺陷应集中区域归一化应与归一化距离的关系如图8-52所示。

![](images/d35781d5d0560a7fced2e6ac89e14b4a8bf3c362a7b0caff6ba0b6c1da309c98.jpg)  
图8-52 轮盘关注区域球形孔洞局部归化应与归化距离的关系

由图8-52确定的不同无量纲参数 $d / r$ 条件下应力梯度影响因子 $Y$ 值见表8-11,同时表8-11中也给出了8.4节中相同量纲参数 $d / r$ 条件下含缺陷疲劳试样的 $Y$ 值计算结果进对比，为了加以区别以及便于后续使用，将8.4节中疲劳试样计算得到的应力梯度因子 $Y$ 值定义为 $Y _ { \imath }$ ，盘心位置处计算得到的应梯度因 $Y$ 值定义为 $Y _ { 2 }$ ,而轮缘与辐板交接处计算得到的应梯度因 $Y$ 值定义为 $Y _ { 3 }$ 。由表8-11可以看出，随着缺陷从材料表向内部移动，轮盘关注区域含缺陷的应梯度因 $Y$ 值与8.4节疲劳试样含缺陷时的应力梯度因 $Y$ 值变化规律相同，且在相同量纲参数 $d / r$ 条件下，其值也较为接近。

表8-11不同 $d / r$ 条件下的 $Y$ 值对比  

<table><tr><td rowspan=1 colspan=1>d/r</td><td rowspan=1 colspan=1>疲劳试样Y₁值</td><td rowspan=1 colspan=1>盘心处Y_值</td><td rowspan=1 colspan=1>轮缘与辐板交接处Y₃值</td></tr><tr><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>1.399</td><td rowspan=1 colspan=1>1.43</td><td rowspan=1 colspan=1>1.42</td></tr><tr><td rowspan=1 colspan=1>1.5</td><td rowspan=1 colspan=1>1.562</td><td rowspan=1 colspan=1>1.44</td><td rowspan=1 colspan=1>1.55</td></tr><tr><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>1.42</td><td rowspan=1 colspan=1>1.42</td><td rowspan=1 colspan=1>1.43</td></tr></table>

采8.4节中的FGH97合材料参数、Neuber法得到的轮盘关注区域含缺陷时的局部应/应变和局部应比以及表8-11中的 $Y$ 值，采用考虑应力梯度的缺口疲劳寿命预测法对轮盘关注区域含缺陷时的寿命预测结果见表8-12。可以看出，由于缺陷的存在，轮盘关注区域疲劳寿命显著降低，缺陷随量纲参数 $d / r$ 变化对疲劳寿命的影响规律与8.4节中规律基本致。另，表8-12给出了采8.4节疲劳试样计算得到的应力强度因子 $Y _ { \imath }$ 值进含缺陷轮盘寿命预测的结果，预测结果与分别采用盘位置计算得到的 $Y _ { 2 }$ 值，以及轮缘与辐板交接处计算得到的 $Y _ { 3 }$ 值进行轮盘寿命预测得到的结果相差不，表明在含缺陷疲劳试样中获得的相关参数可以直接借鉴，这也体现了8.4节中研究缺陷对疲劳试样寿命影响规律的意义所在，即在实际构件的初步寿命预测工作中，可直接采8.4节中疲劳试样计算获得相关参数，以降低计算量。

表8-12 轮盘关注区域含缺陷时的寿命预测结果  

<table><tr><td rowspan=1 colspan=1>d/r</td><td rowspan=1 colspan=1>无缺陷时寿命</td><td rowspan=1 colspan=1>盘心处采用$Y₂}值时寿命</td><td rowspan=1 colspan=1>轮缘与辐板交接处采用Y₃值时寿命</td><td rowspan=1 colspan=1>盘心处采用Y₁值时寿命</td><td rowspan=1 colspan=1>轮缘与辐板交接处采用Y1值时寿命</td></tr><tr><td rowspan=1 colspan=1>0</td><td rowspan=3 colspan=1>盘心：113029盘缘：24096</td><td rowspan=1 colspan=1>14637</td><td rowspan=1 colspan=1>1145</td><td rowspan=1 colspan=1>11953</td><td rowspan=1 colspan=1>982</td></tr><tr><td rowspan=1 colspan=1>1.5</td><td rowspan=1 colspan=1>9198</td><td rowspan=1 colspan=1>1927</td><td rowspan=1 colspan=1>8286</td><td rowspan=1 colspan=1>2060</td></tr><tr><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>14140</td><td rowspan=1 colspan=1>1528</td><td rowspan=1 colspan=1>14140</td><td rowspan=1 colspan=1>1425</td></tr></table>

# 8.6.4 含缺陷FGH97粉末盘损伤容限分析

开展含缺陷粉末盘损伤容限分析时，出于网格划分便利性及降低计算量的考虑，在有限元计算中宜采用模型法，建含缺陷轮盘模型时，将初始缺陷转化为半圆形裂纹，半径为 $5 0 \mu \mathrm { m }$ ，并使缺陷处于周向应最位置处（盘处），其扩展主要驱动为周向应，盘处涡轮盘模型及裂纹形状位置如图8-53（a）所。对缺陷局部格进细化以保证计算精度，并将沿缺陷半径长度上的节点定义为裂纹尖端，如图8-53（b）所示。

![](images/65955b7b5e7afab6d7d22ae1ec4a4d1394d386d093b42e98c00980f6d98baed5.jpg)  
图8-53 模型初始裂纹形状位置及裂尖格

假定裂纹扩展过程中保持圆形不变，扩展向沿裂纹前缘法向向外，并以 $0 . 7 6 \mathrm { m m }$ 的宏观裂纹作为涡轮盘程可检裂纹的判定标准，即裂纹半径达到 $0 . 3 8 \mathrm { m m }$ 时认为可以被检出，在裂纹半径 $5 0 \sim 3 8 0 \mu \mathrm { m }$ 的扩展区间内建了6个含有不同尺寸裂纹的计算模型，即半径 $a$ 分别为 $5 0 \mu \mathrm { m }$ , $7 5 \mu \mathrm { m }$ , $1 5 0 \mu \mathrm { m }$ , $2 5 0 \mu \mathrm { m }$ 和 $3 8 0 \mu \mathrm { m }$ ，由此可以计算出不同裂纹尺寸时裂纹尖端的应强度因范围，进可进粉末温合涡轮盘的裂纹扩展特性研究。在有限元软件中计算得到不同裂纹半径时的裂纹尖端应强度因范围如图8-54所示。

![](images/c5017217a0bf6d15df66473e29d7246a314c2c58ae7434b67718526133051903.jpg)  
图8-54 盘处不同长度裂纹尖端的应强度因范围

由图8-54可以看出，假定为裂纹的缺陷其裂纹尖端各点应强度因范围除靠近表面处稍有差异，其余位置处的应强度因范围较为接近，说明前假设裂纹扩展时保持圆形不变，扩展向沿着半圆的径向是基本合理的。同时也应当看到，由于此处定义缺陷尺寸在 $5 0 \sim 1 0 0 \mu \mathrm { m }$ ，属于裂纹范畴，由图8-54得到的应强度因范围也相对较小，其值在 $3 0 0 \sim 7 0 0 \mathrm { M P a } \cdot \mathrm { m m } ^ { 1 / 2 }$ ，但是由8.5节中裂纹扩展试验结果可以看出，FGH97合材料其应强度因范围在该区间时，表现出同长裂纹致的扩展规律，参考献[35]的研究也表明Inconel718、Rene95和IN100等种粉末温合材料都表现出了与线弹性断裂学相致的裂纹扩展规律。因此，后续开展缺陷裂纹扩展寿命计算时，假设其符合线弹性断裂力学规律。

按照8.5节的裂纹扩展寿命计算流程，将计算得到的盘心处每个裂纹长度下不同度的裂纹尖端应力强度因子取平均值，然后采用式（8-35）进行拟合，得到应力强度因范围和裂纹长度之间的关系如图8–55所。

![](images/f9c76f154e6a16690b8e27d931b7af70035f162aeac0eaa9580bff5455d92e39.jpg)  
图8-55盘处裂纹应强度因范围与裂纹长度的关系

将图8-55拟合得到的关系式和8.5节中拟合得到的裂纹扩展材料参数以及应比$R = 0$ 代式（8-34），积分得到盘含缺陷时考虑裂纹扩展的寿命预测结果为9132个循环，与8.6.3节中采考虑应梯度的缺口疲劳寿命预测法预测盘含缺陷时的疲劳寿命结果14637个循环较为接近，表明两种法殊途同归，都可以较好地得到含缺陷粉末盘的寿命。然而应当看到，采裂纹扩展的计算式得到的寿命要略低于考虑应梯度的缺口疲劳寿命预测方法预测的寿命，这主要可能是由于对小裂纹初始的裂纹扩展速率掌握仍不够准确，裂纹扩展速率试验中记录的最小的应力强度因子范围在$1 0 \mathrm { M P a } \cdot \mathrm { m } ^ { 1 / 2 }$ 左右，计算盘初始缺陷裂纹前缘的应强度因范围为 $8 \mathrm { { M P a } \cdot \ m ^ { 1 / 2 } }$ ,这也给裂纹扩展寿命的计算带来了一定误差，因而如何更好地研究获得裂纹扩展规律，对含缺陷构件裂纹扩展寿命的预测将大有裨益。

# 参考文献

[1]张丽娜，张麦仓，李晓，等.粉末温合中属夹杂物问题的研究进展[J.

兵器材料科学与工程，2001（24）：64-68.   
[2] Miner R V, Dreshfield R L. Effects of fine porosity on the fatigue behavior of a powder metallurgy superalloy [R]. NASA–TM–81448, 1980.   
[3] Grison J, Remy L. Fatigue failure probability in a powder metallurgy ni– based superalloy [J]. Engineering Fracture Mechanics, 1997, 57 (1): 41–55.   
[4] Jablonski D A. The effect of ceramic inclusion on the low cycle fatigue life of low carbon astrology subjected to hot isostatic pressing [J]. Materials Science and Engineering, 1981,48：189.   
[5] Brückner -Foit A, Jickels H. Prediction of the lifetime distribution of high – strength components subjected to fatigue loading [J]. Fatigue Fract. Engng. Mater. Struct., 1993，16（8）：891-908.   
[6] Dai D N, Hills D A. Simulation of the growth of near – surface defects [J]. Engineering Fracture Mechanics, 1998, 59 (4): 415–424.   
[7中国航空业第606所．先进航空发动机材料集M．1994.   
[8] Hyzak J M, Bernstein I M.The effect of defects on the fatigue crack initiation process in two P/M superalloys: Part I. fatigue origins [J]. Metallurgical Transactions, 1982, 13A:22-43.   
[9] Hyzak J M, Bernstein I M. The effect of defects on the fatigue crack initiation process in two P/M superalloys: Part II. Surface –subsurface transition [J]. Metallurgical Transactions, 1982, 13A: 45–52.   
[10] Shamblen C E, Chang D R. Effect of inclusion on LCF life of HIP plus heat treated powder metal Rene95 [J]. Metallurgical Transactions, 1985, 16B: 775–784.   
[11邹，汪武祥．粉末温合中夹杂物的特性及其质量控制[J．材料科学与 工艺，1999（7）：7-11.   
[12] 国为民，吴剑涛，张凤，等，FGH95镍基温合粉末中的夹杂及其对合疲 劳性能的影响[J．粉末冶金业，2000，10（3）：23-28.   
[13何承群，余泉茂，胡本芙.FGH95合LCF断裂寿命与夹杂特征关系的研究 [J].金属学报，2001，37(3）：247–252.   
[14] 谢锡善，张丽娜，张麦仓，等.镍基粉末温合中夹杂物的微观学为研究 [J].金属学报，2002，38（6）：635–642.   
[15] Bouafia F, Serier B, mecirdi M E A, Boutabout Benali. 3 –D finite element analysis of stress concentration factor in spot – welded joints of steel: the effect of process–induced porosity [J]. Computational Materials Science,2011, 50:1450–1459.   
[16曾燕屏，张麦仓，董建新，等．镍基粉末温合中夹杂物导致裂纹萌和扩展 为的研究[J．材料程，2005（3）：10-13.   
[17] Neuber H. Theory of notch stresses: principles for exact calculation of strength with reference to structural form and material [M]. Oak Ridge, Tenn., USAEC Office of Technical Information, 1961.   
[18」 Waisman J L. Metal Fatigue [M」. New York: McGraw Hill, 1959.   
[19] Tanaka K. Engineering formulae for fatigue strength reduction due to crack –like notches. International Journal of Fracture, 1983, 22 (2): R39–R46.   
[20] Lazzarin P, Tovo R, Meneghett Z G. Fatigue crack initiation and propagation phase near notches in metals with low notch sensitivity [J]. International Journal of Fatigue. 1997,19:647–657.   
[21] Taylor D. Geometrical effects in fatigue: a unifying theoretical model [J]. International Journal of Fatigue, 1999, 21 (5): 413–20.   
[22] Susmel L, Taylor D. A novel formulation of the theory of critical distances to estimate lifetime of notched components in the medium – cycle fatigue regime [J]. Fatigue & Fracture of Engineering Materials & Structures, 2007, 30(7): 567–581.   
[23] Susmel L, Taylor D. An elasto – plastic reformulation of the theory of critical distances to estimate lifetime of notched components failing in the low/medium – cycle fatigue regime [J]. Journal of Engineering Materials and Technology, 2010, 132 (2 ): 021002,1–8.   
[24] El Haddad M H, Topper T H, Smith K N. Fatigue crack propagation of short cracks [J]. Engineering Fracture Mechanics, 1979, 11: 573–584.   
[25] Adib–Ramezani H, Jeong J. Advanced volumetric method for fatigue life prediction using stress gradient effects at notch roots [J]. Computational Materials Science, 2007, 39:694-663.   
[26] Qylafku G, Azari Z, Kadi N, Gjonaj M, et al. Application of a new model proposal for fatigue life prediction on the notches and key –seats [J]. International Journal of Fatigue, 1999, 21:753–760.   
[27] Qylafku G. Loading mode and notch effect in high cycle fatigue [J]. NATO Science Series, 2001, 11: 221–237.   
[28] Boukharouba T, Tamine T, Niu L, et al. The use of notch stress intensity factor asa fatigue crack initiation parameter [J]. Engineering Fracture Mechanics, 1995, 52 (3):503-512.   
[29] 王延荣，李宏新，袁善虎，等．考虑应梯度的缺疲劳寿命预测法[J]．航 空动力学报，2013，28（6）：1028-1214.   
[30] Dowling N E. Mean stress effects in stress – ife and strain – life fatigue [R]. Society of Automotive Engineers, Inc., Technical Paper F2004/51, 2004.   
[31] Filippini M. Stress gradient calculation at notches [J]. International Journal of Fatigue,2000,22（5）:397–409.   
[32亮，魏盛，王延荣.考虑应梯度的轮盘疲劳寿命预测[J．航空动学 报，2013，28（6）：1236-1242.   
[33]中国航空研究院.军飞机疲劳、损伤容限、耐久性者设计册（第三册） [M]中国航空研究院 1994.

[34 魏盛，王延荣.粉末冶涡轮盘裂纹扩展寿命分析[J]．推进技术，2008，29(6)：753-758.

[35] Pelloux R M, Feng J, Romanoski G R. Study of the fatigue behavior of small cracks in nickel–base superalloys [R]. AFOSR–TR–88-0457, 1988.

# 第9章 轮盘结构安全性预测分析法

# 9.1引言

粉末温合由于制造艺的特点，使得其强度和寿命对微缺陷（夹杂、孔、表划痕）分敏感。量粉末材料的低循环疲劳试验结果表明，疲劳裂纹通常起始于材料表面或内部些随机分布的缺陷，如孔和夹杂。20世纪80年代初期，Hyzak及Bernstein较为系统地研究了粉末合AF-115和AF2-1DA中缺陷对疲劳寿命的影响，可见们此时已经注意到了粉末温合疲劳失效机制的特殊性，但仍然未给出较为合适的寿命预测法[1.2]，之后段时期的研究集中在短裂纹的扩展特性上[3,4]。直到20世纪90年代初期，Brückner-Foit[5]和Bussac[6,7]较早采了概率法分别对粉末材料Udimet700及N18进了寿命评估，提出了粉末材料寿命预测的新法。近年来，越来越多的国外学者基于概率模型对粉末材料的破坏进建模和分析。在国内，对粉末温合的破坏研究还较多地基于传统的寿命法，利概率法进研究的还不多。

既然缺陷将导致粉末材料疲劳性能的降低，那么就要找到解决的法。是改善粉末冶艺，尽量减少合中的缺陷含量或减缺陷尺寸；是从寿命预测度解决缺陷问题，基于概率断裂学的反映缺陷随机分布特点的概率法是个不错的选择。制造艺的选择及平使粉末材料中的缺陷分布有其的概率分布特征，导致材料性能也呈现出定的概率特征，寿命预测时对这种概率特征必须加以考虑。因此，基于参考献[6，7，8]提出的概率破坏模型思想，针对粉末材料中缺陷的分布特点，通过对缺陷形状、和位置及其与破坏的关联分析和假设，对原概率破坏模型进了修正和推，建立了一种适用范围更、更为全面地反映不同粉末材料中缺陷特点的寿命预测概率模型。参考献[6，7，9]侧重于分析缺陷自身特征（尺寸、数量等）与失效之间的关系，与试验条件的关联不紧密，假设了缺陷为球形，没有考虑亚表面缺陷，本章将针对这几点进改进。首先，从概率断裂学的角度出发，将缺陷的形状、尺寸与微裂纹扩展相结合，使模型的物理意义更为明确，可以与试验条件（温度、载荷等）较好地关联；其次，着重研究了亚表面缺陷，给出了亚表面缺陷存在时疲劳寿命、失效概率的计算方法，发现亚表面缺陷对材料疲劳性能的影响有时比表面缺陷更为显著；再次，将缺陷视为片层状，既反映了缺陷的各向异性特点，又更接近粉末材料中缺陷的真实形状，同时还可以对椭圆形、尖角等各种缺陷形状进分析。当然，每种方法都有其特定的适用条件及范围，概率方法最终要指导粉末材料及其构件的定寿工作，还需要大量系统的试验验证予以支持，由于国内相关数据的缺乏，本章的研究选用了一些国外献上的试验数据。

本章将以某型粉末冶涡轮盘作为研究对象，并结合基于螺栓孔特征的带缺陷轮盘失效概率分析法进带缺陷涡轮盘寿命预测，为粉末盘的程实化提供个借鉴，从更泛的意义上讲，也将拓宽含缺陷构件的设计分析思路。

# 9.2 寿命预测概率模型的建

从断裂学的度来看，可以认为材料中存在的个尺寸为 $a _ { 0 }$ 的缺陷是裂纹扩展的初始尺寸，并且可以由Paris公式计算含有尺寸为 $a _ { 0 }$ 的缺陷时的材料或构件寿命

$$
N _ { 0 } = \int _ { \alpha _ { 0 } } ^ { \alpha _ { c } } \frac { \mathrm { d } a } { C \left( \Delta K \right) ^ { m } }
$$

式中： $C$ , $m$ -材料常数；

$\Delta K \cdot$ (i:) 缺陷处的应力强度因子范围；

$\boldsymbol { a } _ { c }$ 材料缺陷的临界尺寸。

必须说明的是缺陷尺寸较小，属于短裂纹的研究范畴，与长裂纹的扩展规律有所不同，通常短裂纹的扩展速率远远超过长裂纹，而且在长裂纹的应强度因门槛值以下，短裂纹仍会扩展。但参考献[3，4]在研究中指出，粉末粒度较好的情况下，Rene95短裂纹扩展规律将服从长裂纹的线弹性断裂学规律，参考献[8]中对粉末材料Astroloy的短裂纹研究中也发现其扩展规律同长裂纹接近，并采了Paris公式进裂纹扩展计算，这也是本章研究选的数据。这种情况可能是镍基粉末温合的个特性，如果得到大量试验的验证，将使寿命预测工作大为简化。

式（9-1）中循环数 $N _ { 0 }$ 实际上就是含缺陷材料的剩余寿命，当存在的缺陷尺寸于 $a _ { 0 }$ 时，材料将在 $N _ { 0 }$ 次循环之前失效，在这不妨将 $a _ { 0 }$ 定义为达到临界循环数 $N _ { 0 }$ 时的缺陷临界尺寸。确定尺寸于 $a _ { 0 }$ 的缺陷在材料中存在的概率就是建寿命预测概率模型的出发点，这就是参考献[6]的主要思想，但它只考虑了表面缺陷，并且认为缺陷是呈现各向同性的球形。下将结合缺陷的实际特点对模型进修正，使其可以考虑亚表面缺陷，同时也能够反映缺陷的各向异性特征。

其一，计算时缺陷形状、大小以及数量的选取应与粉末材料中缺陷的真实情况相致。对粉末材料的相关研究进调研后发现，缺陷以属陶瓷夹杂和疏松孔较为常见，夹杂对疲劳性能的影响较大，本章也以夹杂作为研究重点。夹杂通常为层状，片层法向与盘的轴向接近，这与热等静压成形过程有关；夹杂的尺度大多集中在 $5 0 \sim 1 5 0 \mu \mathrm { m }$ ；夹杂在材料中出现的位置是随机的，但出现在表面或亚表面时对破坏的影响最为显著；夹杂数量越多，越容易产裂纹萌源导致破坏。鉴于夹杂缺陷的这些特点并考虑到计算的简便性，将任意形状的属夹杂层按照积等效为状的圆形或半圆形（表夹杂），同时以尺寸与数量的关系式给出夹杂缺陷的分布规律。假设夹杂为层状，这就涉及到了层与外载的向问题。这考虑两种情况：外载与层法向致；外载与层法向垂直。第种情况作为研究重点，是此状态较为危险，是疲劳试验后电镜扫描得到的多是断平面上的夹杂面积，其法向与外载一致，本章中的推导过程以此作为出发点。第二种

情况将在后中给出相应的分析。

其，建模分析时应对缺陷在不同位置时引起不同的破坏概率予以考虑。研究表明：表面或亚表面的缺陷最为危险，但当内部缺陷达到一定尺寸时对材料性能的影响同样是不可忽视的。在确定了采圆形、半圆形的缺陷形式进计算的基础上，给出了新的亚表面位置的定义。

在这些假定的基础上，建概率分析模型的步骤为：（1）根据粉末材料的实际情况给出缺陷尺与数量的函数关系；（2）在表、亚表及内部个不同位置处计算缺陷临界尺寸；（3）计算缺陷在不同位置出现的概率，进得到缺陷引起失效的概率。

# 9.2.1 缺陷临界尺寸的确定

不同位置处的缺陷临界尺寸 $a _ { 0 }$ 并不相同，这是因为裂纹形状及边界效应的影响导致了应强度因范围的不同，致使临界循环数 $N _ { 0 }$ 的缺陷临界尺寸不同。由式(9-1)可以看出确定缺陷临界尺其实就是已知 $N _ { 0 }$ ，求积分下限 $a _ { 0 }$

先，考察表缺陷临界尺寸 $a _ { 0 }$ 的情况，参考献[10，11中给出了半圆形裂纹的应力强度因子

$$
K _ { \mathrm { t m a x } } \ = \ 1 . 2 1 \times { \frac { 2 } { \pi } } \times \sigma \ { \sqrt { \pi a _ { 0 } } } \ = 0 . 7 7 1 \sigma \ { \sqrt { \pi a _ { 0 } } }
$$

式中： $a _ { 0 }$ bcid:) 半圆裂纹半径；

$\sigma$ 垂直于裂纹面的远端应力。

另外，参考献[12，13]中还给出了计算表不规则缺陷处应强度因的经验公式

$$
K _ { \mathrm { l m a x } } \approx 0 . 6 5 \sigma \left( \pi \sqrt { \arctan } \right) ^ { 1 / 2 } = 0 . 6 5 \sigma \left( \pi \sqrt { \pi a _ { 0 } ^ { 2 } / 2 } \right) ^ { 1 / 2 } = 0 . 7 2 8 \sigma \sqrt { \pi a _ { 0 } }
$$

式中：area 表面缺陷面积；$a _ { 0 }$ 等积的半圆裂纹半径。

可以看出式（9-2）将给出个偏于保守的计算结果。

其次，确定亚表面、内部位置及相应的缺陷临界尺寸，此时缺陷按圆形裂纹处理。关于亚表面的位置界定问题，大量文献中均有述及各的标准，本文通过对以往研究作的总结并根据参考献[14中给出的近边裂纹公式，选择 $h _ { 0 } = 2 / 3 a _ { 0 }$ (: $h _ { 0 }$ 为裂纹前缘到表面的最近距离， $a _ { 0 }$ 为圆裂纹半径）作为亚表区域与内部区域的边界，同时按圆形裂纹计算亚表、内部缺陷的临界尺寸

$$
K _ { \mathrm { r } } \ = F \times { \frac { 2 } { \pi } } \times \sigma \ { \sqrt { \pi a _ { \mathrm { 0 } } } }
$$

式中： $F$ 反映边界效应的系数，亚表位置取 $F = 1 , 1 8$ ，内部取 $F = 1$

分别将式（9-2）、式（9-4）代式（9-1）就可以计算出表面、亚表面及内部缺陷的临界尺寸，但必须考察选择的应强度因的表达式合适与否，下就采表9-1的数据进验证。表中数据来参考献[8]， $S$ 为缺陷面积， $d$ 为缺陷到表面的距离， $N$ 为试验循环数。

表9-1粉末合Astroloy疲劳试验数据  

<table><tr><td rowspan=1 colspan=1>S/μm{²$</td><td rowspan=1 colspan=1>d/μm</td><td rowspan=1 colspan=1>N</td><td rowspan=1 colspan=1>S/m^{$</td><td rowspan=1 colspan=1>d/μm</td><td rowspan=1 colspan=1>N</td></tr><tr><td rowspan=1 colspan=3>∆σ=1080MPa,R=0.1</td><td rowspan=1 colspan=1>7240</td><td rowspan=1 colspan=1>50</td><td rowspan=1 colspan=1>156000</td></tr><tr><td rowspan=1 colspan=1>820</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>29000</td><td rowspan=1 colspan=1>17000</td><td rowspan=1 colspan=1>&gt;2000</td><td rowspan=1 colspan=1>217000</td></tr><tr><td rowspan=1 colspan=1>370</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>37000</td><td rowspan=1 colspan=1>14100</td><td rowspan=1 colspan=1>&gt;2000</td><td rowspan=1 colspan=1>252000</td></tr><tr><td rowspan=1 colspan=1>1260</td><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>87000</td><td rowspan=1 colspan=1>10200</td><td rowspan=1 colspan=1>84</td><td rowspan=1 colspan=1>233000</td></tr><tr><td rowspan=1 colspan=1>2830</td><td rowspan=1 colspan=1>57</td><td rowspan=1 colspan=1>113000</td><td rowspan=1 colspan=1>9010</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>20800</td></tr><tr><td rowspan=1 colspan=3>∆σ =1050MPa,R=0</td><td rowspan=1 colspan=1>6280</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>20900</td></tr><tr><td rowspan=1 colspan=1>3920</td><td rowspan=1 colspan=1>17</td><td rowspan=1 colspan=1>230000</td><td rowspan=1 colspan=1>10620</td><td rowspan=1 colspan=1>&gt;2000</td><td rowspan=1 colspan=1>333000</td></tr><tr><td rowspan=1 colspan=1>3260</td><td rowspan=1 colspan=1>67</td><td rowspan=1 colspan=1>265000</td><td rowspan=1 colspan=1>9760</td><td rowspan=1 colspan=1>100</td><td rowspan=1 colspan=1>298000</td></tr><tr><td rowspan=1 colspan=1>1380</td><td rowspan=1 colspan=1>14</td><td rowspan=1 colspan=1>92700</td><td rowspan=1 colspan=1>14070</td><td rowspan=1 colspan=1>695</td><td rowspan=1 colspan=1>237000</td></tr><tr><td rowspan=1 colspan=1>4180</td><td rowspan=1 colspan=1>102</td><td rowspan=1 colspan=1>223000</td><td rowspan=1 colspan=1>4980</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>26000</td></tr><tr><td rowspan=1 colspan=1>4100</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>25300</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr></table>

裂纹扩展寿命的计算结果见图9-1，缺陷形状的假定和应强度因的选择是较为合适的。缺陷位于表面和内部时，计算结果与试验结果吻合较好，缺陷位于亚表面时，个计算点已超出了3倍分散带，这是因为亚表位置处的应强度因随缺陷尺寸和位置的不同不同，式（9-4）存在定的误差。图9-2的横坐标为等效圆形积半径与到表面距离的比值 $( a / h )$ ，纵坐标为缺陷位于亚表位置时的寿命，从拟合结果可以看出当 $a / h = 1 . 5$ 时，寿命有最小值，这也是将 $h = 2 / 3 a$ 作为亚表面和内部边界的重要原因。

![](images/8e61eeaa10734a4afa605b8468c78f8151a23b5719124ab1dee05e3f7f8b01cd.jpg)  
图9-1 预测寿命与试验寿命的对

![](images/41e72d97f34240d6e2118b808393d06ceda6529fc93c5953d3cf068d26e815d9.jpg)  
图9-2 表位置的界定

# 9.2.2 表面缺陷引起失效的概率

表缺陷是指缺陷被表切割，其极限状态是同表相切，图9-3中的缺陷2即处于表面位置，缺陷1、3反映了表面区缺陷的极限位置；缺陷4处于亚表面位置，而缺陷3、5又可以看作是亚表面缺陷的极限位置；缺陷6则为内部缺陷。

![](images/82b84f93773bd02e6f6cedebaaa79467c112bfea90eb0f1ce58dc6bd116dc421.jpg)  
图9-3 表、亚表以及内部位置意图

设圆在某特定区域 $V _ { s }$ 出现的概率为 $p$ ，圆可能出现的总区域为 $V$ ，则有 $p =$ $V _ { s } / V$ ，显然此定义式认为圆在体积 $V$ 中的出现规律呈现均匀分布的特点。因此，对于半径为 $a _ { i }$ 的球形孔或等效的圆形状夹杂在表区域出现的概率可以定义为

$$
p _ { \mathrm { s u r } i } \ = \frac { V _ { \mathrm { s u r } i } } { V _ { \mathrm { t o t } } } \ = \frac { S \times 2 a _ { i } } { V + S \times a _ { i } }
$$

式中： $V _ { \mathrm { s u r } i }$ -圆可能出现在表区位置的体积；

$V _ { \mathrm { t o t } }$ 圆心可能出现位置的总体积；

$S$ (id) 材料的表面积；

V 材料体积。

定义了夹杂在表区域出现的概率以后，还需要考虑夹杂引起失效的概率，图9-4中的说明较为形象和直观。缺陷1为表基准缺陷，半径为 $a _ { 0 \mathrm { s u r } }$ , $a _ { \mathrm { 0 s u r } }$ 为循环数 $N _ { 0 }$ 的表缺陷临界尺寸。假设只要表缺陷的积于基准半圆缺陷的积 $\pi a _ { 0 \mathrm { s u r } } ^ { 2 } /$ 2，材料将在 $N _ { 0 }$ 次循环之前失效。缺陷2尺寸较，较的拱 $h$ 就可以满足面积大于 $\pi a _ { 0 \mathrm { s u r } } ^ { 2 } / 2$ 的条件；缺陷3的尺寸较，需要较的拱。当然，如果缺陷3的尺寸进步减，整个积都于 $\pi a _ { 0 \mathrm { s u r } } ^ { 2 } / 2$ ，这样的缺陷不会造成材料在 $N _ { 0 }$ 次循环之前失效。也就是说，缺陷2或3的圆只要在 $d$ 区域出现，就能够满足缺陷为表面缺陷，并且面积大于 $\pi a _ { 0 \mathrm { s u r } } ^ { 2 } / 2$ 。因此，半径为 $\boldsymbol { a } _ { i }$ 的缺陷，其积于 $\pi a _ { 0 \mathrm { s u r } } ^ { 2 } / 2$ 且出现在表面的概率如下：

当 $\pi a _ { i } ^ { 2 } > \pi a _ { 0 \mathrm { s u r } } ^ { 2 } / 2$

$$
p _ { \mathrm { s u r } i } \ = \frac { V _ { \mathrm { s u r } i } } { V _ { \mathrm { t o t } } } \ = \frac { S ( 2 a _ { i } \ : - \ : h _ { i } ) } { V \ : + \ : S a _ { i } }
$$

当 $\pi a _ { i } ^ { 2 } < \pi a _ { 0 \mathrm { s u r } } ^ { 2 } / 2$ 时

$$
p _ { \mathrm { s u r } i } = 0
$$

式中， $h _ { i } = 2 a _ { i } \sin ^ { 2 } \frac { \theta } { 4 }$ $\theta$ $S _ { _ { i } } = { \frac { 1 } { 2 } } \pi a _ { 0 \mathrm { s u r } } ^ { 2 } = { \frac { 1 } { 2 } } a _ { i } ^ { 2 }$ (:) $\theta - \sin \theta )$ 求出。

![](images/3d3d706b717382ef9086a48a092c80fa6878ec5420531415bc675647bf756e65.jpg)  
图9-4 缺陷引起失效的意图

对于多个缺陷存在的情况，设半径为 $a _ { i }$ 的缺陷数目为 $n _ { i }$ ，那么至少有个积于$\pi a _ { \mathrm { 0 s u r } } ^ { 2 } / 2$ 的缺陷出现在表面的概率为

$$
P ( n _ { i } \geqslant 1 ) = 1 - P ( n _ { i } = 0 ) = 1 - ( 1 - p _ { \mathrm { s u r } i } ) ^ { n _ { i } }
$$

当然，材料中存在不同尺寸的缺陷，如果失效不会发在 $N _ { 0 }$ 次循环以前，那么就不能有面积大于 $\pi a _ { 0 \mathrm { s u r } } ^ { 2 } / 2$ 的缺陷出现在表面，则有

$$
~ 1 - P ( N < N _ { 0 } ) ~ = ~ \prod _ { \pi a _ { i } ^ { 2 } > \pi a _ { 0 \mathrm { s u r } } ^ { 2 } / 2 } P ( n _ { i } ~ = 0 ) ~ = ~ \prod _ { \pi a _ { i } ^ { 2 } > \pi a _ { 0 \mathrm { s u r } } ^ { 2 } / 2 } ( 1 - p _ { \mathrm { s u r } } ) ^ { ~ n _ { i } }
$$

$$
P ( N < N _ { 0 } ) = 1 - \prod _ { \pi a _ { i } ^ { 2 } > \pi a _ { 0 \operatorname { s u r } } ^ { 2 } / 2 } ( 1 - p _ { \operatorname { s u r } { i } } ) ^ { n _ { i } }
$$

式中： $P$ (c: $N < N _ { 0 }$ ) (id:) ${ \mathbf { } } \cdot N _ { 0 }$ 次循环之前失效的概率。

# 9.2.3 表面和内部缺陷引起失效的概率

与表面缺陷相比，确定亚表面和内部缺陷引起失效的概率较为容易，因为不存在表与缺陷相割的情况。只要半径于临界尺寸的缺陷出现在亚表区，那么材料就将在亚表面区的临界循环数之前失效，对于内部区域也同样考虑。例如，图9-4中的缺陷4为基准缺陷，其半径为 $a _ { 0 \mathrm { i n t } }$ , $a _ { 0 \mathrm { i n t } }$ 为循环数 $N _ { 0 }$ 的内部缺陷临界尺寸，当缺陷5在内部出现时试样将会在 $N _ { 0 }$ 次循环之前失效。半径为 $a _ { i }$ 的球形孔或等效的圆形状夹杂在亚表面区域出现的概率可以定义为

$$
p _ { \mathrm { s u b } i } \ = \frac { V _ { \mathrm { s u b } i } } { V _ { \mathrm { t o t } } } \ = \ \frac { 2 } { 3 } \frac { S a _ { i } } { V + S a _ { i } }
$$

在内部区域出现的概率定义为

$$
p _ { \mathrm { i n t i } } ~ = ~ { \frac { V _ { \mathrm { i n t i } } } { V _ { \mathrm { t o t } } } } ~ = ~ { \frac { V _ { \mathrm { t o t } } ~ = ~ V _ { \mathrm { s u r i } } ~ - ~ V _ { \mathrm { s u b i } } } { V + ~ S a _ { i } } }
$$

参考式（9-8），亚表和内部缺陷引起失效的概率可统写为

$$
P ( N < N _ { 0 } ) ~ = ~ 1 ~ - ~ \prod _ { \pi a _ { i } ^ { 2 } > \pi a _ { 0 } ^ { 2 } } ( 1 ~ - p _ { i } ) ^ { n _ { i } }
$$

式中：缺陷位于亚表面时pi=Pubi，a =aosub；缺陷位于内部时pi =Pimi，α0= aint aosib， $a _ { 0 \mathrm { i n t } }$ 分别为循环数 $N _ { 0 }$ 的亚表缺陷临界尺和内部缺陷临界尺寸。

# 9.2.4 总失效概率

前面的分析中包括了三种失效机制，表面缺陷引起失效、亚表面缺陷引起失效，以及内部缺陷引起失效。材料失效不会发在 $N _ { 0 }$ 次循环以前，则表面、亚表面和内部这三种失效机制均不会在 $N _ { 0 }$ 次循环之前引起失效，与此等价的条件就是：不能有面积大于 $\pi a _ { 0 \mathrm { s u r } } ^ { 2 } / 2$ 的缺陷出现在表面，不能有面积大于 $\pi a _ { 0 \mathrm { s u b } } ^ { 2 }$ 的缺陷出现在亚表，也不能有面积大于 $\pi a _ { 0 \mathrm { i n t } } ^ { 2 }$ 的缺陷出现在内部，由此可以得到总体失效概率

$$
\begin{array} { r c l } { { 1 - P _ { \mathrm { t } } ( N < N _ { 0 } ) } } & { { = P _ { \mathrm { s u r } } ( a _ { i } > a _ { \mathrm { 0 a u r } } ) P _ { \mathrm { s u b } } ( a _ { i } > a _ { \mathrm { 0 u s } } ) P _ { \mathrm { i n t } } ( a _ { i } > x _ { \mathrm { i n t } } ) } } & { { ( 9 - 1 2 \pi \mathrm { e } ^ { - 1 2 } ) P _ { \mathrm { s u t } } ( a _ { i } > \cdots b _ { \mathrm { 0 i n t } } ) } } \\ { { - P _ { \mathrm { t } } ( N < N _ { 0 } ) } } & { { = \displaystyle { \prod _ { i } ^ { 2 } \cdots \prod _ { \mathrm { s u r } } P _ { \mathrm { s u r } } ( n _ { i } ~ = 0 ) } \displaystyle { \prod _ { i } ^ { 2 } \cdots \sum _ { \mathrm { s u b } } P _ { \mathrm { s u b } } ( n _ { i } ~ = 0 ) } \displaystyle { \prod _ { i } ^ { 2 } \cdots \sum _ { \mathrm { s u p } } P _ { \mathrm { i n t } } ( n _ { i } ~ = 0 ) } } } & { { } } \\ { { } } & { { } } & { { } } \\ { { . P _ { \mathrm { t } } ( N < N _ { 0 } ) } } & { { = \left[ 1 - P _ { \mathrm { s u r } } ( N < N _ { 0 } ) \right] \left[ 1 - P _ { \mathrm { s u b } } ( N < N _ { 0 } ) \right] \left[ 1 - P _ { \mathrm { i n t } } ( N < N _ { 0 } ) \right] } } \\ { { } } & { { } } & { { } } \\ { { . N < N _ { 0 } \ } } & { { = 1 - \left[ 1 - P _ { \mathrm { s u r } } ( N < N _ { 0 } ) \right] \left[ 1 - P _ { \mathrm { s u b } } ( N < N _ { 0 } ) \right] \left[ 1 - P _ { \mathrm { i n t } } ( N < N _ { 0 } ) \right] } } \end{array}
$$

式中： $P$ $N < N _ { 0 }$ ）为 $N _ { 0 }$ 次循环之前失效的概率； $P$ $a _ { i } > a _ { 0 }$ ）为在某区域于临界尺寸的缺陷出现的概率；下标t、sur、sub、int分别代表总体、表面、亚表面和内部。

# 9.2.5 概率寿命计算结果及分析

只要将粉末材料中缺陷的实际分布以及裂纹扩展试验的材料常数引模型就可以进概率寿命分析。对于所建的模型，缺陷数量及尺寸分布规律的般形式见式（9-13），计算时采的参数见表9-2。

$$
N _ { i } = f ( a _ { i } )
$$

式中： $N _ { i }$ 半径为 $a _ { i }$ 的缺陷个数。

表9-2 Astroloy材料的Paris公式常数  

<table><tr><td rowspan=1 colspan=1>C,真空</td><td rowspan=1 colspan=1>m，真空</td><td rowspan=1 colspan=1>C1,空气</td><td rowspan=1 colspan=1>m1,空气</td><td rowspan=1 colspan=1>C2空气</td><td rowspan=1 colspan=1>m2,空气</td><td rowspan=1 colspan=1>ΔKa(MPa · m1/2)</td><td rowspan=1 colspan=1>Ke(MPa · m12)</td></tr><tr><td rowspan=1 colspan=1>1.1×10-11</td><td rowspan=1 colspan=1>2.81</td><td rowspan=1 colspan=1>2.0×10-13</td><td rowspan=1 colspan=1>2.8</td><td rowspan=1 colspan=1>6.0×10-12</td><td rowspan=1 colspan=1>3.05</td><td rowspan=1 colspan=1>11.5</td><td rowspan=1 colspan=1>95</td></tr></table>

表9-2中为短裂纹扩展试验的相关数据[⁸]，试验温度为 $4 0 0 \mathrm { { ‰} }$ ，频率为 $1 0 \mathrm { H z }$ ，应力比 $R = 0 . 1$ 。空环境的试验中存在个应强度因范围的临界值 $\Delta K _ { _ { \mathrm { 1 h } } } = 1 1 . 5 \mathrm { M P a \cdot m } ^ { 1 / 2 }$ ,当应强度因范围 $\Delta K < \Delta K _ { \mathrm { t h } }$ 时，Paris公式常数取 $C _ { 1 }$ 和 $m _ { 1 }$ ；当 $\Delta K > \Delta K _ { \mathrm { t h } }$ 时，Paris公式常数取 $C _ { 2 }$ 和 $m _ { 2 }$ ; $K _ { \mathrm { c } } = 9 5 \mathrm { M P a } \cdot \mathrm { m } ^ { 1 / 2 }$ ，为断裂韧性。计算时采式（9-14）模拟粉末材料中缺陷的分布，该式在一定程度上能够客观地反映缺陷的分布特征，当然此分布形式与缺陷的实际分布情况仍存在差异，较为准确地描述缺陷的分布依赖于量的统计结果及无损检测技术的精度。

$$
N _ { i } = 1 0 0 0 a _ { i } ^ { - 1 . 5 }
$$

图9-5是式（9-14）的计算结果， $5 0 \mu \mathrm { m }$ 以下的缺陷数量较多， $5 0 \mu \mathrm { m }$ 以上的较大尺寸缺陷数量较少，反映了随着工艺水平的提高，缺陷尺寸越来越小的实际情况。图9-6为计算得出的缺陷临界尺寸和临界循环数的关系。计算采用圆柱形标准试样，工作部分的参考尺寸为 $\phi 6 \mathrm { m m } \times 3 2 \mathrm { m m }$

（1）缺陷位置对失效概率的影响

缺陷处于不同位置时对失效概率的贡献是不同的，表、亚表面缺陷较为危险，而内部缺陷尺寸达到定程度时同样会导致材料失效。采用前面建的模型针对缺陷位置进计算分析，得出了些具有程指导意义的结果，如图9–7\~图9-10所。

图9-6给出了临界尺寸和临界循环数的关系曲线，这是联系概率模型与试验条件的重要步骤。图9-7\~图9-9分别给出了不同应范围下表面、亚表面以及内部缺陷引起失效的概率，在相同失效概率下，应范围的降低使临界循环数增加。由图9-7的计算结果可以看出当循环数达到定次数时表失效概率不再增加，是保持不变，这是因为在计算时给出了个表裂纹扩展的应强度因的门槛值

![](images/d3c2c2e9994e06d2dd0a41b628ad55f423e0eb82bd1a7eefcf6d579a4067dd3a.jpg)  
图9-5 缺陷尺寸和数量的关系

![](images/917f73e73753efdbcb264045fcc99a28a1db36042088f93f4991679061249542.jpg)  
图9–6 临界尺寸和临界循环数的关系

![](images/3d985a6cf0a2a7d0e9f226c02fa7d1be9572c3cbbb28c4c19c17433660389910.jpg)  
图9-7 表缺陷引起失效的概率

![](images/8ce3b173cd355e759ea4906a261c17ce6f416d9d2964a5f6da87b744f193cd3b.jpg)  
图9-8 亚表面缺陷引起失效的概率

![](images/a4968777691b1eebc7a81be0031da7f765d484ff26223aa5dca63c1c0ee8a0be.jpg)  
图9-9 内部缺陷引起失效的概率

![](images/c540944c17dc9a13fdc8cab2548a3e9eb6206951bc582b52270cdaa25672be64.jpg)  
图9-10 总失效概率

$\Delta K _ { \mathrm { t h } }$ ，对应有个临界尺寸的门槛值 $a _ { \mathrm { t h } }$ ，正是它的存在导致了上述情况的发。如果不给出门槛值，失效概率将继续增加但幅度很，这是因为极的缺陷对失效概率的贡献已经相当。图9-8和图9-9的计算结果中存在些“平台”，例如，图9-8中的$A B$ 段， $A B$ 段实际上代表了临界尺寸的段区间。造成“平台”的原因是按式(9-14)给出的缺陷尺寸分布时，其中不包含与 $A B$ 段中临界尺寸较为接近的缺陷，从另外个度分析，就是亚表、内部缺陷引起的失效概率不像表缺陷对尺寸那么敏感。图9-9中在定循环数以后，内部缺陷将导致失效概率迅速增加，失效概率趋近于1。这同样易于理解，内部区域较，缺陷出现的概率较，试验的最终结果就是失效，因此失效概率趋近于1。

图9-10是按照式（9-12）计算得出的总失效概率，与图9-9较可以看出，内部缺陷引起的失效概率在总失效概率中所占的例是很的，尤其在循环区域；在低循环区域，表、亚表缺陷引起的失效概率所占的例则较。显然，当体积定时改变表面积的，表缺陷引起的失效概率与内部缺陷引起的失效概率的例将发改变，这就是所谓的尺效应。后将给出计算结果及分析。

当然还可以简单讨论下表、亚表缺陷与内部缺陷尺寸的等效关系。由图9-6可以看出，内部缺陷的临界尺寸最大，在低循环范围为表面缺陷临界尺寸的1.5倍，为亚表缺陷临界尺寸的2倍，也就是说亚表缺陷最危险；在循环范围，缺陷临界尺寸急剧减，说明要达到这样的寿命条件，对材料质量的要求分严格。

显然，在某个循环数下，可以得到表面、亚表面以及内部缺陷临界尺寸之间的等效关系，这样只需对表缺陷进分析就可以得到总体失效概率。根据计算结果， $1 0 5 0 \mathrm { M P a }$ 下，循环数为8000时，表面缺陷的临界尺寸为 $1 5 6 \mu \mathrm { m }$ ，亚表面和内部缺陷的临界尺寸分别为 $1 1 8 \mu \mathrm { m }$ , $2 7 6 \mu \mathrm { m }$ ，这样根据它们之间的比例关系，将材料中的缺陷转化成表缺陷，或者说只根据表缺陷评估粉末材料的失效，将使分析过程简化。

（2）缺陷数量对失效概率的影响将式（9-14）的形式改为

$$
N _ { i } ~ = 2 0 0 0 a _ { i } ^ { - 1 . 5 }
$$

式中， $a _ { i }$ 的分布保持不变，相当于增加了缺陷的数量，图9-11为式（9-15）给出的缺陷分布形式。与图9–10的结果相比，图9–12计算得到的总失效概率显著提。

（3）表面积对失效概率的影响

保持试样作部分的体积不变，改变试样的表面积，也就是改变了试样的形状，计算得到了图9-13和图9-14的结果。可以看出表积的改变对表缺陷引起失效的影响是较为显著的，对于内部缺陷引起失效的影响较。

表缺陷较为危险且表积对失效概率影响较，这样很然会想到个问题，那就是构件的表面积越大，出现缺陷的可能性就越大，对构件的疲劳性能影响也越。因此，粉末材料构件的表面质量问题关重要。另外，进材料试验的试样均为光滑试样，其尺寸较存在缺陷的可能性也较；而尺寸构件则易含缺陷，裂纹也极易由这些缺陷处萌。因此，以尺寸光滑试样的试验结果预测尺寸构件的寿命就存在定的风险，这也是近年来采植缺陷的试样进量试验研究的个主要原因。根据植夹杂试样的试验结果，进断分析并考虑尺寸效应的影响，就有可能在试样和构件的寿命之间建立某种定量的联系，提寿命预测精度。

![](images/6e667a18c506220db8c9b1c3b7bc1d310bf465fb90dc906739b63299f2dfa800.jpg)  
图9-11 缺陷尺寸和数量的关系

![](images/c66556dfdc5b129e18585fa0f822c2b0ff658ed629e76c710bd728ee616db396.jpg)  
图9-12 失效概率

![](images/d29efa099f9c2bbab2c21b34e10c214ef0f2e8ae68a8f51927cbea89941fb7d9.jpg)  
图9-13 表积对表失效概率的影响

![](images/3d602cc71413e72b112db9dbf24eb7f23e013472341637141aefe6e83dac2ea5.jpg)  
图9-14 表积对内部失效概率的影响

（4）与试样取样向相关的缺陷形状对失效概率的影响

非金属夹杂通常为片层状，片层的法向与盘的轴向接近，这与粉末材料的热等静压成形过程有关。粉末盘坯上轴向取样与径向取样试样相比，在疲劳性能上有较大差异，径向取样试样的疲劳性能远远优于轴向取样试样[15,16]。已经利概率模型对轴向取样进行了分析，下面对径向取样进行分析。

如图9-15所 $Y$ 方向为轴向， $X$ 向为径向。轴向取样时层法向与外载 $\sigma _ { \mathrm { a x i } }$ 方向一致， $\sigma _ { \mathrm { r a d } } = 0$ ；径向取样时层法向与外载 $\sigma _ { \mathrm { { r a d } } }$ 方向垂直， $\sigma _ { \mathrm { a x i } } = 0$ 。不难看出轴向取样试样的疲劳性能较差， $Z$ 方向为弦向，可近似认为弦向取样的疲劳性能同径向取样一致。与前面的分析相比，最大的不同之处就在于应力强度因子的选取。沿径向外载方向看去，非属夹杂的形状为狭长的条状，考虑到夹杂的实际形状以及计算的简便性，不妨将径向取样时的夹杂形状视为椭圆形且其长短轴比为 $n$ $n = 1$ ，2，3，…），并据此给出表面、亚表面，以及内部缺陷的应力强度因子。亚表面区与内部边界的界定仍参考前面的假定，将椭圆形夹杂到表距离与其半宽度的比值（ $h /  { b _ { 0 } }$ ）为 $2 / 3$ 的位置作为亚表面与内部的边界，如图9-16所示。

夹杂1位于表；夹杂3位于亚表，夹杂2可以看作是亚表面及表面的极限位置；夹杂4则位于内部。表、亚表及内部夹杂应强度因的形式可以统一写为

![](images/65bb09a87faa96bb950e98b4c9a609b141a08a7c81b2c2312f3f2dcb510f3383.jpg)  
图9–15 层状属夹杂同外载的向

$$
K _ { \mathrm { 1 } } = F \times \frac { 2 } { \pi } \times \sigma \sqrt { \pi b _ { \mathrm { 0 } } }
$$

![](images/7e648bbedce46c6cc1d5ffac24f3477966a1fa7c4e2be90ebacdafe8f554eaf3.jpg)  
图9-16 表、亚表以及内部位置意图

$a _ { 0 }$ 为半圆裂纹半径（从轴向考虑），也可以看作是椭圆形裂纹（从径向考虑）的半长轴； $b _ { 0 }$ 为椭圆形裂纹的半短轴，这取 $a _ { 0 } / b _ { 0 } = 5$ ; $\sigma$ 为垂直于裂纹面的远端应力；系数 $F$ 的取值见表9-3。给定应强度因后，就可以按照前的步骤进失效概率分析，结果如图9-17和图9-18所示。

表9-3 应力强度因子的选取  

<table><tr><td rowspan=1 colspan=1>缺陷类型</td><td rowspan=1 colspan=1>轴向取样试样</td><td rowspan=1 colspan=1>径向（弦向）取样试样</td></tr><tr><td rowspan=1 colspan=1>表面缺陷</td><td rowspan=1 colspan=1>半圆表裂纹，均匀拉伸，参考献[10]第686页半椭圆表裂纹，均匀拉伸，参考献[10] 第715页2x0√πa0TTKImax = 1.22×</td><td rowspan=1 colspan=1>半圆表裂纹，均匀拉伸，参考献[10]第686页半椭圆表裂纹，均匀拉伸，参考献[10] 第715页2xσ√πb0$TK max =1.75×</td></tr><tr><td rowspan=1 colspan=1>亚表面缺陷</td><td rowspan=1 colspan=1>近边圆裂纹，均匀拉伸，参考文献[10]第708页2xσπa0πKmax =1.15×</td><td rowspan=1 colspan=1>近边椭圆裂纹，均匀拉伸，参考献[10]第708页2x0√πb0$K1max =1.71×π</td></tr><tr><td rowspan=1 colspan=1>内部缺陷</td><td rowspan=1 colspan=1>圆形裂纹，法向均匀拉伸，参考献[10第637页2xσ√πa0π</td><td rowspan=1 colspan=1>椭圆裂纹，法向均匀拉伸，参考献[10]第649页2×0√πb0Kmax =1.51 ×π</td></tr></table>

![](images/da17ed89dfa7dc21232df8b14d7556626272c4728eb810c1b58430da53b18b2e.jpg)  
图9-17 轴向及径向取样试样的失效概率

![](images/c3e15e1d92daf339eb0ca67261919be065d15b3649dec1d196642b4251596631.jpg)  
图9-18 轴向及径向取样试样的总失效概率

图9-17给出了 $1 0 5 0 \mathrm { M P a }$ 拉伸应下轴向及径向取样试样不同位置的失效概率。当试样为径向取样时，表、亚表位置的失效概率均显著降低，说明缺陷形状对表、亚表面失效的影响较大。对于内部缺陷而，相同应力范围下的轴向及径向取样试样的内部位置失效概率曲线较为接近，说明缺陷大小对于内部失效的作用较大，而缺陷形状的作用较。另外，两条内部位置失效概率曲线出现了交点，这与计算时假定的夹杂形状及夹杂分布有关。图9-18则给出了轴向及径向取样试样总失效概率的比较，不同应力平下径向取样试样的总失效概率均有所降低。图9-17和图9-18中的计算曲线出现了些“平台”，前面已经分析了产的原因。当然上述结论是在圆形、椭圆形缺陷形状的假设条件下得出的，实际的缺陷形状较为复杂，尖角的存在将会加快微裂纹的扩展。因此，在进一步的研究中，如果有大量粉末材料无损检测数据作为支持，有必要对模型中缺陷形状的假设进行修正。

# 9.3 基于寿命预测概率模型的粉末盘可靠度计算

前面已建了粉末材料的寿命预测概率模型，并重点分析了试样的概率寿命。本节将延续前面的思想，与有限元分析结果相结合，针对粉末材料中缺陷分布的概率特点对某型粉末冶涡轮盘的可靠性问题进分析，同时验证寿命预测概率模型在构件上的实用性。

盘类零件是航空燃涡轮发动机常见的关键件，在转速和温等极其严酷的条件下作，其结构设计必须满相应的设计准则，以保证具有够的可靠性和耐久性。典型的盘类故障模式主要有：低循环疲劳裂纹的萌生和裂纹的扩展、轮盘外径伸长变形、轮盘超转破裂、轮盘辐板屈曲变形，以及盘叶耦合振动产的开裂破坏等[17,18]。为防止这些故障的发生，满足设计准则的要求，在轮盘设计的各个阶段选用合适的分析方法的同时，需要进风险评估作，也就是轮盘可靠性计算，结构可靠性问题已经越来越引起们的关注。粉末盘中的微缺陷使得上述种故障模式发的概率大增加，尤其是低循环疲劳裂纹的萌和扩展，即裂纹更易萌，裂纹扩展寿命更短。这样看来，考虑粉末盘低循环疲劳裂纹萌和裂纹扩展这故障模式时，微缺陷的随机分布特征将成为影响粉末盘可靠性的个重要因素。这需要进两点必要的说明：是假设萌寿命很短，总寿命取决于微裂纹扩展寿命，本节的可靠性分析侧重于裂纹扩展；是轮盘的可靠度受到多种因素的制约，诸如材料性能的随机性、轮盘载荷的随机性等，这仅仅考虑由于缺陷的存在导致轮盘可靠性降低的问题。

粉末冶涡轮盘的可靠度计算包括以下个步骤：（1）进粉末盘的弹塑性应有限元分析，由此得到轮盘每个单元的应情况；（2）计算每个单元的缺陷临界尺寸，将单元缺陷临界尺寸 $a _ { 0 }$ 定义为单元应作下在 $N _ { 0 }$ 次循环下失效所对应的缺陷尺寸，显然单元中若含有尺寸大于 $a _ { 0 }$ 的缺陷，那么单元将在 $N _ { 0 }$ 次循环之前失效，此步骤需要到粉末材料裂纹扩展试验的结果；（3）给出轮盘中缺陷的分布形式（尺寸、形状和数量等），在此基础上计算缺陷在每个单元中出现的概率，并判断其与单元缺陷临界尺寸 $a _ { 0 }$ 的关系，于 $a _ { 0 }$ 将导致单元在$N _ { 0 }$ 次循环之前失效，这样我们就得到了每个单元在 $N _ { 0 }$ 次循环之前失效的概率；（4）将所有单元视为个并联系统，进计算出整个轮盘的可靠度。下对这四个步骤进详细论述。

# 9.3.1 粉末盘弹塑性应有限元分析

已往的研究中已经成功地在通用有限元程序MSC.MARC中实现了Chaboche本构模型，这将其应在粉末盘件的计算分析中，以模拟FGH95粉末冶涡轮盘的变形特征及应分布。下将简单介绍粉末盘的有限元模型及边界条件，并对计算结果进分析以考核轮盘强度。

（1）有限元模型及边界条件

从轮盘上切取个包含完整榫槽部位的扇区，采循环对称算法进求解，这样可以使有限元建模的作量和计算时间减少。有限元模型共13832个单元，17298个节点，计算时选六体节点单元，如图9-19所。计算况为起飞状态，此状态下的温度场如图9-20所示，施加的边界条件见表9-4。

![](images/11cdad9edee3dcaaa7d22fe526f21b91cae8397205d98c675b0651f29917b899.jpg)  
图9-19 轮盘有限元格

![](images/dba2c1d34f49c31387836ab22b707db15e49e08f5b539e3d68cb9d356dc51d80.jpg)  
图9-20 轮盘结构温度分布

表9-4计算模型的边界条件  

<table><tr><td rowspan=1 colspan=1>边界条件</td><td rowspan=1 colspan=1>位置</td><td rowspan=1 colspan=1>作用</td></tr><tr><td rowspan=1 colspan=1>位移边界条件</td><td rowspan=1 colspan=1>相应安装部位</td><td rowspan=1 colspan=1>用以约束轮盘的轴向、周向位移</td></tr><tr><td rowspan=1 colspan=1>循环对称条件</td><td rowspan=1 colspan=1>轮盘两侧子午面</td><td rowspan=1 colspan=1>反映轮盘的对称特征，简化计算</td></tr><tr><td rowspan=1 colspan=1>离心力载荷</td><td rowspan=1 colspan=1>轮盘的所有单元</td><td rowspan=1 colspan=1>反映轮盘旋转产的离心力场，转速45000r/min</td></tr><tr><td rowspan=1 colspan=1>温度载荷</td><td rowspan=1 colspan=1>轮盘的所有单元</td><td rowspan=1 colspan=1>反映轮盘的起飞状态温度</td></tr><tr><td rowspan=1 colspan=1>榫槽压力</td><td rowspan=1 colspan=1>榫齿工作面</td><td rowspan=1 colspan=1>反映由叶离心力产生的压力，其值为533MPa</td></tr></table>

（2）循环对称模型计算结果

采用上述有限元模型计算得到了粉末盘盘身的应分布情况，如图9-21和图9-22所，几个危险考核点的应平见表9-5。计算结果表明轮盘的应储备平较，盘基本处于弹性状态。

![](images/854a6a8614235e6cfd34d0c91580c67e131ff8cf31c8a90ee809590b3e972c32.jpg)  
图9-21 轮盘径向应分布

![](images/6d098e88eb29c0a28feef6d9b67c78669dae5112525ab11c11fb4f16d1aea912.jpg)  
图9-22 轮盘周向应分布

表9-5 轮盘（循环对称模型）考核点应平  

<table><tr><td rowspan=1 colspan=1>序号</td><td rowspan=1 colspan=1>部位</td><td rowspan=1 colspan=1>应力水平/MPa</td><td rowspan=1 colspan=1>节点号</td></tr><tr><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>轮心处周向应力</td><td rowspan=1 colspan=1>973.0</td><td rowspan=1 colspan=1>12284</td></tr><tr><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>轮心处等效应力</td><td rowspan=1 colspan=1>1086.0</td><td rowspan=1 colspan=1>13180</td></tr><tr><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>榫槽根部径向应力</td><td rowspan=1 colspan=1>1189.0</td><td rowspan=1 colspan=1>722</td></tr><tr><td rowspan=1 colspan=1>4</td><td rowspan=1 colspan=1>榫槽根部等效应力</td><td rowspan=1 colspan=1>1055.2</td><td rowspan=1 colspan=1>706</td></tr><tr><td rowspan=1 colspan=1>5</td><td rowspan=1 colspan=1>辐板圆角处径向应力</td><td rowspan=1 colspan=1>1112.0</td><td rowspan=1 colspan=1>15543</td></tr><tr><td rowspan=1 colspan=1>6</td><td rowspan=1 colspan=1>辐板圆角处等效应力</td><td rowspan=1 colspan=1>793.6</td><td rowspan=1 colspan=1>14657</td></tr></table>

这里直接采用前面的有限元分析结果，以轮盘周向应力作为垂直于裂纹面的应力方向，相应地，以微缺陷在轮盘子午面上的投影大小作为其度量值。这样做有两点好处：其一，考虑了疲劳裂纹扩展的主要因素；其，考虑复合裂纹的扩展问题较为困难，将缺陷在轮盘子午面上的投影面积作为缺陷大小，并以轮盘周向应力作为法向应，可以将空间问题降维。当然也可以将径向应作为垂直于裂纹的应向，并将微缺陷在轮盘圆柱面上的投影大小作为其度量值，但在关于破裂转速的计算中发现子午面比圆柱面更危险，因而这里以轮盘的周向应力作为重点进分析。

# 9.3.2 单元缺陷临界尺寸的计算

单元缺陷临界尺寸的计算是进可靠性分析的前提，前面对缺陷临界尺寸的定义及求解已有较为详细的说明，这不再赘述。由Paris公式计算临界循环数为 $N _ { 0 }$ 时的缺陷临界尺寸 $a _ { 0 }$ ，即已知积分值，求出积分下限。表9-6中给出了Paris公式中的 $C$ , $m$ 材料常数值，以及材料断裂韧性 $K _ { \mathrm { e } }$

表9-6 FGH95材料的Paris公式常数（试验温度 ${ \bf 6 5 0 9 C }$ ，紧凑拉伸试样)  

<table><tr><td rowspan=1 colspan=1>C</td><td rowspan=1 colspan=1>m</td><td rowspan=1 colspan=1>K/ (MPa·m12)，FGH95</td><td rowspan=1 colspan=1>K/(MPa·m1²),CH4169</td></tr><tr><td rowspan=1 colspan=1>4.440×10-8</td><td rowspan=1 colspan=1>2.816</td><td rowspan=1 colspan=1>95.0</td><td rowspan=1 colspan=1>103.5</td></tr></table>

应力强度因子的选取也是一个重要问题，轮盘结构比试样复杂得多，涉及到裂纹、孔边裂纹、表面浅裂纹、内部裂纹等多种裂纹形式，且轮盘不同位置处将具有不同的缺陷临界尺寸，这与该位置处的应强度因的形式密切相关。分析时需要针对轮盘个特殊位置选取不同的应强度因子，分别计算缺陷的临界尺寸，如图9-23和图9-24所示。计算应强度因时采用单元的周向应范围，不同于试样计算时采的拉伸应范围。显然单元缺陷临界尺寸为单元位置以及单元应范围的函数，即

$$
a _ { 0 } ~ = f ( N _ { 0 } , \Delta K ) ~ = f ( N _ { 0 } , x , y , \sigma )
$$

式中： $N _ { 0 }$ 循环数；(id) $\Delta K \cdot$ —应力强度因子；$x$ ,y 单元位置；$\sigma$ (id 单元应力。

![](images/ce269b6a04d8a775f932277c7c7c730466aa3e906c18ac164c3c65ea11b2c0a1.jpg)  
图9-23 轮盘上的典型区域

![](images/9b8d20b961955982f154a0b75bc474ae59c4b518c164382b29b499e918a1e4c0.jpg)  
图9-24 表单元及内部单元

假定缺陷为椭圆形，可以改变椭圆的长短轴之来近似模拟各种形状的缺陷。应强度因子的形式可以统一写为

$$
K _ { \mathrm { r } } \ = \ F \times { \frac { 2 } { \pi } } \times \sigma \ { \sqrt { \pi b _ { 0 } } }
$$

式中： $b _ { 0 }$ 为椭圆形裂纹的短半轴， $a _ { 0 }$ 为椭圆形裂纹的长半轴，计算时取 $a _ { 0 } / b _ { 0 } = 5$ ; $\sigma$ 为单元周向应力； $F$ 为系数，见表9-7。

表9-7 轮盘不同位置处的应力强度因子[10,11]  

<table><tr><td rowspan=1 colspan=1>区域</td><td rowspan=1 colspan=1>描述</td><td rowspan=1 colspan=1>裂纹形式</td><td rowspan=1 colspan=1>应力强度因子表达式</td></tr><tr><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>中心孔端面及榫槽底</td><td rowspan=1 colspan=1>1/4椭圆角裂纹，均匀拉伸</td><td rowspan=1 colspan=1>Kimax =1.73×2x0\πb$π</td></tr><tr><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>轮盘的表面区域</td><td rowspan=1 colspan=1>半椭圆表浅裂纹，均匀拉伸</td><td rowspan=1 colspan=1>K1max =1.75x2x0√πb0$π</td></tr><tr><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>轮盘的亚表面区域</td><td rowspan=1 colspan=1>近边椭圆裂纹，均匀拉伸</td><td rowspan=1 colspan=1>Kmax =1.71×2xσ√πb0π</td></tr><tr><td rowspan=1 colspan=1>4</td><td rowspan=1 colspan=1>轮盘的内部区域</td><td rowspan=1 colspan=1>椭圆裂纹，法向均匀拉伸</td><td rowspan=1 colspan=1>Kmax =1.51×2x0\πb$π</td></tr><tr><td rowspan=1 colspan=1>5</td><td rowspan=1 colspan=1>中心孔边</td><td rowspan=1 colspan=1>半椭圆表面浅裂纹，均匀拉伸</td><td rowspan=1 colspan=1>Kimx =1.75×2x0√πb0πT</td></tr></table>

当然，准确描述缺陷的形状，选择合适的应强度因形式，依赖于损检测数据及微裂纹扩展试验的结果。上述分析可以看出，求解单元的缺陷临界尺寸，有以下个步骤：（1）判断单元位置，提取单元的周向应力范围，给出相应的应强度因值；(2）给出系列临界循环数， $N _ { 0 1 }$ , $N _ { 0 2 }$ , $\cdots$ , $N _ { 0 i }$ , $\cdots$ , $N _ { 0 n }$ ；（3）根据Paris公式计算出对应于临界循环数的单元缺陷临界尺寸，a01，a02，…，ai，…，a0n

# 9.3.3 轮盘中缺陷的分布形式

缺陷的分布情况将直接影响到轮盘的性能，采本模型进分析时，不同的分布将得到不同的可靠度。粉末冶艺包括制粉、粉末筛分、静电分离去除属夹杂等个必备的艺过程，不同产和研究部门在具体艺的选取上各不相同，这种差异将导致缺陷的分布呈现不同的形式，表9-8为等离旋转电极制粉时粉末中的缺陷含量。钢铁研究总院及航空材料研究院量关于粉末材料缺陷的研究表明，缺陷尺寸和数量呈现出种正态分布的规律，且尺寸主要集中在 $5 0 \sim 1 0 0 \mu \mathrm { m }$ $1 0 0 \sim 1 5 0 \mu \mathrm { m }$ 这两个区间范围[19,20]。正态分布的概率密度函数为

$$
f ( x ) = \frac { 1 } { \sqrt { 2 \pi } \sigma } \mathrm { e x p } \Big [ - \frac { ( x - \mu ) ^ { 2 } } { 2 \sigma ^ { 2 } } \Big ] \qquad ( - \infty < x < + \infty )
$$

上式也可以写成 $X \sim N$ : $\mathcal { \mu }$ , $\sigma ^ { 2 }$ ）的形式，表示参数为 $\mu , ~ \sigma$ 的正态分布， $\mu$ 为位置参数， $\sigma$ 为尺度参数， $x$ 代表缺陷的尺寸， $f$ (: $x$ ）代表相应尺寸缺陷的数量。进粉末盘可靠度计算时，将按照正态分布给出种缺陷分布的形式，以此来考察缺陷分布对轮盘可靠度的影响。

表9-8 每千克粉末中非金属夹杂数量与尺寸的关系  

<table><tr><td rowspan=2 colspan=1>类别</td><td rowspan=1 colspan=7>尺寸/μm</td></tr><tr><td rowspan=1 colspan=1>50~100</td><td rowspan=1 colspan=1>100~150</td><td rowspan=1 colspan=1>150~200</td><td rowspan=1 colspan=1>200~250</td><td rowspan=1 colspan=1>250~300</td><td rowspan=1 colspan=1>&gt;300</td><td rowspan=1 colspan=1>总数</td></tr><tr><td rowspan=1 colspan=1>陶瓷</td><td rowspan=1 colspan=1>25</td><td rowspan=1 colspan=1>17</td><td rowspan=1 colspan=1>9</td><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>/</td><td rowspan=1 colspan=1>54</td></tr><tr><td rowspan=1 colspan=1>熔渣</td><td rowspan=1 colspan=1>14</td><td rowspan=1 colspan=1>21</td><td rowspan=1 colspan=1>15</td><td rowspan=1 colspan=1>7</td><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>60</td></tr></table>

# 9.3.4 轮盘可靠度计算及结果分析

计算轮盘的可靠度，首先要计算出每个单元的可靠度，然后将所有的单元视为一个并联系统，从而计算出整个轮盘的可靠度。单元失效概率是与缺陷出现在该单元中的概率密切相关的，任意种缺陷出现在单元中的概率可以按照单元体积与轮盘体积之比的形式给出，可写为

$$
p _ { i } \ = \ { \frac { V _ { \mathrm { e l e m } i } } { V _ { \mathrm { t o t } } } }
$$

式中：Velemi 单元体积；

$V _ { \mathrm { { t o t } } }$ 轮盘体积。

当然，这是三维分析的计算公式，维分析时需将上式写为单元积与轮盘午面积之比。

可以计算出单元的缺陷临界尺寸 $a _ { 0 i }$ ，只要有尺寸大于 $a _ { 0 i }$ 的缺陷出现在单元中，单元就将在 $N _ { 0 }$ 次循环之前失效，考虑所有尺寸的缺陷，单元在 $N _ { 0 }$ 次循环之前失效的概率可以写为

$$
P _ { \mathrm { { E } } } ( N < N _ { 0 } ) \ = \ 1 \ - \ \prod _ { a _ { i } > a _ { 0 i } } ( 1 - p _ { i } ) ^ { n _ { i } }
$$

单元达到 $N _ { 0 }$ 次循环的可靠度为

$$
R _ { \mathrm { E } } ( N < N _ { 0 } ) \ = 1 - P _ { \mathrm { E } } ( N < N _ { 0 } )
$$

需要特别注意的是表面单元和内部单元失效概率的计算是不同的，因为单元涉及表面、亚表面以及内部等不同区域，失效模式是多样的；而内部单元的失效模式则较为单一，只考虑内部缺陷引起的失效即可。

轮盘可靠度可按下式计算

$$
R _ { \mathrm { D } } ( N < N _ { 0 } ) \ = \ \prod _ { i = 1 } ^ { n } R _ { E i } ( N < N _ { 0 } )
$$

式中： $R _ { \mathrm { p } }$ cd: $N < N _ { 0 } ,$ ) 轮盘达到 $N _ { 0 }$ 次循环的可靠度；

$R _ { \mathrm { E } i }$ d $N < N _ { 0 } )$ 第 $i$ 个单元达到 $N _ { 0 }$ 次循环的可靠度；  
$n$ (i:) 单元总数。

（1）表及内部最应单元的失效概率

粉末盘的弹塑性分析中，9972号表面单元具有最的周向应 $9 1 8 \mathrm { M P a }$ ，位于中孔边；10589号内部单元具有最的周向应力 $8 7 2 \mathrm { M P a }$ ，靠近中心孔边。图9-25中，比较表及内部最应单元的缺陷临界尺寸可以看出，表、亚表缺陷的临界尺寸较，在较循环数下与内部缺陷的临界尺寸相差约个数量级。这说明对于FGH95粉末材料，环境因素（氧化）对裂纹扩展的影响较为显著，表缺陷、划痕等将会严重影响构件的疲劳性能。

![](images/29e1e3e0d6b625b0f05dcd59ac5cff334f6d738a186b09f78656b336a79f1a2e.jpg)  
图9-25 最应单元的缺陷临界尺寸

图9-26中可以看出，在给定的循环范围内（40000个循环以下），内部缺陷引起失效的概率为零，表缺陷将成为破坏的主导因素；而达到较循环范围时（图中并未出），内部缺陷将成为破坏的主导因素，失效概率将显著提。因此，保证粉末盘在工作循环范围内具有较高的可靠度，生产制造过程中表面质量的控制十分重要；由于粉末盘的设计寿命较，对于内部缺陷也必须给予同样的重视。

![](images/a2ca56ca39da650832a06b0390b1311f0a211b0b24d9e77f6ecbde2f38bce5d4.jpg)  
图9-26 最应单元的失效概率

(2）正态分布参数对轮盘可靠度的影响

参考献19，20中给出的缺陷尺寸分布规律，按照正态分布给出组缺陷数量和尺寸的关系，见表9-9，并将它们代模型计算轮盘的可靠度。表中尺寸是按照椭圆长轴给出的，长短轴比为5。

表9-9 缺陷尺寸与数量的分布规律  

<table><tr><td rowspan=2 colspan=1>分布</td><td rowspan=1 colspan=7>尺寸/μm</td></tr><tr><td rowspan=1 colspan=1>50~100</td><td rowspan=1 colspan=1>100~150</td><td rowspan=1 colspan=1>150~200</td><td rowspan=1 colspan=1>200~250</td><td rowspan=1 colspan=1>250~300</td><td rowspan=1 colspan=1>&gt;300</td><td rowspan=1 colspan=1>总数</td></tr><tr><td rowspan=1 colspan=1>X~N（75, 1002)</td><td rowspan=1 colspan=1>77</td><td rowspan=1 colspan=1>77</td><td rowspan=1 colspan=1>60</td><td rowspan=1 colspan=1>36</td><td rowspan=1 colspan=1>17</td><td rowspan=1 colspan=1>6</td><td rowspan=1 colspan=1>273</td></tr><tr><td rowspan=1 colspan=1>X~N（100,1002)</td><td rowspan=1 colspan=1>70</td><td rowspan=1 colspan=1>79</td><td rowspan=1 colspan=1>70</td><td rowspan=1 colspan=1>48</td><td rowspan=1 colspan=1>25</td><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>302</td></tr><tr><td rowspan=1 colspan=1>X~N(125, 1$100{$</td><td rowspan=1 colspan=1>60</td><td rowspan=1 colspan=1>77.</td><td rowspan=1 colspan=1>77</td><td rowspan=1 colspan=1>60</td><td rowspan=1 colspan=1>36</td><td rowspan=1 colspan=1>17</td><td rowspan=1 colspan=1>327</td></tr><tr><td rowspan=1 colspan=1>X~N(75,502)</td><td rowspan=1 colspan=1>140</td><td rowspan=1 colspan=1>140</td><td rowspan=1 colspan=1>51</td><td rowspan=1 colspan=1>7</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>338</td></tr><tr><td rowspan=1 colspan=1>X~N (75, 75²2)</td><td rowspan=1 colspan=1>100</td><td rowspan=1 colspan=1>100</td><td rowspan=1 colspan=1>64</td><td rowspan=1 colspan=1>26</td><td rowspan=1 colspan=1>6</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>297</td></tr></table>

图9-27和图9-28分别给出了正态分布位置参数 $\mu$ 、尺度参数 $\sigma$ 对轮盘可靠度的影响。轮盘中微缺陷数目维持在300个左右的前提下，位置参数由 $7 5 \mu$ 增加到 $1 2 5 \mu$ 时，轮盘可靠度降低；尺度参数由 $5 0 \mu$ 增加到 $1 0 0 \mu$ 时，轮盘可靠度降低；另外，在20000个循环以下，缺陷分布形式对轮盘可靠度的影响很。

![](images/7ae8249074846b980bf483a251fec3acfb98d9d410341c8b0dce34a65222d02b.jpg)  
图9-27 位置参数 $\mu$ 对轮盘可靠度的影响

（3）载荷谱对轮盘可靠度的影响

在发动机不同任务循环下考察缺陷的存在对轮盘可靠度的影响，对发动机轮盘的设计工作很有意义。假定的设计任务循环及相应的轮盘可靠度计算结果见表9-10，计算中最大转速取值为 $4 5 0 0 0 \mathrm { r / m i n }$ ，慢车转速在此基础上下降 $30 \%$ ，缺陷分布采用正态分布 $X \sim N$ （75, $1 0 0 ^ { 2 }$ )。主循环下轮盘的可靠度计算采用最大转速条件下的周向应范围，而次循环下的轮盘可靠度计算则采最转速时的周向应与慢车转速时的周向应之间的差值。分别计算出主循环下的轮盘可靠度及次循环下的轮盘可靠度，进给出该任务循环下的轮盘可靠度。

![](images/5b1fb516c4ebb51dc8d99b40f3866cef05bc9a429a76968ff77a2cf0a7d86232.jpg)  
图9-28 尺度参数 $\sigma$ 对轮盘可靠度的影响

表9-10设计任务循环及轮盘可靠度  

<table><tr><td rowspan=2 colspan=1>循环</td><td rowspan=1 colspan=6>剖面</td></tr><tr><td rowspan=1 colspan=1>No.1</td><td rowspan=1 colspan=1>No.2</td><td rowspan=1 colspan=1>No.3</td><td rowspan=1 colspan=1>No.4</td><td rowspan=1 colspan=1>No.5</td><td rowspan=1 colspan=1>No.6</td></tr><tr><td rowspan=1 colspan=1>零一最大—零</td><td rowspan=1 colspan=1>12000</td><td rowspan=1 colspan=1>15000</td><td rowspan=1 colspan=1>20000</td><td rowspan=1 colspan=1>22000</td><td rowspan=1 colspan=1>24000</td><td rowspan=1 colspan=1>26000</td></tr><tr><td rowspan=1 colspan=1>慢车—最大—慢车</td><td rowspan=1 colspan=1>80000</td><td rowspan=1 colspan=1>100000</td><td rowspan=1 colspan=1>105000</td><td rowspan=1 colspan=1>110000</td><td rowspan=1 colspan=1>115000</td><td rowspan=1 colspan=1>120000</td></tr><tr><td rowspan=1 colspan=1>主循环轮盘可靠度</td><td rowspan=1 colspan=1>0.997193</td><td rowspan=1 colspan=1>0.997193</td><td rowspan=1 colspan=1>0.997117</td><td rowspan=1 colspan=1>0.994558</td><td rowspan=1 colspan=1>0.985510</td><td rowspan=1 colspan=1>0.970800</td></tr><tr><td rowspan=1 colspan=1>次循环轮盘可靠度</td><td rowspan=1 colspan=1>1.000000</td><td rowspan=1 colspan=1>1.000000</td><td rowspan=1 colspan=1>1.000000</td><td rowspan=1 colspan=1>1.000000</td><td rowspan=1 colspan=1>0.999780</td><td rowspan=1 colspan=1>0.998502</td></tr><tr><td rowspan=1 colspan=1>轮盘可靠度</td><td rowspan=1 colspan=1>0.997193</td><td rowspan=1 colspan=1>0.997193</td><td rowspan=1 colspan=1>0.997117</td><td rowspan=1 colspan=1>0.994558</td><td rowspan=1 colspan=1>0.985293</td><td rowspan=1 colspan=1>0.969345</td></tr></table>

从计算结果可以看出，对主循环在15000个循环以前，给定的缺陷分布不会对轮盘可靠度产较的影响；对次循环在100000个循环以前，给定的缺陷分布不会对轮盘可靠度产较的影响。这样，我们就可以采概率模型对设计任务的风险性进行评估。

需要特别说明的是轮盘可靠度计算只考虑了缺陷的概率特征，对于包括材料强度、载荷条件等多种随机性的、更为复杂、更具般性的可靠性分析，并未作为研究重点。应寿命预测概率模型分析了缺陷的分布形式对粉末盘可靠度的影响，计算了给定任务循环下的轮盘可靠度，说明了模型应于粉末材料构件设计的可性。通过计算分析得出了些有意义的结论，为粉末盘件的设计和应用提供了一些借鉴，同时也发现了一些不足和有待解决的问题。

（1）模型可以考察不同的缺陷分布形式（如指数分布、正态分布等）对轮盘可靠度的影响，并针对正态分布进了计算，给出了正态分布参数 $( \mu , \sigma$ ）的变化对轮盘可靠度的影响趋势。

（2）模型可以针对不同的设计任务循环计算轮盘的可靠度，疑这对于尚处于设计阶段的粉末盘，具有定的程指导意义。

（3）量试验表明Rene95的裂纹扩展特性受环境因素的影响较为显著，国内正在研制的相近牌号合FGH95可能存在相同的问题。因此，对于粉末盘件的表质量必须给予足够的重视。

（4）另外还存在些不之处，主要是相关数据的缺乏。计算时FGH95的裂纹扩展参数、缺陷的分布形式、轮盘的载荷谱等必要数据来不同的研究及相关献，数据的相关性很不理想。从前国内粉末材料FGH95的现状来看，收集和整理FGH95的相关试验数据，进必要的试验研究，是推动概率模型程应的前提条件，也是研究这种缺陷敏感性材料的一条有效途径。

# 9.4 基于螺栓孔特征的带缺陷轮盘失效概率分析流程

本节主要针对基于螺栓孔特征的带缺陷轮盘进失效概率分析。先，论述了寿命预测概率模型计算程序的理论基础及分析流程；其次，结合程序对输输出数据及计算流程进了必要说明。

基于加导致的孔缺陷特征的失效概率分析流程，如图9-29所，可以计算出针对某类型孔的轮盘失效概率。

![](images/f8032a4f140b6a5d13ccfebb36060a447bafa0106640062c747727e74fb402b2.jpg)  
图9-29 基于加导致的孔缺陷特征的失效概率分析流程

# 9.4.1 初始缺陷分布概率的确定与修正

通过总结量的试验与程数据可以给出与发动机涡轮盘缺陷尺寸对应的概率分布，如图9-30所，横坐标为缺陷尺寸，纵坐标为单位积上缺陷尺寸于某一确定值的概率，曲线左端点横纵坐标分别代表缺陷的最尺寸以及单位积内产个缺陷的概率，曲线右端点横坐标代表缺陷的最大尺寸。将初始缺陷分布概率以点坐标形式存储于数据件（.txt格式）中导主程序。通过如下公式将缺陷超过数转换为累积概率分布函数。

![](images/668174a2a4f06f06ff0389fd3c66ae0c6252b43cca0e695bd6604b249c6c6bce.jpg)  
图9-30 初始缺陷分布概率

由于孔形状的不同，依照参考献[21，对缺陷发概率做如下修正：圆孔深度 $L$ ，圆孔直径 $D$ ，表征圆孔形状的参数 $L / D$ 与修正系数的关系如图9-31所示。通过式（9-25）求解考虑评分与概率修正因的失效概率，其中 $h _ { \mathrm { c p f } }$ 为种特征中的个孔的失效概率， $S$ 为种特征孔的内部表积， $F _ { \mathrm { ~ c ~ } }$ 为失效概率修正系数， $F _ { \mathrm { c r e d i t } }$ 为评分系数，从可以求得针对种特征孔中的个孔的失效概率。

$$
H _ { \mathrm { p f } } ~ = ~ h _ { \mathrm { c p f } } S F _ { \mathrm { c } } / F _ { \mathrm { c r e d i t } }
$$

![](images/0ab117a9aa7a38a8218c7b64ed64939c8d4f3fb4c9b529a53373de224766bf6a.jpg)  
图9-31 初始缺陷概率修正

# 9.4.2 实际问题的简化与应力分析

飞机在服役过程中涡轮盘的外部载荷是很复杂的，很难将所有的情况统一起来，为了简化计算，现提出以下假设。

（1）将飞机的一次起落用一个应力比为0的循环代替，飞过程中最危险的几个载荷状态对应的应力最大值作为峰值点。

（2）将轮盘从整个发动机结构中分离，先进热分析，然后将结果重新导再进行结构分析，提取需要的应力值作为输入结果。

# 9.4.3 缺陷导致的失效分析与寿命计算

（1）对于缺陷导致的失效，本只针对孔表裂纹进分析，由于失效机理的不同，对于轮盘其他位置处的表裂纹以及轮盘内部裂纹本暂不考虑。

针对缺陷发概率的问题，初始缺陷分布概率仅仅是单位积的缺陷发概率，然缺陷在不同位置进扩展的难易程度是不同的，对于实际模型，如图9-32所，孔附近位置标注如图9-33所， $A , B$ 位置以周向应力为主导， $C$ ( $D$ 位置以径向应力为主导，选取A、 $B$ 位置与 $C , \ D$ 位置处较大应力值作为整个孔的应力值进裂纹扩展分析，有定的近似但结果是偏于保守的、可靠的。最终计算失效概率需要乘以整个孔的面积，这种法对孔内表裂纹的计算是比较准确的，但对于裂纹失效概率的计算欠妥，前本暂且仍采这种法，当然，还有待今后做进步的分析与改进。

![](images/b07f83600cdc0bb339233500438f10e1a991ef7169afb25c863342a2c873c474.jpg)  
图9-32 涡轮盘有限元模型

（2）一般情况，由于缺陷形状的不确定性，假设所有的缺陷可以近似用球形或椭球形空腔代替，再进步结合裂纹的扩展形式，假设缺陷以半圆形裂纹的形式进扩展，并将初始缺陷半圆形裂纹代替，初始缺陷的尺寸作为半圆形裂纹的半径。

本假设孔处表裂纹分为孔边裂纹和孔内面裂纹两种，角裂纹和面裂纹的初始裂纹分别近似等效为孔边1/4圆裂纹和孔内1/2圆裂纹，并分别保持各的形状进裂纹扩展，参考献[22中的应强度因的求解结果，如图9-34和图9-35所。由于初始缺陷相对孔径很，裂纹可以等效为在无限大平板上进扩展，无限大平板受均匀拉应，对于角裂纹和面裂纹拉应分别取值为考核孔孔边和孔内的最大第主应。

![](images/c26f303819ca97a5db1bf77ec3beda578513b9547cfc3a54bab53ddfe2133c05.jpg)  
图9-33 模型轴向孔区域标注

![](images/c6cb01912cb842359fdb2fcb067dcfa5a5ec1b31fdd4e5f0df92a231bc976dd3.jpg)  
图9-34 裂纹受分析意图

![](images/ebc602414030a9c5b2f7eca5d27d10de64a5dff614dc8abe9b1b00f61a56c9c3.jpg)  
图9-35 面裂纹受分析示意图

（3）利用Paris公式进裂纹扩展分析，Paris公式中参数对应的应力为0，并且假设裂纹扩展门槛值为0，当应力强度因子值大于断裂韧度时，判断结构失效。在程序中需要计算对于初始缺陷在经过 $N$ 个循环载荷后的缺陷尺寸，见式（9-26）；并且针对确定初始缺陷，在给定临界断裂因时可以计算出轮盘寿命 $N$ ，见式(9-27)。公式中 $C$ 和 $m$ 分别为Paris公式中的系数与指数， $M$ 为对应的裂纹系数， $N$ 为循环数， $a _ { 0 }$ 为产生的初始缺陷的尺寸， $K _ { \mathrm { c } }$ 为临界断裂因。

$$
a _ { \mathrm { t } } \ = \ \bigg [ \bigg ( 1 \ - \frac { m } { 2 } \bigg ) \bigg ( \frac { 2 \sigma M } { \sqrt { \pi } } \bigg ) ^ { m } C N + a _ { 0 } \ ^ { 1 - \frac { m } { 2 } } \bigg ] ^ { \frac { 1 } { 1 - \frac { m } { 2 } } }
$$

$$
N = { \frac { \left( { \frac { K _ { \mathrm { C } } \ { \sqrt { \pi } } } { 2 \sigma M } } \right) ^ { 2 - m } - a _ { 0 } \ ^ { 1 - { \frac { m } { 2 } } } } { 1 - { \frac { m } { 2 } } } } { \frac { 1 } { C } }  \left( { \frac { 2 \sigma M } { \sqrt { \pi } } } \right) ^ { - m }
$$

（4）由于发动机涡轮盘特有的应分布形式及螺栓孔结构，如图9-36所示，孔表面位置处裂纹主要起裂于1、2、3、4这四个位置，但针对实际情况当偏心孔靠近轮缘时，第一主应力最大值会位于与之垂直的孔表面位置，如图9-33中的C、D位置，具体问题需要仔细分析其应力场，选取较大值分别作为孔表面裂纹与角裂纹的考核应力值。结合裂纹的失效模式，选取第一主应力作为初始应力值，对于实际轮盘1、3位置将产裂纹，2、4位置将产生面裂纹，因而分别选取1、3与2、4第一主应力的较大值计算裂纹和面裂纹的裂纹扩展，实际模型裂纹与面裂纹的最大第一主应力值也会产生在与图中所示相垂直的位置处。

![](images/bee0d7f75569df1883dbaa9da3de29293c9ca48e8a41376fa2a082d1adee3eeb.jpg)  
图9-36 裂纹与裂纹分析示意图

# 9.4.4 制造评分与失效概率修正

制造评分的制定来量的发动机制造者经验，本参考献[21]中给出的制造评分内容见表9-11。本制造评分选为5。

表9-11 制造评分  

<table><tr><td rowspan=1 colspan=1>控制过程</td><td rowspan=1 colspan=1>定义</td><td rowspan=1 colspan=1>评分</td></tr><tr><td rowspan=1 colspan=1>过程确认</td><td rowspan=1 colspan=1>在此过程需要确认制造过程提供与设计要求致的零件，并且包括加完成后对零件何缺陷的检测（裂纹、划痕、凹陷、刻痕等）</td><td rowspan=1 colspan=1>5</td></tr><tr><td rowspan=1 colspan=1>单点镗孔</td><td rowspan=1 colspan=1>使用单点镗孔具通过精加除去表浅层材料的操作，至少0.004in深，但这种评分仅仅适于钛合材料</td><td rowspan=1 colspan=1>5</td></tr><tr><td rowspan=1 colspan=1>珩磨</td><td rowspan=1 colspan=1>通过动定磨削操作去除表浅层材料，深度少为0.002in，适于所有材料</td><td rowspan=1 colspan=1>5</td></tr><tr><td rowspan=1 colspan=1>冷却剂监控</td><td rowspan=1 colspan=1>种对冷却剂压进周期性检测的装置以及操作者对冷却剂浓度的监控从而使得其流动方向指向切削边，这种评分适用于所有材料</td><td rowspan=1 colspan=1>5</td></tr><tr><td rowspan=1 colspan=1>功率监控</td><td rowspan=1 colspan=1>种可以连续监控机器功率消耗的装置，由于刀具磨损或者冷却剂不等原因都会导致机器功率增加，并且对于所有材料都适</td><td rowspan=1 colspan=1>20</td></tr><tr><td rowspan=1 colspan=1>进给力监控</td><td rowspan=1 colspan=1>种可以连续监控机器进给的装置，由于刀具磨损或者冷却剂不等原因都会导致机器进给增加，并且对于所有材料都适</td><td rowspan=1 colspan=1>20</td></tr><tr><td rowspan=1 colspan=1>检测</td><td rowspan=1 colspan=1>仅仅包含材料腐蚀面的检测，适用于所有材料</td><td rowspan=1 colspan=1>5</td></tr></table>

除了表9-11中的相关要求，还有些必要的评分准则需要指出。

（1）对于所有的加过程都应包含“过程确认”这控制过程。

（2）功率控制与进给控制分别存在时，评分分别取20，当两者同时存在时两者总评分取30。

（3）冷却剂监控、功率监控以及进给监控是针对包括粗加与精加的整个加工过程而言的。

(4）采功率控制与进给控制必须以冷却剂监控为前提。

（5）单点钻孔与珩磨两者不可以同时存在。

# 9.4.5 轮盘缺陷检测与剔除

参考献[21中分别列出了涡流探伤与荧光渗透剂检验两种检验式与检验平，如图9-37和图9-38所示，本选取涡流探伤的数据作为检测标准，以数据（.txt格式）文件的形式导到程序，然而针对实际情况，检测条件与检测平往往存在较大的差异，需要结合国内相关标准与企业实际情况，选取合适的检测概率曲线作为检测标准。在编程中，通过产0\~1之间的随机数，从而再通过缺陷检测累积概率分布函数求得最小检测尺寸。

![](images/38dcb3086644975831367e901f6116cd5170c29037d01ba8086bcd0778be66cc.jpg)  
图9-37 $50 \%$ 置信度电涡流检验平

![](images/86e5c3796822a9a149db9be1f701dd28ca7ce9e52aa92471a86013da86b4ec8a.jpg)  
图9-38 $50 \%$ 置信度荧光渗透剂检验水平

对于单次检测，子样剔除方式主要分为两种：缺陷被检测到即剔除；缺陷被检测到并且作时间小于预期服役寿命即剔除。对于多次检测，子样剔除方式也分为两种：缺陷被检测到即剔除；缺陷被检测到并且作时间于下次检测时间即剔除（程序前只有单次检测方案）。最终结果为循环数与失效概率的对应关系，失效概率由失效数除以总样数得到，当剔除个样时，失效数减，总样数不变。

# 9.4.6检测与方案改进

可以参照参考文献[21进设计与检测案修订，在设计初始，往往需要确定设计标风险值，由于加条件的限制以及为等因素，机械加法保证所有的产品都是百分之百可靠的，因而对于特定的组件以及特定的失效模式允许一定的失效率。本文设计标风险（design targetrisk，DTR）取为 $2 \times 1 0 ^ { - 5 }$ ，需要说明，此处的DTR仅仅针对圆孔表位置缺陷，包括材料初始缺陷以及制造引起的缺陷。

在设计初始，计算不带检验的失效概率并与DTR进比较，当满设计标风险值时，设计满要求；当不满设计标风险值时，可以考虑重新进设计，也可以考虑增加并选择合适的检测案，通过选择检测对象、检测时间（前程序只适于次检测）、检测法使得失效概率于设计标风险值。需根据实际情况确定检测时间使得失效概率最，由于实际状况的限制，检测时间往往不是确定值，本假设检测时间满正态分布。

# 9.5 涡轮盘实例分析

建个典型的概率寿命分析算例，并对其结果进详细分析，具体步骤如下：

（1）给定材料的缺陷分布规律以及修正规律；  
（2）给定材料的裂纹扩展规律；  
（3）给定检测水平与相应的检测方法；  
(4）给定材料参数与结构载荷。

# 9.5.1 初始缺陷分布概率的确定与修正

初始缺陷分布采参考献[21中的数据，将初始缺陷分布概率图中曲线取点输到Damage_depth_P.txt件并导程序中，见表9-12。

表9-12 单位面积初始缺陷分布概率  

<table><tr><td rowspan=1 colspan=1>缺陷尺寸/cm</td><td rowspan=1 colspan=1>单位面积超过概率/(1/cm2)</td><td rowspan=1 colspan=1>缺陷尺寸/cm</td><td rowspan=1 colspan=1>单位面积超过概率/(1/cm2)</td></tr><tr><td rowspan=1 colspan=1>0.00254</td><td rowspan=1 colspan=1>7.93×10-7</td><td rowspan=1 colspan=1>0.0596</td><td rowspan=1 colspan=1>1.98×10-7</td></tr><tr><td rowspan=1 colspan=1>0.00337</td><td rowspan=1 colspan=1>7.79×10-7</td><td rowspan=1 colspan=1>0.0728</td><td rowspan=1 colspan=1>1.43×10-7</td></tr><tr><td rowspan=1 colspan=1>0.00424</td><td rowspan=1 colspan=1>7.56×10-7</td><td rowspan=1 colspan=1>0.0867</td><td rowspan=1 colspan=1>1.03×10-7</td></tr><tr><td rowspan=1 colspan=1>0.00520</td><td rowspan=1 colspan=1>7.41×10-7</td><td rowspan=1 colspan=1>0.107</td><td rowspan=1 colspan=1>6.15×10-8</td></tr><tr><td rowspan=1 colspan=1>0.00627</td><td rowspan=1 colspan=1>7.24×10-7</td><td rowspan=1 colspan=1>0.118</td><td rowspan=1 colspan=1>4.75×10-8</td></tr><tr><td rowspan=1 colspan=1>0.00772</td><td rowspan=1 colspan=1>7.01×10-7</td><td rowspan=1 colspan=1>0.135</td><td rowspan=1 colspan=1>3.10×10-8</td></tr><tr><td rowspan=1 colspan=1>0.0101</td><td rowspan=1 colspan=1>6.64×10-7</td><td rowspan=1 colspan=1>0.154</td><td rowspan=1 colspan=1>1.97×10-8</td></tr><tr><td rowspan=1 colspan=1>0.0130</td><td rowspan=1 colspan=1>6.13×10-7</td><td rowspan=1 colspan=1>0.172</td><td rowspan=1 colspan=1>1.27×10-8</td></tr><tr><td rowspan=1 colspan=1>0.0169</td><td rowspan=1 colspan=1>5.61×10-7</td><td rowspan=1 colspan=1>0.188</td><td rowspan=1 colspan=1>8.58×10-9</td></tr><tr><td rowspan=1 colspan=1>0.0206</td><td rowspan=1 colspan=1>5.05×10-7</td><td rowspan=1 colspan=1>0.211</td><td rowspan=1 colspan=1>4.97×10-9</td></tr><tr><td rowspan=1 colspan=1>0.0259</td><td rowspan=1 colspan=1>4.47×10-7</td><td rowspan=1 colspan=1>0.227</td><td rowspan=1 colspan=1>3.31×10-9</td></tr><tr><td rowspan=1 colspan=1>0.0332</td><td rowspan=1 colspan=1>3.74×10-7</td><td rowspan=1 colspan=1>0.244</td><td rowspan=1 colspan=1>2.22×10-9</td></tr><tr><td rowspan=1 colspan=1>0.0407</td><td rowspan=1 colspan=1>3.15×10-7</td><td rowspan=1 colspan=1>0.253</td><td rowspan=1 colspan=1>1.81×10-9</td></tr><tr><td rowspan=1 colspan=1>0.0504</td><td rowspan=1 colspan=1>2.48×10-7</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr></table>

表征圆孔形状的参数 $L / D$ 与修正频率关系数据同样参见参考献[21，将献中$L / D$ 修正图中的曲线取点输入到Fc_correction.txt件并导程序中，见表9-13。

表9-13 修正频率系数与参数 $L / D$ 的对应关系  

<table><tr><td rowspan=1 colspan=1>L/D</td><td rowspan=1 colspan=1>修正频率系数</td><td rowspan=1 colspan=1>L/D</td><td rowspan=1 colspan=1>修正频率系数</td></tr><tr><td rowspan=1 colspan=1>0.700261</td><td rowspan=1 colspan=1>0.04</td><td rowspan=1 colspan=1>1.21733</td><td rowspan=1 colspan=1>0.402216</td></tr><tr><td rowspan=1 colspan=1>1.0135</td><td rowspan=1 colspan=1>0.04</td><td rowspan=1 colspan=1>1.23312</td><td rowspan=1 colspan=1>0.480055</td></tr><tr><td rowspan=1 colspan=1>1.03523</td><td rowspan=1 colspan=1>0.0462604</td><td rowspan=1 colspan=1>1.24709</td><td rowspan=1 colspan=1>0.557341</td></tr><tr><td rowspan=1 colspan=1>1.05869</td><td rowspan=1 colspan=1>0.0648199</td><td rowspan=1 colspan=1>1.25745</td><td rowspan=1 colspan=1>0.626316</td></tr><tr><td rowspan=1 colspan=1>1.08095</td><td rowspan=1 colspan=1>0.0839335</td><td rowspan=1 colspan=1>1.26884</td><td rowspan=1 colspan=1>0.704709</td></tr><tr><td rowspan=1 colspan=1>1.10173</td><td rowspan=1 colspan=1>0.108864</td><td rowspan=1 colspan=1>1.27738</td><td rowspan=1 colspan=1>0.77313</td></tr><tr><td rowspan=1 colspan=1>1.1214</td><td rowspan=1 colspan=1>0.134626</td><td rowspan=1 colspan=1>1.28619</td><td rowspan=1 colspan=1>0.852909</td></tr><tr><td rowspan=1 colspan=1>1.13926</td><td rowspan=1 colspan=1>0.167036</td><td rowspan=1 colspan=1>1.29301</td><td rowspan=1 colspan=1>0.919945</td></tr><tr><td rowspan=1 colspan=1>1.15478</td><td rowspan=1 colspan=1>0.199446</td><td rowspan=1 colspan=1>1.29845</td><td rowspan=1 colspan=1>0.970914</td></tr><tr><td rowspan=1 colspan=1>1.17678</td><td rowspan=1 colspan=1>0.256787</td><td rowspan=1 colspan=1>1.30233</td><td rowspan=1 colspan=1>1</td></tr><tr><td rowspan=1 colspan=1>1.19904</td><td rowspan=1 colspan=1>0.32964</td><td rowspan=1 colspan=1>1.49664</td><td rowspan=1 colspan=1>1</td></tr></table>

# 9.5.2 实际问题的简化与应分析

涡轮盘材料为直接时效GH4169，叶材料为DZ125。在轴对称模型分析的基础上，对涡轮盘进三维循环对称模型分析。轮盘上共装有72叶，先建与维轴对称模型致相同格密度的1/72扇区有限元模型，如图9-39所示。根据给定的维温度场获得对应的三维涡轮盘扇区的温度场，然后施加边界条件进应求解。

![](images/1019628d5cee2f6d96e53e68fee99646331dfd644c619a488e6c6a5daa4ed49d.jpg)  
图9-39 轮盘1/72扇区有限元模型

应分析单元选六体节点实体单元（ANSYS中的solid45），采默认的单元选项，进行线弹性计算，具体过程如下。

# （1）施加载荷

有限元分析模型不包括叶模型，因此将叶产的离等效为轮盘榫槽表的法向压力，施加表面压力边界条件，将叶片离心力的 $60 \%$ 施加于第1对榫齿的接触面，将 $40 \%$ 叶载荷施加于第2对榫齿的接触面，如图9-40所。

# (2）位移边界条件

对组件之间的装配连接和接触位置按照给定径向位移和轴向位移（对应位置由轴对称计算结果线性插值给出）施加位移边界条件，需要指出的是，为防止周向出现刚体位移，对涡轮盘与前轴螺栓连接位置处的（281号）节点给定周向位移为零，但是这样的约束会导致该节点的周向应力值出现较大的应力集中，提取结果时可忽略此处的应力集中。

# (3）温度

根据给定的维温度场获得对应的三维涡轮盘扇区的温度场，结果如图9-41所。

![](images/542a5a475f007acf0e363599389588ca413288f5bc30fe8562dec0dc2adfe1c8.jpg)  
图9-40 边界条件示意图

![](images/090922270543220f80a4ec3309c5acf698b0b25915df35825333564d6646044e.jpg)  
图9-41 涡轮盘温度场示意图（单位： $\mathcal { C }$ )

（4）盘腔压力

根据给定的二维盘腔表面压力值可以获得对应的三维涡轮盘扇区的盘腔表面压力值。有限元分析的边界条件施加位置如图9-40所，主要包括位移、转速、表面法向压三种边界条件。

计算结果如图9-42\~图9-44所，各危险部位及应计算结果见表9-14。

![](images/37609d402f49c3ee25be95f971a07b48844c36068b37d5ae90c70683b15cdd83.jpg)  
图9-42 径向应分布

![](images/b17aaf396f40ab897a2dd4e4fbb4659baa315502649dc46b7a49ec53b177ce64.jpg)  
图9-43 周向应力分布

![](images/2d25a783fb817b0d3a57ad3bea048e4225ef42cb0cfbfde297efaa35795efbdd.jpg)  
图9-44 第主应力分布

MPa

表9-14涡轮盘循环对称模型危险点及应力计算结果  

<table><tr><td rowspan=1 colspan=1>危险位置</td><td rowspan=1 colspan=1>节点号</td><td rowspan=1 colspan=1>温度/℃</td><td rowspan=1 colspan=1>径向应力</td><td rowspan=1 colspan=1>周向应力</td><td rowspan=1 colspan=1>第一主应力</td><td rowspan=1 colspan=1>等效应力</td></tr><tr><td rowspan=1 colspan=1>盘心</td><td rowspan=1 colspan=1>44029</td><td rowspan=1 colspan=1>481.48</td><td rowspan=1 colspan=1>11.707</td><td rowspan=1 colspan=1>956.17</td><td rowspan=1 colspan=1>956.17</td><td rowspan=1 colspan=1>1107.9</td></tr><tr><td rowspan=1 colspan=1>螺栓孔边 （内部)</td><td rowspan=1 colspan=1>39939</td><td rowspan=1 colspan=1>613.39</td><td rowspan=1 colspan=1>1230.2</td><td rowspan=1 colspan=1>202.98</td><td rowspan=1 colspan=1>1265.7</td><td rowspan=1 colspan=1>1111.6</td></tr><tr><td rowspan=1 colspan=1>螺栓孔边（角位置）</td><td rowspan=1 colspan=1>30636</td><td rowspan=1 colspan=1>613.48</td><td rowspan=1 colspan=1>102.10</td><td rowspan=1 colspan=1>841.38</td><td rowspan=1 colspan=1>868.05</td><td rowspan=1 colspan=1>773.46</td></tr></table>

可以发现在螺栓孔边起主导的应力为径向应力，其次为周向应力，并且径向应力与第一主应接近，见表9-14，选取第主应作为考核应力，并且沿轴向，孔内第一主应力值最大取为 $1 2 6 5 . 7 \mathrm { M P a }$ ，将此值作为孔内面裂纹的考核应力，结合图9-42，孔边应力较小，取 $7 0 0 \mathrm { M P a }$ 作为孔边裂纹的考核应。

为便分析，做如下定义，将径向坐标最大处定义为12点钟区域，将径向坐标最处定义为6点钟区域，位于两区域中间的孔边两区域分别为3点钟和9点钟区域。程序将孔位置表缺陷等同对待，然结合简化的缺陷模型可以发现，12点钟与6点钟区域的缺陷相3点钟和9点钟区域不容易扩展，因为12点钟和6点钟区域缺陷扩展起主要作用的为周向应力，然而此区域的周向应力最大值近似为 $6 0 0 \mathrm { M P a }$ ，裂纹扩展速度远于3点钟和9点钟区域，因将四个区域的缺陷等同对待是妥的。但是本仅仅针对轴向孔分析，未考虑径向孔的情况，实际孔的应分布形式不只限于这一种情况，具体情况需要具体分析，暂且仍将四个区域等同对待，这样是偏于保守的，当然程序有待进一步改进。

针对应强度因的求解参见参考献[22，由于应为0，应强度因求解公式为 $\Delta K = \frac { M \sigma \sqrt { \pi a } } { \pi / 2 }$ (id 其中 $\sigma$ 为考核点应力（本文取第一主应力） $1 2 6 5 . 7 \mathrm { M P a }$ ,a为当前裂纹长度（单位： $\mathrm { m m }$ ), $M$ 为应力强度因子系数，与缺陷形式和受力状态有关，针对本实例，裂纹 $M$ 取为1.3，面裂纹 $M$ 取为1.05。

将飞机次起落近似等效为个循环，由于试验数据的匮乏，暂且将Paris公式作为裂纹扩展预测模型，且采用应力比 $R = 0 , 1$ 的相关试验数据作为应力比 $R = 0$ 的近似，相关公式拟合参数见表9-15。

表9-15 Paris公式参数  

<table><tr><td rowspan=1 colspan=1>应力比R</td><td rowspan=1 colspan=1>C/ (m/cycle)</td><td rowspan=1 colspan=1>指数m</td></tr><tr><td rowspan=1 colspan=1>0.1</td><td rowspan=1 colspan=1>1.85×10-11</td><td rowspan=1 colspan=1>2.78</td></tr><tr><td rowspan=1 colspan=1>-1</td><td rowspan=1 colspan=1>1.58×10-12</td><td rowspan=1 colspan=1>3.79</td></tr></table>

# 9.5.3 缺陷导致的失效分析与寿命计算

（1）关于制造评分的确定，本实例中，只有过程确认这项内容，总评分为5。输件Feature_hole_input.txt中的内容，见表9–16。

表9-16 特性与受  

<table><tr><td rowspan=1 colspan=1>孔类型序号</td><td rowspan=1 colspan=1>孔深度/m</td><td rowspan=1 colspan=1>孔直径/m</td><td rowspan=1 colspan=1>角裂纹应力值/MPa</td><td rowspan=1 colspan=1>面裂纹应力值/MPa</td><td rowspan=1 colspan=1>圆孔个数</td><td rowspan=1 colspan=1>制造评分</td></tr><tr><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>0.031</td><td rowspan=1 colspan=1>0.00635</td><td rowspan=1 colspan=1>700</td><td rowspan=1 colspan=1>1265.7</td><td rowspan=1 colspan=1>72</td><td rowspan=1 colspan=1>5</td></tr></table>

（2）假设轮盘总的服役寿命为20000个循环，在 $0 \sim 2 0 0 0 0$ 个循环间等分为10个时间段，在每一个时间节点计算其失效概率。在计算之初需要设定合适的蒙特卡罗模拟次数，本程序将缺陷产、缺陷检测时间和缺陷检测平综合在次蒙特卡罗抽样中，并且结合参考献[21对于蒙特卡罗法模拟次数的要求，理论上蒙特卡罗次数应与风险平相关，应比次失效发对应的总样数两个数量级。但通过计算发现，当蒙特卡罗法模拟次数增加到定值时，结果基本稳定，同时为了不使计算时间过长，本文实例中蒙特卡罗方法模拟次数为 $1 0 ^ { 6 }$ o

(3）带检测与不带检测情况需要分别加以计算，计算结果存储于final_result.txt件中。

# 9.5.4 轮盘检验与剔除

（1）检测概率（probability of detection，POD）检测数据取参考献[21中的电涡流检测数据，保存于输入文件inspection_ $\mathrm { P O D } _ { - }$ distribution. txt 中，见表9–17。

表9-17 POD检测数据  

<table><tr><td colspan="1" rowspan="1">缺陷长度/mils</td><td colspan="1" rowspan="1">POD/%</td><td colspan="1" rowspan="1">缺陷长度/mils</td><td colspan="1" rowspan="1">POD/%</td></tr><tr><td colspan="1" rowspan="1">24.60</td><td colspan="1" rowspan="1">0</td><td colspan="1" rowspan="1">30.6998</td><td colspan="1" rowspan="1">4.99868</td></tr><tr><td colspan="1" rowspan="1">24.65</td><td colspan="1" rowspan="1">0.0263089</td><td colspan="1" rowspan="1">32.3944</td><td colspan="1" rowspan="1">7.84004</td></tr><tr><td colspan="1" rowspan="1">25.792</td><td colspan="1" rowspan="1">0.973428</td><td colspan="1" rowspan="1">35.5072</td><td colspan="1" rowspan="1">14.1542</td></tr><tr><td colspan="1" rowspan="1">28.0501</td><td colspan="1" rowspan="1">2.31518</td><td colspan="1" rowspan="1">38.1051</td><td colspan="1" rowspan="1">21.1786</td></tr><tr><td colspan="1" rowspan="1">40.3412</td><td colspan="1" rowspan="1">28.0453</td><td colspan="1" rowspan="1">61.2837</td><td colspan="1" rowspan="1">85.3197</td></tr><tr><td colspan="1" rowspan="1">41.9294</td><td colspan="1" rowspan="1">33.7543</td><td colspan="1" rowspan="1">66.2863</td><td colspan="1" rowspan="1">91.1339</td></tr><tr><td colspan="1" rowspan="1">44.2826</td><td colspan="1" rowspan="1">41.4891</td><td colspan="1" rowspan="1">73.4284</td><td colspan="1" rowspan="1">96.0274</td></tr><tr><td colspan="1" rowspan="1">46.7676</td><td colspan="1" rowspan="1">49.8553</td><td colspan="1" rowspan="1">79.5441</td><td colspan="1" rowspan="1">98.0795</td></tr><tr><td colspan="1" rowspan="1">49.8562</td><td colspan="1" rowspan="1">59.5896</td><td colspan="1" rowspan="1">85.1611</td><td colspan="1" rowspan="1">99.0003</td></tr><tr><td colspan="1" rowspan="1">52.9888</td><td colspan="1" rowspan="1">68.5872</td><td colspan="1" rowspan="1">89.8899</td><td colspan="1" rowspan="1">100</td></tr><tr><td colspan="1" rowspan="1">56.6253</td><td colspan="1" rowspan="1">77.0587</td><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1"></td></tr></table>

（2）检测法存储于inspection_time_distribution.txt中（本暂且持次检验），并且检测到缺陷即剔除，检测案见表9–18。

表9-18 检测方案  

<table><tr><td rowspan=1 colspan=1>检测序号</td><td rowspan=1 colspan=1>检测周期（循环）</td><td rowspan=1 colspan=1>平均值</td><td rowspan=1 colspan=1>标准差</td></tr><tr><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>10000</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>0.2</td></tr></table>

# 9.5.5计算结果及分析

本蒙特卡罗模拟次数为 $1 0 ^ { 6 }$ ，通过比较发现蒙特卡罗模拟次数进步增加对结果的影响很小，但计算时间会大大增加，因而选取 $1 0 ^ { 6 }$ 作为模拟次数。在直角坐标系下和半对数坐标系下的孔内表裂纹与孔裂纹的失效概率分别如图9-45和图9-46所示，两种缺陷类型分别独立处理，在本文给定的检测水平与检测方法的基础上，可以发现缺陷失效概率在经过检测后有一定程度的下降。

![](images/207cd71b321494f72e44a27137560ebb4454abb288f2ed32b7b56ef4a0807820.jpg)  
图9-45 考虑孔处缺陷的轮盘失效概率分析结果

![](images/e92c1da91f542943f76f633752e6d45336d608e32c8f699eed0799dc04b5f275.jpg)  
图9-46 半对数坐标下考虑孔处缺陷的轮盘失效概率分析结果

通过数据输、计算以及结果分析这一完整的运流程，可以得出如下结论：程序运情况良好，可以实现预期的计算功能；算例结果表明计算程序可以定量地分析材料缺陷所引起的破坏概率，计算结果具有程参考价值。

当然还存在些不：将裂纹与裂纹的考核应分别孔内与孔边第主应最值来代替，结果与实际有定误差，但结果偏于保守；程序将裂纹与裂纹分别以1/4圆和1/2圆作为等效，且裂纹保持相同的形状进行扩展，因而对应力强度因子的求解有定的近似；程序中判断结构失效的准则为应强度因与断裂韧性的关系，然对于实际结构是存在一定偏差的。虽然从规律性看，计算结果与献的分析结果致，体现了程序计算结果的合理性，但针对直接时效GH4169温合的验证数据较为缺乏，仍需进步验证。数据输、输出式较为简单，部分功能有待完善，界面也有待改进。

# 9.6小结

本章建了基于缺陷概率分布特征的寿命预测概率模型，希望从寿命预测度探讨粉末材料的夹杂物问题。由于国内相关数据的缺乏，在分析过程中采了些假设，并选了套国外的数据，对粉末材料的失效概率分析表明本章建的概率模型是有效的、可的。但要使模型达到程应的平，需要量的试验研究作为持，涉及含缺陷材料的疲劳试验、裂纹扩展试验以及通过损检测获得缺陷的分布规律等多的作。本章重点分析了试样的概率寿命，但此寿命预测思路对于构件也同样适，只是还需要考虑构件形状、复杂的多轴应状态等诸多因素。

将粉末材料的寿命预测概率模型与有限元计算分析相结合，分析了粉末盘的可靠性问题，这也是本章研究的侧重点。需要特别说明的是轮盘可靠度计算只考虑了缺陷的概率特征，对于包括材料强度、载荷条件等多种随机性的、更为复杂、更具般性的可靠

性分析，并未做重点研究。

对基于螺栓孔特征的带缺陷轮盘进了失效概率分析，轮盘上螺栓孔位置处的缺陷不能等同于一般缺陷，对缺陷的位置、缺陷大小、缺陷检测水平与缺陷产生概率进行分析，并通过选取合适的裂纹扩展方法，得到螺栓孔位置处缺陷对应轮盘的寿命，并结合蒙特卡罗模拟得到轮盘的失效概率。

根据计算结果及分析可以得出如下结论。

（1）所建的粉末材料寿命概率分析模型较好地表征了材料缺陷所引起的失效概率。模型以裂纹扩展公式作为纽带，可以与试验条件较好地相互关联；将缺陷的分布特征引概率破坏模型，使得模型同时可以考察缺陷的尺寸、位置、数量，以及形状对失效概率的影响；还能够计算由于外载变化、试样形状变化所引起的失效概率的变化。与传统粉末材料的破坏研究相，概率模型有以下优点：其，更有利于反映粉末材料破坏的特点，即对小缺陷的敏感性引起的接近脆性的断裂；其，可以反映出不同艺条件下缺陷尺寸、形状、数量等概率分布特点对破坏的影响。当然也存在些不：关于亚表面位置的界定仍需深研究，一些相关的定义尚需逐渐完善；为便于分析将缺陷假定为圆形及半圆形，可能与实际情况存在较大差别，有待于进一步改进；最为重要的点是由于没有找到合适的试验数据，对保载条件及加载频率的影响未进计算分析，而有研究表明这两个因素是影响裂纹扩展速率的重要原因。

（2）粉末合是一种强度低韧性材料，艺特点决定了其对缺陷敏感的特性，因此粉末材料的寿命预测应该从微缺陷手。从国内粉末材料寿命研究的现状来看，一方面，进小裂纹扩展试验，开展构件的损伤容限研究十分必要；另一方面，以概率断裂学为基础的基于缺陷分布特征的概率法对传统定寿法将是一个很好的完善。

（3）概率模型的分析表明：低循环条件下，失效易发在表面或亚表，而在循环条件下，失效易发生在内部，这与许多文献的研究结果是一致的；通过对缺陷各向异性的分析可以看出，在盘坯径向取样试样的疲劳性能要远远优于轴向取样试样，这与参考献[37，38]中的结论是致的；应范围的降低使临界循环数增加，失效概率的减小较为显著；对于内部缺陷，在一定循环数以后，将导致失效概率迅速增加；当缺陷数量增加时，失效概率明显上升。

（4）对于尺寸的试样而，表面、亚表面的缺陷较为危险；对于尺寸的构件，内部缺陷同样会对寿命产较大影响。尺寸效应对表面缺陷引起失效的概率影响较，采用尺寸试样的试验结果预测大尺寸构件的寿命还存在问题。

（5）建并完善了基于螺栓孔特征的带缺陷轮盘失效概率分析流程，对程设计中轮盘结构的失效概率计算分析与检测时间的选取和设置有定的指导意义。

# 参考文献

[1] Hyzak J M, Bernstein I M. The effect of defects on the fatigue crack initiation process in two P/M superalloys: part I. fatigue origins [J]. Metallurgical Transactions, 1982,

13A：33-43.   
[2] Hyzak J M, Bernstein I M. The effect of defects on the fatigue crack initiation process in two P/M superalloys: part II. surface – subsurface transition [J]. Metallurgical Transactions,1982,13A:45–52.   
[3] Pelloux R M, Romanoski G R, Feng J. Study of the fatigue behavior of short cracks in nickel– base superalloys [R]. $\mathrm { A F 0 5 R - T R } - 8 6 - 0 2 2 4$ ,1986.   
[4] Pelloux R M, Feng J, Romanoski G R. Study of the fatigue behavior of small cracks in nickel–base superalloys [R]. AFOSR–TR–88–0457, 1988.   
[5] Brückner– Foit A, Jackels H. Prediction of the lifetime distribution of high - strength components subjected to fatigue loading [J]. Fatigue Fract. Engng. Mater. Struct., 1993,16(8):891-908.   
[6] Bussac A de, Lautridou J C. A probabilistic model for prediction of LCF surface crack initiation in PM alloys [J]. Fatigue Fract. Engng Mater. Struct., 1993, 16 (8): 861– 874.   
[7] Bussac A de. Prediction of the competition between surface and internal fatigue crack initiation in PM alloys [J]. Fatigue Fract. Engng Mater. Struct., 1994, 17 (11 ): 1319–1325.   
[8] Grison J, Remy L. fatigue failure probability in a powder metalurgy ni – base superalloy [J]. Engineering Fracture Mechanics, 1997, 57 (1): 41–55   
[9] Goswami T. Development of generic creep – fatigue life prediction models [J]. Materials and Design, 2004, 25:277–288.   
[10]中国航空研究院.应强度因册（增订版） M]．北京：科学出版社， 1981.   
[11] 聂景旭.断裂学理论及其在发动机上的应[M．北京：北京航空学院， 1985.   
[12] Murakami Y, Endo M. Effct of defects, inclusions and inhomogeneities on fatigue Strength [J]. Fatigue, 1994, 16: 163–182.   
[13] Murakami Y, Kodama S, Konuma S. Quantitative evaluation of effects of non –metallic inclusions on fatigue strength of high strength steels. I: basic fatigue mechanism and evaluation of correlation between the fatigue stress and the size and location of non– metallic inclusions [J]. Int. J. Fatigue, 1989, 11 (5): 291–298.   
[14《中国航空材料册》编辑委员会.中国航空材料册第5卷[M．北京：中国 标准出版社，2002：29-43.   
[15邹，汪武祥．粉末温合中夹杂物特性及其质量控制[J．材料科学与 艺，1999(7)：7-11.   
[16]国为民，吴剑涛，张凤，等．FGH95镍基温合粉末中的夹杂及其对合疲 劳性能的影响[J].粉末冶金工业，2000，10(3）：23-28.   
[17]陈光，《航空发动机设计册》总编委会.航空发动机设计册（第3册)：可靠

性及维修性[M]．北京：航空工业出版社，2000.[18]孔瑞莲．航空发动机可靠性程[M]．北京：航空业出版社，1996.[19]张莹，李世魁，陈.等离旋转电极法制取镍基温合粉末[J．粉末冶金工业，1998，8（6）：17-22.[20]张莹，张锡，张义，等．镍基温合粉末筛分艺的研究[J．粉末冶业，2002，12(5）：24-27.[21] Damage tolerance of hole feature in high – energy turbine engine rotors [R]. FederalAviation Administration, Washington, DC, 2009.[22]应强度因册[M]．北京：科学出版社，1981：359-373.