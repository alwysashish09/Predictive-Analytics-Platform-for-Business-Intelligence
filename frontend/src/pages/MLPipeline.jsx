import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../utils/api';
import { BrainCircuit, Play, ChevronRight, BarChart3, Settings2, ShieldAlert, Download } from 'lucide-react';

export default function MLPipeline() {
  const { datasetId } = useParams();
  const navigate = useNavigate();
  
  const [dataset, setDataset] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Form State
  const [targetCol, setTargetCol] = useState('');
  const [modelType, setModelType] = useState('random_forest');
  
  // Training State
  const [isTraining, setIsTraining] = useState(false);
  const [trainError, setTrainError] = useState('');
  
  // Results State
  const [results, setResults] = useState(null);
  const [history, setHistory] = useState([]);
  const [isDownloading, setIsDownloading] = useState(false);

  useEffect(() => {
    fetchData();
  }, [datasetId]);

  const fetchData = async () => {
    try {
      const [dsRes, runsRes] = await Promise.all([
        api.get(`/datasets/${datasetId}`),
        api.get(`/ml/${datasetId}/runs`)
      ]);
      setDataset(dsRes.data);
      setHistory(runsRes.data);
      
      // Auto-select target column if possible
      if (dsRes.data.target_column) {
        setTargetCol(dsRes.data.target_column);
      } else if (dsRes.data.column_metadata) {
        // Try to find a common target name like 'target', 'label', 'churn', 'status'
        const cols = Object.keys(dsRes.data.column_metadata);
        const likelyTarget = cols.find(c => ['target', 'label', 'class', 'churn', 'status', 'outcome'].includes(c.toLowerCase()));
        if (likelyTarget) setTargetCol(likelyTarget);
        else setTargetCol(cols[cols.length - 1]); // Default to last column
      }
      
    } catch (err) {
      setError('Failed to load dataset details.');
    } finally {
      setLoading(false);
    }
  };

  const handleTrain = async (e) => {
    e.preventDefault();
    if (!targetCol) return;
    
    setIsTraining(true);
    setTrainError('');
    setResults(null);
    
    try {
      const res = await api.post(`/ml/${datasetId}/train`, {
        target_column: targetCol,
        model_type: modelType,
        hyperparameters: {} // Using defaults for MVP
      });
      
      setResults(res.data);
      setHistory([res.data, ...history]);
      
    } catch (err) {
      setTrainError(err.response?.data?.detail || 'Training failed. Please try again.');
    } finally {
      setIsTraining(false);
    }
  };

  const handleDownloadReport = async () => {
    setIsDownloading(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8000/api/v1/reports/${datasetId}/download`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) throw new Error('Failed to download report');
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${dataset?.name?.replace(/ /g, '_') || 'dataset'}_Executive_Report.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      alert('Failed to download report. Make sure a model has been trained.');
    } finally {
      setIsDownloading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-dark-50 dark:bg-dark-950 pt-16">
        <div className="w-10 h-10 border-4 border-primary-200 border-t-primary-500 rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-dark-50 dark:bg-dark-950 pt-24 pb-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-8 animate-fade-in">
        
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <div className="w-12 h-12 rounded-xl gradient-primary flex items-center justify-center shadow-lg shadow-primary-500/20">
            <BrainCircuit className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-dark-900 dark:text-white">Train Model</h1>
            <div className="flex items-center gap-2 text-dark-500 text-sm mt-1">
              <span className="hover:text-primary-500 cursor-pointer" onClick={() => navigate('/datasets')}>Datasets</span>
              <ChevronRight className="w-4 h-4" />
              <span className="hover:text-primary-500 cursor-pointer" onClick={() => navigate(`/datasets/${datasetId}`)}>{dataset?.name}</span>
              <ChevronRight className="w-4 h-4" />
              <span className="text-dark-700 dark:text-dark-300 font-medium">Pipeline</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Configuration Panel */}
          <div className="lg:col-span-1 space-y-6">
            <div className="glass-card p-6">
              <h2 className="text-lg font-bold text-dark-900 dark:text-white mb-6 flex items-center gap-2">
                <Settings2 className="w-5 h-5 text-primary-500" />
                Configuration
              </h2>
              
              <form onSubmit={handleTrain} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-dark-700 dark:text-dark-300 mb-2">
                    Target Variable (What to predict)
                  </label>
                  <select
                    value={targetCol}
                    onChange={(e) => setTargetCol(e.target.value)}
                    disabled={isTraining}
                    className="input-field cursor-pointer"
                  >
                    <option value="" disabled>Select target column</option>
                    {dataset?.column_metadata && Object.keys(dataset.column_metadata).map(col => (
                      <option key={col} value={col}>{col}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-dark-700 dark:text-dark-300 mb-2">
                    Model Architecture
                  </label>
                  <div className="space-y-3">
                    <label className={`flex items-start p-4 rounded-xl border cursor-pointer transition-all ${modelType === 'random_forest' ? 'border-primary-500 bg-primary-50/50 dark:bg-primary-900/10' : 'border-dark-200 dark:border-dark-700 bg-dark-50 dark:bg-dark-800/50 hover:border-dark-300 dark:hover:border-dark-600'}`}>
                      <input 
                        type="radio" 
                        name="modelType" 
                        value="random_forest" 
                        checked={modelType === 'random_forest'}
                        onChange={(e) => setModelType(e.target.value)}
                        className="mt-1 sr-only"
                      />
                      <div className={`w-4 h-4 rounded-full border flex-shrink-0 mt-0.5 mr-3 flex items-center justify-center ${modelType === 'random_forest' ? 'border-primary-500' : 'border-dark-400'}`}>
                        {modelType === 'random_forest' && <div className="w-2 h-2 rounded-full bg-primary-500" />}
                      </div>
                      <div>
                        <div className="font-semibold text-dark-900 dark:text-white mb-1">Random Forest</div>
                        <div className="text-xs text-dark-500 dark:text-dark-400">Robust ensemble model, great for preventing overfitting. Good default choice.</div>
                      </div>
                    </label>
                    
                    <label className={`flex items-start p-4 rounded-xl border cursor-pointer transition-all ${modelType === 'xgboost' ? 'border-primary-500 bg-primary-50/50 dark:bg-primary-900/10' : 'border-dark-200 dark:border-dark-700 bg-dark-50 dark:bg-dark-800/50 hover:border-dark-300 dark:hover:border-dark-600'}`}>
                      <input 
                        type="radio" 
                        name="modelType" 
                        value="xgboost" 
                        checked={modelType === 'xgboost'}
                        onChange={(e) => setModelType(e.target.value)}
                        className="mt-1 sr-only"
                      />
                      <div className={`w-4 h-4 rounded-full border flex-shrink-0 mt-0.5 mr-3 flex items-center justify-center ${modelType === 'xgboost' ? 'border-primary-500' : 'border-dark-400'}`}>
                        {modelType === 'xgboost' && <div className="w-2 h-2 rounded-full bg-primary-500" />}
                      </div>
                      <div>
                        <div className="font-semibold text-dark-900 dark:text-white mb-1">XGBoost</div>
                        <div className="text-xs text-dark-500 dark:text-dark-400">High-performance gradient boosting. Often yields the highest accuracy.</div>
                      </div>
                    </label>
                  </div>
                </div>

                {trainError && (
                  <div className="p-3 bg-accent-rose/10 text-accent-rose text-sm rounded-lg flex items-start gap-2">
                    <ShieldAlert className="w-4 h-4 mt-0.5 shrink-0" />
                    <p>{trainError}</p>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={isTraining || !targetCol}
                  className="w-full btn-primary flex items-center justify-center gap-2"
                >
                  {isTraining ? (
                    <><div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Training Pipeline...</>
                  ) : (
                    <><Play className="w-5 h-5" /> Start Training</>
                  )}
                </button>
              </form>
            </div>
            
            {/* History Panel */}
            {history.length > 0 && (
              <div className="glass-card p-6">
                <h3 className="font-bold text-dark-900 dark:text-white mb-4 text-sm uppercase tracking-wider">Run History</h3>
                <div className="space-y-3 max-h-60 overflow-y-auto pr-2">
                  {history.map(run => (
                    <div 
                      key={run.id}
                      onClick={() => setResults(run)}
                      className={`p-3 rounded-xl border cursor-pointer transition-colors ${results?.id === run.id ? 'border-primary-500 bg-primary-50/50 dark:bg-primary-900/10' : 'border-dark-100 dark:border-dark-800 hover:border-dark-300 dark:hover:border-dark-600'}`}
                    >
                      <div className="flex justify-between items-center mb-1">
                        <span className="font-medium text-sm text-dark-900 dark:text-white capitalize">
                          {run.model_type.replace('_', ' ')}
                        </span>
                        <span className="text-xs font-mono bg-dark-100 dark:bg-dark-800 px-2 py-0.5 rounded text-dark-600 dark:text-dark-300">
                          Acc: {(run.metrics.accuracy * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="text-xs text-dark-500 truncate">Target: {run.target_column}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Results Panel */}
          <div className="lg:col-span-2 space-y-6">
            {isTraining ? (
              <div className="glass-card h-full min-h-[400px] flex flex-col items-center justify-center p-12 text-center relative overflow-hidden">
                {/* Background scanning effect */}
                <div className="absolute inset-0 bg-gradient-to-b from-transparent via-primary-500/5 to-transparent h-1/2 animate-scan" />
                
                <div className="w-16 h-16 rounded-full border-4 border-primary-100 dark:border-primary-900/50 border-t-primary-500 animate-spin mb-6 relative z-10" />
                <h3 className="text-xl font-bold text-dark-900 dark:text-white mb-2 relative z-10">
                  Training Model Pipeline
                </h3>
                <p className="text-dark-500 dark:text-dark-400 max-w-sm relative z-10">
                  Extracting features, scaling data, one-hot encoding variables, and optimizing decision trees...
                </p>
              </div>
            ) : results ? (
              <div className="space-y-6 animate-fade-in">
                {/* Metrics Cards */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {[
                    { label: 'Accuracy', val: results.metrics.accuracy, color: 'text-cyan-500' },
                    { label: 'F1 Score', val: results.metrics.f1_score, color: 'text-primary-500' },
                    { label: 'Precision', val: results.metrics.precision, color: 'text-accent-emerald' },
                    { label: 'Recall', val: results.metrics.recall, color: 'text-accent-amber' },
                  ].map((m, i) => (
                    <div key={i} className="glass-card p-5 flex flex-col items-center justify-center text-center">
                      <div className={`text-3xl font-bold mb-1 ${m.color}`}>
                        {(m.val * 100).toFixed(1)}%
                      </div>
                      <div className="text-xs font-medium text-dark-500 uppercase tracking-wider">
                        {m.label}
                      </div>
                    </div>
                  ))}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Feature Importance */}
                  <div className="glass-card p-6">
                    <h3 className="text-lg font-bold text-dark-900 dark:text-white mb-6 flex items-center gap-2">
                      <BarChart3 className="w-5 h-5 text-primary-500" />
                      Top Drivers (Feature Importance)
                    </h3>
                    <div className="space-y-4 max-h-[300px] overflow-y-auto pr-2">
                      {results.feature_importance.map((f, i) => (
                        <div key={i}>
                          <div className="flex justify-between text-sm mb-1.5">
                            <span className="font-medium text-dark-700 dark:text-dark-300 truncate max-w-[200px]" title={f.feature}>{f.feature}</span>
                            <span className="text-dark-500 font-mono">{(f.importance * 100).toFixed(1)}%</span>
                          </div>
                          <div className="h-2 w-full bg-dark-100 dark:bg-dark-800 rounded-full overflow-hidden">
                            <div 
                              className="h-full bg-gradient-to-r from-primary-600 to-cyan-500 rounded-full"
                              style={{ width: `${f.importance * 100}%` }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Model Metadata */}
                  <div className="glass-card p-6">
                    <h3 className="text-lg font-bold text-dark-900 dark:text-white mb-6">Run Summary</h3>
                    <div className="space-y-4">
                      <div className="flex justify-between py-3 border-b border-dark-100 dark:border-dark-800">
                        <span className="text-dark-500">Algorithm</span>
                        <span className="font-medium text-dark-900 dark:text-white capitalize">{results.model_type.replace('_', ' ')}</span>
                      </div>
                      <div className="flex justify-between py-3 border-b border-dark-100 dark:border-dark-800">
                        <span className="text-dark-500">Target</span>
                        <span className="font-medium text-dark-900 dark:text-white">{results.target_column}</span>
                      </div>
                      <div className="flex justify-between py-3 border-b border-dark-100 dark:border-dark-800">
                        <span className="text-dark-500">Training Time</span>
                        <span className="font-medium text-dark-900 dark:text-white">{results.training_duration_sec.toFixed(2)}s</span>
                      </div>
                      <div className="flex justify-between py-3 border-b border-dark-100 dark:border-dark-800">
                        <span className="text-dark-500">Status</span>
                        <span className="font-medium text-accent-emerald bg-accent-emerald/10 px-2 py-0.5 rounded text-sm uppercase">Success</span>
                      </div>
                    </div>
                    
                    <div className="flex flex-col sm:flex-row gap-3 mt-6">
                      <button 
                        onClick={() => navigate(`/chat/${datasetId}`)}
                        className="flex-1 btn-secondary"
                      >
                        Chat with AI
                      </button>
                      <button 
                        onClick={handleDownloadReport}
                        disabled={isDownloading}
                        className="flex-1 btn-primary flex items-center justify-center gap-2"
                      >
                        {isDownloading ? (
                          <><div className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin" /> Generating...</>
                        ) : (
                          <><Download className="w-4 h-4" /> PDF Report</>
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="glass-card h-full min-h-[400px] flex flex-col items-center justify-center p-12 text-center border-dashed border-2 border-dark-200 dark:border-dark-700 bg-transparent">
                <BrainCircuit className="w-16 h-16 text-dark-300 dark:text-dark-700 mb-4" />
                <h3 className="text-xl font-bold text-dark-400 dark:text-dark-600 mb-2">Ready to Train</h3>
                <p className="text-dark-500 max-w-sm">
                  Select a target column and model architecture on the left, then click Start Training to build your predictive model.
                </p>
              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}
