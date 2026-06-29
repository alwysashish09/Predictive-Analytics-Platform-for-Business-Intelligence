import { Activity, CheckCircle2, ChevronRight, XCircle, PlayCircle } from 'lucide-react';

export default function TransformationLog({ log = [], status = 'ready' }) {
  if (!log || log.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-dark-500 dark:text-dark-400">
        <Activity className="w-8 h-8 mb-3 opacity-50" />
        <p className="text-sm">No transformations recorded yet.</p>
      </div>
    );
  }

  return (
    <div className="relative">
      {/* Vertical line connecting steps */}
      <div className="absolute left-[23px] top-4 bottom-4 w-px bg-dark-200 dark:bg-dark-700 z-0" />

      <div className="space-y-6 relative z-10">
        {log.map((step, idx) => (
          <div key={idx} className="flex gap-4 group">
            {/* Step indicator */}
            <div className="shrink-0 mt-1">
              <div className="w-12 h-12 rounded-full border-4 border-white dark:border-dark-900 bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center group-hover:scale-110 transition-transform">
                <CheckCircle2 className="w-5 h-5 text-primary-500" />
              </div>
            </div>

            {/* Content card */}
            <div className="flex-1">
              <div className="bg-white dark:bg-dark-800 rounded-xl border border-dark-200 dark:border-dark-700 p-4 shadow-sm group-hover:shadow-md group-hover:border-primary-300 dark:group-hover:border-primary-700 transition-all">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-bold text-dark-900 dark:text-white capitalize">
                    {step.step_name.replace(/_/g, ' ')}
                  </h4>
                  <span className="text-xs font-mono text-dark-500 dark:text-dark-400 bg-dark-50 dark:bg-dark-900 px-2 py-1 rounded-md">
                    {step.rows_affected} rows changed
                  </span>
                </div>
                <p className="text-sm text-dark-600 dark:text-dark-300 leading-relaxed">
                  {step.description}
                </p>
                
                {step.columns_affected && step.columns_affected.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-dark-100 dark:border-dark-700">
                    <p className="text-xs text-dark-500 dark:text-dark-400 mb-1.5 font-medium">Affected Columns:</p>
                    <div className="flex flex-wrap gap-1.5">
                      {step.columns_affected.slice(0, 5).map(col => (
                        <span key={col} className="text-[10px] bg-dark-100 dark:bg-dark-700 px-2 py-0.5 rounded text-dark-600 dark:text-dark-300 border border-dark-200 dark:border-dark-600">
                          {col}
                        </span>
                      ))}
                      {step.columns_affected.length > 5 && (
                        <span className="text-[10px] text-dark-500 dark:text-dark-400 px-1 py-0.5">
                          +{step.columns_affected.length - 5} more
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
