import requests
import json
import re
import pandas as pd
import logging

# actually is 11000
ROW_LIMIT = 10000

query_range_api = "/api/v1/query_range"
time_col_name = "Time"

# format a grafana expr to prom query
def format_expr(expr, step):
  replace_funcs = [
    lambda x : x.replace("$__interval", step),
  ]

  for f in replace_funcs:
      expr = f(expr)
  return expr

# generate legend from labels
def gen_legend(raw_legend, labels):
    pattern = r"\{\{([^{}]+)\}\}"
    matches = re.findall(pattern, raw_legend)

    for match in matches:
        if match in labels:
            raw_legend = raw_legend.replace(f"{{{{{match}}}}}", str(labels[match]))
    return raw_legend

def result_to_df(prom_rlt, raw_legend):
    values = prom_rlt["values"]
    legend = gen_legend(raw_legend, prom_rlt["metric"])

    df = pd.DataFrame(values)
    df.rename(columns={0: time_col_name, 1: legend}, inplace=True)
    df.set_index(time_col_name, inplace=True)
    return df

def results_concat_to_df(prom_rlts, raw_legend):
    return pd.concat([result_to_df(prom_rlt, raw_legend) for prom_rlt in prom_rlts], axis=1)


# time str to second
# eg: 10m -> 600 
def timestr_to_second(time_str):
    time_units = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400
    }

    # 获取数字和单位部分
    if not time_str[-1].isnumeric():
        value = int(time_str[:-1])
        unit = time_str[-1].lower()  # 转换为小写以支持大写的时间单位
    else:
        value = int(time_str)
        unit = 's'  # 默认为秒

    return value * time_units.get(unit, 1)  # 如果单位未知，默认为秒

# prometheus support 11000 row data per query by default
# the rows of data can be calculated by: totaltime / step
# totaltime which is greater than 11000 should be split to batch of time ranges
def split_query_to_batch(start, end, istep):
    time_seconed = end - start
    assert time_seconed > 0, f"invalid time range {start} ~ {end}"
    
    logging.info(f'from {start} to {end}, total: {round(time_seconed / 60 / 60, 3)}h')
    max_time_range = istep * ROW_LIMIT
    full_epoch = int(time_seconed / max_time_range)
    rest_time = time_seconed % max_time_range

    query_batchs = []
    for i in range(full_epoch):
        start_time = start + i * max_time_range
        query_batchs.append([start_time, start_time + max_time_range - istep])
        
    if rest_time != 0:
        start_time = start + full_epoch * max_time_range 
        query_batchs.append([start_time, start_time + rest_time])
    
    logging.info(f"split to {len(query_batchs)} batchs")
    return query_batchs

# Prometheus client
class client:
    server = ""
    
    def __init__(self, server):
        self.server = server
    
    def query_range(self, query, start, end, step):
        params = {
        "query": query,
        "start": start, 
        "end": end,
        "step": step,
        }

        query_range_uri = f"http://{self.server}{query_range_api}"
        
        text = requests.get(query_range_uri, params=params).text
        data = json.loads(text)
    
        prom_rlts = data["data"]["result"]
        
        assert len(prom_rlts) > 0 , f"empty result: {query}"
        
        return prom_rlts
        
    def target_to_df(self, target, start, end, step):
        query = format_expr(target["expr"], step)
        raw_legend = target["legendFormat"]
        prom_rlts = self.query_range(query, start, end, step)
    
        return results_concat_to_df(prom_rlts, raw_legend)

    # fetch data between a query range
    def __targets_to_df(self, targets, start, end, step):
        dfs = [self.target_to_df(target, start, end, step) for target in targets]
        aio_df = pd.concat(dfs, axis=1)
        return aio_df

    # query present by targets
    # from start to end, by step
    def targets_to_df(self, targets, start, end, step):
        istep = timestr_to_second(step)
        query_batchs = split_query_to_batch(start, end, istep)
        dfs = [self.__targets_to_df(targets, query_batch[0], query_batch[1], step) for query_batch in query_batchs]
        logging.info(f"all data fetched")
        combined = pd.concat(dfs).fillna(0).replace('NaN', 0).sort_values(by=['Time']).reset_index()
        # using 13-digit timestamp
        combined["Time"] = combined["Time"] * 1000
        logging.info(f"all data formatted")
        return combined