import pandas as pd
import numpy as np
from WindPy import w
import matplotlib.pyplot as plt
from matplotlib import rcParams
import seaborn as sns
import datetime
from scipy import stats
sns.set(font_scale=1.5)
sns.set(font="KaiTi")
rcParams['font.family'] = 'KaiTi'
plt.rcParams['axes.unicode_minus'] =False
import warnings
warnings.filterwarnings('ignore')

w.start()

source_dir = input("结果保存路径为:")

# print("依次输入最近一期时间点与上一期时间点:")
# obs_time,pre_time = map(str,input().split())

f = open(source_dir + "参数.txt", mode="r")
line = f.read()
line = line.split()

save_dir = line[1]
obs_time,pre_time = line[2], line[3]

upstream = [
'黑色金属矿采选业',
'有色金属矿采选业',
'石油和天然气开采业',
'煤炭开采和洗选业',
'非金属矿采选业'
]

midstream = [
'计算机、通信和其他电子设备制造业',
'黑色金属冶炼及压延加工业',	
'金属制品业',
'通用设备制造业',
'有色金属冶炼及压延加工业',		
'专用设备制造业',
'仪器仪表制造业',
'电气机械及器材制造业',
'橡胶和塑料制品业',
'石油、煤炭及其他燃料加工业',
'化学原料及化学制品制造业',
'化学纤维制造业',
'造纸及纸制品业',
'非金属矿物制品业'
]

downstream = [
'铁路、船舶、航空航天和其他运输设备制造业',
'汽车制造业',		
'木材加工及木、竹、藤、棕、草制品业',		
'家具制造业',
'农副食品加工业',		
'食品制造业',
'酒、饮料和精制茶制造业',
'烟草制品业',
'医药制造业',		
'纺织业',
'纺织服装、服饰业',
'皮革、毛皮、羽毛及其制品和制鞋业',
'印刷业和记录媒介的复制',
'文教、工美、体育和娱乐用品制造业',
]
###################################################################################
a=pd.read_excel(source_dir + 'en_cn.xlsx', sheet_name=8)
b= a['指标ID'].to_list()
a['指标名称'] = a['指标名称'].str[3:-9]
stock_name_map = a.set_index(['指标ID'])['指标名称'].to_dict()
stock_raw = w.edb(b,beginTime='2011-01-01',usedf = True)
stock_raw = stock_raw[1]

stock = stock_raw.apply(lambda x: pd.qcut(x, 3, labels=[-1,0,1])) # 三等分
stock.reset_index(level=0, inplace=True)
stock.rename(columns={'index':'time'},inplace=True)
stock.rename(columns=stock_name_map, inplace=True) # 将识别代码换为中文名称

a=pd.read_excel(source_dir + 'en_cn.xlsx', sheet_name=2)
b= a['指标ID'].to_list()
a['指标名称'] = a['指标名称'].str[7:-5]
ppi_name_map = a.set_index(['指标ID'])['指标名称'].to_dict()

ppi_raw = w.edb(b,'2011-01-01',usedf = True)
ppi_raw = ppi_raw[1]

ppi = ppi_raw.apply(lambda x: pd.qcut(x, 3, labels=[-2,0,2])) # 三等分
ppi.reset_index(level=0, inplace=True)
ppi.rename(columns={'index':'time'},inplace=True)
ppi.rename(columns=ppi_name_map, inplace=True) # 将识别代码换为中文名称

# 合并, 计算得分
stock_long = pd.melt(stock, id_vars = ['time'], var_name='id',value_name='stock')
ppi_long = pd.melt(ppi, id_vars = ['time'], var_name='id',value_name='price')
full_data = pd.merge(ppi_long,stock_long,how='left')
full_data['score'] = full_data['price'] + full_data['stock']
full_data['time'] = pd.to_datetime(full_data['time'])
latest_rank = full_data[full_data['time'] == obs_time].sort_values(by=['score'],ascending=False)

pre_rank = full_data[full_data['time'] == pre_time].sort_values(by=['score'],ascending=False)
pre_rank.columns = ['time', 'id', 'price_pre', 'stock_pre', 'score_pre']
pre_rank.drop(['time'], axis=1, inplace=True)

latest_rank = pd.merge(latest_rank, pre_rank, on=['id'], how='left')
latest_rank.columns = ['时间','行业','PPI','库存','景气度','上一期PPI','上一期库存','上一期景气度']

# 细分产业链位置
up_latest_rank=latest_rank[latest_rank['行业'].isin(upstream)]
mid_latest_rank=latest_rank[latest_rank['行业'].isin(midstream)]
down_latest_rank=latest_rank[latest_rank['行业'].isin(downstream)]

