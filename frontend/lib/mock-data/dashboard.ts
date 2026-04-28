import type { DashboardData } from "@/types/dashboard";

export const dashboardData: DashboardData = {
  athleteName: "Leon",
  summary:
    "This is the starting point for reviewing the current training situation before moving into planning, analysis, or coaching workflows.",
  nextAction:
    "Next: review this week's structure and keep the current aerobic base phase consistent.",
  overview: [
    {
      label: "Training focus",
      value: "Base",
      detail: "Build steady volume while keeping intensity controlled.",
    },
    {
      label: "This week",
      value: "4 workouts",
      detail: "Two endurance sessions, one strength session, and one recovery-focused day.",
    },
    {
      label: "Execution",
      value: "On track",
      detail: "Placeholder status until backend dashboard data is introduced.",
    },
    {
      label: "Primary signal",
      value: "Consistency",
      detail: "Keep planned work aligned with recovery and weekly feedback.",
    },
  ],
  currentPlan: {
    name: "Spring endurance build",
    description:
      "A simple working plan placeholder that represents the top-level training block currently mirrored from the Notion workflow.",
    focus: "Aerobic durability",
    timeline: "March to May",
  },
  currentPhase: {
    name: "Base phase",
    description:
      "A phase placeholder for steady training volume, controlled effort, and clean execution before adding more specific intensity.",
    focus: "Volume and repeatability",
    weekLabel: "Week 3 of 6",
  },
  weeklyOutlook: [
    {
      day: "Monday",
      title: "Easy endurance",
      detail: "Low-intensity aerobic session with relaxed pacing.",
      status: "Planned",
    },
    {
      day: "Wednesday",
      title: "Strength maintenance",
      detail: "Short gym session focused on control and movement quality.",
      status: "Planned",
    },
    {
      day: "Friday",
      title: "Steady aerobic",
      detail: "Moderate duration with no hard interval work.",
      status: "Planned",
    },
    {
      day: "Sunday",
      title: "Recovery check-in",
      detail: "Light movement and weekly feedback review.",
      status: "Open",
    },
  ],
};
