import { useState, useCallback, useRef } from 'react';
import { UploadCloud, FileType, CheckCircle2, XCircle, AlertCircle, Trash2 } from 'lucide-react';
import { FILE_TYPES, MAX_FILE_SIZE_MB } from '../utils/constants';

export default function FileDropzone({ onFileSelect, disabled = false }) {
  const [isDragActive, setIsDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState('');
  const inputRef = useRef(null);

  const validateFile = (file) => {
    setError('');
    
    // Check extension
    const ext = `.${file.name.split('.').pop().toLowerCase()}`;
    const validExts = Object.values(FILE_TYPES);
    if (!validExts.includes(ext)) {
      setError(`Invalid file type. Please upload ${validExts.join(', ')}`);
      return false;
    }

    // Check size
    const sizeMB = file.size / (1024 * 1024);
    if (sizeMB > MAX_FILE_SIZE_MB) {
      setError(`File is too large (${sizeMB.toFixed(1)}MB). Max allowed is ${MAX_FILE_SIZE_MB}MB.`);
      return false;
    }

    return true;
  };

  const handleFile = (file) => {
    if (!file) return;
    if (validateFile(file)) {
      setSelectedFile(file);
      onFileSelect(file);
    }
  };

  const handleDragEnter = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) setIsDragActive(true);
  }, [disabled]);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    
    if (disabled) return;
    
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  }, [disabled]); // eslint-disable-next-line react-hooks/exhaustive-deps

  const handleClear = (e) => {
    e.stopPropagation();
    setSelectedFile(null);
    onFileSelect(null);
    if (inputRef.current) inputRef.current.value = '';
    setError('');
  };

  return (
    <div className="w-full">
      <div
        className={`relative border-2 border-dashed rounded-2xl p-8 transition-all duration-200 
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
          ${isDragActive 
            ? 'border-primary-500 bg-primary-50/50 dark:bg-primary-900/10' 
            : 'border-dark-300 dark:border-dark-700 hover:border-primary-400 dark:hover:border-primary-500 bg-white dark:bg-dark-800'
          }
          ${selectedFile ? 'border-solid border-accent-emerald bg-accent-emerald/5 dark:bg-accent-emerald/5' : ''}
        `}
        onDragEnter={handleDragEnter}
        onDragOver={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !disabled && !selectedFile && inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept={Object.values(FILE_TYPES).join(',')}
          className="hidden"
          onChange={(e) => handleFile(e.target.files?.[0])}
          disabled={disabled}
        />

        <div className="flex flex-col items-center justify-center text-center">
          {selectedFile ? (
            <div className="flex flex-col items-center animate-fade-in w-full">
              <div className="w-16 h-16 rounded-full bg-accent-emerald/20 flex items-center justify-center mb-4 text-accent-emerald">
                <FileType className="w-8 h-8" />
              </div>
              <h4 className="text-lg font-semibold text-dark-900 dark:text-white mb-1 truncate max-w-full px-4">
                {selectedFile.name}
              </h4>
              <p className="text-sm text-dark-500 dark:text-dark-400 mb-6 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-accent-emerald" />
                {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB — Ready to upload
              </p>
              
              <button
                type="button"
                onClick={handleClear}
                className="btn-ghost text-accent-rose hover:bg-accent-rose/10 flex items-center gap-2"
                disabled={disabled}
              >
                <Trash2 className="w-4 h-4" />
                Remove File
              </button>
            </div>
          ) : (
            <div className="flex flex-col items-center">
              <div className="w-16 h-16 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center mb-4 text-primary-500">
                <UploadCloud className="w-8 h-8" />
              </div>
              <h4 className="text-lg font-semibold text-dark-900 dark:text-white mb-2">
                Click or drag & drop to upload
              </h4>
              <p className="text-sm text-dark-500 dark:text-dark-400 mb-4 max-w-sm">
                CSV or Excel files only. We automatically clean data, infer types, and prepare it for ML.
              </p>
              <div className="flex items-center gap-4 text-xs font-medium text-dark-400 dark:text-dark-500">
                <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-dark-100 dark:bg-dark-800">
                  <FileType className="w-3 h-3" /> CSV
                </span>
                <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-dark-100 dark:bg-dark-800">
                  <FileType className="w-3 h-3" /> XLSX/XLS
                </span>
                <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-dark-100 dark:bg-dark-800">
                  Max {MAX_FILE_SIZE_MB}MB
                </span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mt-4 flex items-start gap-2 p-3 rounded-xl bg-accent-rose/10 text-accent-rose animate-slide-up">
          <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
          <p className="text-sm font-medium">{error}</p>
        </div>
      )}
    </div>
  );
}
