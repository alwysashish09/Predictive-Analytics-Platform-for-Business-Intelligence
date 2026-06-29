import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../utils/api';
import DataPreviewTable from '../components/DataPreviewTable';
import TransformationLog from '../components/TransformationLog';
import { FileSpreadsheet, ArrowRight, Activity, AlertTriangle, Layers, Settings, Play } from 'lucide-react';

export default function DatasetDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [dataset, setDataset] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Validation state
  const [validationReport, setValidationReport] = useState(null);
  const [isValidating, setIsValidating] = useState(false);

  // Clean state
  const [isCleaning, setIsCleaning] = useState(false);

  useEffect(() => {
    fetchDataset();
  }, [id]);

  const fetchDataset = async () => {
    try {
      const response = await api.get(`/datasets/${id}`);
      setDataset(response.data);
      if (response.data.status === 'uploaded') {
        runValidation(); // Auto-run validation if newly uploaded
      }
    } catch (err) {
      setError('Failed to load dataset details.');
    } finally {
      setLoading(false);
    }
  };

  const runValidation = async () => {
    setIsValidating(true);
    try {
      const res = await api.post(`/etl/${id}/validate`);
      setValidationReport(res.data);
    } catch (err) {
      console.error('Validation failed', err);
    } finally {
      setIsValidating(false);
    }
  };

  const handleClean = async () => {
    setIsCleaning(true);
    try {
      // Default config for now
      await api.post(`/etl/${id}/clean`, {
        handle_nulls: 'auto',
        handle_outliers: 'clip',
        remove_duplicates: true,
        standardize_strings: true,
      });
      await fetchDataset(); // Refresh to get logs and updated stats
    } catch (err) {
      console.error('Cleaning failed', err);
      alert('Cleaning failed. See console.');
    } finally {
      setIsCleaning(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-dark-50 dark:bg-dark-950 pt-16">
        <div className="w-10 h-10 border-4 border-primary-200 border-t-primary-500 rounded-full animate-spin" />
      </div>
    );
  }

  if (error || !dataset) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-dark-50 dark:bg-dark-950 pt-16">
        <div className="p-6 bg-accent-rose/10 text-accent-rose rounded-xl font-medium">
          {error || 'Dataset not found.'}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-dark-50 dark:bg-dark-950 pt-24 pb-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-8 animate-fade-in">
        
        {/* Header section */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white dark:bg-dark-800 p-6 rounded-2xl border border-dark-200 dark:border-dark-700 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-primary-100 dark:bg-primary-900/50 flex items-center justify-center">
              <FileSpreadsheet className="w-6 h-6 text-primary-500" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-dark-900 dark:text-white">
                {dataset.name}
              </h1>
              <p className="text-dark-500 dark:text-dark-400 text-sm flex items-center gap-3 mt-1">
                <span>{dataset.file_name}</span>
                <span className="w-1 h-1 rounded-full bg-dark-300 dark:bg-dark-600" />
                <span>{(dataset.file_size_bytes / (1024*1024)).toFixed(2)} MB</span>
                <span className="w-1 h-1 rounded-full bg-dark-300 dark:bg-dark-600" />
                <span className={`px-2 py-0.5 rounded text-xs font-medium uppercase
                  ${dataset.status === 'ready' ? 'bg-accent-emerald/10 text-accent-emerald' : 
                    dataset.status === 'error' ? 'bg-accent-rose/10 text-accent-rose' : 
                    'bg-accent-amber/10 text-accent-amber'}
                `}>
                  {dataset.status}
                </span>
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <button 
              onClick={() => navigate(`/ml/${dataset.id}`)}
              disabled={dataset.status !== 'ready'}
              className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Train ML Model
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Validation Alert (if issues exist and dataset not yet cleaned) */}
        {validationReport && validationReport.errors > 0 && dataset.status === 'uploaded' && (
          <div className="bg-accent-amber/10 border border-accent-amber/30 rounded-2xl p-6 flex gap-4 animate-slide-up">
            <AlertTriangle className="w-6 h-6 text-accent-amber shrink-0 mt-1" />
            <div>
              <h3 className="font-bold text-accent-amber mb-2">
                Data quality issues detected ({validationReport.errors} critical)
              </h3>
              <p className="text-sm text-dark-700 dark:text-dark-300 mb-4 max-w-3xl">
                We found missing values, constant columns, or mixed data types. 
                We recommend running the automated cleaning pipeline before training ML models.
              </p>
              <button 
                onClick={handleClean}
                disabled={isCleaning}
                className="btn-secondary border-accent-amber/30 hover:bg-accent-amber/20 flex items-center gap-2"
              >
                {isCleaning ? (
                  <><div className="w-4 h-4 rounded-full border-2 border-accent-amber/30 border-t-accent-amber animate-spin" /> Cleaning...</>
                ) : (
                  <><Play className="w-4 h-4 text-accent-amber" /> Run Auto-Clean Pipeline</>
                )}
              </button>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Main Content — Data Preview */}
          <div className="lg:col-span-2 space-y-8">
            <div className="glass-card overflow-hidden">
              <div className="p-6 border-b border-dark-100 dark:border-dark-700">
                <h2 className="text-lg font-bold text-dark-900 dark:text-white flex items-center gap-2">
                  <Layers className="w-5 h-5 text-primary-500" />
                  Data Preview
                </h2>
              </div>
              <div className="p-6">
                <DataPreviewTable datasetId={id} />
              </div>
            </div>
          </div>

          {/* Sidebar — Stats & Logs */}
          <div className="space-y-8">
            {/* Stats Card */}
            <div className="glass-card p-6">
              <h3 className="font-bold text-dark-900 dark:text-white mb-6">Dataset Profile</h3>
              
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="bg-dark-50 dark:bg-dark-900 p-4 rounded-xl border border-dark-100 dark:border-dark-700">
                  <div className="text-2xl font-bold text-cyan-500">{dataset.row_count?.toLocaleString() || 0}</div>
                  <div className="text-xs text-dark-500 font-medium uppercase mt-1">Total Rows</div>
                </div>
                <div className="bg-dark-50 dark:bg-dark-900 p-4 rounded-xl border border-dark-100 dark:border-dark-700">
                  <div className="text-2xl font-bold text-cyan-500">{dataset.column_count || 0}</div>
                  <div className="text-xs text-dark-500 font-medium uppercase mt-1">Features</div>
                </div>
              </div>

              {/* Sample of column metadata if available */}
              {dataset.column_metadata && (
                <div>
                  <h4 className="text-xs font-semibold text-dark-400 uppercase tracking-wider mb-3">Key Features</h4>
                  <div className="space-y-3">
                    {Object.entries(dataset.column_metadata).slice(0, 5).map(([col, meta]) => (
                      <div key={col} className="flex items-center justify-between">
                        <span className="text-sm font-medium text-dark-700 dark:text-dark-300 truncate max-w-[150px]" title={col}>
                          {col}
                        </span>
                        <div className="flex gap-2">
                          <span className="text-[10px] bg-dark-100 dark:bg-dark-800 px-1.5 py-0.5 rounded text-dark-500">
                            {meta.dtype.split('(')[0]}
                          </span>
                          {meta.null_percentage > 0 && (
                            <span className="text-[10px] bg-accent-amber/10 px-1.5 py-0.5 rounded text-accent-amber">
                              {meta.null_percentage}% null
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Transformation Logs */}
            <div className="glass-card p-6">
              <h3 className="font-bold text-dark-900 dark:text-white mb-6 flex items-center justify-between">
                <span>ETL Pipeline</span>
                <Activity className="w-4 h-4 text-primary-500" />
              </h3>
              <TransformationLog log={dataset.cleaning_log} status={dataset.status} />
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}
