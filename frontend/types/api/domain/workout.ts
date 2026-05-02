export const WorkoutStatus = {
  OPEN: "Open",
  DONE: "Done",
  MISSED: "Missed",
  SKIPPED: "Skipped",
  CANCELLED: "Cancelled",
  UNKNOWN: "Unknown",
} as const;

export type WorkoutStatus = (typeof WorkoutStatus)[keyof typeof WorkoutStatus];

export const WorkoutCategory = {
  RUN: "Run",
  STRENGTH: "Strength",
  HYROX: "HYROX",
  MOBILITY: "Mobility",
  CROSS_TRAINING: "Cross-training",
  BOXING: "Boxing",
  CONDITIONING: "Conditioning",
} as const;

export type WorkoutCategory = (typeof WorkoutCategory)[keyof typeof WorkoutCategory];
