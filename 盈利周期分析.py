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
a=pd.read_excel(source_dir + 'en_cn.xlsx', sheet_name=6)
b= a['指标ID'].to_list()
a['指标名称'] = a['指标名称'].str[3:-9]
profit_name_map = a.set_index(['指标ID'])['指标名称'].to_dict()
profit_raw = w.edb(b,beginTime='2011-01-01',usedf = True)
profit_raw = profit_raw[1]

a=pd.read_excel(source_dir + 'en_cn.xlsx', sheet_name=7)
b= a['指标ID'].to_list()
a['指标名称'] = a['指标名称'].str[3:-5]
asset_name_map = a.set_index(['指标ID'])['指标名称'].to_dict()
asset_raw = w.edb(b,beginTime='2011-01-01',usedf = True)
asset_raw = asset_raw[1]

asset = asset_raw.reset_index(drop=False)
asset.rename(columns={'index':'time'},inplace=True)
asset.rename(columns=asset_name_map, inplace=True)
asset_long = pd.melt(asset, id_vars = ['time'], var_name='id',value_name='asset')

profit = profit_raw.reset_index(drop=False)
profit.rename(columns={'index':'time'},inplace=True)
profit.rename(columns=profit_name_map, inplace=True)
profit_long = pd.melt(profit, id_vars = ['time'], var_name='id',value_name='profit')

full_data = pd.merge(profit_long,asset_long,on=['time','id'],how='left')
full_data['margin'] = full_data['profit'] / full_data['asset']
full_data['margin_yoy']=full_data.groupby('id')['margin'].pct_change(11)
full_data.dropna(how='any',inplace=True)

margin_raw = full_data[['time','id','margin_yoy']].pivot('time','id','margin_yoy')
margin = margin_raw.apply(lambda x: pd.qcut(x, 3, labels=[-2,0,2]))
margin.reset_index(drop=False,inplace=True)
margin_long = pd.melt(margin, id_vars = ['time'], var_name='id',value_name='margin')

###################################################################################
a=pd.read_excel(source_dir + 'en_cn.xlsx', sheet_name=3)
b= a['指标ID'].to_list()
a['指标名称'] = a['指标名称'].str[3:-10]
income_name_map = a.set_index(['指标ID'])['指标名称'].to_dict()
income_raw = w.edb(b,beginTime='2011-01-01',usedf = True)
income_raw = income_raw[1]

income = income_raw.apply(lambda x: pd.qcut(x, 3, labels=[-1,0,1]))
income = income.reset_index(drop=False)
income.rename(columns={'index':'time'},inplace=True)
income.rename(columns=income_name_map, inplace=True)
income_long = pd.melt(income, id_vars = ['time'], var_name='id',value_name='income')

income_n_margin = pd.merge(income_long, margin_long, on=['time','id'], how='left')
income_n_margin['score'] = income_n_margin['income'] + income_n_margin['margin']
income_n_margin['time'] = pd.to_datetime(income_n_margin['time'])

latest_rank = income_n_margin[income_n_margin['time'] == obs_time].sort_values(by=['score'],ascending=False)

pre_rank = income_n_margin[income_n_margin['time'] == pre_time].sort_values(by=['score'],ascending=False)
pre_rank.columns = ['time', 'id', 'price_pre', 'production_pre', 'score_pre']
pre_rank.drop(['time'], axis=1, inplace=True)

latest_rank = pd.merge(latest_rank, pre_rank, on=['id'], how='left')
latest_rank.columns = ['时间','行业','利润率','营收','景气度','上一期利润率','上一期营收','上一期景气度']

# 细分产业链位置
up_latest_rank=latest_rank[latest_rank['行业'].isin(upstream)]
mid_latest_rank=latest_rank[latest_rank['行业'].isin(midstream)]
down_latest_rank=latest_rank[latest_rank['行业'].isin(downstream)]

with pd.ExcelWriter(save_dir+'行业盈利周期排序.xlsx') as writer:
    latest_rank.to_excel(writer, sheet_name='全行业', index=False, encoding='utf-8-sig')
    up_latest_rank.to_excel(writer, sheet_name='上游', index=False, encoding='utf-8-sig')
    mid_latest_rank.to_excel(writer, sheet_name='中游', index=False, encoding='utf-8-sig')
    down_latest_rank.to_excel(writer, sheet_name='下游', index=False, encoding='utf-8-sig')

