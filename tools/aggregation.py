import json
import os
import pandas as pd

# extract stress info from workload and transfer to str
def stress_to_str(workload_info):
    stress = ""
    if "stress" in workload_info and workload_info["stress"] != {}:
        for k, v in workload_info["stress"].items():
            for _k, _v in v.items():
                stress = f"{k}_{_v}"
    return stress

# info per epoch to info per workload
def ipe_to_ipw(info_per_epoch):
    info_per_workload = {}
    for epoch_info in info_per_epoch:
        for k,v in epoch_info["workloads"].items():
            if k not in info_per_workload:
                info_per_workload[k] = {"info_per_epoch": [v]}
            else:
               info_per_workload[k]["info_per_epoch"].append(v)
    return info_per_workload

# infor per workload to info per epoch
def ipw_to_ipe(info_per_workload):
    info_per_epoch = []
    keys = list(info_per_workload.keys())
    n_epoch = len(info_per_workload[keys[0]]["info_per_epoch"])
    
    for i in range(n_epoch):
        epoch_info = {"workloads":{}}

        for key in keys:
            epoch_info["workloads"][key] = info_per_workload[key]["info_per_epoch"][i]
        else:
            if "stress" in info_per_workload[key]["info_per_epoch"][i]:
                epoch_info["stress"] = info_per_workload[key]["info_per_epoch"][i]["stress"]

        info_per_epoch.append(epoch_info)
    return info_per_epoch

# format any timestamp to 13 timestamp    
def format_to_13_timestamp(ts):
    assert ts + 1 < 10000000000000
    return int(format(ts, '0<13d'))

# filter dataframe from [start to end]
def filter_row_timerange(start, end):
    return lambda x : x.loc[(x.index >= start) & (x.index <=end)]

# filter useless columns which
# std <= std_min
# mean <= mean_min
def filter_column_useless(excol_prefix=(), std_min=1e-10, mean_min=0):
    def __filter_column_useless(df):
        cols_to_drop = set()
        std = df.std()
        mean = df.mean()

        cols_to_drop.update(std[std <= std_min].index)
        cols_to_drop.update(mean[mean <= mean_min].index)
        return df.drop(columns = [col for col in cols_to_drop if not col.startswith(excol_prefix)])
    return __filter_column_useless


# filter noise row which
# beyond range [quantile_l - delta, quantile_h + delta]
# delta = sparam * (quantile_h - quantile_l)
def filter_row_noise(col_prefix, sparam=1.5, l=0.25, h=0.75):
    def __filter_row_noise(df):
        temp_df = filter_column_startswith(col_prefix)(df)
        q1 = temp_df.quantile(l)
        q3 = temp_df.quantile(h)
        iqr = q3 - q1
  
        outliers = ((temp_df < (q1 - sparam * iqr)) | (temp_df > (q3 + sparam * iqr))).any(axis=1)
        return df.drop(temp_df[outliers].index)
    
    return __filter_row_noise

# filter column starts with col_prefix
def filter_column_startswith(col_prefix):
    return lambda x : x[[col for col in x.columns if col.startswith(col_prefix)]]

# inner: extract stress info from workload info, then add it to dataframe
def _workload_with_stress(workload_info):
    def __filter_workload(df):
        if "stress" in workload_info and workload_info["stress"] != {}:
            stress_data = {}
            for k, v in workload_info["stress"].items():
                for _k, _v in v.items():
                    stress_data[f"stress_{_k}"] = [int(_v) for i in range(df.shape[0])]
                    
            stress_df = pd.DataFrame(stress_data)
            stress_df.set_index(df.index, inplace=True)
            df = pd.concat([stress_df, df], axis=1)
        return df
    return __filter_workload

# inner: extract score info from workload info, then add it to dataframe
def _workload_with_score(workload_info):
    return lambda x:x

# filter workload info
def filter_workload(workload_info, with_stress = False, with_score=False):
    assert "start_time" in workload_info or "start" in workload_info
    assert "end_time" in workload_info or "end" in workload_info
  
    start = format_to_13_timestamp(workload_info["start_time"] if "start_time" in workload_info else workload_info["start"])
    end = format_to_13_timestamp(workload_info["end_time"] if "end_time" in workload_info else workload_info["end"]) 

    df_funcs = [filter_row_timerange(start, end)]
    if with_stress:
        df_funcs.append(_workload_with_stress(workload_info))

    if with_score:
        df_funcs.append(_workload_with_score(workload_info))
    return df_funcs    

def apply_df_funcs(df, df_funcs=[]):
    for df_func in df_funcs:
        df = df_func(df)
    return df

