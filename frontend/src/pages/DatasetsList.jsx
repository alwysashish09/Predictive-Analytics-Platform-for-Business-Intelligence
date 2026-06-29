import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../utils/api';
import { FileSpreadsheet, Plus, Search, MoreVertical, Trash2, ArrowRight } from 'lucide-react';

export default function DatasetsList() {
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchDatasets();
  }, []);

  const fetchDatasets = async () => {
    try {
      const response = await api.get('/datasets');
      setDatasets(response.data);
    } catch (err) {
      setError('Failed to load datasets.');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (e, id) => {
    e.preventDefault();
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this dataset? This action cannot be undone.')) return;
    
    try {
      await api.delete(`/datasets/${id}`);
      setDatasets(datasets.filter(d => d.id !== id));
    } catch (err) {
      alert('Failed to delete dataset.');
    }
  };

  const filteredDatasets = datasets.filter(d => 
    d.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
    d.file_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-dark-50 dark:bg-dark-950 pt-24 pb-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-8 animate-fade-in">
        
        {/* Header & Actions */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold text-dark-900 dark:text-white mb-2">
              Your Datasets
            </h1>
            <p className="text-dark-500 dark:text-dark-400">
              Manage and analyze your uploaded data
            </p>
          </div>
          
          <button 
            onClick={() => navigate('/upload')}
            className="btn-primary flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            New Dataset
          </button>
        </div>

        {/* Search & Filter Bar */}
        <div className="glass p-2 rounded-xl flex items-center max-w-md">
          <div className="pl-3 pr-2 text-dark-400">
            <Search className="w-5 h-5" />
          </div>
          <input
            type="text"
            placeholder="Search datasets by name..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-transparent border-none focus:ring-0 text-dark-900 dark:text-white placeholder:text-dark-400 py-2"
          />
        </div>

        {/* Content */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="w-10 h-10 border-4 border-primary-200 border-t-primary-500 rounded-full animate-spin" />
          </div>
        ) : error ? (
          <div className="p-6 bg-accent-rose/10 text-accent-rose rounded-xl font-medium text-center">
            {error}
          </div>
        ) : filteredDatasets.length === 0 ? (
          <div className="text-center py-20 glass-card">
            <div className="w-16 h-16 rounded-full bg-dark-100 dark:bg-dark-800 flex items-center justify-center mx-auto mb-4">
              <FileSpreadsheet className="w-8 h-8 text-dark-400" />
            </div>
            <h3 className="text-xl font-bold text-dark-900 dark:text-white mb-2">No datasets found</h3>
            <p className="text-dark-500 dark:text-dark-400 mb-6 max-w-sm mx-auto">
              {searchQuery ? "No datasets match your search criteria." : "You haven't uploaded any datasets yet. Get started by uploading your first CSV or Excel file."}
            </p>
            {!searchQuery && (
              <button 
                onClick={() => navigate('/upload')}
                className="btn-secondary"
              >
                Upload Data
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredDatasets.map(dataset => (
              <Link 
                key={dataset.id}
                to={`/datasets/${dataset.id}`}
                className="glass-card p-6 block group hover:border-primary-300 dark:hover:border-primary-700 transition-all duration-300 hover:-translate-y-1"
              >
                <div className="flex justify-between items-start mb-4">
                  <div className="w-10 h-10 rounded-xl bg-primary-50 dark:bg-primary-900/50 flex items-center justify-center group-hover:bg-primary-100 dark:group-hover:bg-primary-900 transition-colors">
                    <FileSpreadsheet className="w-5 h-5 text-primary-500" />
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`text-[10px] uppercase font-bold px-2 py-1 rounded-md
                      ${dataset.status === 'ready' ? 'bg-accent-emerald/10 text-accent-emerald' : 
                        dataset.status === 'error' ? 'bg-accent-rose/10 text-accent-rose' : 
                        'bg-accent-amber/10 text-accent-amber'}
                    `}>
                      {dataset.status}
                    </span>
                    <button 
                      onClick={(e) => handleDelete(e, dataset.id)}
                      className="p-1.5 text-dark-400 hover:text-accent-rose hover:bg-accent-rose/10 rounded-md transition-colors"
                      title="Delete dataset"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                <h3 className="font-bold text-lg text-dark-900 dark:text-white truncate mb-1" title={dataset.name}>
                  {dataset.name}
                </h3>
                <p className="text-xs text-dark-500 truncate mb-6" title={dataset.file_name}>
                  {dataset.file_name}
                </p>

                <div className="grid grid-cols-2 gap-4 pt-4 border-t border-dark-100 dark:border-dark-800">
                  <div>
                    <p className="text-xs text-dark-500 mb-0.5">Rows</p>
                    <p className="font-semibold text-dark-900 dark:text-white">
                      {dataset.row_count?.toLocaleString() || '---'}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-dark-500 mb-0.5">Columns</p>
                    <p className="font-semibold text-dark-900 dark:text-white">
                      {dataset.column_count || '---'}
                    </p>
                  </div>
                </div>
                
                <div className="mt-4 flex items-center justify-end text-primary-500 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity translate-x-2 group-hover:translate-x-0">
                  View Details <ArrowRight className="w-4 h-4 ml-1" />
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
