import pandas as pd
import numpy as np
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

names = upstream + midstream + downstream

source_data_dir = input("结果保存路径为:")

#cycle_name = input("周期名称为:")
#print("依次输入行业名称与周期名称:")
#ind_name, cycle_name = map(str,input().split())


f = open(source_data_dir + "参数.txt", mode="r")
a = []
line = f.read()
line = line.split()
save_dir = line[1]

for cycle_name in ['产出周期', '盈利周期', '库存周期']:
  if cycle_name == '产出周期':
    xlabel, ylabel = 'PPI同比分位数', '工业增加值同比分位数'
    x, y = 'ppi', 'ind_va'
  elif cycle_name == '盈利周期':
    xlabel, ylabel = '利润率分位数', '营收同比分位数'
    x, y = 'margin', 'income'
  else:
    xlabel, ylabel = 'PPI同比分位数', '存货同比分位数'
    x, y = 'ppi', 'stock'

  df = pd.read_csv(save_dir + cycle_name +'合并历史数据.csv')


  for ind_name in upstream:
    ts_ = df[df['id'] == ind_name]
    ts_.dropna(axis=0,how='any',inplace=True)
    ts_.to_csv(save_dir + 'ts_.csv',encoding='utf-8-sig',index=False)
    ts_ = pd.read_csv(save_dir + 'ts_.csv')


    fig=plt.figure(figsize=(30,15))
    #添加绘图区域
    ax=fig.add_subplot(111)
    plt.plot(ts_[x], ts_[y], marker='o', markersize=5)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    for i in range(ts_.shape[0]):
      ax.text(ts_[x][i], y=ts_[y][i], s=ts_.time[i], alpha=0.8)


    ax.axhline(y=50, color='k', linestyle='--', linewidth=1)           
    ax.axvline(x=50, color='k',linestyle='--', linewidth=1) 
    plt.savefig(save_dir + '上游行业/' + f'{ind_name+cycle_name}折线图.jpg', dpi=300)

  for ind_name in midstream:
    ts_ = df[df['id'] == ind_name]
    ts_.dropna(axis=0,how='any',inplace=True)
    ts_.to_csv(save_dir + 'ts_.csv',encoding='utf-8-sig',index=False)
    ts_ = pd.read_csv(save_dir + 'ts_.csv')


    fig=plt.figure(figsize=(30,15))
    #添加绘图区域
    ax=fig.add_subplot(111)
    plt.plot(ts_[x], ts_[y], marker='o', markersize=5)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    for i in range(ts_.shape[0]):
      ax.text(ts_[x][i], y=ts_[y][i], s=ts_.time[i], alpha=0.8)


    ax.axhline(y=50, color='k', linestyle='--', linewidth=1)           
    ax.axvline(x=50, color='k',linestyle='--', linewidth=1) 
    plt.savefig(save_dir + '中游行业/' + f'{ind_name+cycle_name}折线图.jpg', dpi=300)

  for ind_name in downstream:
    ts_ = df[df['id'] == ind_name]
    ts_.dropna(axis=0,how='any',inplace=True)
    ts_.to_csv(save_dir + 'ts_.csv',encoding='utf-8-sig',index=False)
    ts_ = pd.read_csv(save_dir + 'ts_.csv')


    fig=plt.figure(figsize=(30,15))
    #添加绘图区域
    ax=fig.add_subplot(111)
    plt.plot(ts_[x], ts_[y], marker='o', markersize=5)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    for i in range(ts_.shape[0]):
      ax.text(ts_[x][i], y=ts_[y][i], s=ts_.time[i], alpha=0.8)


    ax.axhline(y=50, color='k', linestyle='--', linewidth=1)           
    ax.axvline(x=50, color='k',linestyle='--', linewidth=1) 
    plt.savefig(save_dir + '下游行业/' + f'{ind_name+cycle_name}折线图.jpg', dpi=300)