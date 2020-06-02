#! /usr/bin/env python
from GitAnalysis import BatchRunner

if __name__ == '__main__':
    batch_file = 'user_behaviour_template.json'
    batch_runner = BatchRunner(batch_file=batch_file)
    batch_runner.run_batch()