class ExpData:
    def __init__(self, df, exp):
        self.df = df
        self.exp = exp
        self.workload_preprocess_funcs = defualt_workload_preprocess_funcs
        self.workload_agg_funcs = defualt_workload_agg_funcs

    # opt_interval/delay using second, return ms
    def _time_shift(self, opt_interval, delay=0):
        opt_interval = opt_interval * 1000
        delay = delay * 1000
        
        workload_info = list(self.exp["info_per_epoch"][0]["workloads"].values())[0]
        assert "start_time" in workload_info or "start" in workload_info
        assert "end_time" in workload_info or "end" in workload_info
        
        e_s = format_to_13_timestamp(self.exp["start_time"])
        f_s = format_to_13_timestamp(workload_info["start_time"] if "start_time" in workload_info else workload_info["start"])
        
        delta = f_s - e_s - 2 * opt_interval - delay
        if "stress" in self.exp["info_per_epoch"][0]:
            delta = delta - 2 * opt_interval
            
        return delta

    # timeshift using ms
    def shift_time(self, timeshift):
        workload_info = list(self.exp["info_per_epoch"][0]["workloads"].values())[0]
        start_time_key = "start_time" if "start_time" in workload_info else"start"
        end_time_key = "end_time" if "end_time" in workload_info else"end"

        assert start_time_key in workload_info
        assert end_time_key in workload_info
        
        start = workload_info[start_time_key]
        # using 10bit timestamp
        if format_to_13_timestamp(start) != start:
            timeshift = int(timeshift / 1000)
        
        for k, v in self.exp["info_per_workload"].items():
            for _v in v["info_per_epoch"]:
                _v[start_time_key]  = _v[start_time_key] - timeshift
                _v[end_time_key]  = _v[end_time_key] - timeshift
        
        for v in self.exp["info_per_epoch"]:
            for k, _v in v['workloads'].items():
                _v[start_time_key]  = _v[start_time_key] - timeshift
                _v[end_time_key]  = _v[end_time_key] - timeshift
        return self
        
        
    def workload_keys(self):
        return list(self.exp["info_per_workload"].keys())
      
    def workloads_of(self, workload_name):
        return self.exp["info_per_workload"][workload_name]["info_per_epoch"]

    def workload_df(self, workload, with_stress=False, custom_df_funcs=None):
      df_funcs = filter_workload(workload, with_stress)
      if custom_df_funcs == None:
        df_funcs = df_funcs + self.workload_preprocess_funcs
      else:
        df_funcs = df_funcs + custom_df_funcs
      return apply_df_funcs(self.df, df_funcs)
      
    def set_workload_preprocess_funcs(self, df_funcs):
        self.workload_preprocess_funcs = df_funcs
        return self

    def set_workload_agg_funcs(self, df_funcs):
        self.workload_agg_funcs = df_funcs
        return self

    def agg_one_workload(self, workload_info, with_stress=False, with_score=False):
        df_funcs =  filter_workload(workload_info) + self.workload_preprocess_funcs + self.workload_agg_funcs
        
        # with_stress and with_score after agg
        if with_score:
            df_funcs.append(_workload_with_score(workload_info))
            
        if with_stress:
            df_funcs.append(_workload_with_stress(workload_info))
        return apply_df_funcs(self.df, df_funcs)

    # aggregate one epoch(one stress for each workload)
    def __agg_one_epoch(self, n_epoch):
        epoch_info = self.exp["info_per_epoch"][n_epoch]
        
        dfs = []
        for k,v in epoch_info["workloads"].items():
            df = self.agg_one_workload(v, with_stress=True)
            dfs.append(df)
        
        df = pd.concat(dfs).fillna(0).reset_index(drop=True)
        
        keys = list(epoch_info["workloads"].keys())
        assert df.shape[0] == len(keys), f"miss match length {len(dfs)} and {len(keys)}"
        
        return df.rename(index=lambda x : keys[x])

    def agg_epoch(self, n_epoch=-1, df_funcs=[]):
        assert n_epoch <= self.exp["n_epoch"], f"max len: {len(self.exp['info_per_epoch'])}"

        df = None
        if n_epoch != -1:
            df = self.__agg_one_epoch(n_epoch)
        else: 
            df = pd.concat([self.__agg_one_epoch(n_epoch) for n_epoch in range(self.exp["n_epoch"])]).fillna(0)

        if df is not None:
            df = apply_df_funcs(df, df_funcs)

        return df    

    def one_column_on_stresses(self, column, df_key, df_funcs=[]):
        df_dict = {}
        for workload_info in self.workloads_of(df_key):
            workload_df = self.workload_df(workload_info)
            workload_df = workload_df[column].reset_index(drop=True) 
            df_dict[stress_to_str(workload_info)] = apply_df_funcs(workload_df, df_funcs) 

        return pd.DataFrame(df_dict)
      
    def one_column_on_workloads(self, column, n_epoch=0, df_funcs=[]):
        df_dict = {}
        for workload_key in self.workload_keys():
            workload_info = self.workloads_of(workload_key)[n_epoch]
            workload_df = self.workload_df(workload_info)
            assert column in workload_df.columns, f"{column} not in workload {workload_key}"

            workload_df = apply_df_funcs(workload_df, df_funcs)
            df_dict[workload_key] =  workload_df[column].reset_index(drop=True)
    
        return pd.DataFrame(df_dict)

