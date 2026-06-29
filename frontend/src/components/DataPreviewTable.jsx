import { useState, useEffect } from 'react';
import { ArrowUpDown, AlertCircle, FileType } from 'lucide-react';
import api from '../utils/api';

export default function DataPreviewTable({ datasetId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchPreview = async () => {
      try {
        const response = await api.get(`/etl/${datasetId}/preview?limit=50`);
        setData(response.data);
      } catch (err) {
        setError('Failed to load data preview.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchPreview();
  }, [datasetId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-12">
        <div className="w-8 h-8 border-4 border-primary-200 border-t-primary-500 rounded-full animate-spin mb-4" />
        <p className="text-dark-500 dark:text-dark-400">Loading preview...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center gap-2 p-4 text-accent-rose bg-accent-rose/10 rounded-xl">
        <AlertCircle className="w-5 h-5" />
        <p>{error}</p>
      </div>
    );
  }

  if (!data || data.rows.length === 0) {
    return (
      <div className="text-center p-12 bg-dark-100 dark:bg-dark-800 rounded-xl text-dark-500 dark:text-dark-400">
        No data available for preview.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between text-sm text-dark-500 dark:text-dark-400">
        <p>Showing {data.preview_rows} of {data.total_rows.toLocaleString()} rows</p>
        <p className="flex items-center gap-1.5">
          <FileType className="w-4 h-4" />
          {data.columns.length} columns
        </p>
      </div>

      <div className="overflow-x-auto rounded-xl border border-dark-200 dark:border-dark-700 bg-white dark:bg-dark-900 shadow-sm">
        <table className="w-full text-sm text-left">
          <thead className="text-xs text-dark-500 dark:text-dark-400 uppercase bg-dark-50 dark:bg-dark-800/50 border-b border-dark-200 dark:border-dark-700">
            <tr>
              <th className="px-4 py-3 font-medium text-dark-400 text-center w-12 border-r border-dark-200 dark:border-dark-700">#</th>
              {data.columns.map((col, i) => (
                <th key={i} className="px-4 py-3 font-semibold whitespace-nowrap min-w-[120px] max-w-[200px]">
                  <div className="flex items-center justify-between">
                    <span className="truncate pr-2" title={col}>{col}</span>
                    <span className="text-[10px] font-normal px-1.5 py-0.5 rounded bg-dark-200 dark:bg-dark-700 text-dark-600 dark:text-dark-300 ml-1">
                      {data.dtypes[col]?.split('(')[0] || 'str'}
                    </span>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-dark-100 dark:divide-dark-800">
            {data.rows.map((row, rowIndex) => (
              <tr 
                key={rowIndex}
                className="hover:bg-primary-50/50 dark:hover:bg-primary-900/10 transition-colors"
              >
                <td className="px-4 py-2 text-center text-dark-400 font-medium border-r border-dark-200 dark:border-dark-700 bg-dark-50/50 dark:bg-dark-800/20">
                  {rowIndex + 1}
                </td>
                {data.columns.map((col, colIndex) => {
                  const val = row[col];
                  const isNull = val === null || val === undefined;
                  
                  return (
                    <td key={colIndex} className="px-4 py-2.5 whitespace-nowrap overflow-hidden text-ellipsis max-w-[200px]" title={String(val)}>
                      {isNull ? (
                        <span className="text-dark-400 italic font-mono text-xs bg-dark-100 dark:bg-dark-800 px-1.5 py-0.5 rounded">null</span>
                      ) : (
                        <span className="text-dark-700 dark:text-dark-200">{String(val)}</span>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
