"""
ipctrace.py

Write a trace of instantaneous IPC values for all cores.
First argument is either a filename, or none to write to standard output.
Second argument is the interval size in nanoseconds (default is 10000)
"""

import sys, os, sim

class instrTrace:
  def setup(self, args):
    args = dict(enumerate((args or '').split(':')))
    filename = args.get(0, None)
    filename = 'instr.log'      #hardcoding file name for now
    interval_ns = long(args.get(1, 1000000))    #1 ms interval
    if filename:
      self.fd = file(os.path.join(sim.config.output_dir, filename), 'w')
      self.isTerminal = False
    else:
      self.fd = sys.stdout
      self.isTerminal = True
    for core in range(sim.config.ncores):
        self.fd.write('C%d ' %core)
    self.fd.write('\n')
    self.sd = sim.util.StatsDelta()
    self.stats = {
      'time': [ self.sd.getter('performance_model', core, 'elapsed_time') for core in range(sim.config.ncores) ],
      'ffwd_time': [ self.sd.getter('fastforward_performance_model', core, 'fastforwarded_time') for core in range(sim.config.ncores) ],
      'instrs': [ self.sd.getter('performance_model', core, 'instruction_count') for core in range(sim.config.ncores) ],
      'coreinstrs': [ self.sd.getter('core', core, 'instructions') for core in range(sim.config.ncores) ],
    }
    sim.util.Every(interval_ns * sim.util.Time.NS, self.periodic, statsdelta = self.sd, roi_only = True)

  def periodic(self, time, time_delta):
    if self.isTerminal:
      self.fd.write('[INSTR] ')
    #self.fd.write('%u' % (time / 1e6)) # Time in ns
    for core in range(sim.config.ncores):
      # detailed-only IPC
      instrs = self.stats['instrs'][core].delta
      #self.fd.write(' %.3f' % instrs)

      # include fast-forward IPCs
      instrs = self.stats['coreinstrs'][core].last
      self.fd.write('%d ' % instrs)
    self.fd.write('\n')


sim.util.register(instrTrace())