# aggregate det dateframe on target stress
# df_workload is workload dataframe under any stress
# no_stress_df is workload dataframe without stress
# det_columns is the target column to be calculated
# stress is the column in df workload which indicate workload stress
def agg_det_columns_on_stress(df_workload, no_stress_df, det_columns=[], stress=""):
    if stress == "" or stress not in df_workload.columns:
        stress = df_workload.columns[0]

    if len(det_columns) == 0:
        det_columns = list(set(no_stress_df.columns).intersection(set(df_workload.columns)))

    delta_df = df_worklad[det_columns] - no_stress_df[det_columns]
    det_percentage_df = delta_df / no_stress_df[det_columns]
    det_percentage_df.index = [f"{stress.split('_', 1)[1]}_{i}" for i in df_workload[stress]]
    return det_percentage_df

def agg_per_workload_column_on_stress(exp_data, no_stress_df_epoch, qos_column, stress=""):
    df_epoch = exp_data.agg_epoch()
    df_epoch_group = df_epoch.groupby(df_epoch.index)

    qos_percentage_dfs = []
    for group in df_epoch_group.groups:
        df_workload = df_epoch_group.get_group(group)
        if stress == "" or stress not in df_workload.columns:
            stress = df_workload.columns[0]
        no_stress = no_stress_df_epoch.loc[[group]]
        delta_df = df_workload[qos_column] - no_stress[qos_column]
        qos_percentage_df = delta_df / no_stress[qos_column]
        qos_percentage_df.index = [f"{stress.split('_', 1)[1]}_{i}" for i in df_workload[stress]]
        qos_percentage_dfs.append(qos_percentage_df)
    df = pd.concat(qos_percentage_dfs, axis=1)
    df.columns = list(df_epoch_group.groups.keys())
    return df

def workload_on_stress(exp_data, workload_key, with_stress=True, with_score=True):
    dfs = []
    for workload_info in exp_data.workloads_of(workload_key):
        dfs.append(exp_data.agg_one_workload(workload_info, with_stress, with_score))
    df = pd.concat(dfs).fillna(0).reset_index(drop=True)
    df_workload = df.rename(index=lambda x : workload_key)
    return df_workload

def no_stress_of_workload(exp_data, workload_key):
    return workload_on_stress(exp_data, workload_key, with_stress=False)
    
def __check_exp(exp):
    essential_fields = [
        "n_epoch",
        "info_per_epoch",
    ]
    return all(field in exp for field in essential_fields)
    
def read_from_dir(dir):
    exp_json = os.path.join(dir, "exp.json")
    exp_data = os.path.join(dir, "merged.csv")

    assert os.path.exists(exp_json) and os.path.exists(exp_data)
    df_total = pd.read_csv(exp_data, index_col=0)
    df_total.set_index('Time', inplace=True)
    
    with open(exp_json, 'r') as f:
        exp = json.load(f)

    assert __check_exp(exp)
    if "info_per_workload" not in exp or exp["info_per_workload"] == {}:
        exp["info_per_workload"] = ipe_to_ipw(exp["info_per_epoch"])
    
    return ExpData(df_total, exp)

# To Be Tested
def concat(exp_datas=[]):
    if len(exp_datas) == 0:
        return None
    if len(exp_datas) == 1:
        return exp_datas[0]
        
    exp_datas.sort(key = lambda x : x.exp["start_time"])
    
    start_time = exp_datas[0].exp["start_time"]
    end_time = exp_datas[1].exp["end_time"]
    total_time = end_time - start_time
    date_format = exp_datas[0].exp["date_format"]

    n_epoch = 0
    info_per_workload = {}
    for exp in exp_datas:
        info_per_workload.update(exp.exp["info_per_workload"])
        n_epoch = exp.exp["n_epoch"]

    info_per_epoch = ipw_to_ipe(info_per_workload)
    total_exp = {
        "start_time": start_time,
        "end_time": end_time,
        "total_time": total_time,
        "n_epoch": n_epoch,
        "date_format": date_format,
        "info_per_workload": info_per_workload,
        "info_per_epoch": info_per_epoch,        
    }

    total_df = pd.concat([exp_data.df for exp_data in exp_datas], axis=0)

    return ExpData(total_df, total_exp)

def exp_roots_from_dir(root_dir, senario):
    exp_roots = {"no_stress": "","stresses": []}
    for dir in os.listdir(root_dir):
        if dir == senario:
            for _dir in os.listdir(os.path.join(root_dir, dir)):
                if _dir == ".ipynb_checkpoints":
                    continue
                exp_roots["stresses"].append(os.path.join(root_dir, dir, _dir))
            exp_roots["stresses"].sort(key=lambda x : int(x.split('_')[-1]))   
            
        if dir == "no_stress":
            dir_list = [d for d in os.listdir(os.path.join(root_dir, dir)) if d != ".ipynb_checkpoints"]
            dir_list.sort(key=lambda x : int(x.split('_')[-1]))
    
            exp_roots["no_stress"] = os.path.join(root_dir, dir, dir_list[-1])
    return exp_roots

defualt_workload_preprocess_funcs = [
    filter_column_startswith(col_prefix=("stress", "host", "vm", "app")),
    filter_column_useless(excol_prefix=("stress")),
    filter_row_noise(col_prefix=("app")),
]

defualt_workload_agg_funcs = [
    lambda x : x.mean().to_frame().T,
]