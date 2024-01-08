import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import networkx as nx
import math

sns.set_context("paper")

def plt_deterioration_heatmap(det_df, qos_column):
    plt.figure(figsize=(16, 9))
    sns.heatmap(det_df, annot=True, fmt=".3%", cmap='coolwarm', center=0)
    plt.title(qos_column)
    plt.show()

def plt_clique_on_graph(G, clique, rename_node=True, scaling=1.5, label_pos=0.35):
    subgraph = G.subgraph(clique)
    n_nodes = len(subgraph.nodes())
    if n_nodes < 2:
      return

    node_df = None
    if rename_node:
        node_map = {node: str(index) for index, node in enumerate(subgraph.nodes())}
        node_df = pd.DataFrame({"Metric Name": [k for k, v in node_map.items()]})
        node_df.index.name = "Node Num"
        subgraph = nx.relabel_nodes(subgraph, node_map)
    
    
    pos = nx.spring_layout(subgraph)
   
    plt.figure(figsize=(scaling * n_nodes, scaling * n_nodes))
    nx.draw(
        subgraph, pos, with_labels=True, edge_color='black', 
        node_color='white', edgecolors="black", node_size=800,
        font_size=12, font_color="black")

    edge_weights = nx.get_edge_attributes(subgraph, "weight")
    nx.draw_networkx_edge_labels(subgraph, pos, edge_labels=edge_weights, label_pos=label_pos)
    plt.show()
    
    return node_df

def plt_box(df, var_name="Series", value_name="Values"):
    df_melted = df.melt(var_name=var_name, value_name=value_name).dropna()
    plt.figure(figsize=(10, 4))

    sns.boxplot(x=var_name, y=value_name, data=df_melted, width=0.5, boxprops=dict(facecolor='grey', edgecolor='none'))
    sns.boxplot(x=var_name, y=value_name, data=df_melted, width=0.5, boxprops=dict(facecolor='none', edgecolor='black'))
                
    means = df.mean()
    positions = np.arange(len(means))
    plt.plot(positions, means, marker='o', color='r', linestyle='--')
    plt.rcParams["axes.labelsize"] = 12
    plt.rcParams["axes.titlesize"] = 14
    plt.show()
  
def plt_by_column(data, x_column="", columns=None, ncols=0):
    # 逐列绘图
    if columns == None:
      columns = data.columns
      
    if len(columns) == 0:
      return
      
    total_plots = len(columns)
    nrows = 0
    if ncols != 0:
      nrows = total_plots // ncols + (1 if total_plots % ncols else 0)
    else:
      ncols = math.ceil(math.sqrt(total_plots))
      nrows = math.ceil(total_plots / ncols) 

    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(8 * ncols, 4 * nrows))
    if len(columns) == 1:
      ax = axes
      column = columns[0]
      if x_column != "":
        ax.plot(data[x_column], data[column], label=column)
        ax.set_xlabel(x_column)
      else:
        ax.plot(data[column], label=column)
        ax.set_xlabel(data.index.name)
        
      ax.legend()
      ax.set_title(column)
      ax.tick_params(axis='x', rotation=45)
      return
      
    # 默认不进行绘制
    for ax in axes.flat:
      ax.axis('off')

    for i, column in enumerate(columns):
        row = i // ncols
        col = i % ncols
        
        ax = axes[row, col] if nrows != 1 else axes[col]
        ax.axis('on')
        if x_column != "":
          ax.plot(data[x_column], data[column], label=column)
          ax.set_xlabel(x_column)
        else:
          ax.plot(data[column], label=column)
          ax.set_xlabel(data.index.name)
          
        ax.legend()
        ax.set_title(column)
        ax.tick_params(axis='x', rotation=45)
      
    plt.tight_layout()
    plt.show()
  

def plt_corr_heatmap(corr_matrix):
    return None
    # 使用 seaborn 绘制热力图
    plt.figure(figsize=(80, 60)) # 可以调整大小
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')  # 'annot=True' 显示相关系数
    
    # 显示图形
    plt.show() 