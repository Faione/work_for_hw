import os
import sys
import time
import datetime
import logging

DATE_FORMAT_TIMESTAMP = "timestamp"
DEFAULT_DATE_FORMAT = "%Y%m%d%H%M%S" 

# An Experiment is of three parts
# 1. init client and server (scripts needed)
# 2. run inference app as setting
# 3. run client workload as setting
# 4. save result and clear env(if needed)
class Experiment:
    def __init__(self,
                 name="",
                 start_time=0, end_time=0, total_time=0,
                 n_epoch=0,
                 info_per_workload={}, info_per_epoch=[],
                 date_format=DEFAULT_DATE_FORMAT):
        # start_time is the start time of the whole experiment
        # end_time is the end time of the whole experiment
        self.start_time = start_time
        self.end_time = end_time
        self.total_time = 0
        self.n_epoch = n_epoch
        self.date_format = date_format
        self.info_per_workload = info_per_workload
        self.info_per_epoch = info_per_epoch
        self.name = name

    # run exp with both workload and stress
    def __run(self, workload_exec, stress_exec, interval):
        epoch_n = 0
        for stress_flag in stress_exec.iter():
            with stress_exec as se:
                stress_info = se.exec(flag=stress_flag)
                
                workload_n = 0
                epoch_infos = {"stress": stress_info}
                workload_infos = {}
                for workload_flag in workload_exec.iter():
                    workload_name = f"{workload_exec.type}_{workload_n}"
                    with workload_exec as we:
                        workload_info = we.exec(flag=workload_flag)
                        workload_info["name"] = workload_name
                        workload_info["stress"] = stress_info
                    if workload_name not in self.info_per_workload:
                        self.info_per_workload[workload_name] = {"info_per_epoch": [workload_info]}
                    else:
                        self.info_per_workload[workload_name]["info_per_epoch"].append(workload_info)

                    workload_infos[workload_name] = workload_info
                    workload_n = workload_n + 1
            epoch_infos["workloads"] = workload_infos
            self.info_per_epoch.append(epoch_infos)
            epoch_n = epoch_n + 1
            time.sleep(interval)
        self.n_epoch += epoch_n

    # run only workload
    def __run_only_workload(self, workload_exec, interval):
        for epoch_n in range(0, self.n_epoch):
            workload_n = 0
            epoch_infos = {}
            workload_infos = {}
            for workload_flag in workload_exec.iter():
                workload_name = f"{workload_exec.type}_{workload_n}"           
                with workload_exec as we:
                    workload_info = we.exec(flag=workload_flag)
                    workload_info["name"] = workload_name
        
                if workload_name not in self.info_per_workload:
                    self.info_per_workload[workload_name] = {"info_per_epoch": [workload_info]}
                else:
                    self.info_per_workload[workload_name]["info_per_epoch"].append(workload_info)
        
                workload_infos[workload_name] = workload_info
                workload_n = workload_n + 1
            epoch_infos["workloads"] = workload_infos
            self.info_per_epoch.append(epoch_infos)
             
    def run(self, workload_exec, stress_exec, interval=60):
        assert workload_exec != None
        assert self.n_epoch != 0 or stress_exec != None

        self.info_per_workload = {}
        self.info_per_epoch = []
        
        self.start_time = int(time.time())
        logging.info(f"{self.start()} experiment start") 

        if stress_exec != None:
            self.__run(workload_exec, stress_exec, interval)
        else:
            self.__run_only_workload(workload_exec, interval)
        
        self.end_time = int(time.time())
        logging.info(f"{self.end()} experiment end")
        self.total_time = self.end_time - self.start_time
        self.__gen_dir_name(workload_exec, stress_exec)

    # dir_name is the exp name, format like {workload_type}_{stress_type}_{time}
    # eg: redis_cache_20231024161754
    def __gen_dir_name(self, workload_exec, stress_exec):
        stress = "no"
        if stress_exec != None and "type" in stress_exec.__dict__:
            stress = stress_exec.type

        workload = "standard"
        if workload_exec != None and "type" in workload_exec.__dict__:
            workload = workload_exec.type
        
        self.name = "_".join([workload, stress, str(self.start(DEFAULT_DATE_FORMAT))])
        
        
    def dir_name(self):
        return self.name
    
    def start(self, date_format=""):
        if date_format == "":
            date_format = self.date_format

        if date_format == DATE_FORMAT_TIMESTAMP:
            return self.start_time

        return datetime.datetime.fromtimestamp(self.start_time).strftime(date_format)
        
    def end(self, date_format=""):
        if date_format == "":
            date_format = self.date_format

        if date_format == DATE_FORMAT_TIMESTAMP:
            return self.start_time

        return datetime.datetime.fromtimestamp(self.end_time).strftime(date_format)

class Executor:
    
    def __init__(self, type="", name="executor", opt_interval=0):
        self.name = name
        self.type = type
        self.opt_interval = opt_interval

    def __wait_opt_interval(self):
        if self.opt_interval != 0:
            time.sleep(self.opt_interval)    
            
    def __enter__(self):
        self.__wait_opt_interval()
        logging.debug(f"{self.name}: prologue")
        self.do_prologue()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__wait_opt_interval()
        logging.debug(f"{self.name}: epilogue")
        self.do_epilogue()

    def exec(self, **kwargs):
        self.__wait_opt_interval()    
        args = "" if not kwargs else kwargs
        logging.debug(f"{self.name}: exec {args}")
        return self.do_exec(**kwargs)

    def do_prologue(self):
        pass

    def do_epilogue(self):
        pass

    def do_exec(self, **kwargs):
        pass