import React from 'react';
import { cn } from '@/lib/utils';
import { ProgressBarProps } from '@/types';

const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  className,
  showLabel = true,
  variant = 'default',
}) => {
  const variants = {
    default: 'bg-primary-600',
    success: 'bg-success-600',
    warning: 'bg-yellow-600',
    error: 'bg-danger-600',
  };

  return (
    <div className={cn('w-full', className)}>
      {showLabel && (
        <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-2">
          <span>Progress</span>
          <span>{Math.round(progress)}%</span>
        </div>
      )}
      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
        <div
          className={cn(
            'h-full transition-all duration-300 ease-out rounded-full',
            variants[variant]
          )}
          style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
        >
          <div className="h-full bg-gradient-to-r from-transparent via-white to-transparent opacity-30 animate-pulse" />
        </div>
      </div>
    </div>
  );
};

export default ProgressBar;