with pd.ExcelWriter(save_dir+'行业库存周期排序.xlsx') as writer:
    latest_rank.to_excel(writer, sheet_name='全行业', index=False, encoding='utf-8-sig')
    up_latest_rank.to_excel(writer, sheet_name='上游', index=False, encoding='utf-8-sig')
    mid_latest_rank.to_excel(writer, sheet_name='中游', index=False, encoding='utf-8-sig')
    down_latest_rank.to_excel(writer, sheet_name='下游', index=False, encoding='utf-8-sig')


###################################################################################
stock_qnt = stock_raw.dropna(axis=0,how='any')
stock_qnt = stock_qnt.apply(lambda x: stats.rankdata(x)*100/len(x))
stock_qnt.reset_index(level=0, inplace=True)
stock_qnt.rename(columns={'index':'time'},inplace=True)
stock_qnt.rename(columns=stock_name_map, inplace=True)
stock_qnt['time'] = pd.to_datetime(stock_qnt['time'])
#stock_qnt['time'] = stock_qnt['time'].dt.date
stock_qnt.set_index('time',inplace=True)

# 月度取平均以聚合成季度数据
stock_qnt_quarter = stock_qnt.resample('Q').mean()
stock_qnt_quarter.reset_index(drop=False,inplace=True)
stock_qnt_quarter['time'] = stock_qnt_quarter['time'].dt.date
stock_qnt_quarter.set_index('time',inplace=True)

stock_qnt_mry = stock_qnt_quarter.iloc[-8:].T
stock_qnt_mry.columns = [x.strftime('%Y-%m-%d') for x in stock_qnt_mry.columns.values]
stock_qnt_mry.reset_index(drop=False,inplace=True)

ppi_qnt = ppi_raw.dropna(how='any')
ppi_qnt = ppi_qnt.apply(lambda x: stats.rankdata(x)*100/len(x))
ppi_qnt.reset_index(level=0, inplace=True)
ppi_qnt.rename(columns={'index':'time'},inplace=True)
ppi_qnt.rename(columns=ppi_name_map, inplace=True)
ppi_qnt['time'] = pd.to_datetime(ppi_qnt['time'])
ppi_qnt.set_index('time',inplace=True)

ppi_qnt_quarter = ppi_qnt.resample('Q').mean()
ppi_qnt_quarter.reset_index(drop=False,inplace=True)
ppi_qnt_quarter['time'] = ppi_qnt_quarter['time'].dt.date
ppi_qnt_quarter.set_index('time',inplace=True)

stock_qnt_latest = stock_qnt_quarter.iloc[-1:].T
stock_qnt_latest.columns = [x.strftime('%Y-%m-%d') for x in stock_qnt_latest.columns.values]
stock_qnt_latest.reset_index(drop=False,inplace=True)

# 因为库存同比更新时间更晚, 以其为基准

ppi_qnt_latest = ppi_qnt_quarter[ppi_qnt_quarter.index == pd.to_datetime(stock_qnt_latest.columns[-1])].T
ppi_qnt_latest.reset_index(drop=False, inplace=True)


ppi_qnt_latest.columns=['id', 'ppi']
stock_qnt_latest.columns=['id', 'stock']
ppi_n_stock = pd.merge(stock_qnt_latest, ppi_qnt_latest, on=['id'], how='left')
ppi_n_stock.dropna(axis=0,how='any',inplace=True)

ppi_n_stock.to_csv(save_dir +'stock_ppi.csv',encoding='utf-8-sig',index=False)
ppi_n_stock = pd.read_csv(save_dir + "stock_ppi.csv")

fig=plt.figure(figsize=(30,15))
#添加绘图区域
ax=fig.add_subplot(111)
sns.scatterplot(data=ppi_n_stock, x='ppi', y='stock')
ax.set_xlabel("PPI同比分位数")
ax.set_ylabel("存货同比分位数")

for i in range(ppi_n_stock.shape[0]):
  ax.text(ppi_n_stock.ppi[i], y=ppi_n_stock.stock[i], s=ppi_n_stock.id[i], alpha=0.8)

        
ax.axhline(y=50, color='k', linestyle='--', linewidth=1)           
ax.axvline(x=50, color='k',linestyle='--', linewidth=1)
plt.savefig(save_dir + '最新一期库存景气度四象限图.jpg', dpi=300)


ppi_qnt_quarter_long = ppi_qnt_quarter.reset_index(drop=False)
ppi_qnt_quarter_long = pd.melt(ppi_qnt_quarter_long, id_vars=['time'], var_name='id', value_name='ppi')

stock_qnt_quarter_long = stock_qnt_quarter.reset_index(drop=False)
stock_qnt_quarter_long = pd.melt(stock_qnt_quarter_long, id_vars=['time'], var_name='id', value_name='stock')

ppi_n_stock_long = pd.merge(ppi_qnt_quarter_long, stock_qnt_quarter_long, on=['time','id'], how='left')
ppi_n_stock_long.to_csv(save_dir + '库存周期合并历史数据.csv',index = False, encoding='utf-8-sig')