import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np

def scatter_enrichr(lab, org, method, n_features, n_ontologies=30, column_sort='Adjusted P-value', plot_type='bar', 
                    list_onto=['KEGG_2019_Mouse', 'WikiPathways_2019_Mouse', 'KEGG_2019_Human', 'WikiPathways_2019_Human',
                               'GO_Biological_Process_2018', 'GO_Cellular_Component_2018', 'GO_Molecular_Function_2018',], save=True):
    list_FS = ['triku', 'scanpy', 'std', 'scry', 'brennecke', 'm3drop', 'nbumi']
    palette = ["#E73F74","#7F3C8D","#11A579","#3969AC","#F2B701","#80BA5A","#E68310","#a0a0a0","#505050"]
    
    fig, ax = plt.subplots(1, 1, figsize=(10, 3))
    
    dict_dfs = {}
    
    for n_feature_idx, n_feature in enumerate(n_features):
        for FS_idx, FS in enumerate(list_FS):
            df = pd.read_csv(os.getcwd() + f'/exports/enrichr/{lab}_{method}_{org}_{n_feature}_{FS}.csv')
            df = df[df['Gene_set'].isin(list_onto)]
            
            if column_sort == 'Adjusted P-value':
                df = df.sort_values(by=column_sort).iloc[:n_ontologies]
                y_vals = df[column_sort].values
                y_vals = - np.log10(y_vals)

            elif column_sort == 'Combined Score':
                df = df.sort_values(by=column_sort, ascending=False).iloc[:n_ontologies]
                y_vals = df[column_sort].values
            
            elif column_sort == 'division':
                table_vals = df['Overlap'].values
                df['divided'] = [int(i.split('/')[0]) / int(i.split('/')[1]) for i in table_vals]
                df = df.sort_values(by='divided', ascending=False).iloc[:n_ontologies]
                y_vals = df['divided'].values
                
            
            x_pos = n_feature_idx + (FS_idx - len(list_FS) // 2) / (len(list_FS) + 3)
            
            if plot_type == 'bar':
                plt.bar(x_pos , np.mean(y_vals), 
                        width = 0.1, yerr=np.std(y_vals), color=palette[FS_idx])
            elif plot_type == 'scatter':
                plt.scatter([x_pos] * len(y_vals), y_vals, c=palette[FS_idx], alpha=0.8)
            
            dict_dfs[f'{n_feature}_{FS}'] = df
    
    legend_elements = [
        mpl.lines.Line2D(
            [0], [0], marker="o", color=palette[j], label=list_FS[j]
        )
        for j in range(len(list_FS))
    ]
    ax.legend(handles=legend_elements, bbox_to_anchor=(1.2, 0.9))
    ax.set_xticks(range(len(n_features)))
    ax.set_xticklabels(n_features)
    ax.set_ylabel(column_sort)
    ax.set_xlabel('Number of features')
    
    plt.tight_layout()
    
    if save:
        plt.savefig(save)
    
    return dict_dfs

def barplot_ontologies_individual(df, axis=None, color="#ababab", column='Adjusted P-value', ascending=False, log=True, y_text=''):
    if axis is None:
        fig, axis = plt.subplots(1, 1, figsize=(10, 7))
    
    vals = df.sort_values(by=column, ascending=ascending)[column].values
    names = [i.split(' (')[0] for i in df.sort_values(by=column, ascending=ascending)['Term'].values]
    names = [i[: 42] + '...' if len(i) > 42 else i for i in names]

    if log:
        vals = - np.log10(df.sort_values(by=column, ascending=ascending)[column].values)
    
    if column == 'Adjusted P-value':
        if log:
            axis.plot(-np.log10([0.05, 0.05]), [-1.5, len(names) + 0.5], c="#ababab", alpha=0.8, linewidth=3, zorder=0)
        else:
            axis.plot([0.05, 0.05], [-1.5, len(names) + 0.5], c="#ababab", alpha=0.8, linewidth=3, zorder=0)
        
    axis.barh(range(len(df)), vals, color=color, zorder=5, alpha=0.7)
    
    for y in range(len(df)):
        axis.text(0.05 * np.max(axis.get_xlim()), y - 0.2, names[y], zorder=10, fontsize=12)
        
    axis.set_yticks([])
    axis.spines['right'].set_visible(False)
    axis.spines['top'].set_visible(False)

    x_text = column if not log else column + ' (log)'
    axis.set_xlabel(x_text)
    axis.set_ylabel(y_text)
    
    return axis

    
def barplot_ontologies_all(dict_dfs, n_features=1000, list_FSs=['triku', 'std', 'scry', 'scanpy', 'm3drop', 'nbumi'], 
                           list_colors=["#E73F74", "#11A579","#3969AC", "#7F3C8D", "#80BA5A","#E68310"], figsize=(17, 14), save=''):
    
    mpl.rcParams.update({'font.size':17})
    fig, axis = plt.subplots(2, 3, figsize=figsize)
    
    for i in range(len(list_FSs)):
        barplot_ontologies_individual(dict_dfs[f'{n_features}_{list_FSs[i]}'], axis=axis.ravel()[i], 
                                      color=list_colors[i], column='Adjusted P-value', ascending=False, log=True, y_text=list_FSs[i])
    
    plt.tight_layout()
    
    if save:
        plt.savefig(save)
        
    mpl.rcParams.update(mpl.rcParamsDefault)