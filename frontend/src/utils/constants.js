export const APP_NAME = 'Predictive Analytics Platform';
export const APP_VERSION = '1.0.0';

export const ROUTES = {
  LOGIN: '/login',
  SIGNUP: '/signup',
  DASHBOARD: '/dashboard',
  UPLOAD: '/upload',
  DATASETS: '/datasets',
  DATASET_DETAIL: '/datasets/:id',
  ML_PIPELINE: '/ml/:datasetId',
  CHAT: '/chat/:datasetId',
  REPORTS: '/reports',
  SETTINGS: '/settings',
};

export const DATASET_STATUS = {
  UPLOADED: 'uploaded',
  CLEANING: 'cleaning',
  READY: 'ready',
  ERROR: 'error',
};

export const MODEL_TYPES = {
  RANDOM_FOREST: 'random_forest',
  XGBOOST: 'xgboost',
  ENSEMBLE: 'ensemble',
};

export const FILE_TYPES = {
  CSV: '.csv',
  XLSX: '.xlsx',
  XLS: '.xls',
};

export const MAX_FILE_SIZE_MB = 50;
