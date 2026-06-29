import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';
import FileDropzone from '../components/FileDropzone';
import { ArrowRight, FileText, Settings2, ShieldCheck, Zap } from 'lucide-react';

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [datasetName, setDatasetName] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleUpload = async () => {
    if (!file) return;
    
    setIsUploading(true);
    setError('');
    
    const formData = new FormData();
    formData.append('file', file);
    if (datasetName.trim()) {
      formData.append('name', datasetName.trim());
    }

    try {
      // Simulate progress for UX
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) return prev;
          return prev + 10;
        });
      }, 300);

      const response = await api.post('/datasets/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      // Brief delay to show 100% completion
      setTimeout(() => {
        navigate(`/datasets/${response.data.id}`);
      }, 800);
      
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to upload dataset.');
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  return (
    <div className="min-h-screen bg-dark-50 dark:bg-dark-950 pt-20 pb-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto space-y-8 animate-fade-in">
        
        {/* Header */}
        <div className="text-center max-w-2xl mx-auto mb-12">
          <h1 className="text-4xl font-extrabold text-dark-900 dark:text-white mb-4">
            Import your <span className="gradient-text">dataset</span>
          </h1>
          <p className="text-lg text-dark-500 dark:text-dark-400">
            Upload your raw CSV or Excel file. Our automated ETL pipeline will instantly clean, 
            validate, and prepare it for machine learning.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Main Upload Area */}
          <div className="lg:col-span-2 space-y-6">
            <div className="glass-card p-6 md:p-8">
              <h2 className="text-xl font-bold text-dark-900 dark:text-white mb-6 flex items-center gap-2">
                <FileText className="w-5 h-5 text-primary-500" />
                Select File
              </h2>
              
              <FileDropzone 
                onFileSelect={setFile} 
                disabled={isUploading} 
              />

              {file && (
                <div className="mt-8 space-y-4 animate-slide-up">
                  <div>
                    <label htmlFor="dataset-name" className="block text-sm font-medium text-dark-700 dark:text-dark-300 mb-1.5">
                      Dataset Name (Optional)
                    </label>
                    <input
                      id="dataset-name"
                      type="text"
                      placeholder="e.g. Q3 Sales Data, Customer Churn"
                      value={datasetName}
                      onChange={(e) => setDatasetName(e.target.value)}
                      disabled={isUploading}
                      className="input-field"
                    />
                  </div>

                  {error && (
                    <div className="p-4 rounded-xl bg-accent-rose/10 text-accent-rose text-sm font-medium border border-accent-rose/20">
                      {error}
                    </div>
                  )}

                  {isUploading ? (
                    <div className="space-y-3">
                      <div className="flex justify-between text-sm font-medium">
                        <span className="text-dark-600 dark:text-dark-300">Uploading & Parsing...</span>
                        <span className="text-primary-500">{uploadProgress}%</span>
                      </div>
                      <div className="h-2 w-full bg-dark-100 dark:bg-dark-800 rounded-full overflow-hidden">
                        <div 
                          className="h-full gradient-primary transition-all duration-300 ease-out"
                          style={{ width: `${uploadProgress}%` }}
                        />
                      </div>
                    </div>
                  ) : (
                    <div className="pt-4 border-t border-dark-100 dark:border-dark-800 flex justify-end">
                      <button
                        onClick={handleUpload}
                        className="btn-primary flex items-center gap-2"
                      >
                        Start Processing
                        <ArrowRight className="w-4 h-4" />
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Right Sidebar — Features */}
          <div className="space-y-6">
            <div className="glass-card p-6">
              <h3 className="font-bold text-dark-900 dark:text-white mb-4">
                What happens next?
              </h3>
              
              <div className="space-y-6">
                {[
                  {
                    icon: Zap,
                    color: 'text-accent-amber',
                    bg: 'bg-accent-amber/10',
                    title: 'Automated Cleaning',
                    desc: 'We handle missing values, duplicates, and outliers automatically.'
                  },
                  {
                    icon: Settings2,
                    color: 'text-primary-500',
                    bg: 'bg-primary-500/10',
                    title: 'Type Inference',
                    desc: 'Smart detection of categorical, numeric, and text features.'
                  },
                  {
                    icon: ShieldCheck,
                    color: 'text-accent-emerald',
                    bg: 'bg-accent-emerald/10',
                    title: 'Data Validation',
                    desc: 'Checks for consistency, constants, and edge cases.'
                  }
                ].map((item, i) => (
                  <div key={i} className="flex gap-4">
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${item.bg} ${item.color}`}>
                      <item.icon className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-dark-900 dark:text-white mb-1">
                        {item.title}
                      </h4>
                      <p className="text-xs text-dark-500 dark:text-dark-400 leading-relaxed">
                        {item.desc}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="glass-card p-6 bg-gradient-to-br from-primary-900/50 to-dark-900 border-primary-500/20">
              <h3 className="font-bold text-white mb-2">Secure & Private</h3>
              <p className="text-sm text-white/70">
                Your files are encrypted at rest in isolated Supabase Storage buckets with strict Row Level Security.
              </p>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
