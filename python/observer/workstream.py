"""
Workstream: Observable cluster of related artifacts.
Redefinition: Not organizational unit but cluster of stable activity.
"""

def extract_observable_workstream(asset_name):
    """
    Extract workstream as observable cluster.
    Returns artifacts grouped by evidentiary relationships.
    """
    # Example: APOE4 workstream
    workstream = {
        'workstream_id': f'{asset_name}_cluster',
        'definition': 'Observable cluster of datasets, papers, code',
        'artifact_types': ['dataset', 'paper', 'code', 'protocol'],
        'evidence_boundaries': ['biomarker', 'genetics', 'imaging'],
        'temporal_coherence': 'stable'  # or 'emerging'
    }
    return workstream

# DO NOT archive - this is the correct definition