###################################################################################
# 计算分位数
income_qnt = income_raw.dropna(how='any')
income_qnt = income_qnt.apply(lambda x: stats.rankdata(x)*100/len(x))
income_qnt.reset_index(level=0, inplace=True)
income_qnt.rename(columns={'index':'time'},inplace=True)
income_qnt.rename(columns=income_name_map, inplace=True)
income_qnt['time'] = pd.to_datetime(income_qnt['time'])
#income_qnt['time'] = income_qnt['time'].dt.date
income_qnt.set_index('time',inplace=True)


# 月度取平均以聚合成季度数据
income_qnt_quarter = income_qnt.resample('Q').mean()
income_qnt_quarter.reset_index(drop=False,inplace=True)
income_qnt_quarter['time'] = income_qnt_quarter['time'].dt.date
income_qnt_quarter.set_index('time',inplace=True)

margin_qnt = margin_raw.dropna(how='any')
margin_qnt = margin_qnt.apply(lambda x: stats.rankdata(x)*100/len(x))
margin_qnt.reset_index(level=0, inplace=True)
margin_qnt.rename(columns={'index':'time'},inplace=True)
margin_qnt['time'] = pd.to_datetime(margin_qnt['time'])
#margin_qnt['time'] = margin_qnt['time'].dt.date
margin_qnt.set_index('time',inplace=True)

margin_qnt_quarter = margin_qnt.resample('Q').mean()
margin_qnt_quarter.reset_index(drop=False,inplace=True)
margin_qnt_quarter['time'] = margin_qnt_quarter['time'].dt.date
margin_qnt_quarter.set_index('time',inplace=True)

income_qnt_mry = income_qnt_quarter.iloc[-4:].T
income_qnt_mry.columns = [x.strftime('%Y-%m-%d') for x in income_qnt_mry.columns.values]
income_qnt_mry.reset_index(drop=False,inplace=True)
income_qnt_mry.rename(columns={'index':'id'}, inplace=True)

margin_qnt_mry = margin_qnt_quarter.iloc[-4:].T
margin_qnt_mry.columns = [x.strftime('%Y-%m-%d') for x in margin_qnt_mry.columns.values]
margin_qnt_mry.reset_index(drop=False,inplace=True)

margin_qnt_latest = margin_qnt_mry[['id',margin_qnt_mry.columns[-1]]]
margin_qnt_latest.columns = ['id', 'margin']
income_qnt_latest = income_qnt_mry[['id',margin_qnt_mry.columns[-1]]]
income_qnt_latest.columns = ['id', 'income']
income_n_margin = pd.merge(margin_qnt_latest, income_qnt_latest, on='id', how='left')


###################################################################################
fig=plt.figure(figsize=(24,12))
#添加绘图区域
ax=fig.add_subplot(111)
sns.scatterplot(data=income_n_margin, x='margin', y='income')
plt.xlabel("利润率同比分位数")
plt.ylabel("营收同比分位数")
          
for i in range(income_n_margin.shape[0]):
  plt.text(income_n_margin.margin[i], y=income_n_margin.income[i], s=income_n_margin.id[i], alpha=0.8)
         
        
plt.axhline(y=50, color='k', linestyle='--', linewidth=1)        
plt.axvline(x=50, color='k',linestyle='--', linewidth=1)
plt.savefig(save_dir + '最新一期盈利景气度四象限图.jpg', dpi=300)

###################################################################################
margin_qnt_quarter_long = margin_qnt_quarter.reset_index(drop=False)
margin_qnt_quarter_long = pd.melt(margin_qnt_quarter_long, id_vars=['time'], var_name='id', value_name='margin')

income_qnt_quarter_long = income_qnt_quarter.reset_index(drop=False)
income_qnt_quarter_long = pd.melt(income_qnt_quarter_long, id_vars=['time'], var_name='id', value_name='income')

margin_n_income_long = pd.merge(margin_qnt_quarter_long, income_qnt_quarter_long, on=['time','id'], how='left')
margin_n_income_long.to_csv(save_dir + '盈利周期合并历史数据.csv',index = False, encoding='utf-8-sig')