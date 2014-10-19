# -----------------------------------------------------------------------------
# Common States
NEW = 'New'
DONE = 'Done'
CANCELED = 'Canceled'
FAILED = 'Failed'
PENDING = 'Pending'

# -----------------------------------------------------------------------------
# ComputePilot States
PENDING_LAUNCH = 'PendingLaunch'  # Pilot inserted into the system
LAUNCHING = 'Launching'           # Going to launch SAGA job
PENDING_ACTIVE = 'PendingActive'  # SAGA job is submitted
ACTIVE = 'Active'                 # Pilot become active

# -----------------------------------------------------------------------------
# ComputeUnit States
STATE_X = 'StateX'
PENDING_INPUT_STAGING = 'PendingInputStaging'
STAGING_INPUT = 'StagingInput'
PENDING_EXECUTION = 'PendingExecution'
SCHEDULING = 'Scheduling'
EXECUTING = 'Executing'
PENDING_OUTPUT_STAGING = 'PendingOutputStaging'
STAGING_OUTPUT = 'StagingOutput'
