import os
from datetime import datetime
from pathlib import Path
import pandas as pd

from exp_management import params


class ExpManager:
    def __init__(self, project_folder, experiment, root_folder = "plotter_exps", fsize=4):
        """
        An experiment manager creates and manages a directory structure for running different types of
        experiments.

        Basic Usage
        ------------------------------------------------------
        em = experiment_manager.ExpManager("some_project", "first_exp")

        # the parameter set from some_global_parameters.json
        em.global_configs.some_global_parameters

        # the experiment parameter set from some_exp_parameter.json
        em.configs.some_exp_parameter

        run experiment

        # make a new id for this experiment so that it doesn't override an old result
        # also log that we used parameters_used for that experiment id
        output_filepath = em.get_savepath("my_experiment.result", parameters_used)
        # output_filepath will look like $HOME/root_folder/projects/some_project/first_exp/0001_my_experiment.result
        result.save(output_filepath)

        File Structure
        -------------------------------------------------------
        The root where everything is saved is $HOME/root_folder

        It creates the structure

        $HOME/root_folder/global_configs
        $HOME/root_folder/projects

        global configs is a place to store config files that might be useful
        across all your projects.


        The projects folder will store all your different projects, their logs,
        configs, and results. It looks like

        $HOME/root_folder/projects/some_project_1/configs
        $HOME/root_folder/projects/some_project_1/logs
        $HOME/root_folder/projects/some_project_1/some_experiment_1

        configs is where those project specific configurations go.
        """
        self.fsize = fsize
        self.log_df = None

        # get the global directories
        self.root_dir = os.path.join(os.getenv("HOME"), root_folder)
        self.global_config_dir = os.path.join(self.root_dir, "global_configs")
        self.project_root = os.path.join(self.root_dir, "projects")

        self.project_dir = os.path.join(self.project_root, project_folder)
        self.project_configs = os.path.join(self.project_dir, "configs")

        self.logs = os.path.join(self.project_dir, "logs")
        self.log_file = os.path.join(self.logs, "{}.csv".format(experiment))
        self.results = os.path.join(self.project_dir, experiment)

        for p in [self.root_dir, self.global_config_dir, self.project_root,
                  self.project_dir , self.project_configs, self.logs, self.results]:
            path = Path(p)
            path.mkdir(parents=True, exist_ok=True)

        self.global_configs = ConfigLoader(self.global_config_dir)
        self.configs = ConfigLoader(self.project_configs)


    def get_savepath(self, filename, exp_params=None, batch_logging = False):
        if exp_params == None:
            print("Warning, you aren't saving with any parameters. This will make replication hard to do.")
            param_values = {}
        else:
            if isinstance(exp_params, params.Parameters):
                param_values = exp_params.last_sample
            else:
                param_values = exp_params

        param_values = self._add_metadata(filename, param_values)
        id = self._get_current_id() + 1
        self._log_experiment(id, param_values, batch_logging)
        return self._get_savepath(id, filename)


    def _get_current_id(self):
        ids = []
        ignore = [".DS"]
        for f in os.listdir(self.results):
            if any(i in f for i in ignore):
                continue
            id_str = f.split("_")[0]
            ids.append(int(id_str))
        if len(ids)>0:
            return max(ids)
        else:
            return 0

    def _get_savepath(self, id, filename):
        s = "{:0"+str(self.fsize)+"}"
        fmt_id = s.format(id)
        fullname = "{}_{}".format(fmt_id, filename)
        return os.path.join(self.results, fullname)

    def _add_metadata(self, filename, params):
        p = {
            "name": os.path.splitext(filename)[0],
            "time_created":datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        p.update(params)
        return p

    def _log_experiment(self, id, params, batch_logging=False):
        flatted_param = {}
        for k,v in params.items():
            if isinstance(k, list):
                for i, l in enumerate(k):
                    flatted_param["{}_{}".format(k, i)] = l
            elif isinstance(k, dict):
                for k1, v1 in k.items():
                    flatted_param["{}_{}".format(k, k1)] = v
            else:
                flatted_param[k] = v

        p = {"id":id}
        p.update(flatted_param)
        df = pd.DataFrame([p], columns=p.keys())

        if self.log_df is None:
            if os.path.exists(self.log_file):
                logs = pd.read_csv(self.log_file)
            else:
                logs = pd.DataFrame({})
        else:
            logs = self.df

        logs = logs.append(df, sort=False)

        if batch_logging:
            self.log_df = logs
        else:
            logs.to_csv(self.log_file, index=False)

    def write_logs(self):
        if self.log_df is not None:
            self.log_df.to_csv(self.log_file, index=False)

class ConfigLoader:
    def __init__(self, directory):
        self.directory = directory
        self.reload()

    def reload(self):
        for filename in os.listdir(self.directory):
            f = os.path.join(self.directory, filename)
            name = os.path.splitext(filename)[0]
            setattr(self, name, params.load(f))

    def write(self, name, config):
        if name[-len(".json"):] != ".json":
            name = "{}.json".format(name)
        output_file = os.path.join(self.directory, name)
        config.save(output_file)
