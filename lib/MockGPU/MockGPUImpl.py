# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os

from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.specialClient import special as special
#END_HEADER


class MockGPU:
    '''
    Module Name:
    MockGPU

    Module Description:
    A KBase module: MockGPU
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = ""
    GIT_COMMIT_HASH = ""

    #BEGIN_CLASS_HEADER
    def _submit_gpu(self, token):
        print("Will Submit SLURM GPU")
        with open('./work/tmp/slurm.sl', 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('#SBATCH -N 1 -C gpu -q regular -t 30:00 -A kbase_g\n')
            # This part is a bit of hack.  This is so you can run the HPC job
            # using the same container.
            f.write('#SBATCH --image=%s\n' % (os.environ["SHIFTER_IMAGEREQUEST"]))
            f.write('echo Running nvidia-smi in container\n')
            f.write('shifter nvidia-smi\n')

        p = {'submit_script': 'slurm.sl'}
        print("Submitting SLURM GPU")
        sr = special(self.callback_url, token=token)
        res = sr.slurm(p)
        print('slurm'+str(res))

    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.shared_folder = config['scratch']
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        #END_CONSTRUCTOR
        pass


    def run_MockGPU(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_MockGPU
        if params["parameter_1"] == "1":
            self._submit_gpu(ctx["token"])
        report = KBaseReport(self.callback_url)
        report_info = report.create({'report': {'objects_created':[],
                                                'text_message': params['parameter_1']},
                                                'workspace_name': params['workspace_name']})
        output = {
            'report_name': report_info['name'],
            'report_ref': report_info['ref'],
        }
        #END run_MockGPU

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_MockGPU return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
