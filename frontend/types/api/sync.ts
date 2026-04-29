export interface NotionSyncEntitySummary {
  entity: string;
  fetched: number;
  success: number;
  failed: number;
}

export interface NotionSyncSummary {
  total_fetched: number;
  total_success: number;
  total_failed: number;
  results: NotionSyncEntitySummary[];
}
