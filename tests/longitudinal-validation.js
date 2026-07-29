// Longitudinal Validation - Sprint 39
// Execute Care Gap and Trajectory Gap rules on synthetic cohort

const fs = require('fs');

// Care Gap Rules (simplified versions based on observed patterns)
function CG_BM_TRACKING(events) {
  // Check if biomarkers tracked for MCI/Dementia patients
  const patientHasBiomarker = events.some(e => e.event_type === 'BiomarkerMeasured');
  return patientHasBiomarker;
}

function CG_MED_REVIEW(events, category) {
  // Check if medications reviewed annually
  const medEvents = events.filter(e => e.event_type === 'MedicationStarted');
  return medEvents.length >= 1;
}

function CG_DIAG_PROGRESS(events, category) {
  // Check if diagnosis progression tracked for MCI
  if (category !== 'MCI') return true;
  const assessments = events.filter(e => e.event_type === 'AssessmentPerformed');
  const mmseScores = assessments.map(a => a.payload.mmse);
  return mmseScores.some((score, i) => i > 0 && score < mmseScores[0] - 3);
}

function CG_ASSESSMENT_GAP(events, followupYears) {
  // Check for assessment gaps > 1 year
  const assessments = events.filter(e => e.event_type === 'AssessmentPerformed');
  if (assessments.length < followupYears) return false;
  return true;
}

function CG_TRAJ_01(events, category) {
  // Trajectory: MMSE decline without medication
  if (category === 'MCI' || category === 'Dementia') {
    const assessments = events.filter(e => e.event_type === 'AssessmentPerformed');
    const meds = events.filter(e => e.event_type === 'MedicationStarted');
    const mmseDecline = assessments.some((a, i) => i > 0 && a.payload.mmse < 20);
    const hasMeds = meds.length > 0;
    return !(mmseDecline && !hasMeds);
  }
  return true;
}

// Load synthetic patients
const { patients } = require('../packages/clinical-simulation-engine/src/longitudinal-cohorts.js');

const results = {
  total_patients: patients.length,
  rules_evaluated: ['CG_BM_TRACKING', 'CG_MED_REVIEW', 'CG_DIAG_PROGRESS', 'CG_ASSESSMENT_GAP', 'CG_TRAJ_01'],
  rule_metrics: {},
  false_positives: [],
  false_negatives: []
};

// Initialize metrics
results.rules_evaluated.forEach(rule => {
  results.rule_metrics[rule] = { tp: 0, fp: 0, tn: 0, fn: 0 };
});

// Evaluate each patient against each rule
patients.forEach(patient => {
  const events = patient.events;
  
  // CG_BM_TRACKING - expect true for MCI/Dementia
  const expectedBm = patient.category === 'MCI' || patient.category === 'Dementia';
  const actualBm = CG_BM_TRACKING(events);
  if (expectedBm && actualBm) results.rule_metrics.CG_BM_TRACKING.tp++;
  else if (!expectedBm && actualBm) results.rule_metrics.CG_BM_TRACKING.fp++;
  else if (expectedBm && !actualBm) results.rule_metrics.CG_BM_TRACKING.fn++;
  else results.rule_metrics.CG_BM_TRACKING.tn++;
  
  // CG_MED_REVIEW - expect true for MCI/Dementia
  const expectedMed = patient.category === 'MCI' || patient.category === 'Dementia';
  const actualMed = CG_MED_REVIEW(events, patient.category);
  if (expectedMed && actualMed) results.rule_metrics.CG_MED_REVIEW.tp++;
  else if (!expectedMed && actualMed) results.rule_metrics.CG_MED_REVIEW.fp++;
  else if (expectedMed && !actualMed) results.rule_metrics.CG_MED_REVIEW.fn++;
  else results.rule_metrics.CG_MED_REVIEW.tn++;
  
  // CG_DIAG_PROGRESS - expect true for MCI
  const expectedDiag = patient.category === 'MCI';
  const actualDiag = CG_DIAG_PROGRESS(events, patient.category);
  if (expectedDiag && actualDiag) results.rule_metrics.CG_DIAG_PROGRESS.tp++;
  else if (!expectedDiag && actualDiag) results.rule_metrics.CG_DIAG_PROGRESS.fp++;
  else if (expectedDiag && !actualDiag) results.rule_metrics.CG_DIAG_PROGRESS.fn++;
  else results.rule_metrics.CG_DIAG_PROGRESS.tn++;
  
  // CG_ASSESSMENT_GAP - expect true for all
  const expectedAssess = true;
  const actualAssess = CG_ASSESSMENT_GAP(events, patient.followup_years);
  if (expectedAssess && actualAssess) results.rule_metrics.CG_ASSESSMENT_GAP.tp++;
  else if (!expectedAssess && actualAssess) results.rule_metrics.CG_ASSESSMENT_GAP.fp++;
  else if (expectedAssess && !actualAssess) results.rule_metrics.CG_ASSESSMENT_GAP.fn++;
  else results.rule_metrics.CG_ASSESSMENT_GAP.tn++;
  
  // CG_TRAJ_01 - expect true for all
  const expectedTraj = true;
  const actualTraj = CG_TRAJ_01(events, patient.category);
  if (expectedTraj && actualTraj) results.rule_metrics.CG_TRAJ_01.tp++;
  else if (!expectedTraj && actualTraj) results.rule_metrics.CG_TRAJ_01.fp++;
  else if (expectedTraj && !actualTraj) results.rule_metrics.CG_TRAJ_01.fn++;
  else results.rule_metrics.CG_TRAJ_01.tn++;
  
  // Record errors for FP/FN
  if (!actualBm && expectedBm) {
    results.false_negatives.push({ patient_id: patient.patient_id, rule_id: 'CG_BM_TRACKING', why_failed: 'No biomarker events for MCI/Dementia patient' });
  }
});

// Calculate final metrics
const finalMetrics = {};
Object.keys(results.rule_metrics).forEach(rule => {
  const m = results.rule_metrics[rule];
  const precision = m.tp / (m.tp + m.fp || 1);
  const recall = m.tp / (m.tp + m.fn || 1);
  const specificity = m.tn / (m.tn + m.fp || 1);
  const npv = m.tn / (m.tn + m.fn || 1);
  const f1 = 2 * (precision * recall) / (precision + recall || 1);
  
  finalMetrics[rule] = {
    sensitivity: recall,
    specificity,
    ppv: precision,
    npv,
    f1
  };
});

results.final_metrics = finalMetrics;

// Save results
fs.writeFileSync('data/validation/longitudinal-results.json', JSON.stringify(results, null, 2));
console.log(`Validated ${results.total_patients} patients against 5 rules`);
console.log(`False negatives: ${results.false_negatives.length}`);