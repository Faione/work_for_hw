import os
import sys
import time
import experiment
import logging
import generator

DEFAUTL_OPT_INTERVAL=60

# support for python below 3.9
def _removeprefix(s, chars):
    if s.startswith(chars):
        return s[len(chars):]
    return s

def run_shell(cmd):
    if cmd == "":
        return
    logging.info(f"run: {cmd}")
    if os.system(cmd) != 0:
        sys.exit(1)

class StressExecutor(experiment.Executor, generator.Flags):
    
    def __init__(self, cmd_base="", flag_base="", stop_cmd="", type="", name="stress_executor", opt_interval=DEFAUTL_OPT_INTERVAL):
        experiment.Executor.__init__(self, type, name, opt_interval)
        generator.Flags.__init__(self, flag_base)
        
        self.cmd_base = cmd_base
        self.stop_cmd = stop_cmd
        self.runnig  = False
        
    def stress_info(self, flag):
        if flag == "":
            return {}

        flaglist = _removeprefix(flag, self.flag_base).split()
        flags = {}
        for i in range(0, len(flaglist), 2):
            k = _removeprefix(flaglist[i], "--")
            v = flaglist[i+1]
            flags[k] = v
        return flags
        
        
    def do_exec(self, **kwargs):
        flag = ""
        if "flag" in kwargs:
            flag = kwargs["flag"]
        
        self.runnig  = False
        run_shell(f"{self.cmd_base} --name stress_{self.type} {flag}")
        self.runnig  = True
        return {self.type: self.stress_info(flag)}

    
    def do_epilogue(self):
        if self.runnig:
            run_shell(f"{self.stop_cmd} stress_{self.type}")

class WorkloadExecutor(experiment.Executor, generator.Flags):
    
    def __init__(self,
                 cmd_base="", flag_base="", type="", warmup_cmd="",
                 name="workload_executor", opt_interval=DEFAUTL_OPT_INTERVAL):
        experiment.Executor.__init__(self, type, name, opt_interval)
        generator.Flags.__init__(self, flag_base)

        self.cmd_base = cmd_base
        self.warmup_cmd= warmup_cmd
        
    def iter(self):
        flags = self.flag_list()
        assert len(flags) > 0, "no workload setted"
            
        for flag in flags:
            yield flag 

    def do_exec(self, **kwargs):
        flag = ""
        if "flag" in kwargs:
            flag = kwargs["flag"]

        run_shell(self.warmup_cmd)
        info = {}
        info["start_time"] = int(time.time()) 
        info["run_cmd"] = f"{self.cmd_base} {flag}"
        run_shell(info["run_cmd"])
        info["end_time"] = int(time.time())
        return info
        
    
        
        
