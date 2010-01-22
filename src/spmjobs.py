#!/usr/bin/env python

import os, sys
sys.path.append('/Data/vtrak1/SysAdmin/production/python')

## Class Encapsulating attributes of an spm job unique to one subject.
class SPMJobIdentity(object):

    def __init__(self, subid, paths, runs, fieldmap=True):
        """Constructor for a new identity."""
        self.subid = subid
        self.paths = paths
        self.runs = runs
        self.fieldmap = fieldmap

    def __str__(self):
        """Provides a sensible string representation of an identity."""
        return "%s\n%s\n%s\n%s" % (repr(self), self.subid, self.paths, self.runs)


## Class encapsulating an spm preprocessing job.
#    
# An instance knows where in the file system its job lives, the subject identity
# associated with the job, and how to change its own identity and make a new job.
# The class is somewhat generic and allows specific job types to inherit from it.
class SPMJob(object):
    # Queue holds series of matlab commands
    mlQ = []
    jobFile = None
    identity = None
    
    def __init__(self, jobFile, identity, spm_version = 'spm5'):
        self.jobFile = jobFile
        self.identity = identity
        if spm_version == 'spm5':
            self.spm_batch_struct = 'jobs'
        elif spm_version == 'spm8':
            self.spm_batch_struct = 'matlabbatch'
        else:
            raise(Exception, "Unrecognized spm_version, should be either 'spm5' or 'spm8'")

    def __str__(self):
        return "%s\n%s\n%s" % (repr(self), self.jobFile, self.identity)

    ## Returns a matlab command that opens self's jobfile.
    def load_cmd(self):
        return "load %s" % self.jobFile

    ## Returns a matlab command that walks the jobfile and replaces all
    # occurences of a string with a new one.
    def replace_cmd(self, old, new, matlabstruct = 'jobs'):
        return "%s=StructStrRep(%s, '%s', '%s')" % (self.spm_batch_struct, self.spm_batch_struct, old, new)

    ## Returns a matlab command that saves self's jobfile.
    def save_cmd(self):
        return "save '%s' '%s'" % (self.jobFile, self.spm_batch_struct)

    ## Returns an exit command for matlab.        
    def exit_cmd(self):
        return "exit"

    ## Wraps the matlab queue in an executable os call.
    def wrap_matlab_cmds(self):
        return "matlab7 -nodesktop -nosplash -r \"%s\"" % ('; '.join(self.mlQ))
        
    ##Replaces all elements of the current identity with a new identity.
    #
    # This command changes both self's attributes, and the data inside the.
    # Use it to transform a template job into a subject job.
    def replaceIdentity(self, newIdentity):
        # Check for same number of runs
        if len(self.identity.runs) != len(newIdentity.runs):
            raise IndexError('Spm job identities must have same number of runs.')
        if len(self.identity.paths) != len(newIdentity.paths):
        	raise IndexError('New identity must have same number of paths as original.')

        # make a list of commands to send to matlab
        self.mlQ = []
        self.mlQ.append( self.load_cmd() )
        for oldpath, newpath in zip(self.identity.paths, newIdentity.paths):
            self.mlQ.append( self.replace_cmd( oldpath, newpath ) )
        self.mlQ.append( self.replace_cmd( self.identity.subid, newIdentity.subid ) )
        for oldrun in self.identity.runs:
            mangled_oldrun = '__' + oldrun + '__'
            self.mlQ.append( self.replace_cmd( oldrun, mangled_oldrun ) )
        for oldrun, newrun in zip( self.identity.runs, newIdentity.runs ):
            mangled_oldrun = '__' + oldrun + '__'
            self.mlQ.append( self.replace_cmd( mangled_oldrun, newrun ) )
        if self.identity.fieldmap and not newIdentity.fieldmap:
        	self.mlQ.append( self.replace_cmd('_fm','') )
        self.mlQ.append( self.save_cmd() )
        self.mlQ.append( self.exit_cmd() )
        
        # construct final matlab call and run
        print( self.wrap_matlab_cmds() )
        os.system( self.wrap_matlab_cmds() )
        
        # replace the identity in this SPMJob object
        self.identity = newIdentity


## This simpler version of SPMJob doesn't worry about identity and simply takes
#  two ordered arrays of strings as inputs and does a replace on each to take
#  the old string and replace it with the new one.
class SimpleSPMJob(SPMJob):
    mlQ = []
    jobFile = None

    def __init__(self, jobfile):
        self.jobFile = jobFile

    def replaceIdentity(self, old_strings, new_strings):
        # Check for same number of runs
        if len(old_strings) != len(new_strings):
            raise IndexError('Lists of strings to replace must be the same length.')

        # make a list of commands to send to matlab
        self.mlQ = []
        self.mlQ.append( self.load_cmd() )

        for old_string, new_string in zip(old_strings, new_strings):
            self.mlQ.append( self.replace_cmd( old_string, new_string ) )

        self.mlQ.append( self.save_cmd() )
        self.mlQ.append( self.exit_cmd() )

        # construct final matlab call and run
        print( self.wrap_matlab_cmds() )
        os.system( self.wrap_matlab_cmds() )

        # replace the identity in this SPMJob object
        self.identity = newIdentity
    


if __name__ == '__main__':
    import spmjobs
    help(spmjobs)
